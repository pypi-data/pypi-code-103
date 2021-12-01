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
from datetime import datetime
from .base import ReviewItem
import operator
from pathlib import Path
import shutil
import warnings
from typing import List, Union
from .Status import Status
from .Note import Note
from . import logging

import lxml.etree as ET
from inspect import getmembers, isroutine


@dataclass
class MediaReview(ReviewItem):

    _media = None
    media: Union[str, Path]
    _status = None
    status: Status = None
    notes: List[Note] = None
    metadata: dict = None
    _status_history = []  # Read only

    def __init__(
        self,
        media: Union[str, Path],
        status: Status = None,
        notes: List[Note] = None,
        metadata: dict = None,
    ):
        """Review of a media.

        :param media: Path to the media the review is linked to.
        :param status: Review status.
        :param notes: Review's notes ordered by creation date. TODO Read only ?
        :param metadata: Review's metadata.
        """
        super().__init__()

        self.media = media

        self.status = status or Status("waiting review", "default")

        self.notes = []
        if notes:
            self.add_note(notes)

        self.metadata = metadata or {}

    # Media getter and setter
    @property
    def media(self):
        return self._media

    @media.setter
    def media(self, value):
        self._media = Path(value)

    # Status getter and setter
    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, value):
        if type(value) is not Status:
            value = Status(value)
        self._status = value

    def add_note(self, note: Union[Note, List[Note]] = None):
        """Append a note (or all notes if a list is provided) it to the review's notes list.

        :param note: Note(s) to add."""

        if type(note) is list:
            for n in note:
                self.add_note(n)
        else:
            # Append note to notes if there is no note with the same date
            if note.date not in [n.date for n in self.notes]:
                self.notes.append(note)
            else:
                warnings.warn(
                    f"Note with date: {note.date} already exists, not overridden. Use get_note() to modify it.",
                    Warning,
                    stacklevel=2,
                )

        # Sort notes by date
        self.notes = sorted(self.notes, key=operator.attrgetter("date"))

    def import_note(self, note_path: Union[Path, str]) -> Note:
        """Import and add note from path of an exported note.

        :param note_path: Path to exported note
        :type note_path: Path
        :return: Imported note
        :rtype: Note
        """
        note_path = Path(note_path).resolve()  # sentinel

        if note_path.is_dir():  # If folder, don't change the path
            note_folder_root = note_path
        else:
            # If zip, uncompress
            if note_path.suffix == ".zip":
                # Unpack
                # temp_folder = tempfile.gettempdir().joinpath(f"{note_path.stem}.orio")
                temp_folder = note_path.parent.joinpath(f"{note_path.stem}.orio")
                shutil.unpack_archive(note_path, temp_folder)

                # Run import_note again to unpacked folder
                return self.import_note(temp_folder)

            else:  # If file, get parent folder
                note_folder_root = note_path.parent

        note_file = note_folder_root.joinpath("note.orio")

        # Build Note
        import xml.etree.ElementTree as ET

        note_xml = ET.parse(note_file).getroot()

        from . import _load_note_to_review

        return _load_note_to_review(note_folder_root, note_xml, self)

    def get_note(self, date: str) -> Note:
        """Get a note by it's date.

        :return: Note
        """
        if date:
            for n in self.notes:
                if n.date == datetime.fromisoformat(date):
                    return n

    def get_notes_list(self, from_date: datetime = None) -> List[Note]:
        """Get notes depending on some filtering parameters.

        :param from_date: Date to get notes from, defaults to None
        :return: List of filtered notes
        """
        notes_list = []

        # Return all if from_date is None
        if not from_date:
            return self.notes

        for note in self.notes:
            if note.date > from_date:
                notes_list.append(note)

        return notes_list

    def write(
        self, path: Union[str, Path] = "", include_attached_files: bool = True
    ) -> Path:
        """Write the review in a folder according to the folder structure.
        If no path provided, the note is written next to the related media file in a folder 'media_name.ext.orio'.

        :param path: Folder path to write the review.
        :param include_attached_files: Copies all files related to contents in the created folder.
        :return: Path to the folder of the exported media review.
        """
        # Create review
        path = Path(path).resolve()

        # Error if file path
        if path.is_file():
            raise ValueError("Writing path target must be a folder.")

        # Create folder
        if not path.is_dir():
            path.mkdir(parents=True)

        if path.suffix == ".orio":
            review_folder = path
        else:
            review_folder = path.joinpath(f"{self.media.name}.orio")

        # XML
        # create the file structure
        review = ET.Element(
            "review",
            {
                "media_path": str(self.media),
                "media_signature": "d41d8cd98f00b204e9800998ecf8427e",
            },
        )
        # Set review metadata
        # Sentinel casting for values to string
        metadata = ET.SubElement(
            review, "metadata", dict([[k, str(v)] for k, v in self.metadata.items()])
        )

        # Statuses
        # --------
        # History
        statuses = ET.SubElement(review, "statuses")
        for s in self.get_status_history():
            status = ET.Element(
                "status", {"date": s.date.isoformat(), "author": s.author}
            )
            status.text = s.state
            statuses.append(status)

        # Current
        status = ET.Element(
            "status",
            {"date": self.status.date.isoformat(), "author": self.status.author},
        )
        status.text = self.status.state
        statuses.append(status)

        # Notes
        notes = ET.SubElement(review, "notes")
        files_to_copy = []
        for n in self.notes:
            note = ET.Element(
                "note",
                {
                    "date": n.date.isoformat(),
                    "author": n.author,
                    "parent": n.parent.date.isoformat() if n.parent else "",
                },
            )

            # Contents
            contents = ET.SubElement(note, "contents")
            for c in n.contents:
                # Dynamically set parameters from members
                params = {}
                for attribute, value in getmembers(c, lambda a: not (isroutine(a))):
                    if not attribute.startswith("_"):
                        if (
                            value
                            and attribute in {"path_to_image", "reference_image"}
                            and include_attached_files
                        ):
                            # Special cases
                            image_path = value

                            # Set attribute's value as relative
                            relative_path = Path(
                                n.date.isoformat().replace(":", "_"),
                                Path(image_path).name,
                            )
                            params[attribute] = str(relative_path)
                            # Keep files to copy
                            new_attachment_path = review_folder.joinpath(relative_path)
                            files_to_copy.append(
                                (
                                    Path(image_path),
                                    new_attachment_path,
                                )
                            )
                            # Update attribute of written note
                            setattr(c, attribute, new_attachment_path)

                        else:
                            params[attribute] = str(value)

                # Test if body characters are accepted, else clean it
                try:
                    content = ET.Element(c.__class__.__name__, params)
                except ValueError:
                    import string

                    string_to_clean = params.get("body")
                    params["body"] = "".join(
                        [s for s in string_to_clean if s in string.printable]
                    )

                    content = ET.Element(c.__class__.__name__, params)

                contents.append(content)

            # Set note metadata
            # Sentinel casting for values to string
            metadata = ET.SubElement(
                note, "metadata", dict([[k, str(v)] for k, v in n.metadata.items()])
            )

            notes.append(note)

        #   Write to folder
        if not review_folder.is_dir():
            review_folder.mkdir()

        # Write to file
        # create a new XML file with the results
        xml = ET.ElementTree(review)

        file = review_folder.joinpath("review.orio")
        with file.open("wb") as f:
            xml.write(f, encoding="utf-8", xml_declaration=True, pretty_print=True)

        # Copy files if they have to be copied
        for source, target in files_to_copy:
            if not target.parent.is_dir():
                target.parent.mkdir()

            if not target.is_file():
                if source.is_file():  # Copy if file exists
                    shutil.copy2(source, target)
                else:  # Warn the user
                    logging.warning(f"Source file to copy doesn't exist: {source}")

        return review_folder

    def compare(self, review: MediaReview) -> MediaReview:
        """Compare the current review with the given one.
        TODO: Not implemented yet!

        :returns: A differential review with notes included in the current review that they aren't in the compared one.
        """
        pass

    def get_status_history(self) -> List[Status]:
        """Give the statuses history of the review.

        :returns: A list of statuses
        """
        return self._status_history

    def set_status_history(self, statuses_list):
        """Set the statuses history of the review."""
        self._status_history = statuses_list
