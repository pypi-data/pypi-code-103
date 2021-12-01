import os
from dataclasses import dataclass


@dataclass
class S3Connection:
    aws_access_key_id: str = os.environ.get("AWS_ACCESS_KEY_ID")
    aws_access_secret_key: str = os.environ.get("AWS_ACCESS_KEY_SECRET")
    aws_endpoint_url: str = os.environ.get("AWS_ENDPOINT_URL")
