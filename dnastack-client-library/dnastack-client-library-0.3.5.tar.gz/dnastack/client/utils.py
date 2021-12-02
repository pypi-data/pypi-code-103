import sys

import click
import requests
from requests.exceptions import SSLError, HTTPError
from search_python_client.search import SearchClient, DrsClient
from typing import Optional
import json
import io
import csv
from .auth_client import login_refresh_token
from time import time
import jwt
from urllib.parse import urlparse, urlunparse
from ..constants import SUPPORTED_SERVICES


def handle_client_results(results, dataconnect_url):
    try:
        yield from results
    except SSLError:
        raise Exception(
            f"There was an error retrieving the SSL certificate from [{dataconnect_url}]"
        )
    except HTTPError as e:
        error_res = requests.get(e.response.url)
        error_json = json.loads(error_res.text)
        if "errors" in error_json:
            error_msg = error_json["errors"][0]["title"]
            raise Exception(error_msg)
        else:
            raise e


def token_expired(token):
    access_token = jwt.decode(
        token["access_token"], options={"verify_signature": False}
    )
    return not int(access_token["exp"]) > time()


def get_audience_for_wallet(publisher_client, wallet_url: str) -> list:
    urls = []
    for service in publisher_client.get_services():
        pass
    return urls


def get_audience_from_url(url):
    parsed_url = urlparse(url)
    if parsed_url.scheme in ("https", "drs"):
        return str(urlunparse(("https", parsed_url.netloc, "", "", "", ""))) + "/"
    else:
        raise Exception(
            f"Cannot get audience from url: {url} (scheme must be either 'https' or 'drs')"
        )


def get_dataconnect_client(dataconnect_url, oauth_token: Optional[dict] = None):
    if oauth_token:
        if token_expired(oauth_token):
            login_refresh_token(oauth_token)
        dataconnect_client = SearchClient(
            dataconnect_url, wallet=oauth_token["access_token"]
        )
    else:
        dataconnect_client = SearchClient(dataconnect_url)

    return dataconnect_client


def get_drs_client(drs_url, oauth_token: Optional[dict] = None):
    if oauth_token:
        if token_expired(oauth_token):
            login_refresh_token(oauth_token)
        drs_client = DrsClient(drs_url, wallet=oauth_token["access_token"])
    else:
        drs_client = DrsClient(drs_url)

    return drs_client


def format_query_result_as_csv(query_results, include_headers=True):
    output = io.StringIO()
    writer = csv.writer(output)

    # if we have at least one result, add the headers
    if len(query_results) > 0 and include_headers:
        writer.writerow(query_results[0].keys())

    for res in query_results:
        data_row = list(map(lambda x: str(x).replace(",", "\,"), res.values()))
        writer.writerow(data_row)

    return output.getvalue()


def get_access_token_for_wes_client(oauth_token, auth_params):
    if not oauth_token:
        return None

    if token_expired(oauth_token) and auth_params:
        login_refresh_token(oauth_token, auth_params)

    return oauth_token["access_token"]
