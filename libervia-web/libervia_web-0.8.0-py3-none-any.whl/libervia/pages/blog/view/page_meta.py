#!/usr/bin/env python3

import html
from libervia.server.constants import Const as C
from twisted.words.protocols.jabber import jid
from twisted.web import server
from sat.core.i18n import _, D_
from sat.tools.common.template import safe
from sat.tools.common import uri
from sat.tools.common import data_format
from sat.tools.common import regex
from sat.core.log import getLogger
from libervia.server import utils
from libervia.server.utils import SubPage

log = getLogger(__name__)

"""generic blog (with service/node provided)"""
name = 'blog_view'
template = "blog/articles.html"
uri_handlers = {('pubsub', 'microblog'): 'microblog_uri'}

URL_LIMIT_MARK = 90  # if canonical URL is longer than that, text will not be appended


def microblog_uri(self, uri_data):
    args = [uri_data['path'], uri_data['node']]
    if 'item' in uri_data:
        args.extend(['id', uri_data['item']])
    return self.getURL(*args)

def parse_url(self, request):
    """URL is /[service]/[node]/[filter_keyword]/[item]|[other]

    if [node] is '@', default namespace is used
    if a value is unset, default one will be used
    keyword can be one of:
        id: next value is a item id
        tag: next value is a blog tag
    """
    data = self.getRData(request)

    try:
        service = self.nextPath(request)
    except IndexError:
        data['service'] = ''
    else:
        try:
            data["service"] = jid.JID(service)
        except Exception:
            log.warning(_("bad service entered: {}").format(service))
            self.pageError(request, C.HTTP_BAD_REQUEST)

    try:
        node = self.nextPath(request)
    except IndexError:
        node = '@'
    data['node'] = '' if node == '@' else node

    try:
        filter_kw = data['filter_keyword'] = self.nextPath(request)
    except IndexError:
        filter_kw = '@'
    else:
        if filter_kw == '@':
            # No filter, this is used when a subpage is needed, notably Atom feed
            pass
        elif filter_kw == 'id':
            try:
                data['item'] = self.nextPath(request)
            except IndexError:
                self.pageError(request, C.HTTP_BAD_REQUEST)
            # we get one more argument in case text has been added to have a nice URL
            try:
                self.nextPath(request)
            except IndexError:
                pass
        elif filter_kw == 'tag':
            try:
                data['tag'] = self.nextPath(request)
            except IndexError:
                self.pageError(request, C.HTTP_BAD_REQUEST)
        else:
            # invalid filter keyword
            log.warning(_("invalid filter keyword: {filter_kw}").format(
                filter_kw=filter_kw))
            self.pageError(request, C.HTTP_BAD_REQUEST)

    # if URL is parsed here, we'll have atom.xml available and we need to
    # add the link to the page
    atom_url = self.getURLByPath(
        SubPage('blog_view'),
        service,
        node,
        filter_kw,
        SubPage('blog_feed_atom'),
    )
    request.template_data['atom_url'] = atom_url
    request.template_data.setdefault('links', []).append({
        "href": atom_url,
        "type": "application/atom+xml",
        "rel": "alternate",
        "title": "{service}'s blog".format(service=service)})


def add_breadcrumb(self, request, breadcrumbs):
    data = self.getRData(request)
    breadcrumbs.append({
        "label": D_("Feed"),
        "url": self.getURL(data["service"].full(), data.get("node", "@"))
    })
    if "item" in data:
        breadcrumbs.append({
            "label": D_("Post"),
        })


async def appendComments(self, request, blog_items, profile):
    await self.fillMissingIdentities(
        request, [i['author_jid'] for i in blog_items['items']])
    for blog_item in blog_items['items']:
        for comment_data in blog_item['comments']:
            service = comment_data['service']
            node = comment_data['node']
            try:
                comments_data = await self.host.bridgeCall('mbGet',
                                      service,
                                      node,
                                      C.NO_LIMIT,
                                      [],
                                      {C.KEY_ORDER_BY: C.ORDER_BY_CREATION},
                                      profile)
            except Exception as e:
                log.warning(
                    _("Can't get comments at {node} (service: {service}): {msg}").format(
                        service=service,
                        node=node,
                        msg=e))
                comment_data['items'] = []
                continue

            comments = data_format.deserialise(comments_data)
            comment_data['items'] = comments['items']
            await appendComments(self, request, comments, profile)

async def getBlogItems(
    self,
    request: server.Request,
    service: jid.JID,
    node: str,
    item_id,
    extra: dict,
    profile: str
) -> dict:
    try:
        if item_id:
            items_id = [item_id]
        else:
            items_id = []
        blog_data = await self.host.bridgeCall('mbGet',
                              service.userhost(),
                              node,
                              C.NO_LIMIT,
                              items_id,
                              extra,
                              profile)
    except Exception as e:
        # FIXME: need a better way to test errors in bridge errback
        if "forbidden" in str(e):
            self.pageError(request, 401)
        else:
            log.warning(_("can't retrieve blog for [{service}]: {msg}".format(
                service = service.userhost(), msg=e)))
            blog_data = {"items": []}
    else:
        blog_data = data_format.deserialise(blog_data)

    return blog_data

async def prepare_render(self, request):
    data = self.getRData(request)
    template_data = request.template_data
    page_max = data.get("page_max", 10)
    # if the comments are not explicitly hidden, we show them
    service, node, item_id, show_comments = (
        data.get('service', ''),
        data.get('node', ''),
        data.get('item'),
        data.get('show_comments', True)
    )
    profile = self.getProfile(request)
    if profile is None:
        profile = C.SERVICE_PROFILE
        profile_connected = False
    else:
        profile_connected = True

    ## pagination/filtering parameters
    if item_id:
        extra = {}
    else:
        extra = self.getPubsubExtra(request, page_max=page_max)
        tag = data.get('tag')
        if tag:
            extra[f'mam_filter_{C.MAM_FILTER_CATEGORY}'] = tag
        self.handleSearch(request, extra)

    ## main data ##
    # we get data from backend/XMPP here
    blog_items = await getBlogItems(self, request, service, node, item_id, extra, profile)

    ## navigation ##
    # no let's fill service, node and pagination URLs
    if 'service' not in template_data:
        template_data['service'] = service
    if 'node' not in template_data:
        template_data['node'] = node
    target_profile = template_data.get('target_profile')

    if blog_items:
        if item_id:
            template_data["previous_page_url"] = self.getURL(
                service.full(),
                node,
                before=item_id,
                page_max=1
            )
            template_data["next_page_url"] = self.getURL(
                service.full(),
                node,
                after=item_id,
                page_max=1
            )
            blog_items["rsm"] = {
                "last": item_id,
                "first": item_id,
            }
            blog_items["complete"] = False
        else:
            self.setPagination(request, blog_items)
    else:
        if item_id:
            # if item id has been specified in URL and it's not found,
            # we must return an error
            self.pageError(request, C.HTTP_NOT_FOUND)

    ## identities ##
    # identities are used to show nice nickname or avatars
    await self.fillMissingIdentities(request, [i['author_jid'] for i in blog_items['items']])

    ## Comments ##
    # if comments are requested, we need to take them
    if show_comments:
        await appendComments(self, request, blog_items, profile)

    ## URLs ##
    # We will fill items_http_uri and tags_http_uri in template_data with suitable urls
    # if we know the profile, we use it instead of service + blog (nicer url)
    if target_profile is None:
        blog_base_url_item = self.getPageByName('blog_view').getURL(service.full(), node or '@', 'id')
        blog_base_url_tag = self.getPageByName('blog_view').getURL(service.full(), node or '@', 'tag')
    else:
        blog_base_url_item = self.getURLByNames([('user', [target_profile]), ('user_blog', ['id'])])
        blog_base_url_tag = self.getURLByNames([('user', [target_profile]), ('user_blog', ['tag'])])
        # we also set the background image if specified by user
        bg_img = await self.host.bridgeCall('asyncGetParamA', 'Background', 'Blog page', 'value', -1, template_data['target_profile'])
        if bg_img:
            template_data['dynamic_style'] = safe("""
                :root {
                    --bg-img: url("%s");
                }
                """ % html.escape(bg_img, True))

    template_data['blog_items'] = data['blog_items'] = blog_items
    if request.args.get(b'reverse') == ['1']:
        template_data['blog_items'].items.reverse()
    template_data['items_http_uri'] = items_http_uri = {}
    template_data['tags_http_uri'] = tags_http_uri = {}


    for item in blog_items['items']:
        blog_canonical_url = '/'.join([blog_base_url_item, utils.quote(item['id'])])
        if len(blog_canonical_url) > URL_LIMIT_MARK:
            blog_url = blog_canonical_url
        elif '-' not in item['id']:
            # we add text from title or body at the end of URL
            # to make it more human readable
            # we do it only if there is no "-", as a "-" probably means that
            # item's id is already user friendly.
            # TODO: to be removed,  this is only kept for a transition period until
            #   user friendly item IDs are more common.
            text = regex.urlFriendlyText(item.get('title', item['content']))
            if text:
                blog_url = blog_canonical_url + '/' + text
            else:
                blog_url = blog_canonical_url
        else:
            blog_url = blog_canonical_url

        items_http_uri[item['id']] = self.host.getExtBaseURL(request, blog_url)
        for tag in item['tags']:
            if tag not in tags_http_uri:
                tag_url = '/'.join([blog_base_url_tag, utils.quote(tag)])
                tags_http_uri[tag] = self.host.getExtBaseURL(request, tag_url)

    # if True, page should display a comment box
    template_data['allow_commenting'] = data.get('allow_commenting', profile_connected)

    # last but not least, we add a xmpp: link to the node
    uri_args = {'path': service.full()}
    if node:
        uri_args['node'] = node
    if item_id:
        uri_args['item'] = item_id
    template_data['xmpp_uri'] = uri.buildXMPPUri(
        'pubsub', subtype='microblog', **uri_args
    )


async def on_data_post(self, request):
    profile = self.getProfile(request)
    if profile is None:
        self.pageError(request, C.HTTP_FORBIDDEN)
    type_ = self.getPostedData(request, 'type')
    if type_ == 'comment':
        service, node, body = self.getPostedData(request, ('service', 'node', 'body'))

        if not body:
            self.pageError(request, C.HTTP_BAD_REQUEST)
        comment_data = {"content_rich": body}
        try:
            await self.host.bridgeCall('mbSend',
                                       service,
                                       node,
                                       data_format.serialise(comment_data),
                                       profile)
        except Exception as e:
            if "forbidden" in str(e):
                self.pageError(request, 401)
            else:
                raise e
    else:
        log.warning(_("Unhandled data type: {}").format(type_))
