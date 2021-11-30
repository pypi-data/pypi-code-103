from dataclasses import dataclass
from io import StringIO
from logging import getLogger
from typing import IO, Optional

from doutline.outline import OutlineNode
from doutline.writers.utils import make_anchor


@dataclass
class RenderHtmlResult:
    wrote_line: bool
    wrote_children: bool


def render_html(
    node: OutlineNode[str],
    writer: IO[str],
    hi: Optional[int] = None,
    hyperlinks: bool = False,
    lo: Optional[int] = None,
    root: bool = True,
) -> RenderHtmlResult:
    """returns: wrote line, not counting children"""

    logger = getLogger("doutline")

    inner_writer = StringIO()

    line: Optional[str] = None

    if node.data and node.in_range(hi, lo):
        if hyperlinks:
            line = f'<a href="#{make_anchor(node.data)}">{node.data}</a>'
        else:
            line = str(node.data)

    if line is not None:
        inner_writer.write("<li>")
        inner_writer.write(line)

    child_writer = StringIO()

    wrote_any_children = False

    for child in node.children:
        inner_result = render_html(
            child,
            child_writer,
            hi=hi,
            hyperlinks=hyperlinks,
            lo=lo,
            root=False,
        )
        wrote_any_children = wrote_any_children or inner_result.wrote_line

    if child_writer.getvalue():
        write_ul = not child_writer.getvalue().startswith("<ol>")
        if write_ul:
            logger.debug("Writing UL because: %s", child_writer.getvalue())
            inner_writer.write("<ol>")
        inner_writer.write(child_writer.getvalue())
        if write_ul:
            inner_writer.write("</ol>")

    if line is not None:
        inner_writer.write("</li>")

    if inner_writer.getvalue():
        if root:
            writer.write('<nav class="toc">')
        writer.write(inner_writer.getvalue())
        if root:
            writer.write("</nav>")

    return RenderHtmlResult(
        wrote_line=line is not None,
        wrote_children=wrote_any_children,
    )
