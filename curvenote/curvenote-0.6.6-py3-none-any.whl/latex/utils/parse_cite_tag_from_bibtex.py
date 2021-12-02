import logging
import re

from .get_fast_hash import get_fast_hash

BIBTEX_ENTRY_TYPES = [
    "article",
    "book",
    "booklet",
    "conference",
    "inbook",
    "incollection",
    "inproceedings",
    "manual",
    "mastersthesis",
    "misc",
    "phdthesis",
    "proceedings",
    "techreport",
    "unpublished",
]


def parse_cite_tag_from_bibtex(content: str):
    logging.debug("bibtex: %s", content)
    tag = "ref"
    logging.debug(r"@[a-z]{3,}{([0-9a-zA-Z_]+),")
    match = re.match(r"@[a-z]{3,}{([0-9a-zA-Z_]+),", content)
    if match is not None:
        logging.debug("match %s", match)
        tag = match[1].replace(",", "")
    # adding quasi-random hash to save de-duping work
    hash_id = get_fast_hash()
    tag_with_hash = f"{tag}_{hash_id}"

    return tag_with_hash, tag
