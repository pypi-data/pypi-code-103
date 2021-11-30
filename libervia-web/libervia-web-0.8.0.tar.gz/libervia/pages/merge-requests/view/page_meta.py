#!/usr/bin/env python3


from libervia.server.constants import Const as C
from sat.core.i18n import _
from libervia.server.utils import SubPage
from libervia.server import session_iface
from twisted.words.protocols.jabber import jid
from sat.tools.common import template_xmlui
from sat.tools.common import uri
from sat.tools.common import data_format
from sat.core.log import getLogger

name = "merge-requests_view"
access = C.PAGES_ACCESS_PUBLIC
template = "merge-request/item.html"
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
    session = self.host.getSessionData(request, session_iface.ISATSession)
    service, node, list_item_id = (
        data.get("service", ""),
        data.get("node", ""),
        data["list_item_id"],
    )
    profile = self.getProfile(request)

    if profile is None:
        profile = C.SERVICE_PROFILE

    merge_requests = data_format.deserialise(
        await self.host.bridgeCall(
            "mergeRequestsGet",
            service.full() if service else "",
            node,
            C.NO_LIMIT,
            [list_item_id],
            "",
            {"parse": C.BOOL_TRUE, "labels_as_list": C.BOOL_TRUE},
            profile,
        )
    )
    list_item = template_xmlui.create(
        self.host, merge_requests['items'][0], ignore=["request_data", "type"]
    )
    template_data["item"] = list_item
    template_data["patches"] = merge_requests['items_patches'][0]
    comments_uri = list_item.widgets["comments_uri"].value
    if comments_uri:
        uri_data = uri.parseXMPPUri(comments_uri)
        template_data["comments_node"] = comments_node = uri_data["node"]
        template_data["comments_service"] = comments_service = uri_data["path"]
        template_data["comments"] = data_format.deserialise(await self.host.bridgeCall(
            "mbGet", comments_service, comments_node, C.NO_LIMIT, [], {}, profile
        ))

        template_data["login_url"] = self.getPageRedirectURL(request)

    if session.connected:
        # we set edition URL only if user is the publisher or the node owner
        publisher = jid.JID(list_item.widgets["publisher"].value)
        is_publisher = publisher.userhostJID() == session.jid.userhostJID()
        affiliation = None
        if not is_publisher:
            node = node or self.host.ns_map["merge_requests"]
            affiliation = await self.host.getAffiliation(request, service, node)
        if is_publisher or affiliation == "owner":
            template_data["url_list_item_edit"] = self.getURLByPath(
                SubPage("merge-requests"),
                service.full(),
                node or "@",
                SubPage("merge-requests_edit"),
                list_item_id,
            )


async def on_data_post(self, request):
    type_ = self.getPostedData(request, "type")
    if type_ == "comment":
        blog_page = self.getPageByName("blog_view")
        await blog_page.on_data_post(self, request)
    else:
        log.warning(_("Unhandled data type: {}").format(type_))
