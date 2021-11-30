#!/usr/bin/env python3

from sat.core.i18n import _
from libervia.server.constants import Const as C
from twisted.words.protocols.jabber import jid
from twisted.internet import defer
from libervia.server import session_iface
from sat.tools.common import data_format
from sat.core.log import getLogger

log = getLogger(__name__)

name = "blog"
access = C.PAGES_ACCESS_PUBLIC
template = "blog/discover.html"


async def prepare_render(self, request):
    profile = self.getProfile(request)
    template_data = request.template_data
    if profile is not None:
        __, entities_own, entities_roster = await self.host.bridgeCall(
            "discoFindByFeatures",
            [],
            [("pubsub", "pep")],
            True,
            False,
            True,
            True,
            True,
            profile,
        )
        entities = template_data["disco_entities"] = (
            list(entities_own.keys()) + list(entities_roster.keys())
        )
        entities_url = template_data["entities_url"] = {}
        identities = self.host.getSessionData(
            request, session_iface.ISATSession
        ).identities
        d_list = {}
        for entity_jid_s in entities:
            entities_url[entity_jid_s] = self.getPageByName("blog_view").getURL(
                entity_jid_s
            )
            if entity_jid_s not in identities:
                d_list[entity_jid_s] = self.host.bridgeCall(
                        "identityGet",
                        entity_jid_s,
                        [],
                        True,
                        profile)
        identities_data = await defer.DeferredList(d_list.values())
        entities_idx = list(d_list.keys())
        for idx, (success, identity_raw) in enumerate(identities_data):
            entity_jid_s = entities_idx[idx]
            if not success:
                log.warning(_("Can't retrieve identity of {entity}")
                    .format(entity=entity_jid_s))
            else:
                identities[entity_jid_s] = data_format.deserialise(identity_raw)

        template_data["url_blog_edit"] = self.getSubPageURL(request, "blog_edit")


def on_data_post(self, request):
    jid_str = self.getPostedData(request, "jid")
    try:
        jid_ = jid.JID(jid_str)
    except RuntimeError:
        self.pageError(request, C.HTTP_BAD_REQUEST)
    url = self.getPageByName("blog_view").getURL(jid_.full())
    self.HTTPRedirect(request, url)
