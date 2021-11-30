#!/usr/bin/env python3


from libervia.server.constants import Const as C
from twisted.internet import defer
from twisted.words.protocols.jabber import jid

"""page used to target a user profile, e.g. for public blog"""

name = "user"
access = C.PAGES_ACCESS_PUBLIC  # can be a callable
template = "blog/articles.html"
url_cache = True


@defer.inlineCallbacks
def parse_url(self, request):
    try:
        prof_requested = self.nextPath(request)
    except IndexError:
        self.pageError(request)

    data = self.getRData(request)

    target_profile = yield self.host.bridgeCall("profileNameGet", prof_requested)
    request.template_data["target_profile"] = target_profile
    target_jid = yield self.host.bridgeCall(
        "asyncGetParamA", "JabberID", "Connection", "value", profile_key=target_profile
    )
    target_jid = jid.JID(target_jid)
    data["service"] = target_jid

    # if URL is parsed here, we'll have atom.xml available and we need to
    # add the link to the page
    atom_url = self.getSubPageURL(request, 'user_blog_feed_atom')
    request.template_data['atom_url'] = atom_url
    request.template_data.setdefault('links', []).append({
        "href": atom_url,
        "type": "application/atom+xml",
        "rel": "alternate",
        "title": "{target_profile}'s blog".format(target_profile=target_profile)})

def add_breadcrumb(self, request, breadcrumbs):
    # we don't want a breadcrumb here
    pass


@defer.inlineCallbacks
def prepare_render(self, request):
    data = self.getRData(request)
    self.checkCache(
        request, C.CACHE_PUBSUB, service=data["service"], node=None, short="microblog"
    )
    self.pageRedirect("blog_view", request)

def on_data_post(self, request):
    return self.getPageByName("blog_view").on_data_post(self, request)
