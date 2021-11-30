from typing import Any, Dict, List, Optional, Union
from pathlib import Path
import json
import os
import requests
from dotenv import load_dotenv
from requests.models import Response


def strtobool(val):
    """Convert a string representation of truth to true (1) or false (0).

    True values are 'y', 'yes', 't', 'true', 'on', and '1'; false values
    are 'n', 'no', 'f', 'false', 'off', and '0'.  Raises ValueError if
    'val' is anything else.
    credits: https://github.com/nautobot
    """
    val = val.lower()
    if val in ("y", "yes", "t", "true", "on", "1"):
        return 1
    elif val in ("n", "no", "f", "false", "off", "0"):
        return 0
    else:
        raise ValueError("invalid truth value %r" % (val,))


def is_truthy(arg) -> bool:
    """Convert "truthy" strings into Booleans.

    Examples:
        >>> is_truthy('yes')
        True
    Args:
        arg (str): Truthy string (True values are y, yes, t, true, on and 1; false values are n, no,
        f, false, off and 0. Raises ValueError if val is anything else.
    credits: https://github.com/nautobot
    """
    if isinstance(arg, bool):
        return arg
    return bool(strtobool(arg))


class SecretServer:

    # see .env.example
    SECRET_SERVER_SITE: str
    SECRET_SERVER_AUTH_API: str
    SECRET_SERVER_USERNAME: str
    SECRET_SERVER_PASSWORD: str
    SECRET_SERVER_SSL_VERIFY: Union[bool, str]
    SECRET_SERVER_API: str
    SECRET_SERVER_DEFAULT_SLUGS: List[str] = ["id", "url", "username", "password"]
    SECRET_SERVER_IS_DUMMY: bool
    SECRET_SERVER_TEST_DUMMY_RESULT: Dict[Any, Any]

    def __init__(self) -> None:
        load_dotenv(".env")

        self.SECRET_SERVER_SITE = os.getenv("SECRET_SERVER_SITE", "https://pw.example.local/SecretServer")
        self.SECRET_SERVER_AUTH_API = os.getenv("SECRET_SERVER_AUTH_API", "/oauth2/token")
        self.SECRET_SERVER_USERNAME = os.getenv("SECRET_SERVER_USERNAME", "thycotic_api_username")
        self.SECRET_SERVER_PASSWORD = os.getenv("SECRET_SERVER_PASSWORD", "my-secret-password")

        # SECRET_SERVER_SSL_VERIFY
        # values:
        #   - True: certificate will be verified (Default)
        #   - False: certificate will be ignored
        #   - Path: path to trusted certificat bundle e.g. "/etc/ssl/certs/ca-bundle.crt"
        ssl_verify = os.getenv("SECRET_SERVER_SSL_VERIFY", "True")

        if Path(ssl_verify).exists():
            self.SECRET_SERVER_SSL_VERIFY = ssl_verify
        else:
            self.SECRET_SERVER_SSL_VERIFY = is_truthy(ssl_verify)

        slugliststr = os.getenv("SECRET_SERVER_DEFAULT_SLUGS", "")
        if len(self.SECRET_SERVER_DEFAULT_SLUGS) > 0:
            try:
                self.SECRET_SERVER_DEFAULT_SLUGS = json.loads(slugliststr)
            except:
                pass

        self.SECRET_SERVER_API = self.SECRET_SERVER_SITE + "/api/v1"
        self.SECRET_SERVER_IS_DUMMY = is_truthy(os.getenv("SECRET_SERVER_IS_DUMMY", "False"))
        try:
            dummyres = json.loads(str(os.getenv("SECRET_SERVER_TEST_DUMMY_RESULT")))
        except:
            dummyres = None
        if not dummyres or ("username" not in dummyres) or ("password" not in dummyres) or ("url" not in dummyres):
            dummyres = {
                "username": "testuser",
                "password": "testpassword",
                "url": "https://localhost/SecretServer",
            }
        self.SECRET_SERVER_TEST_DUMMY_RESULT = dummyres
        self._isconnected = False
        self.token = None

    def getAuthToken(self):
        """Get token with given credentials"""
        if self.SECRET_SERVER_IS_DUMMY:
            return "DUMMY_TOKEN"
        creds = {}
        creds["username"] = self.SECRET_SERVER_USERNAME
        creds["password"] = self.SECRET_SERVER_PASSWORD
        creds["grant_type"] = "password"

        uri = self.SECRET_SERVER_SITE + self.SECRET_SERVER_AUTH_API
        headers = {
            "Accept": "application/json",
            "content-type": "application/x-www-form-urlencoded",
        }
        resp = requests.post(
            uri,
            data=creds,
            headers=headers,
            verify=self.SECRET_SERVER_SSL_VERIFY,
        )

        if resp.status_code not in (200, 304):
            raise Exception(
                "Problems getting a token from Secret Server for %s. %s %s"
                % (self.SECRET_SERVER_USERNAME, resp.status_code, resp)
            )
        self.token = resp.json()["access_token"]
        self._isconnected = True
        return self.token

    def getSecret(self, secretId: str):
        """Retrieve the infomation about the secret having id==secretid
        Args:
            secretId (str): Entry ID to retrieve fron server

        Raises:
            Exception: REST Api Call failed

        Returns:
            [Response.json()]: Answer from server
        """
        if self.SECRET_SERVER_IS_DUMMY:
            return {
                    "id": secretId,
                    "name": "DUMMY Secret",
                    "items": [
                        {
                            "itemId": 18582,
                            "itemValue": "https://example.com/net-automation/inventory.git",
                            "slug": "url",
                        },
                        {
                            "itemId": 18583,
                            "itemValue": self.SECRET_SERVER_TEST_DUMMY_RESULT["username"],
                            "slug": "username",
                        },
                        {
                            "itemId": 18584,
                            "itemValue": self.SECRET_SERVER_TEST_DUMMY_RESULT["password"],
                            "slug": "password",
                        },
                    ],
                }
        if not self._isconnected:
            self.getAuthToken()

        headers = {
            "Authorization": f"Bearer {self.token}",
            "content-type": "application/json",
        }
        srv_response = requests.get(
            self.SECRET_SERVER_API + f"/secrets/{secretId}",
            headers=headers,
            verify=self.SECRET_SERVER_SSL_VERIFY,
        )

        if srv_response.status_code not in (200, 304):
            self._isconnected = False
            raise Exception(f"Error retrieving Secret. {srv_response.status_code} {srv_response}")
        self._response = srv_response.json()
        return self._response

    def getFieldItemWithSlug(self, response, slugs: Optional[List[str]] = None) -> Dict[str, Any]:
        """Return the field values from the fields selected in list[slugs]

        Args:
            response (Response.json()): response from secretserver
            slugs ([str], optional): Slugs to extract. When None, the default is used. Defaults to None.

        Returns:
            [dict]: Fieldname and Value
        """
        result = {}

        if slugs is None:
            slugs = self.SECRET_SERVER_DEFAULT_SLUGS
        elif isinstance(slugs, str):
            slugs = json.loads(slugs)
        if "id" in slugs:  # type: ignore
            result = {"id": response["id"]}
        if "name" in slugs:  # type: ignore
            result.update({"name": response.name})
        for field in response["items"]:
            if field["slug"] in slugs:
                result.update({field["slug"]: field["itemValue"]})
        return result

    def searchSecretResponse(self, text, slugs: Optional[List[str]] = None):
        """Search the secret name and return

        Args:
            text ([type]): [description]
            slugs ([type], optional): [description]. Defaults to None.

        Raises:
            Exception: Error retrieving Secret.

        Returns:
            [dict]: Extracted Secret field-names and values
        """
        if not slugs:
            slugs = self.SECRET_SERVER_DEFAULT_SLUGS
        if isinstance(slugs, str):
            slugs = json.loads(slugs)
        if not self._isconnected:
            self.getAuthToken()

        headers = {
            "Authorization": f"Bearer {self.token}",
            "content-type": "application/json",
            "filter.searchField": text,
        }
        if self.SECRET_SERVER_IS_DUMMY:
            with Path(__file__).parent.joinpath("tests","data","get_secret_response.json").open("r") as stream:
                srv_response_json = json.load(stream)
        else:
            srv_response = requests.get(
                self.SECRET_SERVER_API + "/secrets/",
                headers=headers,
                verify=self.SECRET_SERVER_SSL_VERIFY,
            )
            if srv_response.status_code not in (200, 304):
                self._isconnected = False
                raise Exception(f"Error retrieving Secret. {srv_response.status_code} {srv_response}")
            srv_response_json = srv_response.json()

        found = list(filter(lambda x: text in x["name"], srv_response_json["records"]))
        if found:
            secret_id = str(found[0]["id"])
            return self.getSecret(secret_id)
        return srv_response_json()

    def searchSecret(self, name_or_id, slugs: Optional[List[str]] = None):
        """Search a secret by name or id

        Args:
            name_or_id (str): Secret Name or ID to search fo

        Returns:
            dict: Field names and values
        """
        try:
            secid = int(name_or_id)
            resp = self.getSecret(str(secid))
        except ValueError:
            resp = self.searchSecretResponse(name_or_id)
        return self.getFieldItemWithSlug(resp, slugs=slugs)
