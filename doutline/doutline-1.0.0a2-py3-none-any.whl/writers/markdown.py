from typing import IO, Optional

from doutline.outline import OutlineNode
from doutline.writers.utils import make_anchor


def render_markdown(
    node: OutlineNode[str],
    writer: IO[str],
    hi: Optional[int] = None,
    hyperlinks: bool = False,
    indent: int = 0,
    lo: Optional[int] = None,
) -> None:
    """
    Renders the node to a Markdown fragment.

    Arguments:
        node:   Node to render.
        writer: Writer.
        hi:     Highest level to include.
        indent: Indent spaces.
        lo:     Lowest level to include.
    """

    if node.data and node.in_range(hi, lo):
        prefix = " " * indent

        if hyperlinks:
            value = f"[{node.data}](#{make_anchor(node.data)})"
        else:
            value = node.data

        line = f"{prefix}- {value}\n"
        writer.write(line)
        indent += 2

    for child in node.children:
        render_markdown(
            child,
            writer,
            hi=hi,
            hyperlinks=hyperlinks,
            indent=indent,
            lo=lo,
        )
