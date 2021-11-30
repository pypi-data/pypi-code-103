#!/usr/bin/env python3


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


from . import base
from sat.core.i18n import _
from sat_frontends.jp.constants import Const as C
from sat.tools.common.ansi import ANSI as A
from sat.tools.common import data_format

__commands__ = ["Invitation"]


class Create(base.CommandBase):
    def __init__(self, host):
        base.CommandBase.__init__(
            self,
            host,
            "create",
            use_profile=False,
            use_output=C.OUTPUT_DICT,
            help=_("create and send an invitation"),
        )

    def add_parser_options(self):
        self.parser.add_argument(
            "-j",
            "--jid",
            default="",
            help="jid of the invitee (default: generate one)",
        )
        self.parser.add_argument(
            "-P",
            "--password",
            default="",
            help="password of the invitee profile/XMPP account (default: generate one)",
        )
        self.parser.add_argument(
            "-n",
            "--name",
            default="",
            help="name of the invitee",
        )
        self.parser.add_argument(
            "-N",
            "--host-name",
            default="",
            help="name of the host",
        )
        self.parser.add_argument(
            "-e",
            "--email",
            action="append",
            default=[],
            help="email(s) to send the invitation to (if --no-email is set, email will just be saved)",
        )
        self.parser.add_argument(
            "--no-email", action="store_true", help="do NOT send invitation email"
        )
        self.parser.add_argument(
            "-l",
            "--lang",
            default="",
            help="main language spoken by the invitee",
        )
        self.parser.add_argument(
            "-u",
            "--url",
            default="",
            help="template to construct the URL",
        )
        self.parser.add_argument(
            "-s",
            "--subject",
            default="",
            help="subject of the invitation email (default: generic subject)",
        )
        self.parser.add_argument(
            "-b",
            "--body",
            default="",
            help="body of the invitation email (default: generic body)",
        )
        self.parser.add_argument(
            "-x",
            "--extra",
            metavar=("KEY", "VALUE"),
            action="append",
            nargs=2,
            default=[],
            help="extra data to associate with invitation/invitee",
        )
        self.parser.add_argument(
            "-p",
            "--profile",
            default="",
            help="profile doing the invitation (default: don't associate profile)",
        )

    async def start(self):
        extra = dict(self.args.extra)
        email = self.args.email[0] if self.args.email else None
        emails_extra = self.args.email[1:]
        if self.args.no_email:
            if email:
                extra["email"] = email
                data_format.iter2dict("emails_extra", emails_extra)
        else:
            if not email:
                self.parser.error(
                    _("you need to specify an email address to send email invitation")
                )

        try:
            invitation_data = await self.host.bridge.invitationCreate(
                email,
                emails_extra,
                self.args.jid,
                self.args.password,
                self.args.name,
                self.args.host_name,
                self.args.lang,
                self.args.url,
                self.args.subject,
                self.args.body,
                extra,
                self.args.profile,
            )
        except Exception as e:
            self.disp(f"can't create invitation: {e}", error=True)
            self.host.quit(C.EXIT_BRIDGE_ERRBACK)
        else:
            await self.output(invitation_data)
            self.host.quit(C.EXIT_OK)


class Get(base.CommandBase):
    def __init__(self, host):
        base.CommandBase.__init__(
            self,
            host,
            "get",
            use_profile=False,
            use_output=C.OUTPUT_DICT,
            help=_("get invitation data"),
        )

    def add_parser_options(self):
        self.parser.add_argument("id", help=_("invitation UUID"))
        self.parser.add_argument(
            "-j",
            "--with-jid",
            action="store_true",
            help=_("start profile session and retrieve jid"),
        )

    async def output_data(self, data, jid_=None):
        if jid_ is not None:
            data["jid"] = jid_
        await self.output(data)
        self.host.quit()

    async def start(self):
        try:
            invitation_data = await self.host.bridge.invitationGet(
                self.args.id,
            )
        except Exception as e:
            self.disp(msg=_("can't get invitation data: {e}").format(e=e), error=True)
            self.host.quit(C.EXIT_BRIDGE_ERRBACK)

        if not self.args.with_jid:
            await self.output_data(invitation_data)
        else:
            profile = invitation_data["guest_profile"]
            try:
                await self.host.bridge.profileStartSession(
                    invitation_data["password"],
                    profile,
                )
            except Exception as e:
                self.disp(msg=_("can't start session: {e}").format(e=e), error=True)
                self.host.quit(C.EXIT_BRIDGE_ERRBACK)

            try:
                jid_ = await self.host.bridge.asyncGetParamA(
                    "JabberID",
                    "Connection",
                    profile_key=profile,
                )
            except Exception as e:
                self.disp(msg=_("can't retrieve jid: {e}").format(e=e), error=True)
                self.host.quit(C.EXIT_BRIDGE_ERRBACK)

            await self.output_data(invitation_data, jid_)


class Delete(base.CommandBase):
    def __init__(self, host):
        base.CommandBase.__init__(
            self,
            host,
            "delete",
            use_profile=False,
            help=_("delete guest account"),
        )

    def add_parser_options(self):
        self.parser.add_argument("id", help=_("invitation UUID"))

    async def start(self):
        try:
            await self.host.bridge.invitationDelete(
                self.args.id,
            )
        except Exception as e:
            self.disp(msg=_("can't delete guest account: {e}").format(e=e), error=True)
            self.host.quit(C.EXIT_BRIDGE_ERRBACK)

        self.host.quit()


class Modify(base.CommandBase):
    def __init__(self, host):
        base.CommandBase.__init__(
            self, host, "modify", use_profile=False, help=_("modify existing invitation")
        )

    def add_parser_options(self):
        self.parser.add_argument(
            "--replace", action="store_true", help="replace the whole data"
        )
        self.parser.add_argument(
            "-n",
            "--name",
            default="",
            help="name of the invitee",
        )
        self.parser.add_argument(
            "-N",
            "--host-name",
            default="",
            help="name of the host",
        )
        self.parser.add_argument(
            "-e",
            "--email",
            default="",
            help="email to send the invitation to (if --no-email is set, email will just be saved)",
        )
        self.parser.add_argument(
            "-l",
            "--lang",
            dest="language",
            default="",
            help="main language spoken by the invitee",
        )
        self.parser.add_argument(
            "-x",
            "--extra",
            metavar=("KEY", "VALUE"),
            action="append",
            nargs=2,
            default=[],
            help="extra data to associate with invitation/invitee",
        )
        self.parser.add_argument(
            "-p",
            "--profile",
            default="",
            help="profile doing the invitation (default: don't associate profile",
        )
        self.parser.add_argument("id", help=_("invitation UUID"))

    async def start(self):
        extra = dict(self.args.extra)
        for arg_name in ("name", "host_name", "email", "language", "profile"):
            value = getattr(self.args, arg_name)
            if not value:
                continue
            if arg_name in extra:
                self.parser.error(
                    _(
                        "you can't set {arg_name} in both optional argument and extra"
                    ).format(arg_name=arg_name)
                )
            extra[arg_name] = value
        try:
            await self.host.bridge.invitationModify(
                self.args.id,
                extra,
                self.args.replace,
            )
        except Exception as e:
            self.disp(f"can't modify invitation: {e}", error=True)
            self.host.quit(C.EXIT_BRIDGE_ERRBACK)
        else:
            self.disp(_("invitations have been modified successfuly"))
            self.host.quit(C.EXIT_OK)


class List(base.CommandBase):
    def __init__(self, host):
        extra_outputs = {"default": self.default_output}
        base.CommandBase.__init__(
            self,
            host,
            "list",
            use_profile=False,
            use_output=C.OUTPUT_COMPLEX,
            extra_outputs=extra_outputs,
            help=_("list invitations data"),
        )

    def default_output(self, data):
        for idx, datum in enumerate(data.items()):
            if idx:
                self.disp("\n")
            key, invitation_data = datum
            self.disp(A.color(C.A_HEADER, key))
            indent = "  "
            for k, v in invitation_data.items():
                self.disp(indent + A.color(C.A_SUBHEADER, k + ":") + " " + str(v))

    def add_parser_options(self):
        self.parser.add_argument(
            "-p",
            "--profile",
            default=C.PROF_KEY_NONE,
            help=_("return only invitations linked to this profile"),
        )

    async def start(self):
        try:
            data = await self.host.bridge.invitationList(
                self.args.profile,
            )
        except Exception as e:
            self.disp(f"return only invitations linked to this profile: {e}", error=True)
            self.host.quit(C.EXIT_BRIDGE_ERRBACK)
        else:
            await self.output(data)
            self.host.quit()


class Invitation(base.CommandBase):
    subcommands = (Create, Get, Delete, Modify, List)

    def __init__(self, host):
        super(Invitation, self).__init__(
            host,
            "invitation",
            use_profile=False,
            help=_("invitation of user(s) without XMPP account"),
        )
