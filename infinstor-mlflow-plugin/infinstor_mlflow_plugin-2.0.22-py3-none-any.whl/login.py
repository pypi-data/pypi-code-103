#!/usr/bin/env python
import sys
import getpass
import json
import builtins
from . import servicedefs ,set_builtins_with_serverside_config   # do not remove 'servicedefs', although it is unreferenced; needed to setup some 'builtins' attributes
from infinstor_mlflow_plugin.tokenfile import write_token_file, get_token
from requests.exceptions import HTTPError
import requests
from os.path import expanduser
from os.path import sep as separator
import time
import configparser
from urllib.parse import unquote, urlparse
import os
import traceback
import logging

from . import get_log_level_from_config_json
logger = logging.getLogger(__name__)
loglevel_int:int = get_log_level_from_config_json(__name__)
if loglevel_int:
    logger.setLevel(loglevel_int)

def print_version(token):
    headers = { 'Authorization': token }
    url = 'https://' + builtins.mlflowserver + '/api/2.0/mlflow/infinstor/get_version'
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
    except HTTPError as http_err:
        print(f'HTTP error occurred while getting version: {http_err}')
        raise
    except Exception as err:
        print(f'Other error occurred while getting version: {err}')
        raise

def get_creds():
    if sys.stdin.isatty():
        username = input("Username: ")
        password = getpass.getpass("Password: ")
    else:
        username = sys.stdin.readline().rstrip()
        password = sys.stdin.readline().rstrip()
    return username, password

def get_customer_info_rest(idToken:str) -> dict:
    """Invokes api.<infinstor.com>/customerinfo API and returns the dict

    Args:
        idToken (str): idToken to use for authentication

    Returns:
        dict: the response from /customerinfo call
        {'awsAccountId': 'xxx', 'enableProjects': 'true', 'InfinSnapBuckets': [], 'InfinStorAccessKeyId': 'xxxx', 'userName': 'xxxxx@infinstor.com', 'serviceVersion': '2.0.18', 'productCode': ['xxxx'], 'iamExternalId': 'xxx', 'customerId': 'xxxxx', 'customerArtifactUri': 'xxxxx', 'customerRoleArn': 'xxxxx', 'mlflowTrackingDdbTableName': 'xxxxxx', 'isSecondaryUser': 'true'}
    """
    payload = ("ProductCode=" + builtins.prodcode)
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Authorization': idToken
        }

    url = 'https://' + builtins.apiserver + '/customerinfo'
    try:
        response = requests.post(url, data=payload, headers=headers)
        response.raise_for_status()
    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
        raise
    except Exception as err:
        print(f'Other error occurred: {err}')
        raise

    # print('customerinfo success')
    logger.debug(f"url={url}; response.content={response.content}")    
    response_json:dict = response.json()
    
    return response_json
    
def login_and_update_token_file(region, username, password) -> dict:
    """ does AuthFlow = "USER_PASSWORD_AUTH".  Note that this method is currently only useful when USER_PASSWORD_AUTH flow is enabled in cognito.  If 'ExternalAuth' is enabled (federated identity, say SAML), then this username, password will not work..
    
    does AuthFlow = "REFRESH_TOKEN_AUTH"
    
    then updates ~/.infinstor/token file

    Args:
        region (str): AWS region where cognito is deployed
        username (str): see above description
        password (str): see above description
    Returns:
        [dict]: returns /customerinfo REST call results
    """
    postdata = dict()
    auth_parameters = dict()
    auth_parameters['USERNAME'] = username
    auth_parameters['PASSWORD'] = password
    postdata['AuthParameters'] = auth_parameters
    postdata['AuthFlow'] = "USER_PASSWORD_AUTH"
    postdata['ClientId'] = builtins.clientid

    payload = json.dumps(postdata)

    url = 'https://cognito-idp.' +region +'.amazonaws.com:443/'
    headers = {
            'Content-Type': 'application/x-amz-json-1.1',
            'X-Amz-Target' : 'AWSCognitoIdentityProviderService.InitiateAuth'
            }

    try:
        response = requests.post(url, data=payload, headers=headers)
        response.raise_for_status()
    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
        raise
    except Exception as err:
        print(f'Other error occurred: {err}')
        raise


    authres = response.json()['AuthenticationResult']
    idToken = authres['IdToken']
    accessToken = authres['AccessToken']
    refresh_token = authres['RefreshToken']

    ##Refresh token once############################
    postdata = dict()
    auth_parameters = dict()
    auth_parameters['REFRESH_TOKEN'] = refresh_token
    postdata['AuthParameters'] = auth_parameters
    postdata['AuthFlow'] = "REFRESH_TOKEN_AUTH"
    postdata['ClientId'] = builtins.clientid

    payload = json.dumps(postdata)

    url = 'https://cognito-idp.' +region +'.amazonaws.com:443/'
    headers = {
            'Content-Type': 'application/x-amz-json-1.1',
            'X-Amz-Target' : 'AWSCognitoIdentityProviderService.InitiateAuth'
            }

    try:
        response = requests.post(url, data=payload, headers=headers)
        response.raise_for_status()
    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
        raise
    except Exception as err:
        print(f'Other error occurred: {err}')
        raise

    authres = response.json()['AuthenticationResult']
    idToken = authres['IdToken']
    accessToken = authres['AccessToken']

    #########

    token_time = int(time.time())
    tokfile = expanduser("~") + separator + '.infinstor' + separator + 'token'
    write_token_file(tokfile, token_time, accessToken, refresh_token, builtins.clientid,\
                builtins.service, idToken)

    response_json:dict = get_customer_info_rest(idToken)
    
    infinStorAccessKeyId = unquote(response_json.get('InfinStorAccessKeyId'))
    infinStorSecretAccessKey = unquote(response_json.get('InfinStorSecretAccessKey'))
    setup_credentials(infinStorAccessKeyId, infinStorSecretAccessKey)

    print('Login to service ' + builtins.service + ' complete')
    print_version(accessToken)
    return response_json

def setup_credentials(infinStorAccessKeyId, infinStorSecretAccessKey):
    home = expanduser("~")
    config = configparser.ConfigParser()
    newconfig = configparser.ConfigParser()
    credsfile = home + separator + ".aws" + separator + "credentials"
    if (os.path.exists(credsfile)):
        credsfile_save = home + separator + ".aws" + separator + "credentials.save"
        try:
            os.remove(credsfile_save)
        except Exception as err:
            print()
        try:
            os.rename(credsfile, credsfile_save)
        except Exception as err:
            print()
        config.read(credsfile_save)
        for section in config.sections():
            if (section != 'infinstor'):
                newconfig[section] = {}
                dct = dict(config[section])
                for key in dct:
                    newconfig[section][key] = dct[key]
    else:
        dotaws = home + "/.aws"
        if (os.path.exists(dotaws) == False):
            os.mkdir(dotaws, 0o755)
            open(credsfile, 'a').close()

    newconfig['infinstor'] = {}
    newconfig['infinstor']['aws_access_key_id'] = infinStorAccessKeyId
    newconfig['infinstor']['aws_secret_access_key'] = infinStorSecretAccessKey

    with open(credsfile, 'w') as configfile:
        newconfig.write(configfile)

# returns dict of service details if successful, None if unsuccessful
def bootstrap_from_mlflow_rest():
    """ use the MLFLOW_TRACKING_URI environment variable to bootstrap: call get_version() REST API and use it to return a dict with the configuration detected like 'clientid', 'appclientid', 'service', 'region' and others..

    Returns:
        [dict]: see description above
    """
    
    ##########
    #  TODO: a copy exists in infinstor-jupyterlab/server-extention/jupyterlab_infinstor/cognito_utils.py and infinstor-jupyterlab/clientlib/__init__.py.  Need to see how to share code between two pypi packages to eliminate this duplication
    #  when refactoring this code, also refactor the copy
    ############
    
    muri = os.getenv('MLFLOW_TRACKING_URI')
    pmuri = urlparse(muri)
    if (pmuri.scheme.lower() != 'infinstor'):
        return None
    cognito_domain = pmuri.hostname[pmuri.hostname.index('.')+1:]
    url = 'https://' + pmuri.hostname + '/api/2.0/mlflow/infinstor/get_version'
    headers = { 'Authorization': 'None' }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        resp = response.json()
        return { 'clientid' : resp['cognitoCliClientId'],
                'appclientid' : resp['cognitoAppClientId'],
                'mlflowserver' : resp['mlflowDnsName'] + '.' + cognito_domain,
                'mlflowuiserver' : resp['mlflowuiDnsName'] + '.' + cognito_domain,
                'mlflowstaticserver' : resp['mlflowstaticDnsName'] + '.' + cognito_domain,
                'apiserver' : resp['apiDnsName'] + '.' + cognito_domain,
                'serviceserver' : resp['serviceDnsName'] + '.' + cognito_domain,
                'service' : cognito_domain,
                'region': resp['region']}
    except HTTPError as http_err:
        print(f"Caught Exception: {http_err}: {traceback.format_exc()}" )
        return None
    except Exception as err:
        print(f"Caught Exception: {err}: {traceback.format_exc()}" )
        return None

def login(srvdct):
    set_builtins_with_serverside_config(srvdct)
    
    try:
        tokfile = expanduser("~") + separator + '.infinstor' + separator + 'token'
        token, service = get_token(srvdct['region'], tokfile, False)
        if (service == builtins.service):
            print('Login to service ' + service + ' completed')
            sys.exit(0)
        else:
            print('service mismatch between MLFLOW_TRACKING_URI and ~/.infinstor/token. Forcing login')
            raise Exception('service mismatch between MLFLOW_TRACKING_URI and ~/.infinstor/token. Forcing login')
    except Exception as err:
        print('caught exception ' + str(err))
        pass

    username, password = get_creds()
    customerinfo:dict = login_and_update_token_file(srvdct['region'], username, password)

    # set enableProjects / isProjectEnabled ; /customer_info REST response has 'enableProjects': 'true'        
    builtins.enableProjects = True if customerinfo.get('enableProjects', False) == 'true' else False
    srvdct['enableProjects'] = builtins.enableProjects
    logger.error(f"enableProjects={builtins.enableProjects}")

if __name__ == "__main__":
    if (login(bootstrap_from_mlflow_rest())):
        exit(0)
    else:
        exit(255)
