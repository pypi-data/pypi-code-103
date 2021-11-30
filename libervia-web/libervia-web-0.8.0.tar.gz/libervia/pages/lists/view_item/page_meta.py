#!/usr/bin/env python3

from twisted.words.protocols.jabber import jid
from sat.core.i18n import _, D_
from sat.tools.common import template_xmlui
from sat.tools.common import uri
from sat.tools.common import data_format
from sat.core.log import getLogger
from sat_frontends.bridge.bridge_frontend import BridgeException
from libervia.server.constants import Const as C
from libervia.server.utils import SubPage
from libervia.server import session_iface

log = getLogger(__name__)


name = "list_view"
access = C.PAGES_ACCESS_PUBLIC
template = "list/item.html"


def parse_url(self, request):
    self.getPathArgs(request, ["service", "node", "item_id"], service="jid", node="@")
    data = self.getRData(request)
    if data["item_id"] is None:
        log.warning(_("no list item id specified"))
        self.pageError(request, C.HTTP_BAD_REQUEST)


def add_breadcrumb(self, request, breadcrumbs):
    data = self.getRData(request)
    list_url = self.getPageByName("lists").getURL(data["service"].full(),
                                                  data.get("node") or "@")
    breadcrumbs.append({
        "label": D_("List"),
        "url": list_url
    })
    breadcrumbs.append({
        "label": D_("Item"),
    })


async def prepare_render(self, request):
    data = self.getRData(request)
    template_data = request.template_data
    session = self.host.getSessionData(request, session_iface.ISATSession)
    service, node, item_id = (
        data.get("service", ""),
        data.get("node", ""),
        data["item_id"],
    )
    namespace = node or self.host.ns_map["tickets"]
    node = await self.host.bridgeCall("psSchemaSubmittedNodeGet", namespace)

    profile = self.getProfile(request)
    if profile is None:
        profile = C.SERVICE_PROFILE

    list_raw = await self.host.bridgeCall(
        "listGet",
        service.full() if service else "",
        node,
        C.NO_LIMIT,
        [item_id],
        "",
        {"labels_as_list": C.BOOL_TRUE},
        profile,
    )
    list_items, __ = data_format.deserialise(list_raw, type_check=list)
    list_item = [template_xmlui.create(self.host, x) for x in list_items][0]
    template_data["item"] = list_item
    try:
        comments_uri = list_item.widgets["comments_uri"].value
    except KeyError:
        pass
    else:
        if comments_uri:
            uri_data = uri.parseXMPPUri(comments_uri)
            template_data["comments_node"] = comments_node = uri_data["node"]
            template_data["comments_service"] = comments_service = uri_data["path"]
            try:
                comments = data_format.deserialise(await self.host.bridgeCall(
                    "mbGet", comments_service, comments_node, C.NO_LIMIT, [], {}, profile
                ))
            except BridgeException as e:
                if e.classname == 'NotFound' or e.condition == 'item-not-found':
                    log.warning(
                        _("Can't find comment node at [{service}] {node!r}")
                        .format(service=comments_service, node=comments_node)
                    )
                else:
                    raise e
            else:
                template_data["comments"] = comments
                template_data["login_url"] = self.getPageRedirectURL(request)
                self.exposeToScripts(
                    request,
                    comments_node=comments_node,
                    comments_service=comments_service,
                )

    if session.connected:
        # we activate modification action (edit, delete) only if user is the publisher or
        # the node owner
        publisher = jid.JID(list_item.widgets["publisher"].value)
        is_publisher = publisher.userhostJID() == session.jid.userhostJID()
        affiliation = None
        if not is_publisher:
            affiliation = await self.host.getAffiliation(request, service, node)
        if is_publisher or affiliation == "owner":
            self.exposeToScripts(
                request,
                pubsub_service = service.full(),
                pubsub_node = node,
                pubsub_item = item_id,
            )
            template_data["can_modify"] = True
            template_data["url_list_item_edit"] = self.getURLByPath(
                SubPage("list_edit"),
                service.full(),
                node or "@",
                item_id,
            )

    # we add xmpp: URI
    uri_args = {'path': service.full()}
    uri_args['node'] = node
    if item_id:
        uri_args['item'] = item_id
    template_data['xmpp_uri'] = uri.buildXMPPUri('pubsub', **uri_args)


async def on_data_post(self, request):
    type_ = self.getPostedData(request, "type")
    if type_ == "comment":
        blog_page = self.getPageByName("blog_view")
        await blog_page.on_data_post(self, request)
    else:
        log.warning(_("Unhandled data type: {}").format(type_))
