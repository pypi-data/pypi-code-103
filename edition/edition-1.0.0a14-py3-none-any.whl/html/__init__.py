from importlib.resources import open_text
from typing import IO


def to_anchor_id(text: str) -> str:
    """
    Converts `text` to an anchor ID.

    This method is intended to be compatible with GitHub's method of converting heading
    text to anchors for tables of content.
    """

    a = ""
    for c in text:
        if c in [" ", "-"]:
            a += "-"
        elif str.isalnum(c):
            a += c.lower()
    return a


def get_css() -> IO[str]:
    """
    Returns a reader for the CSS.

    The onus is on the caller to close the reader when finished with it.
    """

    return open_text(__package__, "style.css")


def get_html_template() -> IO[str]:
    """
    Returns a reader for the HTML template.

    The onus is on the caller to close the reader when finished with it.
    """

    return open_text(__package__, "document.html")
