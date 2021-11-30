#!/usr/bin/env python3


from libervia.server.constants import Const as C
from twisted.internet import defer
from sat.core.i18n import _
from sat.core.log import getLogger

log = getLogger(__name__)

name = "photos"
access = C.PAGES_ACCESS_PROFILE
template = "photo/discover.html"


@defer.inlineCallbacks
def prepare_render(self, request):
    profile = self.getProfile(request)
    template_data = request.template_data
    namespace = self.host.ns_map["fis"]
    if profile is not None:
        try:
            interests = yield self.host.bridgeCall(
                "interestsList", "", "", namespace, profile)
        except Exception:
            log.warning(_("Can't get interests list for {profile}").format(
                profile=profile))
        else:
            # we only want photo albums
            filtered_interests = []
            for interest in interests:
                if interest.get('subtype') != 'photos':
                    continue
                path = interest.get('path', '')
                path_args = [p for p in path.split('/') if p]
                interest["url"] = self.getSubPageURL(
                    request,
                    "photos_album",
                    interest['service'],
                    *path_args
                )
                filtered_interests.append(interest)

            template_data['interests'] = filtered_interests

        template_data["url_photos_new"] = self.getSubPageURL(request, "photos_new")


@defer.inlineCallbacks
def on_data_post(self, request):
    jid_ = self.getPostedData(request, "jid")
    url = self.getPageByName("photos_album").getURL(jid_)
    self.HTTPRedirect(request, url)
