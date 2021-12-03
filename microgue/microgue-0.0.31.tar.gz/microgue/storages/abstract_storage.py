import boto3
import logging
import os
import uuid
from pathlib import Path

logger = logging.getLogger('microgue')


class DownloadFailed(Exception):
    pass


class UploadFailed(Exception):
    pass


class DeleteFailed(Exception):
    pass


class AbstractStorage:
    class File:
        def __init__(self, remote_path=None, local_path=None, url=None):
            self.remote_path = remote_path
            self.local_path = local_path
            self.url = url

    bucket_name = ''
    bucket_public_url = ''

    def __init__(self, *args, **kwargs):
        self.storage = boto3.client('s3')

    def upload(self, local_file_path, remote_file_path=None):
        if remote_file_path is None:
            remote_file_path = str(uuid.uuid4()) + '-' + local_file_path.split('/')[-1]

        logger.debug("########## {} Upload ##########".format(self.__class__.__name__))
        logger.debug("local_file_path: {}".format(local_file_path))
        logger.debug("remote_file_path: {}".format(remote_file_path))

        try:
            self.storage.upload_file(local_file_path, self.bucket_name, remote_file_path)
        except Exception as e:
            logger.error("########## {} Upload Error".format(self.__class__.__name__))
            logger.error("{}: {}".format(e.__class__.__name__, str(e)))
            raise UploadFailed(str(e))

        return self.File(
            remote_path=remote_file_path,
            local_path=local_file_path,
            url=self.bucket_public_url + '/' + remote_file_path
        )

    def download(self, remote_file_path, local_file_path=None):
        if local_file_path is None:
            local_file_path = os.getcwd() + '/' + remote_file_path

        # ensure local_file_path directories exist
        Path(os.path.dirname(local_file_path)).mkdir(parents=True, exist_ok=True)

        logger.debug("########## {} Download ##########".format(self.__class__.__name__))
        logger.debug("remote_file_path: {}".format(remote_file_path))
        logger.debug("local_file_path: {}".format(local_file_path))

        try:
            self.storage.download_file(self.bucket_name, remote_file_path, local_file_path)
        except Exception as e:
            logger.error("########## {} Download Error".format(self.__class__.__name__))
            logger.error("{}: {}".format(e.__class__.__name__, str(e)))
            raise DownloadFailed(str(e))

        return self.File(
            remote_path=remote_file_path,
            local_path=local_file_path,
            url=self.bucket_public_url + '/' + remote_file_path
        )

    def delete(self, remote_file_path):
        logger.debug("########## {} Delete ##########".format(self.__class__.__name__))
        logger.debug("remote_file_path: {}".format(remote_file_path))

        try:
            self.storage.delete_object(Bucket=self.bucket_name, Key=remote_file_path)
        except Exception as e:
            logger.error("########## {} Delete Error".format(self.__class__.__name__))
            logger.error("{}: {}".format(e.__class__.__name__, str(e)))
            raise DeleteFailed(str(e))

        return True
