from io import StringIO
from typing import IO, Callable, Optional

from comprehemd import MarkdownParser
from dinject.enums import Content, Host
from dinject.types import ParserOptions
from doutline.writers import render_markdown

from edition.html_renderer import EditionHtmlRenderer
from edition.presses.press import Press


class MarkdownPress(Press):
    @property
    def injection_options(self) -> ParserOptions:
        return ParserOptions(force_content=Content.MARKDOWN, force_host=Host.SHELL)

    def _press(self, writer: IO[str]) -> None:
        reader = StringIO(self._markdown_body)

        toc_writer: Optional[Callable[[IO[str], int, int], None]] = None
        outline_root = self._metadata.get("outline", None)

        if outline_root is not None:

            def render_toc(writer: IO[str], hi: int, lo: int) -> None:
                if outline_root:
                    render_markdown(outline_root, writer, hi=hi, hyperlinks=True, lo=lo)

            toc_writer = render_toc

        for block in MarkdownParser().read(reader):
            if not block.source.startswith("<edition "):
                writer.write(block.source)
                writer.write("\n")
                continue

            renderer = EditionHtmlRenderer(
                metadata=self._metadata,
                toc_writer=toc_writer,
            )

            renderer.render(
                reader=StringIO(block.source),
                writer=writer,
            )
            writer.write("\n")
