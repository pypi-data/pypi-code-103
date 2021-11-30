#!/usr/bin/env python3


from libervia.server.constants import Const as C
from sat.core.i18n import _, D_
from sat.core.log import getLogger
from sat.tools.common import data_format

log = getLogger(__name__)

name = "forum_view"
label = D_("View")
access = C.PAGES_ACCESS_PUBLIC
template = "forum/view.html"


def parse_url(self, request):
    self.getPathArgs(request, ["service", "node"], 2, service="jid")


async def prepare_render(self, request):
    data = self.getRData(request)
    data["show_comments"] = False
    blog_page = self.getPageByName("blog_view")
    request.args[b"before"] = [b""]
    request.args[b"reverse"] = [b"1"]
    await blog_page.prepare_render(self, request)
    request.template_data["login_url"] = self.getPageRedirectURL(request)


async def on_data_post(self, request):
    profile = self.getProfile(request)
    if profile is None:
        self.pageError(request, C.HTTP_FORBIDDEN)
    type_ = self.getPostedData(request, "type")
    if type_ == "comment":
        service, node, body = self.getPostedData(request, ("service", "node", "body"))

        if not body:
            self.pageError(request, C.HTTP_BAD_REQUEST)
        mb_data = {"content_rich": body}
        try:
            await self.host.bridgeCall(
                "mbSend", service, node, data_format.serialise(mb_data), profile)
        except Exception as e:
            if "forbidden" in str(e):
                self.pageError(request, 401)
            else:
                raise e
    else:
        log.warning(_("Unhandled data type: {}").format(type_))
