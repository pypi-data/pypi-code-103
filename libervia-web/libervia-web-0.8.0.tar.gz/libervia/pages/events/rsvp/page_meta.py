#!/usr/bin/env python3


from libervia.server.constants import Const as C
from sat.core.i18n import _, D_
from twisted.internet import defer
from twisted.words.protocols.jabber import jid
from sat.core.log import getLogger
from sat.tools.common.template import safe
import time
import html

"""creation of new events"""

name = "event_rsvp"
label = D_("Event Invitation")
access = C.PAGES_ACCESS_PROFILE
template = "event/invitation.html"
log = getLogger(__name__)


def parse_url(self, request):
    self.getPathArgs(
        request,
        ("event_service", "event_node", "event_id"),
        min_args=2,
        event_service="@jid",
        event_id="",
    )


@defer.inlineCallbacks
def prepare_render(self, request):
    template_data = request.template_data
    data = self.getRData(request)
    profile = self.getProfile(request)

    ## Event ##

    event_service = data["event_service"]
    event_node = data["event_node"]
    event_id = data["event_id"]
    event_timestamp, event_data = yield self.host.bridgeCall(
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
    event_invitee_data = yield self.host.bridgeCall(
        "eventInviteeGet",
        event_data["invitees_service"],
        event_data["invitees_node"],
        '',
        profile,
    )
    template_data["invitee"] = event_invitee_data
    template_data["days_left"] = int((event_timestamp - time.time()) / (60 * 60 * 24))

    ## Blog ##

    data["service"] = jid.JID(event_data["blog_service"])
    data["node"] = event_data["blog_node"]
    data["allow_commenting"] = "simple"

    # we now need blog items, using blog common page
    # this will fill the "items" template data
    blog_page = self.getPageByName("blog_view")
    yield blog_page.prepare_render(self, request)


@defer.inlineCallbacks
def on_data_post(self, request):
    type_ = self.getPostedData(request, "type")
    if type_ == "comment":
        blog_page = self.getPageByName("blog_view")
        yield blog_page.on_data_post(self, request)
    elif type_ == "attendance":
        profile = self.getProfile(request)
        service, node, attend, guests = self.getPostedData(
            request, ("service", "node", "attend", "guests")
        )
        data = {"attend": attend, "guests": guests}
        yield self.host.bridgeCall("eventInviteeSet", service, node, data, profile)
    else:
        log.warning(_("Unhandled data type: {}").format(type_))
