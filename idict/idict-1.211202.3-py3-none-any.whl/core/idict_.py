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

from garoupa import ø40

import idict.core.frozenidentifieddict as fro
from idict.parameter.ifunctionspace import iFunctionSpace
from idict.parameter.ilet import iLet
from idict.persistence.cache import Cache
from ldict.core.appearance import decolorize
from ldict.core.base import AbstractMutableLazyDict, AbstractLazyDict
from ldict.exception import WrongKeyType

VT = TypeVar("VT")


# TODO: colorize show() for "_history": "split----------------------sklearn-1.0.1 fit--------------------------------idict predict----------------------------idict"
# TODO(minor): implement extend, to avoid excessive calculation when batch inserting values
class Idict(AbstractMutableLazyDict):
    """Mutable lazy identified dict for serializable (picklable) pairs str->value

    Usage:

    >>> from idict import idict
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
    >>> d = idict(x=123123, y=88)
    >>> d2 = d >> (lambda x: {"z": x**2})
    >>> d2.ids  # doctest:+ELLIPSIS
    {'z': '...', 'x': 'd5_fa01214009ca14a1527bd38a753b84cbc2cff', 'y': 'EV_f4049757e5085edc56b4262974be71951792a'}
    >>> d2.hosh == d2.identity * d2.ids["z"] * d2.ids["x"] * d2.ids["y"]
    True
    >>> e = d2 >> (lambda x,y: {"w": x/y})
    >>> e.show(colored=False)  # doctest:+ELLIPSIS
    {
        "w": "→(x y)",
        "z": "→(x)",
        "x": 123123,
        "y": 88,
        "_id": "...",
        "_ids": {
            "w": "...",
            "z": "...",
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
    >>> from idict import Ø
    >>> d = Ø >> {"x": "more content"}
    >>> d.show(colored=False)
    {
        "x": "more content",
        "_id": "aF_64eaced14bf0114a6b9eceaac31744c2093df",
        "_ids": {
            "x": "aF_64eaced14bf0114a6b9eceaac31744c2093df"
        }
    }
    >>> d = idict() >> {"x": "more content"}
    >>> d.show(colored=False)
    {
        "x": "more content",
        "_id": "aF_64eaced14bf0114a6b9eceaac31744c2093df",
        "_ids": {
            "x": "aF_64eaced14bf0114a6b9eceaac31744c2093df"
        }
    }
    >>> e.ids.keys()
    dict_keys(['w', 'z', 'x', 'y'])
    >>> del e["z"]
    >>> e.show(colored=False)  # doctest:+ELLIPSIS
    {
        "w": "→(x y)",
        "x": 123123,
        "y": 88,
        "_id": "...",
        "_ids": {
            "w": "...",
            "x": "d5_fa01214009ca14a1527bd38a753b84cbc2cff (content: I6_bcc6fa41b424962f427be985853b8416b2cff)",
            "y": "EV_f4049757e5085edc56b4262974be71951792a (content: 6X_ceb4a9cfad6b3b5a56b49c3484be71dff692a)"
        }
    }
    >>> e.hosh == e.identity * e.ids["w"] * e.ids["x"] * e.ids["y"]
    True
    >>> e["x"] = 77
    >>> e.show(colored=False)  # doctest:+ELLIPSIS
    {
        "w": "→(x y)",
        "x": 77,
        "y": 88,
        "_id": "...",
        "_ids": {
            "w": "...",
            "x": "zG_8a2e85e3b861ec7279f5f1c357969eb907ded (content: 2I_96abdb2113ef4fff69f518ce57969e04f6ded)",
            "y": "EV_f4049757e5085edc56b4262974be71951792a (content: 6X_ceb4a9cfad6b3b5a56b49c3484be71dff692a)"
        }
    }
    >>> f = lambda x,y: {"z":x+y}
    >>> d = idict(x=5, y=7)
    >>> d2 = d >> f
    >>> d2.show(colored=False)  # doctest:+ELLIPSIS
    {
        "z": "→(x y)",
        "x": 5,
        "y": 7,
        "_id": "...",
        "_ids": {
            "z": "...",
            "x": "hi_7d6b4783509390c5384ac2c1b88fbd3d3cd8f (content: Mj_3bcd9aefb5020343384ae8ccb88fbd872cd8f)",
            "y": "Bk_b75c77bb5e2640ad6428eb35f82a492dd8065 (content: 3m_131910d18a892d1b64285250092a4967c8065)"
        }
    }
    >>> c = {}
    >>> d3 = d2 >> [c]
    >>> d3.show(colored=False)  # doctest:+ELLIPSIS
    {
        "z": "→(↑ x y)",
        "x": 5,
        "y": 7,
        "_id": "...",
        "_ids": {
            "z": "...",
            "x": "hi_7d6b4783509390c5384ac2c1b88fbd3d3cd8f (content: Mj_3bcd9aefb5020343384ae8ccb88fbd872cd8f)",
            "y": "Bk_b75c77bb5e2640ad6428eb35f82a492dd8065 (content: 3m_131910d18a892d1b64285250092a4967c8065)"
        }
    }
    >>> c
    {}
    >>> d3.z
    12
    >>> c  # doctest:+ELLIPSIS
    {'...': 12, 'hi_7d6b4783509390c5384ac2c1b88fbd3d3cd8f': 5, 'Bk_b75c77bb5e2640ad6428eb35f82a492dd8065': 7, '...': {'_id': '...', '_ids': {'z': '...', 'x': 'hi_7d6b4783509390c5384ac2c1b88fbd3d3cd8f', 'y': 'Bk_b75c77bb5e2640ad6428eb35f82a492dd8065'}}}
    >>> d3.show(colored=False)  # doctest:+ELLIPSIS
    {
        "z": 12,
        "x": 5,
        "y": 7,
        "_id": "...",
        "_ids": {
            "z": "...",
            "x": "hi_7d6b4783509390c5384ac2c1b88fbd3d3cd8f (content: Mj_3bcd9aefb5020343384ae8ccb88fbd872cd8f)",
            "y": "Bk_b75c77bb5e2640ad6428eb35f82a492dd8065 (content: 3m_131910d18a892d1b64285250092a4967c8065)"
        }
    }
    >>> c = {}
    >>> from idict import setup
    >>> setup(cache=c)
    >>> d3 = d >> f ^ Ø
    >>> d3.show(colored=False)  # doctest:+ELLIPSIS
    {
        "z": "→(↑ x y)",
        "x": 5,
        "y": 7,
        "_id": "...",
        "_ids": {
            "z": "...",
            "x": "hi_7d6b4783509390c5384ac2c1b88fbd3d3cd8f (content: Mj_3bcd9aefb5020343384ae8ccb88fbd872cd8f)",
            "y": "Bk_b75c77bb5e2640ad6428eb35f82a492dd8065 (content: 3m_131910d18a892d1b64285250092a4967c8065)"
        }
    }
    >>> c
    {}
    >>> d3.z
    12
    >>> c  # doctest:+ELLIPSIS
    {'...': 12, 'hi_7d6b4783509390c5384ac2c1b88fbd3d3cd8f': 5, 'Bk_b75c77bb5e2640ad6428eb35f82a492dd8065': 7, '...': {'_id': '...', '_ids': {'z': '...', 'x': 'hi_7d6b4783509390c5384ac2c1b88fbd3d3cd8f', 'y': 'Bk_b75c77bb5e2640ad6428eb35f82a492dd8065'}}}
    >>> d3.show(colored=False)  # doctest:+ELLIPSIS
    {
        "z": 12,
        "x": 5,
        "y": 7,
        "_id": "...",
        "_ids": {
            "z": "...",
            "x": "hi_7d6b4783509390c5384ac2c1b88fbd3d3cd8f (content: Mj_3bcd9aefb5020343384ae8ccb88fbd872cd8f)",
            "y": "Bk_b75c77bb5e2640ad6428eb35f82a492dd8065 (content: 3m_131910d18a892d1b64285250092a4967c8065)"
        }
    }
    >>> f = lambda x: {"y": x ** 2, "_history": ...}
    >>> g = lambda x: {"y":x + 1000, "_history": ...}
    >>> f.metadata = {"id": "b5d6efbc9820dafe0d8fbe87a79adbe9797abc87", "name": "squared", "description": "Some text."}
    >>> g.metadata = {"id": "05d6efbc9820dafe0d8fbe87a79adbe9797abc87", "name": "add1000", "description": "Some text."}
    >>> d = idict(x=3) >> f >> g
    >>> d.show(colored=False)
    {
        "y": "→(x)",
        "_history": "b5d6efbc9820dafe0d8fbe87a79adbe9797abc87 05d6efbc9820dafe0d8fbe87a79adbe9797abc87",
        "x": 3,
        "_id": "FWBpAOEbVb-c8wa-jJbreKTOkZq1smsieeekmoge",
        "_ids": {
            "y": "SKKfkobjfpGEFAccrq89n50FxtdKtmsieaekmogf",
            "_history": "ofEb.nRSYsUsgAnnyp4KYFovZaUOV6000sv....-",
            "x": "n4_51866e4dc164a1c5cd82c0babdafb9a65d5ab (content: S5_331b7e710abd1443cd82d6b5cdafb9f04d5ab)"
        }
    }
    >>> (idict(x=3).hosh * "b5d6efbc9820dafe0d8fbe87a79adbe9797abc87" * "05d6efbc9820dafe0d8fbe87a79adbe9797abc87").show(colored=False)
    FWBpAOEbVb-c8wa-jJbreKTOkZq1smsieeekmoge
    >>> a = idict(x=3)
    >>> b = idict(y=5)
    >>> b["d"] = lambda y: a
    >>> cache = {}
    >>> b >>= [cache]
    >>> b.show(colored=False)  # doctest:+ELLIPSIS
    {
        "d": "→(↑ y)",
        "y": 5,
        "_id": "...",
        "_ids": {
            "d": "...",
            "y": "ii_6ee7b815d7ae16c5384a72b1b88fbd4d3cd8f (content: Mj_3bcd9aefb5020343384ae8ccb88fbd872cd8f)"
        }
    }
    >>> b.d.show(colored=False)
    {
        "x": 3,
        "_id": "n4_51866e4dc164a1c5cd82c0babdafb9a65d5ab",
        "_ids": {
            "x": "n4_51866e4dc164a1c5cd82c0babdafb9a65d5ab"
        }
    }
    >>> import json
    >>> print(json.dumps(cache, indent=2))  # doctest:+ELLIPSIS
    {
      "...": {
        "_id": "_4_51866e4dc164a1c5cd82c0babdafb9a65d5ab"
      },
      "n4_51866e4dc164a1c5cd82c0babdafb9a65d5ab": 3,
      "_4_51866e4dc164a1c5cd82c0babdafb9a65d5ab": {
        "_id": "n4_51866e4dc164a1c5cd82c0babdafb9a65d5ab",
        "_ids": {
          "x": "n4_51866e4dc164a1c5cd82c0babdafb9a65d5ab"
        }
      },
      "ii_6ee7b815d7ae16c5384a72b1b88fbd4d3cd8f": 5,
      "...": {
        "_id": "...",
        "_ids": {
          "d": "...",
          "y": "ii_6ee7b815d7ae16c5384a72b1b88fbd4d3cd8f"
        }
      }
    }
    >>> d = idict.fromid("n4_51866e4dc164a1c5cd82c0babdafb9a65d5ab", cache)
    >>> d.show(colored=False)
    {
        "x": "→(↑)",
        "_id": "n4_51866e4dc164a1c5cd82c0babdafb9a65d5ab",
        "_ids": {
            "x": "n4_51866e4dc164a1c5cd82c0babdafb9a65d5ab"
        }
    }
    >>> d.evaluated.show(colored=False)
    {
        "x": 3,
        "_id": "n4_51866e4dc164a1c5cd82c0babdafb9a65d5ab",
        "_ids": {
            "x": "n4_51866e4dc164a1c5cd82c0babdafb9a65d5ab"
        }
    }
    >>> idict.fromid(d.id, cache).evaluated.show(colored=False)
    {
        "x": 3,
        "_id": "n4_51866e4dc164a1c5cd82c0babdafb9a65d5ab",
        "_ids": {
            "x": "n4_51866e4dc164a1c5cd82c0babdafb9a65d5ab"
        }
    }
    >>> e = idict(f=lambda x: 5)
    >>> e.show(colored=False)  # doctest:+ELLIPSIS
    {
        "f": "<function <lambda> at 0x...>",
        "_id": "jvnzqh2e6TjL2fzatsuk0nNTAYYMFC6QA.xVsZcm",
        "_ids": {
            "f": "jvnzqh2e6TjL2fzatsuk0nNTAYYMFC6QA.xVsZcm"
        }
    }
    >>> from idict.core.appearance import idict2txt
    >>> d = idict(x=1,y=2)
    >>> decolorize(idict2txt(d, False, False))
    '{\\n    "x": 1,\\n    "y": 2,\\n    "_id": "mH_70118e827bbcd88303202a006d34eb63e4fbd",\\n    "_ids": "S6_787ce43265467bacea460e239d4b36762f272 wA_8d94995016666dd618d91cdccfe8a5fcb5c4b"\\n}'
    >>> decolorize(idict2txt(d, True, False))
    '{\\n    "x": 1,\\n    "y": 2,\\n    "_id": "mH_70118e827bbcd88303202a006d34eb63e4fbd",\\n    "_ids": {\\n        "x": "S6_787ce43265467bacea460e239d4b36762f272 (content: l8_09c7059156c4ed2aea46243e9d4b36c01f272)",\\n        "y": "wA_8d94995016666dd618d91cdccfe8a5fcb5c4b (content: -B_305c3d0e44c94a5418d982f7dfe8a537a5c4b)"\\n    }\\n}'
    >>> cache = {}
    >>> a = idict(x=5) >> (lambda x:{"y": x**x}) >> [[cache]]  # Cache within double brackets has strict/eager behavior.
    >>> a.show(colored=False)  # doctest:+ELLIPSIS
    {
        "y": 3125,
        "x": 5,
        "_id": "...",
        "_ids": {
            "y": "...",
            "x": "hi_7d6b4783509390c5384ac2c1b88fbd3d3cd8f (content: Mj_3bcd9aefb5020343384ae8ccb88fbd872cd8f)"
        }
    }
    >>> idict(a.id, cache).show(colored=False)  # doctest:+ELLIPSIS
    {
        "y": "→(↑)",
        "x": "→(↑)",
        "_id": "...",
        "_ids": {
            "y": "...",
            "x": "hi_7d6b4783509390c5384ac2c1b88fbd3d3cd8f (content: Mj_3bcd9aefb5020343384ae8ccb88fbd872cd8f)"
        }
    }
    """

    frozen: fro.FrozenIdentifiedDict

    # noinspection PyMissingConstructor
    def __init__(self, /, _dictionary=None, _id=None, _ids=None, rnd=None, identity=ø40, _cloned=None, **kwargs):
        from idict.core.frozenidentifieddict import FrozenIdentifiedDict

        self.identity = identity
        if isinstance(_dictionary, str) and isinstance(_id, (dict, Cache)):
            # Build idict from id+cache.
            if _ids or rnd or _cloned or kwargs:
                raise Exception("Cannot pass more arguments when first argument is id and second argument is cache.")
            # TODO (minor): detect identity from number of digits
            self.frozen = FrozenIdentifiedDict.fromid(_dictionary, _id, identity=identity)
        else:
            self.frozen = FrozenIdentifiedDict(_dictionary, _id, _ids, rnd, identity, _cloned, **kwargs)

    @property
    def id(self):
        return self.hosh.id

    @property
    def ids(self):
        return self.frozen.ids

    @property
    def hosh(self):
        return self.frozen.hosh

    @property
    def blobs(self):
        return self.frozen.blobs

    @property
    def hashes(self):
        return self.frozen.hashes

    @property
    def hoshes(self):
        return self.frozen.hoshes

    def __getattr__(self, item):
        if item in self.frozen:
            return self.frozen[item]
        _item = "_" + item
        if _item in self.frozen:
            return self.frozen[_item]
        return self.__getattribute__(item)

    def __delitem__(self, key):
        if not isinstance(key, str):
            raise WrongKeyType(f"Key must be string, not {type(key)}.", key)
        data, blobs, hashes, hoshes = self.data.copy(), self.blobs.copy(), self.hashes.copy(), self.hoshes.copy()
        del data[key]
        for coll in [blobs, hashes, hoshes]:
            if key in coll:
                del coll[key]
        hosh = reduce(operator.mul, [self.identity] + [v for k, v in hoshes.items() if not k.startswith("_")])
        self.frozen = self.frozen.clone(data, _cloned=dict(blobs=blobs, hashes=hashes, hoshes=hoshes, hosh=hosh))

    def clone(self, data=None, rnd=None, _cloned=None):
        return self.frozen.clone(data, rnd, _cloned).asmutable

    def show(self, colored=True, width=None):
        self.frozen.show(colored, width)

    def __rrshift__(self, left: Union[Random, dict, Callable, iFunctionSpace]):
        """
        >>> ({"x": 5} >> Idict(y=2)).show(colored=False)
        {
            "x": 5,
            "y": 2,
            "_id": "OS_ea00e0e366f9fd9c4024ee9e7878633af1ada",
            "_ids": {
                "x": "hi_7d6b4783509390c5384ac2c1b88fbd3d3cd8f (content: Mj_3bcd9aefb5020343384ae8ccb88fbd872cd8f)",
                "y": "wA_8d94995016666dd618d91cdccfe8a5fcb5c4b (content: -B_305c3d0e44c94a5418d982f7dfe8a537a5c4b)"
            }
        }
        >>> from ldict import ldict
        >>> (lambda x: {"y": 5*x}) >> ldict(y = 2)
        «λ × {
            "y": 2
        }»
        """
        if isinstance(left, list) or callable(left):
            return iFunctionSpace(left, aop, self)
        clone = self.__class__(identity=self.identity)
        clone.frozen = left >> self.frozen
        return clone

    def __rshift__(self, other: Union[list, dict, AbstractLazyDict, Callable, iLet, iFunctionSpace, Random]):
        """
        >>> d = Idict(x=2) >> (lambda x: {"y": 2 * x})
        >>> d.ids  # doctest:+ELLIPSIS
        {'y': '...', 'x': 'vA_88beb4e68c50d7d618d97ceccfe8a5ecb5c4b'}
        """
        clone = self.__class__(identity=self.identity)
        clone.frozen = self.frozen >> other
        return clone

    def __rxor__(self, left: Union[Random, dict, Callable, iFunctionSpace]):
        if isinstance(left, list) or callable(left):
            return iFunctionSpace(left, cop, self)
        clone = self.__class__(identity=self.identity)
        clone.frozen = left ^ self.frozen
        return clone

    def __xor__(self, other: Union[dict, AbstractLazyDict, Callable, iLet, iFunctionSpace, Random]):
        clone = self.__class__(identity=self.identity)
        clone.frozen = self.frozen ^ other
        return clone

    @property
    def all(self):
        return self.frozen.all

    @staticmethod
    def fromid(id, cache, identity=ø40):
        from idict.core.frozenidentifieddict import FrozenIdentifiedDict

        return FrozenIdentifiedDict.fromid(id, cache, identity).asmutable

    @staticmethod
    def fromfile(name, output=["df"], output_format="df", include_name=False, identity=ø40):
        from idict.core.frozenidentifieddict import FrozenIdentifiedDict

        return FrozenIdentifiedDict.fromfile(name, output, output_format, include_name, identity).asmutable

    @staticmethod
    def fromtoy(output=["X", "y"], output_format="Xy", identity=ø40):
        from idict.core.frozenidentifieddict import FrozenIdentifiedDict

        return FrozenIdentifiedDict.fromtoy(output, output_format, identity).asmutable

    @staticmethod
    def fromminiarff(output=["df"], output_format="df", identity=ø40):
        from idict.core.frozenidentifieddict import FrozenIdentifiedDict

        return FrozenIdentifiedDict.fromminiarff(output, output_format, identity).asmutable

    @staticmethod
    def fromminicsv(output=["df"], output_format="df", identity=ø40):
        from idict.core.frozenidentifieddict import FrozenIdentifiedDict

        return FrozenIdentifiedDict.fromminicsv(output, output_format, identity).asmutable

    @staticmethod
    def fromopenml(name, version=1, Xout="X", yout="y", identity=ø40):
        from idict.core.frozenidentifieddict import FrozenIdentifiedDict

        return FrozenIdentifiedDict.fromopenml(name, version, Xout, yout, identity).asmutable

    @property
    def metafields(self):
        """
        >>> from idict import idict
        >>> idict(a=1, _b=2, _c=3).metafields
        {'_b': 2, '_c': 3}
        """
        return self.frozen.metafields

    @property
    def trimmed(self):
        """
        >>> from idict import idict
        >>> idict(a=1, _b=2, _history=[1,2,3]).trimmed.show(colored=False)
        {
            "a": 1,
            "_id": "v6_3ac82db5497101bcea46bd139d4b36862f272",
            "_ids": {
                "a": "v6_3ac82db5497101bcea46bd139d4b36862f272"
            }
        }
        """
        return self.frozen.trimmed.asmutable

    # def wrapped(self, version, version_id):
    #     """
    #     Wrap a trimmed version of an idict object by a metafield container
    #
    #     The container is identified by `object.id * extra_field__id`.
    #
    #     >>> from idict import idict
    #     >>> d = idict(x=3, _metafield_1=5, _history={"id-of-some-previous-step----------------": 5})
    #     >>> d.show(colored=False)
    #     {
    #         "x": 3,
    #         "_metafield_1": 5,
    #         "_history": "id-of-some-previous-step----------------",
    #         "_id": "n4_51866e4dc164a1c5cd82c0babdafb9a65d5ab",
    #         "_ids": {
    #             "x": "n4_51866e4dc164a1c5cd82c0babdafb9a65d5ab",
    #             "_metafield_1": "KG_c33bb4404f27e9a7878b29dcb88fbd772cd8f (content: Mj_3bcd9aefb5020343384ae8ccb88fbd872cd8f)",
    #             "_history": "T4_254b4402e8d23be907236a140ff90245285a8 (content: VO_b2b5c7d8ff9718670723c03f0ff9028f085a8)"
    #         }
    #     }
    #     >>> e = d.wrapped("user 1", "uuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuu")
    #     >>> e.show(colored=False)
    #     {
    #         "fields": {
    #             "x": 3,
    #             "_id": "n4_51866e4dc164a1c5cd82c0babdafb9a65d5ab",
    #             "_ids": {
    #                 "x": "n4_51866e4dc164a1c5cd82c0babdafb9a65d5ab"
    #             }
    #         },
    #         "version": "user 1",
    #         "_metafield_1": 5,
    #         "_history": "id-of-some-previous-step----------------",
    #         "_id": "g.0pzcYOgFTneQ8ojVDcReKkaqDuuuuuuuuuuuuu",
    #         "_ids": {
    #             "fields": "n4_51866e4dc164a1c5cd82c0babdafb9a65d5ab",
    #             "version": "uuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuu",
    #             "_metafield_1": "KG_c33bb4404f27e9a7878b29dcb88fbd772cd8f",
    #             "_history": "T4_254b4402e8d23be907236a140ff90245285a8"
    #         }
    #     }
    #     >>> d.hosh == e.fields.hosh
    #     True
    #     """
    #     return self.frozen.wrapped(version, version_id).asmutable
