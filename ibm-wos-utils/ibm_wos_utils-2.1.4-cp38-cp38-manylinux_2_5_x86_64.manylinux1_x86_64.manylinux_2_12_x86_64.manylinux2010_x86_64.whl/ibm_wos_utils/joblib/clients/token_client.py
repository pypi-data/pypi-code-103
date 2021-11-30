# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-J33
# Copyright IBM Corp. 2020
# The source code for this program is not published or other-wise divested of its trade
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

from ibm_wos_utils.joblib.utils.rest_util import RestUtil

class TokenClient():

    @classmethod
    def get_iam_token(cls, server_url, username, password):
        url = "{}/v1/preauth/validateAuth".format(server_url)
        response = RestUtil.request().get(url=url, headers={
            "username": username,
            "password": password
        })

        return response.json().get("accessToken")

    @classmethod
    def get_iam_token_with_apikey(cls, server_url, username, apikey):
        url = "{}/v1/preauth/validateAuth".format(server_url)
        response = RestUtil.request().get(url=url, headers={
            "username": username,
            "apikey": apikey
        }, verify=False)

        return response.json().get("accessToken")