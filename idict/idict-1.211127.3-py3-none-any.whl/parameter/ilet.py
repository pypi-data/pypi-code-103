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
from functools import cached_property
from json import dumps
from operator import rshift as aop
from operator import xor as cop
from random import Random
from typing import Union, Callable

from ldict.core.base import AbstractLazyDict
from ldict.customjson import CustomJSONEncoder
from ldict.parameter.abslet import AbstractLet


class iLet(AbstractLet):
    """
    Set values or sampling intervals for parameterized functions

    >>> from idict import idict, let
    >>> f = lambda x,y, a=[-1,-0.9,-0.8,...,1]: {"z": a*x + y}
    >>> f_a = let(f, a=0)
    >>> f_a
    λ{'a': 0}
    >>> d = idict(x=5,y=7)
    >>> d2 = d >> f_a
    >>> d2.show(colored=False)
    {
        "z": "→(a x y)",
        "x": 5,
        "y": 7,
        "_id": "jrbP9TOUI2Fu.Cj56WZtFZ-uR-aIf7PP0vTUHwdO",
        "_ids": {
            "z": "KjFKlsh7jqDr22rlIdQ1ENpz0hhIf7PP0vTUHwdO",
            "x": "hi_7d6b4783509390c5384ac2c1b88fbd3d3cd8f (content: Mj_3bcd9aefb5020343384ae8ccb88fbd872cd8f)",
            "y": "Bk_b75c77bb5e2640ad6428eb35f82a492dd8065 (content: 3m_131910d18a892d1b64285250092a4967c8065)"
        }
    }
    >>> d2.evaluate()
    >>> d2.show(colored=False)
    {
        "z": 7,
        "x": 5,
        "y": 7,
        "_id": "jrbP9TOUI2Fu.Cj56WZtFZ-uR-aIf7PP0vTUHwdO",
        "_ids": {
            "z": "KjFKlsh7jqDr22rlIdQ1ENpz0hhIf7PP0vTUHwdO",
            "x": "hi_7d6b4783509390c5384ac2c1b88fbd3d3cd8f (content: Mj_3bcd9aefb5020343384ae8ccb88fbd872cd8f)",
            "y": "Bk_b75c77bb5e2640ad6428eb35f82a492dd8065 (content: 3m_131910d18a892d1b64285250092a4967c8065)"
        }
    }
    >>> from random import Random
    >>> d2 = d >> Random(0) >> let(f, a=[8,9])
    >>> d2.show(colored=False)
    {
        "z": "→(a x y)",
        "x": 5,
        "y": 7,
        "_id": "BNML4tU7pW1RdptZLNisRSXAlRnMrJxAMFjv1ppr",
        "_ids": {
            "z": "Z5X.KORnk-EfmNAdm590QGmFw7uMrJxAMFjv1ppr",
            "x": "hi_7d6b4783509390c5384ac2c1b88fbd3d3cd8f (content: Mj_3bcd9aefb5020343384ae8ccb88fbd872cd8f)",
            "y": "Bk_b75c77bb5e2640ad6428eb35f82a492dd8065 (content: 3m_131910d18a892d1b64285250092a4967c8065)"
        }
    }
    >>> d2.evaluate()
    >>> d2.show(colored=False)
    {
        "z": 52,
        "x": 5,
        "y": 7,
        "_id": "BNML4tU7pW1RdptZLNisRSXAlRnMrJxAMFjv1ppr",
        "_ids": {
            "z": "Z5X.KORnk-EfmNAdm590QGmFw7uMrJxAMFjv1ppr",
            "x": "hi_7d6b4783509390c5384ac2c1b88fbd3d3cd8f (content: Mj_3bcd9aefb5020343384ae8ccb88fbd872cd8f)",
            "y": "Bk_b75c77bb5e2640ad6428eb35f82a492dd8065 (content: 3m_131910d18a892d1b64285250092a4967c8065)"
        }
    }
    >>> let(f, a=5) >> {"x": 5, "y": 7}
    «λ{'a': 5} × {'x': 5, 'y': 7}»
    >>> (idict({"x": 5, "y": 7}) >> let(f, a=5)).show(colored=False)
    {
        "z": "→(a x y)",
        "x": 5,
        "y": 7,
        "_id": "PeaN8nAdYZWPpGB6unSYsRONBbPCMKqODpuKHpoM",
        "_ids": {
            "z": "skJZ-.de47J3SFmG3HIwTKdSMtFCMKqODpuKHpoM",
            "x": "hi_7d6b4783509390c5384ac2c1b88fbd3d3cd8f (content: Mj_3bcd9aefb5020343384ae8ccb88fbd872cd8f)",
            "y": "Bk_b75c77bb5e2640ad6428eb35f82a492dd8065 (content: 3m_131910d18a892d1b64285250092a4967c8065)"
        }
    }
    >>> from idict.core.appearance import decolorize
    >>> print(decolorize(str(let(f, a=5) >> idict({"x": 5, "y": 7}))))
    «λ{'a': 5} × {
        "x": 5,
        "y": 7,
        "_id": "TC_15c7ce3faeb9d063ac62bef6a1b9076a15ee4",
        "_ids": "hi_7d6b4783509390c5384ac2c1b88fbd3d3cd8f Bk_b75c77bb5e2640ad6428eb35f82a492dd8065"
    }»
    >>> let(f, a=5) >> ["mycache"]
    «λ{'a': 5} × ^»
    >>> from idict.parameter.ifunctionspace import iFunctionSpace
    >>> let(f, a=5) >> iFunctionSpace()
    «λ{'a': 5}»
    >>> iFunctionSpace() >> let(f, a=5)
    «λ{'a': 5}»
    >>> (lambda x: {"z": x*8}) >> let(f, a=5)
    «λ × λ{'a': 5}»
    >>> d = {"x":3, "y": 8} >> let(f, a=5)
    >>> d.show(colored=False)
    {
        "z": "→(a x y)",
        "x": 3,
        "y": 8,
        "_id": "XIlmFY.9CnG-cahneqWtFfHk2MNCMKqODpuKHpoM",
        "_ids": {
            "z": "c7xJAzdbnwH1-t7Vm9w.rXgIJZTCMKqODpuKHpoM",
            "x": "n4_51866e4dc164a1c5cd82c0babdafb9a65d5ab (content: S5_331b7e710abd1443cd82d6b5cdafb9f04d5ab)",
            "y": "Ny_2c054fb898b960f9bf0d1fd7c59add74ecbf8 (content: fA_de7615cbcc0d4d67bf0d85f2d59addbeccbf8)"
        }
    }
    >>> print(d.z)
    23
    >>> d >>= Random(0) >> let(f, a=[1,2,3]) >> let(f, a=[9,8,7])
    >>> d.show(colored=False)
    {
        "z": "→(a x y)",
        "x": 3,
        "y": 8,
        "_id": "5R.rmGg2IXzfd7NE0cmFzqxUJf8s9cp4PHp-q0TO",
        "_ids": {
            "z": "vgtk9oIi0CwaqrDa9XXam67gptes9cp4PHp-q0TO",
            "x": "n4_51866e4dc164a1c5cd82c0babdafb9a65d5ab (content: S5_331b7e710abd1443cd82d6b5cdafb9f04d5ab)",
            "y": "Ny_2c054fb898b960f9bf0d1fd7c59add74ecbf8 (content: fA_de7615cbcc0d4d67bf0d85f2d59addbeccbf8)"
        }
    }
    >>> print(d.z)
    32
    """

    def __init__(self, f, **kwargs):
        from idict.core.idict_ import Idict

        super().__init__(f, Idict, config=None)
        self.config = {k: kwargs[k] for k in sorted(kwargs.keys())}

    @cached_property
    def bytes(self):
        return dumps(self.config, sort_keys=True, cls=CustomJSONEncoder).encode()

    def __repr__(self):
        return "λ" + str(self.config)

    def __rrshift__(self, left: Union[dict, list, Random, Callable, "iLet"]):
        """
        >>> from idict.parameter.ilet import iLet
        >>> ({"x":5} >> iLet(lambda x=None:{"x": x**2}, x=5)).show(colored=False)
        {
            "x": "→(x)",
            "_id": "vwO4YONlRgV.xo-hoayAKTqnyoOR-tw5D.nfk2Sv",
            "_ids": {
                "x": "vwO4YONlRgV.xo-hoayAKTqnyoOR-tw5D.nfk2Sv"
            }
        }
        >>> [{}] >> iLet(lambda x=None:{"x": x**2}, x=5)
        «^ × λ{'x': 5}»
        >>> from idict import Ø, idict
        >>> d = idict() >> (Ø >> iLet(lambda x=None:{"x": x**2}, x=5))
        >>> d.show(colored=False)
        {
            "x": "→(x)",
            "_id": "in2IaGHscEXIobU6WbD2JOBlpHPR-tw5D.nfk2Sv",
            "_ids": {
                "x": "in2IaGHscEXIobU6WbD2JOBlpHPR-tw5D.nfk2Sv"
            }
        }
        """
        from idict import iEmpty

        if isinstance(left, iEmpty):
            from idict.parameter.ifunctionspace import iFunctionSpace

            return iFunctionSpace(self)
        if isinstance(left, dict) and not isinstance(left, AbstractLazyDict):
            from idict.core.idict_ import Idict

            return Idict(left) >> self
        if isinstance(left, (list, Random, Callable)):
            from idict.parameter.ifunctionspace import iFunctionSpace

            return iFunctionSpace(left, aop, self)
        return NotImplemented  # pragma: no cover

    def __rshift__(self, other: Union[dict, list, Random, Callable, "iLet", AbstractLazyDict]):
        """
        >>> iLet(lambda x:{"x": x**2}, x=5) >> [1]
        «λ{'x': 5} × ^»
        """

        if isinstance(other, (dict, list, Random, Callable, iLet)):
            from idict.parameter.ifunctionspace import iFunctionSpace

            return iFunctionSpace(self, aop, other)
        return NotImplemented  # pragma: no cover

    def __rxor__(self, left: Union[dict, list, Random, Callable, "iLet"]):
        if isinstance(left, (dict, list, Random, Callable)) and not isinstance(left, AbstractLazyDict):
            from idict.parameter.ifunctionspace import iFunctionSpace

            return iFunctionSpace(left, cop, self)
        return NotImplemented  # pragma: no cover

    def __xor__(self, other: Union[dict, list, Random, Callable, "iLet", AbstractLazyDict]):
        if isinstance(other, (dict, list, Random, Callable, iLet)):
            from idict.parameter.ifunctionspace import iFunctionSpace

            return iFunctionSpace(self, cop, other)
        return NotImplemented  # pragma: no cover

    def __getattr__(self, item):  # pragma: no cover
        from idict.core.idict_ import Idict

        if hasattr(Idict, item):
            raise Exception(
                "An expression will only become an 'idict' after being fed with data.\n"
                "E.g.: 'e = let(f, par1=5)' and 'e = Ø >> f' are non-applied expressions."
                "They need some input values to become an idict, e.g.: '{y=3} >> e'\n"
                f"Parameters provided for {self.f}: {self.config}"
            )
