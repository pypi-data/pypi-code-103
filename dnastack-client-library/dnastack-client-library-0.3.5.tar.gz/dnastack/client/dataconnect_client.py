from os import write
import sys
from dnastack.constants import *
from datetime import datetime
from requests.exceptions import SSLError
import click
import json
from requests import HTTPError
from dnastack.client.utils import handle_client_results, get_dataconnect_client
from typing import Optional
from .utils import format_query_result_as_csv


def query(
    dataconnect_url,
    q,
    download=False,
    format="json",
    raw=False,
    oauth_token: Optional[dict] = None,
):
    dataconnect_client = get_dataconnect_client(dataconnect_url, oauth_token)

    results = dataconnect_client.search_table(q)

    if format == "csv":
        output = format_query_result_as_csv(
            list(handle_client_results(results, dataconnect_url)), not raw
        )
    else:
        output = json.dumps(
            list(handle_client_results(results, dataconnect_url)), indent=4
        )

    if download:
        # TODO: be able to specify output file
        download_file = f"{downloads_directory}/query{datetime.now().strftime('%Y-%m-%d-%H:%M:%S')}{'.csv' if format == 'csv' else '.json'}"
        with open(download_file, "w") as fs:
            fs.write(output)
    else:
        return output


def list_tables(dataconnect_url, oauth_token: Optional[dict] = None):
    dataconnect_client = get_dataconnect_client(dataconnect_url, oauth_token)

    tables_iterator = dataconnect_client.get_table_list()

    return json.dumps(
        list(handle_client_results(tables_iterator, dataconnect_url)), indent=4
    )


def get_table(dataconnect_url, table_name, oauth_token: Optional[dict] = None):
    dataconnect_client = get_dataconnect_client(dataconnect_url, oauth_token)

    table_info = dataconnect_client.get_table_info(table_name)

    # formatting response to remove unnecessary fields
    results = table_info.to_dict()
    results["name"] = table_info["name"]["$id"]
    results["description"] = table_info["description"]["$id"]

    return json.dumps(results, indent=4)
