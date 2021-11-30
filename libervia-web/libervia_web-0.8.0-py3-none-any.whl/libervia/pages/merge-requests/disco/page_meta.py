#!/usr/bin/env python3


from libervia.server.constants import Const as C
from twisted.words.protocols.jabber import jid
from sat.core.log import getLogger

log = getLogger(__name__)


name = "merge-requests_disco"
access = C.PAGES_ACCESS_PUBLIC
template = "merge-request/discover.html"


def prepare_render(self, request):
    mr_handlers_config = self.host.options["mr_handlers_json"]
    if mr_handlers_config:
        handlers = request.template_data["mr_handlers"] = []
        try:
            for handler_data in mr_handlers_config:
                service = handler_data["service"]
                node = handler_data["node"]
                name = handler_data["name"]
                url = self.getPageByName("merge-requests").getURL(service, node)
                handlers.append({"name": name, "url": url})
        except KeyError as e:
            log.warning("Missing field in mr_handlers_json: {msg}".format(msg=e))
        except Exception as e:
            log.warning("Can't decode mr handlers: {msg}".format(msg=e))


def on_data_post(self, request):
    jid_str = self.getPostedData(request, "jid")
    try:
        jid_ = jid.JID(jid_str)
    except RuntimeError:
        self.pageError(request, C.HTTP_BAD_REQUEST)
    # for now we just use default node
    url = self.getPageByName("merge-requests").getURL(jid_.full(), "@")
    self.HTTPRedirect(request, url)
