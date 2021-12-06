import argparse
import os
import uuid
import random
import requests
from random import choice
from string import digits
import subprocess


ACCOUNTS_URL = None
INTERFACE_URL = None
LOCALSTACK_URL = None
DEBUG = os.environ.get("DEBUG")


def debug_print(to_print):
    if DEBUG == '2':
        print(to_print)


def get_data_org(org_shortcode):
    return {
        "data": {
            "attributes": {
                "name": org_shortcode,
                "description": "string",
                "external_company_id": str(uuid.uuid4()),
                "is_visible": "true",
                "domains": [
                    {"domain_name": f"{org_shortcode}.com"}
                ],
                "short_code": org_shortcode
            }
        }
    }


def get_data_sub_org(org_shortcode, org_id):
    return {
        "data": {
            "attributes": {
                "name": f"{org_shortcode}_sub",
                "description": "string",
                "organisation_id": org_id,
            }
        }
    }


def get_data_aws_accounts(aws_account_id, org_id):
    return {
        "data": {
            "attributes": {
                "vendor_aws_account_id": aws_account_id,
                "vendor_aws_account_name": aws_account_id,
                "aws_region": "eu-west-1",
                "aws_role_arn": "arn:aws:iam::000000000001:user/root",
                "organisation_id": org_id
            }
        }
    }


def get_data_aws_account_role(account_id):
    return {
        "owner_type": "aws-accounts",
        "owner_id": account_id,
        "role": "aws-account-user"
    }


def get_data_sub_org_role(suborg_id, role):
    return {
        "owner_type": "suborganisations",
        "owner_id": suborg_id,
        "role": role
    }


def get_data_packages(package_name, suborg_id):
    return {
        "data": {
            "attributes": {
                "name": package_name,
                "description": "This is a package created for testing S3Proxy.",
                "keywords": ["testing"],
                "topic": "Automotive",
                "access": "Unrestricted",
                "is_internal_within_organisation": "false",
                "terms_and_conditions": "There are no terms and conditions",
                "publisher": "b30a3e2c-ad7e-11eb-b02d-377b10141544",
                "suborganisation_id": suborg_id
            }
        }
    }


def get_data_datasets(sql_enabled, dataset_shortcode, PACKAGE_ID, load_type, AWS_ACCOUNT_ID, bucket, prefix):
    return {
        "data": {
            "attributes": {
                "sql_enabled": sql_enabled,
                "earliest_date_field": "2020",
                "data_preview_type": "NONE",
                "publishing_frequency": "Hourly",
                "naming_convention": "test",
                "documentation": "test",
                "description": "test",
                "content_type": "Structured",
                "data_format": "PARQUET",
                "short_code": dataset_shortcode,
                "package_id": PACKAGE_ID,
                "load_type": load_type,
                "details_visible_to_lite_users": "false",
                "has_datafile_monitoring": "false",
                "taxonomy": ["Forecasting"],
                "location": {
                    "s3": {
                        "type": "S3",
                        "owner": {"aws_account_id": AWS_ACCOUNT_ID},
                        "bucket": bucket,
                        "prefix": prefix
                    }
                },
                "keywords": ["test"],
                "name": dataset_shortcode
            }
        }
    }


def uuid_mod_string():
    s = str(uuid.uuid4())
    s = s.replace("-","")
    num_upper = random.randint(0, 10)
    for i in range(num_upper):
        idx = random.randint(0, 31)
        if not isinstance(s[idx], int):
            s = s[:idx] + s[idx].upper() + s[idx:]
    return s


def get_random_digits():
    return ''.join(choice(digits) for i in range(5))


def check_response_code(fn):
    def wrapper(*args, **kwargs):
        output = fn(*args, **kwargs)
        if output.status_code != 200 and output.status_code != 201:
            raise Exception(f"[CATALOGUE SETUP] [{fn.__name__}] Failure, non 200 response code: {output.json()}, Args: {args}, Kwargs: {kwargs}")
        return output
    return wrapper


@check_response_code
def make_catalogue_get(url, endpoint, headers, data=None):
    output = requests.get(f"http://{url}/{endpoint}", headers=headers, data=data)  # TODO
    debug_print(f"{output}")
    return output


@check_response_code
def make_catalogue_post(url, endpoint, headers, data=None):
    output = requests.post(f"http://{url}/{endpoint}", headers=headers, json=data)
    debug_print(f"{output}")
    return output


def get_random_for_empty(
        jwt_token, org_shortcode, package_name, dataset_shortcode, load_type,
        bucket, prefix, local_data, sql_enabled
):
    jwt_token = jwt_token
    if jwt_token == '':
        raise Exception("[CATALOGUE SETUP] Please pass a test JWT")
    load_type = 'Incremental Load' if load_type is None else 'Full Load'
    org_shortcode = uuid_mod_string() if org_shortcode is None else org_shortcode
    package_name = uuid_mod_string() if package_name is None else package_name
    dataset_shortcode = uuid_mod_string() if dataset_shortcode is None else dataset_shortcode
    bucket = uuid_mod_string().lower() if bucket is None else bucket
    prefix = uuid_mod_string() if prefix is None else prefix
    sql_enabled = 'false' if sql_enabled is None else sql_enabled
    local_data = 'tools/tests/data/integration_dataset/' if local_data is None else local_data
    return package_name, dataset_shortcode, org_shortcode, load_type, bucket, prefix, local_data, sql_enabled


def setup_named_new_dataset_in_named_new_package_in_named_new_org(args=None):
    jwt_token = args.jwt_token
    if jwt_token == '':
        raise Exception("[CATALOGUE SETUP] Please pass a test JWT")
    load_type = 'Incremental Load' if args.load_type is None else 'Full Load'
    org_shortcode = uuid_mod_string() if args.org_shortcode is None else args.org_shortcode
    package_name =uuid_mod_string() if args.package_name is None else args.package_name
    dataset_shortcode = uuid_mod_string() if args.dataset_shortcode is None else args.dataset_shortcode
    bucket = uuid_mod_string().lower() if args.bucket is None else args.bucket
    prefix = uuid_mod_string() if args.prefix is None else args.prefix
    sql_enabled = 'false' if args.sql_enabled is None else args.sql_enabled
    local_data = 'tools/tests/data/integration_dataset/' if args.local_data is None else args.local_data

    setup_new_dataset_in_new_package_in_new_org(jwt_token, load_type, org_shortcode, package_name, dataset_shortcode, bucket, prefix, sql_enabled, local_data)

    # print(org_shortcode, ORG_ID, SUBORG_ID,
    #       package_name, PACKAGE_ID,
    #       dataset_shortcode, dataset_id,
    #       bucket, prefix, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)


def setup_new_dataset(
    jwt_token, bucket, prefix, local_data, sql_enabled, dataset_shortcode, PACKAGE_ID, load_type, AWS_ACCOUNT_ID
):
    global ACCOUNTS_URL
    global INTERFACE_URL
    global LOCALSTACK_URL

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {jwt_token}"
    }

    # upload data to localstack ----------------------------------------------------------------------------
    def call_subprocess(cmd):
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        out, err = proc.communicate()
        if len(err) > 1:
            raise Exception(f"[CATALOGUE SETUP] Failed for AWS command: {cmd}, ERR: {err}")
        debug_print(f"AWS CMD: {cmd}, OUT: {out}, ERR: {err}")

    aws_command_1 = f"aws s3api create-bucket --bucket \"preview-bucket\" --endpoint-url=\"http://{LOCALSTACK_URL}\" --region \"us-east-1\""
    aws_command_2 = f"aws s3api create-bucket --bucket \"{bucket}\" --endpoint-url=\"http://{LOCALSTACK_URL}\" --region \"us-east-1\""
    aws_command_3 = f"aws s3 cp --recursive --endpoint-url=\"http://{LOCALSTACK_URL}\" {local_data} \"s3://{bucket}/{prefix}/\" --region \"us-east-1\""
    cmds = [aws_command_1, aws_command_2, aws_command_3]
    for cmd in cmds:
        call_subprocess(cmd)

    # get datasets ----------------------------------------------------------------------------
    debug_print(f"[CATALOGUE SETUP] [setup_new_dataset_in_new_package_in_new_org] get datasets...")
    datasets_data = get_data_datasets(sql_enabled, dataset_shortcode, PACKAGE_ID, load_type, AWS_ACCOUNT_ID, bucket, prefix)
    outp = make_catalogue_post(INTERFACE_URL, "__api_v2/datasets/", headers, datasets_data)
    datasets = outp.json()
    print(datasets)
    dataset_id = datasets['data']['id']
    return dataset_id


def setup_new_package(jwt_token, package_name, SUBORG_ID):
    global ACCOUNTS_URL
    global INTERFACE_URL
    global LOCALSTACK_URL
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {jwt_token}"
    }
    # get packages ----------------------------------------------------------------------------
    debug_print(f"[CATALOGUE SETUP] [setup_new_dataset_in_new_package_in_new_org] get packages...")
    package_data = get_data_packages(package_name, SUBORG_ID)
    packages = make_catalogue_post(INTERFACE_URL, "__api_v2/packages/", headers, package_data)
    PACKAGE_ID = packages.json()['data']['id']
    return PACKAGE_ID


def setup_new_dataset_in_new_package(
    INTERFACE=None, LOCALSTACK=None, jwt_token=None, SUBORG_ID=None, ORG_ID=None, AWS_ACCOUNT_ID=None,
    package_name=None, dataset_shortcode=None, load_type=None, bucket=None, prefix=None,
    local_data=None, sql_enabled=None, org_shortcode=None
):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {jwt_token}"
    }

    try:
        global ACCOUNTS_URL
        global INTERFACE_URL
        global LOCALSTACK_URL
        INTERFACE_URL = INTERFACE
        ACCOUNTS_URL = INTERFACE_URL
        LOCALSTACK_URL = LOCALSTACK

        if AWS_ACCOUNT_ID is None:
            _, AWS_ACCOUNT_ID, _ = setup_aws_account_for_user(ORG_ID, headers)

        package_name, dataset_shortcode, org_shortcode, load_type, bucket, prefix, local_data, sql_enabled = get_random_for_empty(
            jwt_token, org_shortcode, package_name, dataset_shortcode, load_type,
            bucket, prefix, local_data, sql_enabled
        )
        PACKAGE_ID = setup_new_package(jwt_token, package_name, SUBORG_ID)
        dataset_id = setup_new_dataset(jwt_token, bucket, prefix, local_data, sql_enabled, dataset_shortcode, PACKAGE_ID, load_type, AWS_ACCOUNT_ID)
        return PACKAGE_ID, dataset_id

    except Exception as e:
        print(f"[CATALOGUE SETUP] Setup has failed: {e}")


def setup_new_dataset_in_new_package_in_new_org(
    jwt_token, load_type, org_shortcode, package_name, dataset_shortcode, bucket, prefix, sql_enabled, local_data
):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {jwt_token}"
    }
    try:
        debug_print(f"[CATALOGUE SETUP] [setup_new_dataset_in_new_package_in_new_org] setup_org...")
        ORG_ID, SUBORG_ID = setup_org(org_shortcode, headers)

        debug_print(f"[CATALOGUE SETUP] [setup_new_dataset_in_new_package_in_new_org] setup_user_package_creation...")
        (NEW_GROUP_ID, SUBORG_ID, USER_ID, AWS_ACCOUNT_ID, ACCOUNT_ID,
         ADDITIONAL_ORGS_NEW, ADDITIONAL_ORGS_CURRENT) = setup_user_package_creation(ORG_ID, SUBORG_ID, headers)
        _ = setup_new_dataset_in_new_package(jwt_token, ORG_ID, SUBORG_ID, AWS_ACCOUNT_ID, package_name,org_shortcode, dataset_shortcode, load_type, bucket, prefix, local_data, sql_enabled)

    except Exception as e:
        print(f"[CATALOGUE SETUP] Setup has failed: {e}")


def setup_org(org_shortcode, headers):
    debug_print(f"[CATALOGUE SETUP] [setup_org] organisations")
    org_data = get_data_org(org_shortcode)
    outp = make_catalogue_post(ACCOUNTS_URL, "__api_v2/organisations", headers, org_data)
    json_output = outp.json()
    debug_print(json_output)
    org_id = json_output["data"]["id"]
    debug_print(f"ORG_ID: {org_id}")

    debug_print(f"[CATALOGUE SETUP] [setup_org] suborganisations")
    suborg_data = get_data_sub_org(org_shortcode, org_id)
    outp = make_catalogue_post(ACCOUNTS_URL, "__api_v2/suborganisations", headers, suborg_data)
    json_output = outp.json()
    debug_print(json_output)
    suborg_id = json_output["data"]["id"]
    debug_print(f"SUB_ORG_ID: {suborg_id}")
    return org_id, suborg_id


def setup_aws_account_for_user(ORG_ID, headers):

    # register aws account for users ----------------------------------------------------------------------------
    debug_print(f"[CATALOGUE SETUP] [setup_aws_account_for_user] register aws account for users")
    AWS_ACCOUNT_ID = get_random_digits()
    aws_accounts_data = get_data_aws_accounts(AWS_ACCOUNT_ID, ORG_ID)
    outp = make_catalogue_post(INTERFACE_URL, "__api_v2/aws_accounts", headers, aws_accounts_data)
    json_output = outp.json()
    debug_print(json_output)
    ACCOUNT_ID = json_output['data']['id']

    # TODO Disable after Catalogue DL-7224
    # get our user group --------------------------------------------------------------------------------------------
    debug_print(f"[CATALOGUE SETUP] [setup_aws_account_for_user] get our user group")
    outp = make_catalogue_get(ACCOUNTS_URL, "__api_v2/user_groups/", headers)  # NOTE: this is a GET
    json_output = outp.json()
    debug_print(json_output)
    group_id = json_output['data'][0]['id']
    NEW_GROUP_ID = group_id

    # add the aws_account to our user's group -----------------------------------------------------------------------
    debug_print(f"[CATALOGUE SETUP] [setup_aws_account_for_user] add the aws_account to our user's group")
    role_data = get_data_aws_account_role(ACCOUNT_ID)
    outp = make_catalogue_post(ACCOUNTS_URL, f"__api_v2/user_groups/{NEW_GROUP_ID}/roles", headers, role_data)
    json_output = outp.json()
    debug_print(json_output)

    return NEW_GROUP_ID, AWS_ACCOUNT_ID, ACCOUNT_ID


def setup_user_package_creation(org_id, SUBORG_ID, headers):

    debug_print(f"[CATALOGUE SETUP] [setup_user_package_creation] [setup_aws_account_for_user]")
    NEW_GROUP_ID, AWS_ACCOUNT_ID, ACCOUNT_ID = setup_aws_account_for_user(org_id, headers)

    # set permissions on suborg for our user now we have the group id -----------------------------------------------
    debug_print(f"[CATALOGUE SETUP] [setup_user_package_creation] set permissions on suborg for our user now we have the group id")
    role = 'data-steward'
    role_data = get_data_sub_org_role(SUBORG_ID, role)
    outp = make_catalogue_post(ACCOUNTS_URL, f"__api_v2/user_groups/{NEW_GROUP_ID}/roles", headers, role_data)
    json_output = outp.json()
    debug_print(json_output)

    # set permissions on suborganisations with role technical-support for our user ----------------------------------
    debug_print(f"[CATALOGUE SETUP] [setup_user_package_creation] set permissions on suborganisations with role technical-support for our user")
    role = 'technical-support'
    role_data = get_data_sub_org_role(SUBORG_ID, role)
    outp = make_catalogue_post(ACCOUNTS_URL, f"__api_v2/user_groups/{NEW_GROUP_ID}/roles", headers, role_data)
    json_output = outp.json()
    debug_print(json_output)

    # set permissions on suborganisations with role access-manager for our user ------------------------------------
    debug_print(f"[CATALOGUE SETUP] [setup_user_package_creation] set permissions on suborganisations with role access-manager for our user")
    role = 'access-manager'
    role_data = get_data_sub_org_role(SUBORG_ID, role)
    outp = make_catalogue_post(ACCOUNTS_URL, f"__api_v2/user_groups/{NEW_GROUP_ID}/roles", headers, role_data)
    json_output = outp.json()
    debug_print(json_output)

    # set permissions on suborganisations with role package-creator for our user ----------------------------------
    debug_print(f"[CATALOGUE SETUP] [setup_user_package_creation] set permissions on suborganisations with role package-creator for our user")
    role = 'package-creator'
    role_data = get_data_sub_org_role(SUBORG_ID, role)
    outp = make_catalogue_post(ACCOUNTS_URL, f"__api_v2/user_groups/{NEW_GROUP_ID}/roles", headers, role_data)
    json_output = outp.json()
    debug_print(json_output)

    # TODO label in bash to uncomment code for ADDITIONAL_ORGS_NEW, ADDITIONAL_ORGS_CURRENT
    USER_ID=None
    ADDITIONAL_ORGS_NEW=None
    ADDITIONAL_ORGS_CURRENT=None

    return NEW_GROUP_ID, SUBORG_ID, USER_ID, AWS_ACCOUNT_ID, ACCOUNT_ID, ADDITIONAL_ORGS_NEW, ADDITIONAL_ORGS_CURRENT


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--accounts", "-a", type=str, required=True)
    parser.add_argument("--interface", "-i", type=str, required=True)

    parser.add_argument("--localstack", "-l", type=str, required=True)

    parser.add_argument("--jwt_token", "-j", type=str, required=False)
    parser.add_argument("--load_type", "-t", type=str, required=False)
    parser.add_argument("--org_shortcode", "-o", type=str, required=False)
    parser.add_argument("--package_name", "-p", type=str, required=False)
    parser.add_argument("--dataset_shortcode", "-s", type=str, required=False)
    parser.add_argument("--bucket", "-b", type=str, required=False)
    parser.add_argument("--prefix", "-x", type=str, required=False)
    parser.add_argument("--sql_enabled", "-e", type=str, required=False)
    parser.add_argument("--local_data", "-d", type=str, required=False)
    parser.add_argument("--mode", "-m", type=str, required=True)

    args = parser.parse_args()
    ACCOUNTS_URL = args.interface #args.accounts
    LOCALSTACK_URL = args.localstack
    INTERFACE_URL = args.interface  # to be args.accounts
    ACCOUNTS = INTERFACE_URL
    INTERFACE = INTERFACE_URL
    LOCALSTACK = LOCALSTACK_URL

    DEBUG = os.environ.get("DEBUG", "2")
    if not ACCOUNTS_URL or not INTERFACE_URL or not LOCALSTACK_URL:
        raise Exception(f"Environment variables are not set: "
                        f"ACCOUNTS_URL:{ACCOUNTS_URL}"
                        f"INTERFACE_URL:{INTERFACE_URL}"
                        f"LOCALSTACK_URL:{LOCALSTACK_URL}"
                        )
    # setup_named_new_dataset_in_named_new_package_in_named_new_org(args)
    pass