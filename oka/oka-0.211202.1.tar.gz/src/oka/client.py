#  Copyright (c) 2020. Davi Pereira dos Santos and Rafael Amatte Bisão
#  This file is part of the oka project.
#  Please respect the license. Removing authorship by any means
#  (by code make up or closing the sources) or ignoring property rights
#  is a crime and is unethical regarding the effort and time spent here.
#  Relevant employers or funding agencies will be notified accordingly.
#
#  oka is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  oka is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with oka.  If not, see <http://www.gnu.org/licenses/>.
#
from dataclasses import dataclass
from typing import Union

import jwt
import requests as req
from garoupa import ø40, ø, Hosh
from garoupa.misc.colors import colorize128bit
from pandas import DataFrame

from idict import idict
from idict.data.compression import unpack, pack
from idict.persistence.compressedcache import CompressedCache
from oka.config import default_url


def j(r):
    """Helper function needed because flask test_client() provide json as a property(?), not as a method."""
    return r.json() if callable(r.json) else r.json


# TODO (minor): detect identity according to number of digits, to pass it as keyworded argument to idict
# TODO: Replace packing of pandas by json-like or pandas own solution


@dataclass
class Oka(CompressedCache):
    """Client for OKA repository

    >>>
    Role:
        - Send/receive datasets or results as pandas DataFrame objects.
        - Send/receive datasets, processed data or results in any format (cannot be visualized on the web).
        - Seamless caching of data within a workflow.

    TODO:
        - Handle posts from command line to spare the user from accessing the web to publish results.
        - Distributed cache (after 'oka.lock(id, state)' is implemented to reserve a job and mark it is still alive).
    """

    # TODO: put sync here also
    token: str = None
    url: str = default_url
    id: str = None
    debug: bool = False

    def __post_init__(self):
        # TODO(minor): verify_signature??
        self.login = jwt.decode(self.token, options={"verify_signature": False})["sub"]
        # TODO: change uid to hybrid? unordered? e o alfabeto?
        # TODO: limitar caracteres do login, pra poder usar b"davips----------------------------"?
        self.user_hosh = ø * ("oka:" + self.login).encode()

    def __contains__(self, item):
        url = f"/api/item/{item}?checkonly=true"
        ret = j(self.request(url, "get"))
        return ret

    def __setitem__(self, id, value, packing=True):
        if self.debug:
            print("oka:", colorize128bit("set", 8), id)
        url = f"/api/item/{id}"
        content = pack(value, ensure_determinism=False) if packing else value
        response = j(self.request(url, "post", files={"file": content}))["success"]
        if not response and self.debug:
            print(f"Content already stored for id {id}")
            return None
        return response

    def __getitem__(self, id, oid="<unknown>", packing=True):
        if self.debug:
            print("oka:", colorize128bit("get", 8), id)
        url = f"/api/item/{id}"
        response = self.request(url, "get")
        if not response:
            raise Exception(f"[Error] Missing key {id} for idict with OID {oid}.")
        if packing:
            return unpack(response.content)
        return response.content

    def __delitem__(self, key):
        pass

    def lockid(self, id):
        pass

    def get(self, id):
        """Get a dataframe, callable or idict from server

        On single-valued idicts, content (dataframe or callable) take precedence over idict and is returned directly."""
        if isinstance(id, Hosh):  # pragma: no cover
            id = id.id
        if not isinstance(id, str):  # pragma: no cover
            raise Exception(f"Wrong id format: {id}; type: {type(id)}")
        value = self.__getitem__(id, oid=id)
        if isinstance(value, DataFrame) or callable(value):
            return value

        # REMINDER: We waste the request above, but return a lazy idict.
        return idict(id, self)

    def send(self, d: Union[DataFrame, idict], name=None, description=None, identity=ø40):
        """Send a dataframe, callable or idict to server"""
        # Create idict.
        if callable(d):
            d = idict(f=d, identity=identity)
        if isinstance(d, DataFrame):
            d = idict(df=d, identity=identity)

        # Build metadata.
        if name:
            d["_name"] = name
        if description:
            d["_description"] = description

        # Store.
        d >> [[self]]

        return d.id

    def __repr__(self):
        pass

    def __iter__(self):
        pass

    # todo-icones/cores na web
    # todo-checar mem leak
    # todo-client enviar blob
    # todo-enviar DF

    def copy(self):
        raise NotImplementedError

    def request(self, route, method, **kwargs):
        headers = {"Authorization": "Bearer " + self.token}
        r = getattr(req, method)(self.url + route, headers=headers, **kwargs)
        if r.status_code == 401:  # pragma: no cover
            raise Exception("Token invalid!")
        elif r.status_code == 422:
            pass
        else:
            if r.ok:
                return r
            print(r.content)
            print(j(r))
            print(j(r)["errors"])
            msg = j(r)["errors"]["json"]
            print(msg)
            raise Exception(msg)

    def __lshift__(self, other):
        """Alias to be used within expressions

        `client << value` is equivalent to `client.send(value)` but returns value.

        `value` can be a Data object or a tuple `(value, name, description)`."""
        if isinstance(other, tuple):
            self.send(other[0], *other[1:])
            return other[0]
        self.send(other)
        return other

    def __rmatmul__(self, other):
        """Alias to be used within expressions

        `id@client` is equivalent to `client.get(value)`"""
        return self.get(other)
