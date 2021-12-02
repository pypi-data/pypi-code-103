import re
from itertools import chain
from typing import List


def run_regex_matchers(regex_matchers: List[str], content: str):
    """
    Will run one of more regex matchers and concatenate the resulting
    match iterators
    """
    list_of_matches = []
    for matcher in regex_matchers:
        match = re.finditer(matcher, content)
        list_of_matches.append(match)
    return (
        list(chain(*list_of_matches))
        if len(list_of_matches) > 1
        else list_of_matches[0]
    )
