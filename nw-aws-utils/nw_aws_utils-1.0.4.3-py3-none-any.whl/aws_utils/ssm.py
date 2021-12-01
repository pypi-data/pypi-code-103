"""Functions for fetching parametes from SSM.
"""
import os
from boto3 import client as boto3_client
from botocore.exceptions import ClientError, NoCredentialsError, NoRegionError
from aws_utils.exceptions import SsmError

def env_or_ssm(env_key=None, ssm_key=None, required=True, aws_region=None,
               aws_access_key_id=None, aws_secret_access_key=None):
    """Try to get an environmet variable first from env, then AWS SSM.
    Raises error if required is True.
    """
    value = None

    # 1. try to get from env
    if env_key is not None:
        value = os.environ.get(env_key)

    # 2. try to get from SSM
    if value is None or value == "":
        try:
            value = get_ssm_parameter(ssm_key, aws_region=aws_region,
                                      aws_access_key_id=aws_access_key_id,
                                      aws_secret_access_key=aws_secret_access_key)
        except NoCredentialsError:
            pass

    # 3. Error if required
    if (value is None or value == "") and required:
        raise SsmError("Required setting undefined. Set {} in environment or "
                       "or {} in AWS SSM.".format(env_key, ssm_key))

    return value


def get_ssm_parameter(key, aws_region=None, aws_access_key_id=None,
                      aws_secret_access_key=None):
    """Fetch value of an AWS SSM parameter.

    `aws_region`,  `aws_access_key_id` and `aws_secret_access_key` may be
    defined if you haven't set them up in your environment or if you want to
    override the environment.
    Read more about setting up credentials here:
    https://boto3.amazonaws.com/v1/documentation/api/latest/guide/configuration.html#configuring-credentials
    """
    client_params = {}
    if aws_region is not None:
        client_params["region_name"] = aws_region
    if aws_access_key_id is not None:
        client_params["aws_access_key_id"] = aws_access_key_id
    if aws_secret_access_key is not None:
        client_params["aws_secret_access_key"] = aws_secret_access_key

    try:
        ssm_client = boto3_client('ssm', **client_params)
        resp = ssm_client.get_parameter(Name=key, WithDecryption=True)
        val = resp['Parameter']['Value']
    except (ClientError, NoRegionError) as e:
        val = None
    return val
