# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-H76
# Copyright IBM Corp. 2020, 2021
# The source code for this program is not published or other-wise divested of its trade
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

from http import HTTPStatus
from ibm_wos_utils.joblib.exceptions.client_errors import *
from ibm_wos_utils.joblib.utils.rest_util import RestUtil


class TokenClient():

    @classmethod
    def get_iam_token(cls, server_url, username, password):
        url = "{}/v1/preauth/validateAuth".format(server_url)
        response = RestUtil.request().get(url=url, headers={
            "username": username,
            "password": password
        })
        if not response.ok:
            if response.status_code == HTTPStatus.UNAUTHORIZED.value:
                raise AuthenticationError(
                    "The credentials provided to generate access token are invalid.")
            raise DependentServiceError(
                "An error occurred while generating access token.", response)
        return response.json().get("accessToken")

    @classmethod
    def get_iam_token_with_apikey(cls, server_url, username, apikey):
        url = "{}/v1/preauth/validateAuth".format(server_url)
        response = RestUtil.request().get(url=url, headers={
            "username": username,
            "apikey": apikey
        }, verify=False)
        if not response.ok:
            if response.status_code == HTTPStatus.UNAUTHORIZED.value:
                raise AuthenticationError(
                    "The credentials provided to generate access token are invalid.")
            raise DependentServiceError(
                "An error occurred while generating access token.", response)
        return response.json().get("accessToken")
