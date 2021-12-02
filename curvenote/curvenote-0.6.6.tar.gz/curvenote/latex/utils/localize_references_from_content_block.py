import logging
import re
from typing import List

from curvenote.models import Block, BlockVersion

from ...client import Session
from .index import LocalMarker, get_model
from .links import block_hash_to_api_url, oxa_path_to_api_url, unpin_oxa_path
from .parse_cite_tag_from_bibtex import parse_cite_tag_from_bibtex
from .regex import (
    BLOCK_REGEX,
    INLINE_CITATION_BLOCK_REGEX,
    INLINE_CITATION_OXA_REGEX,
    OXA_REGEX,
    UNPINNED_BLOCK_REGEX_ENDLINE,
    UNPINNED_BLOCK_REGEX_INLINE,
    UNPINNED_OXA_REGEX_ENDLINE,
    UNPINNED_OXA_REGEX_INLINE,
)
from .run_regex_matchers import run_regex_matchers


def split_remote_paths(remote_path: str) -> List[str]:
    """Splits a remote path into a list of block_paths or oxa_paths"""
    matches = run_regex_matchers(
        [
            OXA_REGEX,
            UNPINNED_OXA_REGEX_ENDLINE,
            UNPINNED_OXA_REGEX_INLINE,
            BLOCK_REGEX,
            UNPINNED_BLOCK_REGEX_ENDLINE,
            UNPINNED_BLOCK_REGEX_INLINE,
        ],
        remote_path,
    )

    if len(matches) == 0:
        return [remote_path]

    if len(matches) > 1:
        logging.info("Found group of %s paths, splitting...", len(matches))

    return [m[0] for m in matches]


def localize_references_from_content_block(
    session: Session, reference_list: List[LocalMarker], content: str
):
    """Looks for cite TeX commands in the content then replaces the block ids
    with locally unique identifiers based on the local reference list.

    The reference list is extended as new references are found (side effect)

    Appends a unique hash to each new reference encountered
    """
    patched_content = content

    matches = run_regex_matchers(
        [INLINE_CITATION_BLOCK_REGEX, INLINE_CITATION_OXA_REGEX], content
    )

    # citep blocks can contain multiple citations, so we need to iterate over
    # the list of matches, check each one and split them
    remote_paths: List[str] = []
    for match in matches:
        remote_paths += split_remote_paths(match[1])

    for remote_path in remote_paths:
        logging.info("processing remote path: %s", remote_path)
        # check for the reference in the reference list based on the block_path
        matched_references = [r for r in reference_list if r.remote_path == remote_path]
        existing_reference = (
            matched_references[0] if (len(matched_references) > 0) else None
        )

        if existing_reference is None:
            if remote_path.startswith("oxa:"):
                unpinned_path = unpin_oxa_path(remote_path)
                url = oxa_path_to_api_url(session.api_url, unpinned_path)
            else:
                url = block_hash_to_api_url(session.api_url, remote_path)

            logging.info("fetching reference block %s", url)
            block = get_model(session, url, Block)
            logging.info("got reference block")

            # get latest version
            version_url = f"{url}/versions/{block.latest_version}?format=bibtex"
            logging.info("fetching reference version %s", version_url)
            version = get_model(session, version_url, BlockVersion)
            logging.info("got reference version")

            # update the list
            bibtex_content: str = version.content
            _, plain_tag = parse_cite_tag_from_bibtex(bibtex_content)

            reference_item = LocalMarker(
                plain_tag, remote_path, plain_tag, bibtex_content
            )
            reference_list.append(reference_item)
            existing_reference = reference_item
            logging.info("using new reference %s", existing_reference.marker)
        else:
            logging.info("using existing reference %s", existing_reference.marker)

        # patch the content and move on
        patched_content = patched_content.replace(
            remote_path, existing_reference.marker
        )

    return patched_content
