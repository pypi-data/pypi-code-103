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
from idict.parameter.ifunctionspace import iFunctionSpace
from idict.parameter.ilet import iLet
from idict.persistence.cached import build, get_following_pointers
from ldict.core.base import AbstractMutableLazyDict, AbstractLazyDict
from ldict.exception import WrongKeyType

VT = TypeVar("VT")


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
    >>> d2.ids
    {'z': 'FI8-Sco6sGMjxpkIQ8-uTHfhAKZJBi6bgQpYHIM8', 'x': 'd5_fa01214009ca14a1527bd38a753b84cbc2cff', 'y': 'EV_f4049757e5085edc56b4262974be71951792a'}
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
    >>> e.show(colored=False)
    {
        "w": "→(x y)",
        "x": 123123,
        "y": 88,
        "_id": "BAcWIBldD8aIp06GjLRUt.BeHm.fTbFo4RK7M5M5",
        "_ids": {
            "w": "rl51vcB3tJbMS6y7RQHwJ1c51F.fTbFo4RK7M5M5",
            "x": "d5_fa01214009ca14a1527bd38a753b84cbc2cff (content: I6_bcc6fa41b424962f427be985853b8416b2cff)",
            "y": "EV_f4049757e5085edc56b4262974be71951792a (content: 6X_ceb4a9cfad6b3b5a56b49c3484be71dff692a)"
        }
    }
    >>> e.hosh == e.identity * e.ids["w"] * e.ids["x"] * e.ids["y"]
    True
    >>> e["x"] = 77
    >>> e.show(colored=False)
    {
        "w": "→(x y)",
        "x": 77,
        "y": 88,
        "_id": "f9O-wbkUFPQTHrtyM71xqkWa9IUfTbFo4RK7M5M5",
        "_ids": {
            "w": "rl51vcB3tJbMS6y7RQHwJ1c51F.fTbFo4RK7M5M5",
            "x": "zG_8a2e85e3b861ec7279f5f1c357969eb907ded (content: 2I_96abdb2113ef4fff69f518ce57969e04f6ded)",
            "y": "EV_f4049757e5085edc56b4262974be71951792a (content: 6X_ceb4a9cfad6b3b5a56b49c3484be71dff692a)"
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
    >>> from idict import setup
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
    >>> f = lambda x: {"y": x ** 2, "_history": ...}
    >>> g = lambda x: {"y":x + 1000, "_history": ...}
    >>> f.metadata = {"id": "b5d6efbc9820dafe0d8fbe87a79adbe9797abc87", "name": "squared", "description": "Some text."}
    >>> g.metadata = {"id": "05d6efbc9820dafe0d8fbe87a79adbe9797abc87", "name": "add1000", "description": "Some text."}
    >>> d = idict(x=3) >> f >> g
    >>> d.show(colored=False)
    {
        "y": "→(x)",
        "_history": {
            "b5d6efbc9820dafe0d8fbe87a79adbe9797abc87": {
                "name": "squared",
                "description": "Some text."
            },
            "05d6efbc9820dafe0d8fbe87a79adbe9797abc87": {
                "name": "add1000",
                "description": "Some text."
            }
        },
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
    >>> b.show(colored=False)
    {
        "d": "→(^ y)",
        "y": 5,
        "_id": "zPIOd8YS56A4GjVdQMtk5op1MMAZJVxChr1XgFng",
        "_ids": {
            "d": "7VPk71Y8BJeY-V67FeutM8Zt0cwZJVxChr1XgFng",
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
    >>> print(json.dumps(cache, indent=2))
    {
      "7VPk71Y8BJeY-V67FeutM8Zt0cwZJVxChr1XgFng": {
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
      "zPIOd8YS56A4GjVdQMtk5op1MMAZJVxChr1XgFng": {
        "_id": "zPIOd8YS56A4GjVdQMtk5op1MMAZJVxChr1XgFng",
        "_ids": {
          "d": "7VPk71Y8BJeY-V67FeutM8Zt0cwZJVxChr1XgFng",
          "y": "ii_6ee7b815d7ae16c5384a72b1b88fbd4d3cd8f"
        }
      }
    }
    >>> idict.fromid("n4_51866e4dc164a1c5cd82c0babdafb9a65d5ab", cache).show(colored=False)
    {
        "x": 3,
        "_id": "n4_51866e4dc164a1c5cd82c0babdafb9a65d5ab",
        "_ids": {
            "x": "n4_51866e4dc164a1c5cd82c0babdafb9a65d5ab"
        }
    }
    >>> idict.fromid("7VPk71Y8BJeY-V67FeutM8Zt0cwZJVxChr1XgFng", cache).show(colored=False)
    {
        "x": 3,
        "_id": "n4_51866e4dc164a1c5cd82c0babdafb9a65d5ab",
        "_ids": {
            "x": "n4_51866e4dc164a1c5cd82c0babdafb9a65d5ab"
        }
    }
    >>> idict(f=lambda x: 5).show(colored=False)  # doctest:+ELLIPSIS
    {
        "f": "<function <lambda> at 0x...>",
        "_id": "NhULktUPKQW0kiK9Gen3yzxunKQ4yXDl70-yAzi4",
        "_ids": {
            "f": "NhULktUPKQW0kiK9Gen3yzxunKQ4yXDl70-yAzi4"
        }
    }
    """

    # noinspection PyMissingConstructor
    def __init__(self, /, _dictionary=None, _id=None, _ids=None, rnd=None, identity=ø40, _cloned=None, **kwargs):
        self.identity = identity
        from idict.core.frozenidentifieddict import FrozenIdentifiedDict

        self.frozen: FrozenIdentifiedDict = FrozenIdentifiedDict(
            _dictionary, _id, _ids, rnd, identity, _cloned, **kwargs
        )

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
        try:
            return getattr(self.frozen, item)
        except (KeyError, AttributeError) as e:
            return getattr(self.frozen, "_" + item)

    def __delitem__(self, key):
        if not isinstance(key, str):
            raise WrongKeyType(f"Key must be string, not {type(key)}.", key)
        data, blobs, hashes, hoshes = self.data.copy(), self.blobs.copy(), self.hashes.copy(), self.hoshes.copy()
        del data[key]
        for coll in [blobs, hashes, hoshes]:
            if key in coll:
                del coll[key]
        hosh = reduce(operator.mul, [self.identity] + list(hoshes.values()))
        self.frozen = self.frozen.clone(data, _cloned=dict(blobs=blobs, hashes=hashes, hoshes=hoshes, hosh=hosh))

    def clone(self, data=None, rnd=None, _cloned=None):
        cloned_internals = _cloned or dict(blobs=self.blobs, hashes=self.hashes, hoshes=self.hoshes, hosh=self.hosh)
        return self.__class__(data or self.data, rnd=rnd or self.rnd, identity=self.identity, _cloned=cloned_internals)

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
                "y": "wA_8d94995016666dd618d91cdccfe8a5fcb5c4b"
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

    def __rshift__(self, other: Union[dict, AbstractLazyDict, Callable, iLet, iFunctionSpace, Random]):
        """
        >>> d = Idict(x=2) >> (lambda x: {"y": 2 * x})
        >>> d.ids
        {'y': 'OujWZCkpmqiUcA1K9LZZDO2jzijWqcXxhrGWdepm', 'x': 'vA_88beb4e68c50d7d618d97ceccfe8a5ecb5c4b'}
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

    @staticmethod
    def fromid(id, cache, identity=ø40):
        """
        >>> from idict import idict
        >>> cache = {}
        >>> d = idict(x=5) >> (lambda x: {"y": x**2}) >> [cache]
        >>> d.show(colored=False)
        {
            "y": "→(^ x)",
            "x": 5,
            "_id": "himLChDa.3GCFEBwkoJXPo3dD18LRgUAfdP7HEp4",
            "_ids": {
                "y": ".WVCvSxA2auspgV5aSJ444DF7tjLRgUAfdP7HEp4",
                "x": "hi_7d6b4783509390c5384ac2c1b88fbd3d3cd8f (content: Mj_3bcd9aefb5020343384ae8ccb88fbd872cd8f)"
            }
        }
        >>> d.y
        25
        >>> cache
        {'.WVCvSxA2auspgV5aSJ444DF7tjLRgUAfdP7HEp4': 25, 'hi_7d6b4783509390c5384ac2c1b88fbd3d3cd8f': 5, 'himLChDa.3GCFEBwkoJXPo3dD18LRgUAfdP7HEp4': {'_id': 'himLChDa.3GCFEBwkoJXPo3dD18LRgUAfdP7HEp4', '_ids': {'y': '.WVCvSxA2auspgV5aSJ444DF7tjLRgUAfdP7HEp4', 'x': 'hi_7d6b4783509390c5384ac2c1b88fbd3d3cd8f'}}}
        >>> d2 = idict.fromid(d.id, cache)
        >>> d2.show(colored=False)
        {
            "y": 25,
            "x": 5,
            "_id": "himLChDa.3GCFEBwkoJXPo3dD18LRgUAfdP7HEp4",
            "_ids": {
                "y": ".WVCvSxA2auspgV5aSJ444DF7tjLRgUAfdP7HEp4",
                "x": "hi_7d6b4783509390c5384ac2c1b88fbd3d3cd8f"
            }
        }
        >>> d == d2
        True
        """
        if (newid := "_" + id[1:]) in cache:
            id = newid
        d = get_following_pointers(id, cache)
        return build(d["_id"], d["_ids"], cache, identity)

    @staticmethod
    def fromfile(name, field="df", output_format="df"):
        """Input format is defined by file extension: .arff, .csv, TODO: .json, .pickle5
        >>> from testfixtures import TempDirectory
        >>> with TempDirectory() as tmp:  # doctest:+ELLIPSIS
        ...     tmp.write("mini.arff", b"@RELATION mini\\n@ATTRIBUTE attr1	REAL\\n@ATTRIBUTE attr2 	REAL\\n@ATTRIBUTE class 	{0,1}\\n@DATA\\n5.1,3.5,0\\n3.1,4.5,1")
        ...     d = Idict.fromfile(tmp.path + "/mini.arff")
        '/tmp/.../mini.arff'
        >>> d.show(colored=False)
        {
            "df": "«{'attr1@REAL': {0: 5.1, 1: 3.1}, 'attr2@REAL': {0: 3.5, 1: 4.5}, 'class@{0,1}': {0: '0', 1: '1'}}»",
            "_id": "ja_3dbc3e0089a672ae7896199398b692362dc99",
            "_ids": {
                "df": "ja_3dbc3e0089a672ae7896199398b692362dc99"
            }
        }
        >>> d.df.head()
           attr1@REAL  attr2@REAL class@{0,1}
        0         5.1         3.5           0
        1         3.1         4.5           1
        >>> with TempDirectory() as tmp:  # doctest:+ELLIPSIS
        ...     tmp.write("mini.csv", b"attr1,attr2,class\\n5.1,3.5,0\\n3.1,4.5,1")
        ...     d = Idict.fromfile(tmp.path + "/mini.csv")
        '/tmp/.../mini.csv'
        >>> d.show(colored=False)
        {
            "df": "«{'attr1': {0: 5.1, 1: 3.1}, 'attr2': {0: 3.5, 1: 4.5}, 'class': {0: 0, 1: 1}}»",
            "_id": "qp_bb3a13c2e3a533a65f558986b46de028f431c",
            "_ids": {
                "df": "qp_bb3a13c2e3a533a65f558986b46de028f431c"
            }
        }
        >>> d.df.head()
           attr1  attr2  class
        0    5.1    3.5      0
        1    3.1    4.5      1
        """
        if output_format == "df":
            if name.endswith(".arff"):
                from arff2pandas import a2p

                with open(name) as f:
                    df = a2p.load(f)
                return Idict({field: df})
            if name.endswith(".csv"):
                from pandas import read_csv

                return Idict({field: read_csv(name)})
        else:  # pragma: no cover
            raise Exception(f"Unknown {output_format=}.")
