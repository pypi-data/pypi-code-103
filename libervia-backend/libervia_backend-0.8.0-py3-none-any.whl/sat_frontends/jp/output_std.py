#! /usr/bin/env python3


# jp: a SàT command line tool
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
"""Standard outputs"""


from sat_frontends.jp.constants import Const as C
from sat_frontends.tools import jid
from sat.tools.common.ansi import ANSI as A
from sat.tools.common import date_utils
import json

__outputs__ = ["Simple", "Json"]


class Simple(object):
    """Default outputs"""

    def __init__(self, host):
        self.host = host
        host.register_output(C.OUTPUT_TEXT, C.OUTPUT_NAME_SIMPLE, self.simple_print)
        host.register_output(C.OUTPUT_LIST, C.OUTPUT_NAME_SIMPLE, self.list)
        host.register_output(C.OUTPUT_DICT, C.OUTPUT_NAME_SIMPLE, self.dict)
        host.register_output(C.OUTPUT_LIST_DICT, C.OUTPUT_NAME_SIMPLE, self.list_dict)
        host.register_output(C.OUTPUT_DICT_DICT, C.OUTPUT_NAME_SIMPLE, self.dict_dict)
        host.register_output(C.OUTPUT_MESS, C.OUTPUT_NAME_SIMPLE, self.messages)
        host.register_output(C.OUTPUT_COMPLEX, C.OUTPUT_NAME_SIMPLE, self.simple_print)

    def simple_print(self, data):
        self.host.disp(str(data))

    def list(self, data):
        self.host.disp("\n".join(data))

    def dict(self, data, indent=0, header_color=C.A_HEADER):
        options = self.host.parse_output_options()
        self.host.check_output_options({"no-header"}, options)
        show_header = not "no-header" in options
        for k, v in data.items():
            if show_header:
                header = A.color(header_color, k) + ": "
            else:
                header = ""

            self.host.disp(
                (
                    "{indent}{header}{value}".format(
                        indent=indent * " ", header=header, value=v
                    )
                )
            )

    def list_dict(self, data):
        for idx, datum in enumerate(data):
            if idx:
                self.host.disp("\n")
            self.dict(datum)

    def dict_dict(self, data):
        for key, sub_dict in data.items():
            self.host.disp(A.color(C.A_HEADER, key))
            self.dict(sub_dict, indent=4, header_color=C.A_SUBHEADER)

    def messages(self, data):
        # TODO: handle lang, and non chat message (normal, headline)
        for mess_data in data:
            (uid, timestamp, from_jid, to_jid, message, subject, mess_type,
             extra) = mess_data
            time_str = date_utils.date_fmt(timestamp, "auto_day",
                                           tz_info=date_utils.TZ_LOCAL)
            from_jid = jid.JID(from_jid)
            if mess_type == C.MESS_TYPE_GROUPCHAT:
                nick = from_jid.resource
            else:
                nick = from_jid.node

            if self.host.own_jid is not None and self.host.own_jid.bare == from_jid.bare:
                nick_color = A.BOLD + A.FG_BLUE
            else:
                nick_color = A.BOLD + A.FG_YELLOW
            message = list(message.values())[0] if message else ""

            self.host.disp(A.color(
                A.FG_CYAN, '['+time_str+'] ',
                nick_color, nick, A.RESET, A.BOLD, '> ',
                A.RESET, message))


class Json(object):
    """outputs in json format"""

    def __init__(self, host):
        self.host = host
        host.register_output(C.OUTPUT_TEXT, C.OUTPUT_NAME_JSON, self.dump)
        host.register_output(C.OUTPUT_LIST, C.OUTPUT_NAME_JSON, self.dump_pretty)
        host.register_output(C.OUTPUT_LIST, C.OUTPUT_NAME_JSON_RAW, self.dump)
        host.register_output(C.OUTPUT_DICT, C.OUTPUT_NAME_JSON, self.dump_pretty)
        host.register_output(C.OUTPUT_DICT, C.OUTPUT_NAME_JSON_RAW, self.dump)
        host.register_output(C.OUTPUT_LIST_DICT, C.OUTPUT_NAME_JSON, self.dump_pretty)
        host.register_output(C.OUTPUT_LIST_DICT, C.OUTPUT_NAME_JSON_RAW, self.dump)
        host.register_output(C.OUTPUT_DICT_DICT, C.OUTPUT_NAME_JSON, self.dump_pretty)
        host.register_output(C.OUTPUT_DICT_DICT, C.OUTPUT_NAME_JSON_RAW, self.dump)
        host.register_output(C.OUTPUT_MESS, C.OUTPUT_NAME_JSON, self.dump_pretty)
        host.register_output(C.OUTPUT_MESS, C.OUTPUT_NAME_JSON_RAW, self.dump)
        host.register_output(C.OUTPUT_COMPLEX, C.OUTPUT_NAME_JSON, self.dump_pretty)
        host.register_output(C.OUTPUT_COMPLEX, C.OUTPUT_NAME_JSON_RAW, self.dump)

    def dump(self, data):
        self.host.disp(json.dumps(data, default=str))

    def dump_pretty(self, data):
        self.host.disp(json.dumps(data, indent=4, default=str))
