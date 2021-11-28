""" This module implement data functionality  """
import json
import re
from typing import List
from typing import Optional

import boto3 as boto3
import google
from google.cloud import storage
from google.oauth2 import service_account as GCPServiceAccount

from superwise import Config
from superwise.controller.base import BaseController
from superwise.controller.exceptions import SuperwiseStorageDownloadGCSError
from superwise.controller.exceptions import SuperwiseStorageDownloadS3Error
from superwise.controller.exceptions import SuperwiseStorageUploadGCSError
from superwise.controller.exceptions import SuperwiseValidationException
from superwise.models.task import Task


class TransactionController(BaseController):
    """Transaction Controller is in-charge for create transaction using file and batch request """

    def __init__(self, client, sw):
        """
        constructer for DataController class

        :param client:

        """
        super().__init__(client, sw)
        self.path = "gateway/v1/transaction"
        self.model_name = None
        _bucket_name = "superwise-{}-{}".format(self.client.tenant_id, Config.ENVIRONMENT)
        self._gcs_internal_bucket = self._create_gcs_bucket_connection(
            bucket_name=_bucket_name, service_account=self.client.service_account
        )

    def _create_gcs_bucket_connection(self, bucket_name, service_account):
        try:
            self.logger.debug(f"Create connection to superwise bucket {bucket_name}")
            credentials = GCPServiceAccount.Credentials.from_service_account_info(service_account)
            gcs_client = storage.Client(credentials=credentials)
            return gcs_client.bucket(bucket_name)
        except Exception as e:
            self.logger.error(f"Error create connection to superwise bucket {bucket_name}")
            raise Exception(f"Error create connection to superwise bucket {bucket_name}")

    def _extract_directory(self, url: str):
        bucket = url.split("/")[2]
        prefix = "/".join(url.split("/")[3:])
        return bucket, prefix

    def _upload_string_to_internal_bucket(self, data, file_name):
        try:
            self.logger.debug(f"Upload file to superwise bucket {file_name}")
            blob = self._gcs_internal_bucket.blob(file_name)
            blob.upload_from_string(data=data)
            return f"gs://{self._gcs_internal_bucket.name}/{file_name}"
        except google.api_core.exceptions.Forbidden as e:
            if "does not have storage.objects.delete access" in e.message:
                self.logger.error(f"Failed upload file to superwise bucket because {file_name} already exist")
                raise SuperwiseStorageUploadGCSError(
                    f"Failed upload file to superwise bucket because {file_name} already exist"
                )
            raise SuperwiseStorageUploadGCSError(f"Failed upload file to superwise storage {file_name}")
        except Exception as e:
            self.logger.error(f"Failed upload file to superwise storage {file_name}")
            raise SuperwiseStorageUploadGCSError(f"Failed upload file to superwise storage {file_name}")

    def log_batch(self, task_id: str, records: List[dict], version_id: Optional[str] = None):
        """
        stream data of a given file path

        :param
        - task_id: string - model which the data associated to him.
        - version_id: string - version of the model -   Optional
        - records: List[dict] - list of records of data,  each record is a dict.
        :return transaction_id
        """
        self.logger.info("transaction batch")
        payload = dict(records=records, task_id=task_id)
        if version_id is not None:
            payload["version_id"] = version_id
        r = self.client.post(self.build_url("{}".format(self.path + "/batch")), payload)
        self.logger.info("file_log server response: {}".format(r.content))
        if r.status_code == 201:
            return r.json()
        else:
            raise Exception("send records to superwise failed, server error")

    def log_from_s3(self, file_path, aws_access_key_id, aws_secret_access_key):
        if not str(file_path).startswith("s3://"):
            self.logger.error(f"Failed upload file to superwise storage {file_path}")
            raise Exception("file_path must start with 's3://'")
        try:
            self.logger.info("Download file {} from s3".format(file_path))
            bucket, key = self._extract_directory(file_path)
            s3_client = boto3.client(
                "s3", aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key
            )
            resp = s3_client.get_object(Bucket=bucket, Key=key)
            content = resp["Body"]
        except Exception as e:
            self.logger.error(f"Error download file from customer s3 bucket {file_path}")
            raise SuperwiseStorageDownloadS3Error(f"Error download file from customer s3 bucket {file_path}")
        superwise_file_path = self._upload_string_to_internal_bucket(data=content.read(), file_name=key)
        return self.log_file(file_path=superwise_file_path, _origin_path=file_path)

    def log_from_gcs(self, file_path, service_account):
        if not str(file_path).startswith("gs://"):
            self.logger.error("Failed upload file to superwise storage")
            raise Exception("file_path must start with 'gs://'")
        self.logger.info("Download file {} from gcs".format(file_path))
        bucket, key = self._extract_directory(file_path)
        try:
            customer_bucket = self._create_gcs_bucket_connection(bucket, service_account)
            blob = customer_bucket.blob(key)
            data = blob.download_as_string()
        except Exception as e:
            self.logger.error(f"Error download file {file_path} from gcs")
            raise SuperwiseStorageDownloadGCSError(f"Error download file {file_path} from gcs")
        superwise_file_path = self._upload_string_to_internal_bucket(data=data, file_name=key)
        return self.log_file(file_path=superwise_file_path, _origin_path=file_path)

    def log_file(self, file_path, _origin_path=None):
        """
        stream data of a given file path
        :param file_path: url for file stored in cloud str
        :param _origin_path: url for file stored in customer bucket - for internal usage
        :return transaction_id
        """
        self.logger.info("transaction file %s ", file_path)
        pattern = "(s3|gs)://.+"
        if not re.match(pattern, file_path):
            raise SuperwiseValidationException(
                "transaction file failed because of wrong file path. file path should be gcs or s3 path."
            )
        params = {"file": file_path}
        if _origin_path is not None:
            params["origin_path"] = _origin_path
        r = self.client.post(url=self.build_url("{}".format(self.path + "/file")), params=params)
        self.logger.info("transaction file server response: {}".format(r.content))
        if r.status_code == 201:
            return r.json()
        else:
            raise Exception("send file to superwise failed, server error")
