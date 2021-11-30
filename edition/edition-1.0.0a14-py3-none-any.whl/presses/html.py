from io import StringIO
from typing import IO, Callable, Optional

from comprehemd import CodeBlock, MarkdownParser
from dinject.enums import Content, Host
from dinject.types import ParserOptions
from doutline.writers import render_html
from markdown import markdown
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name, guess_lexer

from edition.html import get_html_template
from edition.html_renderer import EditionHtmlRenderer
from edition.pre_html_renderer import PreHtmlRenderer
from edition.presses.press import Press


class HtmlPress(Press):
    @property
    def injection_options(self) -> ParserOptions:
        return ParserOptions(force_content=Content.HTML, force_host=Host.TERMINAL)

    def _replace_blocks_with_pygments(self, body: str) -> str:
        writer = StringIO()

        for block in MarkdownParser().read(StringIO(body)):
            if isinstance(block, CodeBlock):
                lexer = (
                    get_lexer_by_name(block.language)
                    if block.language
                    else guess_lexer(block.text)
                )
                formatter = HtmlFormatter()
                highlight(block.text, lexer, formatter, writer)
            else:
                writer.write(block.source)
                writer.write("\n")

        return writer.getvalue().rstrip()

    def _post_injection(self) -> None:
        self._markdown_body = self._replace_blocks_with_pygments(self._markdown_body)

    def _press(self, writer: IO[str]) -> None:
        html_body = markdown(
            self._markdown_body,
            extensions=["markdown.extensions.tables"],
            output_format="html",
        )

        processed_html = StringIO()

        # This initial run adds anchors to headers. This could probably be added
        # to EditionHtmlRenderer, but remember to feed in just the body here:
        PreHtmlRenderer().render(html_body, processed_html)

        processed_html.seek(0)

        html_body_writer = StringIO()

        toc_writer: Optional[Callable[[IO[str], int, int], None]] = None
        outline_root = self._metadata.get("outline", None)

        if outline_root is not None:

            def render_toc(writer: IO[str], hi: int, lo: int) -> None:
                if outline_root:
                    render_html(outline_root, writer, hi=hi, hyperlinks=True, lo=lo)

            toc_writer = render_toc

        edition_renderer = EditionHtmlRenderer(
            metadata=self._metadata, toc_writer=toc_writer
        )
        edition_renderer.render(reader=processed_html, writer=html_body_writer)

        self._metadata["body"] = html_body_writer.getvalue()

        with get_html_template() as f:
            edition_renderer.render(reader=f, writer=writer)
