#  Copyright (c) 2021. Davi Pereira dos Santos
#  This file is part of the idict project.
#  Please respect the license - more about this in the section (*) below.
#
#  idict is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  idict is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with idict.  If not, see <http://www.gnu.org/licenses/>.
#
#  (*) Removing authorship by any means, e.g. by distribution of derived
#  works or verbatim, obfuscated, compiled or rewritten versions of any
#  part of this work is illegal and unethical regarding the effort and
#  time spent here.
from contextlib import contextmanager
from typing import Dict, TypeVar

from sqlalchemy import Column, String, BLOB, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session

VT = TypeVar("VT")
Base = declarative_base()


class Content(Base):
    __tablename__ = "content"
    id = Column(String(40), primary_key=True)
    blob = Column(BLOB)


def check(key):
    if not isinstance(key, str):
        raise WrongKeyType(f"Key must be string, not {type(key)}.", key)


@contextmanager
def sqladict(url="sqlite+pysqlite:///:memory:", debug=False):
    engine = create_engine(url, echo=debug)
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        yield SQLAdict(session)


class SQLAdict(Dict[str, VT]):
    """
    Dict-like persistence based on SQLAlchemy

    40-digit keys only

    Usage:

    >>> with sqladict("sqlite+pysqlite:////tmp/sqla-doctest.db") as db:
    ...     "x" in db
    ...     db
    False
    {}
    >>> with sqladict("sqlite+pysqlite:////tmp/sqla-doctest.db") as db:
    ...     db["x"] = b"asd"
    ...     db
    {'x': b'asd'}
    >>> with sqladict("sqlite+pysqlite:////tmp/sqla-doctest.db") as db:
    ...     "x" in db
    True
    >>> with sqladict("sqlite+pysqlite:////tmp/sqla-doctest.db") as db:
    ...     db.x == b"asd"
    True
    >>> with sqladict("sqlite+pysqlite:////tmp/sqla-doctest.db") as db:
    ...     del db["x"]
    ...     "x" in db
    False
    """

    def __init__(self, session):
        super().__init__()
        self.session = session

    def __contains__(self, key):
        check(key)
        return self.session.query(Content).filter_by(id=key).first() is not None

    def __iter__(self):
        return (c.id for c in self.session.query(Content).all())

    def __setitem__(self, key: str, value):
        check(key)
        content = Content(id=key, blob=value)
        self.session.add(content)
        self.session.commit()

    def __getitem__(self, key):
        check(key)
        ret = self.session.query(Content).get(key)
        return ret and ret.blob

    def __delitem__(self, key):
        check(key)
        content = self.session.query(Content).get(key)
        self.session.delete(content)
        self.session.commit()

    def __getattr__(self, key):
        check(key)
        if key in self:
            return self[key]
        return self.__getattribute__(key)

    def __str__(self):
        return str(self.asdict)

    __repr__ = __str__

    @property
    def asdict(self):
        return {k: self[k] for k in self}


class WrongKeyType(Exception):
    pass
