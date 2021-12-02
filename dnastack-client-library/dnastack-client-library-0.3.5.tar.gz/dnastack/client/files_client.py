from urllib.parse import urlparse, urlunparse

import click
import urllib3
import threading
import os
from typing import Optional, Union
from dnastack.constants import *
from requests import Response
from requests.exceptions import HTTPError
from dnastack.client.utils import get_drs_client
import gzip
import re
import sys
import io
import pandas as pd

# since our downloads are multi-threaded, we use a lock to avoid race conditions
output_lock = threading.Lock()
exit_code_lock = threading.Lock()


def get_host(url: str) -> str:
    parsed_url = urlparse(url)
    return parsed_url.netloc


def handle_file_response(download_file: str, data: Union[str, bytes]) -> str:
    # decode if fasta
    if re.search(r"\.fa", download_file):
        data = data.decode("utf-8")

    return data


# turn into dataframe for FASTA/FASTQ files, otherwise just return raw data
def file_to_dataframe(download_file: str, data: Union[str, bytes]):
    if re.search(r"\.fa", download_file):
        data = data.split("\n", maxsplit=1)

        meta = data[0]
        sequence = data[1].replace("\n", "")  # remove newlines

        return pd.DataFrame({"meta": [meta], "sequence": [sequence]})

    return data


def is_drs_url(url: str) -> bool:
    parsed_url = urlparse(url)
    return parsed_url.scheme == "drs"


def get_object_info_url_from_drs(url: str) -> tuple:
    if not is_drs_url(url):
        raise Exception(f"[{url}] is not a DRS url")
    parsed_url = urlparse(url)
    object_url = str(
        urlunparse(("https", parsed_url.netloc, "/ga4gh/drs/v1/", "", "", ""))
    )
    return object_url, parsed_url.netloc


def get_object_id_from_drs(url: str) -> str:
    object_id = re.search(r"(?<=/)(\w{8}-\w{4}-\w{4}-\w{4}-\w{12})", url)
    if object_id:
        return object_id.group(0)
    else:
        raise Exception(f"Could not get drs object id from url [{url}]")


def get_filename_from_url(url: str) -> str:
    parsed_url = urlparse(url)
    return parsed_url.path.split("/")[-1]


def exit_download(url: str, code: int, message: str = "", exit_codes: dict = None):
    if exit_codes is not None:
        exit_code_lock.acquire()
        exit_codes[url] = (code, message)
        exit_code_lock.release()


def download_file(
    url: str,
    output_dir: str,
    oauth_token: Optional[dict] = None,
    quiet: bool = False,
    out: Optional[list] = None,
    exit_codes: Optional[dict] = None,
):

    http = urllib3.PoolManager()
    chunk_size = 1024
    download_url = None

    if is_drs_url(url):
        # parse the drs url to the resource url
        try:
            drs_server, drs_host = get_object_info_url_from_drs(url)
            drs_client = get_drs_client(drs_server)
            object_id = get_object_id_from_drs(url)
            object_info = drs_client.get_object_info(object_id)
        except HTTPError as e:
            if e.response.status_code == 404:
                error_msg = f"DRS object at url [{url}] does not exist"
            elif e.response.status_code == 403:
                error_msg = "Access Denied"
            else:
                error_msg = "There was an error getting object info from the DRS Client"
            http.clear()
            exit_download(url, 1, error_msg, exit_codes)
            return
        except Exception as e:
            http.clear()
            exit_download(
                url,
                1,
                f"There was an error getting object info from the DRS Client: {e}",
                exit_codes,
            )
            return

        if "access_methods" in object_info.keys():
            access_methods = object_info["access_methods"][0]
            for access_method in [am for am in access_methods if am["type"] == "https"]:
                # try to use the access_id to get the download url
                if "access_id" in access_method.keys():
                    object_access = drs_client.get_object_access(
                        object_id, access_method["access_id"]
                    )
                    download_url = object_access["url"][0]
                    break
                # if we have a direct access_url for the access_method, use that
                elif "access_url" in access_method.keys():
                    download_url = access_method["access_url"]["url"]
                    break

            if not download_url:
                # we couldn't find a download url, exit unsuccessful
                http.clear()
                exit_download(
                    url,
                    1,
                    f"Error determining access method",
                    exit_codes,
                )
        else:
            return  # next page token, just return
    else:
        http.clear()
        exit_download(url, 1, f"[{url}] is not a valid DRS url", exit_codes)
        return

    try:
        download_stream = http.request("GET", download_url, preload_content=False)
    except Exception as e:
        http.clear()
        exit_download(
            url, 1, f"There was an error downloading [{download_url}] : {e}", exit_codes
        )
        return

    download_filename = get_filename_from_url(download_url)

    if out is not None:
        data = handle_file_response(download_filename, download_stream.read())
        output_lock.acquire()
        out.append(file_to_dataframe(download_filename, data))
        output_lock.release()

    else:
        with open(f"{output_dir}/{download_filename}", "wb+") as dest:
            stream_size = int(download_stream.headers["Content-Length"])
            file_stream = download_stream.stream(chunk_size)
            if not quiet:
                click.echo(f"Downloading {url} into {output_dir}/{download_filename}")
                with click.progressbar(
                    length=stream_size, color=True
                ) as download_progress:
                    for chunk in file_stream:
                        dest.write(chunk)
                        download_progress.update(chunk_size)
            else:
                for chunk in file_stream:
                    dest.write(chunk)
    http.clear()
    exit_download(url, 0, "Download Successful", exit_codes)


def download_files(
    urls,
    output_dir=downloads_directory,
    oauth_token: Optional[dict] = None,
    quiet: bool = False,
    out=None,
):
    download_threads = []
    exit_codes = {}

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for url in urls:
        download = threading.Thread(
            target=download_file(
                url,
                output_dir,
                oauth_token,
                quiet=quiet,
                out=out,
                exit_codes=exit_codes,
            ),
            name=url,
        )
        download.daemon = True
        download_threads.append(download)
        download.start()

    for thread in download_threads:
        thread.join()

    # at least one download failed, raise an exception
    failed_downloads = [
        {"url": url, "code": result[0], "message": result[1]}
        for url, result in exit_codes.items()
        if result[0] != 0
    ]
    if len(failed_downloads) > 0:
        error_msg = f"One or more downloads failed:\n"
        for failure in failed_downloads:
            error_msg += f"[{failure['url']}] failed with code {failure['code']}: {failure['message']}\n"
        raise Exception(error_msg)
