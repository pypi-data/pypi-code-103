"""Main client for redbrick sagemaker."""
import json
import os
import uuid
from typing import Any, Dict, Optional, Tuple

import boto3
import boto3.session
import sagemaker
import sagemaker.transformer

from sagemaker import get_execution_role
from sagemaker.amazon.amazon_estimator import get_image_uri

from redbrick_sagemaker.utils.sagemaker import (
    construct_training_job,
    construct_tuning_job,
)
from redbrick_sagemaker.logging import logger


class SagemakerClient:
    """Interface to run Active Learning cycles with sagemaker."""

    def __init__(
        self,
        bucket: str,
        bucket_prefix: str,
        iam_role: Optional[str],
        cache_dir: str,
        tuning_job: Optional[str] = None,
        profile_name: Optional[str] = "default",
    ) -> None:
        """Construct client."""
        # Define sagemaker execution role
        try:
            self.role: str = get_execution_role()
        except ValueError as error:
            if iam_role:
                self.role = iam_role
            else:
                raise Exception(
                    "When using redbrick_sagemaker outside of AWS notebooks,"
                    + "you have to provide an IAM role"
                ) from error

        # Create sagemaker session
        self.boto_session: boto3.session.Session = boto3.session.Session(
            profile_name=profile_name
        )
        self.sagemaker_session: sagemaker.Session = sagemaker.Session(self.boto_session)

        self.bucket: str = bucket
        self.bucket_prefix: str = bucket_prefix
        self.s3_train: str = f"s3://{bucket}/{bucket_prefix}/train"
        self.s3_validation: str = f"s3://{bucket}/{bucket_prefix}/validation"

        self.cache_dir: str = cache_dir
        self.s3_image_inference = "image_inference"
        self.s3_pred_inference = "pred_inference"

        # Unintialized
        self.predictor: Optional[Any] = None
        self.runtime: Optional[Any] = None
        self.tuning_job_name: Optional[str] = tuning_job

    def upload_images_to_s3(
        self,
        image_dir: str,
    ):
        """
        Upload image directory to s3.

        Parameters
        -------------
        image_dir: str
            Sub folder where images are stored.
            They will be uploaded to s3 under the same folder.
        """
        self.sagemaker_session.upload_data(
            path=image_dir,
            bucket=self.bucket,
            key_prefix=f"{self.bucket_prefix}/{self.s3_image_inference}",
        )

    def download_predictions_from_s3(self, inference_dir: str):
        """
        Download predictions from client s3.

        Predictions are stored in folder self.s3_image_inference in client
        s3 bucket. Function will download them to inference_dir.

        Parameters
        -------------
        inference_dir: str
            Local directory in which inferences
            will be downloaded.
        """
        self.sagemaker_session.download_data(
            path=inference_dir,
            bucket=self.bucket,
            key_prefix=f"{self.bucket_prefix}/{self.s3_pred_inference}",
        )

    def upload_to_s3(self) -> None:
        """Upload files to s3 for training and validation."""
        self.sagemaker_session.upload_data(
            path=os.path.join(self.cache_dir, "annotation_redbrick_validation.rec"),
            bucket=self.bucket,
            key_prefix=f"{self.bucket_prefix}/validation",
        )
        self.sagemaker_session.upload_data(
            path=os.path.join(self.cache_dir, "annotation_redbrick_train.rec"),
            bucket=self.bucket,
            key_prefix=f"{self.bucket_prefix}/train",
        )

    def launch_tuning_job(self, total_training_samples: int):
        """Launch a hyperparameter tuning job."""
        training_image = get_image_uri(
            self.sagemaker_session.boto_region_name,
            "object-detection",
            repo_version="latest",
        )
        self.tuning_job_name = f"redbrick-{str(uuid.uuid4())}"[0:32]
        tuning_job_config = construct_tuning_job(
            num_training_samples=total_training_samples
        )
        training_job_config = construct_training_job(
            training_image=training_image,
            train_uri=self.s3_train,
            validation_uri=self.s3_validation,
            bucket=self.bucket,
            num_classes=3,
            num_training_samples=total_training_samples,
            sagemaker_role=self.role,
        )
        smclient = self.boto_session.client("sagemaker")
        smclient.create_hyper_parameter_tuning_job(
            HyperParameterTuningJobName=self.tuning_job_name,
            HyperParameterTuningJobConfig=tuning_job_config,
            TrainingJobDefinition=training_job_config,
        )

    def transform(self):
        """Create a transformer, and start transform."""
        _, model_name = self.best_training_job()
        model = self.sagemaker_session.create_model_from_job(model_name)

        # create the location path for storing predictions,
        # and create transformer
        output_path = (
            f"s3://{self.bucket}/{self.bucket_prefix}/{self.s3_pred_inference}"
        )
        transformer = sagemaker.transformer.Transformer(
            model_name=model,
            instance_count=1,
            instance_type="ml.m4.xlarge",
            output_path=output_path,
        )

        # specify location of images for predictions, and begin transform
        in_path = (
            f"s3://{self.bucket}/" + f"{self.bucket_prefix}/{self.s3_image_inference}"
        )
        transformer.transform(in_path, content_type="image/jpeg", logs=False)

    def best_training_job(self) -> Tuple[bool, str]:
        """Return the best training job."""
        tuner = sagemaker.tuner.HyperparameterTuner.attach(self.tuning_job_name)
        try:
            best_job = tuner.best_training_job()
            return True, best_job
        except Exception as error:  # pylint: disable=broad-except
            return False, str(error)

    def describe(self, log: bool = True) -> Dict:
        """Check the status of the tuning job."""
        tuner = sagemaker.tuner.HyperparameterTuner.attach(self.tuning_job_name)
        describe = tuner.describe()

        if log:
            # Log useful info
            logger.info(
                "INFO: Your tuning job is %s",
                describe["HyperParameterTuningJobStatus"],
            )
            logger.info(
                "INFO: Summary of training jobs: %s",
                json.dumps(describe["TrainingJobStatusCounters"], indent=2),
            )
        return describe

    def deploy_model(self, model_name):
        """Deploy model to endpoint, and init self."""
        estimator = sagemaker.estimator.Estimator.attach(model_name)
        predictor = estimator.deploy(
            initial_instance_count=1, instance_type="ml.m4.xlarge"
        )
        self.predictor = predictor
        self.runtime = boto3.client(service_name="runtime.sagemaker")

    def predict(self, image_bytes: bytearray) -> Dict[Any, Any]:
        """Make a prediction using deployed predictor."""
        if not self.runtime:
            raise Exception("No runtime!")
        if not self.predictor:
            raise Exception("No predictor!")

        endpoint_response = self.runtime.invoke_endpoint(
            EndpointName=self.predictor.endpoint,
            ContentType="image/jpeg",
            Body=image_bytes,
        )
        results = endpoint_response["Body"].read()
        detections = json.loads(results)
        return detections

    def wait_for_tuning(self):
        """Wait for tuning job."""
        tuner = sagemaker.tuner.HyperparameterTuner.attach(self.tuning_job_name)
        tuner.wait()

    def delete_endpoint(self):
        """Delete a deployed endpoint."""
        # No deployed predictor
        if self.predictor is None:
            return

        endpoint_name = self.predictor.endpoint_name
        client = boto3.client("sagemaker")
        client.delete_endpoint(EndpointName=endpoint_name)
