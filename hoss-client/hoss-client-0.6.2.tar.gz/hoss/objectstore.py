from typing import Optional

import boto3
from boto3.s3.transfer import TransferConfig
import botocore.exceptions
import datetime

from hoss.api import CoreAPI
from hoss.auth import AuthService


class ObjectStore(CoreAPI):
    def __init__(self, object_store_name: str, description: str, endpoint: str, object_store_type: str,
                 server_url: str, auth_instance: Optional[AuthService] = None):
        """A class to interact with the Hoss core service
        
        Args:
            object_store_name: name of the object store
            description: description of the store
            endpoint: object store endpoint (e.g. http://localhost, https://s3.amazonaws.com)
            object_store_type: type of object store (e.g. "s3", "minio")
        """
        super().__init__(server_url, auth_instance)

        self.name = object_store_name
        self.description = description
        self.endpoint = endpoint
        self.object_store_type = object_store_type

        # S3 client
        self._client = dict()
        self._transfer_config = TransferConfig()
        self._sts_credential_expire = None
        self._sts_credential_expire_in_seconds = self.auth.jwt_exp_seconds / 2

    def __repr__(self):
        return f"<Object Store: {self.name} - {self.description} ({self.endpoint})>"

    def _get_sts_credentials(self, namespace: str) -> dict:
        return self._request("GET", f"/namespace/{namespace}/sts")

    def _get_client(self, namespace: str):
        if self._client.get(namespace) is not None:
            if self._sts_credential_expire > datetime.datetime.utcnow():
                # Credentials are still good. Return existing client.
                return self._client.get(namespace)

        # Fetch temporary credentials and create an S3 client
        creds = self._get_sts_credentials(namespace)
        self._sts_credential_expire = datetime.datetime.utcnow() + \
                                      datetime.timedelta(seconds=self._sts_credential_expire_in_seconds)

        client = boto3.client(
            "s3",
            endpoint_url=creds["endpoint"],
            aws_access_key_id=creds["access_key_id"],
            aws_secret_access_key=creds["secret_access_key"],
            aws_session_token=creds["session_token"],
            region_name=creds["region"]
        )
        self._client[namespace] = client
        return client

    def object_exists(self, namespace: str, bucket: str, key):
        # TODO: Need to handle grabbing metadata here better
        client = self._get_client(namespace)

        try:
            client.head_object(Bucket=bucket, Key=key)
            return True
        except botocore.exceptions.ClientError as ce:
            code = ce.response["Error"]["Code"]
            if code == '404':
                return False
            raise

    def head_object(self, namespace: str, bucket: str, key) -> dict:
        client = self._get_client(namespace)
        response = client.head_object(Bucket=bucket, Key=key)
        return {"last_modified": response.get('LastModified'),
                "size_bytes": response.get('ContentLength'),
                "etag": response.get('ETag'),
                "metadata": response.get('Metadata')}

    @staticmethod
    def _remove_prefix(text, prefix):
        return text[text.startswith(prefix) and len(prefix):]

    def list_objects(self, namespace: str, bucket: str, prefix, recursive=False):
        client = self._get_client(namespace)

        kwargs = {
            "Bucket": bucket,
            "Delimiter": "/",
        }

        if recursive:
            del kwargs["Delimiter"]

        if not prefix.endswith('/'):
            prefix += '/'
        kwargs["Prefix"] = prefix

        paginator = client.get_paginator("list_objects_v2")
        for resp in paginator.paginate(**kwargs):
            for d in resp.get("CommonPrefixes", []):
                yield {"key": d["Prefix"],
                       "name": self._remove_prefix(d["Prefix"], prefix),
                       "etag": d.get("ETag"),
                       "last_modified": d.get("LastModified"),
                       "size_bytes": d.get("Size")}

            for f in resp.get("Contents", []):
                yield {"key": f["Key"],
                       "name": self._remove_prefix(f["Key"], prefix),
                       "etag": f.get("ETag"),
                       "last_modified": f.get("LastModified"),
                       "size_bytes": f.get("Size")}

    def get_object(self, namespace: str, bucket: str, key):
        # TODO: Need to handle grabbing metadata here better
        client = self._get_client(namespace)
        return client.get_object(Bucket=bucket, Key=key)["Body"].read()

    def put_object(self, namespace: str, bucket: str, key, data, metadata: Optional[dict] = None):
        client = self._get_client(namespace)
        client.put_object(Bucket=bucket, Key=key, Body=data,
                          Metadata=metadata if metadata is not None else dict())

    def delete_object(self, namespace: str, bucket: str, key):
        client = self._get_client(namespace)
        client.delete_object(Bucket=bucket, Key=key)

    def copy_object(self, namespace: str, bucket: str, key, target_key):
        client = self._get_client(namespace)
        source = {"Bucket": bucket, "Key": key}
        client.copy_object(Bucket=bucket, Key=target_key, CopySource=source)

    def download_file(self, namespace: str, bucket: str, key, filename):
        client = self._get_client(namespace)
        return client.download_file(bucket, key, filename, Config=self._transfer_config)

    def download_fileobj(self, namespace: str, bucket: str, key, fh):
        client = self._get_client(namespace)
        return client.download_fileobj(bucket, key, fh, Config=self._transfer_config)

    def upload_file(self, namespace: str, bucket: str, key, filename, metadata: Optional[dict] = None):
        client = self._get_client(namespace)
        return client.upload_file(filename, bucket, key, Config=self._transfer_config,
                                  ExtraArgs={"Metadata": metadata} if metadata is not None else None)

    def upload_fileobj(self, namespace: str, bucket: str, key, fh, metadata: Optional[dict] = None):
        client = self._get_client(namespace)
        return client.upload_fileobj(fh, bucket, key, Config=self._transfer_config,
                                     ExtraArgs={"Metadata": metadata} if metadata is not None else None)

    def set_transfer_config(self, multipart_threshold, max_concurrency):
        self._transfer_config = TransferConfig(
            multipart_threshold=multipart_threshold,
            max_concurrency=max_concurrency
        )
