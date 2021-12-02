import re
from typing import Union

from curvenote.latex.utils.regex import (
    EXTRACT_UNPINNED_OXA_REGEX,
    FULL_URL,
    GROUPED_BLOCK_REGEX,
    GROUPED_OXA_REGEX,
    OXA_LINK,
    P1B1VB2V_GROUPED_OXA_REGEX,
    PINNED_BLOCK_URL,
    PROJECT_URL,
    TEAM_URL,
)
from curvenote.models import BlockChildID, BlockFormat, PathSpec, VersionID


def block_hash_to_api_url(
    api_url: str, block_hash: str, fmt: Union[BlockFormat, None] = None
):
    """
    Converts a block hash with format:
        `block:project1/block1/v

    into a valid api url
    """
    query = ""
    if fmt is not None:
        query = f"?format={fmt}"
    match = re.search(GROUPED_BLOCK_REGEX, block_hash)
    if match:
        if match[3]:
            return f"{api_url}/blocks/{match[1]}/{match[2]}/versions/{match[3]}{query}"
        return f"{api_url}/blocks/{match[1]}/{match[2]}{query}"
    raise ValueError(f"invalid block hash {block_hash}")


def oxa_path_to_api_url(
    api_url: str, oxa_path: str, fmt: Union[BlockFormat, None] = None
):
    """
    Converts a oxa path with format:
        `oxa:project1/block1.version

    into a valid api url
    """
    query = ""
    if fmt is not None:
        query = f"?format={fmt}"
    match = re.search(GROUPED_OXA_REGEX, oxa_path)
    if match:
        if match[3]:
            return f"{api_url}/blocks/{match[1]}/{match[2]}/versions/{match[3]}{query}"
        return f"{api_url}/blocks/{match[1]}/{match[2]}{query}"
    raise ValueError(f"invalid oxa path {oxa_path}")


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


def version_id_to_block_path(block_id: BlockChildID):
    return f"block:{block_id.project}/{block_id.block}/{block_id.version}"


def version_id_to_oxa_path(block_id: BlockChildID):
    return f"oxa:{block_id.project}/{block_id.block}.{block_id.version}"


def version_id_to_local_path(block_id: BlockChildID):
    return f"images/{block_id.project}_{block_id.block}_{block_id.version}"


def unpin_oxa_path(oxa_path: str):
    """
    Take an oxa path or oxa link and return the unpinned version
    Should work for links as well as paths

    e.g.
        oxa:project1/block2.1 -> oxa:project1/block2
        oxa:project1/block1.1:project2/block2.1#id -> oxa:block1.1:project2/block2
        http://api.curvenote.com:8888/oxa:project1/block2.1 -> http://api.curvenote.com:8888/oxa:project1/block2

    If there is no match we assume it's already unpinned and return the argument
    """
    match = re.search(EXTRACT_UNPINNED_OXA_REGEX, oxa_path)
    return oxa_path if match is None else match[1]


def minimise_oxa_path(oxa_path: str):
    """
    Take an oxa path or oxa link and return the most compact version of it without any context

    e.g.
        oxa:project1/block1.1:project2/block2.1#id -> oxa:block1.1:project2/block2

    If no match for a long form oxa path is found, the argument will be returned

    TODO needs extended to other cases
    """
    match = re.search(P1B1VB2V_GROUPED_OXA_REGEX, oxa_path)
    if match is None:
        return oxa_path

    return f"oxa:{match[1]}/{match[4]}.{match[5]}"
