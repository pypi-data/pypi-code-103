#!/usr/bin/env python3

from sat.core.log import getLogger
from sat.core import exceptions
from libervia.server.constants import Const as C

log = getLogger(__name__)

name = "embed_app"
template = "embed/embed.html"


def parse_url(self, request):
    self.getPathArgs(request, ["app_name"], min_args=1)
    data = self.getRData(request)
    app_name = data["app_name"]
    try:
        app_data = self.vhost_root.libervia_apps[app_name]
    except KeyError:
        self.pageError(request, C.HTTP_BAD_REQUEST)
    template_data = request.template_data
    template_data['full_screen_body'] = True
    try:
        template_data["target_url"] = app_data["url_prefix"]
    except KeyError:
        raise exceptions.InternalError(f'"url_prefix" is missing for {app_name!r}')
