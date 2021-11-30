#!/usr/bin/env python3

# jp: a SàT command line tool
# Copyright (C) 2009-2021 Jérôme Poisson (goffi@goffi.org)
# Copyright (C) 2003-2016 Adrien Cossa (souliane@mailoo.org)

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
from collections import OrderedDict
from sat.core.i18n import _
from sat_frontends.jp.constants import Const as C
from sat_frontends.tools import jid
from sat.tools.common.ansi import ANSI as A

__commands__ = ["Roster"]


class Get(base.CommandBase):

    def __init__(self, host):
        super().__init__(
            host, 'get', use_output=C.OUTPUT_DICT, use_verbose=True,
            extra_outputs = {"default": self.default_output},
            help=_('retrieve the roster entities'))

    def add_parser_options(self):
        pass

    def default_output(self, data):
        for contact_jid, contact_data in data.items():
            all_keys = list(contact_data.keys())
            keys_to_show = []
            name = contact_data.get('name', contact_jid.node)

            if self.verbosity >= 1:
                keys_to_show.append('groups')
                all_keys.remove('groups')
            if self.verbosity >= 2:
                keys_to_show.extend(all_keys)

            if name is None:
                self.disp(A.color(C.A_HEADER, contact_jid))
            else:
                self.disp(A.color(C.A_HEADER, name, A.RESET, f" ({contact_jid})"))
            for k in keys_to_show:
                value = contact_data[k]
                if value:
                    if isinstance(value, list):
                        value = ', '.join(value)
                    self.disp(A.color(
                        "    ", C.A_SUBHEADER, f"{k}: ", A.RESET, str(value)))

    async def start(self):
        try:
            contacts = await self.host.bridge.getContacts(profile_key=self.host.profile)
        except Exception as e:
            self.disp(f"error while retrieving the contacts: {e}", error=True)
            self.host.quit(C.EXIT_BRIDGE_ERRBACK)

        contacts_dict = {}
        for contact_jid_s, data, groups in contacts:
            # FIXME: we have to convert string to bool here for historical reason
            #        getContacts format should be changed and serialised properly
            for key in ('from', 'to', 'ask'):
                if key in data:
                    data[key] = C.bool(data[key])
            data['groups'] = list(groups)
            contacts_dict[jid.JID(contact_jid_s)] = data

        await self.output(contacts_dict)
        self.host.quit()


class Set(base.CommandBase):

    def __init__(self, host):
        super().__init__(host, 'set', help=_('set metadata for a roster entity'))

    def add_parser_options(self):
        self.parser.add_argument(
            "-n", "--name", default="", help=_('name to use for this entity'))
        self.parser.add_argument(
            "-g", "--group", dest='groups', action='append', metavar='GROUP', default=[],
            help=_('groups for this entity'))
        self.parser.add_argument(
            "-R", "--replace", action="store_true",
            help=_("replace all metadata instead of adding them"))
        self.parser.add_argument(
            "jid", help=_("jid of the roster entity"))

    async def start(self):

        if self.args.replace:
            name = self.args.name
            groups = self.args.groups
        else:
            try:
                entity_data = await self.host.bridge.contactGet(
                    self.args.jid, self.host.profile)
            except Exception as e:
                self.disp(f"error while retrieving the contact: {e}", error=True)
                self.host.quit(C.EXIT_BRIDGE_ERRBACK)
            name = self.args.name or entity_data[0].get('name') or ''
            groups = set(entity_data[1])
            groups = list(groups.union(self.args.groups))

        try:
            await self.host.bridge.updateContact(
                self.args.jid, name, groups, self.host.profile)
        except Exception as e:
            self.disp(f"error while updating the contact: {e}", error=True)
            self.host.quit(C.EXIT_BRIDGE_ERRBACK)
        self.host.quit()


class Delete(base.CommandBase):

    def __init__(self, host):
        super().__init__(host, 'delete', help=_('remove an entity from roster'))

    def add_parser_options(self):
        self.parser.add_argument(
            "-f", "--force", action="store_true", help=_("delete without confirmation")
        )
        self.parser.add_argument(
            "jid", help=_("jid of the roster entity"))

    async def start(self):
        if not self.args.force:
            message = _("Are you sure to delete {entity} fril your roster?").format(
                entity=self.args.jid
            )
            await self.host.confirmOrQuit(message, _("entity deletion cancelled"))
        try:
            await self.host.bridge.delContact(
                self.args.jid, self.host.profile)
        except Exception as e:
            self.disp(f"error while deleting the entity: {e}", error=True)
            self.host.quit(C.EXIT_BRIDGE_ERRBACK)
        self.host.quit()


class Stats(base.CommandBase):

    def __init__(self, host):
        super(Stats, self).__init__(host, 'stats', help=_('Show statistics about a roster'))

    def add_parser_options(self):
        pass

    async def start(self):
        try:
            contacts = await self.host.bridge.getContacts(profile_key=self.host.profile)
        except Exception as e:
            self.disp(f"error while retrieving the contacts: {e}", error=True)
            self.host.quit(C.EXIT_BRIDGE_ERRBACK)

        hosts = {}
        unique_groups = set()
        no_sub, no_from, no_to, no_group, total_group_subscription = 0, 0, 0, 0, 0
        for contact, attrs, groups in contacts:
            from_, to = C.bool(attrs["from"]), C.bool(attrs["to"])
            if not from_:
                if not to:
                    no_sub += 1
                else:
                    no_from += 1
            elif not to:
                no_to += 1

            host = jid.JID(contact).domain

            hosts.setdefault(host, 0)
            hosts[host] += 1
            if groups:
                unique_groups.update(groups)
                total_group_subscription += len(groups)
            if not groups:
                no_group += 1
        hosts = OrderedDict(sorted(list(hosts.items()), key=lambda item:-item[1]))

        print()
        print("Total number of contacts: %d" % len(contacts))
        print("Number of different hosts: %d" % len(hosts))
        print()
        for host, count in hosts.items():
            print("Contacts on {host}: {count} ({rate:.1f}%)".format(
                host=host, count=count, rate=100 * float(count) / len(contacts)))
        print()
        print("Contacts with no 'from' subscription: %d" % no_from)
        print("Contacts with no 'to' subscription: %d" % no_to)
        print("Contacts with no subscription at all: %d" % no_sub)
        print()
        print("Total number of groups: %d" % len(unique_groups))
        try:
            contacts_per_group = float(total_group_subscription) / len(unique_groups)
        except ZeroDivisionError:
            contacts_per_group = 0
        print("Average contacts per group: {:.1f}".format(contacts_per_group))
        try:
            groups_per_contact = float(total_group_subscription) / len(contacts)
        except ZeroDivisionError:
            groups_per_contact = 0
        print(f"Average groups' subscriptions per contact: {groups_per_contact:.1f}")
        print("Contacts not assigned to any group: %d" % no_group)
        self.host.quit()


class Purge(base.CommandBase):

    def __init__(self, host):
        super(Purge, self).__init__(
            host, 'purge',
            help=_('purge the roster from its contacts with no subscription'))

    def add_parser_options(self):
        self.parser.add_argument(
            "--no-from", action="store_true",
            help=_("also purge contacts with no 'from' subscription"))
        self.parser.add_argument(
            "--no-to", action="store_true",
            help=_("also purge contacts with no 'to' subscription"))

    async def start(self):
        try:
            contacts = await self.host.bridge.getContacts(self.host.profile)
        except Exception as e:
            self.disp(f"error while retrieving the contacts: {e}", error=True)
            self.host.quit(C.EXIT_BRIDGE_ERRBACK)

        no_sub, no_from, no_to = [], [], []
        for contact, attrs, groups in contacts:
            from_, to = C.bool(attrs["from"]), C.bool(attrs["to"])
            if not from_:
                if not to:
                    no_sub.append(contact)
                elif self.args.no_from:
                    no_from.append(contact)
            elif not to and self.args.no_to:
                no_to.append(contact)
        if not no_sub and not no_from and not no_to:
            self.disp(
                f"Nothing to do - there's a from and/or to subscription(s) between "
                f"profile {self.host.profile!r} and each of its contacts"
            )
        elif await self.ask_confirmation(no_sub, no_from, no_to):
            for contact in no_sub + no_from + no_to:
                try:
                    await self.host.bridge.delContact(
                        contact, profile_key=self.host.profile)
                except Exception as e:
                    self.disp(f"can't delete contact {contact!r}: {e}", error=True)
                else:
                    self.disp(f"contact {contact!r} has been removed")

        self.host.quit()

    async def ask_confirmation(self, no_sub, no_from, no_to):
        """Ask the confirmation before removing contacts.

        @param no_sub (list[unicode]): list of contacts with no subscription
        @param no_from (list[unicode]): list of contacts with no 'from' subscription
        @param no_to (list[unicode]): list of contacts with no 'to' subscription
        @return bool
        """
        if no_sub:
            self.disp(
                f"There's no subscription between profile {self.host.profile!r} and the "
                f"following contacts:")
            self.disp("    " + "\n    ".join(no_sub))
        if no_from:
            self.disp(
                f"There's no 'from' subscription between profile {self.host.profile!r} "
                f"and the following contacts:")
            self.disp("    " + "\n    ".join(no_from))
        if no_to:
            self.disp(
                f"There's no 'to' subscription between profile {self.host.profile!r} and "
                f"the following contacts:")
            self.disp("    " + "\n    ".join(no_to))
        message = f"REMOVE them from profile {self.host.profile}'s roster"
        while True:
            res = await self.host.ainput(f"{message} (y/N)? ")
            if not res or res.lower() == 'n':
                return False
            if res.lower() == 'y':
                return True


class Resync(base.CommandBase):

    def __init__(self, host):
        super(Resync, self).__init__(
            host, 'resync', help=_('do a full resynchronisation of roster with server'))

    def add_parser_options(self):
        pass

    async def start(self):
        try:
            await self.host.bridge.rosterResync(profile_key=self.host.profile)
        except Exception as e:
            self.disp(f"can't resynchronise roster: {e}", error=True)
            self.host.quit(C.EXIT_BRIDGE_ERRBACK)
        else:
            self.disp(_("Roster resynchronized"))
            self.host.quit(C.EXIT_OK)


class Roster(base.CommandBase):
    subcommands = (Get, Set, Delete, Stats, Purge, Resync)

    def __init__(self, host):
        super(Roster, self).__init__(
            host, 'roster', use_profile=True, help=_("Manage an entity's roster"))
