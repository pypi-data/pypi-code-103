#!/usr/bin/env python3


from libervia.server.constants import Const as C
from sat.tools.common import template_xmlui
from sat.tools.common import data_format
from sat.tools.common import data_objects
from sat.core.log import getLogger

log = getLogger(__name__)


name = "merge-requests"
access = C.PAGES_ACCESS_PUBLIC
template = "list/overview.html"


def parse_url(self, request):
    self.getPathArgs(request, ["service", "node"], service="jid")
    data = self.getRData(request)
    service, node = data["service"], data["node"]
    if node is None:
        self.pageRedirect("merge-requests_disco", request)
    if node == "@":
        node = data["node"] = ""
    self.checkCache(
        request, C.CACHE_PUBSUB, service=service, node=node, short="merge-requests"
    )
    template_data = request.template_data
    template_data["url_list_items"] = self.getPageByName("merge-requests").getURL(
        service.full(), node
    )
    template_data["url_list_new"] = self.getSubPageURL(request, "merge-requests_new")


async def prepare_render(self, request):
    data = self.getRData(request)
    template_data = request.template_data
    service, node = data["service"], data["node"]
    profile = self.getProfile(request) or C.SERVICE_PROFILE

    merge_requests = data_format.deserialise(
        await self.host.bridgeCall(
            "mergeRequestsGet",
            service.full() if service else "",
            node,
            C.NO_LIMIT,
            [],
            "",
            {"labels_as_list": C.BOOL_TRUE},
            profile,
        )
    )

    template_data["list_items"] = [
        template_xmlui.create(self.host, x) for x in merge_requests['items']
    ]
    template_data["on_list_item_click"] = data_objects.OnClick(
        url=self.getSubPageURL(request, "merge-requests_view") + "/{item.id}"
    )
