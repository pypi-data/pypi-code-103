"""
Detect important environmental packages/libraries.
"""
import os
import re
from pathlib import Path
from typing import List

from jaepeto.utils import post


def read_packages(project_dir: Path) -> List[str]:
    packages = []

    if "requirements.txt" in os.listdir(project_dir):
        with open(project_dir / "requirements.txt", "r") as f:
            contents = f.readlines()

        if new_packages := post("parse-reqs/requirements", contents):
            packages.extend(new_packages)

    for _file in ("environment.yml", "environment.yaml"):
        if _file in os.listdir(project_dir):
            with open(project_dir / _file, "r") as f:
                contents = f.readlines()

            if new_packages := post("parse-reqs/environment", contents):
                packages.extend(new_packages)

    return packages


class PyVersionDetector:
    def __init__(self):
        self.PY37 = 37
        self.PY38 = 38
        self.PY39 = 39
        self.PY310 = 310
        self._version = None
        self.possible_versions = (self.PY38, self.PY39, self.PY310)

        # 3.8
        self._walrus = []
        self._walrus_pattern = re.compile(r"if\s\(?\w*\s?:=\s?.+\)?")

        # 3.9
        self._dict_union = []
        self._dict_union_pattern = re.compile(
            rf"^\s*(?:\w+(?:\s?:\s?\w+(?:\[\w+:\w+\])?)?\s?=\s?)?[\w_]+\s?\|\s?[\w_]+"
        )

        # 3.10
        self._pipe_optional = []
        self._pipe_pattern = re.compile(
            rf":\s?\w+(?:\[\w+:?\w+\])?\s?\|\s?\w+(?:\[\w+:?\w+\])?\s?[,\)=]"
        )

        self._type_hint = []
        self._match_operator = []

    @property
    def version(self) -> str:
        _ver = str(self._version) if self._version else str(self.PY37)
        _ver = _ver[0] + "." + _ver[1:]
        return _ver

    def review(self, filename: str, code_contents: List[str]) -> None:
        __version = self.PY37 if not self._version else self._version

        for considered_version in self.possible_versions:
            if considered_version <= __version:
                continue

            if considered_version == self.PY38:
                self._match_38(filename, code_contents)
            elif considered_version == self.PY39:
                self._match_39(filename, code_contents)
            elif considered_version == self.PY310:
                self._match_310(filename, code_contents)

    def _match_38(self, filename: str, code_contents: List[str]) -> None:
        for _code in code_contents:
            if walrus := self._walrus_pattern.search(_code):
                self._walrus.append(filename)
                self._version = self.PY38

    def _match_39(self, filename: str, code_contents: List[str]) -> None:
        for _code in code_contents:
            if pipe_dict := self._dict_union_pattern.search(_code):
                self._dict_union.append(filename)
                self._version = self.PY39

    def _match_310(self, filename: str, code_contents: List[str]) -> None:
        for _code in code_contents:
            if pipe := self._pipe_pattern.search(_code):
                self._pipe_optional.append(filename)
                self._version = self.PY310

    def __str__(self):
        if not self._version:
            return """
                    No exact compatable Python version has been detected.
                    Versions below 3.8 are compatable.
                    """

        return f"""
                The codebase is compatible with Python {self.version} and below.
                """
