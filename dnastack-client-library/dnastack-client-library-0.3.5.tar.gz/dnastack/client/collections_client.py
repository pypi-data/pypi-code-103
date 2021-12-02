import json
import requests as req
from .utils import format_query_result_as_csv


def list_collections(collections_url):
    return req.get(collections_url).json()


def list_tables(collections_url, collection_name):
    collection_tables_url = collections_url + f"{collection_name}/data-connect/tables"
    return req.get(collection_tables_url).json()


def query(collections_url, collection_name, query, format="json"):
    collection_query_url = collections_url + f"{collection_name}/data-connect/search"

    res = req.post(collection_query_url, json={"query": query})

    results = res.json()

    if not res.ok:
        if "errors" in results:
            error_msg = results["errors"][0]["title"]
            raise Exception(error_msg)
        raise Exception(f"Error reaching [{collections_url}]")

    if format == "csv":
        return format_query_result_as_csv(results["data"])
    else:
        # load and redump the json to allow for proper formatting
        return json.dumps(results["data"], indent=4)
