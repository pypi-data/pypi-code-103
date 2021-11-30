#!/usr/bin/env python3

from libervia.server.constants import Const as C
from sat.core.log import getLogger
from sat.core.i18n import _
from sat.tools.common import uri as xmpp_uri

log = getLogger(__name__)
import json

"""forum handling pages"""

name = "forums"
access = C.PAGES_ACCESS_PUBLIC
template = "forum/overview.html"


def parse_url(self, request):
    self.getPathArgs(
        request,
        ["service", "node", "forum_key"],
        service="@jid",
        node="@",
        forum_key="",
    )


def add_breadcrumb(self, request, breadcrumbs):
    # we don't want breadcrumbs here as long as there is no forum discovery
    # because it will be the landing page for forums activity until then
    pass


def getLinks(self, forums):
    for forum in forums:
        try:
            uri = forum["uri"]
        except KeyError:
            pass
        else:
            uri = xmpp_uri.parseXMPPUri(uri)
            service = uri["path"]
            node = uri["node"]
            forum["http_url"] = self.getPageByName("forum_topics").getURL(service, node)
        if "sub-forums" in forum:
            getLinks(self, forum["sub-forums"])


async def prepare_render(self, request):
    data = self.getRData(request)
    template_data = request.template_data
    service, node, key = data["service"], data["node"], data["forum_key"]
    profile = self.getProfile(request) or C.SERVICE_PROFILE

    try:
        forums_raw = await self.host.bridgeCall(
            "forumsGet", service.full() if service else "", node, key, profile
        )
    except Exception as e:
        log.warning(_("Can't retrieve forums: {msg}").format(msg=e))
        forums = []
    else:
        forums = json.loads(forums_raw)
    getLinks(self, forums)

    template_data["forums"] = forums
