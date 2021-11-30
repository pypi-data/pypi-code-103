#!/usr/bin/env python3


from libervia.server.constants import Const as C
from twisted.internet import defer
from sat.core.i18n import _
from sat.core.log import getLogger

log = getLogger(__name__)


name = "events"
access = C.PAGES_ACCESS_PUBLIC
template = "event/overview.html"


@defer.inlineCallbacks
def prepare_render(self, request):
    profile = self.getProfile(request)
    template_data = request.template_data
    template_data["url_event_new"] = self.getSubPageURL(request, "event_new")
    if profile is not None:
        try:
            events = yield self.host.bridgeCall("eventsList", "", "", profile)
        except Exception as e:
            log.warning(_("Can't get events list for {profile}: {reason}").format(
                profile=profile, reason=e))
        else:
            own_events = []
            other_events = []
            for event in events:
                if C.bool(event.get("creator", C.BOOL_FALSE)):
                    own_events.append(event)
                    event["url"] = self.getSubPageURL(
                        request,
                        "event_admin",
                        event.get("service", ""),
                        event.get("node", ""),
                        event.get("item"),
                    )
                else:
                    other_events.append(event)
                    event["url"] = self.getSubPageURL(
                        request,
                        "event_rsvp",
                        event.get("service", ""),
                        event.get("node", ""),
                        event.get("item"),
                    )
                if "thumb_url" not in event and "image" in event:
                    event["thumb_url"] = event["image"]

            template_data["events"] = own_events + other_events
