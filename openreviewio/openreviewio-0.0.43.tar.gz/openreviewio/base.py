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
from dataclasses import asdict, dataclass


@dataclass
class ReviewItem:
    _type: str

    def __init__(self) -> None:
        self._type = str(self.__class__.__name__)

    def as_dict(self) -> dict:
        """Return current item as a dict.

        :return: Dict describing the item
        """
        return asdict(self)
