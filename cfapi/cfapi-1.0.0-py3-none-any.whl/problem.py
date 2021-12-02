from .base import Base

import re
from urllib.parse import urljoin
from dataclasses import dataclass
from copy import copy

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Optional, Tuple
    from bs4 import BeautifulSoup


@dataclass(frozen=True)
class SampleTest:
    input: str
    output: str


class Problem(Base):

    _FROM_URL_REGEX = re.compile(
        "/(?P<setid>[0-9]+)(/.*)*/(?P<problemid>[a-zA-Z]+[0-9]*)"
    )
    _SPLIT_IDENTIFIER_REGEX = re.compile(
        "(?P<setid>[0-9]+)(?P<problemid>[a-zA-Z]+[0-9]*)"
    )

    @classmethod
    def identifier_from_url(cls, url: str) -> "Optional[str]":
        result = re.search(cls._FROM_URL_REGEX, url)
        if result:
            return result.group("setid") + result.group("problemid")

    @property
    def url(self) -> str:
        match = self._SPLIT_IDENTIFIER_REGEX.match(self.identifier)
        set, id = match.group("setid", "problemid")
        return urljoin(self.BASE_URL, f"contest/{set}/problem/{id}")

    # ------------------------------------------------------ Helper methods -- #

    def _get_header_entry(self, name: str) -> str:
        header = self.data.find("div", {"class": "header"})
        entry = header.find("div", {"class": name})
        return entry.find(text=True, recursive=False).get_text()

    @staticmethod
    def _soup_to_html(soup: "Optional[BeautifulSoup]") -> "Optional[str]":
        if soup is not None:
            return str(soup)

    @staticmethod
    def _soup_to_text(soup: "Optional[BeautifulSoup]") -> "Optional[str]":
        if soup is not None:
            return "\n".join(line.get_text() for line in soup.children)

    # ----------------------------------------------------------- Statement -- #

    @property
    def statement_soup(self) -> "BeautifulSoup":
        soup = copy(self.data.find("div", {"class": "problem-statement"}))

        for elem in soup.find_all("div", attrs={"class": True}, recursive=False):
            # Remove special sections that are provided using other methods
            elem.extract()

        return soup

    @property
    def statement_html(self) -> str:
        return str(self.statement_soup)

    @property
    def statement_text(self) -> str:
        return "\n".join(
            paragraph.get_text()
            for section in self.statement_soup.children
            for paragraph in section.children
        )

    # ---------------------------------------------------------------- Note -- #

    @property
    def note_soup(self) -> "Optional[BeautifulSoup]":
        problem = self.data.find("div", {"class": "problem-statement"})
        return problem.find("div", {"class": "note"})

    @property
    def note_text(self) -> "Optional[str]":
        return self._soup_to_text(self.note_soup)

    @property
    def note_html(self) -> "Optional[str]":
        return self._soup_to_html(self.note_soup)

    # ------------------------------------------------- Input specification -- #

    @property
    def input_specification_soup(self) -> "Optional[BeautifulSoup]":
        problem = self.data.find("div", {"class": "problem-statement"})
        return problem.find("div", {"class": "input-specification"})

    @property
    def input_specification_text(self) -> "Optional[str]":
        return self._soup_to_text(self.input_specification_soup)

    @property
    def input_specification_html(self) -> "Optional[str]":
        return self._soup_to_html(self.input_specification_soup)

    # ------------------------------------------------ Output specification -- #

    @property
    def output_specification_soup(self) -> "Optional[BeautifulSoup]":
        problem = self.data.find("div", {"class": "problem-statement"})
        return problem.find("div", {"class": "output-specification"})

    @property
    def output_specification_text(self) -> "Optional[str]":
        return self._soup_to_text(self.output_specification_soup)

    @property
    def output_specification_html(self) -> "Optional[str]":
        return self._soup_to_html(self.output_specification_soup)

    # ----------------------------------------------------- Header Metadata -- #

    @property
    def title(self) -> str:
        return self._get_header_entry("title")

    @property
    def time_limit(self) -> str:
        return self._get_header_entry("time-limit")

    @property
    def memory_limit(self) -> str:
        return self._get_header_entry("memory-limit")

    @property
    def input_file(self) -> str:
        return self._get_header_entry("input-file")

    @property
    def output_file(self) -> str:
        return self._get_header_entry("output-file")

    # -------------------------------------------------------- Sample Tests -- #

    @property
    def sample_tests(self) -> "Tuple[SampleTest]":
        div = self.data.find("div", {"class": "problem-statement"})
        tests = div.find("div", {"class": "sample-test"})

        inputs = (t.pre.get_text() for t in tests.find_all("div", {"class": "input"}))
        outputs = (t.pre.get_text() for t in tests.find_all("div", {"class": "output"}))

        return tuple(SampleTest(i, o) for i, o in zip(inputs, outputs))
