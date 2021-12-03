"""Clean a html page."""

import re
from typing import Union

from bs4 import BeautifulSoup
from bs4.element import NavigableString, Tag

TAGS_TO_REMOVE = [
    "header",
    "head",
    "footer",
    "nav",
    "script",
    "noscript",
    "style",
    "iframe",
    "svg",
    "input",
    "button",
    "textarea",
    "button",
    "checkbox",
    "label",
]
TAGS_HEADERS = {"h" + str(i) for i in range(6)}
TAGS_FORCE_NEWLINE = {"tbody", "thead", "section", "p"}
TAGS_SPACE = {"a", "strong", "i"}
TAGS_TAB = {"th", "td"}

TO_STRIP = "\t\n "


def get_text_recursive(tag: Union[Tag, NavigableString, None]) -> str:
    """Extract the text using the childrens."""
    if tag is None:
        return ""
    if isinstance(tag, NavigableString):
        return str(tag).strip().replace("\n", " ")

    tag_name = tag.name

    # Special tags, like headers, lists, tables, ...
    if tag_name in TAGS_HEADERS:
        return (
            "\n" * 2
            + " ".join(
                filter(
                    lambda x: len(x) > 0,
                    [get_text_recursive(x) for x in tag.children if x is not None],
                )
            )
            + "\n"
        )
    if tag_name in {"ul", "ol"}:
        return (
            "\n".join(
                map(
                    lambda x: "- " + x,
                    filter(
                        lambda x: len(x) > 0,
                        [get_text_recursive(x) for x in tag.children if x is not None],
                    ),
                )
            )
            + "\n" * 2
        )
    if tag_name == "tr":
        return (
            "- "
            + ";  ".join(
                filter(
                    lambda x: len(x) > 0,
                    [get_text_recursive(x) for x in tag.children if x is not None],
                ),
            )
            + "\n" * 2
        )

    # What should be the end, after the text of the element
    if tag_name in TAGS_FORCE_NEWLINE:
        end = "\n"
    elif tag_name in TAGS_SPACE:
        end = " "
    else:
        end = ""

    return (
        " ".join(
            filter(
                lambda x: len(x) > 0, [get_text_recursive(x) for x in tag.children if x is not None]
            )
        )
        + end
    )


def clean_html_to_text(raw_html: str) -> str:
    """Extract the meaningful text from the page."""
    # Preprocessing
    raw_html = re.sub(r"\<\!\-\-.*\-\-\>", "", raw_html)
    raw_html = re.sub(r"[”“”]", '"', raw_html)
    soup = BeautifulSoup(raw_html, features="html.parser").find("body")

    # Clean the soup before boiling/cooking it
    for to_remove in (
        soup.find_all(TAGS_TO_REMOVE)
        + soup.find_all(class_=re.compile(r"(header|footer)"))
        + soup.find_all(id=re.compile(r"(header|footer)"))
    ):
        to_remove.extract()

    # Get all the paragraphs / texts needed in the selected tags
    text = ""

    for tag in soup.find_all(recursive=False):
        if tag is None:
            continue
        text += get_text_recursive(tag)

    # Special processing
    text = re.sub(r"\n[ \t]+", "\n", text)
    text = re.sub(r" +", r" ", text)
    text = text.strip()

    return text
