#!/usr/bin/env python3

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


import copy, logging
from datetime import datetime, timezone

from zope.interface import implementer

from twisted.internet import reactor
from twisted.internet import defer
from twisted.words.protocols.jabber import jid
from twisted.words.xish import domish
from twisted.python import log

from wokkel import generic
from wokkel.pubsub import Subscription, BadRequest

from sat_pubsub import error
from sat_pubsub import iidavoll
from sat_pubsub import const
from sat_pubsub import container
from sat_pubsub import exceptions
import uuid
import psycopg2
import psycopg2.extensions
# we wants psycopg2 to return us unicode, not str
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE)
psycopg2.extensions.register_type(psycopg2.extensions.UNICODEARRAY)

# parseXml manage str, but we get unicode
parseXml = lambda unicode_data: generic.parseXml(unicode_data.encode('utf-8'))
ITEMS_SEQ_NAME = 'node_{node_id}_seq'
PEP_COL_NAME = 'pep'
CURRENT_VERSION = '9'
# retrieve the maximum integer item id + 1
NEXT_ITEM_ID_QUERY = r"SELECT COALESCE(max(item::integer)+1,1) as val from items where node_id={node_id} and item ~ E'^\\d+$'"


def withPEP(query, values, pep, recipient):
    """Helper method to facilitate PEP management

    @param query: SQL query basis
    @param values: current values to replace in query
    @param pep(bool): True if we are in PEP mode
    @param recipient(jid.JID): jid of the recipient
    @return: query + PEP AND check,
        recipient's bare jid is added to value if needed
    """
    if pep:
        pep_check="AND {}=%s".format(PEP_COL_NAME)
        values=list(values) + [recipient.userhost()]
    else:
        pep_check="AND {} IS NULL".format(PEP_COL_NAME)
    return "{} {}".format(query, pep_check), values


@implementer(iidavoll.IStorage)
class Storage:

    fts_languages = ['generic']
    defaultConfig = {
            'leaf': {
                const.OPT_PERSIST_ITEMS: True,
                const.OPT_MAX_ITEMS: 'max',
                const.OPT_DELIVER_PAYLOADS: True,
                const.OPT_SEND_LAST_PUBLISHED_ITEM: 'on_sub',
                const.OPT_ACCESS_MODEL: const.VAL_AMODEL_DEFAULT,
                const.OPT_PUBLISH_MODEL: const.VAL_PMODEL_DEFAULT,
                const.OPT_OVERWRITE_POLICY: const.VAL_OWPOL_DEFAUT,
                const.OPT_SERIAL_IDS: False,
                const.OPT_CONSISTENT_PUBLISHER: False,
                const.OPT_FTS_LANGUAGE: const.VAL_FTS_GENERIC,
            },
            'collection': {
                const.OPT_DELIVER_PAYLOADS: True,
                const.OPT_SEND_LAST_PUBLISHED_ITEM: 'on_sub',
                const.OPT_ACCESS_MODEL: const.VAL_AMODEL_DEFAULT,
                const.OPT_PUBLISH_MODEL: const.VAL_PMODEL_DEFAULT,
            }
    }

    def __init__(self, dbpool):
        self.dbpool = dbpool
        d = self.dbpool.runQuery("SELECT value FROM metadata WHERE key='version'")
        d.addCallbacks(self._checkVersion, self._versionEb)

    def _checkVersion(self, row):
        version = row[0].value
        if version != CURRENT_VERSION:
            logging.error("Bad database schema version ({current}), please upgrade to {needed}".format(
                current=version, needed=CURRENT_VERSION))
            reactor.stop()

    def _versionEb(self, failure):
        logging.error("Can't check schema version: {reason}".format(reason=failure))
        reactor.stop()

    def _buildNode(self, row):
        """Build a note class from database result row"""
        if not row:
            raise error.NodeNotFound()

        if row[2] == 'leaf':
            configuration = {
                    const.OPT_PERSIST_ITEMS: row[3],
                    const.OPT_MAX_ITEMS: 'max' if row[4] == 0 else str(row[4]),
                    const.OPT_DELIVER_PAYLOADS: row[5],
                    const.OPT_SEND_LAST_PUBLISHED_ITEM: row[6],
                    const.OPT_ACCESS_MODEL:row[7],
                    const.OPT_PUBLISH_MODEL:row[8],
                    const.OPT_OVERWRITE_POLICY: row[9],
                    const.OPT_SERIAL_IDS:row[10],
                    const.OPT_CONSISTENT_PUBLISHER:row[11],
                    const.OPT_FTS_LANGUAGE: row[12],
                    }
            schema = row[13]
            if schema is not None:
                schema = parseXml(schema)
            node = LeafNode(row[0], row[1], configuration, schema)
            node.dbpool = self.dbpool
            return node
        elif row[2] == 'collection':
            configuration = {
                    const.OPT_DELIVER_PAYLOADS: row[5],
                    const.OPT_SEND_LAST_PUBLISHED_ITEM: row[6],
                    const.OPT_ACCESS_MODEL: row[7],
                    const.OPT_PUBLISH_MODEL:row[8],
                    }
            node = CollectionNode(row[0], row[1], configuration, None)
            node.dbpool = self.dbpool
            return node
        else:
            raise BadRequest(text="Unknown node type !")

    def getFTSLanguages(self):
        """Get list of available languages for full text search"""
        return self.dbpool.runInteraction(self._getFTSLanguages)

    def _getFTSLanguages(self, cursor):
        cursor.execute("SELECT cfgname FROM pg_ts_config")
        result = [r.cfgname for r in cursor.fetchall()]
        result.remove("simple")
        result.insert(0, "generic")
        Node.fts_languages = self.fts_languages = result
        return result

    def getNodeById(self, nodeDbId):
        """Get node using database ID insted of pubsub identifier

        @param nodeDbId(unicode): database ID
        """
        return self.dbpool.runInteraction(self._getNodeById, nodeDbId)

    def _getNodeById(self, cursor, nodeDbId):
        cursor.execute("""SELECT node_id,
                                 node,
                                 node_type,
                                 persist_items,
                                 max_items,
                                 deliver_payloads,
                                 send_last_published_item,
                                 access_model,
                                 publish_model,
                                 overwrite_policy,
                                 serial_ids,
                                 consistent_publisher,
                                 fts_language,
                                 schema::text,
                                 pep
                            FROM nodes
                            WHERE node_id=%s""",
                       (nodeDbId,))
        row = cursor.fetchone()
        return self._buildNode(row)

    def getNode(self, nodeIdentifier, pep, recipient=None):
        return self.dbpool.runInteraction(self._getNode, nodeIdentifier, pep, recipient)

    def _getNode(self, cursor, nodeIdentifier, pep, recipient):
        cursor.execute(*withPEP("""SELECT node_id,
                                          node,
                                          node_type,
                                          persist_items,
                                          max_items,
                                          deliver_payloads,
                                          send_last_published_item,
                                          access_model,
                                          publish_model,
                                          overwrite_policy,
                                          serial_ids,
                                          consistent_publisher,
                                          fts_language,
                                          schema::text,
                                          pep
                                   FROM nodes
                                   WHERE node=%s""",
                              (nodeIdentifier,), pep, recipient))
        row = cursor.fetchone()
        return self._buildNode(row)

    def getNodeIds(self, pep, recipient, allowed_accesses=None):
        """retrieve ids of existing nodes

        @param pep(bool): True if it's a PEP request
        @param recipient(jid.JID, None): recipient of the PEP request
        @param allowed_accesses(None, set): only nodes with access
            in this set will be returned
            None to return all nodes
        @return (list[unicode]): ids of nodes
        """
        if not pep:
            query = "SELECT node from nodes WHERE pep is NULL"
            values = []
        else:
            query = "SELECT node from nodes WHERE pep=%s"
            values = [recipient.userhost()]

        if allowed_accesses is not None:
            query += "AND access_model IN %s"
            values.append(tuple(allowed_accesses))

        d = self.dbpool.runQuery(query, values)
        d.addCallback(lambda results: [r[0] for r in results])
        return d

    def createNode(self, nodeIdentifier, owner, config, schema, pep, recipient=None):
        return self.dbpool.runInteraction(self._createNode, nodeIdentifier,
                                           owner, config, schema, pep, recipient)

    def _createNode(self, cursor, nodeIdentifier, owner, config, schema, pep, recipient):
        if config['pubsub#node_type'] != 'leaf':
            raise error.NoCollections()

        owner = owner.userhost()

        try:
            cursor.execute("""INSERT INTO nodes
                              (node,
                               node_type,
                               persist_items,
                               deliver_payloads,
                               send_last_published_item,
                               access_model,
                               publish_model,
                               overwrite_policy,
                               serial_ids,
                               consistent_publisher,
                               fts_language,
                               schema,
                               pep)
                              VALUES
                              (%s, 'leaf', %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                           (nodeIdentifier,
                            config['pubsub#persist_items'],
                            config['pubsub#deliver_payloads'],
                            config['pubsub#send_last_published_item'],
                            config[const.OPT_ACCESS_MODEL],
                            config[const.OPT_PUBLISH_MODEL],
                            config[const.OPT_OVERWRITE_POLICY],
                            config[const.OPT_SERIAL_IDS],
                            config[const.OPT_CONSISTENT_PUBLISHER],
                            config[const.OPT_FTS_LANGUAGE],
                            schema,
                            recipient.userhost() if pep else None
                            )
                           )
        except cursor._pool.dbapi.IntegrityError as e:
            if e.pgcode == "23505":
                # unique_violation
                raise error.NodeExists()
            else:
                raise error.InvalidConfigurationOption()

        cursor.execute(*withPEP("""SELECT node_id FROM nodes WHERE node=%s""",
                                (nodeIdentifier,), pep, recipient));
        node_id = cursor.fetchone()[0]

        cursor.execute("""SELECT 1 as bool from entities where jid=%s""",
                       (owner,))

        if not cursor.fetchone():
            # XXX: we can NOT rely on the previous query! Commit is needed now because
            # if the entry exists the next query will leave the database in a corrupted
            # state: the solution is to rollback. I tried with other methods like
            # "WHERE NOT EXISTS" but none of them worked, so the following solution
            # looks like the sole - unless you have auto-commit on. More info
            # about this issue: http://cssmay.com/question/tag/tag-psycopg2
            cursor.connection.commit()
            try:
                cursor.execute("""INSERT INTO entities (jid) VALUES (%s)""",
                               (owner,))
            except psycopg2.IntegrityError as e:
                cursor.connection.rollback()
                logging.warning("during node creation: %s" % e.message)

        cursor.execute("""INSERT INTO affiliations
                          (node_id, entity_id, affiliation)
                          SELECT %s, entity_id, 'owner' FROM
                          (SELECT entity_id FROM entities
                                            WHERE jid=%s) as e""",
                       (node_id, owner))

        if config[const.OPT_ACCESS_MODEL] == const.VAL_AMODEL_PUBLISHER_ROSTER:
            if const.OPT_ROSTER_GROUPS_ALLOWED in config:
                allowed_groups = config[const.OPT_ROSTER_GROUPS_ALLOWED]
            else:
                allowed_groups = []
            for group in allowed_groups:
                #TODO: check that group are actually in roster
                cursor.execute("""INSERT INTO node_groups_authorized (node_id, groupname)
                                  VALUES (%s,%s)""" , (node_id, group))
        # XXX: affiliations can't be set on during node creation (at least not with XEP-0060 alone)
        #      so whitelist affiliations need to be done afterward

        # no we may have to do extra things according to config options
        default_conf = self.defaultConfig['leaf']
        # XXX: trigger works on node creation because OPT_SERIAL_IDS is False in defaultConfig
        #      if this value is changed, the _configurationTriggers method should be adapted.
        Node._configurationTriggers(cursor, node_id, default_conf, config)

    def deleteNodeByDbId(self, db_id):
        """Delete a node using directly its database id"""
        return self.dbpool.runInteraction(self._deleteNodeByDbId, db_id)

    def _deleteNodeByDbId(self, cursor, db_id):
        cursor.execute("""DELETE FROM nodes WHERE node_id=%s""",
                       (db_id,))

        if cursor.rowcount != 1:
            raise error.NodeNotFound()

    def deleteNode(self, nodeIdentifier, pep, recipient=None):
        return self.dbpool.runInteraction(self._deleteNode, nodeIdentifier, pep, recipient)

    def _deleteNode(self, cursor, nodeIdentifier, pep, recipient):
        cursor.execute(*withPEP("""DELETE FROM nodes WHERE node=%s""",
                                (nodeIdentifier,), pep, recipient))

        if cursor.rowcount != 1:
            raise error.NodeNotFound()

    def getAffiliations(self, entity, nodeIdentifier, pep, recipient=None):
        return self.dbpool.runInteraction(self._getAffiliations, entity, nodeIdentifier, pep, recipient)

    def _getAffiliations(self, cursor, entity, nodeIdentifier, pep, recipient=None):
        query = ["""SELECT node, affiliation FROM entities
                    NATURAL JOIN affiliations
                    NATURAL JOIN nodes
                    WHERE jid=%s"""]
        args = [entity.userhost()]

        if nodeIdentifier is not None:
            query.append("AND node=%s")
            args.append(nodeIdentifier)

        cursor.execute(*withPEP(' '.join(query), args, pep, recipient))
        rows = cursor.fetchall()
        return [tuple(r) for r in rows]

    def getSubscriptions(self, entity, nodeIdentifier=None, pep=False, recipient=None):
        """retrieve subscriptions of an entity

        @param entity(jid.JID): entity to check
        @param nodeIdentifier(unicode, None): node identifier
            None to retrieve all subscriptions
        @param pep: True if we are in PEP mode
        @param recipient: jid of the recipient
        """

        def toSubscriptions(rows):
            subscriptions = []
            for row in rows:
                subscriber = jid.internJID('%s/%s' % (row.jid,
                                                      row.resource))
                subscription = Subscription(row.node, subscriber, row.state)
                subscriptions.append(subscription)
            return subscriptions

        query = ["""SELECT node,
                           jid,
                           resource,
                           state
                    FROM entities
                    NATURAL JOIN subscriptions
                    NATURAL JOIN nodes
                    WHERE jid=%s"""]

        args = [entity.userhost()]

        if nodeIdentifier is not None:
            query.append("AND node=%s")
            args.append(nodeIdentifier)

        d = self.dbpool.runQuery(*withPEP(' '.join(query), args, pep, recipient))
        d.addCallback(toSubscriptions)
        return d

    def getDefaultConfiguration(self, nodeType):
        return self.defaultConfig[nodeType].copy()

    def formatLastItems(self, result):
        last_items = []
        for pep_jid_s, node, data, item_access_model in result:
            pep_jid = jid.JID(pep_jid_s)
            item = generic.stripNamespace(parseXml(data))
            last_items.append((pep_jid, node, item, item_access_model))
        return last_items

    def getLastItems(self, entities, nodes, node_accesses, item_accesses, pep):
        """get last item for several nodes and entities in a single request"""
        # TODO: manage other access model (whitelist, …)
        if not entities or not nodes or not node_accesses or not item_accesses:
            raise BadRequest(text="entities, nodes and accesses must not be empty")
        if any(not {"open", "presence"}.issuperset(a)
               for a in (node_accesses, item_accesses)):
            raise NotImplementedError('only "open" and "presence" access model are handled for now')
        if not pep:
            raise NotImplementedError("getLastItems is only implemented for PEP at the moment")
        d = self.dbpool.runQuery("""SELECT DISTINCT ON (node_id) pep, node, data::text, items.access_model
                                    FROM items
                                    NATURAL JOIN nodes
                                    WHERE nodes.pep IN %s
                                    AND node IN %s
                                    AND nodes.access_model in %s
                                    AND items.access_model in %s
                                    ORDER BY node_id DESC, items.updated DESC, items.item_id DESC""",
                                 (tuple([e.userhost() for e in entities]),
                                  nodes,
                                  node_accesses,
                                  item_accesses))
        d.addCallback(self.formatLastItems)
        return d

    def getRosterCache(self):
        return self.dbpool.runInteraction(self._getRosterCache)

    def _getRosterCache(self, cursor):
        cursor.execute(
            "SELECT roster_id, jid, version, updated, roster::text FROM roster"
        )
        return [(r.roster_id, jid.JID(r.jid), r.version, r.updated.timestamp(),
                parseXml(r.roster)) for r in cursor.fetchall()]

    def setRosterCache(
            self,
            jid_: jid.JID,
            version: str,
            updated: int,
            roster: domish.Element
    ):
        return self.dbpool.runInteraction(self._setRosterCache, jid_, version, updated, roster)

    def _setRosterCache(self, cursor, jid_, version, updated, roster):
        cursor.execute(
            "INSERT INTO roster(jid, version, updated, roster) VALUES (%s, %s, %s, %s) "
            "ON CONFLICT (jid) DO UPDATE SET version=EXCLUDED.version, "
            "updated=EXCLUDED.updated, roster=EXCLUDED.roster",
            (
                jid_.userhost(),
                version,
                datetime.fromtimestamp(updated, tz=timezone.utc),
                roster.toXml()
            )
        )


@implementer(iidavoll.INode)
class Node:


    def __init__(self, nodeDbId, nodeIdentifier, config, schema):
        self.nodeDbId = nodeDbId
        self.nodeIdentifier = nodeIdentifier
        self._config = config
        self._schema = schema

    def _checkNodeExists(self, cursor):
        cursor.execute("""SELECT 1 as exist FROM nodes WHERE node_id=%s""",
                       (self.nodeDbId,))
        if not cursor.fetchone():
            raise error.NodeNotFound()

    def getType(self):
        return self.nodeType

    def getOwners(self):
        d = self.dbpool.runQuery("""SELECT jid FROM nodes NATURAL JOIN affiliations NATURAL JOIN entities WHERE node_id=%s and affiliation='owner'""", (self.nodeDbId,))
        d.addCallback(lambda rows: [jid.JID(r[0]) for r in rows])
        return d

    def getConfiguration(self):
        return self._config

    def getNextId(self):
        """return XMPP item id usable for next item to publish

        the return value will be next int if serila_ids is set,
        else an UUID will be returned
        """
        if self._config[const.OPT_SERIAL_IDS]:
            d = self.dbpool.runQuery("SELECT nextval('{seq_name}')".format(
                seq_name = ITEMS_SEQ_NAME.format(node_id=self.nodeDbId)))
            d.addCallback(lambda rows: str(rows[0][0]))
            return d
        else:
            return defer.succeed(str(uuid.uuid4()))

    @staticmethod
    def _configurationTriggers(cursor, node_id, old_config, new_config):
        """trigger database relative actions needed when a config is changed

        @param cursor(): current db cursor
        @param node_id(unicode): database ID of the node
        @param old_config(dict): config of the node before the change
        @param new_config(dict): new options that will be changed
        """
        if const.OPT_SERIAL_IDS not in new_config:
            return
        serial_ids = new_config[const.OPT_SERIAL_IDS]
        if serial_ids != old_config[const.OPT_SERIAL_IDS]:
            # serial_ids option has been modified,
            # we need to handle corresponding sequence

            # XXX: we use .format in following queries because values
            #      are generated by ourself
            seq_name = ITEMS_SEQ_NAME.format(node_id=node_id)
            if serial_ids:
                # the next query get the max value +1 of all XMPP items ids
                # which are integers, and default to 1
                cursor.execute(NEXT_ITEM_ID_QUERY.format(node_id=node_id))
                next_val = cursor.fetchone()[0]
                cursor.execute("DROP SEQUENCE IF EXISTS {seq_name}".format(seq_name = seq_name))
                cursor.execute("CREATE SEQUENCE {seq_name} START {next_val} OWNED BY nodes.node_id".format(
                    seq_name = seq_name,
                    next_val = next_val))
            else:
                cursor.execute("DROP SEQUENCE IF EXISTS {seq_name}".format(seq_name = seq_name))

    def setConfiguration(self, options):
        to_delete = []
        for option, value in options.items():
            try:
                if self._config[option] == value:
                    to_delete.append(option)
            except KeyError:
                raise BadRequest(text=f"Invalid option: {option!r}")

        for option in to_delete:
            del options.fields[option]

        if not options.fields:
            return defer.succeed(None)

        if options.get(const.OPT_MAX_ITEMS) == "max":
            # XXX: "max" is default value for config we must convert
            #   it to an interger. See backend's _doSetNodeConfiguration comment
            options[const.OPT_MAX_ITEMS] = "0"

        if ((const.OPT_FTS_LANGUAGE in options
             and options[const.OPT_FTS_LANGUAGE] not in self.fts_languages)):
            raise BadRequest(text=
                f"invalid {const.OPT_FTS_LANGUAGE} value: "
                f"{options[const.OPT_FTS_LANGUAGE]!r}"
            )


        d = self.dbpool.runInteraction(self._setConfiguration, options)
        d.addCallback(self._updateCachedConfiguration, options)
        return d

    def _setConfiguration(self, cursor, options):
        self._configurationTriggers(cursor, self.nodeDbId, self._config, options)
        # options names all follow the scheme "pubsub#{col_name}"
        col_names = (o[7:] for o in options)
        values = ','.join(f"{name}=%s" for name in col_names)
        cursor.execute(f"UPDATE nodes SET {values} WHERE node_id=%s",
                       (*options.values(), self.nodeDbId))
        if cursor.rowcount == 0:
            raise error.NodeNotFound()

    def _updateCachedConfiguration(self, __, options):
        self._config.update(options)

    def getSchema(self):
        return self._schema

    def setSchema(self, schema):
        d = self.dbpool.runInteraction(self._setSchema, schema)
        d.addCallback(self._setCachedSchema, schema)
        return d

    def _setSchema(self, cursor, schema):
        self._checkNodeExists(cursor)
        cursor.execute("""UPDATE nodes SET schema=%s
                          WHERE node_id=%s""",
                       (schema.toXml() if schema else None,
                        self.nodeDbId))

    def _setCachedSchema(self, __, schema):
        self._schema = schema

    def getMetaData(self):
        config = copy.copy(self._config)
        config["pubsub#node_type"] = self.nodeType
        return config

    def getAffiliation(self, entity):
        return self.dbpool.runInteraction(self._getAffiliation, entity)

    def _getAffiliation(self, cursor, entity):
        self._checkNodeExists(cursor)
        cursor.execute("""SELECT affiliation FROM affiliations
                          NATURAL JOIN nodes
                          NATURAL JOIN entities
                          WHERE node_id=%s AND jid=%s""",
                       (self.nodeDbId,
                        entity.userhost()))

        try:
            return cursor.fetchone()[0]
        except TypeError:
            return None

    def getAccessModel(self):
        return self._config[const.OPT_ACCESS_MODEL]

    def getSubscription(self, subscriber):
        return self.dbpool.runInteraction(self._getSubscription, subscriber)

    def _getSubscription(self, cursor, subscriber):
        self._checkNodeExists(cursor)

        userhost = subscriber.userhost()
        resource = subscriber.resource or ''

        cursor.execute("""SELECT state FROM subscriptions
                          NATURAL JOIN nodes
                          NATURAL JOIN entities
                          WHERE node_id=%s AND jid=%s AND resource=%s""",
                       (self.nodeDbId,
                        userhost,
                        resource))

        row = cursor.fetchone()
        if not row:
            return None
        else:
            return Subscription(self.nodeIdentifier, subscriber, row[0])

    def getSubscriptions(self, state=None):
        return self.dbpool.runInteraction(self._getSubscriptions, state)

    def _getSubscriptions(self, cursor, state):
        self._checkNodeExists(cursor)

        query = """SELECT node, jid, resource, state,
                          subscription_type, subscription_depth
                   FROM subscriptions
                   NATURAL JOIN nodes
                   NATURAL JOIN entities
                   WHERE node_id=%s"""
        values = [self.nodeDbId]

        if state:
            query += " AND state=%s"
            values.append(state)

        cursor.execute(query, values)
        rows = cursor.fetchall()

        subscriptions = []
        for row in rows:
            subscriber = jid.JID('%s/%s' % (row.jid, row.resource))

            options = {}
            if row.subscription_type:
                options['pubsub#subscription_type'] = row.subscription_type;
            if row.subscription_depth:
                options['pubsub#subscription_depth'] = row.subscription_depth;

            subscriptions.append(Subscription(row.node, subscriber,
                                              row.state, options))

        return subscriptions

    def addSubscription(self, subscriber, state, config):
        return self.dbpool.runInteraction(self._addSubscription, subscriber,
                                          state, config)

    def _addSubscription(self, cursor, subscriber, state, config):
        self._checkNodeExists(cursor)

        userhost = subscriber.userhost()
        resource = subscriber.resource or ''

        subscription_type = config.get('pubsub#subscription_type')
        subscription_depth = config.get('pubsub#subscription_depth')

        try:
            cursor.execute("""INSERT INTO entities (jid) VALUES (%s)""",
                           (userhost,))
        except cursor._pool.dbapi.IntegrityError:
            cursor.connection.rollback()

        try:
            cursor.execute("""INSERT INTO subscriptions
                              (node_id, entity_id, resource, state,
                               subscription_type, subscription_depth)
                              SELECT %s, entity_id, %s, %s, %s, %s FROM
                              (SELECT entity_id FROM entities
                                                WHERE jid=%s) AS ent_id""",
                           (self.nodeDbId,
                            resource,
                            state,
                            subscription_type,
                            subscription_depth,
                            userhost))
        except cursor._pool.dbapi.IntegrityError:
            raise error.SubscriptionExists()

    def removeSubscription(self, subscriber):
        return self.dbpool.runInteraction(self._removeSubscription,
                                           subscriber)

    def _removeSubscription(self, cursor, subscriber):
        self._checkNodeExists(cursor)

        userhost = subscriber.userhost()
        resource = subscriber.resource or ''

        cursor.execute("""DELETE FROM subscriptions WHERE
                          node_id=%s AND
                          entity_id=(SELECT entity_id FROM entities
                                                      WHERE jid=%s) AND
                          resource=%s""",
                       (self.nodeDbId,
                        userhost,
                        resource))
        if cursor.rowcount != 1:
            raise error.NotSubscribed()

        return None

    def setSubscriptions(self, subscriptions):
        return self.dbpool.runInteraction(self._setSubscriptions, subscriptions)

    def _setSubscriptions(self, cursor, subscriptions):
        self._checkNodeExists(cursor)

        entities = self.getOrCreateEntities(cursor, [s.subscriber for s in subscriptions])
        entities_map = {jid.JID(e.jid): e for e in entities}

        # then we construct values for subscriptions update according to entity_id we just got
        placeholders = ','.join(len(subscriptions) * ["%s"])
        values = []
        for subscription in subscriptions:
            entity_id = entities_map[subscription.subscriber].entity_id
            resource = subscription.subscriber.resource or ''
            values.append((self.nodeDbId, entity_id, resource, subscription.state, None, None))
        # we use upsert so new values are inserted and existing one updated. This feature is only available for PostgreSQL >= 9.5
        cursor.execute("INSERT INTO subscriptions(node_id, entity_id, resource, state, subscription_type, subscription_depth) VALUES " + placeholders + " ON CONFLICT (entity_id, resource, node_id) DO UPDATE SET state=EXCLUDED.state", [v for v in values])

    def isSubscribed(self, entity):
        return self.dbpool.runInteraction(self._isSubscribed, entity)

    def _isSubscribed(self, cursor, entity):
        self._checkNodeExists(cursor)

        cursor.execute("""SELECT 1 as bool FROM entities
                          NATURAL JOIN subscriptions
                          NATURAL JOIN nodes
                          WHERE entities.jid=%s
                          AND node_id=%s AND state='subscribed'""",
                       (entity.userhost(),
                       self.nodeDbId))

        return cursor.fetchone() is not None

    def getAffiliations(self):
        return self.dbpool.runInteraction(self._getAffiliations)

    def _getAffiliations(self, cursor):
        self._checkNodeExists(cursor)

        cursor.execute("""SELECT jid, affiliation FROM nodes
                          NATURAL JOIN affiliations
                          NATURAL JOIN entities
                          WHERE node_id=%s""",
                       (self.nodeDbId,))
        result = cursor.fetchall()

        return {jid.internJID(r[0]): r[1] for r in result}

    def getOrCreateEntities(self, cursor, entities_jids):
        """Get entity_id from entities in entities table

        Entities will be inserted it they don't exist
        @param entities_jid(list[jid.JID]): entities to get or create
        @return list[record(entity_id,jid)]]: list of entity_id and jid (as plain string)
            both existing and inserted entities are returned
        """
        # cf. http://stackoverflow.com/a/35265559
        placeholders = ','.join(len(entities_jids) * ["(%s)"])
        query = (
        """
        WITH
        jid_values (jid) AS (
               VALUES {placeholders}
        ),
        inserted (entity_id, jid) AS (
            INSERT INTO entities (jid)
            SELECT jid
            FROM jid_values
            ON CONFLICT DO NOTHING
            RETURNING entity_id, jid
        )
        SELECT e.entity_id, e.jid
        FROM entities e JOIN jid_values jv ON jv.jid = e.jid
        UNION ALL
        SELECT entity_id, jid
        FROM inserted""".format(placeholders=placeholders))
        cursor.execute(query, [j.userhost() for j in entities_jids])
        return cursor.fetchall()

    def setAffiliations(self, affiliations):
        return self.dbpool.runInteraction(self._setAffiliations, affiliations)

    def _setAffiliations(self, cursor, affiliations):
        self._checkNodeExists(cursor)

        entities = self.getOrCreateEntities(cursor, affiliations)

        # then we construct values for affiliations update according to entity_id we just got
        placeholders = ','.join(len(affiliations) * ["(%s,%s,%s)"])
        values = []
        for e in entities:
            values.extend((e.entity_id, affiliations[jid.JID(e.jid)], self.nodeDbId))

        # we use upsert so new values are inserted and existing one updated. This feature is only available for PostgreSQL >= 9.5
        cursor.execute("INSERT INTO affiliations(entity_id,affiliation,node_id) VALUES " + placeholders + " ON CONFLICT  (entity_id,node_id) DO UPDATE SET affiliation=EXCLUDED.affiliation", values)

    def deleteAffiliations(self, entities):
        return self.dbpool.runInteraction(self._deleteAffiliations, entities)

    def _deleteAffiliations(self, cursor, entities):
        """delete affiliations and subscriptions for this entity"""
        self._checkNodeExists(cursor)
        placeholders = ','.join(len(entities) * ["%s"])
        cursor.execute("DELETE FROM affiliations WHERE node_id=%s AND entity_id in (SELECT entity_id FROM entities WHERE jid IN (" + placeholders + ")) RETURNING entity_id", [self.nodeDbId] + [e.userhost() for e in entities])

        rows = cursor.fetchall()
        placeholders = ','.join(len(rows) * ["%s"])
        cursor.execute("DELETE FROM subscriptions WHERE node_id=%s AND entity_id in (" + placeholders + ")", [self.nodeDbId] + [r[0] for r in rows])

    def getAuthorizedGroups(self):
        return self.dbpool.runInteraction(self._getNodeGroups)

    def _getAuthorizedGroups(self, cursor):
        cursor.execute("SELECT groupname FROM node_groups_authorized NATURAL JOIN nodes WHERE node=%s",
                                (self.nodeDbId,))
        rows = cursor.fetchall()
        return [row[0] for row in rows]


@implementer(iidavoll.ILeafNode)
class LeafNode(Node):


    nodeType = 'leaf'

    def getOrderBy(self, ext_data, direction='ASC'):
        """Return ORDER BY clause corresponding to Order By key in ext_data

        @param ext_data (dict): extra data as used in getItems
        @param direction (unicode): ORDER BY direction (ASC or DESC)
        @return (unicode): ORDER BY clause to use
        """
        keys = ext_data.get('order_by')
        if not keys:
            return f"ORDER BY updated {direction}, item_id {direction}"
        cols_statmnt = []
        for key in keys:
            if key == 'creation':
                column = 'created'
            elif key == 'modification':
                column = 'updated'
            else:
                log.msg("WARNING: Unknown order by key: {key}".format(key=key))
                column = 'updated'
            cols_statmnt.append(f"{column} {direction}")

        cols_statmnt.append(f"item_id {direction}")
        return "ORDER BY " + ",".join([col for col in cols_statmnt])

    @defer.inlineCallbacks
    def storeItems(self, items_data, publisher):
        # XXX: runInteraction doesn't seem to work when there are several "insert"
        #      or "update".
        #      Before the unpacking was done in _storeItems, but this was causing trouble
        #      in case of multiple items_data. So this has now be moved here.
        # FIXME: investigate the issue with runInteraction
        for item_data in items_data:
            yield self.dbpool.runInteraction(self._storeItems, item_data, publisher)

    def _storeItems(self, cursor, item_data, publisher):
        self._checkNodeExists(cursor)
        self._storeItem(cursor, item_data, publisher)

    def _storeItem(self, cursor, item_data, publisher):
        # first try to insert the item
        # - if it fails (conflict), and the item is new and we have serial_ids options,
        #   current id will be recomputed using next item id query (note that is not perfect, as
        #   table is not locked and this can fail if two items are added at the same time
        #   but this can only happen with serial_ids and if future ids have been set by a client,
        #   this case should be rare enough to consider this situation acceptable)
        # - if item insertion fail and the item is not new, we do an update
        # - in other cases, exception is raised
        item, access_model, item_config = item_data.item, item_data.access_model, item_data.config
        data = item.toXml()
        data_fts_cfg = self._config[const.OPT_FTS_LANGUAGE]
        if data_fts_cfg == const.VAL_FTS_GENERIC:
            data_fts_cfg = "simple"

        insert_query = (
            "INSERT INTO items(node_id, item, publisher, data, access_model, "
            "data_fts_cfg) VALUES (%s, %s, %s, %s, %s, %s) RETURNING item_id"
        )
        insert_data = [self.nodeDbId,
                       item["id"],
                       publisher.full(),
                       data,
                       access_model,
                       data_fts_cfg,
                       ]

        try:
            cursor.execute(insert_query, insert_data)
        except cursor._pool.dbapi.IntegrityError as e:
            if e.pgcode != "23505":
                # we only handle unique_violation, every other exception must be raised
                raise e
            cursor.connection.rollback()
            # the item already exist
            if item_data.new:
                # the item is new
                if self._config[const.OPT_SERIAL_IDS]:
                    # this can happen with serial_ids, if a item has been stored
                    # with a future id (generated by XMPP client)
                    cursor.execute(NEXT_ITEM_ID_QUERY.format(node_id=self.nodeDbId))
                    next_id = cursor.fetchone()[0]
                    # we update the sequence, so we can skip conflicting ids
                    cursor.execute("SELECT setval('{seq_name}', %s)".format(
                        seq_name = ITEMS_SEQ_NAME.format(node_id=self.nodeDbId)), [next_id])
                    # and now we can retry the query with the new id
                    item['id'] = insert_data[1] = str(next_id)
                    # item saved in DB must also be updated with the new id
                    insert_data[3] = item.toXml()
                    cursor.execute(insert_query, insert_data)
                else:
                    # but if we have not serial_ids, we have a real problem
                    raise e
            else:
                # this is an update
                cursor.execute("""UPDATE items SET updated=now(), publisher=%s, data=%s
                                  WHERE node_id=%s AND items.item=%s
                                  RETURNING item_id""",
                               (publisher.full(),
                                data,
                                self.nodeDbId,
                                item["id"]))
                if cursor.rowcount != 1:
                    raise exceptions.InternalError("item has not been updated correctly")
                item_id = cursor.fetchone()[0];
                self._storeCategories(cursor, item_id, item_data.categories, update=True)
                return

        item_id = cursor.fetchone()[0];
        self._storeCategories(cursor, item_id, item_data.categories)

        if access_model == const.VAL_AMODEL_PUBLISHER_ROSTER:
            if const.OPT_ROSTER_GROUPS_ALLOWED in item_config:
                # XXX: needed to force list if there is only one value
                item_config.fields[const.OPT_ROSTER_GROUPS_ALLOWED].fieldType='list-multi'
                allowed_groups = item_config[const.OPT_ROSTER_GROUPS_ALLOWED]
            else:
                allowed_groups = []
            for group in allowed_groups:
                #TODO: check that group are actually in roster
                cursor.execute("""INSERT INTO item_groups_authorized (item_id, groupname)
                                  VALUES (%s,%s)""" , (item_id, group))
        # TODO: whitelist access model

        max_items = self._config.get(const.OPT_MAX_ITEMS, 'max')

        if max_items != 'max':
            try:
                max_items = int(self._config[const.OPT_MAX_ITEMS])
            except ValueError:
                log.err(f"Invalid max_items value: {max_items!r}")
            else:
                if max_items > 0:
                    # we delete all items above the requested max
                    cursor.execute(
                        "DELETE FROM items WHERE node_id=%s and item_id in (SELECT "
                        "item_id FROM items WHERE node_id=%s ORDER BY items.updated "
                        "DESC, items.item_id DESC OFFSET %s)" ,
                        (self.nodeDbId, self.nodeDbId, max_items)
                    )


    def _storeCategories(self, cursor, item_id, categories, update=False):
        # TODO: handle canonical form
        if update:
            cursor.execute("""DELETE FROM item_categories
                              WHERE item_id=%s""", (item_id,))

        # we use a set to avoid duplicates
        for category in set(categories):
            cursor.execute("""INSERT INTO item_categories (item_id, category)
                              VALUES (%s, %s)""", (item_id, category))

    def removeItems(self, itemIdentifiers):
        return self.dbpool.runInteraction(self._removeItems, itemIdentifiers)

    def _removeItems(self, cursor, itemIdentifiers):
        self._checkNodeExists(cursor)

        deleted = []

        for itemIdentifier in itemIdentifiers:
            cursor.execute("""DELETE FROM items WHERE
                              node_id=%s AND
                              item=%s""",
                           (self.nodeDbId,
                            itemIdentifier))

            if cursor.rowcount:
                deleted.append(itemIdentifier)

        return deleted

    def getItems(self, authorized_groups, unrestricted, maxItems=None, ext_data=None):
        """ Get all authorised items

        @param authorized_groups: we want to get items that these groups can access
        @param unrestricted: if true, don't check permissions (i.e.: get all items)
        @param maxItems: nb of items we want to get
        @param ext_data: options for extra features like RSM and MAM

        @return: list of container.ItemData
            if unrestricted is False, access_model and config will be None
        """
        if ext_data is None:
            ext_data = {}
        return self.dbpool.runInteraction(self._getItems, authorized_groups, unrestricted, maxItems, ext_data, ids_only=False)

    def getItemsIds(self, authorized_groups, unrestricted, maxItems=None, ext_data=None):
        """ Get all authorised items ids

        @param authorized_groups: we want to get items that these groups can access
        @param unrestricted: if true, don't check permissions (i.e.: get all items)
        @param maxItems: nb of items we want to get
        @param ext_data: options for extra features like RSM and MAM

        @return list(unicode): list of ids
        """
        if ext_data is None:
            ext_data = {}
        return self.dbpool.runInteraction(self._getItems, authorized_groups, unrestricted, maxItems, ext_data, ids_only=True)

    def _appendSourcesAndFilters(self, query, args, authorized_groups, unrestricted, ext_data):
        """append sources and filters to sql query requesting items and return ORDER BY

        arguments query, args, authorized_groups, unrestricted and ext_data are the same as for
        _getItems
        """
        # SOURCES
        query.append("FROM items")

        if unrestricted:
            query_filters = ["WHERE node_id=%s"]
            args.append(self.nodeDbId)
        else:
            query.append("LEFT JOIN item_groups_authorized USING (item_id)")
            args.append(self.nodeDbId)
            if authorized_groups:
                get_groups = " or (items.access_model='roster' and groupname in %s)"
                args.append(authorized_groups)
            else:
                get_groups = ""

            query_filters = ["WHERE node_id=%s AND (items.access_model='open'" + get_groups + ")"]

        # FILTERS
        if 'filters' in ext_data:  # MAM filters
            for filter_ in ext_data['filters']:
                if filter_.var == 'start':
                    query_filters.append("AND created>=%s")
                    args.append(filter_.value)
                elif filter_.var == 'end':
                    query_filters.append("AND created<=%s")
                    args.append(filter_.value)
                elif filter_.var == 'with':
                    jid_s = filter_.value
                    if '/' in jid_s:
                        query_filters.append("AND publisher=%s")
                        args.append(filter_.value)
                    else:
                        query_filters.append("AND publisher LIKE %s")
                        args.append("{}%".format(filter_.value))
                elif filter_.var == const.MAM_FILTER_FTS:
                    fts_cfg = self._config[const.OPT_FTS_LANGUAGE]
                    if fts_cfg == const.VAL_FTS_GENERIC:
                        fts_cfg = "simple"
                    query_filters.append(
                        "AND data_fts @@ websearch_to_tsquery(%s, %s)"
                    )
                    args.append(fts_cfg)
                    args.append(filter_.value)
                elif filter_.var == const.MAM_FILTER_CATEGORY:
                    query.append("LEFT JOIN item_categories USING (item_id)")
                    query_filters.append("AND category=%s")
                    args.append(filter_.value)
                else:
                    log.msg("WARNING: unknown filter: {}".format(filter_.encode('utf-8')))

        query.extend(query_filters)

        return self.getOrderBy(ext_data, direction="ASC")

    def _getItems(self, cursor, authorized_groups, unrestricted, maxItems, ext_data, ids_only):
        self._checkNodeExists(cursor)

        if maxItems == 0:
            return []

        args = []

        # SELECT
        if ids_only:
            query = ["SELECT item"]
        else:
            query = ["SELECT data::text,items.access_model,item_id,created,updated"]

        query_order = self._appendSourcesAndFilters(query, args, authorized_groups, unrestricted, ext_data)

        if 'rsm' in ext_data:
            rsm = ext_data['rsm']
            maxItems = rsm.max
            if rsm.index is not None:
                # We need to know the item_id of corresponding to the index (offset) of the current query
                # so we execute the query to look for the item_id
                tmp_query = query[:]
                tmp_args = args[:]
                tmp_query[0] = "SELECT item_id"
                tmp_query.append("{} LIMIT 1 OFFSET %s".format(query_order))
                tmp_args.append(rsm.index)
                cursor.execute(' '.join(query), args)
                # FIXME: bad index is not managed yet
                item_id = cursor.fetchall()[0][0]

                # now that we have the id, we can use it
                query.append("AND item_id<=%s")
                args.append(item_id)
            elif rsm.before is not None:
                if rsm.before != '':
                    query.insert(0,"SELECT * from (")
                    query[1] += f",row_number() OVER ({query_order}) as row_number"
                    query.append(f"{query_order}) as x")
                    query.append(
                        "WHERE row_number<(SELECT row_number FROM (SELECT row_number() "
                        f"OVER ({query_order}) as row_number,item"
                    )
                    self._appendSourcesAndFilters(
                        query, args, authorized_groups, unrestricted, ext_data
                    )
                    query.append(") as row_num_sub WHERE item=%s)")
                    args.append(rsm.before)
                # we need to reverse order in a first query to get the right
                # items
                query.insert(0,"SELECT * from (")
                query.append(self.getOrderBy(ext_data, direction='DESC'))
                query.append("LIMIT %s) as x")
                if maxItems is None:
                    # we default to 10 max when we request last page
                    log.msg(
                        "WARNING: getting last page with RSM without max, "
                        "we default to max=10"
                    )
                    args.append(10)
                else:
                    args.append(maxItems)
            elif rsm.after:
                query.insert(0,"SELECT * from (")
                query[1] += f",row_number() OVER ({query_order}) as row_number"
                query.append(f"{query_order}) as x")
                query.append(
                    "WHERE row_number>(SELECT row_number FROM (SELECT row_number() "
                    f"OVER ({query_order}) as row_number,item"
                )
                self._appendSourcesAndFilters(
                    query, args, authorized_groups, unrestricted, ext_data
                )
                query.append(") as row_num_sub WHERE item=%s)")
                args.append(rsm.after)
        else:
            rsm = False

        query.append(query_order)

        if maxItems is not None:
            if rsm == False:
                # if we have legacy maxItems (i.e. not RSM max), we need to
                # reverse order (maxItems get last items, cf.
                # https://xmpp.org/extensions/xep-0060.html#subscriber-retrieve-requestrecent)
                # in a first query to get the right items
                query.insert(0,"SELECT * from (")
                query.insert(len(query)-1, self.getOrderBy(ext_data, direction='DESC'))
                query.insert(len(query)-1, "LIMIT %s) as x")
                args.append(maxItems)
            else:
                query.append("LIMIT %s")
                args.append(maxItems)

        cursor.execute(' '.join(query), args)

        result = cursor.fetchall()
        if unrestricted and not ids_only:
            # with unrestricted query, we need to fill the access_list for a roster access items
            ret = []
            for item_data in result:
                item = generic.stripNamespace(parseXml(item_data.data))
                access_model = item_data.access_model
                item_id = item_data.item_id
                created = item_data.created
                updated = item_data.updated
                access_list = {}
                if access_model == const.VAL_AMODEL_PUBLISHER_ROSTER:
                    cursor.execute('SELECT groupname FROM item_groups_authorized WHERE item_id=%s', (item_id,))
                    access_list[const.OPT_ROSTER_GROUPS_ALLOWED] = [r.groupname for r in cursor.fetchall()]

                ret.append(container.ItemData(item, access_model, access_list, created=created, updated=updated))
                # TODO: whitelist item access model
            return ret

        if ids_only:
            return [r.item for r in result]
        else:
            items_data = [container.ItemData(generic.stripNamespace(parseXml(r.data)), r.access_model, created=r.created, updated=r.updated) for r in result]
        return items_data

    def getItemsById(self, authorized_groups, unrestricted, itemIdentifiers):
        """Get items which are in the given list

        @param authorized_groups: we want to get items that these groups can access
        @param unrestricted: if true, don't check permissions
        @param itemIdentifiers: list of ids of the items we want to get
        @return: list of container.ItemData
            ItemData.config will contains access_list (managed as a dictionnary with same key as for item_config)
            if unrestricted is False, access_model and config will be None
        """
        return self.dbpool.runInteraction(self._getItemsById, authorized_groups, unrestricted, itemIdentifiers)

    def _getItemsById(self, cursor, authorized_groups, unrestricted, itemIdentifiers):
        self._checkNodeExists(cursor)
        ret = []
        if unrestricted: #we get everything without checking permissions
            for itemIdentifier in itemIdentifiers:
                cursor.execute("""SELECT data::text,items.access_model,item_id,created,updated FROM nodes
                                  INNER JOIN items USING (node_id)
                                  WHERE node_id=%s AND item=%s""",
                               (self.nodeDbId,
                                itemIdentifier))
                result = cursor.fetchone()
                if not result:
                    raise error.ItemNotFound()

                item = generic.stripNamespace(parseXml(result[0]))
                access_model = result[1]
                item_id = result[2]
                created= result[3]
                updated= result[4]
                access_list = {}
                if access_model == const.VAL_AMODEL_PUBLISHER_ROSTER:
                    cursor.execute('SELECT groupname FROM item_groups_authorized WHERE item_id=%s', (item_id,))
                    access_list[const.OPT_ROSTER_GROUPS_ALLOWED] = [r[0] for r in cursor.fetchall()]
                 #TODO: WHITELIST access_model

                ret.append(container.ItemData(item, access_model, access_list, created=created, updated=updated))
        else: #we check permission before returning items
            for itemIdentifier in itemIdentifiers:
                args = [self.nodeDbId, itemIdentifier]
                if authorized_groups:
                    args.append(authorized_groups)
                cursor.execute("""SELECT data::text, created, updated FROM nodes
                           INNER  JOIN items USING (node_id)
                           LEFT JOIN item_groups_authorized USING (item_id)
                           WHERE node_id=%s AND item=%s AND
                           (items.access_model='open' """ +
                           ("or (items.access_model='roster' and groupname in %s)" if authorized_groups else '') + ")",
                           args)

                result = cursor.fetchone()
                if result:
                    ret.append(container.ItemData(generic.stripNamespace(parseXml(result[0])), created=result[1], updated=result[2]))

        return ret

    def getItemsCount(self, authorized_groups, unrestricted, ext_data=None):
        """Count expected number of items in a getItems query

        @param authorized_groups: we want to get items that these groups can access
        @param unrestricted: if true, don't check permissions (i.e.: get all items)
        @param ext_data: options for extra features like RSM and MAM
        """
        if ext_data is None:
            ext_data = {}
        return self.dbpool.runInteraction(self._getItemsCount, authorized_groups, unrestricted, ext_data)

    def _getItemsCount(self, cursor, authorized_groups, unrestricted, ext_data):
        self._checkNodeExists(cursor)
        args = []

        # SELECT
        query = ["SELECT count(1)"]

        self._appendSourcesAndFilters(query, args, authorized_groups, unrestricted, ext_data)

        cursor.execute(' '.join(query), args)
        return cursor.fetchall()[0][0]

    def getItemsIndex(self, item_id, authorized_groups, unrestricted, ext_data=None):
        """Get expected index of first item in the window of a getItems query

        @param item_id: id of the item
        @param authorized_groups: we want to get items that these groups can access
        @param unrestricted: if true, don't check permissions (i.e.: get all items)
        @param ext_data: options for extra features like RSM and MAM
        """
        if ext_data is None:
            ext_data = {}
        return self.dbpool.runInteraction(self._getItemsIndex, item_id, authorized_groups, unrestricted, ext_data)

    def _getItemsIndex(self, cursor, item_id, authorized_groups, unrestricted, ext_data):
        self._checkNodeExists(cursor)
        args = []

        # SELECT
        query = []

        query_order = self._appendSourcesAndFilters(query, args, authorized_groups, unrestricted, ext_data)

        query_select = "SELECT row_number from (SELECT row_number() OVER ({}), item".format(query_order)
        query.insert(0, query_select)
        query.append(") as x WHERE item=%s")
        args.append(item_id)

        cursor.execute(' '.join(query), args)
        # XXX: row_number start at 1, but we want that index start at 0
        try:
            return cursor.fetchall()[0][0] - 1
        except IndexError:
            raise error.NodeNotFound()

    def getItemsPublishers(self, itemIdentifiers):
        """Get the publishers for all given identifiers

        @return (dict[unicode, jid.JID]): map of itemIdentifiers to publisher
            if item is not found, key is skipped in resulting dict
        """
        return self.dbpool.runInteraction(self._getItemsPublishers, itemIdentifiers)

    def _getItemsPublishers(self, cursor, itemIdentifiers):
        self._checkNodeExists(cursor)
        ret = {}
        for itemIdentifier in itemIdentifiers:
            cursor.execute("""SELECT publisher FROM items
                              WHERE node_id=%s AND item=%s""",
                            (self.nodeDbId, itemIdentifier,))
            result = cursor.fetchone()
            if result:
                ret[itemIdentifier] = jid.JID(result[0])
        return ret

    def purge(self):
        return self.dbpool.runInteraction(self._purge)

    def _purge(self, cursor):
        self._checkNodeExists(cursor)

        cursor.execute("""DELETE FROM items WHERE
                          node_id=%s""",
                       (self.nodeDbId,))


class CollectionNode(Node):

    nodeType = 'collection'
