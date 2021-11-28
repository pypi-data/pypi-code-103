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

import requests as req
from idict import idict
from idict.data.compression import unpack, pack
from idict.persistence.cache import Cache
from pandas import DataFrame

from oka.config import default_url


def j(r):
    """Helper function needed because flask test_client() provide json as a property(?), not as a method."""
    return r.json() if callable(r.json) else r.json


@dataclass
class Oka(Cache):
    """Handle posts from command line to spare the user from accessing the web to publish results."""

    # TODO: put sync here also
    token: str = None
    url: str = default_url
    id: str = None

    # Only used in parent class; useless here, but can be used for a Session
    decorator = None

    def __contains__(self, item):
        url = f"/api/item/{item}?checkonly=true"
        ret = j(self.request(url, "get"))
        return ret

    def __lshift__(self, other):
        """Can receive a Data object or a tuple (data, name, description)."""
        if isinstance(other, tuple):
            self.send(other[0], *other[1:])
        self.send(other)

    def __rmatmul__(self, other):
        return self.get(other)

    # noinspection PyArgumentList
    def __call__(self, id=None):
        if id is None:
            return self.__class__(url=self.url)
        return self.get(id)

    def request(self, route, method, **kwargs):
        headers = {"Authorization": "Bearer " + self.token}
        r = getattr(req, method)(self.url + route, headers=headers, **kwargs)
        if r.status_code == 401:
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

    def get(self, id):
        """Get a dataframe, callable or idict from server

        On single-valued idicts, content (dataframe or callable) take precedence and is returned directly."""
        url = f"/api/item/{id}"
        if not (response := self.request(url, "get")):
            raise Exception(f"[Error] Data with OID {id} was not found.")
        value = unpack(response.content)
        if isinstance(value, DataFrame) or callable(value):
            return value
        dic = {}
        for k, v in value["ids"].items():
            url = f"/api/sync?id={id}&fetch=true"
            if not value:
                raise Exception(f"[Error] Missing key {k} for idict with OID {id}.")
            dic[k] = unpack(j(self.request(url, "get")))
        return idict(dic)
        # if not isinstance(value, dict) or "ids" not in value:
        #     raise Exception("dict containing key 'ids' expected.", type(value), value)

    def send(self, d: Union[DataFrame, idict], name=None, description=None):
        """Send a dataframe, callable or idict to server"""
        # Create inactive Post.
        # name = name or "→".join(
        #     x[:3] for x in data.history ^ "name" if x[:3] not in ["B", "Rev", "In", "Aut", "E"]
        # )
        if callable(d) or isinstance(d, DataFrame):
            d = idict(df=d)
        if name:
            d["_name"] = name
        if description:
            d["_description"] = description

        id = "_" + d.id[1:] if len(d.ids) == 1 else d.id
        url = f"/api/item/{id}"
        content = pack({"ids": d.ids})
        response = j(self.request(url, "post", files={"file": content}))["success"]
        if not response:
            print(f"Content already stored for id {d.id}")
            return d.id
        for k, v in d.ids.items():
            if k in d.blobs:
                # Use cached blob.
                content = d.blobs[k]
            else:
                content = pack(d[k], nondeterministic_fallback=True)
            url = f"/api/item/{v}"
            _ = j(self.request(url, "post", files={"file": content}))["success"]

        # except DuplicateEntryException as e:
        #     if "OKATESTING" not in os.environ:
        #         print(f"[Error] You have already uploaded the dataset with OID {e}.")

        return d.id

    def __setitem__(self, key, value):
        url = f"/api/item/{key}"
        content = pack(value)
        response = j(self.request(url, "post", files={"file": content}))["success"]
        if not response:
            print(f"Content already stored for id {key}")
            return None
        return response

    def __getitem__(self, key):
        url = f"/api/item/{key}"
        response = self.request(url, "get")
        if not response:
            raise Exception(f"[Error] Data with OID {key} was not found.")
        return unpack(response.content)

    def __delitem__(self, key):
        pass

    def __repr__(self):
        pass

    def __iter__(self):
        pass


# todo-icones/cores na web
# todo-checar mem leak
# todo-client enviar blob
# todo-enviar DF
