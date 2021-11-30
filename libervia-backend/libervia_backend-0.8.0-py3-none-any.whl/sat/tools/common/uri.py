#!/usr/bin/env python3


# SAT: a jabber client
# Copyright (C) 2009-2021 Jérôme Poisson (goffi@goffi.org)

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

""" XMPP uri parsing tools """

import sys
import urllib.parse
import urllib.request, urllib.parse, urllib.error

# FIXME: basic implementation, need to follow RFC 5122


def parseXMPPUri(uri):
    """Parse an XMPP uri and return a dict with various information

    @param uri(unicode): uri to parse
    @return dict(unicode, unicode): data depending of the URI where key can be:
        type: one of ("pubsub", TODO)
            type is always present
        sub_type: can be:
            - microblog
            only used for pubsub for now
        path: XMPP path (jid of the service or entity)
        node: node used
        id: id of the element (item for pubsub)
    @raise ValueError: the scheme is not xmpp
    """
    uri_split = urllib.parse.urlsplit(uri)
    if uri_split.scheme != "xmpp":
        raise ValueError("this is not a XMPP URI")

    # XXX: we don't use jid.JID for path as it can be used both in backend and frontend
    # which may use different JID classes
    data = {"path": urllib.parse.unquote(uri_split.path)}

    query_end = uri_split.query.find(";")
    query_type = uri_split.query[:query_end]
    if query_end == -1 or "=" in query_type:
        raise ValueError("no query type, invalid XMPP URI")

    if sys.version_info >= (3, 9):
        # parse_qs behaviour has been modified in Python 3.9, ";" is not understood as a
        # parameter separator anymore but the "separator" argument has been added to
        # change it.
        pairs = urllib.parse.parse_qs(uri_split.geturl(), separator=";")
    else:
        pairs = urllib.parse.parse_qs(uri_split.geturl())
    for k, v in list(pairs.items()):
        if len(v) != 1:
            raise NotImplementedError("multiple values not managed")
        if k in ("path", "type", "sub_type"):
            raise NotImplementedError("reserved key used in URI, this is not supported")
        data[k] = urllib.parse.unquote(v[0])

    if query_type:
        data["type"] = query_type
    elif "node" in data:
        data["type"] = "pubsub"
    else:
        data["type"] = ""

    if "node" in data:
        if data["node"].startswith("urn:xmpp:microblog:"):
            data["sub_type"] = "microblog"

    return data


def addPairs(uri, pairs):
    for k, v in pairs.items():
        uri.append(
            ";"
            + urllib.parse.quote_plus(k.encode("utf-8"))
            + "="
            + urllib.parse.quote_plus(v.encode("utf-8"))
        )


def buildXMPPUri(type_, **kwargs):
    uri = ["xmpp:"]
    subtype = kwargs.pop("subtype", None)
    path = kwargs.pop("path")
    uri.append(urllib.parse.quote_plus(path.encode("utf-8")).replace("%40", "@"))

    if type_ == "pubsub":
        if subtype == "microblog" and not kwargs.get("node"):
            kwargs["node"] = "urn:xmpp:microblog:0"
        if kwargs:
            uri.append("?")
            addPairs(uri, kwargs)
    else:
        raise NotImplementedError("{type_} URI are not handled yet".format(type_=type_))

    return "".join(uri)
