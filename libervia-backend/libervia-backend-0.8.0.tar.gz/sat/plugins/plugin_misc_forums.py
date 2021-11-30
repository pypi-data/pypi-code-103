#!/usr/bin/env python3


# SAT plugin for pubsub forums
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

from sat.core.i18n import _
from sat.core.constants import Const as C
from sat.core import exceptions
from sat.core.log import getLogger
from sat.tools.common import uri, data_format
from twisted.words.protocols.jabber import jid
from twisted.words.xish import domish
from twisted.internet import defer
import shortuuid
import json
log = getLogger(__name__)

NS_FORUMS = 'org.salut-a-toi.forums:0'
NS_FORUMS_TOPICS = NS_FORUMS + '#topics'

PLUGIN_INFO = {
    C.PI_NAME: _("forums management"),
    C.PI_IMPORT_NAME: "forums",
    C.PI_TYPE: "EXP",
    C.PI_PROTOCOLS: [],
    C.PI_DEPENDENCIES: ["XEP-0060", "XEP-0277"],
    C.PI_MAIN: "forums",
    C.PI_HANDLER: "no",
    C.PI_DESCRIPTION: _("""forums management plugin""")
}
FORUM_ATTR = {'title', 'name', 'main-language', 'uri'}
FORUM_SUB_ELTS = ('short-desc', 'desc')
FORUM_TOPICS_NODE_TPL = '{node}#topics_{uuid}'
FORUM_TOPIC_NODE_TPL = '{node}_{uuid}'


class forums(object):

    def __init__(self, host):
        log.info(_("forums plugin initialization"))
        self.host = host
        self._m = self.host.plugins['XEP-0277']
        self._p = self.host.plugins['XEP-0060']
        self._node_options = {
            self._p.OPT_ACCESS_MODEL: self._p.ACCESS_OPEN,
            self._p.OPT_PERSIST_ITEMS: 1,
            self._p.OPT_MAX_ITEMS: -1,
            self._p.OPT_DELIVER_PAYLOADS: 1,
            self._p.OPT_SEND_ITEM_SUBSCRIBE: 1,
            self._p.OPT_PUBLISH_MODEL: self._p.ACCESS_OPEN,
            }
        host.registerNamespace('forums', NS_FORUMS)
        host.bridge.addMethod("forumsGet", ".plugin",
                              in_sign='ssss', out_sign='s',
                              method=self._get,
                              async_=True)
        host.bridge.addMethod("forumsSet", ".plugin",
                              in_sign='sssss', out_sign='',
                              method=self._set,
                              async_=True)
        host.bridge.addMethod("forumTopicsGet", ".plugin",
                              in_sign='ssa{ss}s', out_sign='(aa{ss}s)',
                              method=self._getTopics,
                              async_=True)
        host.bridge.addMethod("forumTopicCreate", ".plugin",
                              in_sign='ssa{ss}s', out_sign='',
                              method=self._createTopic,
                              async_=True)

    @defer.inlineCallbacks
    def _createForums(self, client, forums, service, node, forums_elt=None, names=None):
        """Recursively create <forums> element(s)

        @param forums(list): forums which may have subforums
        @param service(jid.JID): service where the new nodes will be created
        @param node(unicode): node of the forums
            will be used as basis for the newly created nodes
        @param parent_elt(domish.Element, None): element where the forum must be added
            if None, the root <forums> element will be created
        @return (domish.Element): created forums
        """
        if not isinstance(forums, list):
            raise ValueError(_("forums arguments must be a list of forums"))
        if forums_elt is None:
            forums_elt = domish.Element((NS_FORUMS, 'forums'))
            assert names is None
            names = set()
        else:
            if names is None or forums_elt.name != 'forums':
                raise exceptions.InternalError('invalid forums or names')
            assert names is not None

        for forum in forums:
            if not isinstance(forum, dict):
                raise ValueError(_("A forum item must be a dictionary"))
            forum_elt = forums_elt.addElement('forum')

            for key, value in forum.items():
                if key == 'name' and key in names:
                    raise exceptions.ConflictError(_("following forum name is not unique: {name}").format(name=key))
                if key == 'uri' and not value.strip():
                    log.info(_("creating missing forum node"))
                    forum_node = FORUM_TOPICS_NODE_TPL.format(node=node, uuid=shortuuid.uuid())
                    yield self._p.createNode(client, service, forum_node, self._node_options)
                    value = uri.buildXMPPUri('pubsub',
                                             path=service.full(),
                                             node=forum_node)
                if key in FORUM_ATTR:
                    forum_elt[key] = value.strip()
                elif key in FORUM_SUB_ELTS:
                    forum_elt.addElement(key, content=value)
                elif key == 'sub-forums':
                    sub_forums_elt = forum_elt.addElement('forums')
                    yield self._createForums(client, value, service, node, sub_forums_elt, names=names)
                else:
                    log.warning(_("Unknown forum attribute: {key}").format(key=key))
            if not forum_elt.getAttribute('title'):
                name = forum_elt.getAttribute('name')
                if name:
                    forum_elt['title'] = name
                else:
                    raise ValueError(_("forum need a title or a name"))
            if not forum_elt.getAttribute('uri') and not forum_elt.children:
                raise ValueError(_("forum need uri or sub-forums"))
        defer.returnValue(forums_elt)

    def _parseForums(self, parent_elt=None, forums=None):
        """Recursivly parse a <forums> elements and return corresponding forums data

        @param item(domish.Element): item with <forums> element
        @param parent_elt(domish.Element, None): element to parse
        @return (list): parsed data
        @raise ValueError: item is invalid
        """
        if parent_elt.name == 'item':
            forums = []
            try:
                forums_elt = next(parent_elt.elements(NS_FORUMS, 'forums'))
            except StopIteration:
                raise ValueError(_("missing <forums> element"))
        else:
            forums_elt = parent_elt
            if forums is None:
                raise exceptions.InternalError('expected forums')
            if forums_elt.name != 'forums':
                raise ValueError(_('Unexpected element: {xml}').format(xml=forums_elt.toXml()))
        for forum_elt in forums_elt.elements():
            if forum_elt.name == 'forum':
                data = {}
                for attrib in FORUM_ATTR.intersection(forum_elt.attributes):
                    data[attrib] = forum_elt[attrib]
                unknown = set(forum_elt.attributes).difference(FORUM_ATTR)
                if unknown:
                    log.warning(_("Following attributes are unknown: {unknown}").format(unknown=unknown))
                for elt in forum_elt.elements():
                    if elt.name in FORUM_SUB_ELTS:
                        data[elt.name] = str(elt)
                    elif elt.name == 'forums':
                        sub_forums = data['sub-forums'] = []
                        self._parseForums(elt, sub_forums)
                if not 'title' in data or not {'uri', 'sub-forums'}.intersection(data):
                    log.warning(_("invalid forum, ignoring: {xml}").format(xml=forum_elt.toXml()))
                else:
                    forums.append(data)
            else:
                log.warning(_("unkown forums sub element: {xml}").format(xml=forum_elt))

        return forums

    def _get(self, service=None, node=None, forums_key=None, profile_key=C.PROF_KEY_NONE):
        client = self.host.getClient(profile_key)
        if service.strip():
            service = jid.JID(service)
        else:
            service = None
        if not node.strip():
            node = None
        d=self.get(client, service, node, forums_key or None)
        d.addCallback(lambda data: json.dumps(data))
        return d

    @defer.inlineCallbacks
    def get(self, client, service=None, node=None, forums_key=None):
        if service is None:
            service = client.pubsub_service
        if node is None:
            node = NS_FORUMS
        if forums_key is None:
            forums_key = 'default'
        items_data = yield self._p.getItems(client, service, node, item_ids=[forums_key])
        item = items_data[0][0]
        # we have the item and need to convert it to json
        forums = self._parseForums(item)
        defer.returnValue(forums)

    def _set(self, forums, service=None, node=None, forums_key=None, profile_key=C.PROF_KEY_NONE):
        client = self.host.getClient(profile_key)
        forums = json.loads(forums)
        if service.strip():
            service = jid.JID(service)
        else:
            service = None
        if not node.strip():
            node = None
        return self.set(client, forums, service, node, forums_key or None)

    @defer.inlineCallbacks
    def set(self, client, forums, service=None, node=None, forums_key=None):
        """Create or replace forums structure

        @param forums(list): list of dictionary as follow:
            a dictionary represent a forum metadata, with the following keys:
                - title: title of the forum
                - name: short name (unique in those forums) for the forum
                - main-language: main language to be use in the forums
                - uri: XMPP uri to the microblog node hosting the forum
                - short-desc: short description of the forum (in main-language)
                - desc: long description of the forum (in main-language)
                - sub-forums: a list of sub-forums with the same structure
            title or name is needed, and uri or sub-forums
        @param forums_key(unicode, None): key (i.e. item id) of the forums
            may be used to store different forums structures for different languages
            None to use "default"
        """
        if service is None:
             service = client.pubsub_service
        if node is None:
            node = NS_FORUMS
        if forums_key is None:
            forums_key = 'default'
        forums_elt = yield self._createForums(client, forums, service, node)
        yield self._p.sendItem(client, service, node, forums_elt, item_id=forums_key)

    def _getTopics(self, service, node, extra=None, profile_key=C.PROF_KEY_NONE):
        client = self.host.getClient(profile_key)
        extra = self._p.parseExtra(extra)
        d = self.getTopics(client, jid.JID(service), node, rsm_request=extra.rsm_request, extra=extra.extra)
        d.addCallback(
            lambda topics_data: (topics_data[0], data_format.serialise(topics_data[1]))
        )
        return d

    @defer.inlineCallbacks
    def getTopics(self, client, service, node, rsm_request=None, extra=None):
        """Retrieve topics data

        Topics are simple microblog URIs with some metadata duplicated from first post
        """
        topics_data = yield self._p.getItems(client, service, node, rsm_request=rsm_request, extra=extra)
        topics = []
        item_elts, metadata = topics_data
        for item_elt in item_elts:
            topic_elt = next(item_elt.elements(NS_FORUMS, 'topic'))
            title_elt = next(topic_elt.elements(NS_FORUMS, 'title'))
            topic = {'uri': topic_elt['uri'],
                     'author': topic_elt['author'],
                     'title': str(title_elt)}
            topics.append(topic)
        defer.returnValue((topics, metadata))

    def _createTopic(self, service, node, mb_data, profile_key):
        client = self.host.getClient(profile_key)
        return defer.ensureDeferred(
            self.createTopic(client, jid.JID(service), node, mb_data)
        )

    async def createTopic(self, client, service, node, mb_data):
        try:
            title = mb_data['title']
            content = mb_data.pop('content')
        except KeyError as e:
            raise exceptions.DataError("missing mandatory data: {key}".format(key=e.args[0]))
        else:
            mb_data["content_rich"] = content
        topic_node = FORUM_TOPIC_NODE_TPL.format(node=node, uuid=shortuuid.uuid())
        await self._p.createNode(client, service, topic_node, self._node_options)
        await self._m.send(client, mb_data, service, topic_node)
        topic_uri = uri.buildXMPPUri('pubsub',
                                     subtype='microblog',
                                     path=service.full(),
                                     node=topic_node)
        topic_elt = domish.Element((NS_FORUMS, 'topic'))
        topic_elt['uri'] = topic_uri
        topic_elt['author'] = client.jid.userhost()
        topic_elt.addElement('title', content = title)
        await self._p.sendItem(client, service, node, topic_elt)
