#!/usr/bin/env python3
#
# Copyright (c) 2012-2021 Jérôme Poisson
# Copyright (c) 2013-2016 Adrien Cossa
# Copyright (c) 2003-2011 Ralph Meijer


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
# --

# This program is based on Idavoll (http://idavoll.ik.nu/),
# originaly written by Ralph Meijer (http://ralphm.net/blog/)
# It is sublicensed under AGPL v3 (or any later version) as allowed by the original
# license.

# --

# Here is a copy of the original license:

# Copyright (c) 2003-2011 Ralph Meijer

# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:

# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


"""
Generic publish-subscribe backend.

This module implements a generic publish-subscribe backend service with
business logic as per
U{XEP-0060<http://www.xmpp.org/extensions/xep-0060.html>} that interacts with
a given storage facility. It also provides an adapter from the XMPP
publish-subscribe protocol.
"""

import copy
import uuid
from typing import Optional, List, Tuple

from zope.interface import implementer

from twisted.application import service
from twisted.python import components, failure, log
from twisted.internet import defer, reactor
from twisted.words.protocols.jabber.error import StanzaError
from twisted.words.protocols.jabber import jid
from twisted.words.xish import domish, utility

from wokkel import disco
from wokkel import data_form
from wokkel import rsm
from wokkel import iwokkel
from wokkel import pubsub
from wokkel.subprotocols import XMPPHandler

from sat_pubsub import error
from sat_pubsub import iidavoll
from sat_pubsub import const
from sat_pubsub import container

# TODO: modernise the code, get rid of legacy Twisted logging, use coroutines,
#   better formatting


def _getAffiliation(node, entity):
    d = node.getAffiliation(entity)
    d.addCallback(lambda affiliation: (node, affiliation))
    return d


def elementCopy(element):
    """Make a copy of a domish.Element

    The copy will have its own children list, so other elements
    can be added as direct children without modifying orignal one.
    Children are not deeply copied, so if an element is added to a child or grandchild,
    it will also affect original element.
    @param element(domish.Element): Element to clone
    """
    new_elt = domish.Element(
        (element.uri, element.name),
        defaultUri = element.defaultUri,
        attribs = element.attributes,
        localPrefixes = element.localPrefixes)
    new_elt.parent = element.parent
    new_elt.children = element.children[:]
    return new_elt


def itemDataCopy(item_data):
    """Make a copy of an item_data

    deep copy every element of the tuple but item
    do an elementCopy of item_data.item
    @param item_data(ItemData): item data to copy
    @return (ItemData): copied data
    """
    return container.ItemData(*[elementCopy(item_data.item)]
                              + [copy.deepcopy(d) for d in item_data[1:]])


@implementer(iidavoll.IBackendService)
class BackendService(service.Service, utility.EventDispatcher):
    """
    Generic publish-subscribe backend service.

    @cvar nodeOptions: Node configuration form as a mapping from the field
                       name to a dictionary that holds the field's type, label
                       and possible options to choose from.
    @type nodeOptions: C{dict}.
    @cvar defaultConfig: The default node configuration.
    """


    nodeOptions = {
            const.OPT_PERSIST_ITEMS:
                {"type": "boolean",
                 "label": "Persist items to storage"},
            const.OPT_MAX_ITEMS:
                {"type": "text-single",
                 "label": 'number of items to keep ("max" for unlimited)'},
            const.OPT_DELIVER_PAYLOADS:
                {"type": "boolean",
                 "label": "Deliver payloads with event notifications"},
            const.OPT_SEND_LAST_PUBLISHED_ITEM:
                {"type": "list-single",
                 "label": "When to send the last published item",
                 "options": {
                     "never": "Never",
                     "on_sub": "When a new subscription is processed"}
                },
            const.OPT_ACCESS_MODEL:
                {"type": "list-single",
                 "label": "Who can subscribe to this node",
                 "options": {
                     const.VAL_AMODEL_OPEN: "Public node",
                     const.VAL_AMODEL_PRESENCE: "Node restricted to entites subscribed to owner presence",
                     const.VAL_AMODEL_PUBLISHER_ROSTER: "Node restricted to some groups of publisher's roster",
                     const.VAL_AMODEL_WHITELIST: "Node restricted to some jids",
                     }
                },
            const.OPT_ROSTER_GROUPS_ALLOWED:
                {"type": "list-multi",
                 "label": "Groups of the roster allowed to access the node",
                },
            const.OPT_PUBLISH_MODEL:
                {"type": "list-single",
                 "label": "Who can publish to this node",
                 "options": {
                     const.VAL_PMODEL_OPEN: "Everybody can publish",
                     const.VAL_PMODEL_PUBLISHERS: "Only owner and publishers can publish",
                     const.VAL_PMODEL_SUBSCRIBERS: "Everybody which subscribed to the node",
                     }
                },
            const.OPT_OVERWRITE_POLICY:
                {"type": "list-single",
                 "label": "Who can overwrite an item",
                 "options": {
                     const.VAL_OWPOL_ORIGINAL: "Only original publisher of the item",
                     const.VAL_OWPOL_ANY_PUB: "Any publisher",
                     }
                },
            const.OPT_SERIAL_IDS:
                {"type": "boolean",
                 "label": "Use serial ids"},
            const.OPT_CONSISTENT_PUBLISHER:
                {"type": "boolean",
                 "label": "Keep publisher on update"},
            const.OPT_FTS_LANGUAGE:
                {"type": "list-single",
                 "label": "Default language to use for full text search",
                 "options": {
                     const.VAL_FTS_GENERIC: (
                         "Generic (use if unsure of if your language is not present)"
                     )
                 }
                },
            }

    subscriptionOptions = {
            "pubsub#subscription_type":
                {"type": "list-single",
                 "options": {
                     "items": "Receive notification of new items only",
                     "nodes": "Receive notification of new nodes only"}
                },
            "pubsub#subscription_depth":
                {"type": "list-single",
                 "options": {
                     "1": "Receive notification from direct child nodes only",
                     "all": "Receive notification from all descendent nodes"}
                },
            }

    def __init__(self, storage, config):
        utility.EventDispatcher.__init__(self)
        self.storage = storage
        self.config = config
        self.admins = config['admins_jids_list']
        self.jid = config["jid"]
        if config["server_jid"] is None:
            self.server_jid = jid.JID(str(self.jid).split(".", 1)[1])
        else:
            self.server_jid = jid.JID(config["server_jid"])
        d = self.storage.getFTSLanguages()
        d.addCallbacks(self._getFTSLanguagesCb, self._getFTSLanguagesEb)

    def _getFTSLanguagesCb(self, languages):
        # we skip the first one which is always "generic", as we already have it
        for l in languages[1:]:
            self.nodeOptions[const.OPT_FTS_LANGUAGE]["options"][l] = l.title()

    def _getFTSLanguagesEb(self, failure_):
        log.msg(f"WARNING: can get FTS languages: {failure_}")

    def isAdmin(self, entity_jid):
        """Return True if an entity is an administrator"""
        return entity_jid.userhostJID() in self.admins

    def supportsPublishOptions(self):
        return True

    def supportsPublisherAffiliation(self):
        return True

    def supportsGroupBlog(self):
        return True

    def supportsOutcastAffiliation(self):
        return True

    def supportsPersistentItems(self):
        return True

    def supportsPublishModel(self):
        return True

    def getNodeType(self, nodeIdentifier, pep, recipient=None):
        # FIXME: manage pep and recipient
        d = self.storage.getNode(nodeIdentifier, pep, recipient)
        d.addCallback(lambda node: node.getType())
        return d

    def _getNodesIds(self, subscribed, pep, recipient):
        # TODO: filter whitelist nodes
        # TODO: handle publisher-roster (should probably be renamed to owner-roster for nodes)
        if not subscribed:
            allowed_accesses = {'open', 'whitelist'}
        else:
            allowed_accesses = {'open', 'presence', 'whitelist'}
        return self.storage.getNodeIds(pep, recipient, allowed_accesses)

    async def getNodes(self, requestor, pep, recipient):
        if pep:
            subscribed = await self.privilege.isSubscribedFrom(requestor, recipient)
            return await self._getNodesIds(subscribed, pep, recipient)
        return await self.storage.getNodeIds(pep, recipient)

    def getNodeMetaData(self, nodeIdentifier, pep, recipient=None):
        # FIXME: manage pep and recipient
        d = self.storage.getNode(nodeIdentifier, pep, recipient)
        d.addCallback(lambda node: node.getMetaData())
        d.addCallback(self._makeMetaData)
        return d

    def _makeMetaData(self, metaData):
        options = []
        for key, value in metaData.items():
            if key in self.nodeOptions:
                option = {"var": key}
                option.update(self.nodeOptions[key])
                option["value"] = value
                options.append(option)

        return options

    async def _checkAuth(self, node, requestor):
        """ Check authorisation of publishing in node for requestor """
        affiliation = await node.getAffiliation(requestor)
        configuration = node.getConfiguration()
        publish_model = configuration[const.OPT_PUBLISH_MODEL]
        if publish_model == const.VAL_PMODEL_PUBLISHERS:
            if affiliation not in ['owner', 'publisher']:
                raise error.Forbidden()
        elif publish_model == const.VAL_PMODEL_SUBSCRIBERS:
            if affiliation not in ['owner', 'publisher']:
                # we are in subscribers publish model, we must check that
                # the requestor is a subscriber to allow him to publish
                subscribed = await node.isSubscribed(requestor)
                if not subscribed:
                    raise error.Forbidden()
        elif publish_model != const.VAL_PMODEL_OPEN:
            # publish_model must be publishers (default), subscribers or open.
            raise ValueError('Unexpected value')

        return (affiliation, node)

    def parseItemConfig(self, item):
        """Get and remove item configuration information

        @param item (domish.Element): item to parse
        @return (tuple[unicode, dict)): (access_model, item_config)
        """
        item_config = None
        access_model = const.VAL_AMODEL_DEFAULT
        for idx, elt in enumerate(item.elements()):
            if elt.uri != data_form.NS_X_DATA or elt.name != 'x':
                continue
            form = data_form.Form.fromElement(elt)
            if form.formNamespace == const.NS_ITEM_CONFIG:
                item_config = form
                del item.children[idx] #we need to remove the config from item
                break

        if item_config:
            access_model = item_config.get(const.OPT_ACCESS_MODEL, const.VAL_AMODEL_DEFAULT)
        return (access_model, item_config)

    def parseCategories(self, item_elt):
        """Check if item contain an atom entry, and parse categories if possible

        @param item_elt (domish.Element): item to parse
        @return (list): list of found categories
        """
        categories = []
        try:
            entry_elt = next(item_elt.elements(const.NS_ATOM, "entry"))
        except StopIteration:
            return categories

        for category_elt in entry_elt.elements(const.NS_ATOM, 'category'):
            category = category_elt.getAttribute('term')
            if category:
                categories.append(category)

        return categories

    def enforceSchema(self, item_elt, schema, affiliation):
        """modifify item according to element, or refuse publishing

        @param item_elt(domish.Element): item to check/modify
        @param schema(domish.Eement): schema to enfore
        @param affiliation(unicode): affiliation of the publisher
        """
        try:
            x_elt = next(item_elt.elements(data_form.NS_X_DATA, 'x'))
            item_form = data_form.Form.fromElement(x_elt)
        except (StopIteration, data_form.Error):
            raise pubsub.BadRequest(text="node has a schema but item has no form")
        else:
            item_elt.children.remove(x_elt)

        schema_form = data_form.Form.fromElement(schema)

        # we enforce restrictions
        for field_elt in schema.elements(data_form.NS_X_DATA, 'field'):
            var = field_elt['var']
            for restrict_elt in field_elt.elements(const.NS_SCHEMA_RESTRICT, 'restrict'):
                write_restriction = restrict_elt.attributes.get('write')
                if write_restriction is not None:
                    if write_restriction == 'owner':
                        if affiliation != 'owner':
                            # write is not allowed on this field, we use default value
                            # we can safely use Field from schema_form because
                            # we have created this instance only for this method
                            try:
                                item_form.removeField(item_form.fields[var])
                            except KeyError:
                                pass
                            item_form.addField(schema_form.fields[var])
                    else:
                        raise StanzaError('feature-not-implemented', text='unknown write restriction {}'.format(write_restriction))

        # we now remove every field which is not in data schema
        to_remove = set()
        for item_var, item_field in item_form.fields.items():
            if item_var not in schema_form.fields:
                to_remove.add(item_field)

        for field in to_remove:
            item_form.removeField(field)
        item_elt.addChild(item_form.toElement())

    def _getFDPSubmittedNode(
        self,
        nodeIdentifier: str,
        pep: bool,
        recipient: jid.JID,
    ) -> Optional[defer.Deferred]:
        """Get submitted forms node for Form Discovery and Publishing

        @param nodeIdentifier: template node (must start with const.FDP_TEMPLATE_PREFIX)
        @êeturn: node or None if the node doesn't exist
        """
        app_ns = nodeIdentifier[len(const.FDP_TEMPLATE_PREFIX):]
        submitted_node_id = f"{const.FDP_SUBMITTED_PREFIX}{app_ns}"
        try:
            return self.storage.getNode(submitted_node_id, pep, recipient)
        except error.NodeNotFound:
            return None

    async def publish(self, nodeIdentifier, items, requestor, options, pep, recipient):
        if len(items) == 0:
            raise pubsub.BadRequest(text="no item to publish")
        node = await self.storage.getNode(nodeIdentifier, pep, recipient)
        affiliation, node = await self._checkAuth(node, requestor)

        if node.nodeType == 'collection':
            raise error.NoPublishing()

        configuration = node.getConfiguration()
        persistItems = configuration[const.OPT_PERSIST_ITEMS]
        deliverPayloads = configuration[const.OPT_DELIVER_PAYLOADS]

        # we check that publish-options are satisfied
        for field, value in options.items():
            try:
               current_value = configuration[field]
            except KeyError:
                raise error.ConstraintFailed(
                    f"publish-options {field!r} doesn't exist in node configuration"
                )
            if current_value != value:
                raise error.ConstraintFailed(
                    f"configuration field {field!r} has a value of {current_value!r} "
                    f"which doesn't fit publish-options expected {value!r}"
                )

        if items and not persistItems and not deliverPayloads:
            raise error.ItemForbidden()
        elif not items and (persistItems or deliverPayloads):
            raise error.ItemRequired()

        items_data = []
        check_overwrite = False
        ret_payload = None  # payload returned, None or domish.Element
        for item in items:
            # we enforce publisher (cf XEP-0060 §7.1.2.3)
            item['publisher'] = requestor.full()
            if persistItems or deliverPayloads:
                item.uri = None
                item.defaultUri = None
                if not item.getAttribute("id"):
                    item["id"] = await node.getNextId()
                    new_item = True
                    if ret_payload is None:
                        ret_pubsub_elt = domish.Element((pubsub.NS_PUBSUB, 'pubsub'))
                        ret_publish_elt = ret_pubsub_elt.addElement('publish')
                        ret_publish_elt['node'] = node.nodeIdentifier
                        ret_payload = ret_pubsub_elt
                    ret_publish_elt = ret_payload.publish
                    ret_item_elt = ret_publish_elt.addElement('item')
                    ret_item_elt["id"] = item["id"]
                else:
                    check_overwrite = True
                    new_item = False
            access_model, item_config = self.parseItemConfig(item)
            categories = self.parseCategories(item)
            schema = node.getSchema()
            if schema is not None:
                self.enforceSchema(item, schema, affiliation)
            items_data.append(container.ItemData(item, access_model, item_config, categories, new=new_item))

        if persistItems:

            if check_overwrite:
                itemIdentifiers = [item['id'] for item in items
                                   if item.getAttribute('id')]

                if affiliation == 'owner' or self.isAdmin(requestor):
                    if configuration[const.OPT_CONSISTENT_PUBLISHER]:
                        pub_map = await node.getItemsPublishers(itemIdentifiers)
                        if pub_map:
                            # if we have existing items, we replace publishers with
                            # original one to stay consistent
                            publishers = set(pub_map.values())
                            if len(publishers) != 1:
                                # TODO: handle multiple items publishing (from several
                                #       publishers)
                                raise error.NoPublishing(
                                    "consistent_publisher is currently only possible when "
                                    "publishing items from a single publisher. Try to "
                                    "publish one item at a time")
                            # we replace requestor and new payload's publisher by original
                            # item publisher to keep publisher consistent
                            requestor = publishers.pop()
                            for item in items:
                                item['publisher'] = requestor.full()
                elif configuration[const.OPT_OVERWRITE_POLICY] == const.VAL_OWPOL_ORIGINAL:
                    # we don't want a publisher to overwrite the item
                    # of an other publisher
                    item_pub_map = await node.getItemsPublishers(itemIdentifiers)
                    for item_publisher in item_pub_map.values():
                        if item_publisher.userhost() != requestor.userhost():
                            raise error.ItemForbidden(
                                "Item can only be overwritten by original publisher"
                            )

            if node.nodeIdentifier.startswith(const.FDP_TEMPLATE_PREFIX):
                schema_item = items_data[-1].item
                try:
                    schema = next(schema_item.elements(data_form.NS_X_DATA, 'x'))
                except StopIteration:
                    raise pubsub.BadRequest(text="Data form is missing in FDP request")
                submitted_node = await self._getFDPSubmittedNode(
                    node.nodeIdentifier, pep, recipient)
                if submitted_node is not None:
                    await submitted_node.setSchema(schema)

            # TODO: check conflict and recalculate max id if serial_ids is set
            await node.storeItems(items_data, requestor)

        self._doNotify(node, items_data, deliverPayloads, pep, recipient)
        return ret_payload

    def _doNotify(self, node, items_data, deliverPayloads, pep, recipient):
        if items_data and not deliverPayloads:
            for item_data in items_data:
                item_data.item.children = []
        self.dispatch({'items_data': items_data, 'node': node, 'pep': pep, 'recipient': recipient},
                      '//event/pubsub/notify')

    def getNotifications(self, node, items_data):
        """Build a list of subscriber to the node

        subscribers will be associated with subscribed items,
        and subscription type.
        """

        def toNotifications(subscriptions, items_data):
            subsBySubscriber = {}
            for subscription in subscriptions:
                if subscription.options.get('pubsub#subscription_type',
                                            'items') == 'items':
                    subs = subsBySubscriber.setdefault(subscription.subscriber,
                                                       set())
                    subs.add(subscription)

            notifications = [(subscriber, subscriptions_, items_data)
                             for subscriber, subscriptions_
                             in subsBySubscriber.items()]

            return notifications

        def rootNotFound(failure):
            failure.trap(error.NodeNotFound)
            return []

        d1 = node.getSubscriptions('subscribed')
        # FIXME: must add root node subscriptions ?
        # d2 = self.storage.getNode('', False) # FIXME: to check
        # d2.addCallback(lambda node: node.getSubscriptions('subscribed'))
        # d2.addErrback(rootNotFound)
        # d = defer.gatherResults([d1, d2])
        # d.addCallback(lambda result: result[0] + result[1])
        d1.addCallback(toNotifications, items_data)
        return d1

    def registerPublishNotifier(self, observerfn, *args, **kwargs):
        self.addObserver('//event/pubsub/notify', observerfn, *args, **kwargs)

    def registerRetractNotifier(self, observerfn, *args, **kwargs):
        self.addObserver('//event/pubsub/retract', observerfn, *args, **kwargs)

    def registerDeleteNotifier(self, observerfn, *args, **kwargs):
        self.addObserver('//event/pubsub/delete', observerfn, *args, **kwargs)

    def registerPurgeNotifier(self, observerfn, *args, **kwargs):
        self.addObserver('//event/pubsub/purge', observerfn, *args, **kwargs)

    def subscribe(self, nodeIdentifier, subscriber, requestor, pep, recipient):
        subscriberEntity = subscriber.userhostJID()
        if subscriberEntity != requestor.userhostJID():
            return defer.fail(error.Forbidden())

        d = self.storage.getNode(nodeIdentifier, pep, recipient)
        d.addCallback(_getAffiliation, subscriberEntity)
        d.addCallback(self._doSubscribe, subscriber, pep, recipient)
        return d

    def _doSubscribe(self, result, subscriber, pep, recipient):
        node, affiliation = result

        if affiliation == 'outcast':
            raise error.Forbidden()

        access_model = node.getAccessModel()

        if access_model == const.VAL_AMODEL_OPEN:
            d = defer.succeed(None)
        elif access_model == const.VAL_AMODEL_PRESENCE:
            d = self.checkPresenceSubscription(node, subscriber)
        elif access_model == const.VAL_AMODEL_PUBLISHER_ROSTER:
            d = self.checkRosterGroups(node, subscriber)
        elif access_model == const.VAL_AMODEL_WHITELIST:
            d = self.checkNodeAffiliations(node, subscriber)
        else:
            raise NotImplementedError

        def trapExists(failure):
            failure.trap(error.SubscriptionExists)
            return False

        def cb(sendLast):
            d = node.getSubscription(subscriber)
            if sendLast:
                d.addCallback(self._sendLastPublished, node, pep, recipient)
            return d

        d.addCallback(lambda _: node.addSubscription(subscriber, 'subscribed', {}))
        d.addCallbacks(lambda _: True, trapExists)
        d.addCallback(cb)

        return d

    def _sendLastPublished(self, subscription, node, pep, recipient):

        def notifyItem(items_data):
            if items_data:
                reactor.callLater(0, self.dispatch,
                                     {'items_data': items_data,
                                      'node': node,
                                      'pep': pep,
                                      'recipient': recipient,
                                      'subscription': subscription,
                                     },
                                     '//event/pubsub/notify')

        config = node.getConfiguration()
        sendLastPublished = config.get('pubsub#send_last_published_item',
                                       'never')
        if sendLastPublished == 'on_sub' and node.nodeType == 'leaf':
            entity = subscription.subscriber.userhostJID()
            d = defer.ensureDeferred(
                self.getItemsData(
                    node.nodeIdentifier, entity, recipient, maxItems=1, ext_data={'pep': pep}
                )
            )
            d.addCallback(notifyItem)
            d.addErrback(log.err)

        return subscription

    def unsubscribe(self, nodeIdentifier, subscriber, requestor, pep, recipient):
        if subscriber.userhostJID() != requestor.userhostJID():
            return defer.fail(error.Forbidden())

        d = self.storage.getNode(nodeIdentifier, pep, recipient)
        d.addCallback(lambda node: node.removeSubscription(subscriber))
        return d

    def getSubscriptions(self, requestor, nodeIdentifier, pep, recipient):
        """retrieve subscriptions of an entity

        @param requestor(jid.JID): entity who want to check subscriptions
        @param nodeIdentifier(unicode, None): identifier of the node
            node to get all subscriptions of a service
        @param pep(bool): True if it's a PEP request
        @param recipient(jid.JID, None): recipient of the PEP request
        """
        return self.storage.getSubscriptions(requestor, nodeIdentifier, pep, recipient)

    def supportsAutoCreate(self):
        return True

    def supportsInstantNodes(self):
        return True

    async def _createNode(
            self,
            nodeIdentifier: Optional[str],
            requestor: jid.JID,
            options: Optional[dict] = None,
            pep: bool = False,
            recipient: Optional[jid.JID] = None
    ) -> str:
        if pep:
            if recipient == self.server_jid:
                if not self.isAdmin(requestor):
                    raise error.Forbidden()
            elif requestor.userhostJID() != recipient.userhostJID():
                 raise error.Forbidden()

        if not nodeIdentifier:
            nodeIdentifier = 'generic/%s' % uuid.uuid4()

        if not options:
            options = {}

        nodeType = 'leaf'
        config = self.storage.getDefaultConfiguration(nodeType)
        config['pubsub#node_type'] = nodeType
        config.update(options)

        # TODO: handle schema on creation
        await self.storage.createNode(
            nodeIdentifier, requestor, config, None, pep, recipient
        )
        return nodeIdentifier

    def createNode(
            self,
            nodeIdentifier: Optional[str],
            requestor: jid.JID,
            options: Optional[dict] = None,
            pep: bool = False,
            recipient: Optional[jid.JID] = None
    ) -> defer.Deferred:
        return defer.ensureDeferred(self._createNode(
            nodeIdentifier=nodeIdentifier,
            requestor=requestor,
            options=options,
            pep=pep,
            recipient=recipient
        ))

    def getDefaultConfiguration(self, nodeType):
        d = defer.succeed(self.storage.getDefaultConfiguration(nodeType))
        return d

    def getNodeConfiguration(self, nodeIdentifier, pep, recipient):
        if not nodeIdentifier:
            return defer.fail(error.NoRootNode())

        d = self.storage.getNode(nodeIdentifier, pep, recipient)
        d.addCallback(lambda node: node.getConfiguration())

        return d

    def setNodeConfiguration(self, nodeIdentifier, options, requestor, pep, recipient):
        if not nodeIdentifier:
            return defer.fail(error.NoRootNode())

        d = self.storage.getNode(nodeIdentifier, pep, recipient)
        d.addCallback(_getAffiliation, requestor)
        d.addCallback(
            lambda result: defer.ensureDeferred(
                self._doSetNodeConfiguration(result, requestor, options))
        )
        return d

    async def _doSetNodeConfiguration(self, result, requestor, options):
        node, affiliation = result

        if affiliation != 'owner' and not self.isAdmin(requestor):
            raise error.Forbidden()

        max_items = options.get(const.OPT_MAX_ITEMS, '').strip().lower()
        if not max_items:
            pass
        elif max_items == 'max':
            # FIXME: we use "0" for max for now, but as "0" may be used as legal value
            #   in XEP-0060 ("max" is used otherwise), we should use "None" instead.
            #   This require a schema update, as NULL is not allowed at the moment
            options.fields[const.OPT_MAX_ITEMS].value = "0"
        else:
            # max_items is a number, we have to check that it's not bigger than the
            # total number of items on this node
            try:
                max_items = int(max_items)
            except ValueError:
                raise error.InvalidConfigurationValue('Invalid "max_items" value')
            else:
                options.fields[const.OPT_MAX_ITEMS].value = str(max_items)
            if max_items:
                items_count = await node.getItemsCount(None, True)
                if max_items < items_count:
                    raise error.ConstraintFailed(
                        "\"max_items\" can't be set to a value lower than the total "
                        "number of items on this node. Please increase \"max_items\" "
                        "or delete items from this node")

        return await node.setConfiguration(options)

    def getAffiliations(self, entity, nodeIdentifier, pep, recipient):
        return self.storage.getAffiliations(entity, nodeIdentifier, pep, recipient)

    def getAffiliationsOwner(self, nodeIdentifier, requestor, pep, recipient):
        d = self.storage.getNode(nodeIdentifier, pep, recipient)
        d.addCallback(_getAffiliation, requestor)
        d.addCallback(self._doGetAffiliationsOwner, requestor)
        return d

    def _doGetAffiliationsOwner(self, result, requestor):
        node, affiliation = result

        if affiliation != 'owner' and not self.isAdmin(requestor):
            raise error.Forbidden()
        return node.getAffiliations()

    def setAffiliationsOwner(self, nodeIdentifier, requestor, affiliations, pep, recipient):
        d = self.storage.getNode(nodeIdentifier, pep, recipient)
        d.addCallback(_getAffiliation, requestor)
        d.addCallback(self._doSetAffiliationsOwner, requestor, affiliations)
        return d

    def _doSetAffiliationsOwner(self, result, requestor, affiliations):
        # Check that requestor is allowed to set affiliations, and delete entities
        # with "none" affiliation

        # TODO: return error with failed affiliations in case of failure
        node, requestor_affiliation = result

        if requestor_affiliation != 'owner' and not self.isAdmin(requestor):
            raise error.Forbidden()

        # we don't allow requestor to change its own affiliation
        requestor_bare = requestor.userhostJID()
        if requestor_bare in affiliations and affiliations[requestor_bare] != 'owner':
            # FIXME: it may be interesting to allow the owner to ask for ownership removal
            #        if at least one other entity is owner for this node
            raise error.Forbidden("You can't change your own affiliation")

        to_delete = [jid_ for jid_, affiliation in affiliations.items() if affiliation == 'none']
        for jid_ in to_delete:
            del affiliations[jid_]

        if to_delete:
            d = node.deleteAffiliations(to_delete)
            if affiliations:
                d.addCallback(lambda dummy: node.setAffiliations(affiliations))
        else:
            d = node.setAffiliations(affiliations)

        return d

    def getSubscriptionsOwner(self, nodeIdentifier, requestor, pep, recipient):
        d = self.storage.getNode(nodeIdentifier, pep, recipient)
        d.addCallback(_getAffiliation, requestor)
        d.addCallback(self._doGetSubscriptionsOwner, requestor)
        return d

    def _doGetSubscriptionsOwner(self, result, requestor):
        node, affiliation = result

        if affiliation != 'owner' and not self.isAdmin(requestor):
            raise error.Forbidden()
        return node.getSubscriptions()

    def setSubscriptionsOwner(self, nodeIdentifier, requestor, subscriptions, pep, recipient):
        d = self.storage.getNode(nodeIdentifier, pep, recipient)
        d.addCallback(_getAffiliation, requestor)
        d.addCallback(self._doSetSubscriptionsOwner, requestor, subscriptions)
        return d

    def unwrapFirstError(self, failure):
        failure.trap(defer.FirstError)
        return failure.value.subFailure

    def _doSetSubscriptionsOwner(self, result, requestor, subscriptions):
        # Check that requestor is allowed to set subscriptions, and delete entities
        # with "none" subscription

        # TODO: return error with failed subscriptions in case of failure
        node, requestor_affiliation = result

        if requestor_affiliation != 'owner' and not self.isAdmin(requestor):
            raise error.Forbidden()

        d_list = []

        for subscription in subscriptions.copy():
            if subscription.state == 'none':
                subscriptions.remove(subscription)
                d_list.append(node.removeSubscription(subscription.subscriber))

        if subscriptions:
            d_list.append(node.setSubscriptions(subscriptions))

        d = defer.gatherResults(d_list, consumeErrors=True)
        d.addCallback(lambda _: None)
        d.addErrback(self.unwrapFirstError)
        return d

    def filterItemsWithSchema(self, items_data, schema, owner):
        """Check schema restriction and remove fields/items if they don't comply

        @param items_data(list[ItemData]): items to filter
            items in this list will be modified
        @param schema(domish.Element): node schema
        @param owner(bool): True is requestor is a owner of the node
        """
        fields_to_remove = set()
        for field_elt in schema.elements(data_form.NS_X_DATA, 'field'):
            for restrict_elt in field_elt.elements(const.NS_SCHEMA_RESTRICT, 'restrict'):
                read_restriction = restrict_elt.attributes.get('read')
                if read_restriction is not None:
                    if read_restriction == 'owner':
                        if not owner:
                            fields_to_remove.add(field_elt['var'])
                    else:
                        raise StanzaError('feature-not-implemented', text='unknown read restriction {}'.format(read_restriction))
        items_to_remove = []
        for idx, item_data in enumerate(items_data):
            item_elt = item_data.item
            try:
                x_elt = next(item_elt.elements(data_form.NS_X_DATA, 'x'))
            except StopIteration:
                log.msg("WARNING, item {id} has a schema but no form, ignoring it")
                items_to_remove.append(item_data)
                continue
            form = data_form.Form.fromElement(x_elt)
            # we remove fields which are not visible for this user
            for field in fields_to_remove:
                try:
                    form.removeField(form.fields[field])
                except KeyError:
                    continue
            item_elt.children.remove(x_elt)
            item_elt.addChild(form.toElement())

        for item_data in items_to_remove:
            items_data.remove(item_data)

    def checkPresenceSubscription(self, node, requestor):
        """check if requestor has presence subscription from node owner

        @param node(Node): node to check
        @param requestor(jid.JID): entity who want to access node
        """
        def gotRoster(roster):
            if roster is None:
                raise error.Forbidden()

            if requestor not in roster:
                raise error.Forbidden()

            if not roster[requestor].subscriptionFrom:
                raise error.Forbidden()

        d = defer.ensureDeferred(self.getOwnerRoster(node))
        d.addCallback(gotRoster)
        return d

    @defer.inlineCallbacks
    def checkRosterGroups(self, node, requestor):
        """check if requestor is in allowed groups of a node

        @param node(Node): node to check
        @param requestor(jid.JID): entity who want to access node
        """
        roster = yield defer.ensureDeferred(self.getOwnerRoster(node))

        if roster is None:
            raise error.Forbidden()

        if requestor not in roster:
            raise error.Forbidden()

        authorized_groups = yield node.getAuthorizedGroups()

        if not roster[requestor].groups.intersection(authorized_groups):
            # requestor is in roster but not in one of the allowed groups
            raise error.Forbidden()

    def checkNodeAffiliations(self, node, requestor):
        """check if requestor is in white list of a node

        @param node(Node): node to check
        @param requestor(jid.JID): entity who want to access node
        """
        def gotAffiliations(affiliations):
            try:
                affiliation = affiliations[requestor.userhostJID()]
            except KeyError:
                raise error.Forbidden()
            else:
                if affiliation not in ('owner', 'publisher', 'member'):
                    raise error.Forbidden()

        d = node.getAffiliations()
        d.addCallback(gotAffiliations)
        return d

    @defer.inlineCallbacks
    def checkNodeAccess(self, node, requestor):
        """check if a requestor can access data of a node

        @param node(Node): node to check
        @param requestor(jid.JID): entity who want to access node
        @return (tuple): permissions data with:
            - owner(bool): True if requestor is owner of the node
            - roster(None, ): roster of the requestor
                None if not needed/available
            - access_model(str): access model of the node
        @raise error.Forbidden: access is not granted
        @raise error.NotLeafNodeError: this node is not a leaf
        """
        node, affiliation = yield _getAffiliation(node, requestor)

        if not iidavoll.ILeafNode.providedBy(node):
            raise error.NotLeafNodeError()

        if affiliation == 'outcast':
            raise error.Forbidden()

        # node access check
        owner = affiliation == 'owner'
        access_model = node.getAccessModel()
        roster = None

        if access_model == const.VAL_AMODEL_OPEN or owner:
            pass
        elif access_model == const.VAL_AMODEL_PRESENCE:
            yield self.checkPresenceSubscription(node, requestor)
        elif access_model == const.VAL_AMODEL_PUBLISHER_ROSTER:
            # FIXME: for node, access should be renamed owner-roster, not publisher
            yield self.checkRosterGroups(node, requestor)
        elif access_model == const.VAL_AMODEL_WHITELIST:
            yield self.checkNodeAffiliations(node, requestor)
        else:
            raise Exception("Unknown access_model")

        defer.returnValue((affiliation, owner, roster, access_model))

    async def getItemsIds(
        self,
        nodeIdentifier: str,
        requestor: jid.JID,
        authorized_groups: Optional[List[str]],
        unrestricted: bool,
        maxItems: Optional[int] = None,
        ext_data: Optional[dict] = None,
        pep: bool = False,
        recipient: Optional[jid.JID] = None
    ) -> List[str]:
        """Retrieve IDs of items from a nodeIdentifier

        Requestor permission is checked before retrieving items IDs
        """
        # FIXME: items access model are not checked
        # TODO: check items access model
        node = await self.storage.getNode(nodeIdentifier, pep, recipient)
        await self.checkNodeAccess(node, requestor)
        ids = await node.getItemsIds(
            authorized_groups,
            unrestricted,
            maxItems,
            ext_data
        )
        return ids

    def getItems(self, nodeIdentifier, requestor, recipient, maxItems=None,
                       itemIdentifiers=None, ext_data=None):
        d = defer.ensureDeferred(
            self.getItemsData(
                nodeIdentifier, requestor, recipient, maxItems, itemIdentifiers, ext_data
            )
        )
        d.addCallback(lambda items_data: [item_data.item for item_data in items_data])
        return d

    async def getOwnerRoster(self, node, owners=None):
        # FIXME: roster of publisher, not owner, must be used
        if owners is None:
            owners = await node.getOwners()

        if len(owners) != 1:
            log.msg('publisher-roster access is not allowed with more than 1 owner')
            return

        owner_jid = owners[0]

        try:
            roster = await self.privilege.getRoster(owner_jid)
        except error.NotAllowedError:
            return
        except Exception as e:
            log.msg("Error while getting roster of {owner_jid}: {msg}".format(
                owner_jid = owner_jid.full(),
                msg = e))
            return
        return roster

    async def getItemsData(self, nodeIdentifier, requestor, recipient, maxItems=None,
                       itemIdentifiers=None, ext_data=None):
        """like getItems but return the whole ItemData"""
        if maxItems == 0:
            log.msg("WARNING: maxItems=0 on items retrieval")
            return []

        if ext_data is None:
            ext_data = {}
        node = await self.storage.getNode(nodeIdentifier, ext_data.get('pep', False), recipient)
        try:
            affiliation, owner, roster, access_model = await self.checkNodeAccess(node, requestor)
        except error.NotLeafNodeError:
            return []

        # at this point node access is checked

        if owner:
            # requestor_groups is only used in restricted access
            requestor_groups = None
        else:
            if roster is None:
                # FIXME: publisher roster should be used, not owner
                roster = await self.getOwnerRoster(node)
                if roster is None:
                    roster = {}
            roster_item = roster.get(requestor.userhostJID())
            requestor_groups = tuple(roster_item.groups) if roster_item else tuple()

        if itemIdentifiers:
            items_data = await node.getItemsById(requestor_groups, owner, itemIdentifiers)
        else:
            items_data = await node.getItems(requestor_groups, owner, maxItems, ext_data)

        if owner:
            # Add item config data form to items with roster access model
            for item_data in items_data:
                if item_data.access_model == const.VAL_AMODEL_OPEN:
                    pass
                elif item_data.access_model == const.VAL_AMODEL_PUBLISHER_ROSTER:
                    form = data_form.Form('submit', formNamespace=const.NS_ITEM_CONFIG)
                    access = data_form.Field(None, const.OPT_ACCESS_MODEL, value=const.VAL_AMODEL_PUBLISHER_ROSTER)
                    allowed = data_form.Field(None, const.OPT_ROSTER_GROUPS_ALLOWED, values=item_data.config[const.OPT_ROSTER_GROUPS_ALLOWED])
                    form.addField(access)
                    form.addField(allowed)
                    item_data.item.addChild(form.toElement())
                elif access_model == const.VAL_AMODEL_WHITELIST:
                    #FIXME
                    raise NotImplementedError
                else:
                    raise error.BadAccessTypeError(access_model)

        schema = node.getSchema()
        if schema is not None:
            self.filterItemsWithSchema(items_data, schema, owner)

        await self._items_rsm(
            items_data, node, requestor_groups, owner, itemIdentifiers, ext_data)
        return items_data

    def _setCount(self, value, response):
        response.count = value

    def _setIndex(self, value, response, adjust):
        """Set index in RSM response

        @param value(int): value of the reference index (i.e. before or after item)
        @param response(RSMResponse): response instance to fill
        @param adjust(int): adjustement term (i.e. difference between reference index and first item of the result)
        """
        response.index = value + adjust

    async def _items_rsm(self, items_data, node, authorized_groups, owner,
                   itemIdentifiers, ext_data):
        # FIXME: move this to a separate module
        # TODO: Index can be optimized by keeping a cache of the last RSM request
        #       An other optimisation would be to look for index first and use it as offset
        try:
            rsm_request = ext_data['rsm']
        except KeyError:
            # No RSM in this request, nothing to do
            return items_data

        if itemIdentifiers:
            log.msg("WARNING, itemIdentifiers used with RSM, ignoring the RSM part")
            return items_data

        response = rsm.RSMResponse()

        d_count = node.getItemsCount(authorized_groups, owner, ext_data)
        d_count.addCallback(self._setCount, response)
        d_list = [d_count]

        if items_data:
            response.first = items_data[0].item['id']
            response.last = items_data[-1].item['id']

            # index handling
            if rsm_request.index is not None:
                response.index = rsm_request.index
            elif rsm_request.before:
                # The last page case (before == '') is managed in render method
                d_index = node.getItemsIndex(rsm_request.before, authorized_groups, owner, ext_data)
                d_index.addCallback(self._setIndex, response, -len(items_data))
                d_list.append(d_index)
            elif rsm_request.after is not None:
                d_index = node.getItemsIndex(rsm_request.after, authorized_groups, owner, ext_data)
                d_index.addCallback(self._setIndex, response, 1)
                d_list.append(d_index)
            else:
                # the first page was requested
                response.index = 0


        await defer.DeferredList(d_list)

        if rsm_request.before == '':
            # the last page was requested
            response.index = response.count - len(items_data)

        items_data.append(container.ItemData(response.toElement()))

        return items_data

    async def retractItem(self, nodeIdentifier, itemIdentifiers, requestor, notify, pep, recipient):
        node = await self.storage.getNode(nodeIdentifier, pep, recipient)
        node, affiliation = await _getAffiliation(node, requestor)

        persistItems = node.getConfiguration()[const.OPT_PERSIST_ITEMS]

        if not persistItems:
            raise error.NodeNotPersistent()

        # we need to get the items before removing them, for the notifications

        if affiliation not in ['owner', 'publisher']:
            # the requestor doesn't have right to retract on the whole node
            # we check if he is a publisher for all items he wants to retract
            # and forbid the retraction else.
            publishers_map = await node.getItemsPublishers(itemIdentifiers)
            # TODO: the behaviour should be configurable (per node ?)
            if (any((requestor.userhostJID() != publisher.userhostJID()
                    for publisher in publishers_map.values()))
                and not self.isAdmin(requestor)
               ):
                raise error.Forbidden()

        items_data = await node.getItemsById(None, True, itemIdentifiers)
        # Remove the items and keep only actually removed ones in items_data
        removed = await node.removeItems(itemIdentifiers)
        retracted_items_data = [
            item_data for item_data in items_data if item_data.item["id"] in removed
        ]
        if nodeIdentifier.startswith(const.FDP_TEMPLATE_PREFIX):
            app_ns = nodeIdentifier[len(const.FDP_TEMPLATE_PREFIX):]
            submitted_node_id = f"{const.FDP_SUBMITTED_PREFIX}{app_ns}"
            submitted_node = await self.storage.getNode(submitted_node_id, pep, recipient)
            schema_items = await node.getItems([], True, maxItems=1)
            if not schema_items:
                # no more schema, we need to remove it from submitted node
                submitted_node = await self._getFDPSubmittedNode(
                    nodeIdentifier, pep, recipient)
                if submitted_node is not None:
                    submitted_node.setSchema(None)
            else:
                # not all items have been removed from the FDP template node, we check
                # if the last one correspond to current submitted node schema, and if not,
                # we update it.
                current_schema = next(schema_items[0].item.elements(
                    data_form.NS_X_DATA, 'x'))
                if current_schema == node.schema:
                    submitted_node = await self._getFDPSubmittedNode(
                        nodeIdentifier, pep, recipient)
                    if submitted_node is not None:
                        submitted_node.setSchema(current_schema)

        if notify:
            self._doNotifyRetraction(retracted_items_data, node, pep, recipient)

        return [r.item for r in retracted_items_data]

    def _doNotifyRetraction(self, items_data, node, pep, recipient):
        self.dispatch({'items_data': items_data,
                       'node': node,
                       'pep': pep,
                       'recipient': recipient},
                      '//event/pubsub/retract')

    async def purgeNode(self, nodeIdentifier, requestor, pep, recipient):
        node = await self.storage.getNode(nodeIdentifier, pep, recipient)
        node, affiliation = await _getAffiliation(node, requestor)
        persistItems = node.getConfiguration()[const.OPT_PERSIST_ITEMS]

        if affiliation != 'owner' and not self.isAdmin(requestor):
            raise error.Forbidden()

        if not persistItems:
            raise error.NodeNotPersistent()

        await node.purge()

        subscribers = await self.getSubscribers(nodeIdentifier, pep, recipient)

        # now we can send notifications
        self.dispatch(
            {
                'node': node,
                'pep': pep,
                'recipient': recipient,
                'subscribers': subscribers,
            },
            '//event/pubsub/purge'
        )

    def getSubscribers(self, nodeIdentifier, pep, recipient):
        def cb(subscriptions):
            return [subscription.subscriber for subscription in subscriptions]

        d = self.storage.getNode(nodeIdentifier, pep, recipient)
        d.addCallback(lambda node: node.getSubscriptions('subscribed'))
        d.addCallback(cb)
        return d

    async def deleteNode(
        self,
        nodeIdentifier: str,
        requestor: jid.JID,
        pep: bool,
        recipient: jid.JID,
        redirectURI: str = None
    ) -> None:
        node = await self.storage.getNode(nodeIdentifier, pep, recipient)
        node, affiliation = await _getAffiliation(node, requestor)

        if affiliation != 'owner' and not self.isAdmin(requestor):
            raise error.Forbidden()

        # we have to get subscribers (for notifications) before the node is deleted
        subscribers = await self.getSubscribers(nodeIdentifier, pep, recipient)

        await self.storage.deleteNodeByDbId(node.nodeDbId)

        if node.nodeIdentifier.startswith(const.FDP_TEMPLATE_PREFIX):
            # we need to delete the associated schema
            submitted_node = await self._getFDPSubmittedNode(
                node.nodeIdentifier, pep, recipient)
            if submitted_node is not None:
                await submitted_node.setSchema(None)

        # now we can send notifications
        self.dispatch(
            {
                'node': node,
                'pep': pep,
                'recipient': recipient,
                'redirectURI': redirectURI,
                'subscribers': subscribers,
            },
            '//event/pubsub/delete'
        )


class PubSubResourceFromBackend(pubsub.PubSubResource):
    """
    Adapts a backend to an xmpp publish-subscribe service.
    """

    features = [
        "config-node",
        "create-nodes",
        "delete-any",
        "delete-nodes",
        "item-ids",
        "meta-data",
        "publish",
        "purge-nodes",
        "retract-items",
        "retrieve-affiliations",
        "retrieve-default",
        "retrieve-items",
        "retrieve-subscriptions",
        "subscribe",
    ]

    discoIdentity = disco.DiscoIdentity('pubsub',
                                        'service',
                                        const.SERVICE_NAME)

    pubsubService = None

    _errorMap = {
        error.NodeNotFound: ('item-not-found', None, None),
        error.NodeExists: ('conflict', None, None),
        error.Forbidden: ('forbidden', None, None),
        error.NotAuthorized: ('not-authorized', None, None),
        error.ItemNotFound: ('item-not-found', None, None),
        error.ItemForbidden: ('bad-request', 'item-forbidden', None),
        error.ItemRequired: ('bad-request', 'item-required', None),
        error.NoInstantNodes: ('not-acceptable',
                               'unsupported',
                               'instant-nodes'),
        error.NotSubscribed: ('unexpected-request', 'not-subscribed', None),
        error.InvalidConfigurationOption: ('not-acceptable', None, None),
        error.InvalidConfigurationValue: ('not-acceptable', None, None),
        error.NodeNotPersistent: ('feature-not-implemented',
                                  'unsupported',
                                  'persistent-node'),
        error.NoRootNode: ('bad-request', None, None),
        error.NoCollections: ('feature-not-implemented',
                              'unsupported',
                              'collections'),
        error.NoPublishing: ('feature-not-implemented',
                             'unsupported',
                             'publish'),
        error.ConstraintFailed: ('conflict', 'precondition-not-met', None),
    }

    def __init__(self, backend):
        pubsub.PubSubResource.__init__(self)

        self.backend = backend
        self.hideNodes = False

        self.__class__.discoIdentity.name = backend.config["service_name"]

        self.backend.registerPublishNotifier(self._notifyPublish)
        self.backend.registerRetractNotifier(self._notifyRetract)
        self.backend.registerDeleteNotifier(self._notifyDelete)
        self.backend.registerPurgeNotifier(self._notifyPurge)

        if self.backend.supportsAutoCreate():
            self.features.append("auto-create")

        if self.backend.supportsPublishOptions():
            self.features.append("publish-options")

        if self.backend.supportsInstantNodes():
            self.features.append("instant-nodes")

        if self.backend.supportsOutcastAffiliation():
            self.features.append("outcast-affiliation")

        if self.backend.supportsPersistentItems():
            self.features.append("persistent-items")

        if self.backend.supportsPublisherAffiliation():
            self.features.append("publisher-affiliation")

        if self.backend.supportsGroupBlog():
            self.features.append("groupblog")

        # XXX: this feature is not really described in XEP-0060, we just can see it in
        #      examples but it's necessary for microblogging comments (see XEP-0277)
        if self.backend.supportsPublishModel():
            self.features.append("publish_model")

    def getFullItem(self, item_data):
        """ Attach item configuration to this item

        Used to give item configuration back to node's owner (and *only* to owner)
        """
        # TODO: a test should check that only the owner get the item configuration back

        item, item_config = item_data.item, item_data.config
        if item_config:
            new_item = elementCopy(item)
            new_item.addChild(item_config.toElement())
            return new_item
        else:
            return item

    def _notifyPublish(self, data: dict) -> defer.Deferred:
        return defer.ensureDeferred(self.notifyPublish(data))

    async def notifyPublish(self, data: dict) -> None:
        items_data = data['items_data']
        node = data['node']
        pep = data['pep']
        recipient = data['recipient']

        owners, notifications_filtered = await self._prepareNotify(
            items_data, node, data.get('subscription'), pep, recipient
        )

        # we notify the owners
        # FIXME: check if this comply with XEP-0060 (option needed ?)
        # TODO: item's access model have to be sent back to owner
        # TODO: same thing for getItems

        for owner_jid in owners:
            notifications_filtered.append(
                (owner_jid,
                 {pubsub.Subscription(node.nodeIdentifier,
                                      owner_jid,
                                      'subscribed')},
                 [self.getFullItem(item_data) for item_data in items_data]))

        if pep:
            self.backend.privilege.notifyPublish(
                recipient,
                node.nodeIdentifier,
                notifications_filtered
            )

        else:
            self.pubsubService.notifyPublish(
                self.serviceJID,
                node.nodeIdentifier,
                notifications_filtered)

    def _notifyRetract(self, data: dict) -> defer.Deferred:
        return defer.ensureDeferred(self.notifyRetract(data))

    async def notifyRetract(self, data: dict) -> None:
        items_data = data['items_data']
        node = data['node']
        pep = data['pep']
        recipient = data['recipient']

        owners, notifications_filtered = await self._prepareNotify(
            items_data, node, data.get('subscription'), pep, recipient
        )

        #we add the owners

        for owner_jid in owners:
            notifications_filtered.append(
                (owner_jid,
                 {pubsub.Subscription(node.nodeIdentifier,
                                      owner_jid,
                                      'subscribed')},
                 [item_data.item for item_data in items_data]))

        if pep:
            return self.backend.privilege.notifyRetract(
                recipient,
                node.nodeIdentifier,
                notifications_filtered)

        else:
            return self.pubsubService.notifyRetract(
                self.serviceJID,
                node.nodeIdentifier,
                notifications_filtered)

    async def _prepareNotify(
        self,
        items_data: Tuple[domish.Element, str, dict],
        node,
        subscription: Optional[pubsub.Subscription] = None,
        pep: bool = False,
        recipient: Optional[jid.JID] = None
    ) -> Tuple:
        """Do a bunch of permissions check and filter notifications

        The owner is not added to these notifications,
        it must be added by the calling method
        @param items_data: must contain:
            - item
            - access_model
            - access_list (dict as returned getItemsById, or item_config)
        @param node(LeafNode): node hosting the items
        @param subscription: TODO

        @return: will contain:
            - notifications_filtered
            - node_owner_jid
            - items_data
        """
        if subscription is None:
            notifications = await self.backend.getNotifications(node, items_data)
        else:
            notifications = [(subscription.subscriber, [subscription], items_data)]

        if ((pep
             and node.getConfiguration()[const.OPT_ACCESS_MODEL] in ('open', 'presence')
           )):
            # for PEP we need to manage automatic subscriptions (cf. XEP-0163 §4)
            explicit_subscribers = {subscriber for subscriber, _, _ in notifications}
            auto_subscribers = await self.backend.privilege.getAutoSubscribers(
                recipient, node.nodeIdentifier, explicit_subscribers
            )
            for sub_jid in auto_subscribers:
                 sub = pubsub.Subscription(node.nodeIdentifier, sub_jid, 'subscribed')
                 notifications.append((sub_jid, [sub], items_data))

        owners = await node.getOwners()
        owner_roster = None

        # now we check access of subscriber for each item, and keep only allowed ones

        #we filter items not allowed for the subscribers
        notifications_filtered = []
        schema = node.getSchema()

        for subscriber, subscriptions, items_data in notifications:
            subscriber_bare = subscriber.userhostJID()
            if subscriber_bare in owners:
                # as notification is always sent to owner,
                # we ignore owner if he is here
                continue
            allowed_items = [] #we keep only item which subscriber can access

            if schema is not None:
                # we have to copy items_data because different subscribers may receive
                # different items (e.g. read restriction in schema)
                items_data = [itemDataCopy(item_data) for item_data in items_data]
                self.backend.filterItemsWithSchema(items_data, schema, False)

            for item_data in items_data:
                item, access_model = item_data.item, item_data.access_model
                access_list = item_data.config
                if access_model == const.VAL_AMODEL_OPEN:
                    allowed_items.append(item)
                elif access_model == const.VAL_AMODEL_PUBLISHER_ROSTER:
                    if owner_roster is None:
                        # FIXME: publisher roster should be used, not owner
                        owner_roster= await self.backend.getOwnerRoster(node, owners)
                    if owner_roster is None:
                        owner_roster = {}
                    if not subscriber_bare in owner_roster:
                        continue
                    #the subscriber is known, is he in the right group ?
                    authorized_groups = access_list[const.OPT_ROSTER_GROUPS_ALLOWED]
                    if owner_roster[subscriber_bare].groups.intersection(authorized_groups):
                        allowed_items.append(item)
                else: #unknown access_model
                    # TODO: white list access
                    raise NotImplementedError

            if allowed_items:
                notifications_filtered.append((subscriber, subscriptions, allowed_items))

        return (owners, notifications_filtered)

    async def _aNotifyDelete(self, data):
        nodeIdentifier = data['node'].nodeIdentifier
        pep = data['pep']
        recipient = data['recipient']
        redirectURI = data.get('redirectURI', None)
        subscribers = data['subscribers']
        if pep:
            self.backend.privilege.notifyDelete(
                recipient,
                nodeIdentifier,
                subscribers,
                redirectURI
            )
        else:
            self.pubsubService.notifyDelete(
                self.serviceJID,
                nodeIdentifier,
                subscribers,
                redirectURI
            )

    def _notifyDelete(self, data):
        d = defer.ensureDeferred(self._aNotifyDelete(data))
        d.addErrback(log.err)

    async def _aNotifyPurge(self, data):
        nodeIdentifier = data['node'].nodeIdentifier
        pep = data['pep']
        recipient = data['recipient']
        subscribers = data['subscribers']
        if pep:
            self.backend.privilege.notifyPurge(
                recipient,
                nodeIdentifier,
                subscribers,
            )
        else:
            self.pubsubService.notifyPurge(
                self.serviceJID,
                nodeIdentifier,
                subscribers,
            )

    def _notifyPurge(self, data):
        d = defer.ensureDeferred(self._aNotifyPurge(data))
        d.addErrback(log.err)

    def _mapErrors(self, failure):
        e = failure.trap(*list(self._errorMap.keys()))

        condition, pubsubCondition, feature = self._errorMap[e]
        msg = failure.value.msg

        if pubsubCondition:
            exc = pubsub.PubSubError(condition, pubsubCondition, feature, msg)
        else:
            exc = StanzaError(condition, text=msg)

        raise exc

    async def _getInfo(
        self,
        requestor: jid.JID,
        service: jid.JID,
        nodeIdentifier: str,
        pep: bool = False,
        recipient: Optional[jid.JID] = None
    ) -> Optional[dict]:
        if not requestor.resource:
            # this avoid error when getting a disco request from server during namespace
            # delegation
            return None
        info = {}
        try:
            info["type"] = await self.backend.getNodeType(nodeIdentifier, pep, recipient)
            info["meta-data"] = await self.backend.getNodeMetaData(
                nodeIdentifier, pep, recipient
            )
        except error.NodeNotFound:
            info["meta-data"] = None
            return None
        except failure.Failure as e:
            self._mapErrors(e)
        except Exception as e:
            self._mapErrors(failure.Failure(e))
        else:
            return info

    def getInfo(self, requestor, service, nodeIdentifier):
        try:
            pep = service.delegated
        except AttributeError:
            pep = False
            recipient = None
        else:
            recipient = service if pep else None
        return defer.ensureDeferred(
            self._getInfo(
                requestor, service, nodeIdentifier, pep, recipient
            )
        )

    async def _getNodes(self, requestor, service, nodeIdentifier):
        """return nodes for disco#items

        Pubsub/PEP nodes will be returned if disco node is not specified
        else Pubsub/PEP items will be returned
        (according to what requestor can access)
        """
        try:
            pep = service.pep
        except AttributeError:
            pep = False

        if self.hideNodes or service.resource:
            return []

        if nodeIdentifier:
            items = await self.backend.getItemsIds(
                nodeIdentifier,
                requestor,
                [],
                requestor.userhostJID() == service,
                None,
                None,
                pep,
                service
            )
            # items must be set as name, not node
            return [(None, item) for item in items]
        else:
            try:
                return await self.backend.getNodes(
                    requestor.userhostJID(),
                    pep,
                    service
                )
            except failure.Failure as e:
                self._mapErrors(e)
            except Exception as e:
                self._mapErrors(failure.Failure(e))

    def getNodes(self, requestor, service, nodeIdentifier):
        return defer.ensureDeferred(self._getNodes(requestor, service, nodeIdentifier))

    def getConfigurationOptions(self):
        return self.backend.nodeOptions

    def _publish_errb(self, failure, request):
        if failure.type == error.NodeNotFound and self.backend.supportsAutoCreate():
            print(f"Auto-creating node {request.nodeIdentifier}")
            d = self.backend.createNode(request.nodeIdentifier,
                                        request.sender,
                                        request.options,
                                        pep=self._isPep(request),
                                        recipient=request.recipient)
            d.addCallback(
                lambda __, request: defer.ensureDeferred(self.backend.publish(
                    request.nodeIdentifier,
                    request.items,
                    request.sender,
                    request.options,
                    self._isPep(request),
                    request.recipient,
                )),
                request,
            )
            return d

        return failure

    def _isPep(self, request):
        try:
            return request.delegated
        except AttributeError:
            return False

    def publish(self, request):
        d = defer.ensureDeferred(self.backend.publish(
            request.nodeIdentifier,
            request.items,
            request.sender,
            request.options,
            self._isPep(request),
            request.recipient
        ))
        d.addErrback(self._publish_errb, request)
        return d.addErrback(self._mapErrors)

    def subscribe(self, request):
        d = self.backend.subscribe(request.nodeIdentifier,
                                   request.subscriber,
                                   request.sender,
                                   self._isPep(request),
                                   request.recipient)
        return d.addErrback(self._mapErrors)

    def unsubscribe(self, request):
        d = self.backend.unsubscribe(request.nodeIdentifier,
                                     request.subscriber,
                                     request.sender,
                                     self._isPep(request),
                                     request.recipient)
        return d.addErrback(self._mapErrors)

    def subscriptions(self, request):
        d = self.backend.getSubscriptions(request.sender,
                                          request.nodeIdentifier,
                                          self._isPep(request),
                                          request.recipient)
        return d.addErrback(self._mapErrors)

    def affiliations(self, request):
        """Retrieve affiliation for normal entity (cf. XEP-0060 §5.7)

        retrieve all node where this jid is affiliated
        """
        d = self.backend.getAffiliations(request.sender,
                                         request.nodeIdentifier,
                                         self._isPep(request),
                                         request.recipient)
        return d.addErrback(self._mapErrors)

    def create(self, request):
        d = self.backend.createNode(request.nodeIdentifier,
                                    request.sender, request.options,
                                    self._isPep(request),
                                    request.recipient)
        return d.addErrback(self._mapErrors)

    def default(self, request):
        d = self.backend.getDefaultConfiguration(request.nodeType,
                                                 self._isPep(request),
                                                 request.sender)
        return d.addErrback(self._mapErrors)

    def configureGet(self, request):
        d = self.backend.getNodeConfiguration(request.nodeIdentifier,
                                              self._isPep(request),
                                              request.recipient)
        return d.addErrback(self._mapErrors)

    def configureSet(self, request):
        d = self.backend.setNodeConfiguration(request.nodeIdentifier,
                                              request.options,
                                              request.sender,
                                              self._isPep(request),
                                              request.recipient)
        return d.addErrback(self._mapErrors)

    def affiliationsGet(self, request):
        """Retrieve affiliations for owner (cf. XEP-0060 §8.9.1)

        retrieve all affiliations for a node
        """
        d = self.backend.getAffiliationsOwner(request.nodeIdentifier,
                                              request.sender,
                                              self._isPep(request),
                                              request.recipient)
        return d.addErrback(self._mapErrors)

    def affiliationsSet(self, request):
        d = self.backend.setAffiliationsOwner(request.nodeIdentifier,
                                              request.sender,
                                              request.affiliations,
                                              self._isPep(request),
                                              request.recipient)
        return d.addErrback(self._mapErrors)

    def subscriptionsGet(self, request):
        """Retrieve subscriptions for owner (cf. XEP-0060 §8.8.1)

        retrieve all affiliations for a node
        """
        d = self.backend.getSubscriptionsOwner(request.nodeIdentifier,
                                               request.sender,
                                               self._isPep(request),
                                               request.recipient)
        return d.addErrback(self._mapErrors)

    def subscriptionsSet(self, request):
        d = self.backend.setSubscriptionsOwner(request.nodeIdentifier,
                                              request.sender,
                                              request.subscriptions,
                                              self._isPep(request),
                                              request.recipient)
        return d.addErrback(self._mapErrors)

    def items(self, request):
        ext_data = {}
        if const.FLAG_ENABLE_RSM and request.rsm is not None:
            if request.rsm.max < 0:
                raise pubsub.BadRequest(text="max can't be negative")
            ext_data['rsm'] = request.rsm
        try:
            ext_data['pep'] = request.delegated
        except AttributeError:
            pass
        ext_data['order_by'] = request.orderBy or []
        d = self.backend.getItems(request.nodeIdentifier,
                                  request.sender,
                                  request.recipient,
                                  request.maxItems,
                                  request.itemIdentifiers,
                                  ext_data)
        return d.addErrback(self._mapErrors)

    def retract(self, request):
        d = defer.ensureDeferred(
            self.backend.retractItem(request.nodeIdentifier,
                                     request.itemIdentifiers,
                                     request.sender,
                                     request.notify,
                                     self._isPep(request),
                                     request.recipient)
        )
        return d.addErrback(self._mapErrors)

    def purge(self, request):
        d = defer.ensureDeferred(
            self.backend.purgeNode(request.nodeIdentifier,
                                   request.sender,
                                   self._isPep(request),
                                   request.recipient)
        )
        return d.addErrback(self._mapErrors)

    def delete(self, request):
        d = defer.ensureDeferred(
            self.backend.deleteNode(request.nodeIdentifier,
                                    request.sender,
                                    self._isPep(request),
                                    request.recipient)
        )
        return d.addErrback(self._mapErrors)

components.registerAdapter(PubSubResourceFromBackend,
                           iidavoll.IBackendService,
                           iwokkel.IPubSubResource)



@implementer(iwokkel.IDisco)
class ExtraDiscoHandler(XMPPHandler):
    # see comment in twisted/plugins/pubsub.py
    # FIXME: upstream must be fixed so we can use custom (non pubsub#) disco features

    def getDiscoInfo(self, requestor, service, nodeIdentifier=''):
        return [
            disco.DiscoFeature(rsm.NS_RSM),
            # cf. https://xmpp.org/extensions/xep-0060.html#subscriber-retrieve-returnsome
            disco.DiscoFeature(const.NS_PUBSUB_RSM),
            disco.DiscoFeature(pubsub.NS_ORDER_BY),
            disco.DiscoFeature(const.NS_FDP)
        ]

    def getDiscoItems(self, requestor, service, nodeIdentifier=''):
        return []
