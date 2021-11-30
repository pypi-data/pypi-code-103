#!/usr/bin/env python3


from libervia.server.constants import Const as C
from twisted.words.protocols.jabber import jid
from sat.tools.common.template import safe
from sat.tools.common import data_format
from sat.core.i18n import _, D_
from sat.core.log import getLogger
import time
import html
import math
import re

name = "event_admin"
label = D_("Event Administration")
access = C.PAGES_ACCESS_PROFILE
template = "event/admin.html"
log = getLogger(__name__)
REG_EMAIL_RE = re.compile(C.REG_EMAIL_RE, re.IGNORECASE)


def parse_url(self, request):
    self.getPathArgs(
        request,
        ("event_service", "event_node", "event_id"),
        min_args=2,
        event_service="@jid",
        event_id="",
    )


async def prepare_render(self, request):
    data = self.getRData(request)
    template_data = request.template_data

    ## Event ##

    event_service = template_data["event_service"] = data["event_service"]
    event_node = template_data["event_node"] = data["event_node"]
    event_id = template_data["event_id"] = data["event_id"]
    profile = self.getProfile(request)
    event_timestamp, event_data = await self.host.bridgeCall(
        "eventGet",
        event_service.userhost() if event_service else "",
        event_node,
        event_id,
        profile,
    )
    try:
        background_image = event_data.pop("background-image")
    except KeyError:
        pass
    else:
        template_data["dynamic_style"] = safe(
            """
            html {
                background-image: url("%s");
                background-size: 15em;
            }
            """
            % html.escape(background_image, True)
        )
    template_data["event"] = event_data
    invitees = await self.host.bridgeCall(
        "eventInviteesList",
        event_data["invitees_service"],
        event_data["invitees_node"],
        profile,
    )
    template_data["invitees"] = invitees
    invitees_guests = 0
    for invitee_data in invitees.values():
        if invitee_data.get("attend", "no") == "no":
            continue
        try:
            invitees_guests += int(invitee_data.get("guests", 0))
        except ValueError:
            log.warning(
                _("guests value is not valid: {invitee}").format(invitee=invitee_data)
            )
    template_data["invitees_guests"] = invitees_guests
    template_data["days_left"] = int(
        math.ceil((event_timestamp - time.time()) / (60 * 60 * 24))
    )

    ## Blog ##

    data["service"] = jid.JID(event_data["blog_service"])
    data["node"] = event_data["blog_node"]
    data["allow_commenting"] = "simple"

    # we now need blog items, using blog common page
    # this will fill the "items" template data
    blog_page = self.getPageByName("blog_view")
    await blog_page.prepare_render(self, request)


async def on_data_post(self, request):
    profile = self.getProfile(request)
    if not profile:
        log.error("got post data without profile")
        self.pageError(request, C.HTTP_INTERNAL_ERROR)
    type_ = self.getPostedData(request, "type")
    if type_ == "blog":
        service, node, title, body, lang = self.getPostedData(
            request, ("service", "node", "title", "body", "language")
        )

        if not body.strip():
            self.pageError(request, C.HTTP_BAD_REQUEST)
        data = {"content": body}
        if title:
            data["title"] = title
        if lang:
            data["language"] = lang
        try:
            comments = bool(self.getPostedData(request, "comments").strip())
        except KeyError:
            pass
        else:
            if comments:
                data["allow_comments"] = True

        try:
            await self.host.bridgeCall(
                "mbSend", service, node, data_format.serialise(data), profile)
        except Exception as e:
            if "forbidden" in str(e):
                self.pageError(request, C.HTTP_FORBIDDEN)
            else:
                raise e
    elif type_ == "event":
        service, node, event_id, jids, emails = self.getPostedData(
            request, ("service", "node", "event_id", "jids", "emails")
        )
        for invitee_jid_s in jids.split():
            try:
                invitee_jid = jid.JID(invitee_jid_s)
            except RuntimeError:
                log.warning(
                    _("this is not a valid jid: {jid}").format(jid=invitee_jid_s)
                )
                continue
            await self.host.bridgeCall(
                "eventInvite", invitee_jid.userhost(), service, node, event_id, profile
            )
        for email_addr in emails.split():
            if not REG_EMAIL_RE.match(email_addr):
                log.warning(
                    _("this is not a valid email address: {email}").format(
                        email=email_addr
                    )
                )
                continue
            await self.host.bridgeCall(
                "eventInviteByEmail",
                service,
                node,
                event_id,
                email_addr,
                {},
                "",
                "",
                "",
                "",
                "",
                "",
                profile,
            )

    else:
        log.warning(_("Unhandled data type: {}").format(type_))
