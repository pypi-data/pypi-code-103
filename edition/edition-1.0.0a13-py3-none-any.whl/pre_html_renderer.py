from html.parser import HTMLParser
from sys import stdout
from typing import IO, List, Optional, Tuple

from edition.html import to_anchor_id

TAttribute = Tuple[str, Optional[str]]


class PreHtmlRenderer(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self._writer: IO[str] = stdout
        self._current_heading: Optional[str] = None
        self._current_heading_text: str = ""

    def handle_data(self, data: str) -> None:
        if self._current_heading:
            self._current_heading_text += data
        self._writer.write(data)

    def handle_decl(self, decl: str) -> None:
        self._writer.write(f"<!{decl}>")

    def handle_endtag(self, tag: str) -> None:
        if self._current_heading and self._current_heading == tag:
            self._writer.write(
                f'<a id="{to_anchor_id(self._current_heading_text)}"></a>'
            )
            self._current_heading = None
        self._writer.write(f"</{tag}>")

    def handle_startendtag(self, tag: str, attrs: List[TAttribute]) -> None:
        attributes = self.make_attributes(attrs) if attrs else ""
        inner = f"{tag} {attributes}".strip()
        self._writer.write(f"<{inner} />")

    def handle_starttag(self, tag: str, attrs: Optional[List[TAttribute]]) -> None:
        if tag in ["h2", "h3", "h4", "h5", "h6"]:
            self._current_heading = tag
            self._current_heading_text = ""

        attributes = self.make_attributes(attrs) if attrs else ""
        inner = f"{tag} {attributes}".strip()
        self._writer.write(f"<{inner}>")

    def make_attribute(self, attribute: TAttribute) -> str:
        return f'{attribute[0]}="{attribute[1]}"'

    def make_attributes(self, attributes: List[TAttribute]) -> str:
        return " ".join([self.make_attribute(a) for a in attributes])

    def render(self, body: str, writer: IO[str]) -> None:
        self._writer = writer
        self.feed(body)
        self.close()
