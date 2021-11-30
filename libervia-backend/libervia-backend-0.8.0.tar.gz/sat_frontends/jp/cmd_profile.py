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

"""This module permits to manage profiles. It can list, create, delete
and retrieve information about a profile."""

from sat_frontends.jp.constants import Const as C
from sat.core.log import getLogger
from sat.core.i18n import _
from sat_frontends.jp import base

log = getLogger(__name__)


__commands__ = ["Profile"]

PROFILE_HELP = _('The name of the profile')


class ProfileConnect(base.CommandBase):
    """Dummy command to use profile_session parent, i.e. to be able to connect without doing anything else"""

    def __init__(self, host):
        # it's weird to have a command named "connect" with need_connect=False, but it can be handy to be able
        # to launch just the session, so some paradoxes don't hurt
        super(ProfileConnect, self).__init__(host, 'connect', need_connect=False, help=('connect a profile'))

    def add_parser_options(self):
        pass

    async def start(self):
        # connection is already managed by profile common commands
        # so we just need to check arguments and quit
        if not self.args.connect and not self.args.start_session:
            self.parser.error(_("You need to use either --connect or --start-session"))
        self.host.quit()

class ProfileDisconnect(base.CommandBase):

    def __init__(self, host):
        super(ProfileDisconnect, self).__init__(host, 'disconnect', need_connect=False, help=('disconnect a profile'))

    def add_parser_options(self):
        pass

    async def start(self):
        try:
            await self.host.bridge.disconnect(self.args.profile)
        except Exception as e:
            self.disp(f"can't disconnect profile: {e}", error=True)
            self.host.quit(C.EXIT_BRIDGE_ERRBACK)
        else:
            self.host.quit()


class ProfileCreate(base.CommandBase):
    def __init__(self, host):
        super(ProfileCreate, self).__init__(
            host, 'create', use_profile=False, help=('create a new profile'))

    def add_parser_options(self):
        self.parser.add_argument('profile', type=str, help=_('the name of the profile'))
        self.parser.add_argument(
            '-p', '--password', type=str, default='',
            help=_('the password of the profile'))
        self.parser.add_argument(
            '-j', '--jid', type=str, help=_('the jid of the profile'))
        self.parser.add_argument(
            '-x', '--xmpp-password', type=str,
            help=_(
                'the password of the XMPP account (use profile password if not specified)'
            ),
            metavar='PASSWORD')
        self.parser.add_argument(
            '-A', '--autoconnect', choices=[C.BOOL_TRUE, C.BOOL_FALSE], nargs='?',
            const=C.BOOL_TRUE,
            help=_('connect this profile automatically when backend starts')
        )
        self.parser.add_argument(
            '-C', '--component', default='',
            help=_('set to component import name (entry point) if this is a component'))

    async def start(self):
        """Create a new profile"""
        if self.args.profile in await self.host.bridge.profilesListGet():
            self.disp(f"Profile {self.args.profile} already exists.", error=True)
            self.host.quit(C.EXIT_BRIDGE_ERROR)
        try:
            await self.host.bridge.profileCreate(
                self.args.profile, self.args.password, self.args.component)
        except Exception as e:
            self.disp(f"can't create profile: {e}", error=True)
            self.host.quit(C.EXIT_BRIDGE_ERRBACK)

        try:
            await self.host.bridge.profileStartSession(
                self.args.password, self.args.profile)
        except Exception as e:
            self.disp(f"can't start profile session: {e}", error=True)
            self.host.quit(C.EXIT_BRIDGE_ERRBACK)

        if self.args.jid:
            await self.host.bridge.setParam(
                "JabberID", self.args.jid, "Connection", profile_key=self.args.profile)
        xmpp_pwd = self.args.password or self.args.xmpp_password
        if xmpp_pwd:
            await self.host.bridge.setParam(
                "Password", xmpp_pwd, "Connection", profile_key=self.args.profile)

        if self.args.autoconnect is not None:
            await self.host.bridge.setParam(
                "autoconnect_backend", self.args.autoconnect, "Connection",
                profile_key=self.args.profile)

        self.disp(f'profile {self.args.profile} created successfully', 1)
        self.host.quit()


class ProfileDefault(base.CommandBase):
    def __init__(self, host):
        super(ProfileDefault, self).__init__(
            host, 'default', use_profile=False, help=('print default profile'))

    def add_parser_options(self):
        pass

    async def start(self):
        print(await self.host.bridge.profileNameGet('@DEFAULT@'))
        self.host.quit()


class ProfileDelete(base.CommandBase):
    def __init__(self, host):
        super(ProfileDelete, self).__init__(host, 'delete', use_profile=False, help=('delete a profile'))

    def add_parser_options(self):
        self.parser.add_argument('profile', type=str, help=PROFILE_HELP)
        self.parser.add_argument('-f', '--force', action='store_true', help=_('delete profile without confirmation'))

    async def start(self):
        if self.args.profile not in await self.host.bridge.profilesListGet():
            log.error(f"Profile {self.args.profile} doesn't exist.")
            self.host.quit(C.EXIT_NOT_FOUND)
        if not self.args.force:
            message = f"Are you sure to delete profile [{self.args.profile}] ?"
            cancel_message = "Profile deletion cancelled"
            await self.host.confirmOrQuit(message, cancel_message)

        await self.host.bridge.asyncDeleteProfile(self.args.profile)
        self.host.quit()


class ProfileInfo(base.CommandBase):

    def __init__(self, host):
        super(ProfileInfo, self).__init__(
            host, 'info', need_connect=False, use_output=C.OUTPUT_DICT,
            help=_('get information about a profile'))
        self.to_show = [(_("jid"), "Connection", "JabberID"),]

    def add_parser_options(self):
        self.parser.add_argument(
            '--show-password', action='store_true',
            help=_('show the XMPP password IN CLEAR TEXT'))

    async def start(self):
        if self.args.show_password:
            self.to_show.append((_("XMPP password"), "Connection", "Password"))
        self.to_show.append((_("autoconnect (backend)"), "Connection",
                                "autoconnect_backend"))
        data = {}
        for label, category, name in self.to_show:
            try:
                value = await self.host.bridge.asyncGetParamA(
                    name, category, profile_key=self.host.profile)
            except Exception as e:
                self.disp(f"can't get {name}/{category} param: {e}", error=True)
            else:
                data[label] = value

        await self.output(data)
        self.host.quit()


class ProfileList(base.CommandBase):
    def __init__(self, host):
        super(ProfileList, self).__init__(
            host, 'list', use_profile=False, use_output='list', help=('list profiles'))

    def add_parser_options(self):
        group = self.parser.add_mutually_exclusive_group()
        group.add_argument(
            '-c', '--clients', action='store_true', help=_('get clients profiles only'))
        group.add_argument(
            '-C', '--components', action='store_true',
            help=('get components profiles only'))

    async def start(self):
        if self.args.clients:
            clients, components = True, False
        elif self.args.components:
            clients, components = False, True
        else:
            clients, components = True, True
        await self.output(await self.host.bridge.profilesListGet(clients, components))
        self.host.quit()


class ProfileModify(base.CommandBase):

    def __init__(self, host):
        super(ProfileModify, self).__init__(
            host, 'modify', need_connect=False, help=_('modify an existing profile'))

    def add_parser_options(self):
        profile_pwd_group = self.parser.add_mutually_exclusive_group()
        profile_pwd_group.add_argument(
            '-w', '--password', help=_('change the password of the profile'))
        profile_pwd_group.add_argument(
            '--disable-password', action='store_true',
            help=_('disable profile password (dangerous!)'))
        self.parser.add_argument('-j', '--jid', help=_('the jid of the profile'))
        self.parser.add_argument(
            '-x', '--xmpp-password', help=_('change the password of the XMPP account'),
            metavar='PASSWORD')
        self.parser.add_argument(
            '-D', '--default', action='store_true', help=_('set as default profile'))
        self.parser.add_argument(
            '-A', '--autoconnect', choices=[C.BOOL_TRUE, C.BOOL_FALSE], nargs='?',
            const=C.BOOL_TRUE,
            help=_('connect this profile automatically when backend starts')
        )

    async def start(self):
        if self.args.disable_password:
            self.args.password = ''
        if self.args.password is not None:
            await self.host.bridge.setParam(
                "Password", self.args.password, "General", profile_key=self.host.profile)
        if self.args.jid is not None:
            await self.host.bridge.setParam(
                "JabberID", self.args.jid, "Connection", profile_key=self.host.profile)
        if self.args.xmpp_password is not None:
            await self.host.bridge.setParam(
                "Password", self.args.xmpp_password, "Connection",
                profile_key=self.host.profile)
        if self.args.default:
            await self.host.bridge.profileSetDefault(self.host.profile)
        if self.args.autoconnect is not None:
            await self.host.bridge.setParam(
                "autoconnect_backend", self.args.autoconnect, "Connection",
                profile_key=self.host.profile)

        self.host.quit()


class Profile(base.CommandBase):
    subcommands = (
        ProfileConnect, ProfileDisconnect, ProfileCreate, ProfileDefault, ProfileDelete,
        ProfileInfo, ProfileList, ProfileModify)

    def __init__(self, host):
        super(Profile, self).__init__(
            host, 'profile', use_profile=False, help=_('profile commands'))
