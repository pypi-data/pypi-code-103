#!/usr/bin/env python3

from libervia.server.constants import Const as C
from sat.core.log import getLogger
from sat.tools.common import data_format

log = getLogger(__name__)

name = "blog_edit"
access = C.PAGES_ACCESS_PROFILE
template = "blog/publish.html"


async def on_data_post(self, request):
    profile = self.getProfile(request)
    if profile is None:
        self.pageError(request, C.HTTP_FORBIDDEN)
    request_data = self.getRData(request)
    title, tags, body = self.getPostedData(request, ('title', 'tags', 'body'))
    mb_data = {"content_rich": body}
    title = title.strip()
    if title:
        mb_data["title_rich"] = title
    tags = [t.strip() for t in tags.split(',') if t.strip()]
    if tags:
        mb_data["tags"] = tags

    await self.host.bridgeCall(
        'mbSend',
        "",
        "",
        data_format.serialise(mb_data),
        profile
    )

    request_data["post_redirect_page"] = self.getPageByName("blog")
