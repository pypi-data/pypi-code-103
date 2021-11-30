#!/usr/bin/env python3


from libervia.server.constants import Const as C
from sat.core.i18n import _, D_
from sat.core.log import getLogger
from sat.tools.common import uri as xmpp_uri
from sat.tools.common import data_format
from libervia.server import session_iface

log = getLogger(__name__)

name = "forum_topics"
label = D_("Forum Topics")
access = C.PAGES_ACCESS_PUBLIC
template = "forum/view_topics.html"


def parse_url(self, request):
    self.getPathArgs(request, ["service", "node"], 2, service="jid")


def add_breadcrumb(self, request, breadcrumbs):
    data = self.getRData(request)
    breadcrumbs.append({
        "label": label,
        "url": self.getURL(data["service"].full(), data["node"])
    })


async def prepare_render(self, request):
    profile = self.getProfile(request) or C.SERVICE_PROFILE
    data = self.getRData(request)
    service, node = data["service"], data["node"]
    request.template_data.update({"service": service, "node": node})
    template_data = request.template_data
    page_max = data.get("page_max", 20)
    extra = self.getPubsubExtra(request, page_max=page_max)
    topics, metadata = await self.host.bridgeCall(
        "forumTopicsGet",
        service.full(),
        node,
        extra,
        profile
    )
    metadata = data_format.deserialise(metadata)
    self.setPagination(request, metadata)
    identities = self.host.getSessionData(
        request, session_iface.ISATSession
    ).identities
    for topic in topics:
        parsed_uri = xmpp_uri.parseXMPPUri(topic["uri"])
        author = topic["author"]
        topic["http_uri"] = self.getPageByName("forum_view").getURL(
            parsed_uri["path"], parsed_uri["node"]
        )
        if author not in identities:
            id_raw = await self.host.bridgeCall(
                "identityGet", author, [], True, profile
            )
            identities[topic["author"]] = data_format.deserialise(id_raw)

    template_data["topics"] = topics
    template_data["url_topic_new"] = self.getSubPageURL(request, "forum_topic_new")


async def on_data_post(self, request):
    profile = self.getProfile(request)
    if profile is None:
        self.pageError(request, C.HTTP_FORBIDDEN)
    type_ = self.getPostedData(request, "type")
    if type_ == "new_topic":
        service, node, title, body = self.getPostedData(
            request, ("service", "node", "title", "body")
        )

        if not title or not body:
            self.pageError(request, C.HTTP_BAD_REQUEST)
        topic_data = {"title": title, "content": body}
        try:
            await self.host.bridgeCall(
                "forumTopicCreate", service, node, topic_data, profile
            )
        except Exception as e:
            if "forbidden" in str(e):
                self.pageError(request, 401)
            else:
                raise e
    else:
        log.warning(_("Unhandled data type: {}").format(type_))
