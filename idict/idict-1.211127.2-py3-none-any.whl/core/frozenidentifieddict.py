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
#
import operator
from functools import reduce
from operator import rshift as aop
from operator import xor as cop
from random import Random
from typing import TypeVar, Union, Callable

from garoupa import ø40, Hosh
from idict.config import GLOBAL
from idict.core.appearance import decolorize, idict2txt
from idict.core.identification import key2id, blobs_hashes_hoshes
from idict.parameter.ifunctionspace import iFunctionSpace, reduce3
from idict.parameter.ilet import iLet
from idict.persistence.cached import cached
from ldict.core.base import AbstractLazyDict, AbstractMutableLazyDict
from ldict.customjson import CustomJSONEncoder
from ldict.frozenlazydict import FrozenLazyDict

VT = TypeVar("VT")


class FrozenIdentifiedDict(AbstractLazyDict):
    """Immutable lazy universally identified dict for serializable (picklable) pairs str->value

    Usage:

    >>> idict = FrozenIdentifiedDict
    >>> idict().show(colored=False)
    {
        "_id": "0000000000000000000000000000000000000000",
        "_ids": {}
    }
    >>> d = idict(x=5, y=3)
    >>> d.show(colored=False)
    {
        "x": 5,
        "y": 3,
        "_id": "Gm_5a27861eacedc78bf5dc236c663f77f39933b",
        "_ids": {
            "x": "hi_7d6b4783509390c5384ac2c1b88fbd3d3cd8f (content: Mj_3bcd9aefb5020343384ae8ccb88fbd872cd8f)",
            "y": "o4_fcbb3f8a5c5a37c5cd8260aabdafb9b65d5ab (content: S5_331b7e710abd1443cd82d6b5cdafb9f04d5ab)"
        }
    }
    >>> d["y"]
    3
    >>> idict(y=88, x=123123).show(colored=False)
    {
        "y": 88,
        "x": 123123,
        "_id": "S-_6a05b897eed2728ea8200aa3f9e90651e952a",
        "_ids": {
            "y": "EV_f4049757e5085edc56b4262974be71951792a (content: 6X_ceb4a9cfad6b3b5a56b49c3484be71dff692a)",
            "x": "d5_fa01214009ca14a1527bd38a753b84cbc2cff (content: I6_bcc6fa41b424962f427be985853b8416b2cff)"
        }
    }
    >>> d = idict(x=123123, y=88)
    >>> d2 = d >> (lambda x: {"z": x**2})
    >>> d2.hosh == d2.identity * d2.ids["z"] * d2.ids["x"] * d2.ids["y"]
    True
    >>> e = d2 >> (lambda x,y: {"w": x/y})
    >>> e.show(colored=False)
    {
        "w": "→(x y)",
        "z": "→(x)",
        "x": 123123,
        "y": 88,
        "_id": "jWguT1MkE.y2lbZAetjGw2tmoFRZsuLzkF84sOwe",
        "_ids": {
            "w": "rl51vcB3tJbMS6y7RQHwJ1c51F.fTbFo4RK7M5M5",
            "z": "FI8-Sco6sGMjxpkIQ8-uTHfhAKZJBi6bgQpYHIM8",
            "x": "d5_fa01214009ca14a1527bd38a753b84cbc2cff (content: I6_bcc6fa41b424962f427be985853b8416b2cff)",
            "y": "EV_f4049757e5085edc56b4262974be71951792a (content: 6X_ceb4a9cfad6b3b5a56b49c3484be71dff692a)"
        }
    }
    >>> a = d >> (lambda x: {"z": x**2}) >> (lambda x, y: {"w": x/y})
    >>> b = d >> (lambda x, y: {"w": x/y}) >> (lambda x: {"z": x**2})
    >>> dic = d.asdict  # Converting to dict
    >>> dic
    {'x': 123123, 'y': 88, '_id': 'S-_6a05b897eed2728ea8200aa3f9e90651e952a', '_ids': {'x': 'd5_fa01214009ca14a1527bd38a753b84cbc2cff', 'y': 'EV_f4049757e5085edc56b4262974be71951792a'}}
    >>> d2 = idict(dic)  # Reconstructing from a dict
    >>> d2.show(colored=False)
    {
        "x": 123123,
        "y": 88,
        "_id": "S-_6a05b897eed2728ea8200aa3f9e90651e952a",
        "_ids": {
            "x": "d5_fa01214009ca14a1527bd38a753b84cbc2cff",
            "y": "EV_f4049757e5085edc56b4262974be71951792a"
        }
    }
    >>> d == d2
    True
    >>> from idict import Ø, setup
    >>> d = idict() >> {"x": "more content"}
    >>> d.show(colored=False)
    {
        "x": "more content",
        "_id": "aF_64eaced14bf0114a6b9eceaac31744c2093df",
        "_ids": {
            "x": "aF_64eaced14bf0114a6b9eceaac31744c2093df"
        }
    }
    >>> f = lambda x,y: {"z":x+y}
    >>> d = idict(x=5, y=7)
    >>> d2 = d >> f
    >>> d2.show(colored=False)
    {
        "z": "→(x y)",
        "x": 5,
        "y": 7,
        "_id": "GNYCBw8fGAYow5Ml4xadiKc3TxKm.mdn2sxVEnRv",
        "_ids": {
            "z": "pgVTwHntCH.mN6xVFQ0NIDD72QAm.mdn2sxVEnRv",
            "x": "hi_7d6b4783509390c5384ac2c1b88fbd3d3cd8f (content: Mj_3bcd9aefb5020343384ae8ccb88fbd872cd8f)",
            "y": "Bk_b75c77bb5e2640ad6428eb35f82a492dd8065 (content: 3m_131910d18a892d1b64285250092a4967c8065)"
        }
    }
    >>> c = {}
    >>> d3 = d2 >> [c]
    >>> d3.show(colored=False)
    {
        "z": "→(^ x y)",
        "x": 5,
        "y": 7,
        "_id": "GNYCBw8fGAYow5Ml4xadiKc3TxKm.mdn2sxVEnRv",
        "_ids": {
            "z": "pgVTwHntCH.mN6xVFQ0NIDD72QAm.mdn2sxVEnRv",
            "x": "hi_7d6b4783509390c5384ac2c1b88fbd3d3cd8f (content: Mj_3bcd9aefb5020343384ae8ccb88fbd872cd8f)",
            "y": "Bk_b75c77bb5e2640ad6428eb35f82a492dd8065 (content: 3m_131910d18a892d1b64285250092a4967c8065)"
        }
    }
    >>> c
    {}
    >>> d3.z
    12
    >>> c
    {'pgVTwHntCH.mN6xVFQ0NIDD72QAm.mdn2sxVEnRv': 12, 'hi_7d6b4783509390c5384ac2c1b88fbd3d3cd8f': 5, 'Bk_b75c77bb5e2640ad6428eb35f82a492dd8065': 7, 'GNYCBw8fGAYow5Ml4xadiKc3TxKm.mdn2sxVEnRv': {'_id': 'GNYCBw8fGAYow5Ml4xadiKc3TxKm.mdn2sxVEnRv', '_ids': {'z': 'pgVTwHntCH.mN6xVFQ0NIDD72QAm.mdn2sxVEnRv', 'x': 'hi_7d6b4783509390c5384ac2c1b88fbd3d3cd8f', 'y': 'Bk_b75c77bb5e2640ad6428eb35f82a492dd8065'}}}
    >>> d3.show(colored=False)
    {
        "z": 12,
        "x": 5,
        "y": 7,
        "_id": "GNYCBw8fGAYow5Ml4xadiKc3TxKm.mdn2sxVEnRv",
        "_ids": {
            "z": "pgVTwHntCH.mN6xVFQ0NIDD72QAm.mdn2sxVEnRv",
            "x": "hi_7d6b4783509390c5384ac2c1b88fbd3d3cd8f (content: Mj_3bcd9aefb5020343384ae8ccb88fbd872cd8f)",
            "y": "Bk_b75c77bb5e2640ad6428eb35f82a492dd8065 (content: 3m_131910d18a892d1b64285250092a4967c8065)"
        }
    }
    >>> c = {}
    >>> setup(cache=c)
    >>> d3 = d >> f ^ Ø
    >>> d3.show(colored=False)
    {
        "z": "→(^ x y)",
        "x": 5,
        "y": 7,
        "_id": "GNYCBw8fGAYow5Ml4xadiKc3TxKm.mdn2sxVEnRv",
        "_ids": {
            "z": "pgVTwHntCH.mN6xVFQ0NIDD72QAm.mdn2sxVEnRv",
            "x": "hi_7d6b4783509390c5384ac2c1b88fbd3d3cd8f (content: Mj_3bcd9aefb5020343384ae8ccb88fbd872cd8f)",
            "y": "Bk_b75c77bb5e2640ad6428eb35f82a492dd8065 (content: 3m_131910d18a892d1b64285250092a4967c8065)"
        }
    }
    >>> c
    {}
    >>> d3.z
    12
    >>> c
    {'pgVTwHntCH.mN6xVFQ0NIDD72QAm.mdn2sxVEnRv': 12, 'hi_7d6b4783509390c5384ac2c1b88fbd3d3cd8f': 5, 'Bk_b75c77bb5e2640ad6428eb35f82a492dd8065': 7, 'GNYCBw8fGAYow5Ml4xadiKc3TxKm.mdn2sxVEnRv': {'_id': 'GNYCBw8fGAYow5Ml4xadiKc3TxKm.mdn2sxVEnRv', '_ids': {'z': 'pgVTwHntCH.mN6xVFQ0NIDD72QAm.mdn2sxVEnRv', 'x': 'hi_7d6b4783509390c5384ac2c1b88fbd3d3cd8f', 'y': 'Bk_b75c77bb5e2640ad6428eb35f82a492dd8065'}}}
    >>> d3.show(colored=False)
    {
        "z": 12,
        "x": 5,
        "y": 7,
        "_id": "GNYCBw8fGAYow5Ml4xadiKc3TxKm.mdn2sxVEnRv",
        "_ids": {
            "z": "pgVTwHntCH.mN6xVFQ0NIDD72QAm.mdn2sxVEnRv",
            "x": "hi_7d6b4783509390c5384ac2c1b88fbd3d3cd8f (content: Mj_3bcd9aefb5020343384ae8ccb88fbd872cd8f)",
            "y": "Bk_b75c77bb5e2640ad6428eb35f82a492dd8065 (content: 3m_131910d18a892d1b64285250092a4967c8065)"
        }
    }
    """

    hosh: Hosh

    # noinspection PyMissingConstructor
    def __init__(self, /, _dictionary=None, _id=None, _ids=None, rnd=None, identity=ø40, _cloned=None, **kwargs):
        self.rnd = rnd
        self.identity = identity
        data = _dictionary or {}
        data.update(kwargs)

        # Freeze mutable *dicts.
        for k, v in data.items():
            if isinstance(v, AbstractMutableLazyDict):
                data[k] = v.frozen

        if _cloned:
            self.blobs = _cloned["blobs"]
            self.hashes = _cloned["hashes"]
            self.hoshes = _cloned["hoshes"]
            self.hosh = _cloned["hosh"]
        else:
            if "_id" in data:
                if _id:  # pragma: no cover
                    raise Exception(f"Conflicting 'id' values: {_id} and {data['_id']}")
                _id = data.pop("_id")
            if "_ids" in data:
                if _ids:  # pragma: no cover
                    raise Exception(f"Conflicting 'ids' values: {_ids} and {data['_ids']}")
                _ids = data.pop("_ids")

            if _id:
                if _ids is None:  # pragma: no cover
                    raise Exception(f"'id' {_id} given, but 'ids' is missing.")
                self.blobs = {}
                self.hashes = {}
                self.hoshes = {k: identity * v for k, v in _ids.items()}
            else:
                self.blobs, self.hashes, self.hoshes = blobs_hashes_hoshes(
                    data, identity, _ids or {}, self.identity.version
                ).values()
            self.hosh = reduce(operator.mul, [identity] + list(self.hoshes.values()))

        if _id is None:
            _id = self.hosh.id
            try:
                _ids = {k: v.id for k, v in self.hoshes.items()}
            except:  # pragma: no cover
                print(self.hoshes)
                raise Exception()

        # Store as an immutable lazy dict.
        self.frozen = FrozenLazyDict(data, _id=_id, _ids=_ids, rnd=rnd)
        self.data = self.frozen.data
        self.id = _id
        self.ids = _ids

    def __getitem__(self, item):
        return self.frozen[item]

    def __setitem__(self, key: str, value):
        self.frozen[key] = value

    def __delitem__(self, key):
        del self.frozen[key]

    def __getattr__(self, item):
        """
        >>> d = FrozenIdentifiedDict(x=5)
        >>> f = lambda x: {"y": x**x, "_history": ...}
        >>> f.metadata = {"name": "function f"}
        >>> (d >> f).history
        {0: {'name': 'function f'}}
        """
        try:
            return getattr(self.frozen, item)
        except (KeyError, AttributeError) as e:
            return getattr(self.frozen, "_" + item)

    def evaluate(self):
        """
        >>> from idict.core.frozenidentifieddict import FrozenIdentifiedDict as idict
        >>> f = lambda x: {"y": x+2}
        >>> d = idict(x=3)
        >>> a = d >> f
        >>> a.show(colored=False)
        {
            "y": "→(x)",
            "x": 3,
            "_id": "NfDlK1.4MFGwvI9SXFRBUlgdD0.xW4AU0sYuSnwe",
            "_ids": {
                "y": "r6qgPdf1kPTU.K8bw-R-e0PzHWZxW4AU0sYuSnwe",
                "x": "n4_51866e4dc164a1c5cd82c0babdafb9a65d5ab (content: S5_331b7e710abd1443cd82d6b5cdafb9f04d5ab)"
            }
        }
        >>> a.evaluate()
        >>> a.show(colored=False)
        {
            "y": 5,
            "x": 3,
            "_id": "NfDlK1.4MFGwvI9SXFRBUlgdD0.xW4AU0sYuSnwe",
            "_ids": {
                "y": "r6qgPdf1kPTU.K8bw-R-e0PzHWZxW4AU0sYuSnwe",
                "x": "n4_51866e4dc164a1c5cd82c0babdafb9a65d5ab (content: S5_331b7e710abd1443cd82d6b5cdafb9f04d5ab)"
            }
        }
        """
        self.frozen.evaluate()

    @property
    def asdict(self):
        """
        >>> from idict.core.frozenidentifieddict import FrozenIdentifiedDict as idict
        >>> d = idict(x=3, y=5)
        >>> d.id
        'Gm_969c1762a9edc78bf5dc236c663f77f39933b'
        >>> e = idict(x=7, y=8, d=d)
        >>> e.asdict
        {'x': 7, 'y': 8, 'd': {'x': 3, 'y': 5, '_id': 'Gm_969c1762a9edc78bf5dc236c663f77f39933b', '_ids': {'x': 'n4_51866e4dc164a1c5cd82c0babdafb9a65d5ab', 'y': 'ii_6ee7b815d7ae16c5384a72b1b88fbd4d3cd8f'}}, '_id': 'dc_ecfbc17842ca0e082a02528315f3aee08ff89', '_ids': {'x': 'Ak_4864e8a41a20ba9d64284c45f82a491dd8065', 'y': 'Ny_2c054fb898b960f9bf0d1fd7c59add74ecbf8', 'd': 'Tk_c466af3b9f5f550ef5dc0d51663f77a9a933b'}}
        >>> d.hosh ** key2id("d", d.identity.digits) == e.hoshes["d"]
        True
        """
        return self.frozen.asdict

    def clone(self, data=None, rnd=None, _cloned=None):
        cloned_internals = _cloned or dict(blobs=self.blobs, hashes=self.hashes, hoshes=self.hoshes, hosh=self.hosh)
        return FrozenIdentifiedDict(
            data or self.data, rnd=rnd or self.rnd, identity=self.identity, _cloned=cloned_internals
        )

    def __hash__(self):
        return hash(self.hosh)

    def show(self, colored=True, width=None):
        r"""
        >>> idict = FrozenIdentifiedDict
        >>> idict(x=134124, y= 56).show(colored=False)
        {
            "x": 134124,
            "y": 56,
            "_id": "tV_c3c37026dc9a795bb61f18be755b7a8a094f2",
            "_ids": {
                "x": "Ad_045ef613e3a78b8b54468cccd1fe32d9f4bae (content: 3f_cbb9283e13010e09544692d7e1fe3224e4bae)",
                "y": "UH_5e477903f808edcf52d8abe1a36c38b014944 (content: mJ_7beba502c36bca4d52d8120da36c38faf3944)"
            }
        }
        """
        CustomJSONEncoder.width = width
        return print(self.all if colored else decolorize(self.all))

    def __repr__(self, all=False):
        return idict2txt(self, all)

    __str__ = __repr__

    @property
    def all(self):
        r"""
        Usage:

        >>> from idict.core.frozenidentifieddict import FrozenIdentifiedDict as idict
        >>> from idict.core.appearance import decolorize
        >>> out = idict(x=134124, y= 56).all
        >>> decolorize(out)
        '{\n    "x": 134124,\n    "y": 56,\n    "_id": "tV_c3c37026dc9a795bb61f18be755b7a8a094f2",\n    "_ids": {\n        "x": "Ad_045ef613e3a78b8b54468cccd1fe32d9f4bae (content: 3f_cbb9283e13010e09544692d7e1fe3224e4bae)",\n        "y": "UH_5e477903f808edcf52d8abe1a36c38b014944 (content: mJ_7beba502c36bca4d52d8120da36c38faf3944)"\n    }\n}'
        """
        return self.__repr__(all=True)

    def __eq__(self, other):
        """
        >>> from idict import idict
        >>> idict(x=3) == {"x": 3}
        True
        >>> idict(x=3) == {"x": 3, "_id": idict(x=3).id}
        True
        >>> idict(x=3) == idict(x=3)
        True
        >>> idict(x=3) != {"x": 4}
        True
        >>> idict(x=3) != idict(x=4)
        True
        >>> idict(x=3) != {"y": 3}
        True
        >>> idict(x=3) != {"x": 3, "_id": (~idict(x=3).hosh).id}
        True
        >>> idict(x=3) != idict(y=3)
        True
        """
        if isinstance(other, dict):
            if "_id" in other:
                return self.id == other["_id"]
            if list(self.keys())[:-2] != list(other.keys()):
                return False
        from idict.core.idict_ import Idict

        if isinstance(other, (FrozenIdentifiedDict, Idict)):
            return self.hosh == other.hosh
        if isinstance(other, AbstractLazyDict):
            if self.keys() != other.keys():
                return False
            other.evaluate()
            return self.data == other.data
        if isinstance(other, dict):
            data = self.data.copy()
            del data["_id"]
            del data["_ids"]
            return data == other
        raise TypeError(f"Cannot compare {type(self)} and {type(other)}")  # pragma: no cover

    def __rrshift__(self, left: Union[Random, dict, Callable, iFunctionSpace]):
        if isinstance(left, dict) and not isinstance(left, AbstractLazyDict):
            return FrozenIdentifiedDict(left) >> self
        if isinstance(left, list) or callable(left):
            return iFunctionSpace(left, aop, self)
        if isinstance(left, Random):
            return self.clone(rnd=left)
        return NotImplemented

    def __rshift__(
        self, other: Union[dict, AbstractLazyDict, "FrozenIdentifiedDict", Callable, iLet, iFunctionSpace, Random]
    ):
        from idict.core.rshift import application, ihandle_dict
        from idict.core.idict_ import Idict

        if isinstance(other, (Idict, FrozenIdentifiedDict)):
            clone = self.clone(rnd=other.rnd) if other.rnd else self.clone()
            for k, v in other.data.items():
                if k not in ["_id", "_ids"]:
                    clone.data[k] = v
                    if k in other.blobs:
                        clone.blobs[k] = other.blobs[k]
                    if k in other.hashes:
                        clone.blobs[k] = other.hashes[k]
                    clone.hoshes[k] = other.hoshes[k]
            hosh = reduce(operator.mul, [self.identity] + [v for k, v in clone.hoshes.items() if not k.startswith("_")])
            internals = dict(blobs=clone.blobs, hashes=clone.hashes, hoshes=clone.hoshes, hosh=hosh)
            del clone.data["_id"]
            del clone.data["_ids"]
            return FrozenIdentifiedDict(clone.data, rnd=clone.rnd, _cloned=internals, **{k: v})
        if isinstance(other, dict):
            return ihandle_dict(self, other)
        if isinstance(other, Random):
            return self.clone(rnd=other)
        if isinstance(other, iLet):
            return application(self, other, other.f, other.bytes)
        if callable(other):
            return application(self, other, other, self.identity)
        if isinstance(other, list):
            d = self
            for cache in other:
                d = cached(d, cache)
            return d
        if isinstance(other, iFunctionSpace):
            return reduce3(lambda a, op, b: op(a, b), (self, aop) + other.functions)
        return NotImplemented

    def __rxor__(self, left: Union[Random, dict, Callable, iFunctionSpace]):
        if (isinstance(left, (dict, list, Random)) or callable(left)) and not isinstance(left, AbstractLazyDict):
            return iFunctionSpace(left, cop, self)
        return NotImplemented

    def __xor__(self, other: Union[dict, AbstractLazyDict, Callable, iLet, iFunctionSpace, Random]):
        if callable(other) or isinstance(other, (dict, Random, list, iLet)):
            return cached(self, GLOBAL["cache"]) >> other
        if isinstance(other, iFunctionSpace):
            return reduce3(lambda a, op, b: op(a, b), (self, cop) + other.functions)
        return NotImplemented
