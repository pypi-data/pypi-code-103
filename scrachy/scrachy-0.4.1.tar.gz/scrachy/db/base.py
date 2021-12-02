#  Copyright 2020 Reid Swanson.
#
#  This file is part of scrachy.
#
#  scrachy is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  scrachy is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser General Public License for more details.
#
#   You should have received a copy of the GNU Lesser General Public License
#   along with scrachy.  If not, see <https://www.gnu.org/licenses/>.

# Python Modules
import datetime
from typing import Any, Dict

# 3rd Party Modules
import sqlalchemy.orm

from sqlalchemy.ext.declarative import declarative_base

# Project Modules


class Base(object):
    # Modified from https://stackoverflow.com/a/55749579/4971706
    def __repr__(self) -> str:
        return self._repr()

    def _repr(self, max_text_len: int = 30, **fields: Dict[str, Any]) -> str:
        """
        Helper for __repr__
        """
        field_strings = []
        at_least_one_attached_attribute = False
        for key, field in fields.items():
            if isinstance(field, str):
                end = min(len(field), max_text_len)
                field = f"{field[:end]}{'...' if end < len(field) else ''}"

            if isinstance(field, (datetime.date, datetime.datetime)):
                field = str(field)

            if isinstance(field, bytes):
                field = field.hex()

            try:
                field_strings.append(f'{key}={field!r}')
            except sqlalchemy.orm.exc.DetachedInstanceError:
                field_strings.append(f'{key}=DetachedInstanceError')
            else:
                at_least_one_attached_attribute = True
        if at_least_one_attached_attribute:
            return f"<{self.__class__.__name__}({','.join(field_strings)})>"
        return f"<{self.__class__.__name__} {id(self)}>"


Base = declarative_base(cls=Base)
