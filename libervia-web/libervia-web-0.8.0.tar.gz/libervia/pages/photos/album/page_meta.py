#!/usr/bin/env python3


from sat.core.i18n import D_
from sat.core.log import getLogger
from libervia.server.constants import Const as C

log = getLogger(__name__)

name = "photos_album"
label = D_("Photos Album")
access = C.PAGES_ACCESS_PROFILE
template = "photo/album.html"


def parse_url(self, request):
    self.getPathArgs(request, ["service", "*path"], min_args=1, service="jid", path="")


def prepare_render(self, request):
    data = self.getRData(request)
    data["thumb_limit"] = 800
    data["retrieve_comments"] = True
    files_page = self.getPageByName("files_list")
    return files_page.prepare_render(self, request)


def on_data_post(self, request):
    blog_page = self.getPageByName("blog_view")
    return blog_page.on_data_post(self, request)
