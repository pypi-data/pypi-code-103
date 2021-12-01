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

from dataclasses import dataclass
from datetime import datetime, timezone
from .base import ReviewItem
from pathlib import Path
import toml
from typing import List, Union

allowed_statuses: List[str] = toml.load(
    Path(__file__).parent.joinpath("orio_classes", "Status.toml")
).get("available")


@dataclass
class Status(ReviewItem):
    _date = None
    state: str
    author: str
    date: datetime = ""

    def __init__(self, state, author="", date: Union[str, datetime] = None):
        """Status of a review.

        :param state: Value of the status. Accepted statuses are defined by the ORIO version. TODO: Insert here a dynamic list of available ones
        :param author: Author of the note.
        :param date: Note's time of creation, provided as ISO UTC (datetime.now(timezone.utc).isoformat()).
        """
        super().__init__()

        # Check if status state is authorized by standard
        if state in allowed_statuses:
            self.state = state
        else:
            raise ValueError(
                f"Status '{state}' is not defined in the current version of OpenReviewIO standard."
                f"Available statuses are: {', '.join(allowed_statuses)}."
            )

        self.author = author

        if date:
            self.date = date
        else:
            self.date = datetime.now(timezone.utc).isoformat()

    @property
    def date(self):
        return self._date

    @date.setter
    def date(self, value):
        if isinstance(value, datetime):
            self._date = value
        else:
            self._date = datetime.fromisoformat(value)

    # TODO Override print for status to print: Status ... written by ... at ...
