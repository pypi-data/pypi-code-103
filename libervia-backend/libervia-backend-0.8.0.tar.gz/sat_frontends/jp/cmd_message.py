#!/usr/bin/env python3


# jp: a SAT command line tool
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

import sys
from sat_frontends.jp import base
from sat_frontends.jp.constants import Const as C
from sat_frontends.tools import jid
from sat.core.i18n import _
from sat.tools.utils import clean_ustr
from sat.tools.common import data_format
from sat.tools.common.ansi import ANSI as A

__commands__ = ["Message"]


class Send(base.CommandBase):
    def __init__(self, host):
        super(Send, self).__init__(host, "send", help=_("send a message to a contact"))

    def add_parser_options(self):
        self.parser.add_argument(
            "-l", "--lang", type=str, default="", help=_("language of the message")
        )
        self.parser.add_argument(
            "-s",
            "--separate",
            action="store_true",
            help=_(
                "separate xmpp messages: send one message per line instead of one "
                "message alone."
            ),
        )
        self.parser.add_argument(
            "-n",
            "--new-line",
            action="store_true",
            help=_(
                "add a new line at the beginning of the input (usefull for ascii art ;))"
            ),
        )
        self.parser.add_argument(
            "-S",
            "--subject",
            help=_("subject of the message"),
        )
        self.parser.add_argument(
            "-L", "--subject-lang", type=str, default="", help=_("language of subject")
        )
        self.parser.add_argument(
            "-t",
            "--type",
            choices=C.MESS_TYPE_STANDARD + (C.MESS_TYPE_AUTO,),
            default=C.MESS_TYPE_AUTO,
            help=_("type of the message"),
        )
        self.parser.add_argument("-e", "--encrypt", metavar="ALGORITHM",
                                 help=_("encrypt message using given algorithm"))
        self.parser.add_argument(
            "--encrypt-noreplace",
            action="store_true",
            help=_("don't replace encryption algorithm if an other one is already used"))
        syntax = self.parser.add_mutually_exclusive_group()
        syntax.add_argument("-x", "--xhtml", action="store_true", help=_("XHTML body"))
        syntax.add_argument("-r", "--rich", action="store_true", help=_("rich body"))
        self.parser.add_argument(
            "jid", help=_("the destination jid")
        )

    async def sendStdin(self, dest_jid):
        """Send incomming data on stdin to jabber contact

        @param dest_jid: destination jid
        """
        header = "\n" if self.args.new_line else ""
        # FIXME: stdin is not read asynchronously at the moment
        stdin_lines = [
            stream for stream in sys.stdin.readlines()
        ]
        extra = {}
        if self.args.subject is None:
            subject = {}
        else:
            subject = {self.args.subject_lang: self.args.subject}

        if self.args.xhtml or self.args.rich:
            key = "xhtml" if self.args.xhtml else "rich"
            if self.args.lang:
                key = f"{key}_{self.args.lang}"
            extra[key] = clean_ustr("".join(stdin_lines))
            stdin_lines = []

        to_send = []

        error = False

        if self.args.separate:
            # we send stdin in several messages
            if header:
                # first we sent the header
                try:
                    await self.host.bridge.messageSend(
                        dest_jid,
                        {self.args.lang: header},
                        subject,
                        self.args.type,
                        profile_key=self.profile,
                    )
                except Exception as e:
                    self.disp(f"can't send header: {e}", error=True)
                    error = True

            to_send.extend({self.args.lang: clean_ustr(l.replace("\n", ""))}
                           for l in stdin_lines)
        else:
            # we sent all in a single message
            if not (self.args.xhtml or self.args.rich):
                msg = {self.args.lang: header + clean_ustr("".join(stdin_lines))}
            else:
                msg = {}
            to_send.append(msg)

        for msg in to_send:
            try:
                await self.host.bridge.messageSend(
                    dest_jid,
                    msg,
                    subject,
                    self.args.type,
                    data_format.serialise(extra),
                    profile_key=self.host.profile)
            except Exception as e:
                self.disp(f"can't send message {msg!r}: {e}", error=True)
                error = True

        if error:
            # at least one message sending failed
            self.host.quit(C.EXIT_BRIDGE_ERRBACK)

        self.host.quit()

    async def start(self):
        if self.args.xhtml and self.args.separate:
            self.disp(
                "argument -s/--separate is not compatible yet with argument -x/--xhtml",
                error=True,
            )
            self.host.quit(C.EXIT_BAD_ARG)

        jids = await self.host.check_jids([self.args.jid])
        jid_ = jids[0]

        if self.args.encrypt_noreplace and self.args.encrypt is None:
            self.parser.error("You need to use --encrypt if you use --encrypt-noreplace")

        if self.args.encrypt is not None:
            try:
                namespace = await self.host.bridge.encryptionNamespaceGet(
                    self.args.encrypt)
            except Exception as e:
                self.disp(f"can't get encryption namespace: {e}", error=True)
                self.host.quit(C.EXIT_BRIDGE_ERRBACK)

            try:
                await self.host.bridge.messageEncryptionStart(
                    jid_, namespace, not self.args.encrypt_noreplace, self.profile
                )
            except Exception as e:
                self.disp(f"can't start encryption session: {e}", error=True)
                self.host.quit(C.EXIT_BRIDGE_ERRBACK)

        await self.sendStdin(jid_)


class MAM(base.CommandBase):

    def __init__(self, host):
        super(MAM, self).__init__(
            host, "mam", use_output=C.OUTPUT_MESS, use_verbose=True,
            help=_("query archives using MAM"))

    def add_parser_options(self):
        self.parser.add_argument(
            "-s", "--service", default="",
            help=_("jid of the service (default: profile's server"))
        self.parser.add_argument(
            "-S", "--start", dest="mam_start", type=base.date_decoder,
            help=_(
                "start fetching archive from this date (default: from the beginning)"))
        self.parser.add_argument(
            "-E", "--end", dest="mam_end", type=base.date_decoder,
            help=_("end fetching archive after this date (default: no limit)"))
        self.parser.add_argument(
            "-W", "--with", dest="mam_with",
            help=_("retrieve only archives with this jid"))
        self.parser.add_argument(
            "-m", "--max", dest="rsm_max", type=int, default=20,
            help=_("maximum number of items to retrieve, using RSM (default: 20))"))
        rsm_page_group = self.parser.add_mutually_exclusive_group()
        rsm_page_group.add_argument(
            "-a", "--after", dest="rsm_after",
            help=_("find page after this item"), metavar='ITEM_ID')
        rsm_page_group.add_argument(
            "-b", "--before", dest="rsm_before",
            help=_("find page before this item"), metavar='ITEM_ID')
        rsm_page_group.add_argument(
            "--index", dest="rsm_index", type=int,
            help=_("index of the page to retrieve"))

    async def start(self):
        extra = {}
        if self.args.mam_start is not None:
            extra["mam_start"] = float(self.args.mam_start)
        if self.args.mam_end is not None:
            extra["mam_end"] = float(self.args.mam_end)
        if self.args.mam_with is not None:
            extra["mam_with"] = self.args.mam_with
        for suff in ('max', 'after', 'before', 'index'):
            key = 'rsm_' + suff
            value = getattr(self.args,key)
            if value is not None:
                extra[key] = str(value)
        try:
            data, metadata_s, profile = await self.host.bridge.MAMGet(
                self.args.service, data_format.serialise(extra), self.profile)
        except Exception as e:
            self.disp(f"can't retrieve MAM archives: {e}", error=True)
            self.host.quit(C.EXIT_BRIDGE_ERRBACK)

        metadata = data_format.deserialise(metadata_s)

        try:
            session_info = await self.host.bridge.sessionInfosGet(self.profile)
        except Exception as e:
            self.disp(f"can't get session infos: {e}", error=True)
            self.host.quit(C.EXIT_BRIDGE_ERRBACK)

        # we need to fill own_jid for message output
        self.host.own_jid = jid.JID(session_info["jid"])

        await self.output(data)

        # FIXME: metadata are not displayed correctly and don't play nice with output
        #        they should be added to output data somehow
        if self.verbosity:
            for value in ("rsm_first", "rsm_last", "rsm_index", "rsm_count",
                          "mam_complete", "mam_stable"):
                if value in metadata:
                    label = value.split("_")[1]
                    self.disp(A.color(
                        C.A_HEADER, label, ': ' , A.RESET, metadata[value]))

        self.host.quit()


class Message(base.CommandBase):
    subcommands = (Send, MAM)

    def __init__(self, host):
        super(Message, self).__init__(
            host, "message", use_profile=False, help=_("messages handling")
        )
