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
import re

from ldict.customjson import CustomJSONEncoder

from idict.core.identification import key2id


def decolorize(txt):
    """
    >>> decolorize("\x1b[38;5;116m\x1b[1m\x1b[48;5;0mB\x1b[0m\x1b[38;5;85m\x1b[1m\x1b[48;5;0ma\x1b[0m\x1b[38;5;157m\x1b[1m\x1b[48;5;0m_\x1b[0m\x1b[38;5;122m\x1b[1m\x1b[48;5;0m3\x1b[0m\x1b[38;5;86m\x1b[1m\x1b[48;5;0m1\x1b[0m\x1b[38;5;156m\x1b[1m\x1b[48;5;0md\x1b[0m\x1b[38;5;114m\x1b[1m\x1b[48;5;0m0\x1b[0m\x1b[38;5;80m\x1b[1m\x1b[48;5;0m0\x1b[0m\x1b[38;5;86m\x1b[1m\x1b[48;5;0m1\x1b[0m\x1b[38;5;156m\x1b[1m\x1b[48;5;0mc\x1b[0m\x1b[38;5;116m\x1b[1m\x1b[48;5;0m1\x1b[0m\x1b[38;5;84m\x1b[1m\x1b[48;5;0ma\x1b[0m\x1b[38;5;114m\x1b[1m\x1b[48;5;0ma\x1b[0m\x1b[38;5;80m\x1b[1m\x1b[48;5;0m4\x1b[0m\x1b[38;5;86m\x1b[1m\x1b[48;5;0m0\x1b[0m\x1b[38;5;156m\x1b[1m\x1b[48;5;0m5\x1b[0m\x1b[38;5;116m\x1b[1m\x1b[48;5;0m6\x1b[0m\x1b[38;5;85m\x1b[1m\x1b[48;5;0mb\x1b[0m\x1b[38;5;157m\x1b[1m\x1b[48;5;0m4\x1b[0m\x1b[38;5;122m\x1b[1m\x1b[48;5;0m6\x1b[0m\x1b[38;5;86m\x1b[1m\x1b[48;5;0mb\x1b[0m\x1b[38;5;156m\x1b[1m\x1b[48;5;0m2\x1b[0m\x1b[38;5;114m\x1b[1m\x1b[48;5;0m0\x1b[0m\x1b[38;5;80m\x1b[1m\x1b[48;5;0m1\x1b[0m\x1b[38;5;86m\x1b[1m\x1b[48;5;0m6\x1b[0m\x1b[38;5;156m\x1b[1m\x1b[48;5;0m1\x1b[0m\x1b[38;5;116m\x1b[1m\x1b[48;5;0m6\x1b[0m\x1b[38;5;84m\x1b[1m\x1b[48;5;0m0\x1b[0m\x1b[38;5;114m\x1b[1m\x1b[48;5;0mb\x1b[0m\x1b[38;5;80m\x1b[1m\x1b[48;5;0mb\x1b[0m\x1b[38;5;86m\x1b[1m\x1b[48;5;0m9\x1b[0m\x1b[38;5;156m\x1b[1m\x1b[48;5;0m5\x1b[0m\x1b[38;5;116m\x1b[1m\x1b[48;5;0m7\x1b[0m\x1b[38;5;85m\x1b[1m\x1b[48;5;0m4\x1b[0m\x1b[38;5;157m\x1b[1m\x1b[48;5;0m2\x1b[0m\x1b[38;5;122m\x1b[1m\x1b[48;5;0me\x1b[0m\x1b[38;5;86m\x1b[1m\x1b[48;5;0me\x1b[0m\x1b[38;5;156m\x1b[1m\x1b[48;5;0mc\x1b[0m\x1b[38;5;114m\x1b[1m\x1b[48;5;0m2\x1b[0m\x1b[38;5;80m\x1b[1m\x1b[48;5;0mb\x1b[0m")
    'Ba_31d001c1aa4056b46b2016160bb95742eec2b'

    Parameters
    ----------
    txt

    Returns
    -------

    """
    ansi_escape = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
    return ansi_escape.sub("", txt)


def idict2txt(d, all):
    r"""
    Textual representation of a ldict object

    >>> from idict.core.frozenidentifieddict import FrozenIdentifiedDict as idict
    >>> d = idict(x=1,y=2)
    >>> decolorize(idict2txt(d, False))
    '{\n    "x": 1,\n    "y": 2,\n    "_id": "mH_70118e827bbcd88303202a006d34eb63e4fbd",\n    "_ids": "S6_787ce43265467bacea460e239d4b36762f272 wA_8d94995016666dd618d91cdccfe8a5fcb5c4b"\n}'
    >>> decolorize(idict2txt(d, True))
    '{\n    "x": 1,\n    "y": 2,\n    "_id": "mH_70118e827bbcd88303202a006d34eb63e4fbd",\n    "_ids": {\n        "x": "S6_787ce43265467bacea460e239d4b36762f272 (content: l8_09c7059156c4ed2aea46243e9d4b36c01f272)",\n        "y": "wA_8d94995016666dd618d91cdccfe8a5fcb5c4b (content: -B_305c3d0e44c94a5418d982f7dfe8a537a5c4b)"\n    }\n}'

    Parameters
    ----------
    d
    all

    Returns
    -------

    """
    dic = idict2dict(d, all)
    txt = json.dumps(dic, indent=4, ensure_ascii=False, cls=CustomJSONEncoder)
    for k, v in dic.items():
        if k == "_id":
            txt = txt.replace(dic[k], d.hosh.idc)
    if all:
        for k, v in d.hoshes.items():
            nokey = f" (content: {v // key2id(k, v.digits)})" if k in d.hashes else ""
            txt = txt.replace(v.id, v.idc + nokey)  # REMINDER: workaround to avoid json messing with colors
    return txt


def idict2dict(d, all):
    # from ldict.core.base import AbstractLazyDict
    dic = d.data.copy()
    for k, v in d.data.items():
        # if isinstance(v, LazyVal):
        #     dic[k] = str(v)
        # elif isinstance(v, AbstractLazyDict):
        #     dic[k] = ldict2dict(v, all)
        if not all:
            if len(d.ids) < 3:
                dic["_ids"] = " ".join(d.ids.values())
            else:
                ids = list(d.ids.values())
                dic["_ids"] = f"{ids[0]}... +{len(d) - 4} ...{ids[-1]}"
        elif k == "_ids":
            dic["_ids"] = d.ids.copy()
    return dic
