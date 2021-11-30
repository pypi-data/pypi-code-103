#!/usr/bin/env python3

# SAT plugin for microblogging over XMPP (xep-0277)
# Copyright (C) 2009-2021 Jérôme Poisson (goffi@goffi.org)

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import time
import dateutil
import calendar
from secrets import token_urlsafe
from typing import Optional
from functools import partial

import shortuuid

from twisted.words.protocols.jabber import jid, error
from twisted.words.protocols.jabber.xmlstream import XMPPHandler
from twisted.words.xish import domish
from twisted.internet import defer
from twisted.python import failure

# XXX: sat_tmp.wokkel.pubsub is actually used instead of wokkel version
from wokkel import pubsub
from wokkel import disco, iwokkel
from zope.interface import implementer

from sat.core.i18n import _
from sat.core.constants import Const as C
from sat.core.log import getLogger
from sat.core import exceptions
from sat.core.xmpp import SatXMPPEntity
from sat.tools import xml_tools
from sat.tools import sat_defer
from sat.tools import utils
from sat.tools.common import data_format
from sat.tools.common import uri as xmpp_uri
from sat.tools.common import regex


log = getLogger(__name__)


NS_MICROBLOG = "urn:xmpp:microblog:0"
NS_ATOM = "http://www.w3.org/2005/Atom"
NS_PUBSUB_EVENT = "{}{}".format(pubsub.NS_PUBSUB, "#event")
NS_COMMENT_PREFIX = "{}:comments/".format(NS_MICROBLOG)


PLUGIN_INFO = {
    C.PI_NAME: "Microblogging over XMPP Plugin",
    C.PI_IMPORT_NAME: "XEP-0277",
    C.PI_TYPE: "XEP",
    C.PI_PROTOCOLS: ["XEP-0277"],
    C.PI_DEPENDENCIES: ["XEP-0163", "XEP-0060", "TEXT_SYNTAXES"],
    C.PI_RECOMMENDATIONS: ["XEP-0059", "EXTRA-PEP"],
    C.PI_MAIN: "XEP_0277",
    C.PI_HANDLER: "yes",
    C.PI_DESCRIPTION: _("""Implementation of microblogging Protocol"""),
}


class NodeAccessChangeException(Exception):
    pass


class XEP_0277(object):
    namespace = NS_MICROBLOG

    def __init__(self, host):
        log.info(_("Microblogging plugin initialization"))
        self.host = host
        host.registerNamespace("microblog", NS_MICROBLOG)
        self._p = self.host.plugins[
            "XEP-0060"
        ]  # this facilitate the access to pubsub plugin
        self.rt_sessions = sat_defer.RTDeferredSessions()
        self.host.plugins["XEP-0060"].addManagedNode(
            NS_MICROBLOG, items_cb=self._itemsReceived
        )

        host.bridge.addMethod(
            "mbSend",
            ".plugin",
            in_sign="ssss",
            out_sign="",
            method=self._mbSend,
            async_=True,
        )
        host.bridge.addMethod(
            "mbPreview",
            ".plugin",
            in_sign="ssss",
            out_sign="s",
            method=self._mbPreview,
            async_=True,
        )
        host.bridge.addMethod(
            "mbRetract",
            ".plugin",
            in_sign="ssss",
            out_sign="",
            method=self._mbRetract,
            async_=True,
        )
        host.bridge.addMethod(
            "mbGet",
            ".plugin",
            in_sign="ssiasa{ss}s",
            out_sign="s",
            method=self._mbGet,
            async_=True,
        )
        host.bridge.addMethod(
            "mbRename",
            ".plugin",
            in_sign="sssss",
            out_sign="",
            method=self._mbRename,
            async_=True,
        )
        host.bridge.addMethod(
            "mbSetAccess",
            ".plugin",
            in_sign="ss",
            out_sign="",
            method=self.mbSetAccess,
            async_=True,
        )
        host.bridge.addMethod(
            "mbSubscribeToMany",
            ".plugin",
            in_sign="sass",
            out_sign="s",
            method=self._mbSubscribeToMany,
        )
        host.bridge.addMethod(
            "mbGetFromManyRTResult",
            ".plugin",
            in_sign="ss",
            out_sign="(ua(sssasa{ss}))",
            method=self._mbGetFromManyRTResult,
            async_=True,
        )
        host.bridge.addMethod(
            "mbGetFromMany",
            ".plugin",
            in_sign="sasia{ss}s",
            out_sign="s",
            method=self._mbGetFromMany,
        )
        host.bridge.addMethod(
            "mbGetFromManyWithCommentsRTResult",
            ".plugin",
            in_sign="ss",
            out_sign="(ua(sssa(sa(sssasa{ss}))a{ss}))",
            method=self._mbGetFromManyWithCommentsRTResult,
            async_=True,
        )
        host.bridge.addMethod(
            "mbGetFromManyWithComments",
            ".plugin",
            in_sign="sasiia{ss}a{ss}s",
            out_sign="s",
            method=self._mbGetFromManyWithComments,
        )

    def getHandler(self, client):
        return XEP_0277_handler()

    def _checkFeaturesCb(self, available):
        return {"available": C.BOOL_TRUE}

    def _checkFeaturesEb(self, fail):
        return {"available": C.BOOL_FALSE}

    def getFeatures(self, profile):
        client = self.host.getClient(profile)
        d = self.host.checkFeatures(client, [], identity=("pubsub", "pep"))
        d.addCallbacks(self._checkFeaturesCb, self._checkFeaturesEb)
        return d

    ## plugin management methods ##

    def _itemsReceived(self, client, itemsEvent):
        """Callback which manage items notifications (publish + retract)"""

        def manageItem(data, event):
            self.host.bridge.psEvent(
                C.PS_MICROBLOG,
                itemsEvent.sender.full(),
                itemsEvent.nodeIdentifier,
                event,
                data_format.serialise(data),
                client.profile,
            )

        for item in itemsEvent.items:
            if item.name == C.PS_ITEM:
                # FIXME: service and node should be used here
                self.item2mbdata(client, item, None, None).addCallbacks(
                    manageItem, lambda failure: None, (C.PS_PUBLISH,)
                )
            elif item.name == C.PS_RETRACT:
                manageItem({"id": item["id"]}, C.PS_RETRACT)
            else:
                raise exceptions.InternalError("Invalid event value")

    ## data/item transformation ##

    @defer.inlineCallbacks
    def item2mbdata(
        self,
        client: SatXMPPEntity,
        item_elt: domish.Element,
        service: Optional[jid.JID],
        # FIXME: node is Optional until all calls to item2mbdata set properly service
        #   and node. Once done, the Optional must be removed here
        node: Optional[str]
    ) -> dict:
        """Convert an XML Item to microblog data

        @param item_elt: microblog item element
        @param service: PubSub service where the item has been retrieved
            profile's PEP is used when service is None
        @param node: PubSub node where the item has been retrieved
            if None, "uri" won't be set
        @return: microblog data
        """
        microblog_data = {}

        def check_conflict(key, increment=False):
            """Check if key is already in microblog data

            @param key(unicode): key to check
            @param increment(bool): if suffix the key with an increment
                instead of raising an exception
            @raise exceptions.DataError: the key already exists
                (not raised if increment is True)
            """
            if key in microblog_data:
                if not increment:
                    raise failure.Failure(
                        exceptions.DataError(
                            "key {} is already present for item {}"
                        ).format(key, item_elt["id"])
                    )
                else:
                    idx = 1  # the idx 0 is the key without suffix
                    fmt = "{}#{}"
                    new_key = fmt.format(key, idx)
                    while new_key in microblog_data:
                        idx += 1
                        new_key = fmt.format(key, idx)
                    key = new_key
            return key

        @defer.inlineCallbacks
        def parseElement(elem):
            """Parse title/content elements and fill microblog_data accordingly"""
            type_ = elem.getAttribute("type")
            if type_ == "xhtml":
                data_elt = elem.firstChildElement()
                if data_elt is None:
                    raise failure.Failure(
                        exceptions.DataError(
                            "XHML content not wrapped in a <div/> element, this is not "
                            "standard !"
                        )
                    )
                if data_elt.uri != C.NS_XHTML:
                    raise failure.Failure(
                        exceptions.DataError(
                            _("Content of type XHTML must declare its namespace!")
                        )
                    )
                key = check_conflict("{}_xhtml".format(elem.name))
                data = data_elt.toXml()
                microblog_data[key] = yield self.host.plugins["TEXT_SYNTAXES"].cleanXHTML(
                    data
                )
            else:
                key = check_conflict(elem.name)
                microblog_data[key] = str(elem)

        id_ = item_elt.getAttribute("id", "")  # there can be no id for transient nodes
        microblog_data["id"] = id_
        if item_elt.uri not in (pubsub.NS_PUBSUB, NS_PUBSUB_EVENT):
            msg = "Unsupported namespace {ns} in pubsub item {id_}".format(
                ns=item_elt.uri, id_=id_
            )
            log.warning(msg)
            raise failure.Failure(exceptions.DataError(msg))

        try:
            entry_elt = next(item_elt.elements(NS_ATOM, "entry"))
        except StopIteration:
            msg = "No atom entry found in the pubsub item {}".format(id_)
            raise failure.Failure(exceptions.DataError(msg))

        # uri
        # FIXME: node should alway be set in the future, check FIXME in method signature
        if node is not None:
            microblog_data['uri'] = xmpp_uri.buildXMPPUri(
                "pubsub",
                path=service.full() if service is not None else client.jid.userhost(),
                node=node,
                item=id_,
            )

        # language
        try:
            microblog_data["language"] = entry_elt[(C.NS_XML, "lang")].strip()
        except KeyError:
            pass

        # atom:id
        try:
            id_elt = next(entry_elt.elements(NS_ATOM, "id"))
        except StopIteration:
            msg = ("No atom id found in the pubsub item {}, this is not standard !"
                   .format(id_))
            log.warning(msg)
            microblog_data["atom_id"] = ""
        else:
            microblog_data["atom_id"] = str(id_elt)

        # title/content(s)

        # FIXME: ATOM and XEP-0277 only allow 1 <title/> element
        #        but in the wild we have some blogs with several ones
        #        so we don't respect the standard for now (it doesn't break
        #        anything anyway), and we'll find a better option later
        # try:
        #     title_elt = entry_elt.elements(NS_ATOM, 'title').next()
        # except StopIteration:
        #     msg = u'No atom title found in the pubsub item {}'.format(id_)
        #     raise failure.Failure(exceptions.DataError(msg))
        title_elts = list(entry_elt.elements(NS_ATOM, "title"))
        if not title_elts:
            msg = "No atom title found in the pubsub item {}".format(id_)
            raise failure.Failure(exceptions.DataError(msg))
        for title_elt in title_elts:
            yield parseElement(title_elt)

        # FIXME: as for <title/>, Atom only authorise at most 1 content
        #        but XEP-0277 allows several ones. So for no we handle as
        #        if more than one can be present
        for content_elt in entry_elt.elements(NS_ATOM, "content"):
            yield parseElement(content_elt)

        # we check that text content is present
        for key in ("title", "content"):
            if key not in microblog_data and ("{}_xhtml".format(key)) in microblog_data:
                log.warning(
                    "item {id_} provide a {key}_xhtml data but not a text one".format(
                        id_=id_, key=key
                    )
                )
                # ... and do the conversion if it's not
                microblog_data[key] = yield self.host.plugins["TEXT_SYNTAXES"].convert(
                    microblog_data["{}_xhtml".format(key)],
                    self.host.plugins["TEXT_SYNTAXES"].SYNTAX_XHTML,
                    self.host.plugins["TEXT_SYNTAXES"].SYNTAX_TEXT,
                    False,
                )

        if "content" not in microblog_data:
            # use the atom title data as the microblog body content
            microblog_data["content"] = microblog_data["title"]
            del microblog_data["title"]
            if "title_xhtml" in microblog_data:
                microblog_data["content_xhtml"] = microblog_data["title_xhtml"]
                del microblog_data["title_xhtml"]

        # published/updated dates
        try:
            updated_elt = next(entry_elt.elements(NS_ATOM, "updated"))
        except StopIteration:
            msg = "No atom updated element found in the pubsub item {}".format(id_)
            raise failure.Failure(exceptions.DataError(msg))
        microblog_data["updated"] = calendar.timegm(
            dateutil.parser.parse(str(updated_elt)).utctimetuple()
        )
        try:
            published_elt = next(entry_elt.elements(NS_ATOM, "published"))
        except StopIteration:
            microblog_data["published"] = microblog_data["updated"]
        else:
            microblog_data["published"] = calendar.timegm(
                dateutil.parser.parse(str(published_elt)).utctimetuple()
            )

        # links
        comments = microblog_data['comments'] = []
        for link_elt in entry_elt.elements(NS_ATOM, "link"):
            if (
                link_elt.getAttribute("rel") == "replies"
                and link_elt.getAttribute("title") == "comments"
            ):
                uri = link_elt["href"]
                comments_data = {
                    "uri": uri,
                }
                try:
                    service, node = self.parseCommentUrl(uri)
                except Exception as e:
                    log.warning(f"Can't parse comments url: {e}")
                    continue
                else:
                    comments_data["service"] = service.full()
                    comments_data["node"] = node
                comments.append(comments_data)
            else:
                rel = link_elt.getAttribute("rel", "")
                title = link_elt.getAttribute("title", "")
                href = link_elt.getAttribute("href", "")
                log.warning(
                    "Unmanaged link element: rel={rel} title={title} href={href}".format(
                        rel=rel, title=title, href=href
                    )
                )

        # author
        publisher = item_elt.getAttribute("publisher")
        try:
            author_elt = next(entry_elt.elements(NS_ATOM, "author"))
        except StopIteration:
            log.debug("Can't find author element in item {}".format(id_))
        else:
            # name
            try:
                name_elt = next(author_elt.elements(NS_ATOM, "name"))
            except StopIteration:
                log.warning(
                    "No name element found in author element of item {}".format(id_)
                )
            else:
                author = microblog_data["author"] = str(name_elt).strip()
            # uri
            try:
                uri_elt = next(author_elt.elements(NS_ATOM, "uri"))
            except StopIteration:
                log.debug(
                    "No uri element found in author element of item {}".format(id_)
                )
                if publisher:
                    microblog_data["author_jid"] = publisher
            else:
                uri = str(uri_elt)
                if uri.startswith("xmpp:"):
                    uri = uri[5:]
                    microblog_data["author_jid"] = uri
                else:
                    microblog_data["author_jid"] = (
                        item_elt.getAttribute("publisher") or ""
                    )
                if not author and microblog_data["author_jid"]:
                    # FIXME: temporary workaround for missing author name, would be
                    #   better to use directly JID's identity (to be done from frontends?)
                    try:
                        microblog_data["author"] = jid.JID(microblog_data["author_jid"]).user
                    except Exception as e:
                        log.warning(f"No author name found, and can't parse author jid: {e}")

                if not publisher:
                    log.debug("No publisher attribute, we can't verify author jid")
                    microblog_data["author_jid_verified"] = False
                elif jid.JID(publisher).userhostJID() == jid.JID(uri).userhostJID():
                    microblog_data["author_jid_verified"] = True
                else:
                    log.warning(
                        "item atom:uri differ from publisher attribute, spoofing "
                        "attempt ? atom:uri = {} publisher = {}".format(
                            uri, item_elt.getAttribute("publisher")
                        )
                    )
                    microblog_data["author_jid_verified"] = False
            # email
            try:
                email_elt = next(author_elt.elements(NS_ATOM, "email"))
            except StopIteration:
                pass
            else:
                microblog_data["author_email"] = str(email_elt)

        if not microblog_data.get("author_jid"):
            if publisher:
                microblog_data["author_jid"] = publisher
                microblog_data["author_jid_verified"] = True
            else:
                iq_elt = xml_tools.findAncestor(item_elt, "iq", C.NS_CLIENT)
                microblog_data["author_jid"] = iq_elt["from"]
                microblog_data["author_jid_verified"] = False

        # categories
        categories = [
            category_elt.getAttribute("term", "")
            for category_elt in entry_elt.elements(NS_ATOM, "category")
        ]
        microblog_data["tags"] = categories

        ## the trigger ##
        # if other plugins have things to add or change
        yield self.host.trigger.point(
            "XEP-0277_item2data", item_elt, entry_elt, microblog_data
        )

        defer.returnValue(microblog_data)

    @defer.inlineCallbacks
    def data2entry(self, client, data, item_id, service, node):
        """Convert a data dict to en entry usable to create an item

        @param data: data dict as given by bridge method.
        @param item_id(unicode): id of the item to use
        @param service(jid.JID, None): pubsub service where the item is sent
            Needed to construct Atom id
        @param node(unicode): pubsub node where the item is sent
            Needed to construct Atom id
        @return: deferred which fire domish.Element
        """
        entry_elt = domish.Element((NS_ATOM, "entry"))

        ## language ##
        if "language" in data:
            entry_elt[(C.NS_XML, "lang")] = data["language"].strip()

        ## content and title ##
        synt = self.host.plugins["TEXT_SYNTAXES"]

        for elem_name in ("title", "content"):
            for type_ in ["", "_rich", "_xhtml"]:
                attr = "{}{}".format(elem_name, type_)
                if attr in data:
                    elem = entry_elt.addElement(elem_name)
                    if type_:
                        if type_ == "_rich":  # convert input from current syntax to XHTML
                            xml_content = yield synt.convert(
                                data[attr], synt.getCurrentSyntax(client.profile), "XHTML"
                            )
                            if "{}_xhtml".format(elem_name) in data:
                                raise failure.Failure(
                                    exceptions.DataError(
                                        _(
                                            "Can't have xhtml and rich content at the same time"
                                        )
                                    )
                                )
                        else:
                            xml_content = data[attr]

                        div_elt = xml_tools.ElementParser()(
                            xml_content, namespace=C.NS_XHTML
                        )
                        if (
                            div_elt.name != "div"
                            or div_elt.uri != C.NS_XHTML
                            or div_elt.attributes
                        ):
                            # we need a wrapping <div/> at the top with XHTML namespace
                            wrap_div_elt = domish.Element((C.NS_XHTML, "div"))
                            wrap_div_elt.addChild(div_elt)
                            div_elt = wrap_div_elt
                        elem.addChild(div_elt)
                        elem["type"] = "xhtml"
                        if elem_name not in data:
                            # there is raw text content, which is mandatory
                            # so we create one from xhtml content
                            elem_txt = entry_elt.addElement(elem_name)
                            text_content = yield self.host.plugins[
                                "TEXT_SYNTAXES"
                            ].convert(
                                xml_content,
                                self.host.plugins["TEXT_SYNTAXES"].SYNTAX_XHTML,
                                self.host.plugins["TEXT_SYNTAXES"].SYNTAX_TEXT,
                                False,
                            )
                            elem_txt.addContent(text_content)
                            elem_txt["type"] = "text"

                    else:  # raw text only needs to be escaped to get HTML-safe sequence
                        elem.addContent(data[attr])
                        elem["type"] = "text"

        try:
            next(entry_elt.elements(NS_ATOM, "title"))
        except StopIteration:
            # we have no title element which is mandatory
            # so we transform content element to title
            elems = list(entry_elt.elements(NS_ATOM, "content"))
            if not elems:
                raise exceptions.DataError(
                    "There must be at least one content or title element"
                )
            for elem in elems:
                elem.name = "title"

        ## author ##
        author_elt = entry_elt.addElement("author")
        try:
            author_name = data["author"]
        except KeyError:
            # FIXME: must use better name
            author_name = client.jid.user
        author_elt.addElement("name", content=author_name)

        try:
            author_jid_s = data["author_jid"]
        except KeyError:
            author_jid_s = client.jid.userhost()
        author_elt.addElement("uri", content="xmpp:{}".format(author_jid_s))

        try:
            author_jid_s = data["author_email"]
        except KeyError:
            pass

        ## published/updated time ##
        current_time = time.time()
        entry_elt.addElement(
            "updated", content=utils.xmpp_date(float(data.get("updated", current_time)))
        )
        entry_elt.addElement(
            "published",
            content=utils.xmpp_date(float(data.get("published", current_time))),
        )

        ## categories ##
        for tag in data.get('tags', []):
            category_elt = entry_elt.addElement("category")
            category_elt["term"] = tag

        ## id ##
        entry_id = data.get(
            "id",
            xmpp_uri.buildXMPPUri(
                "pubsub",
                path=service.full() if service is not None else client.jid.userhost(),
                node=node,
                item=item_id,
            ),
        )
        entry_elt.addElement("id", content=entry_id)  #

        ## comments ##
        for comments_data in data.get('comments', []):
            link_elt = entry_elt.addElement("link")
            # XXX: "uri" is set in self._manageComments if not already existing
            link_elt["href"] = comments_data["uri"]
            link_elt["rel"] = "replies"
            link_elt["title"] = "comments"

        ## final item building ##
        item_elt = pubsub.Item(id=item_id, payload=entry_elt)

        ## the trigger ##
        # if other plugins have things to add or change
        yield self.host.trigger.point(
            "XEP-0277_data2entry", client, data, entry_elt, item_elt
        )

        defer.returnValue(item_elt)

    ## publish/preview ##

    def getCommentsNode(self, item_id):
        """Generate comment node

        @param item_id(unicode): id of the parent item
        @return (unicode): comment node to use
        """
        return "{}{}".format(NS_COMMENT_PREFIX, item_id)

    def getCommentsService(self, client, parent_service=None):
        """Get prefered PubSub service to create comment node

        @param pubsub_service(jid.JID, None): PubSub service of the parent item
        @param return((D)jid.JID, None): PubSub service to use
        """
        if parent_service is not None:
            if parent_service.user:
                # we are on a PEP
                if parent_service.host == client.jid.host:
                    #  it's our server, we use already found client.pubsub_service below
                    pass
                else:
                    # other server, let's try to find a non PEP service there
                    d = self.host.findServiceEntity(
                        client, "pubsub", "service", parent_service
                    )
                    d.addCallback(lambda entity: entity or parent_service)
            else:
                # parent is already on a normal Pubsub service, we re-use it
                return defer.succeed(parent_service)

        return defer.succeed(
            client.pubsub_service if client.pubsub_service is not None else parent_service
        )

    @defer.inlineCallbacks
    def _manageComments(self, client, mb_data, service, node, item_id, access=None):
        """Check comments keys in mb_data and create comments node if necessary

        if a comments node metadata is set in the mb_data['comments'] list, it is used
        otherwise it is generated (if allow_comments is True).
        @param mb_data(dict): microblog mb_data
        @param service(jid.JID, None): PubSub service of the parent item
        @param node(unicode): node of the parent item
        @param item_id(unicode): id of the parent item
        @param access(unicode, None): access model
            None to use same access model as parent item
        """
        allow_comments = mb_data.pop("allow_comments", None)
        if allow_comments is None:
            if "comments" in mb_data:
                mb_data["allow_comments"] = True
            else:
                # no comments set or requested, nothing to do
                return
        elif allow_comments == False:
            if "comments" in mb_data:
                log.warning(
                    "comments are not allowed but there is already a comments node, "
                    "it may be lost: {uri}".format(
                        uri=mb_data["comments"]
                    )
                )
                del mb_data["comments"]
            return

        # we have usually a single comment node, but the spec allow several, so we need to
        # handle this in a list
        if len(mb_data.setdefault('comments', [])) == 0:
            # we need at least one comment node
            comments_data = {}
            mb_data['comments'].append({})

        if access is None:
            # TODO: cache access models per service/node
            parent_node_config = yield self._p.getConfiguration(client, service, node)
            access = parent_node_config.get(self._p.OPT_ACCESS_MODEL, self._p.ACCESS_OPEN)

        options = {
            self._p.OPT_ACCESS_MODEL: access,
            self._p.OPT_PERSIST_ITEMS: 1,
            self._p.OPT_MAX_ITEMS: -1,
            self._p.OPT_DELIVER_PAYLOADS: 1,
            self._p.OPT_SEND_ITEM_SUBSCRIBE: 1,
            # FIXME: would it make sense to restrict publish model to subscribers?
            self._p.OPT_PUBLISH_MODEL: self._p.ACCESS_OPEN,
        }

        # if other plugins need to change the options
        yield self.host.trigger.point("XEP-0277_comments", client, mb_data, options)

        for comments_data in mb_data['comments']:
            uri = comments_data.get('uri')
            comments_node = comments_data.get('node')
            try:
                comments_service = jid.JID(comments_data["service"])
            except KeyError:
                comments_service = None

            if uri:
                uri_service, uri_node = self.parseCommentUrl(uri)
                if ((comments_node is not None and comments_node!=uri_node)
                     or (comments_service is not None and comments_service!=uri_service)):
                    raise ValueError(
                        f"Incoherence between comments URI ({uri}) and comments_service "
                        f"({comments_service}) or comments_node ({comments_node})")
                comments_data['service'] = comments_service = uri_service
                comments_data['node'] = comments_node = uri_node
            else:
                if not comments_node:
                    comments_node = self.getCommentsNode(item_id)
                comments_data['node'] = comments_node
                if comments_service is None:
                    comments_service = yield self.getCommentsService(client, service)
                    if comments_service is None:
                        comments_service = client.jid.userhostJID()
                comments_data['service'] = comments_service

                comments_data['uri'] = xmpp_uri.buildXMPPUri(
                    "pubsub",
                    path=comments_service.full(),
                    node=comments_node,
                )

            try:
                yield self._p.createNode(client, comments_service, comments_node, options)
            except error.StanzaError as e:
                if e.condition == "conflict":
                    log.info(
                        "node {} already exists on service {}".format(
                            comments_node, comments_service
                        )
                    )
                else:
                    raise e
            else:
                if access == self._p.ACCESS_WHITELIST:
                    # for whitelist access we need to copy affiliations from parent item
                    comments_affiliations = yield self._p.getNodeAffiliations(
                        client, service, node
                    )
                    # …except for "member", that we transform to publisher
                    # because we wants members to be able to write to comments
                    for jid_, affiliation in list(comments_affiliations.items()):
                        if affiliation == "member":
                            comments_affiliations[jid_] == "publisher"

                    yield self._p.setNodeAffiliations(
                        client, comments_service, comments_node, comments_affiliations
                    )

    def friendlyId(self, data):
        """Generate a user friendly id from title or content"""
        # TODO: rich content should be converted to plain text
        id_base = regex.urlFriendlyText(
            data.get('title')
            or data.get('title_rich')
            or data.get('content')
            or data.get('content_rich')
            or ''
        )
        return f"{id_base}-{token_urlsafe(3)}"

    def _mbSend(self, service, node, data, profile_key):
        service = jid.JID(service) if service else None
        node = node if node else NS_MICROBLOG
        client = self.host.getClient(profile_key)
        data = data_format.deserialise(data)
        return defer.ensureDeferred(self.send(client, data, service, node))

    async def send(
        self,
        client: SatXMPPEntity,
        data: dict,
        service: Optional[jid.JID] = None,
        node: Optional[str] = NS_MICROBLOG
    ) -> None:
        """Send XEP-0277's microblog data

        @param data: microblog data (must include at least a "content" or a "title" key).
            see http://wiki.goffi.org/wiki/Bridge_API_-_Microblogging/en for details
        @param service: PubSub service where the microblog must be published
            None to publish on profile's PEP
        @param node: PubSub node to use (defaut to microblog NS)
            None is equivalend as using default value
        """
        # TODO: check that all data keys are used, this would avoid sending publicly a private message
        #       by accident (e.g. if group plugin is not loaded, and "group*" key are not used)
        if node is None:
            node = NS_MICROBLOG

        item_id = data.get("id")
        if item_id is None:
            if data.get("user_friendly_id", True):
                item_id = self.friendlyId(data)
            else:
                item_id = str(shortuuid.uuid())

        try:
            await self._manageComments(client, data, service, node, item_id, access=None)
        except error.StanzaError:
            log.warning("Can't create comments node for item {}".format(item_id))
        item = await self.data2entry(client, data, item_id, service, node)
        return await self._p.publish(client, service, node, [item])

    def _mbPreview(self, service, node, data, profile_key):
        service = jid.JID(service) if service else None
        node = node if node else NS_MICROBLOG
        client = self.host.getClient(profile_key)
        data = data_format.deserialise(data)
        d = defer.ensureDeferred(self.preview(client, data, service, node))
        d.addCallback(data_format.serialise)
        return d

    async def preview(
        self,
        client: SatXMPPEntity,
        data: dict,
        service: Optional[jid.JID] = None,
        node: Optional[str] = NS_MICROBLOG
    ) -> dict:
        """Preview microblog data without publishing them

        params are the same as for [send]
        @return: microblog data as would be retrieved from published item
        """
        if node is None:
            node = NS_MICROBLOG

        item_id = data.get("id", "")

        # we have to serialise then deserialise to be sure that all triggers are called
        item_elt = await self.data2entry(client, data, item_id, service, node)
        item_elt.uri = pubsub.NS_PUBSUB
        return await self.item2mbdata(client, item_elt, service, node)


    ## retract ##

    def _mbRetract(self, service_jid_s, nodeIdentifier, itemIdentifier, profile_key):
        """Call self._p._retractItem, but use default node if node is empty"""
        return self._p._retractItem(
            service_jid_s,
            nodeIdentifier or NS_MICROBLOG,
            itemIdentifier,
            True,
            profile_key,
        )

    ## get ##

    def _mbGetSerialise(self, data):
        items, metadata = data
        metadata['items'] = items
        return data_format.serialise(metadata)

    def _mbGet(self, service="", node="", max_items=10, item_ids=None, extra_dict=None,
               profile_key=C.PROF_KEY_NONE):
        """
        @param max_items(int): maximum number of item to get, C.NO_LIMIT for no limit
        @param item_ids (list[unicode]): list of item IDs
        """
        client = self.host.getClient(profile_key)
        service = jid.JID(service) if service else None
        max_items = None if max_items == C.NO_LIMIT else max_items
        extra = self._p.parseExtra(extra_dict)
        d = self.mbGet(client, service, node or None, max_items, item_ids,
                       extra.rsm_request, extra.extra)
        d.addCallback(self._mbGetSerialise)
        return d

    @defer.inlineCallbacks
    def mbGet(self, client, service=None, node=None, max_items=10, item_ids=None,
              rsm_request=None, extra=None):
        """Get some microblogs

        @param service(jid.JID, None): jid of the publisher
            None to get profile's PEP
        @param node(unicode, None): node to get (or microblog node if None)
        @param max_items(int): maximum number of item to get, None for no limit
        @param item_ids (list[unicode]): list of item IDs
        @param rsm_request (rsm.RSMRequest): RSM request data
        @param extra (dict): extra data

        @return: a deferred couple with the list of items and metadatas.
        """
        if node is None:
            node = NS_MICROBLOG
        items_data = yield self._p.getItems(
            client,
            service,
            node,
            max_items=max_items,
            item_ids=item_ids,
            rsm_request=rsm_request,
            extra=extra,
        )
        mb_data = yield self._p.transItemsDataD(
            items_data, partial(self.item2mbdata, client, service=service, node=node))
        defer.returnValue(mb_data)

    def _mbRename(self, service, node, item_id, new_id, profile_key):
        return defer.ensureDeferred(self.mbRename(
            self.host.getClient(profile_key),
            jid.JID(service) if service else None,
            node or None,
            item_id,
            new_id
        ))

    async def mbRename(
        self,
        client: SatXMPPEntity,
        service: Optional[jid.JID],
        node: Optional[str],
        item_id: str,
        new_id: str
    ) -> None:
        if not node:
            node = NS_MICROBLOG
        await self._p.renameItem(client, service, node, item_id, new_id)

    def parseCommentUrl(self, node_url):
        """Parse a XMPP URI

        Determine the fields comments_service and comments_node of a microblog data
        from the href attribute of an entry's link element. For example this input:
        xmpp:sat-pubsub.example.net?;node=urn%3Axmpp%3Acomments%3A_af43b363-3259-4b2a-ba4c-1bc33aa87634__urn%3Axmpp%3Agroupblog%3Asomebody%40example.net
        will return(JID(u'sat-pubsub.example.net'), 'urn:xmpp:comments:_af43b363-3259-4b2a-ba4c-1bc33aa87634__urn:xmpp:groupblog:somebody@example.net')
        @return (tuple[jid.JID, unicode]): service and node
        """
        try:
            parsed_url = xmpp_uri.parseXMPPUri(node_url)
            service = jid.JID(parsed_url["path"])
            node = parsed_url["node"]
        except Exception as e:
            raise exceptions.DataError(f"Invalid comments link: {e}")

        return (service, node)

    ## configure ##

    def mbSetAccess(self, access="presence", profile_key=C.PROF_KEY_NONE):
        """Create a microblog node on PEP with given access

        If the node already exists, it change options
        @param access: Node access model, according to xep-0060 #4.5
        @param profile_key: profile key
        """
        #  FIXME: check if this mehtod is need, deprecate it if not
        client = self.host.getClient(profile_key)

        _options = {
            self._p.OPT_ACCESS_MODEL: access,
            self._p.OPT_PERSIST_ITEMS: 1,
            self._p.OPT_MAX_ITEMS: -1,
            self._p.OPT_DELIVER_PAYLOADS: 1,
            self._p.OPT_SEND_ITEM_SUBSCRIBE: 1,
        }

        def cb(result):
            # Node is created with right permission
            log.debug(_("Microblog node has now access %s") % access)

        def fatal_err(s_error):
            # Something went wrong
            log.error(_("Can't set microblog access"))
            raise NodeAccessChangeException()

        def err_cb(s_error):
            # If the node already exists, the condition is "conflict",
            # else we have an unmanaged error
            if s_error.value.condition == "conflict":
                # d = self.host.plugins["XEP-0060"].deleteNode(client, client.jid.userhostJID(), NS_MICROBLOG)
                # d.addCallback(lambda x: create_node().addCallback(cb).addErrback(fatal_err))
                change_node_options().addCallback(cb).addErrback(fatal_err)
            else:
                fatal_err(s_error)

        def create_node():
            return self._p.createNode(
                client, client.jid.userhostJID(), NS_MICROBLOG, _options
            )

        def change_node_options():
            return self._p.setOptions(
                client.jid.userhostJID(),
                NS_MICROBLOG,
                client.jid.userhostJID(),
                _options,
                profile_key=profile_key,
            )

        create_node().addCallback(cb).addErrback(err_cb)

    ## methods to manage several stanzas/jids at once ##

    # common

    def _getClientAndNodeData(self, publishers_type, publishers, profile_key):
        """Helper method to construct node_data from publishers_type/publishers

        @param publishers_type: type of the list of publishers, one of:
            C.ALL: get all jids from roster, publishers is not used
            C.GROUP: get jids from groups
            C.JID: use publishers directly as list of jids
        @param publishers: list of publishers, according to "publishers_type" (None,
            list of groups or list of jids)
        @param profile_key: %(doc_profile_key)s
        """
        client = self.host.getClient(profile_key)
        if publishers_type == C.JID:
            jids_set = set(publishers)
        else:
            jids_set = client.roster.getJidsSet(publishers_type, publishers)
            if publishers_type == C.ALL:
                try:
                    # display messages from salut-a-toi@libervia.org or other PEP services
                    services = self.host.plugins["EXTRA-PEP"].getFollowedEntities(
                        profile_key
                    )
                except KeyError:
                    pass  # plugin is not loaded
                else:
                    if services:
                        log.debug(
                            "Extra PEP followed entities: %s"
                            % ", ".join([str(service) for service in services])
                        )
                        jids_set.update(services)

        node_data = []
        for jid_ in jids_set:
            node_data.append((jid_, NS_MICROBLOG))
        return client, node_data

    def _checkPublishers(self, publishers_type, publishers):
        """Helper method to deserialise publishers coming from bridge

        publishers_type(unicode): type of the list of publishers, one of:
        publishers: list of publishers according to type
        @return: deserialised (publishers_type, publishers) tuple
        """
        if publishers_type == C.ALL:
            if publishers:
                raise failure.Failure(
                    ValueError(
                        "Can't use publishers with {} type".format(publishers_type)
                    )
                )
            else:
                publishers = None
        elif publishers_type == C.JID:
            publishers[:] = [jid.JID(publisher) for publisher in publishers]
        return publishers_type, publishers

    # subscribe #

    def _mbSubscribeToMany(self, publishers_type, publishers, profile_key):
        """

        @return (str): session id: Use pubsub.getSubscribeRTResult to get the results
        """
        publishers_type, publishers = self._checkPublishers(publishers_type, publishers)
        return self.mbSubscribeToMany(publishers_type, publishers, profile_key)

    def mbSubscribeToMany(self, publishers_type, publishers, profile_key):
        """Subscribe microblogs for a list of groups or jids

        @param publishers_type: type of the list of publishers, one of:
            C.ALL: get all jids from roster, publishers is not used
            C.GROUP: get jids from groups
            C.JID: use publishers directly as list of jids
        @param publishers: list of publishers, according to "publishers_type" (None, list
            of groups or list of jids)
        @param profile: %(doc_profile)s
        @return (str): session id
        """
        client, node_data = self._getClientAndNodeData(
            publishers_type, publishers, profile_key
        )
        return self._p.subscribeToMany(
            node_data, client.jid.userhostJID(), profile_key=profile_key
        )

    # get #

    def _mbGetFromManyRTResult(self, session_id, profile_key=C.PROF_KEY_DEFAULT):
        """Get real-time results for mbGetFromMany session

        @param session_id: id of the real-time deferred session
        @param return (tuple): (remaining, results) where:
            - remaining is the number of still expected results
            - results is a list of tuple with
                - service (unicode): pubsub service
                - node (unicode): pubsub node
                - failure (unicode): empty string in case of success, error message else
                - items_data(list): data as returned by [mbGet]
                - items_metadata(dict): metadata as returned by [mbGet]
        @param profile_key: %(doc_profile_key)s
        """

        client = self.host.getClient(profile_key)

        def onSuccess(items_data):
            """convert items elements to list of microblog data in items_data"""
            d = self._p.transItemsDataD(
                items_data,
                # FIXME: service and node should be used here
                partial(self.item2mbdata, client),
                serialise=True
            )
            d.addCallback(lambda serialised: ("", serialised))
            return d

        d = self._p.getRTResults(
            session_id,
            on_success=onSuccess,
            on_error=lambda failure: (str(failure.value), ([], {})),
            profile=client.profile,
        )
        d.addCallback(
            lambda ret: (
                ret[0],
                [
                    (service.full(), node, failure, items, metadata)
                    for (service, node), (success, (failure, (items, metadata))) in ret[
                        1
                    ].items()
                ],
            )
        )
        return d

    def _mbGetFromMany(self, publishers_type, publishers, max_items=10, extra_dict=None,
                       profile_key=C.PROF_KEY_NONE):
        """
        @param max_items(int): maximum number of item to get, C.NO_LIMIT for no limit
        """
        max_items = None if max_items == C.NO_LIMIT else max_items
        publishers_type, publishers = self._checkPublishers(publishers_type, publishers)
        extra = self._p.parseExtra(extra_dict)
        return self.mbGetFromMany(
            publishers_type,
            publishers,
            max_items,
            extra.rsm_request,
            extra.extra,
            profile_key,
        )

    def mbGetFromMany(self, publishers_type, publishers, max_items=None, rsm_request=None,
                      extra=None, profile_key=C.PROF_KEY_NONE):
        """Get the published microblogs for a list of groups or jids

        @param publishers_type (str): type of the list of publishers (one of "GROUP" or
            "JID" or "ALL")
        @param publishers (list): list of publishers, according to publishers_type (list
            of groups or list of jids)
        @param max_items (int): optional limit on the number of retrieved items.
        @param rsm_request (rsm.RSMRequest): RSM request data, common to all publishers
        @param extra (dict): Extra data
        @param profile_key: profile key
        @return (str): RT Deferred session id
        """
        # XXX: extra is unused here so far
        client, node_data = self._getClientAndNodeData(
            publishers_type, publishers, profile_key
        )
        return self._p.getFromMany(
            node_data, max_items, rsm_request, profile_key=profile_key
        )

    # comments #

    def _mbGetFromManyWithCommentsRTResultSerialise(self, data):
        """Serialisation of result

        This is probably the longest method name of whole SàT ecosystem ^^
        @param data(dict): data as received by rt_sessions
        @return (tuple): see [_mbGetFromManyWithCommentsRTResult]
        """
        ret = []
        data_iter = iter(data[1].items())
        for (service, node), (success, (failure_, (items_data, metadata))) in data_iter:
            items = []
            for item, item_metadata in items_data:
                item = data_format.serialise(item)
                items.append((item, item_metadata))
            ret.append((
                service.full(),
                node,
                failure_,
                items,
                metadata))

        return data[0], ret

    def _mbGetFromManyWithCommentsRTResult(self, session_id,
                                           profile_key=C.PROF_KEY_DEFAULT):
        """Get real-time results for [mbGetFromManyWithComments] session

        @param session_id: id of the real-time deferred session
        @param return (tuple): (remaining, results) where:
            - remaining is the number of still expected results
            - results is a list of 5-tuple with
                - service (unicode): pubsub service
                - node (unicode): pubsub node
                - failure (unicode): empty string in case of success, error message else
                - items(list[tuple(dict, list)]): list of 2-tuple with
                    - item(dict): item microblog data
                    - comments_list(list[tuple]): list of 5-tuple with
                        - service (unicode): pubsub service where the comments node is
                        - node (unicode): comments node
                        - failure (unicode): empty in case of success, else error message
                        - comments(list[dict]): list of microblog data
                        - comments_metadata(dict): metadata of the comment node
                - metadata(dict): original node metadata
        @param profile_key: %(doc_profile_key)s
        """
        profile = self.host.getClient(profile_key).profile
        d = self.rt_sessions.getResults(session_id, profile=profile)
        d.addCallback(self._mbGetFromManyWithCommentsRTResultSerialise)
        return d

    def _mbGetFromManyWithComments(self, publishers_type, publishers, max_items=10,
                                   max_comments=C.NO_LIMIT, extra_dict=None,
                                   extra_comments_dict=None, profile_key=C.PROF_KEY_NONE):
        """
        @param max_items(int): maximum number of item to get, C.NO_LIMIT for no limit
        @param max_comments(int): maximum number of comments to get, C.NO_LIMIT for no
            limit
        """
        max_items = None if max_items == C.NO_LIMIT else max_items
        max_comments = None if max_comments == C.NO_LIMIT else max_comments
        publishers_type, publishers = self._checkPublishers(publishers_type, publishers)
        extra = self._p.parseExtra(extra_dict)
        extra_comments = self._p.parseExtra(extra_comments_dict)
        return self.mbGetFromManyWithComments(
            publishers_type,
            publishers,
            max_items,
            max_comments or None,
            extra.rsm_request,
            extra.extra,
            extra_comments.rsm_request,
            extra_comments.extra,
            profile_key,
        )

    def mbGetFromManyWithComments(self, publishers_type, publishers, max_items=None,
                                  max_comments=None, rsm_request=None, extra=None,
                                  rsm_comments=None, extra_comments=None,
                                  profile_key=C.PROF_KEY_NONE):
        """Helper method to get the microblogs and their comments in one shot

        @param publishers_type (str): type of the list of publishers (one of "GROUP" or
            "JID" or "ALL")
        @param publishers (list): list of publishers, according to publishers_type (list
            of groups or list of jids)
        @param max_items (int): optional limit on the number of retrieved items.
        @param max_comments (int): maximum number of comments to retrieve
        @param rsm_request (rsm.RSMRequest): RSM request for initial items only
        @param extra (dict): extra configuration for initial items only
        @param rsm_comments (rsm.RSMRequest): RSM request for comments only
        @param extra_comments (dict): extra configuration for comments only
        @param profile_key: profile key
        @return (str): RT Deferred session id
        """
        # XXX: this method seems complicated because it do a couple of treatments
        #      to serialise and associate the data, but it make life in frontends side
        #      a lot easier

        client, node_data = self._getClientAndNodeData(
            publishers_type, publishers, profile_key
        )

        def getComments(items_data):
            """Retrieve comments and add them to the items_data

            @param items_data: serialised items data
            @return (defer.Deferred): list of items where each item is associated
                with a list of comments data (service, node, list of items, metadata)
            """
            items, metadata = items_data
            items_dlist = []  # deferred list for items
            for item in items:
                dlist = []  # deferred list for comments
                for key, value in item.items():
                    # we look for comments
                    if key.startswith("comments") and key.endswith("_service"):
                        prefix = key[: key.find("_")]
                        service_s = value
                        service = jid.JID(service_s)
                        node = item["{}{}".format(prefix, "_node")]
                        # time to get the comments
                        d = self._p.getItems(
                            client,
                            service,
                            node,
                            max_comments,
                            rsm_request=rsm_comments,
                            extra=extra_comments,
                        )
                        # then serialise
                        d.addCallback(
                            lambda items_data: self._p.transItemsDataD(
                                items_data,
                                partial(
                                    self.item2mbdata, client, service=service, node=node
                                ),
                                serialise=True
                            )
                        )
                        # with failure handling
                        d.addCallback(
                            lambda serialised_items_data: ("",) + serialised_items_data
                        )
                        d.addErrback(lambda failure: (str(failure.value), [], {}))
                        # and associate with service/node (needed if there are several
                        # comments nodes)
                        d.addCallback(
                            lambda serialised, service_s=service_s, node=node: (
                                service_s,
                                node,
                            )
                            + serialised
                        )
                        dlist.append(d)
                # we get the comments
                comments_d = defer.gatherResults(dlist)
                # and add them to the item data
                comments_d.addCallback(
                    lambda comments_data, item=item: (item, comments_data)
                )
                items_dlist.append(comments_d)
            # we gather the items + comments in a list
            items_d = defer.gatherResults(items_dlist)
            # and add the metadata
            items_d.addCallback(lambda items_completed: (items_completed, metadata))
            return items_d

        deferreds = {}
        for service, node in node_data:
            d = deferreds[(service, node)] = self._p.getItems(
                client, service, node, max_items, rsm_request=rsm_request, extra=extra
            )
            d.addCallback(
                lambda items_data: self._p.transItemsDataD(
                    items_data,
                    partial(self.item2mbdata, client, service=service, node=node),
                )
            )
            d.addCallback(getComments)
            d.addCallback(lambda items_comments_data: ("", items_comments_data))
            d.addErrback(lambda failure: (str(failure.value), ([], {})))

        return self.rt_sessions.newSession(deferreds, client.profile)


@implementer(iwokkel.IDisco)
class XEP_0277_handler(XMPPHandler):

    def getDiscoInfo(self, requestor, target, nodeIdentifier=""):
        return [disco.DiscoFeature(NS_MICROBLOG)]

    def getDiscoItems(self, requestor, target, nodeIdentifier=""):
        return []
