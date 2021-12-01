#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author: similraface
# @contact: yangwubing@molbreeding.com
# @software: PyCharm
# @file: s3help.py
# @time: 2021/12/1 11:43 上午
# @desc:
import os
import boto3
from batool import logger
from botocore.exceptions import ClientError
from batool.utils.fs import split_oss_path as split_path

protocol = ["s3", "s3a"]


def download_s3_file(oss_path, local_path):
    logger.info(f"downloading {oss_path} to {local_path}")
    s3_client = boto3.client('s3')
    bucket_name, object_name, _ = split_path(oss_path, protocol=protocol)
    return s3_client.download_file(bucket_name, object_name, local_path)


def upload_s3_file(file_name, oss_path):
    """Upload a file to an S3 bucket

    :param file_name: File to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """
    logger.info(f"upload {file_name} to {oss_path}")
    bucket, object_name, _ = split_path(oss_path, protocol=protocol)
    # If S3 object_name was not specified, use file_name
    if object_name is None or object_name == '':
        object_name = os.path.basename(file_name)
    # Upload the file
    s3_client = boto3.client('s3')
    try:
        response = s3_client.upload_file(file_name, bucket, object_name)
    except ClientError as e:
        logger.error(e)
        return False
    return True


def upload_dir_to_s3(dir_path, oss_dir_path, skip_filename=[]):
    bucket, object_name, _ = split_path(oss_dir_path, protocol=protocol)
    if os.path.exists(dir_path) and os.path.isdir(dir_path):
        for lpath in os.listdir(dir_path):
            if lpath in skip_filename:
                continue
            abs_path = os.path.join(dir_path, lpath)
            upload_s3_file(abs_path, oss_path=os.path.join(oss_dir_path, lpath))
    else:
        return False


def download_s3_dir_to_local(oss_dir_path, dir_path):
    pass
