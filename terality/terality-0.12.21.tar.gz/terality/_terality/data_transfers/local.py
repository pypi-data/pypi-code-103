from pathlib import Path
from typing import List

from common_client_scheduler.requests_responses import AwsCredentials

from .. import global_client
from ...exceptions import TeralityClientError


def upload_local_files(path: str, transfer_id: str, aws_credentials: AwsCredentials) -> None:
    """
    Copy files from a local directory to a Terality-owned S3 bucket.

    Args:
        path: path to a single file or a directory. If a directory, all files in the directory will be uploaded.
    """
    try:
        paths: List[str] = (
            [path]
            if Path(path).is_file()
            else [str(path_) for path_ in sorted(Path(path).iterdir())]
        )
        for file_num, _ in enumerate(paths):
            global_client().data_transfer().upload_local_file(
                aws_credentials, paths[file_num], f"{transfer_id}/{file_num}.data"
            )
    except FileNotFoundError as e:
        raise TeralityClientError(
            f"File '{path}' could not be found in your local directory, please verify the path. If your file is stored on the cloud, make sure your path starts with 's3://', 'abfs://', or 'az://'.",
        ) from e
