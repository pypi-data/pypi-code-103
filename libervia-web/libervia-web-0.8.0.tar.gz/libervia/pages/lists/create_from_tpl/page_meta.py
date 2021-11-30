#!/usr/bin/env python3

from sat.tools.common import data_format
from sat.core.log import getLogger
from sat.core.i18n import D_
from sat.core import exceptions
from libervia.server.constants import Const as C
from sat_frontends.bridge.bridge_frontend import BridgeException

log = getLogger(__name__)

name = "list_create_from_tpl"
access = C.PAGES_ACCESS_PROFILE
template = "list/create_from_template.html"


def parse_url(self, request):
    self.getPathArgs(request, ["template_id"])

async def prepare_render(self, request):
    data = self.getRData(request)
    template_id = data["template_id"]
    if not template_id:
        self.pageError(request, C.HTTP_BAD_REQUEST)

    template_data = request.template_data
    profile = self.getProfile(request)
    tpl_raw = await self.host.bridgeCall(
        "listTemplateGet",
        template_id,
        "",
        profile,
    )
    template = data_format.deserialise(tpl_raw)
    template['id'] = template_id
    template_data["list_template"] = template

async def on_data_post(self, request):
    data = self.getRData(request)
    template_id = data['template_id']
    name, access = self.getPostedData(request, ('name', 'access'))
    if access == 'private':
        access_model = 'whitelist'
    elif access == 'public':
        access_model = 'open'
    else:
        log.warning(f"Unknown access for template creation: {access}")
        self.pageError(request, C.HTTP_BAD_REQUEST)
    profile = self.getProfile(request)
    try:
        service, node = await self.host.bridgeCall(
            "listTemplateCreate", template_id, name, access_model, profile
        )
    except BridgeException as e:
        if e.condition == "conflict":
            raise exceptions.DataError(D_("A list with this name already exists"))
        else:
            log.error(f"Can't create list from template: {e}")
            raise e
    data["post_redirect_page"] = (
        self.getPageByName("lists"),
        service,
        node or "@",
    )
