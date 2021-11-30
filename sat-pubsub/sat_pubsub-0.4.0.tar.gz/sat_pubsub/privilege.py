#!/usr/bin/env python3
#
# Copyright (c) 2015-2021 Jérôme Poisson


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

"This module implements XEP-0356 (Privileged Entity) to manage rosters, messages and "
"presences"

from typing import Dict, List, Optional, Set
import time

from twisted.internet import defer
from twisted.python import log
from twisted.python import failure
from twisted.words.protocols.jabber import error, jid
from twisted.words.xish import domish
from wokkel import xmppim
from wokkel import pubsub
from wokkel import disco
from wokkel.compat import IQ
from wokkel.iwokkel import IPubSubService

from .error import NotAllowedError

FORWARDED_NS = 'urn:xmpp:forward:0'
PRIV_ENT_NS = 'urn:xmpp:privilege:1'
PRIV_ENT_ADV_XPATH = '/message/privilege[@xmlns="{}"]'.format(PRIV_ENT_NS)
ROSTER_NS = 'jabber:iq:roster'
PERM_ROSTER = 'roster'
PERM_MESSAGE = 'message'
PERM_PRESENCE = 'presence'
ALLOWED_ROSTER = ('none', 'get', 'set', 'both')
ALLOWED_MESSAGE = ('none', 'outgoing')
ALLOWED_PRESENCE = ('none', 'managed_entity', 'roster')
TO_CHECK = {
    PERM_ROSTER:ALLOWED_ROSTER,
    PERM_MESSAGE:ALLOWED_MESSAGE,
    PERM_PRESENCE:ALLOWED_PRESENCE
}

# Number of seconds before a roster cache is not considered valid anymore.
# We keep this delay to avoid requesting roster too much in a row if an entity is
# connecting/disconnecting often in a short time.
ROSTER_TTL = 3600


Roster = Dict[jid.JID, xmppim.RosterItem]


class InvalidStanza(Exception):
    pass

class PrivilegesHandler(disco.DiscoClientProtocol):
    # FIXME: need to manage updates, XEP-0356 must be updated to get roster pushes
    # TODO: cache

    def __init__(self, service_jid):
        super(PrivilegesHandler, self).__init__()
        self.backend = None
        self._permissions = {PERM_ROSTER: 'none',
                             PERM_MESSAGE: 'none',
                             PERM_PRESENCE: 'none'}
        self._pubsub_service = None
        self.caps_map = {}  # key: bare jid, value: dict of resources with caps hash
        # key: (hash,version), value: dict with DiscoInfo instance (infos) and nodes to
        # notify (notify)
        self.hash_map = {}
        # dict which will be filled from database once connection is initialized,
        # key: jid, value: dict with "timestamp" and "roster"
        self.roster_cache = None
        # key: jid, value: set of entities who need to receive a notification when we
        #   get a presence from them. All entities in value have a presence subscription
        #   to the key entity.
        self.presence_map = {}
        # resource currently online
        self.presences = set()

    @property
    def permissions(self):
        return self._permissions

    async def getRosterCacheFromDB(self):
        rows = await self.backend.storage.getRosterCache()
        for __, owner_jid, version, timestamp, roster_elt in rows:
            roster = self.getRosterFromElement(roster_elt)
            self.roster_cache[owner_jid] = {
                "timestamp": timestamp,
                "roster": roster,
                "version": version
            }
            self.updatePresenceMap(owner_jid, roster, None)

    def connectionInitialized(self):
        for handler in self.parent.handlers:
            if IPubSubService.providedBy(handler):
                self._pubsub_service = handler
                break
        self.backend = self.parent.parent.getServiceNamed('backend')
        self.xmlstream.addObserver(PRIV_ENT_ADV_XPATH, self.onAdvertise)
        self.xmlstream.addObserver('/presence', self._onPresence)
        if self.roster_cache is None:
            self.roster_cache = {}
            defer.ensureDeferred(self.getRosterCacheFromDB())

    def onAdvertise(self, message):
        """Managage the <message/> advertising privileges

        self._permissions will be updated according to advertised privileged
        """
        privilege_elt = next(message.elements(PRIV_ENT_NS, 'privilege'))
        for perm_elt in privilege_elt.elements(PRIV_ENT_NS):
            try:
                if perm_elt.name != 'perm':
                    raise InvalidStanza('unexpected element {}'.format(perm_elt.name))
                perm_access = perm_elt['access']
                perm_type = perm_elt['type']
                try:
                    if perm_type not in TO_CHECK[perm_access]:
                        raise InvalidStanza(
                            'bad type [{}] for permission {}'
                            .format(perm_type, perm_access)
                        )
                except KeyError:
                    raise InvalidStanza('bad permission [{}]'.format(perm_access))
            except InvalidStanza as e:
                log.msg(
                    f"Invalid stanza received ({e}), setting permission to none"
                )
                for perm in self._permissions:
                    self._permissions[perm] = 'none'
                break

            self._permissions[perm_access] = perm_type or 'none'

        log.msg(
            'Privileges updated: roster={roster}, message={message}, presence={presence}'
            .format(**self._permissions)
        )

    ## roster ##

    def updatePresenceMap(
        self,
        owner_jid: jid.JID,
        roster: Roster,
        old_roster: Optional[Roster]
    ) -> None:
        """Update ``self.presence_map`` from roster

        @param owner_jid: jid of the owner of the roster
        @param roster: roster dict as returned by self.getRoster
        @param old_roster: previously cached roster if any
        """
        if old_roster is not None:
            # we check if presence subscription have not been removed and update
            # presence_map accordingly
            for roster_jid, roster_item in old_roster.items():
                if ((roster_item.subscriptionFrom
                     and (roster_jid not in roster
                          or not roster[roster_jid].subscriptionFrom)
                     )):
                    try:
                        self.presence_map[roster_jid].discard(owner_jid)
                    except KeyError:
                        pass
                if ((roster_item.subscriptionTo
                     and (roster_jid not in roster
                          or not roster[roster_jid].subscriptionTo)
                     )):
                    try:
                        self.presence_map[owner_jid].discard(roster_jid)
                    except KeyError:
                        pass

        for roster_jid, roster_item in roster.items():
            if roster_item.subscriptionFrom:
                # we need to know who is subscribed to our user, to send them
                # notifications when they send presence to us
                self.presence_map.setdefault(roster_jid, set()).add(owner_jid)
            if ((roster_item.subscriptionTo
                 and jid.JID(roster_jid.host) == self.backend.server_jid)):
                # we also need to know who on this server we are subscribed to, so
                # we can get their notifications even if they didn't connect so far.
                self.presence_map.setdefault(owner_jid, set()).add(roster_jid)

    def serialiseRoster(
        self,
        roster: Roster,
        version: Optional[str] = None
    ) -> domish.Element:
        """Reconstruct Query element of the roster"""
        roster_elt = domish.Element((ROSTER_NS, "query"))
        if version:
            roster_elt["ver"] = version
        for item in roster.values():
            roster_elt.addChild(item.toElement())
        return roster_elt

    async def updateRosterCache(
        self,
        owner_jid: jid.JID,
        roster: Roster,
        version: str
    ) -> None:
        """Update local roster cache and database"""
        now = time.time()
        self.roster_cache[owner_jid] = {
            'timestamp': now,
            'roster': roster,
            'version': version
        }
        roster_elt = self.serialiseRoster(roster, version)
        await self.backend.storage.setRosterCache(
            owner_jid, version, now, roster_elt
        )

    def getRosterFromElement(self, query_elt: domish.Element) -> Roster:
        """Parse roster query result payload to get a Roster dict"""
        roster = {}
        for element in query_elt.elements(ROSTER_NS, 'item'):
            item = xmppim.RosterItem.fromElement(element)
            roster[item.entity] = item
        return roster

    async def getRoster(self, to_jid: jid.JID) -> Optional[Roster]:
        """Retrieve contact list.

        @param to_jid: jid of the entity owning the roster
        @return: roster data
        """
        if jid.JID(to_jid.host) != self.backend.server_jid:
            # no need to try to get the roster if it's not a user of our own server
            return None
        if self._permissions[PERM_ROSTER] not in ('get', 'both'):
            raise NotAllowedError('roster get is not allowed')

        iq = IQ(self.xmlstream, 'get')
        iq.addElement((ROSTER_NS, 'query'))
        iq["to"] = to_jid.userhost()
        iq_result = await iq.send()
        roster = self.getRosterFromElement(iq_result.query)

        version = iq_result.query.getAttribute('ver')
        cached_roster = self.roster_cache.get("to_jid")
        if not cached_roster:
            self.updatePresenceMap(to_jid, roster, None)
            await self.updateRosterCache(to_jid, roster, version)
        else:
            # we already have a roster in cache, we have to check it if the new one is
            # modified, and update presence_map and database
            if version:
                if cached_roster["version"] != version:
                    self.updatePresenceMap(to_jid, roster, cached_roster["roster"])
                    await self.updateRosterCache(to_jid, roster, version)
                else:
                    cached_roster["timestamp"] = time.time()
            else:
                # no version available, we have to compare the whole XML
                if ((self.serialiseRoster(cached_roster["roster"]).toXml() !=
                     self.serialiseRoster(roster))):
                    self.updatePresenceMap(to_jid, roster, cached_roster["roster"])
                    await self.updateRosterCache(to_jid, roster, version)
                else:
                    cached_roster["timestamp"] = time.time()

        return roster

    async def isSubscribedFrom(self, entity: jid.JID, roster_owner_jid: jid.JID) -> bool:
        """Check if entity has presence subscription from roster_owner_jid

        @param entity: entity to check subscription to
        @param roster_owner_jid: owner of the roster to check
        @return: True if entity has a subscription from roster_owner_jid
        """
        roster = await self.getRoster(roster_owner_jid)
        try:
            return roster[entity.userhostJID()].subscriptionFrom
        except KeyError:
            return False

    ## message ##

    def sendMessage(self, priv_message, to_jid=None):
        """Send privileged message (in the name of the server)

        @param priv_message(domish.Element): privileged message
        @param to_jid(jid.JID, None): main message destinee
            None to use our own server
        """
        if self._permissions[PERM_MESSAGE] not in ('outgoing',):
            log.msg("WARNING: permission not allowed to send privileged messages")
            raise NotAllowedError('privileged messages are not allowed')

        main_message = domish.Element((None, "message"))
        if to_jid is None:
            to_jid = self.backend.server_jid
        main_message['to'] = to_jid.full()
        privilege_elt = main_message.addElement((PRIV_ENT_NS, 'privilege'))
        forwarded_elt = privilege_elt.addElement((FORWARDED_NS, 'forwarded'))
        priv_message['xmlns'] = 'jabber:client'
        forwarded_elt.addChild(priv_message)
        self.send(main_message)

    def notifyPublish(self, pep_jid, nodeIdentifier, notifications):
        """Do notifications using privileges"""
        for subscriber, subscriptions, items in notifications:
            message = self._pubsub_service._createNotification(
                'items',
                pep_jid,
                nodeIdentifier,
                subscriber,
                subscriptions
            )
            for item in items:
                item.uri = pubsub.NS_PUBSUB_EVENT
                message.event.items.addChild(item)
            self.sendMessage(message)

    def notifyRetract(self, pep_jid, nodeIdentifier, notifications):
        for subscriber, subscriptions, items in notifications:
            message = self._pubsub_service._createNotification(
                'items',
                pep_jid,
                nodeIdentifier,
                subscriber,
                subscriptions
            )
            for item in items:
                retract = domish.Element((None, "retract"))
                retract['id'] = item['id']
                message.event.items.addChild(retract)
            self.sendMessage(message)

    def notifyDelete(self, pep_jid, nodeIdentifier, subscribers, redirectURI=None):
        for subscriber in subscribers:
            message = self._pubsub_service._createNotification(
                'delete',
                pep_jid,
                nodeIdentifier,
                subscriber
            )
            if redirectURI:
                redirect = message.event.delete.addElement('redirect')
                redirect['uri'] = redirectURI
            self.sendMessage(message)

    def notifyPurge(self, pep_jid, nodeIdentifier, subscribers):
        for subscriber in subscribers:
            message = self._pubsub_service._createNotification(
                'purge',
                pep_jid,
                nodeIdentifier,
                subscriber
            )
            self.sendMessage(message)

    ## presence ##

    def _onPresence(self, presence_elt: domish.Element) -> None:
        defer.ensureDeferred(self.onPresence(presence_elt))

    async def onPresence(self, presence_elt: domish.Element) -> None:
        from_jid = jid.JID(presence_elt['from'])
        from_jid_bare = from_jid.userhostJID()
        if ((jid.JID(from_jid.host) == self.backend.server_jid
             and (
                 from_jid_bare not in self.roster_cache
                 or time.time()-self.roster_cache[from_jid_bare]["timestamp"]>ROSTER_TTL
             ))):
            roster = await self.getRoster(from_jid)

        presence_type = presence_elt.getAttribute('type')
        if presence_type == "unavailable":
            self.presences.discard(from_jid)
        elif from_jid not in self.presences:
            # new resource available

            # we keep resources present in cache to avoid sending notifications on each
            # status change
            self.presences.add(from_jid)

            # we check entity capabilities
            try:
                c_elt = next(
                    presence_elt.elements('http://jabber.org/protocol/caps', 'c')
                )
                hash_ = c_elt['hash']
                ver = c_elt['ver']
            except (StopIteration, KeyError):
                # no capabilities, we don't go further
                return

            # FIXME: hash is not checked (cf. XEP-0115)
            disco_tuple = (hash_, ver)

            if disco_tuple not in self.hash_map:
                # first time we se this hash, what is behind it?
                try:
                    infos = await self.requestInfo(from_jid)
                except error.StanzaError as e:
                    log.msg(
                        f"WARNING: can't request disco info for {from_jid!r} (presence: "
                        f"{presence_type}): {e}"
                    )
                else:
                    self.hash_map[disco_tuple] = {
                        'notify': {
                            f[:-7] for f in infos.features if f.endswith('+notify')
                        },
                        'infos': infos
                    }

            # jid_caps must be filled only after hash_map is set, to be sure that
            # the hash data is available in getAutoSubscribers
            jid_caps = self.caps_map.setdefault(from_jid_bare, {})
            if from_jid.resource not in jid_caps:
                jid_caps[from_jid.resource] = disco_tuple

            # nodes are the nodes subscribed with +notify
            nodes = tuple(self.hash_map[disco_tuple]['notify'])
            if not nodes:
                return
            # publishers are entities which have granted presence access to our user
            # + user itself + server
            publishers = (
                tuple(self.presence_map.get(from_jid_bare, ()))
                + (from_jid_bare, self.backend.server_jid)
            )

            # FIXME: add "presence" access_model (for node) for getLastItems
            # TODO: manage other access model (whitelist, …)
            last_items = await self.backend.storage.getLastItems(
                publishers,
                nodes,
                ('open', 'presence'), ('open', 'presence'), True
            )
            # we send message with last item, as required by
            # https://xmpp.org/extensions/xep-0163.html#notify-last
            for pep_jid, node, item, item_access_model in last_items:
                self.notifyPublish(pep_jid, node, [(from_jid, None, [item])])

    ## misc ##

    async def getAutoSubscribers(
        self,
        recipient: jid.JID,
        nodeIdentifier: str,
        explicit_subscribers: Set[jid.JID]
    ) -> List[jid.JID]:
        """Get automatic subscribers

        Get subscribers with presence subscription and +notify for this node
        @param recipient: jid of the PEP owner of this node
        @param nodeIdentifier: node
        @param explicit_subscribers: jids of people which have an explicit subscription
        @return: full jid of automatically subscribed entities
        """
        auto_subscribers = []
        roster = await self.getRoster(recipient)
        for roster_jid, roster_item in roster.items():
            if roster_jid in explicit_subscribers:
                continue
            if roster_item.subscriptionFrom:
                try:
                    online_resources = self.caps_map[roster_jid]
                except KeyError:
                    continue
                for res, disco_tuple in online_resources.items():
                     notify = self.hash_map[disco_tuple]['notify']
                     if nodeIdentifier in notify:
                         full_jid = jid.JID(tuple=(roster_jid.user, roster_jid.host, res))
                         auto_subscribers.append(full_jid)
        return auto_subscribers
