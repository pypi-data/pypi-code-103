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


from dateutil import parser as du_parser
import calendar
import time
from sat.core.i18n import _
from sat.tools.common.ansi import ANSI as A
from sat_frontends.jp.constants import Const as C
from sat_frontends.jp import common
from sat.tools.common import data_format
from . import base

__commands__ = ["Event"]

OUTPUT_OPT_TABLE = "table"

# TODO: move date parsing to base, it may be useful for other commands


class List(base.CommandBase):
    def __init__(self, host):
        base.CommandBase.__init__(
            self,
            host,
            "list",
            use_output=C.OUTPUT_LIST_DICT,
            use_pubsub=True,
            use_verbose=True,
            help=_("get list of registered events"),
        )

    def add_parser_options(self):
        pass

    async def start(self):
        try:
            events = await self.host.bridge.eventsList(
                self.args.service,
                self.args.node,
                self.profile,
            )
        except Exception as e:
            self.disp(f"can't get list of events: {e}", error=True)
            self.host.quit(C.EXIT_BRIDGE_ERRBACK)
        else:
            await self.output(events)
            self.host.quit()


class Get(base.CommandBase):
    def __init__(self, host):
        base.CommandBase.__init__(
            self,
            host,
            "get",
            use_output=C.OUTPUT_DICT,
            use_pubsub=True,
            pubsub_flags={C.SINGLE_ITEM},
            use_verbose=True,
            help=_("get event data"),
        )

    def add_parser_options(self):
        pass

    async def start(self):
        try:
            event_tuple = await self.host.bridge.eventGet(
                self.args.service,
                self.args.node,
                self.args.item,
                self.profile,
            )
        except Exception as e:
            self.disp(f"can't get event data: {e}", error=True)
            self.host.quit(C.EXIT_BRIDGE_ERRBACK)
        else:
            event_date, event_data = event_tuple
            event_data["date"] = event_date
            await self.output(event_data)
            self.host.quit()


class EventBase(object):
    def add_parser_options(self):
        self.parser.add_argument(
            "-i",
            "--id",
            default="",
            help=_("ID of the PubSub Item"),
        )
        self.parser.add_argument("-d", "--date", type=str, help=_("date of the event"))
        self.parser.add_argument(
            "-f",
            "--field",
            action="append",
            nargs=2,
            dest="fields",
            metavar=("KEY", "VALUE"),
            help=_("configuration field to set"),
        )

    def parseFields(self):
        return dict(self.args.fields) if self.args.fields else {}

    def parseDate(self):
        if self.args.date:
            try:
                date = int(self.args.date)
            except ValueError:
                try:
                    date_time = du_parser.parse(
                        self.args.date, dayfirst=not ("-" in self.args.date)
                    )
                except ValueError as e:
                    self.parser.error(_("Can't parse date: {msg}").format(msg=e))
                if date_time.tzinfo is None:
                    date = calendar.timegm(date_time.timetuple())
                else:
                    date = time.mktime(date_time.timetuple())
        else:
            date = -1
        return date


class Create(EventBase, base.CommandBase):
    def __init__(self, host):
        super(Create, self).__init__(
            host,
            "create",
            use_pubsub=True,
            help=_("create or replace event"),
        )
        EventBase.__init__(self)

    async def start(self):
        fields = self.parseFields()
        date = self.parseDate()
        try:
            node = await self.host.bridge.eventCreate(
                date,
                fields,
                self.args.service,
                self.args.node,
                self.args.id,
                self.profile,
            )
        except Exception as e:
            self.disp(f"can't create event: {e}", error=True)
            self.host.quit(C.EXIT_BRIDGE_ERRBACK)
        else:
            self.disp(_("Event created successfuly on node {node}").format(node=node))
            self.host.quit()


class Modify(EventBase, base.CommandBase):
    def __init__(self, host):
        super(Modify, self).__init__(
            host,
            "modify",
            use_pubsub=True,
            pubsub_flags={C.NODE},
            help=_("modify an existing event"),
        )
        EventBase.__init__(self)

    async def start(self):
        fields = self.parseFields()
        date = 0 if not self.args.date else self.parseDate()
        try:
            self.host.bridge.eventModify(
                self.args.service,
                self.args.node,
                self.args.id,
                date,
                fields,
                self.profile,
            )
        except Exception as e:
            self.disp(f"can't update event data: {e}", error=True)
            self.host.quit(C.EXIT_BRIDGE_ERRBACK)
        else:
            self.host.quit()


class InviteeGet(base.CommandBase):
    def __init__(self, host):
        base.CommandBase.__init__(
            self,
            host,
            "get",
            use_output=C.OUTPUT_DICT,
            use_pubsub=True,
            pubsub_flags={C.NODE},
            use_verbose=True,
            help=_("get event attendance"),
        )

    def add_parser_options(self):
        self.parser.add_argument(
            "-j", "--jid", default="", help=_("bare jid of the invitee")
        )

    async def start(self):
        try:
            event_data = await self.host.bridge.eventInviteeGet(
                self.args.service,
                self.args.node,
                self.args.jid,
                self.profile,
            )
        except Exception as e:
            self.disp(f"can't get event data: {e}", error=True)
            self.host.quit(C.EXIT_BRIDGE_ERRBACK)
        else:
            await self.output(event_data)
            self.host.quit()


class InviteeSet(base.CommandBase):
    def __init__(self, host):
        super(InviteeSet, self).__init__(
            host,
            "set",
            use_output=C.OUTPUT_DICT,
            use_pubsub=True,
            pubsub_flags={C.NODE},
            help=_("set event attendance"),
        )

    def add_parser_options(self):
        self.parser.add_argument(
            "-f",
            "--field",
            action="append",
            nargs=2,
            dest="fields",
            metavar=("KEY", "VALUE"),
            help=_("configuration field to set"),
        )

    async def start(self):
        fields = dict(self.args.fields) if self.args.fields else {}
        try:
            self.host.bridge.eventInviteeSet(
                self.args.service,
                self.args.node,
                fields,
                self.profile,
            )
        except Exception as e:
            self.disp(f"can't set event data: {e}", error=True)
            self.host.quit(C.EXIT_BRIDGE_ERRBACK)
        else:
            self.host.quit()


class InviteesList(base.CommandBase):
    def __init__(self, host):
        extra_outputs = {"default": self.default_output}
        base.CommandBase.__init__(
            self,
            host,
            "list",
            use_output=C.OUTPUT_DICT_DICT,
            extra_outputs=extra_outputs,
            use_pubsub=True,
            pubsub_flags={C.NODE},
            use_verbose=True,
            help=_("get event attendance"),
        )

    def add_parser_options(self):
        self.parser.add_argument(
            "-m",
            "--missing",
            action="store_true",
            help=_("show missing people (invited but no R.S.V.P. so far)"),
        )
        self.parser.add_argument(
            "-R",
            "--no-rsvp",
            action="store_true",
            help=_("don't show people which gave R.S.V.P."),
        )

    def _attend_filter(self, attend, row):
        if attend == "yes":
            attend_color = C.A_SUCCESS
        elif attend == "no":
            attend_color = C.A_FAILURE
        else:
            attend_color = A.FG_WHITE
        return A.color(attend_color, attend)

    def _guests_filter(self, guests):
        return "(" + str(guests) + ")" if guests else ""

    def default_output(self, event_data):
        data = []
        attendees_yes = 0
        attendees_maybe = 0
        attendees_no = 0
        attendees_missing = 0
        guests = 0
        guests_maybe = 0
        for jid_, jid_data in event_data.items():
            jid_data["jid"] = jid_
            try:
                guests_int = int(jid_data["guests"])
            except (ValueError, KeyError):
                pass
            attend = jid_data.get("attend", "")
            if attend == "yes":
                attendees_yes += 1
                guests += guests_int
            elif attend == "maybe":
                attendees_maybe += 1
                guests_maybe += guests_int
            elif attend == "no":
                attendees_no += 1
                jid_data["guests"] = ""
            else:
                attendees_missing += 1
                jid_data["guests"] = ""
            data.append(jid_data)

        show_table = OUTPUT_OPT_TABLE in self.args.output_opts

        table = common.Table.fromListDict(
            self.host,
            data,
            ("nick",) + (("jid",) if self.host.verbosity else ()) + ("attend", "guests"),
            headers=None,
            filters={
                "nick": A.color(C.A_HEADER, "{}" if show_table else "{} "),
                "jid": "{}" if show_table else "{} ",
                "attend": self._attend_filter,
                "guests": "{}" if show_table else self._guests_filter,
            },
            defaults={"nick": "", "attend": "", "guests": 1},
        )
        if show_table:
            table.display()
        else:
            table.display_blank(show_header=False, col_sep="")

        if not self.args.no_rsvp:
            self.disp("")
            self.disp(
                A.color(
                    C.A_SUBHEADER,
                    _("Attendees: "),
                    A.RESET,
                    str(len(data)),
                    _(" ("),
                    C.A_SUCCESS,
                    _("yes: "),
                    str(attendees_yes),
                    A.FG_WHITE,
                    _(", maybe: "),
                    str(attendees_maybe),
                    ", ",
                    C.A_FAILURE,
                    _("no: "),
                    str(attendees_no),
                    A.RESET,
                    ")",
                )
            )
            self.disp(
                A.color(C.A_SUBHEADER, _("confirmed guests: "), A.RESET, str(guests))
            )
            self.disp(
                A.color(
                    C.A_SUBHEADER,
                    _("unconfirmed guests: "),
                    A.RESET,
                    str(guests_maybe),
                )
            )
            self.disp(
                A.color(C.A_SUBHEADER, _("total: "), A.RESET, str(guests + guests_maybe))
            )
        if attendees_missing:
            self.disp("")
            self.disp(
                A.color(
                    C.A_SUBHEADER,
                    _("missing people (no reply): "),
                    A.RESET,
                    str(attendees_missing),
                )
            )

    async def start(self):
        if self.args.no_rsvp and not self.args.missing:
            self.parser.error(_("you need to use --missing if you use --no-rsvp"))
        if not self.args.missing:
            prefilled = {}
        else:
            # we get prefilled data with all people
            try:
                affiliations = await self.host.bridge.psNodeAffiliationsGet(
                    self.args.service,
                    self.args.node,
                    self.profile,
                )
            except Exception as e:
                self.disp(f"can't get node affiliations: {e}", error=True)
                self.host.quit(C.EXIT_BRIDGE_ERRBACK)
            else:
                # we fill all affiliations with empty data, answered one will be filled
                # below. We only consider people with "publisher" affiliation as invited,
                # creators are not, and members can just observe
                prefilled = {
                    jid_: {}
                    for jid_, affiliation in affiliations.items()
                    if affiliation in ("publisher",)
                }

        try:
            event_data = await self.host.bridge.eventInviteesList(
                self.args.service,
                self.args.node,
                self.profile,
            )
        except Exception as e:
            self.disp(f"can't get event data: {e}", error=True)
            self.host.quit(C.EXIT_BRIDGE_ERRBACK)

            # we fill nicknames and keep only requested people

        if self.args.no_rsvp:
            for jid_ in event_data:
                # if there is a jid in event_data it must be there in prefilled too
                # otherwie somebody is not on the invitees list
                try:
                    del prefilled[jid_]
                except KeyError:
                    self.disp(
                        A.color(
                            C.A_WARNING,
                            f"We got a RSVP from somebody who was not in invitees "
                            f"list: {jid_}",
                        ),
                        error=True,
                    )
        else:
            # we replace empty dicts for existing people with R.S.V.P. data
            prefilled.update(event_data)

            # we get nicknames for everybody, make it easier for organisers
        for jid_, data in prefilled.items():
            id_data = await self.host.bridge.identityGet(jid_, [], True, self.profile)
            id_data = data_format.deserialise(id_data)
            data["nick"] = id_data["nicknames"][0]

        await self.output(prefilled)
        self.host.quit()


class InviteeInvite(base.CommandBase):
    def __init__(self, host):
        base.CommandBase.__init__(
            self,
            host,
            "invite",
            use_pubsub=True,
            pubsub_flags={C.NODE, C.SINGLE_ITEM},
            help=_("invite someone to the event through email"),
        )

    def add_parser_options(self):
        self.parser.add_argument(
            "-e",
            "--email",
            action="append",
            default=[],
            help="email(s) to send the invitation to",
        )
        self.parser.add_argument(
            "-N",
            "--name",
            default="",
            help="name of the invitee",
        )
        self.parser.add_argument(
            "-H",
            "--host-name",
            default="",
            help="name of the host",
        )
        self.parser.add_argument(
            "-l",
            "--lang",
            default="",
            help="main language spoken by the invitee",
        )
        self.parser.add_argument(
            "-U",
            "--url-template",
            default="",
            help="template to construct the URL",
        )
        self.parser.add_argument(
            "-S",
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

    async def start(self):
        email = self.args.email[0] if self.args.email else None
        emails_extra = self.args.email[1:]

        try:
            await self.host.bridge.eventInviteByEmail(
                self.args.service,
                self.args.node,
                self.args.item,
                email,
                emails_extra,
                self.args.name,
                self.args.host_name,
                self.args.lang,
                self.args.url_template,
                self.args.subject,
                self.args.body,
                self.args.profile,
            )
        except Exception as e:
            self.disp(f"can't create invitation: {e}", error=True)
            self.host.quit(C.EXIT_BRIDGE_ERRBACK)
        else:
            self.host.quit()


class Invitee(base.CommandBase):
    subcommands = (InviteeGet, InviteeSet, InviteesList, InviteeInvite)

    def __init__(self, host):
        super(Invitee, self).__init__(
            host, "invitee", use_profile=False, help=_("manage invities")
        )


class Event(base.CommandBase):
    subcommands = (List, Get, Create, Modify, Invitee)

    def __init__(self, host):
        super(Event, self).__init__(
            host, "event", use_profile=False, help=_("event management")
        )
