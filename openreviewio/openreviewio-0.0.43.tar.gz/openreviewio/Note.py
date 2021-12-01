# This file is part of openreviewio-py.
#
# openreviewio-py is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# openreviewio-py is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with openreviewio-py.  If not, see <https://www.gnu.org/licenses/>


from __future__ import annotations
from dataclasses import dataclass
from .base import ReviewItem
from typing import List, Union
from datetime import datetime, timezone
from pathlib import Path
from .Content import TextAnnotation, TextComment, Image, ImageAnnotation
import xml.etree.ElementTree as ET
from inspect import getmembers
import shutil
from xml.dom import minidom

# Typing
Content = Union[TextComment, TextAnnotation, Image, ImageAnnotation]


@dataclass
class Note(ReviewItem):
    _date = None
    author: str
    date: datetime = ""
    contents: Union[Content, List[Content]] = None
    parent: Note = None
    metadata: dict = None

    def __init__(
        self,
        author: str,
        date: Union[str, datetime] = None,
        contents: Union[Content, List[Content]] = None,
        parent: Note = None,
        metadata: dict = None,
    ):
        """Contains contents.

        :param author: Author of the note.
        :param date: Note's time of creation, provided as ISO UTC (datetime.now(timezone.utc).isoformat()).
        :param contents: All note's contents. You can pass a single content at construction.
        :param parent: Note to reply to.
        :param metadata: Note metadata.
        """
        super().__init__()

        self.author = author

        if date:
            self.date = date
        else:
            self.date = datetime.now(timezone.utc).isoformat()

        self.contents = []
        if contents:
            self.add_content(contents)

        self.parent = parent

        self.metadata = metadata or {}

    @property
    def date(self):
        return self._date

    @date.setter
    def date(self, value):
        if isinstance(value, datetime):
            self._date = value
        else:
            self._date = datetime.fromisoformat(value)

    def add_content(self, content: Union[Content, List[Content]]):
        """Add content to the note.
        If the content is an Abstract one, a TypeError is raised.

        :param content: Content to add to the note.
        :return: Created content."""

        # Sentinel for checking if content type is valid
        if getattr(content, "__type__", "") == "Abstract":
            raise TypeError(
                f"Cannot create content from {content.__name__}, it is an abstract type."
            )

        # Add content, if list add all of them by running this function for each element to have the Abstract check
        if type(content) is list:
            for a in content:
                self.add_content(a)
        else:
            self.contents.append(content)

    def export(
        self,
        path: Union[Path, str],
        include_attached_files: bool = True,
        compress=False,
    ) -> Path:
        """Export note to given path.
        /!\\ API util only, not defined in the standard for now.

        :param path: Path to write the note
        :param include_attached_files: Copies all files related to contents in the created folder.
        :param compress: Export as .zip archive
        :return: Exported Note path
        """
        path = Path(path).resolve()  # Sentinel

        # Error if file path
        if path.is_file():
            raise ValueError("Writing path target must be a folder.")

        # Create folder
        if not path.is_dir():
            path.mkdir(parents=True)

        if path.suffix == ".orio":
            note_folder = path
            path = path.parent
        else:
            note_folder = path.joinpath(f"{self.date.replace(':', '_')}.orio")

        # XML
        # create the file structure

        # Note
        note = ET.Element(
            "note",
            {
                "date": self.date,
                "author": self.author,
                "parent": self.parent.date if self.parent else "",
            },
        )

        # Contents
        files_to_copy = []
        contents = ET.SubElement(note, "contents")
        for c in self.contents:
            # Dynamically set parameters from members
            params = {}
            for attribute, value in getmembers(c):
                if not attribute.startswith("__"):
                    if attribute == "path_to_image":
                        if include_attached_files:
                            # Set path_to_image as relative
                            relative_path = Path(value).name
                            params["path_to_image"] = str(relative_path)
                            # Keep files to copy
                            files_to_copy.append(
                                (Path(value), note_folder.joinpath(relative_path))
                            )
                    else:
                        params[attribute] = str(value)
            content = ET.Element(c.__class__.__name__, params)
            contents.append(content)

        # Set note metadata
        metadata = ET.SubElement(note, "metadata", self.metadata)

        #   Write to folder
        if not note_folder.is_dir():
            note_folder.mkdir()

        # Write to file
        # create a new XML file with the results

        xmlstr = minidom.parseString(ET.tostring(note, encoding="utf-8")).toprettyxml(
            indent="   "
        )
        file = note_folder.joinpath("note.orio")
        with file.open("w") as f:
            f.write(xmlstr)

        # Copy files if they have to be copied
        for source, target in files_to_copy:
            if not target.parent.is_dir():
                target.parent.mkdir()

            if not target.is_file():
                shutil.copy2(source, target)

        # Zip folder
        if compress:
            exported_file = shutil.make_archive(
                path.joinpath(self.date.replace(":", "_")), "zip", note_folder
            )
            # Delete source folder
            shutil.rmtree(note_folder)
            return Path(exported_file)

        return note_folder
