# -*- coding: utf-8 -*-

import boto3
import botocore.exceptions


class s3_server:
    def __init__(self, bucket, region):
        self.bucket = bucket
        self.region = region
        self.client = boto3.client("s3", region_name=region)

    def get_files_and_folders(self, prefix="", continuation_token="", max_keys=1000):
        """
        Get the files and folders that exist at a given prefix. This will
        retrieve max_keys files (default 1000). If there are more files
        available, next_continuation_token will be returned. If it's
        provided as continuation_token, the next set of files will fetched.

        Returns a tuple that contains a list of files, a list of folders,
        and next_continuation_token.
        """
        kwargs = {
            "Bucket": self.bucket,
            "Prefix": prefix,
            "Delimiter": "/",
            "MaxKeys": max_keys,
        }
        if continuation_token:
            # Only set if continuation_token is set
            kwargs["ContinuationToken"] = continuation_token
        page = self.client.list_objects_v2(**kwargs)

        files = []
        folders = []
        next_continuation_token = ""
        for key_prefix in page.get("CommonPrefixes", []):
            if prefix in key_prefix.get("Prefix"):
                folders.append(key_prefix.get("Prefix"))
        for s3_object in page.get("Contents", []):
            if s3_object["Size"] == 0:
                continue
            files.append(s3_object)
        if page.get("IsTruncated"):
            next_continuation_token = page.get("NextContinuationToken", "")
        return (files, folders, next_continuation_token)

    def key_exists(self, key):
        """Try to fetch the metadata for an object. If the object does not
        exist, head_object will raise an exception. Returns True if the
        object exists
        """
        try:
            head = self.client.head_object(Bucket=self.bucket, Key=key)
            if head.get("ContentLength") == 0:
                # Disregard empty objects
                return (False, None)
        except (
            botocore.exceptions.ParamValidationError,
            botocore.exceptions.ClientError,
        ):
            return (False, None)
        return (True, head)

    def create_signed_url(self, key):
        return self.client.generate_presigned_url(
            "get_object", Params={"Bucket": self.bucket, "Key": key}, ExpiresIn=90
        )
