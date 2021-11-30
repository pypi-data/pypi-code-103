#!/usr/bin/env python3

from libervia.server.constants import Const as C
from twisted.words.protocols.jabber import jid
from sat.core.i18n import _, D_
from sat.core.log import getLogger
from sat.tools.common import data_format

log = getLogger(__name__)

name = "lists_disco"
label = D_("Lists Discovery")
access = C.PAGES_ACCESS_PUBLIC
template = "list/discover.html"

async def prepare_render(self, request):
    profile = self.getProfile(request)
    template_data = request.template_data
    template_data["url_list_create"] = self.getPageByName("list_create").url
    lists_directory_config = self.host.options["lists_directory_json"]
    lists_directory = request.template_data["lists_directory"] = []

    if lists_directory_config:
        try:
            for list_data in lists_directory_config:
                service = list_data["service"]
                node = list_data["node"]
                name = list_data["name"]
                url = self.getPageByName("lists").getURL(service, node)
                lists_directory.append({"name": name, "url": url, "from_config": True})
        except KeyError as e:
            log.warning("Missing field in lists_directory_json: {msg}".format(msg=e))
        except Exception as e:
            log.warning("Can't decode lists directory: {msg}".format(msg=e))

    if profile is not None:
        try:
            lists_list_raw = await self.host.bridgeCall("listsList", "", "", profile)
        except Exception as e:
            log.warning(
                _("Can't get list of registered lists for {profile}: {reason}")
                .format(profile=profile, reason=e)
            )
        else:
            lists_list = data_format.deserialise(lists_list_raw, type_check=list)
            for list_data in lists_list:
                service = list_data["service"]
                node = list_data["node"]
                list_data["url"] = self.getPageByName("lists").getURL(service, node)
                list_data["from_config"] = False
                lists_directory.append(list_data)

    icons_names = set()
    for list_data in lists_directory:
        try:
            icons_names.add(list_data['icon_name'])
        except KeyError:
            pass
    if icons_names:
        template_data["icons_names"] = icons_names


def on_data_post(self, request):
    jid_str = self.getPostedData(request, "jid")
    try:
        jid_ = jid.JID(jid_str)
    except RuntimeError:
        self.pageError(request, C.HTTP_BAD_REQUEST)
    # for now we just use default node
    url = self.getPageByName("lists").getURL(jid_.full(), "@")
    self.HTTPRedirect(request, url)
