#!/usr/bin/env python3


from sat.core.i18n import _
from libervia.server.constants import Const as C
from twisted.internet import defer
from twisted.words.protocols.jabber import jid
from sat.tools.common import data_objects
from sat.core.log import getLogger

log = getLogger(__name__)

name = "chat_select"
access = C.PAGES_ACCESS_PROFILE
template = "chat/select.html"


@defer.inlineCallbacks
def prepare_render(self, request):
    profile = self.getProfile(request)
    template_data = request.template_data
    rooms = template_data["rooms"] = []
    bookmarks = yield self.host.bridgeCall("bookmarksList", "muc", "all", profile)
    for bm_values in list(bookmarks.values()):
        for room_jid, room_data in bm_values.items():
            url = self.getPageByName("chat").getURL(room_jid)
            rooms.append(data_objects.Room(room_jid, name=room_data.get("name"), url=url))
    rooms.sort(key=lambda r: r.name)


@defer.inlineCallbacks
def on_data_post(self, request):
    jid_ = self.getPostedData(request, "jid")
    if "@" not in jid_:
        profile = self.getProfile(request)
        service = yield self.host.bridgeCall("mucGetService", "", profile)
        if service:
            muc_jid = jid.JID(service)
            muc_jid.user = jid_
            jid_ = muc_jid.full()
        else:
            log.warning(_("Invalid jid received: {jid}".format(jid=jid_)))
            defer.returnValue(C.POST_NO_CONFIRM)
    url = self.getPageByName("chat").getURL(jid_)
    self.HTTPRedirect(request, url)
