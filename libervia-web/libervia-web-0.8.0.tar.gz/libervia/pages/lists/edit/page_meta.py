#!/usr/bin/env python3


from libervia.server.constants import Const as C
from sat.core.i18n import _
from twisted.internet import defer
from sat.tools.common import template_xmlui
from sat.tools.common import data_format
from sat.core.log import getLogger

log = getLogger(__name__)

name = "list_edit"
access = C.PAGES_ACCESS_PROFILE
template = "list/edit.html"


def parse_url(self, request):
    self.getPathArgs(request, ["service", "node", "item_id"], service="jid", node="@")
    data = self.getRData(request)
    if data["item_id"] is None:
        log.warning(_("no list item id specified"))
        self.pageError(request, C.HTTP_BAD_REQUEST)

@defer.inlineCallbacks
def prepare_render(self, request):
    data = self.getRData(request)
    template_data = request.template_data
    service, node, item_id = (
        data.get("service", ""),
        data.get("node", ""),
        data["item_id"],
    )
    profile = self.getProfile(request)

    # we don't ignore "author" below to keep it when a list item is edited
    # by node owner/admin and "consistent publisher" is activated
    ignore = (
        "publisher",
        "author",
        "author_jid",
        "author_email",
        "created",
        "updated",
        "comments_uri",
    )
    list_raw = yield self.host.bridgeCall(
        "listGet",
        service.full() if service else "",
        node,
        C.NO_LIMIT,
        [item_id],
        "",
        {},
        profile,
    )
    list_items, metadata = data_format.deserialise(list_raw, type_check=list)
    list_item = [template_xmlui.create(self.host, x, ignore=ignore) for x in list_items][0]

    try:
        # small trick to get a one line text input instead of the big textarea
        list_item.widgets["labels"].type = "string"
        list_item.widgets["labels"].value = list_item.widgets["labels"].value.replace(
            "\n", ", "
        )
    except KeyError:
        pass

    # for now we don't have XHTML editor, so we'll go with a TextBox and a convertion
    # to a text friendly syntax using markdown
    wid = list_item.widgets['body']
    if wid.type == "xhtmlbox":
        wid.type = "textbox"
        wid.value =  yield self.host.bridgeCall(
            "syntaxConvert", wid.value, C.SYNTAX_XHTML, "markdown",
            False, profile)

    template_data["new_list_item_xmlui"] = list_item


async def on_data_post(self, request):
    data = self.getRData(request)
    service = data["service"]
    node = data["node"]
    item_id = data["item_id"]
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
        "listSet", service.full(), node, posted_data, "", item_id,
        data_format.serialise(extra), profile
    )
    data["post_redirect_page"] = (
        self.getPageByName("list_view"),
        service.full(),
        node or "@",
        item_id
    )
    return C.POST_NO_CONFIRM
