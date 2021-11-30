from io import StringIO
from typing import Dict, List, Tuple, Type, cast

import frontmatter  # pyright: reportMissingTypeStubs=false
from comprehemd import HeadingBlock, MarkdownParser
from doutline import OutlineNode

from edition.exceptions import NoPressError
from edition.metadata import Metadata
from edition.presses.html import HtmlPress
from edition.presses.markdown import MarkdownPress
from edition.presses.press import Press

registered: Dict[str, Type[Press]] = {}


def keys() -> List[str]:
    return [k for k in registered]


def make(key: str, markdown_content: str) -> "Press":
    press = registered.get(key, None)
    if not press:
        raise NoPressError(key)

    metadata, markdown_body = cast(
        Tuple[Metadata, str],
        frontmatter.parse(markdown_content),
    )  # pyright: reportUnknownMemberType=false

    outline_root = OutlineNode[str]()
    metadata["outline"] = outline_root

    # Extract metadata:
    for block in MarkdownParser().read(StringIO(markdown_body)):
        if isinstance(block, HeadingBlock):
            if block.level == 1:
                metadata["title"] = metadata.get("title", block.text)
            outline_root.append(block.level, block.text)

    return press(markdown_body=markdown_body, metadata=metadata)


def register(key: str, press: Type[Press]) -> None:
    registered[key] = press


register("html", HtmlPress)
register("markdown", MarkdownPress)

__all__ = [
    "HtmlPress",
    "MarkdownPress",
    "Press",
]
