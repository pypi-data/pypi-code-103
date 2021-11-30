#!/usr/bin/env python3


from libervia.server.constants import Const as C
from sat.core.i18n import D_
from sat.core.log import getLogger

log = getLogger(__name__)

name = "forum_topic_new"
label = D_("New Topic")
access = C.PAGES_ACCESS_PROFILE
template = "blog/publish.html"


async def prepare_render(self, request):
   template_data = request.template_data
   template_data.update({
       "post_form_id": "forum_topic_edit",
       "publish_title": D_("New Forum Topic"),
       "title_label": D_("Topic"),
       "title_required": True,
       "body_label": D_("Message"),
       "no_tabs": True,
   })


async def on_data_post(self, request):
    profile = self.getProfile(request)
    if profile is None:
        self.pageError(request, C.HTTP_FORBIDDEN)
    rdata = self.getRData(request)
    service = rdata["service"].full() if rdata["service"] else ""
    node = rdata["node"]
    title, body = self.getPostedData(request, ("title", "body"))
    title = title.strip()
    body = body.strip()
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

    rdata["post_redirect_page"] = (self.getPageByName("forum_topics"), service, node)
