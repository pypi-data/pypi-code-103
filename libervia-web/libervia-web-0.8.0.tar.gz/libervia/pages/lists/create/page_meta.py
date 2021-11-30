#!/usr/bin/env python3

from libervia.server.constants import Const as C
from sat.tools.common import data_format
from sat.core.log import getLogger

log = getLogger(__name__)

name = "list_create"
access = C.PAGES_ACCESS_PROFILE
template = "list/create.html"


def parse_url(self, request):
    self.getPathArgs(request, ["template_id"])
    data = self.getRData(request)
    if data["template_id"]:
        self.HTTPRedirect(
            request,
            self.getPageByName("list_create_from_tpl").getURL(data["template_id"])
        )


async def prepare_render(self, request):
    template_data = request.template_data
    profile = self.getProfile(request)
    tpl_raw = await self.host.bridgeCall(
        "listTemplatesNamesGet",
        "",
        profile,
    )
    lists_templates = data_format.deserialise(tpl_raw, type_check=list)
    template_data["icons_names"] = {tpl['icon'] for tpl in lists_templates}
    template_data["lists_templates"] = [
        {
            "icon": tpl["icon"],
            "name": tpl["name"],
            "url": self.getURL(tpl["id"]),
        }
        for tpl in lists_templates
    ]
