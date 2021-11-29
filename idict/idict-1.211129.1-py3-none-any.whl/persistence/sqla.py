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
from typing import TypeVar

from idict.data.compression import unpack, pack
from idict.persistence.cache import Cache
from idict.persistence.raw.sqladict import sqladict, check, Content

VT = TypeVar("VT")


class SQLA(Cache):  # pragma:  cover
    """Save to/retrieve from SQLAlchemy.

    Based on built-in module shelve. Open and close at every transaction.
    To keep open, please use shelve context manager itself.

    >>> d = SQLA("sqlite+pysqlite:////tmp/sqla-doctest.db")
    >>> d["x"] = 5
    >>> d["x"]
    5
    >>> for k,v in d.items():
    ...     print(k, v)
    x 5
    >>> "x" in d
    True
    >>> len(d)
    1
    >>> del d["x"]
    >>> "x" in d
    False
    >>> d
    SQLA→<class 'idict.persistence.raw.sqladict.SQLAdict'>
    """

    def __init__(
        self, url="sqlite+pysqlite:///:memory:", autopack=True, debug=False, nondeterministic_fallback_on_pack=True
    ):
        super().__init__(lambda: sqladict(url, debug))
        self.autopack = autopack
        self.nondeterministic_fallback_on_pack = nondeterministic_fallback_on_pack

    def __setitem__(self, key: str, value):
        check(key)
        if self.autopack:
            super().__setitem__(key, pack(value, nondeterministic_fallback=self.nondeterministic_fallback_on_pack))
        else:
            super().__setitem__(key, value)

    def __getitem__(self, key):
        check(key)
        ret = super().__getitem__(key)
        if self.autopack:
            return ret and unpack(ret)
        else:
            return ret and ret

    def __iter__(self):
        with self.decorator() as db:
            return (c.id for c in db.session.query(Content).all())

    def __len__(self):
        with self.decorator() as db:
            return db.session.query(Content).count()

    def copy(self):
        raise NotImplementedError


# TODO: passar comentários da lousa pras docs das classes
