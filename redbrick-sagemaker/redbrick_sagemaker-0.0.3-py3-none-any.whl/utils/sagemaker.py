"""Sagemaker related helper functions."""


from typing import Any, Optional


def construct_training_job(
    training_image: Any,
    train_uri: str,
    validation_uri: str,
    bucket: str,
    num_classes: int,
    num_training_samples: int,
    sagemaker_role: str,
    max_epochs: Optional[int] = 200,
    instance_type: Optional[str] = "ml.p2.xlarge",
):
    """Construct a training job object to configure sagemaker."""
    training_job_definition = {
        "AlgorithmSpecification": {
            "TrainingImage": training_image,
            "TrainingInputMode": "File",
        },
        "InputDataConfig": [
            {
                "ChannelName": "train",
                "CompressionType": "None",
                "ContentType": "application/x-recordio",
                "DataSource": {
                    "S3DataSource": {
                        "S3DataDistributionType": "FullyReplicated",
                        "S3DataType": "S3Prefix",
                        "S3Uri": train_uri,
                    }
                },
            },
            {
                "ChannelName": "validation",
                "CompressionType": "None",
                "ContentType": "application/x-recordio",
                "DataSource": {
                    "S3DataSource": {
                        "S3DataDistributionType": "FullyReplicated",
                        "S3DataType": "S3Prefix",
                        "S3Uri": validation_uri,
                    }
                },
            },
        ],
        "OutputDataConfig": {"S3OutputPath": f"s3://{bucket}/output"},
        "ResourceConfig": {
            "InstanceCount": 1,
            "InstanceType": instance_type,
            "VolumeSizeInGB": 20,
        },
        "RoleArn": sagemaker_role,
        "StaticHyperParameters": {
            "num_classes": str(num_classes),
            "num_training_samples": str(num_training_samples),
            "epochs": str(max_epochs),
            "use_pretrained_model": "1",
            "early_stopping": "True",
        },
        "StoppingCondition": {"MaxRuntimeInSeconds": 43200},
    }
    return training_job_definition


def construct_tuning_job(
    num_training_samples: int,
    max_jobs: Optional[int] = 10,
):
    """Construct tuning job to configure sagemaker."""
    # dynamically define batch size bounds
    min_batch = "8"
    max_batch = "32"
    if num_training_samples < 200:
        max_batch = "64"
    if num_training_samples < 80:
        max_batch = "16"
    if num_training_samples <= 50:
        raise Exception("You need at least 70 labeled images to train!")

    tuning_job_config = {
        "TrainingJobEarlyStoppingType": "Auto",
        "ParameterRanges": {
            "CategoricalParameterRanges": [
                {
                    "Name": "optimizer",
                    "Values": ["sgd", "adam", "rmsprop", "adadelta"],
                }
            ],
            "ContinuousParameterRanges": [
                {
                    "MinValue": "1e-6",
                    "MaxValue": "0.5",
                    "Name": "learning_rate",
                },
                {"MinValue": "0", "MaxValue": "0.999", "Name": "momentum"},
                {"MinValue": "0", "MaxValue": "0.999", "Name": "weight_decay"},
            ],
            "IntegerParameterRanges": [
                {
                    "MaxValue": max_batch,
                    "MinValue": min_batch,
                    "Name": "mini_batch_size",
                }
            ],
        },
        "ResourceLimits": {
            "MaxNumberOfTrainingJobs": max_jobs,
            "MaxParallelTrainingJobs": 1,
        },
        "Strategy": "Bayesian",
        "HyperParameterTuningJobObjective": {
            "MetricName": "validation:mAP",
            "Type": "Maximize",
        },
    }
    return tuning_job_config


def construct_warm_start_config(old_job_name: str):
    """Construct a warm start config."""
    warm_start_config = {
        "ParentHyperParameterTuningJobs": [
            {"HyperParameterTuningJobName": old_job_name}
        ],
        "WarmStartType": "TransferLearning",
    }
    return warm_start_config
