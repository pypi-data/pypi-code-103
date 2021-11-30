#!/usr/bin/env python3

from libervia.server.constants import Const as C
from sat.tools.common import template_xmlui
from sat.core.log import getLogger

log = getLogger(__name__)


name = "list_new"
access = C.PAGES_ACCESS_PROFILE
template = "list/create_item.html"


def parse_url(self, request):
    self.getPathArgs(request, ["service", "node"], service="jid", node="@")

async def prepare_render(self, request):
    data = self.getRData(request)
    template_data = request.template_data
    service, node = data.get("service", ""), data.get("node", "")
    profile = self.getProfile(request)
    schema = await self.host.bridgeCall("listSchemaGet", service.full(), node, profile)
    data["schema"] = schema
    # following fields are handled in backend
    ignore = (
        "author",
        "author_jid",
        "author_email",
        "created",
        "updated",
        "comments_uri",
        "status",
        "milestone",
        "priority",
    )
    xmlui_obj = template_xmlui.create(self.host, schema, ignore=ignore)
    try:
        # small trick to get a one line text input instead of the big textarea
        xmlui_obj.widgets["labels"].type = "string"
    except KeyError:
        pass

    try:
        wid = xmlui_obj.widgets['body']
    except KeyError:
        pass
    else:
        if wid.type == "xhtmlbox":
            # same as for list_edit, we have to convert for now
            wid.type = "textbox"
            wid.value =  await self.host.bridgeCall(
                "syntaxConvert", wid.value, C.SYNTAX_XHTML, "markdown",
                False, profile)
    template_data["new_list_item_xmlui"] = xmlui_obj


async def on_data_post(self, request):
    data = self.getRData(request)
    service = data["service"]
    node = data["node"]
    posted_data = self.getAllPostedData(request)
    if (("title" in posted_data and not posted_data["title"])
         or ("body" in posted_data and not posted_data["body"])):
        self.pageError(request, C.HTTP_BAD_REQUEST)
    try:
        posted_data["labels"] = [l.strip() for l in posted_data["labels"][0].split(",")]
    except (KeyError, IndexError):
        pass
    profile = self.getProfile(request)

    # we convert back body to XHTML
    if "body" in posted_data:
        body = await self.host.bridgeCall(
            "syntaxConvert", posted_data['body'][0], "markdown", C.SYNTAX_XHTML,
            False, profile)
        posted_data['body'] = ['<div xmlns="{ns}">{body}</div>'.format(ns=C.NS_XHTML,
                                                                     body=body)]


    await self.host.bridgeCall(
        "listSet", service.full(), node, posted_data, "", "", "", profile
    )
    # we don't want to redirect to creation page on success, but to list overview
    data["post_redirect_page"] = (
        self.getPageByName("lists"),
        service.full(),
        node or "@",
    )
