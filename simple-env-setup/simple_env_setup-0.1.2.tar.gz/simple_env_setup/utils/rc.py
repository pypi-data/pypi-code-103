import re
from functools import partial
from os import environ
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

from simple_env_setup.utils.utils import (get_home_dir, last_words, read,
                                          run_python)

START_MARKER = "# ENV_SETUP_SECTION:"
END_MARKER = "# ENV_SETUP_SECTION_END:"

# ---------------------------------------------------------------------------- #
#                              rc Files Management                             #
# ---------------------------------------------------------------------------- #


class RcFile():
    def __init__(self, info: List[str] | Dict[str, List[str]] | Tuple[List[str], Dict[str, List[str]]]) -> None:
        if isinstance(info, dict):
            self.sections = list(info.keys())
            self.content = info
        elif isinstance(info, tuple):
            self.sections, self.content = info
        else:
            self.sections, self.content = self.parse_text(info)

    def select(self, sections: str | Iterable[str]) -> "RcFile":
        if isinstance(sections, str):
            sections = [sections]
        new_content: Dict[str, List[str]] = {}
        for section in sections:
            if section not in self.content:
                last_words(f"Missing section {section}.")
            new_content[section] = self.content[section]
        return RcFile((list(sections), new_content))

    def update(self, other: "RcFile") -> None:
        other_sections = list(
            filter(lambda key: not key.startswith("none"), other.sections))
        for other_section in other_sections:
            if other_section in self.sections and other_section in self.content:
                self.content[other_section] = other.content[other_section]
            elif (other_section not in self.sections) and (other_section not in self.content):
                self.sections.append(other_section)
                self.content[other_section] = other.content[other_section]
            else:
                last_words("If this prints, I am an idiot.")

    def to_text(self) -> str:
        text = ""
        for section in self.sections:

            is_none = section.startswith("none")

            if not is_none:
                text += f"{START_MARKER} {section}\n"

            text += "\n".join(self.content[section]) + "\n"

            if not is_none:
                text += f"{END_MARKER} {section}\n"

        return re.sub(r"\n{2,}", "\n\n", text).strip()

    def write(self, path: Path) -> None:
        with open(path, "w") as f:
            f.write(self.to_text())

    @staticmethod
    def parse_text(text: List[str]) -> Tuple[List[str], Dict[str, List[str]]]:
        sections = ["none_0"]
        content: Dict[str, List[str]] = {"none_0": []}
        none_count = 0
        current_section = "none_0"

        for line in text:
            # Identify markers
            is_section_start = line.startswith(START_MARKER)
            is_section_end = line.startswith(END_MARKER)

            if (not is_section_start) and (not is_section_end):
                # For normal line, append to current section
                content[current_section].append(line)

            elif is_section_start:
                # At section start, append keys
                current_section = line.replace(START_MARKER, "").strip()
                if current_section in content:
                    last_words(
                        f"Duplicated section {current_section}. Please manually fix it.")
                sections.append(current_section)
                content[current_section] = []

            elif is_section_end:
                # At section start, append keys
                ending_section = line.replace(END_MARKER, "").strip()
                if ending_section != current_section:
                    last_words(
                        f"Missing end marker for section {current_section}. Please manually fix it.")
                none_count += 1
                current_section = f"none_{none_count}"
                sections.append(current_section)
                content[current_section] = []

            else:
                last_words("I thought this can never happen logically?!")

        # Check last ending marker
        if not current_section.startswith("none"):
            ending_section = text[-1].replace(END_MARKER, "").strip()
            if ending_section != current_section:
                last_words(
                    f"Missing end marker for section {current_section}. Please manually fix it.")

        # Filter out empty items
        final_sections = list(
            filter(lambda key: len(content[key]) > -1, sections))
        final_content: Dict[str, List[str]] = {
            key: content[key] for key in final_sections}
        return final_sections, final_content


RC_TEMPLATE = RcFile(read(".shellrc").split())


def get_rc_path() -> Path:
    if environ.get("ENV_SETUP_DRY_RUN"):
        return Path("test.sh")
    rc_path = get_home_dir() / ".local" / ".shellrc"
    if rc_path.exists() and rc_path.is_file():
        return Path(rc_path)
    elif not rc_path.exists():
        with open(rc_path, "w") as _:
            pass
        return Path(rc_path)
    else:
        last_words(
            f"Something weird is going on with you {rc_path}. Consider deleting it.")


def get_rc() -> RcFile:
    return RcFile(open(get_rc_path(), "r").readlines())


@run_python
def _update_rc(info: List[str] | Dict[str, List[str]]) -> None:
    local_rc = get_rc()

    if isinstance(info, dict):
        new_rc = RcFile(info)
    else:
        new_rc = RC_TEMPLATE.select(info)
    local_rc.update(new_rc)
    local_rc.write(get_rc_path())


update_rc = partial(_update_rc, "update ~/.local/.shellrc")


@run_python
def add_rc_line(line: str, files: List[str] = [".zshrc", ".bashrc"]) -> None:
    for file in files:
        lines = open(get_home_dir() / file, "r").readlines()
        if line not in [item.strip() for item in lines]:
            lines.append(line + "\n")
        with open(get_home_dir() / file, "w") as f:
            f.writelines(lines)
