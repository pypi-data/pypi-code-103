#!/usr/bin/env python3

from libervia.server.constants import Const as C
from sat.tools.common import uri
import time

name = "blog_feed_atom"
access = C.PAGES_ACCESS_PUBLIC
template = "blog/atom.xml"


async def prepare_render(self, request):
    request.setHeader("Content-Type", "application/atom+xml; charset=utf-8")
    data = self.getRData(request)
    service, node = data["service"], data.get("node")
    self.checkCache(
        request, C.CACHE_PUBSUB, service=service, node=node, short="microblog"
    )
    data["show_comments"] = False
    template_data = request.template_data
    blog_page = self.getPageByName("blog_view")
    await blog_page.prepare_render(self, request)
    items = data["blog_items"]['items']

    template_data["request_uri"] = self.host.getExtBaseURL(
        request, request.path.decode("utf-8")
    )
    template_data["xmpp_uri"] = uri.buildXMPPUri(
        "pubsub", subtype="microblog", path=service.full(), node=node
    )
    blog_view = self.getPageByName("blog_view")
    template_data["http_uri"] = self.host.getExtBaseURL(
        request, blog_view.getURL(service.full(), node)
    )
    if items:
        template_data["updated"] = items[0]['updated']
    else:
        template_data["updated"] = time.time()
