#!/usr/bin/env python3


from libervia.server.constants import Const as C
from sat.core.i18n import _
from sat.tools.common import template_xmlui
from sat.tools.common import data_format
from sat.core.log import getLogger

"""merge-requests edition"""

name = "merge-requests_edit"
access = C.PAGES_ACCESS_PROFILE
template = "merge-request/edit.html"
log = getLogger(__name__)


def parse_url(self, request):
    try:
        item_id = self.nextPath(request)
    except IndexError:
        log.warning(_("no list item id specified"))
        self.pageError(request, C.HTTP_BAD_REQUEST)

    data = self.getRData(request)
    data["list_item_id"] = item_id


async def prepare_render(self, request):
    data = self.getRData(request)
    template_data = request.template_data
    service, node, list_item_id = (
        data.get("service", ""),
        data.get("node", ""),
        data["list_item_id"],
    )
    profile = self.getProfile(request)

    ignore = (
        "publisher",
        "author",
        "author_jid",
        "author_email",
        "created",
        "updated",
        "comments_uri",
        "request_data",
        "type",
    )
    merge_requests = data_format.deserialise(
        await self.host.bridgeCall(
            "mergeRequestsGet",
            service.full() if service else "",
            node,
            C.NO_LIMIT,
            [list_item_id],
            "",
            {},
            profile,
        )
    )
    list_item = template_xmlui.create(
        self.host, merge_requests['items'][0], ignore=ignore
    )

    try:
        # small trick to get a one line text input instead of the big textarea
        list_item.widgets["labels"].type = "string"
        list_item.widgets["labels"].value = list_item.widgets["labels"].value.replace(
            "\n", ", "
        )
    except KeyError:
        pass

    # same as list_edit
    wid = list_item.widgets['body']
    if wid.type == "xhtmlbox":
        wid.type = "textbox"
        wid.value =  await self.host.bridgeCall(
            "syntaxConvert", wid.value, C.SYNTAX_XHTML, "markdown",
            False, profile)

    template_data["new_list_item_xmlui"] = list_item


async def on_data_post(self, request):
    data = self.getRData(request)
    service = data["service"]
    node = data["node"]
    list_item_id = data["list_item_id"]
    posted_data = self.getAllPostedData(request)
    if not posted_data["title"] or not posted_data["body"]:
        self.pageError(request, C.HTTP_BAD_REQUEST)
    try:
        posted_data["labels"] = [l.strip() for l in posted_data["labels"][0].split(",")]
    except (KeyError, IndexError):
        pass
    profile = self.getProfile(request)

    # we convert back body to XHTML
    body = await self.host.bridgeCall(
        "syntaxConvert", posted_data['body'][0], "markdown", C.SYNTAX_XHTML,
        False, profile)
    posted_data['body'] = ['<div xmlns="{ns}">{body}</div>'.format(ns=C.NS_XHTML,
                                                                     body=body)]

    extra = {'update': True}
    await self.host.bridgeCall(
        "mergeRequestSet",
        service.full(),
        node,
        "",
        "auto",
        posted_data,
        "",
        list_item_id,
        data_format.serialise(extra),
        profile,
    )
    # we don't want to redirect to edit page on success, but to list overview
    data["post_redirect_page"] = (
        self.getPageByName("merge-requests"),
        service.full(),
        node or "@",
    )
