import os
import re
from sre_constants import GROUPREF
from typing import Dict, Union, cast
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

import requests
from pydantic import AnyHttpUrl

from .models import BlockID, PathSpec, SrcID, VersionID


def update_query(
    url: AnyHttpUrl,
    query: Dict[str, str],
) -> AnyHttpUrl:
    """Add query strings to URL"""
    parsed_url = urlparse(url)
    parsed_query = parse_qs(parsed_url.query)
    parsed_query.update(query)
    unparsed_url = urlunparse(
        tuple(parsed_url[:4] + (urlencode(parsed_query, doseq=True),) + parsed_url[5:])
    )
    return unparsed_url


def is_url(value: str) -> bool:
    """Returns True if value is URL"""
    return urlparse(value).scheme and urlparse(value).netloc


def github_to_raw(url: AnyHttpUrl) -> AnyHttpUrl:
    """Converts a github.com URL to raw.githubusercontent.com URL...

    Sketchy.
    """
    return url.replace("github.com", "raw.githubusercontent.com").replace("/blob/", "/")


def title_to_name(title: str) -> str:
    """Replace all non-alphanumeric characters with hyphens"""
    name = re.sub("[^0-9a-z]+", "-", title.lower())[:50]
    while name.startswith("-"):
        name = name[1:]
    while name.endswith("-"):
        name = name[:-1]
    return name


def filename_to_title(filename: str) -> str:
    """Remove path and extension from filename"""
    return filename.split(os.path.sep)[-1].rsplit(".", 1)[0]


OXA_LINK = r"oxa:([a-zA-Z0-9]+)/([a-zA-Z0-9]+)\.([0-9]+)"
FULL_URL = r"http[s]*://.*/@([a-z0-9]{1}[a-z0-9_]+)/([a-zA-Z0-9]{1}[a-zA-Z0-9-]+)/([!a-zA-Z0-9]{1}[a-zA-Z0-9-]+)\.([0-9]+)"
PINNED_BLOCK_URL = r"http[s]*://.*/@([a-z0-9]{1}[a-z0-9_]+)/([a-zA-Z0-9]{1}[a-zA-Z0-9-]+)/([!a-zA-Z0-9]{1}[a-zA-Z0-9-]+)"
PROJECT_URL = r"http[s]*://.*/@([a-z0-9]{1}[a-z0-9_]+)/([a-zA-Z0-9-]+)"
TEAM_URL = r"http[s]*://.*/@([a-z0-9]{1}[a-z0-9_]+)"


def decode_oxa_link(url: str) -> VersionID:
    """
    Retreive a valid Curvenote VersionID from the oxa link
    """
    match = re.search(OXA_LINK, url)
    if match:
        project, block, version = match.groups()
        return VersionID(project=project, block=block, version=int(version))
    raise ValueError("Not a valid oxa link")


def decode_url(url: str) -> Union[VersionID, PathSpec]:
    """
    Retreive a valid Curvenote path spec from the url
    """
    match = re.search(FULL_URL, url)
    if match:
        team, project, block, version = match.groups()
        return PathSpec(
            team=team,
            project=project,
            block=block[1:] if block[0] == "!" else block,
            version=int(version),
        )

    match = re.search(PINNED_BLOCK_URL, url)
    if match:
        team, project, block = match.groups()
        return PathSpec(
            team=team,
            project=project,
            block=block[1:] if block[0] == "!" else block,
        )

    match = re.search(PROJECT_URL, url)
    if match:
        team, project = match.groups()
        return PathSpec(
            team=team,
            project=project,
        )

    match = re.search(TEAM_URL, url)
    if match:
        print(match.groups())
        (team,) = match.groups()
        return PathSpec(team=team)

    raise ValueError("Not a valid Curvenote url")


def fetch(url: str):
    resp = requests.get(url)
    if resp.status_code >= 400:
        raise ValueError(resp.content)
    return resp.content


def download(url, save_path, chunk_size=128):
    """
    Download a file from a url and save to the save_path provided
    """
    resp = requests.get(url, stream=True)
    with open(save_path, "wb") as file:
        for chunk in resp.iter_content(chunk_size=chunk_size):
            file.write(chunk)


def id_to_api_url(base: str, the_id: Union[BlockID, VersionID, SrcID]):
    if "version" in the_id.__dict__:
        version_id = cast(VersionID, the_id)
        return f"{base}/blocks/{version_id.project}/{version_id.block}/versions/{version_id.version}"
    else:
        return f"{base}/blocks/{the_id.project}/{the_id.block}"
