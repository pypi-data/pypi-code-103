#!/usr/bin/env python3

from sat.tools.common import template_xmlui
from sat.tools.common import data_objects
from sat.tools.common import data_format
from sat.core.log import getLogger
from sat_frontends.bridge.bridge_frontend import BridgeException
from libervia.server.constants import Const as C

log = getLogger(__name__)

name = "lists"
access = C.PAGES_ACCESS_PUBLIC
template = "list/overview.html"


def parse_url(self, request):
    self.getPathArgs(request, ["service", "node"], service="jid")
    data = self.getRData(request)
    service, node = data["service"], data["node"]
    if node is None:
        self.HTTPRedirect(request, self.getPageByName("lists_disco").url)
    if node == "@":
        node = data["node"] = ""
    template_data = request.template_data
    template_data["url_list_items"] = self.getURL(service.full(), node or "@")
    template_data["url_list_new"] = self.getPageByName("list_new").getURL(
        service.full(), node or "@")


async def prepare_render(self, request):
    data = self.getRData(request)
    template_data = request.template_data
    service, node = data["service"], data["node"]
    submitted_node = await self.host.bridgeCall(
        "psSchemaSubmittedNodeGet",
        node or self.host.ns_map["tickets"]
    )
    profile = self.getProfile(request) or C.SERVICE_PROFILE

    self.checkCache(request, C.CACHE_PUBSUB, service=service, node=node, short="tickets")

    try:
        lists_types = self.getPageData(request, "lists_types")
        if lists_types is None:
            lists_types = {}
            self.setPageData(request, "lists_types", lists_types)
        list_type = lists_types[(service, node)]
    except KeyError:
        ns_tickets_type = self.host.ns_map["tickets_type"]
        schema_raw = await self.host.bridgeCall(
            "psSchemaDictGet",
            service.full(),
            submitted_node,
            profile
        )
        schema = data_format.deserialise(schema_raw)
        try:
            list_type_field = next(
                f for f in schema["fields"] if f["type"] == "hidden"
                and f.get("name") == ns_tickets_type
            )
        except StopIteration:
            list_type = lists_types[(service, node)] = None
        else:
            if list_type_field.get("value") is None:
                list_type = None
            else:
                list_type = list_type_field["value"].lower().strip()
            lists_types[(service, node)] = list_type

    data["list_type"] = template_data["list_type"] = list_type

    extra = self.getPubsubExtra(request)
    extra["labels_as_list"] = C.BOOL_TRUE
    self.handleSearch(request, extra)

    list_raw = await self.host.bridgeCall(
        "listGet",
        service.full() if service else "",
        node,
        C.NO_LIMIT,
        [],
        "",
        extra,
        profile,
    )
    if profile != C.SERVICE_PROFILE:
        try:
            affiliations = await self.host.bridgeCall(
                "psNodeAffiliationsGet",
                service.full() if service else "",
                submitted_node,
                profile
            )
        except BridgeException as e:
            log.warning(
                f"Can't get affiliations for node {submitted_node!r} at {service}: {e}"
            )
            template_data["owner"] = False
        else:
            is_owner = affiliations.get(self.getJid(request).userhost()) == 'owner'
            template_data["owner"] = is_owner
            if is_owner:
                self.exposeToScripts(
                    request,
                    affiliations={str(e): str(a) for e, a in affiliations.items()}
                )
    else:
        template_data["owner"] = False

    list_items, metadata = data_format.deserialise(list_raw, type_check=list)
    template_data["list_items"] = [
        template_xmlui.create(self.host, x) for x in list_items
    ]
    view_url = self.getPageByName('list_view').getURL(service.full(), node or '@')
    template_data["on_list_item_click"] = data_objects.OnClick(
        url=f"{view_url}/{{item.id}}"
    )
    self.setPagination(request, metadata)
    self.exposeToScripts(
        request,
        lists_ns=self.host.ns_map["tickets"],
        pubsub_service=service.full(),
        pubsub_node=node,
        list_type=list_type,
    )


async def on_data_post(self, request):
    data = self.getRData(request)
    profile = self.getProfile(request)
    service = data["service"]
    node = data["node"]
    list_type = self.getPostedData(request, ("type",))
    if list_type == "grocery":
        name, quantity = self.getPostedData(request, ("name", "quantity"))
        if not name:
            self.pageError(request, C.HTTP_BAD_REQUEST)
        item_data = {
            "name": [name],
        }
        if quantity:
            item_data["quantity"] = [quantity]
        await self.host.bridgeCall(
            "listSet", service.full(), node, item_data, "", "", "", profile
        )
        return C.POST_NO_CONFIRM
    else:
        raise NotImplementedError(
            f"Can't use quick list item set for list of type {list_type!r}"
        )
