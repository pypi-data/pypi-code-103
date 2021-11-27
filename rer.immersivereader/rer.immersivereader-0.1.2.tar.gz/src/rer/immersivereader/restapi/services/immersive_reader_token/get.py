# -*- coding: utf-8 -*-
from plone.restapi.services import Service
from zExceptions import BadRequest

import os
import requests


class TokenGet(Service):
    def reply(self):
        credentials = self.get_credentials()

        headers = {"content-type": "application/x-www-form-urlencoded"}
        data = {
            "client_id": credentials["client_id"],
            "client_secret": credentials["client_secret"],
            "resource": "https://cognitiveservices.azure.com/",
            "grant_type": "client_credentials",
        }

        url = "https://login.windows.net/{tenant_id}/oauth2/token".format(
            tenant_id=credentials["tenant_id"]
        )

        resp = requests.post(url, data=data, headers=headers)

        if resp.status_code != 200:
            resp.raise_for_status()

        data = resp.json()

        token = data.get("access_token", "")
        if not token:
            self.request.response.setStatus(500)
            return dict(
                error=dict(
                    type="InternalServerError",
                    message="Unable to get token from microsoft.",
                )
            )

        return {"token": token, "subdomain": credentials["subdomain"]}

    def get_credentials(self):
        client_id = os.environ.get("IMR_CLIEND_ID")
        client_secret = os.environ.get("IMR_CLIEND_SECRET")
        tenant_id = os.environ.get("IMR_TENANT_ID")
        subdomain = os.environ.get("IMR_SUBDOMAIN")

        if not client_id:
            raise BadRequest(
                "Missing value for 'IMR_CLIEND_ID' in environment variables. Unable to get Token."
            )
        if not client_secret:
            raise BadRequest(
                "Missing value for 'IMR_CLIEND_SECRET' in environment variables. Unable to get Token."
            )
        if not tenant_id:
            raise BadRequest(
                "Missing value for 'IMR_TENANT_ID' in environment variables. Unable to get Token."
            )
        if not subdomain:
            raise BadRequest(
                "Missing value for 'IMR_SUBDOMAIN' in environment variables. Unable to get Token."
            )

        return {
            "client_id": client_id,
            "client_secret": client_secret,
            "tenant_id": tenant_id,
            "subdomain": subdomain,
        }
