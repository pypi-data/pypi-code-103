#!/usr/bin/env python3

# Libervia: an XMPP client
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

"""Objects handling bridge data, with jinja2 safe markup handling"""

from sat.core.constants import Const as C
from sat.tools.common import data_format
from os.path import basename

try:
    from jinja2 import Markup as safe
except ImportError:
    safe = str

from sat.tools.common import uri as xmpp_uri
import urllib.request, urllib.parse, urllib.error

q = lambda value: urllib.parse.quote(value.encode("utf-8"), safe="@")


class Message(object):
    def __init__(self, msg_data):
        self._uid = msg_data[0]
        self._timestamp = msg_data[1]
        self._from_jid = msg_data[2]
        self._to_jid = msg_data[3]
        self._message_data = msg_data[4]
        self._subject_data = msg_data[5]
        self._type = msg_data[6]
        self._extra = data_format.deserialise(msg_data[7])
        self._html = dict(data_format.getSubDict("xhtml", self._extra))

    @property
    def id(self):
        return self._uid

    @property
    def timestamp(self):
        return self._timestamp

    @property
    def from_(self):
        return self._from_jid

    @property
    def text(self):
        try:
            return self._message_data[""]
        except KeyError:
            return next(iter(self._message_data.values()))

    @property
    def subject(self):
        try:
            return self._subject_data[""]
        except KeyError:
            return next(iter(self._subject_data.values()))

    @property
    def type(self):
        return self._type

    @property
    def thread(self):
        return self._extra.get("thread")

    @property
    def thread_parent(self):
        return self._extra.get("thread_parent")

    @property
    def received(self):
        return self._extra.get("received_timestamp", self._timestamp)

    @property
    def delay_sender(self):
        return self._extra.get("delay_sender")

    @property
    def info_type(self):
        return self._extra.get("info_type")

    @property
    def html(self):
        if not self._html:
            return None
        try:
            return safe(self._html[""])
        except KeyError:
            return safe(next(iter(self._html.values())))


class Messages(object):
    def __init__(self, msgs_data):
        self.messages = [Message(m) for m in msgs_data]

    def __len__(self):
        return self.messages.__len__()

    def __missing__(self, key):
        return self.messages.__missing__(key)

    def __getitem__(self, key):
        return self.messages.__getitem__(key)

    def __iter__(self):
        return self.messages.__iter__()

    def __reversed__(self):
        return self.messages.__reversed__()

    def __contains__(self, item):
        return self.messages.__contains__(item)


class Room(object):
    def __init__(self, jid, name=None, url=None):
        self.jid = jid
        self.name = name or jid
        if url is not None:
            self.url = url


class Identity(object):
    def __init__(self, jid_str, data=None):
        self.jid_str = jid_str
        self.data = data if data is not None else {}

    @property
    def avatar_basename(self):
        try:
            return basename(self.data['avatar']['path'])
        except (TypeError, KeyError):
            return None

    def __getitem__(self, key):
        return self.data[key]

    def __getattr__(self, key):
        try:
            return self.data[key]
        except KeyError:
            raise AttributeError(key)


class Identities:
    def __init__(self):
        self.identities = {}

    def __iter__(self):
        return iter(self.identities)

    def __getitem__(self, jid_str):
        try:
            return self.identities[jid_str]
        except KeyError:
            return None

    def __setitem__(self, jid_str, data):
        self.identities[jid_str] = Identity(jid_str, data)

    def __contains__(self, jid_str):
        return jid_str in self.identities


class ObjectQuoter(object):
    """object wrapper which quote attribues (to be used in templates)"""

    def __init__(self, obj):
        self.obj = obj

    def __unicode__(self):
        return q(self.obj.__unicode__())

    def __str__(self):
        return self.__unicode__()

    def __getattr__(self, name):
        return q(self.obj.__getattr__(name))

    def __getitem__(self, key):
        return q(self.obj.__getitem__(key))


class OnClick(object):
    """Class to handle clickable elements targets"""

    def __init__(self, url=None):
        self.url = url

    def formatUrl(self, *args, **kwargs):
        """format URL using Python formatting

        values will be quoted before being used
        """
        return self.url.format(
            *[q(a) for a in args], **{k: ObjectQuoter(v) for k, v in kwargs.items()}
        )
