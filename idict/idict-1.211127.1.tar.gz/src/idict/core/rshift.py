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

import operator
from functools import reduce
from typing import Dict

from garoupa import Hosh
from idict.core.frozenidentifieddict import FrozenIdentifiedDict
from idict.core.identification import fhosh, removal_id, blobs_hashes_hoshes
from idict.parameter.ilet import iLet


def application(self: FrozenIdentifiedDict, other, f, config_hosh, output=None):
    """
    >>> from idict import let
    >>> from garoupa import ø
    >>> d = FrozenIdentifiedDict(x=3)
    >>> f = lambda x: {"y": x**2}
    >>> f.metadata = {"id": "ffffffffffffffffffffffffffffffffffffffff"}
    >>> d2 = application(d, f, f, ø)
    >>> d2.show(colored=False)
    {
        "y": "→(x)",
        "x": 3,
        "_id": "9CQTZ.-ZMrtDr6MTnOPpxL5.2gsfffffffffffff",
        "_ids": {
            "y": "-UXfi8wcv0uck6LcY6QOTpEl7arfffffffffffff",
            "x": "n4_51866e4dc164a1c5cd82c0babdafb9a65d5ab (content: S5_331b7e710abd1443cd82d6b5cdafb9f04d5ab)"
        }
    }
    >>> d2.hosh / f.metadata["id"] == d.id
    True
    """
    f_hosh = f.metadata["id"] if hasattr(f, "metadata") and "id" in f.metadata else fhosh(f, self.identity.version)
    f_hosh_full = self.identity * config_hosh * f_hosh  # d' = d * ħ(config) * f
    if output:
        frozen = self.frozen >> {output: other}
        outputs = [output]
    else:
        frozen = self.frozen >> other
        outputs = frozen.returned
    uf = self.hosh * f_hosh_full
    ufu_1 = lambda: solve(self.hoshes, outputs, uf)

    # Reorder items.
    newdata, newhoshes, newblobs, newhashes, = (
        {},
        {},
        self.blobs.copy(),
        self.hashes.copy(),
    )
    noutputs = len(outputs)
    if noutputs == 1:
        k = outputs[0]
        newdata[k] = frozen.data[k]
        newhoshes[k] = ufu_1() if k in self.ids else uf * ~self.hosh
    else:
        ufu_1 = ufu_1()
        acc = self.identity
        c = 0
        for i, k in enumerate(outputs):
            newdata[k] = frozen.data[k]
            if i < noutputs - 1:
                field_hosh = ufu_1 * rho(c, self.identity.digits)
                c += 1
                acc *= field_hosh
            else:
                field_hosh = ~acc * ufu_1
            newhoshes[k] = field_hosh
            if k in newblobs:
                del newblobs[k]
            if k in newhashes:
                del newhashes[k]
    for k in self.ids:
        if k not in newdata:
            newhoshes[k] = self.hoshes[k]
            newdata[k] = frozen.data[k]

    cloned_internals = dict(blobs=newblobs, hashes=newhashes, hoshes=newhoshes, hosh=uf)
    return self.clone(newdata, _cloned=cloned_internals)


def delete(self, k):
    f_hosh = self.identity * removal_id(self.identity.delete, k)  # d' = d * "--------------------...................y"
    uf = self.hosh * f_hosh
    newdata = self.data.copy()
    newdata[k] = None
    newhoshes, newblobs, newhashes, = (
        self.hoshes.copy(),
        self.blobs.copy(),
        self.hashes.copy(),
    )
    newhoshes[k] = placeholder(k, f_hosh, self.identity, self.hoshes)
    if k in newblobs:
        del newblobs[k]
    if k in newhashes:
        del newhashes[k]
    return self.clone(newdata, _cloned=dict(blobs=newblobs, hashes=newhashes, hoshes=newhoshes, hosh=uf))


def ihandle_dict(self, dictlike):
    """
    >>> from idict.core.frozenidentifieddict import FrozenIdentifiedDict as idict
    >>> d = idict(x=5, y=7, z=8)
    >>> di = ihandle_dict(d, {"y":None})
    >>> di.show(colored=False)
    {
        "x": 5,
        "y": null,
        "z": 8,
        "_id": "d45pzBr6XLzQMA5yn1ft1TCeE9Y............y",
        "_ids": {
            "x": "hi_7d6b4783509390c5384ac2c1b88fbd3d3cd8f (content: Mj_3bcd9aefb5020343384ae8ccb88fbd872cd8f)",
            "y": "e2AeAgvblRse-zBdTCB74l9IgRV............y",
            "z": "Oy_f8cbcfbad5de50f9bf0d2fd7c59add74ecbf8 (content: fA_de7615cbcc0d4d67bf0d85f2d59addbeccbf8)"
        }
    }
    >>> di2 = ihandle_dict(di, {"w":lambda x,z: x**z})
    >>> di2.show(colored=False)
    {
        "w": "→(x z)",
        "x": 5,
        "y": null,
        "z": 8,
        "_id": "OdqXMcEK-0I1OFrjoL-TpeT4-2zs3d9r2rr8kHNE",
        "_ids": {
            "w": "kpmkRxrgldVN9wJLVH8ofrbQWMts3d9r2rr8kHN5",
            "x": "hi_7d6b4783509390c5384ac2c1b88fbd3d3cd8f (content: Mj_3bcd9aefb5020343384ae8ccb88fbd872cd8f)",
            "y": "e2AeAgvblRse-zBdTCB74l9IgRV............y",
            "z": "Oy_f8cbcfbad5de50f9bf0d2fd7c59add74ecbf8 (content: fA_de7615cbcc0d4d67bf0d85f2d59addbeccbf8)"
        }
    }
    >>> ihandle_dict(di2, {"x": 55555}).show(colored=False)
    {
        "w": "→(x z)",
        "x": 55555,
        "y": null,
        "z": 8,
        "_id": "DQPsvv1oMlWaUDwPP1Sp7yOboYps3d9r2rr8kHNE",
        "_ids": {
            "w": "kpmkRxrgldVN9wJLVH8ofrbQWMts3d9r2rr8kHN5",
            "x": "yU_9d40a5fbe9781c6e90f0eb45bd45cd962a94b (content: 1W_b62d995bf2d19eeb90f0f150cd45cde01a94b)",
            "y": "e2AeAgvblRse-zBdTCB74l9IgRV............y",
            "z": "Oy_f8cbcfbad5de50f9bf0d2fd7c59add74ecbf8 (content: fA_de7615cbcc0d4d67bf0d85f2d59addbeccbf8)"
        }
    }
    >>> (d := ihandle_dict(idict(), {"x": 1555})).show(colored=False)
    {
        "x": 1555,
        "_id": "RU_2b5abc50f25ebdae4523f9cc684d0d70823ba",
        "_ids": {
            "x": "RU_2b5abc50f25ebdae4523f9cc684d0d70823ba"
        }
    }
    >>> d >>= lambda x: {"x": x**2}
    >>> d.show(colored=False)
    {
        "x": "→(x)",
        "_id": "S.MNJJmbDWmOJ43tyUbWsrfAsCWs.g4HNqVBp-Sh",
        "_ids": {
            "x": "S.MNJJmbDWmOJ43tyUbWsrfAsCWs.g4HNqVBp-Sh"
        }
    }
    >>> e = idict(y=7) >> d
    >>> e.show(colored=False)
    {
        "y": 7,
        "x": "→(x)",
        "_id": "FFTjF58Z264CW3VJZOM-sKQNAy5t.g4HNqVBp-Sh",
        "_ids": {
            "y": "Bk_b75c77bb5e2640ad6428eb35f82a492dd8065 (content: 3m_131910d18a892d1b64285250092a4967c8065)",
            "x": "S.MNJJmbDWmOJ43tyUbWsrfAsCWs.g4HNqVBp-Sh"
        }
    }
    """
    from idict.core.frozenidentifieddict import FrozenIdentifiedDict
    from ldict.core.base import AbstractLazyDict

    clone = self.clone(rnd=dictlike.rnd) if isinstance(dictlike, AbstractLazyDict) and dictlike.rnd else self.clone()
    for k, v in dictlike.items():
        if v is None:
            clone = delete(clone, k)
        elif k not in ["_id", "_ids"]:
            if isinstance(v, iLet):
                clone = application(clone, v, v.f, v.bytes, k)
            elif callable(v):
                clone = application(clone, v, v, self.identity, k)
            else:
                internals = blobs_hashes_hoshes({k: v}, self.identity, {})
                if k in internals["blobs"]:
                    clone.blobs[k] = internals["blobs"][k]
                if k in internals["hashes"]:
                    clone.hashes[k] = internals["hashes"][k]
                clone.hoshes[k] = internals["hoshes"][k]
                hosh = reduce(
                    operator.mul, [self.identity] + [v for k, v in clone.hoshes.items() if not k.startswith("_")]
                )
                internals = dict(blobs=clone.blobs, hashes=clone.hashes, hoshes=clone.hoshes, hosh=hosh)
                del clone.data["_id"]
                del clone.data["_ids"]
                clone = FrozenIdentifiedDict(clone.data, rnd=clone.rnd, _cloned=internals, **{k: v})
    return clone


def placeholder(key, f_hosh, identity, hoshes: Dict[str, Hosh]):
    it = iter(hoshes.items())
    while (pair := next(it))[0] != key:
        pass
    # noinspection PyTypeChecker
    oldfield_hosh: Hosh = pair[1]
    right = identity
    for k, v in it:
        right *= v
    field_hosh = oldfield_hosh * right * f_hosh * ~right
    return field_hosh


def solve(hoshes, output, uf: Hosh):
    """
    >>> from idict.core.frozenidentifieddict import FrozenIdentifiedDict as idict
    >>> a = idict(x=3)
    >>> a.show(colored=False)
    {
        "x": 3,
        "_id": "n4_51866e4dc164a1c5cd82c0babdafb9a65d5ab",
        "_ids": {
            "x": "n4_51866e4dc164a1c5cd82c0babdafb9a65d5ab"
        }
    }
    >>> a >>= (lambda x: {"x": x+2})
    >>> a.show(colored=False)
    {
        "x": "→(x)",
        "_id": "A78wiBU2iCnSlVZLwafVURwwvcLYDDRQkGiQ6qJ8",
        "_ids": {
            "x": "A78wiBU2iCnSlVZLwafVURwwvcLYDDRQkGiQ6qJ8"
        }
    }
    >>> a = idict(x=3, y=5) >> (lambda x: {"x": x+2})
    >>> a.hosh == a.hoshes["x"] * a.hoshes["y"]
    True
    >>> a = idict(w=2, x=3) >> (lambda x: {"x": x+2})
    >>> a.hosh == a.hoshes["x"] * a.hoshes["w"]
    True
    >>> a = idict(w=2, x=3, z=1, y=4) >> (lambda x: {"x": x+2})
    >>> a.hosh == a.hoshes["x"] * a.hoshes["w"] * a.hoshes["z"] * a.hoshes["y"]
    True
    >>> a = idict(w=2, x=3, z=1, y=4) >> (lambda w,x,y: {"x": x+2, "a": w*x*y})
    >>> a.hosh == a.hoshes["x"] * a.hoshes["a"] * a.hoshes["w"] * a.hoshes["z"] * a.hoshes["y"]
    True
    >>> a = idict(w=2, x=3, z=1, y=4) >> (lambda w,x,y: {"x": x+2, "y": w*x*y})
    >>> a.hosh == a.hoshes["x"] * a.hoshes["y"] * a.hoshes["w"] * a.hoshes["z"]
    True
    >>> a.show(colored=False)
    {
        "x": "→(w x y)",
        "y": "→(w x y)",
        "w": 2,
        "z": 1,
        "_id": "z-xyxdEPgkQLLVlkUTfstq99X3IzkEFdqK4B1zjh",
        "_ids": {
            "x": "hT7PAVVndMXDt04ypVbZgozMFOsgmEFdqG4B1zji",
            "y": "ofEb.nRSYsUsgAnnyp4KYFovZaUOV6000sv....-",
            "w": "uA_df37fcf59e3bd7d618d96ceccfe8a5ecb5c4b (content: -B_305c3d0e44c94a5418d982f7dfe8a537a5c4b)",
            "z": "U6_9e5ffd6b1d6101bcea46bd139d4b36862f272 (content: l8_09c7059156c4ed2aea46243e9d4b36c01f272)"
        }
    }
    """
    previous = uf.ø
    for k, v in hoshes.items():
        if k not in output:
            previous *= v
    return uf * ~previous


def rho(c, digits):
    return digits // 2 * "-" + str(c).rjust(digits // 2, ".")
