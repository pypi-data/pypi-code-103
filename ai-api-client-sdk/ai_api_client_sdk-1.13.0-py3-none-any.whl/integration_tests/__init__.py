import os
import random
import requests
from time import sleep

from ai_api_client_sdk.helpers.authenticator import Authenticator


def get_random_string(l=4):
    alphanumeric = 'abcdefghijklmnopqrstuvwxyz0123456789'
    return ''.join(random.choices(alphanumeric, k=l))


def get_intwdf_cluster_info():
    auth_url = os.getenv('XSUAA_AUTH_URL')
    client_id = os.getenv('XSUAA_CLIENT_ID')
    client_secret = os.getenv('XSUAA_CLIENT_SECRET')
    cluster_base_url = os.getenv('CLUSTER_BASE_URL')
    base_url = f"{cluster_base_url}/v2/lm"
    provisioning_base_url = f'{cluster_base_url}/v2/admin'
    return base_url, auth_url, client_id, client_secret, provisioning_base_url


def get_s3_bucket_info():
    oss_key = os.getenv('OSS_KEY')
    oss_bucket = os.getenv('OSS_BUCKET')
    oss_endpoint = os.getenv('OSS_ENDPOINT')
    oss_region = os.getenv('OSS_REGION')
    oss_secret = os.getenv('OSS_SECRET')
    return oss_bucket, oss_endpoint, oss_region, oss_key, oss_secret


def get_cluster_info():
    return get_intwdf_cluster_info()


def get_number_of_integration_tests():
    dir_path = os.path.dirname(__file__)
    files = os.listdir(dir_path)
    return len(list(filter(lambda x: x.startswith('test'), files)))


TENANT_ID = os.getenv('TEST_TENANT_ID')
RESOURCE_GROUP_ID = f'aicli{get_random_string()}'
BASE_URL, AUTH_URL, CLIENT_ID, CLIENT_SECRET, PROVISIONING_BASE_URL = get_cluster_info()
OSS_BUCKET, OSS_ENDPOINT, OSS_REGION, OSS_KEY, OSS_SECRET = get_s3_bucket_info()


def get_token():
    return Authenticator(auth_url=AUTH_URL, client_id=CLIENT_ID, client_secret=CLIENT_SECRET).get_token()


def provision_resource_group():
    headers = {'Authorization': get_token()}
    res = requests.post(url=f'{PROVISIONING_BASE_URL}/resourceGroups', json={"resourceGroupId": RESOURCE_GROUP_ID},
                        headers=headers)
    if res.status_code // 100 != 2:
        raise Exception(f"Failed to create resource group {RESOURCE_GROUP_ID}: {res.status_code}, {res.text}")

    sleep(5)
    for i in range(10):
        res = requests.get(url=f'{PROVISIONING_BASE_URL}/resourceGroups/{RESOURCE_GROUP_ID}', headers=headers)
        try:
            if res.status_code == 200 and res.json()['status'] == 'PROVISIONED':
                break
        except Exception:
            pass
        sleep(0.5)
    headers['AI-Resource-Group'] = RESOURCE_GROUP_ID
    res = requests.post(url=f'{PROVISIONING_BASE_URL}/objectStoreSecrets',
                        json={"name": "default", "type": 'S3', "bucket": OSS_BUCKET, "endpoint": OSS_ENDPOINT,
                              "pathPrefix": "", "region": OSS_REGION,
                              "data": {"AWS_ACCESS_KEY_ID": OSS_KEY, "AWS_SECRET_ACCESS_KEY": OSS_SECRET}},
                        headers=headers)
    if res.status_code // 100 != 2:
        raise Exception(
            f"Failed to create object store secret for {RESOURCE_GROUP_ID}: {res.status_code}, {res.text}")


def deprovision_resource_group():
    headers = {'Authorization': get_token()}
    res = requests.delete(url=f'{PROVISIONING_BASE_URL}/resourceGroups/{RESOURCE_GROUP_ID}', headers=headers)
    if res.status_code != 202:
        raise Exception(f"Failed to remove resource group {RESOURCE_GROUP_ID}")


# This function will run before all tests in integration_tests module, when run with nosetests
def setUpModule():
    provision_resource_group()


# This function will run after all tests in integration_tests module, when run with nosetests
def tearDownModule():
    deprovision_resource_group()
