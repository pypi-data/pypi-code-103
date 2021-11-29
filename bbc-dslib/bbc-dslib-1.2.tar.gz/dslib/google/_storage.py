import logging
import os
from typing import Optional

from six.moves.urllib.parse import quote

from dslib.utils import ensure_directory_exists

try:
    from google.cloud import storage
    from google.cloud.exceptions import NotFound
except ImportError as e:
    raise ImportError('Please install "google" extra packages.') from e

# Set up logger
logging.getLogger('oauth2client').setLevel(logging.WARNING)  # Silence google authentication
LOGGER = logging.getLogger(__name__)

# Set up special types
BucketType = storage.bucket.Bucket


class StorageWrapper(object):

    def __init__(self, client, default_bucket: Optional[str] = None) -> None:
        if not client.__class__.__name__ == 'Client':
            raise ValueError('"client" argument must be a Google "Client" instance')
        self.client = client
        self.default_bucket_name = default_bucket

    @classmethod
    def from_params(cls, project: str, default_bucket: Optional[str] = None, auth_file: Optional[str] = None):
        if auth_file:
            if not os.path.exists(auth_file):
                raise FileNotFoundError(f'Authentication file does not exist: {auth_file}')
            client = storage.Client.from_service_account_json(auth_file, **{'project': project})
        else:
            client = storage.Client(project=project)
        return StorageWrapper(client, default_bucket)

    def _require_bucket(self, bucket_name: Optional[str] = None) -> BucketType:
        bucket_name = bucket_name or self.default_bucket_name
        if not bucket_name:
            raise ValueError('You need to specify a bucket_name, either at wrapper level or function level')
        return self.client.bucket(bucket_name)

    def upload_file(self, source_filepath: str, destination_filepath: str, bucket_name: Optional[str] = None,
                    replace: bool = False) -> None:
        """
        Upload a file to Google Cloud Storage.
        :param source_filepath: (str) local path of the file to upload
        :param destination_filepath: (str) path to the destination file in the bucket
        :param bucket_name: (str) name of the bucket in which the file should be uploaded (if None, the default bucket
            of the StorageWrapper instance will be used)
        :param replace: (bool) replace the file if it already exists when set to True. Defaults to False
        :return: None
        """
        bucket = self._require_bucket(bucket_name)
        blob = bucket.blob(destination_filepath)
        if replace is False and blob.exists():
            raise FileExistsError(f'gs://{bucket.name}/{destination_filepath} already exists')
        with open(source_filepath, 'rb') as fileobj:
            blob.upload_from_file(fileobj)
        LOGGER.info(f'Uploaded file {source_filepath} to gs://{bucket.name}/{destination_filepath}')

    def download_file(self, source_filepath: str, destination_filepath: str, bucket_name: Optional[str] = None) -> None:
        """
        Downloads a file from Google Cloud Storage.
        :param source_filepath: (str) path of the distant file to download
        :param destination_filepath: (str) local path to store the downloaded file to
        :param bucket_name: (str) bucket name of the file to download (if None, the default bucket of the StorageWrapper
            instance will be used)
        :return: None
        """
        bucket = self._require_bucket(bucket_name)
        blob = bucket.blob(source_filepath)
        with ensure_directory_exists(os.path.dirname(destination_filepath)):
            try:
                blob.download_to_filename(destination_filepath)
            except NotFound as exception:
                raise FileNotFoundError(f'Could not download {source_filepath}') from exception
            except Exception as exception:
                if os.path.exists(destination_filepath):
                    os.remove(destination_filepath)
                LOGGER.error(f'Could not download file gs://{bucket.name}/{source_filepath} to {destination_filepath}')
                raise exception
            else:
                LOGGER.info(f'Downloaded file gs://{bucket.name}/{source_filepath} to {destination_filepath}')

    def delete_file(self, filepath: str, bucket_name: Optional[str] = None) -> None:
        """
        Delete a file from Google Cloud Storage.
        :param filepath: path of the distant file to delete
        :param bucket_name: bucket name of the file to delete (if None, the default bucket of the StorageWrapper
            instance will be used)
        :return: None
        """
        bucket = self._require_bucket(bucket_name)
        blob = bucket.blob(filepath)
        try:
            blob.delete()
            LOGGER.info(f'Deleted file gs://{bucket.name}/{filepath}')
        except NotFound:
            LOGGER.warning(f'Could not delete gs://{bucket.name}/{filepath}: file file not found')

    def exists(self, filepath: str, bucket_name: Optional[str] = None) -> bool:
        """
        Check the existence of a file from Google Cloud Storage.
        :param filepath: path of the distant file to check the existence of
        :param bucket_name: bucket name of the file to check the existence of (if None, the default bucket of the
            StorageWrapper instance will be used)
        :return: True if the file exists, False otherwise
        """
        bucket = self._require_bucket(bucket_name)
        blob = bucket.blob(filepath)
        exists = blob.exists()
        LOGGER.debug(f"File {filepath} {'exists' if exists else 'does not exist'}")
        return exists

    def get_public_url(self, filepath: str, bucket_name: Optional[str] = None) -> str:
        """
        Make a distant file from Google Cloud Storage public and get its public URL.
        :param filepath: path of the distant file to make public and to get the URL from
        :param bucket_name: bucket name of the file to make public and get the URL of (if None, the default bucket of
            the StorageWrapper instance will be used)
        :return: public URL of the file
        """
        bucket = self._require_bucket(bucket_name)
        blob = bucket.blob(filepath)
        blob.make_public()
        LOGGER.warning(f'gs://{bucket.name}/{filepath} was made public')
        return f'{"https://storage.googleapis.com"}/{bucket.name}/{quote(filepath)}'
