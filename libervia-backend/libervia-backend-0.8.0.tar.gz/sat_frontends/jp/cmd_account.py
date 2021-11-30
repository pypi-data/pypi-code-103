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

"""This module permits to manage XMPP accounts using in-band registration (XEP-0077)"""

from sat_frontends.jp.constants import Const as C
from sat_frontends.bridge.bridge_frontend import BridgeException
from sat.core.log import getLogger
from sat.core.i18n import _
from sat_frontends.jp import base
from sat_frontends.tools import jid


log = getLogger(__name__)

__commands__ = ["Account"]


class AccountCreate(base.CommandBase):
    def __init__(self, host):
        super(AccountCreate, self).__init__(
            host,
            "create",
            use_profile=False,
            use_verbose=True,
            help=_("create a XMPP account"),
        )

    def add_parser_options(self):
        self.parser.add_argument(
            "jid", help=_("jid to create")
        )
        self.parser.add_argument(
            "password", help=_("password of the account")
        )
        self.parser.add_argument(
            "-p",
            "--profile",
            help=_(
                "create a profile to use this account (default: don't create profile)"
            ),
        )
        self.parser.add_argument(
            "-e",
            "--email",
            default="",
            help=_("email (usage depends of XMPP server)"),
        )
        self.parser.add_argument(
            "-H",
            "--host",
            default="",
            help=_("server host (IP address or domain, default: use localhost)"),
        )
        self.parser.add_argument(
            "-P",
            "--port",
            type=int,
            default=0,
            help=_("server port (default: {port})").format(
                port=C.XMPP_C2S_PORT
            ),
        )

    async def start(self):
        try:
            await self.host.bridge.inBandAccountNew(
                self.args.jid,
                self.args.password,
                self.args.email,
                self.args.host,
                self.args.port,
            )

        except BridgeException as e:
            if e.condition == 'conflict':
                self.disp(
                    f"The account {self.args.jid} already exists",
                    error=True
                )
                self.host.quit(C.EXIT_CONFLICT)
            else:
                self.disp(
                    f"can't create account on {self.args.host or 'localhost'!r} with jid "
                    f"{self.args.jid!r} using In-Band Registration: {e}", error=True)
                self.host.quit(C.EXIT_BRIDGE_ERRBACK)
        except Exception as e:
            self.disp(f"Internal error: {e}", error=True)
            self.host.quit(C.EXIT_INTERNAL_ERROR)

        self.disp(_("XMPP account created"), 1)

        if self.args.profile is None:
            self.host.quit()


        self.disp(_("creating profile"), 2)
        try:
            await self.host.bridge.profileCreate(
                self.args.profile,
                self.args.password,
                "",
            )
        except BridgeException as e:
            if e.condition == 'conflict':
                self.disp(
                    f"The profile {self.args.profile} already exists",
                    error=True
                )
                self.host.quit(C.EXIT_CONFLICT)
            else:
                self.disp(
                    _("Can't create profile {profile} to associate with jid "
                      "{jid}: {e}").format(
                          profile=self.args.profile,
                          jid=self.args.jid,
                          e=e
                      ),
                    error=True,
                )
                self.host.quit(C.EXIT_BRIDGE_ERRBACK)
        except Exception as e:
            self.disp(f"Internal error: {e}", error=True)
            self.host.quit(C.EXIT_INTERNAL_ERROR)

        self.disp(_("profile created"), 1)
        try:
            await self.host.bridge.profileStartSession(
                self.args.password,
                self.args.profile,
            )
        except Exception as e:
            self.disp(f"can't start profile session: {e}", error=True)
            self.host.quit(C.EXIT_BRIDGE_ERRBACK)

        try:
            await self.host.bridge.setParam(
                "JabberID",
                self.args.jid,
                "Connection",
                profile_key=self.args.profile,
            )
        except Exception as e:
            self.disp(f"can't set JabberID parameter: {e}", error=True)
            self.host.quit(C.EXIT_BRIDGE_ERRBACK)

        try:
            await self.host.bridge.setParam(
                "Password",
                self.args.password,
                "Connection",
                profile_key=self.args.profile,
            )
        except Exception as e:
            self.disp(f"can't set Password parameter: {e}", error=True)
            self.host.quit(C.EXIT_BRIDGE_ERRBACK)

        self.disp(
            f"profile {self.args.profile} successfully created and associated to the new "
            f"account", 1)
        self.host.quit()


class AccountModify(base.CommandBase):
    def __init__(self, host):
        super(AccountModify, self).__init__(
            host, "modify", help=_("change password for XMPP account")
        )

    def add_parser_options(self):
        self.parser.add_argument(
            "password", help=_("new XMPP password")
        )

    async def start(self):
        try:
            await self.host.bridge.inBandPasswordChange(
                self.args.password,
                self.args.profile,
            )
        except Exception as e:
            self.disp(f"can't change XMPP password: {e}", error=True)
            self.host.quit(C.EXIT_BRIDGE_ERRBACK)
        else:
            self.host.quit()


class AccountDelete(base.CommandBase):
    def __init__(self, host):
        super(AccountDelete, self).__init__(
            host, "delete", help=_("delete a XMPP account")
        )

    def add_parser_options(self):
        self.parser.add_argument(
            "-f",
            "--force",
            action="store_true",
            help=_("delete account without confirmation"),
        )

    async def start(self):
        try:
            jid_str = await self.host.bridge.asyncGetParamA(
                "JabberID",
                "Connection",
                profile_key=self.profile,
            )
        except Exception as e:
            self.disp(f"can't get JID of the profile: {e}", error=True)
            self.host.quit(C.EXIT_BRIDGE_ERRBACK)

        jid_ = jid.JID(jid_str)
        if not self.args.force:
            message = (
                f"You are about to delete the XMPP account with jid {jid_!r}\n"
                f"This is the XMPP account of profile {self.profile!r}\n"
                f"Are you sure that you want to delete this account?"
            )
            await self.host.confirmOrQuit(message, _("Account deletion cancelled"))

        try:
            await self.host.bridge.inBandUnregister(jid_.domain, self.args.profile)
        except Exception as e:
            self.disp(f"can't delete XMPP account with jid {jid_!r}: {e}", error=True)
            self.host.quit(C.EXIT_BRIDGE_ERRBACK)

        self.host.quit()


class Account(base.CommandBase):
    subcommands = (AccountCreate, AccountModify, AccountDelete)

    def __init__(self, host):
        super(Account, self).__init__(
            host, "account", use_profile=False, help=("XMPP account management")
        )
