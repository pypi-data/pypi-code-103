"""Active Learning."""
from typing import Dict, Optional, Tuple

import json
import os

import redbrick
from redbrick_sagemaker.logging import logger
from redbrick_sagemaker.utils.bbox import (
    convert_redbrick_to_sagemaker,
    convert_sagemaker_rbai_bbox,
)
from redbrick_sagemaker.utils.redbrick import (
    create_taxonomy_map,
)
from redbrick_sagemaker.utils.dataio import download_images_from_remote
from redbrick_sagemaker.sagemaker_client import SagemakerClient


class ActiveLearner:
    """Runs the Active Learning process."""

    def __init__(
        self,
        api_key: str,
        org_id: str,
        project_id: str,
        s3_bucket: str,
        s3_bucket_prefix: str,
        tuning_job: Optional[str] = None,
        url: Optional[str] = "https://api.redbrickai.com",
        iam_role: Optional[str] = None,
    ):
        """Construct object."""
        self.project_id: str = project_id
        self.org_id: str = org_id
        self.api_key: str = api_key

        # get redbrick ai project object
        self.project: redbrick.RBProject = redbrick.get_project(
            api_key, url, org_id, project_id
        )

        # prepare cache directory
        self.cache_dir = ".redbrick_sagemaker"
        os.makedirs(self.cache_dir, exist_ok=True)

        # prepare sagemaker client
        self.sagemaker_client = SagemakerClient(
            bucket=s3_bucket,
            bucket_prefix=s3_bucket_prefix,
            iam_role=iam_role,
            cache_dir=self.cache_dir,
            tuning_job=tuning_job,
            project_id=self.project_id,
        )

        # info for learning and inference
        self.info: Optional[Dict] = None

    def _get_learning_info(self):
        """Get learning info for active learning."""
        info = self.project.learning2.get_learning_info(min_new_tasks=0)
        with open(
            os.path.join(self.cache_dir, "cache__info.json"),
            "w+",
            encoding="Utf-8",
        ) as file:
            json.dump(info, file, indent=2)

        return info

    def _update_info(self):
        """Update info object."""
        # if self.info is None:
        self.info = self._get_learning_info()

    def train(self):
        """Launch a training job."""
        # Get info from RBAI remote - for learning and inference
        logger.info("Begining a hyperparameter optimization job.")

        self._update_info()
        self.project.learning2.start_processing()

        try:
            # Create training files required by sagemaker, upload to s3
            _, total_training_samples = convert_redbrick_to_sagemaker(
                self.info, cache_dir=self.cache_dir
            )

            logger.info("Uploading training files to s3.")
            self.sagemaker_client.upload_to_s3()

            logger.info("Launching tuning job.")
            # Launch a tuning job
            self.sagemaker_client.launch_tuning_job(total_training_samples)

        except Exception as error:
            # clean up
            self.project.learning2.end_processing()
            raise Exception from error

    def inference(self):
        """Perform inference on unlabeled data."""
        try:
            # Get updated unlabeled tasks from rbai
            self._update_info()
            unlabeled_tasks = self.info["unlabeled"]

            # Download images from remote rbai storage
            logger.info("Downloading images from RedBrick AI.")
            download_images_from_remote(
                self.cache_dir, "images_inference", unlabeled_tasks
            )

            # Upload images for inference to client s3 bucket
            logger.info("Uploading images to client s3 bucket for inference.")
            self.sagemaker_client.upload_images_to_s3(
                os.path.join(self.cache_dir, "images_inference")
            )

            # Begin batch transform job to generate predictions
            logger.info(
                "Starting transform operation to generate %s",
                " predictions in a batch.",
            )
            self.sagemaker_client.transform()

            # Download predictions from client s3
            logger.info("Retrieving predictions from client s3.")
            self.sagemaker_client.download_predictions_from_s3(
                os.path.join(self.cache_dir, "pred_inference")
            )

            # Post process predictions, and convert to RedBrick format
            taxonomy_map, _ = create_taxonomy_map(
                self.info["taxonomy"]["categories"][0]["children"]
            )
            labeled_tasks = convert_sagemaker_rbai_bbox(
                prediction_dir=os.path.join(self.cache_dir, "pred_inference"),
                tasks=unlabeled_tasks,
                taxonomy=taxonomy_map,
            )

        except Exception as error:
            # Clean up endpoint
            raise Exception from error

        return labeled_tasks

    def _status(self) -> Tuple[bool, str]:
        """Check status of training job."""
        return self.sagemaker_client.best_training_job()

    def describe(self):
        """Describe status."""
        self.sagemaker_client.describe()

    def end_processing(self):
        """Force stop processing."""
        self.project.learning2.end_processing()

    def start_processing(self):
        """Force start processing."""
        self.project.learning2.start_processing()

    def run(self, wait: bool = False, force_run: bool = False):
        """Run active learning cycle."""
        is_processing = self.project.learning2.check_is_processing()
        # Check if a tuning job is in progress
        if is_processing:
            # Check if the tuning job is complete
            describe = self.sagemaker_client.describe(log=False)
            tuning_complete = describe["HyperParameterTuningJobStatus"] == "Completed"

            # Check if user wants to perform inference with best model
            if force_run or tuning_complete:
                check, _ = self._status()

                if not check:
                    self.sagemaker_client.describe()

                    jobname = self.sagemaker_client.tuning_job_name
                    raise Exception(
                        f"Your tuning job {jobname}"
                        + " doesn't have a best model it can use"
                        + " for inference yet."
                    )

                # Use best model is available for inference
                logger.info("Starting the inference process on unlabeled data.")
                labeled_tasks = self.inference()

                logger.info(
                    "Updating tasks on RedBrick with %s",
                    "predictions and uncertainty scores.",
                )
                self.project.learning2.update_tasks(1, labeled_tasks)
                self.project.learning2.end_processing()

            else:
                logger.warning("An Active learning process is already in progress.")

        else:
            self.train()
            if wait:
                self.sagemaker_client.wait_for_tuning()

                # Perform inference
                check, _ = self._status()
                labeled_tasks = self.inference()
                self.project.learning2.update_tasks(1, labeled_tasks)
                self.project.learning2.end_processing()
