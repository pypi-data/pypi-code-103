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

import json

from garoupa import Hosh

from idict.core.identification import key2id
from ldict.customjson import CustomJSONEncoder


def idict2txt(d, all, history):
    r"""
    Textual representation of a ldict object

    >>> from idict.core.frozenidentifieddict import FrozenIdentifiedDict as idict
    >>> from ldict.core.appearance import decolorize
    >>> d = idict(x=1,y=2)
    >>> decolorize(idict2txt(d, False, False))
    '{\n    "x": 1,\n    "y": 2,\n    "_id": "mH_70118e827bbcd88303202a006d34eb63e4fbd",\n    "_ids": "S6_787ce43265467bacea460e239d4b36762f272 wA_8d94995016666dd618d91cdccfe8a5fcb5c4b"\n}'
    >>> decolorize(idict2txt(d, True, False))
    '{\n    "x": 1,\n    "y": 2,\n    "_id": "mH_70118e827bbcd88303202a006d34eb63e4fbd",\n    "_ids": {\n        "x": "S6_787ce43265467bacea460e239d4b36762f272 (content: l8_09c7059156c4ed2aea46243e9d4b36c01f272)",\n        "y": "wA_8d94995016666dd618d91cdccfe8a5fcb5c4b (content: -B_305c3d0e44c94a5418d982f7dfe8a537a5c4b)"\n    }\n}'

    Parameters
    ----------
    d
    all

    Returns
    -------

    """
    dic = idict2dict(d, all, history)
    txt = json.dumps(dic, indent=4, ensure_ascii=False, cls=CustomJSONEncoder)
    for k, v in dic.items():
        if k == "_id":
            txt = txt.replace(dic[k], d.hosh.idc)
    if all:
        for k, v in d.hoshes.items():
            nokey = ""
            if k in d.hashes:
                hash = v // key2id(k, v.digits)
                nokey = f" (content: {hash.idc})"
            txt = txt.replace(v.id, v.idc + nokey)  # REMINDER: workaround to avoid json messing with colors
    return txt


def idict2dict(d, all, history):
    # from ldict.core.base import AbstractLazyDict
    dic = d.data.copy()
    if not history and "_history" in dic:
        dic["_history"] = " ".join(Hosh.fromid(k).id for k in dic["_history"])
    if not all:
        if len(d.ids) < 3:
            dic["_ids"] = " ".join(d.ids.values())
        else:
            ids = list(d.ids.values())
            dic["_ids"] = f"{ids[0]}... +{len(d) - 4} ...{ids[-1]}"
    elif "_ids" in dic:
        dic["_ids"] = d.ids.copy()
    return dic
