import re

from collections import namedtuple



Link = namedtuple('Link', ['text', 'url', 'hint'])


def get_pattern(prefix="") -> str:
    return fr'({prefix})\[(.*?)\]\((.+?)(?: \"(.*)\")?\)'


def url_safe(text: str) -> str:
    """Replace characters that are not URL-safe into dashes"""
    return re.sub(r'[^a-zA-Z_][^a-zA-Z0-9_]*', '-', text)


def link(string: str, prefix="") -> Link:
    """Generate text, url and title from string"""

    # If formatted as a link, return the features
    if m := re.match(get_pattern(prefix), string.strip()):
        text = m.group(2)
        url = url_safe(m.group(3))
        hint = m.group(4) or ""

    # Otherwise, generate features from the text
    else:
        text, url, hint = link_from_string(string)

    return Link(text, url, hint)


def link_from_string(string: str):
    """Generate link features from string"""
    return string, url_safe(string), ""