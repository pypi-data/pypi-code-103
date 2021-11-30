#!/usr/bin/env python3


# SAT: a jabber client
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
from sat.memory.crypto import BlockCipher, PasswordHasher
from sat.tools.config import fixConfigOption
from twisted.enterprise import adbapi
from twisted.internet import defer
from twisted.words.protocols.jabber import jid
from twisted.python import failure
from collections import OrderedDict
import sys
import re
import os.path
import pickle as pickle
import hashlib
import sqlite3
import json

log = getLogger(__name__)

CURRENT_DB_VERSION = 9

# XXX: DATABASE schemas are used in the following way:
#      - 'current' key is for the actual database schema, for a new base
#      - x(int) is for update needed between x-1 and x. All number are needed between y and z to do an update
#        e.g.: if CURRENT_DB_VERSION is 6, 'current' is the actuel DB, and to update from version 3, numbers 4, 5 and 6 are needed
#      a 'current' data dict can contains the keys:
#      - 'CREATE': it contains an Ordered dict with table to create as keys, and a len 2 tuple as value, where value[0] are the columns definitions and value[1] are the table constraints
#      - 'INSERT': it contains an Ordered dict with table where values have to be inserted, and many tuples containing values to insert in the order of the rows (#TODO: manage named columns)
#      - 'INDEX':
#      an update data dict (the ones with a number) can contains the keys 'create', 'delete', 'cols create', 'cols delete', 'cols modify', 'insert' or 'specific'. See Updater.generateUpdateData for more infos. This method can be used to autogenerate update_data, to ease the work of the developers.
# TODO: indexes need to be improved

DATABASE_SCHEMAS = {
        "current": {'CREATE': OrderedDict((
                              ('profiles',        (("id INTEGER PRIMARY KEY ASC", "name TEXT"),
                                                   ("UNIQUE (name)",))),
                              ('components',      (("profile_id INTEGER PRIMARY KEY", "entry_point TEXT NOT NULL"),
                                                   ("FOREIGN KEY(profile_id) REFERENCES profiles(id) ON DELETE CASCADE",))),
                              ('message_types',   (("type TEXT PRIMARY KEY",),
                                  ())),
                              ('history',         (("uid TEXT PRIMARY KEY", "stanza_id TEXT", "update_uid TEXT", "profile_id INTEGER", "source TEXT", "dest TEXT", "source_res TEXT", "dest_res TEXT",
                                                    "timestamp DATETIME NOT NULL", "received_timestamp DATETIME", # XXX: timestamp is the time when the message was emitted. If received time stamp is not NULL, the message was delayed and timestamp is the declared value (and received_timestamp the time of reception)
                                                    "type TEXT", "extra BLOB"),
                                                   ("FOREIGN KEY(profile_id) REFERENCES profiles(id) ON DELETE CASCADE", "FOREIGN KEY(type) REFERENCES message_types(type)",
                                                    "UNIQUE (profile_id, stanza_id, source, dest)" # avoid storing 2 times the same message
                                                    ))),
                              ('message',        (("id INTEGER PRIMARY KEY ASC", "history_uid INTEGER", "message TEXT", "language TEXT"),
                                                  ("FOREIGN KEY(history_uid) REFERENCES history(uid) ON DELETE CASCADE",))),
                              ('subject',        (("id INTEGER PRIMARY KEY ASC", "history_uid INTEGER", "subject TEXT", "language TEXT"),
                                                  ("FOREIGN KEY(history_uid) REFERENCES history(uid) ON DELETE CASCADE",))),
                              ('thread',          (("id INTEGER PRIMARY KEY ASC", "history_uid INTEGER", "thread_id TEXT", "parent_id TEXT"),("FOREIGN KEY(history_uid) REFERENCES history(uid) ON DELETE CASCADE",))),
                              ('param_gen',       (("category TEXT", "name TEXT", "value TEXT"),
                                                   ("PRIMARY KEY (category, name)",))),
                              ('param_ind',       (("category TEXT", "name TEXT", "profile_id INTEGER", "value TEXT"),
                                                   ("PRIMARY KEY (profile_id, category, name)", "FOREIGN KEY(profile_id) REFERENCES profiles(id) ON DELETE CASCADE"))),
                              ('private_gen',     (("namespace TEXT", "key TEXT", "value TEXT"),
                                                   ("PRIMARY KEY (namespace, key)",))),
                              ('private_ind',     (("namespace TEXT", "key TEXT", "profile_id INTEGER", "value TEXT"),
                                                   ("PRIMARY KEY (profile_id, namespace, key)", "FOREIGN KEY(profile_id) REFERENCES profiles(id) ON DELETE CASCADE"))),
                              ('private_gen_bin', (("namespace TEXT", "key TEXT", "value BLOB"),
                                                   ("PRIMARY KEY (namespace, key)",))),
                              ('private_ind_bin', (("namespace TEXT", "key TEXT", "profile_id INTEGER", "value BLOB"),
                                                   ("PRIMARY KEY (profile_id, namespace, key)", "FOREIGN KEY(profile_id) REFERENCES profiles(id) ON DELETE CASCADE"))),
                              ('files',           (("id TEXT NOT NULL", "public_id TEXT", "version TEXT NOT NULL",
                                                    "parent TEXT NOT NULL",
                                                    "type TEXT CHECK(type in ('{file}', '{directory}')) NOT NULL DEFAULT '{file}'".format(
                                                        file=C.FILE_TYPE_FILE, directory=C.FILE_TYPE_DIRECTORY),
                                                    "file_hash TEXT", "hash_algo TEXT", "name TEXT NOT NULL", "size INTEGER",
                                                    "namespace TEXT", "media_type TEXT", "media_subtype TEXT",
                                                    "created DATETIME NOT NULL", "modified DATETIME",
                                                    "owner TEXT", "access TEXT", "extra TEXT", "profile_id INTEGER"),
                                                   ("PRIMARY KEY (id, version)", "FOREIGN KEY(profile_id) REFERENCES profiles(id) ON DELETE CASCADE",
                                                    "UNIQUE (public_id)"))),
                              )),
                    'INSERT': OrderedDict((
                              ('message_types', (("'chat'",),
                                                 ("'error'",),
                                                 ("'groupchat'",),
                                                 ("'headline'",),
                                                 ("'normal'",),
                                                 ("'info'",) # info is not standard, but used to keep track of info like join/leave in a MUC
                                                )),
                              )),
                    'INDEX': (('history', (('profile_id', 'timestamp'),
                                           ('profile_id', 'received_timestamp'))),
                              ('message', ('history_uid',)),
                              ('subject', ('history_uid',)),
                              ('thread', ('history_uid',)),
                              ('files', (('profile_id', 'owner', 'media_type', 'media_subtype'),
                                         ('profile_id', 'owner', 'parent'))),
                             )
                    },
        9:         {'specific': 'update_v9'
                   },
        8:         {'specific': 'update_v8'
                   },
        7:         {'specific': 'update_v7'
                   },
        6:         {'cols create': {'history': ('stanza_id TEXT',)},
                   },
        5:         {'create': {'files': (("id TEXT NOT NULL", "version TEXT NOT NULL", "parent TEXT NOT NULL",
                                          "type TEXT CHECK(type in ('{file}', '{directory}')) NOT NULL DEFAULT '{file}'".format(
                                              file=C.FILE_TYPE_FILE, directory=C.FILE_TYPE_DIRECTORY),
                                          "file_hash TEXT", "hash_algo TEXT", "name TEXT NOT NULL", "size INTEGER",
                                          "namespace TEXT", "mime_type TEXT",
                                          "created DATETIME NOT NULL", "modified DATETIME",
                                          "owner TEXT", "access TEXT", "extra TEXT", "profile_id INTEGER"),
                                         ("PRIMARY KEY (id, version)", "FOREIGN KEY(profile_id) REFERENCES profiles(id) ON DELETE CASCADE"))},
                   },
        4:         {'create': {'components': (('profile_id INTEGER PRIMARY KEY', 'entry_point TEXT NOT NULL'), ('FOREIGN KEY(profile_id) REFERENCES profiles(id) ON DELETE CASCADE',))}
                   },
        3:         {'specific': 'update_v3'
                   },
        2:         {'specific': 'update2raw_v2'
                   },
        1:         {'cols create': {'history': ('extra BLOB',)},
                   },
        }

NOT_IN_EXTRA = ('stanza_id', 'received_timestamp', 'update_uid') # keys which are in message data extra but not stored in sqlite's extra field
                                                    # this is specific to this sqlite storage and for now only used for received_timestamp
                                                    # because this value is stored in a separate field


class ConnectionPool(adbapi.ConnectionPool):
    def _runQuery(self, trans, *args, **kw):
        retry = kw.pop('query_retry', 6)
        try:
            trans.execute(*args, **kw)
        except sqlite3.IntegrityError as e:
            # Workaround to avoid IntegrityError causing (i)pdb to be
            # launched in debug mode
            raise failure.Failure(e)
        except Exception as e:
            # FIXME: in case of error, we retry a couple of times
            #        this is a workaround, we need to move to better
            #        Sqlite integration, probably with high level library
            retry -= 1
            if retry == 0:
                log.error(_('too many db tries, we abandon! Error message: {msg}\n'
                            'query was {query}'
                            .format(msg=e, query=' '.join([str(a) for a in args]))))
                raise e
            log.warning(
                _('exception while running query, retrying ({try_}): {msg}').format(
                try_ = 6 - retry,
                msg = e))
            kw['query_retry'] = retry
            return self._runQuery(trans, *args, **kw)
        return trans.fetchall()

    def _runInteraction(self, interaction, *args, **kw):
        # sometimes interaction may fail while committing in _runInteraction
        # and it may be due to a db lock. So we work around it in a similar way
        # as for _runQuery but with only 3 tries
        retry = kw.pop('interaction_retry', 4)
        try:
            return adbapi.ConnectionPool._runInteraction(self, interaction, *args, **kw)
        except Exception as e:
            retry -= 1
            if retry == 0:
                log.error(
                    _('too many interaction tries, we abandon! Error message: {msg}\n'
                      'interaction method was: {interaction}\n'
                      'interaction arguments were: {args}'
                      .format(msg=e, interaction=interaction,
                              args=', '.join([str(a) for a in args]))))
                raise e
            log.warning(
                _('exception while running interaction, retrying ({try_}): {msg}')
                .format(try_ = 4 - retry, msg = e))
            kw['interaction_retry'] = retry
            return self._runInteraction(interaction, *args, **kw)


class SqliteStorage(object):
    """This class manage storage with Sqlite database"""

    def __init__(self, db_filename, sat_version):
        """Connect to the given database

        @param db_filename: full path to the Sqlite database
        """
        # triggered when memory is fully initialised and ready
        self.initialized = defer.Deferred()
        # we keep cache for the profiles (key: profile name, value: profile id)
        self.profiles = {}

        log.info(_("Connecting database"))
        new_base = not os.path.exists(db_filename)  # do we have to create the database ?
        if new_base:  # the dir may not exist if it's not the XDG recommended one
            dir_ = os.path.dirname(db_filename)
            if not os.path.exists(dir_):
                os.makedirs(dir_, 0o700)

        def foreignKeysOn(sqlite):
            sqlite.execute('PRAGMA foreign_keys = ON')

        self.dbpool = ConnectionPool("sqlite3", db_filename, cp_openfun=foreignKeysOn, check_same_thread=False, timeout=15)

        def getNewBaseSql():
            log.info(_("The database is new, creating the tables"))
            database_creation = ["PRAGMA user_version=%d" % CURRENT_DB_VERSION]
            database_creation.extend(Updater.createData2Raw(DATABASE_SCHEMAS['current']['CREATE']))
            database_creation.extend(Updater.insertData2Raw(DATABASE_SCHEMAS['current']['INSERT']))
            database_creation.extend(Updater.indexData2Raw(DATABASE_SCHEMAS['current']['INDEX']))
            return database_creation

        def getUpdateSql():
            updater = Updater(self, sat_version)
            return updater.checkUpdates()

        # init_defer is the initialisation deferred, initialisation is ok when all its callbacks have been done

        init_defer = defer.succeed(None)

        init_defer.addCallback(lambda ignore: getNewBaseSql() if new_base else getUpdateSql())
        init_defer.addCallback(self.commitStatements)

        def fillProfileCache(ignore):
            return self.dbpool.runQuery("SELECT profile_id, entry_point FROM components").addCallback(self._cacheComponentsAndProfiles)

        init_defer.addCallback(fillProfileCache)
        init_defer.chainDeferred(self.initialized)

    def commitStatements(self, statements):

        if statements is None:
            return defer.succeed(None)
        log.debug("\n===== COMMITTING STATEMENTS =====\n%s\n============\n\n" % '\n'.join(statements))
        d = self.dbpool.runInteraction(self._updateDb, tuple(statements))
        return d

    def _updateDb(self, interaction, statements):
        for statement in statements:
            interaction.execute(statement)

    ## Profiles

    def _cacheComponentsAndProfiles(self, components_result):
        """Get components results and send requests profiles

        they will be both put in cache in _profilesCache
        """
        return self.dbpool.runQuery("SELECT name,id FROM profiles").addCallback(
            self._cacheComponentsAndProfiles2, components_result)

    def _cacheComponentsAndProfiles2(self, profiles_result, components):
        """Fill the profiles cache

        @param profiles_result: result of the sql profiles query
        """
        self.components = dict(components)
        for profile in profiles_result:
            name, id_ = profile
            self.profiles[name] = id_

    def getProfilesList(self):
        """"Return list of all registered profiles"""
        return list(self.profiles.keys())

    def hasProfile(self, profile_name):
        """return True if profile_name exists

        @param profile_name: name of the profile to check
        """
        return profile_name in self.profiles

    def profileIsComponent(self, profile_name):
        try:
            return self.profiles[profile_name] in self.components
        except KeyError:
            raise exceptions.NotFound("the requested profile doesn't exists")

    def getEntryPoint(self, profile_name):
        try:
            return self.components[self.profiles[profile_name]]
        except KeyError:
            raise exceptions.NotFound("the requested profile doesn't exists or is not a component")

    def createProfile(self, name, component=None):
        """Create a new profile

        @param name(unicode): name of the profile
        @param component(None, unicode): if not None, must point to a component entry point
        @return: deferred triggered once profile is actually created
        """

        def getProfileId(ignore):
            return self.dbpool.runQuery("SELECT (id) FROM profiles WHERE name = ?", (name, ))

        def setComponent(profile_id):
            id_ = profile_id[0][0]
            d_comp = self.dbpool.runQuery("INSERT INTO components(profile_id, entry_point) VALUES (?, ?)", (id_, component))
            d_comp.addCallback(lambda __: profile_id)
            return d_comp

        def profile_created(profile_id):
            id_= profile_id[0][0]
            self.profiles[name] = id_  # we synchronise the cache

        d = self.dbpool.runQuery("INSERT INTO profiles(name) VALUES (?)", (name, ))
        d.addCallback(getProfileId)
        if component is not None:
            d.addCallback(setComponent)
        d.addCallback(profile_created)
        return d

    def deleteProfile(self, name):
        """Delete profile

        @param name: name of the profile
        @return: deferred triggered once profile is actually deleted
        """
        def deletionError(failure_):
            log.error(_("Can't delete profile [%s]") % name)
            return failure_

        def delete(txn):
            profile_id = self.profiles.pop(name)
            txn.execute("DELETE FROM profiles WHERE name = ?", (name,))
            # FIXME: the following queries should be done by the ON DELETE CASCADE
            #        but it seems they are not, so we explicitly do them by security
            #        this need more investigation
            txn.execute("DELETE FROM history WHERE profile_id = ?", (profile_id,))
            txn.execute("DELETE FROM param_ind WHERE profile_id = ?", (profile_id,))
            txn.execute("DELETE FROM private_ind WHERE profile_id = ?", (profile_id,))
            txn.execute("DELETE FROM private_ind_bin WHERE profile_id = ?", (profile_id,))
            txn.execute("DELETE FROM components WHERE profile_id = ?", (profile_id,))
            return None

        d = self.dbpool.runInteraction(delete)
        d.addCallback(lambda ignore: log.info(_("Profile [%s] deleted") % name))
        d.addErrback(deletionError)
        return d

    ## Params
    def loadGenParams(self, params_gen):
        """Load general parameters

        @param params_gen: dictionary to fill
        @return: deferred
        """

        def fillParams(result):
            for param in result:
                category, name, value = param
                params_gen[(category, name)] = value
        log.debug(_("loading general parameters from database"))
        return self.dbpool.runQuery("SELECT category,name,value FROM param_gen").addCallback(fillParams)

    def loadIndParams(self, params_ind, profile):
        """Load individual parameters

        @param params_ind: dictionary to fill
        @param profile: a profile which *must* exist
        @return: deferred
        """

        def fillParams(result):
            for param in result:
                category, name, value = param
                params_ind[(category, name)] = value
        log.debug(_("loading individual parameters from database"))
        d = self.dbpool.runQuery("SELECT category,name,value FROM param_ind WHERE profile_id=?", (self.profiles[profile], ))
        d.addCallback(fillParams)
        return d

    def getIndParam(self, category, name, profile):
        """Ask database for the value of one specific individual parameter

        @param category: category of the parameter
        @param name: name of the parameter
        @param profile: %(doc_profile)s
        @return: deferred
        """
        d = self.dbpool.runQuery(
            "SELECT value FROM param_ind WHERE category=? AND name=? AND profile_id=?",
            (category, name, self.profiles[profile]))
        d.addCallback(self.__getFirstResult)
        return d

    async def getIndParamValues(self, category, name):
        """Ask database for the individual values of a parameter for all profiles

        @param category: category of the parameter
        @param name: name of the parameter
        @return dict: profile => value map
        """
        result = await self.dbpool.runQuery(
            "SELECT profiles.name, param_ind.value FROM param_ind JOIN profiles ON "
            "param_ind.profile_id = profiles.id WHERE param_ind.category=? "
            "and param_ind.name=?",
            (category, name))
        return dict(result)

    def setGenParam(self, category, name, value):
        """Save the general parameters in database

        @param category: category of the parameter
        @param name: name of the parameter
        @param value: value to set
        @return: deferred"""
        d = self.dbpool.runQuery("REPLACE INTO param_gen(category,name,value) VALUES (?,?,?)", (category, name, value))
        d.addErrback(lambda ignore: log.error(_("Can't set general parameter (%(category)s/%(name)s) in database" % {"category": category, "name": name})))
        return d

    def setIndParam(self, category, name, value, profile):
        """Save the individual parameters in database

        @param category: category of the parameter
        @param name: name of the parameter
        @param value: value to set
        @param profile: a profile which *must* exist
        @return: deferred
        """
        d = self.dbpool.runQuery("REPLACE INTO param_ind(category,name,profile_id,value) VALUES (?,?,?,?)", (category, name, self.profiles[profile], value))
        d.addErrback(lambda ignore: log.error(_("Can't set individual parameter (%(category)s/%(name)s) for [%(profile)s] in database" % {"category": category, "name": name, "profile": profile})))
        return d

    ## History

    def _addToHistoryCb(self, __, data):
        # Message metadata were successfuly added to history
        # now we can add message and subject
        uid = data['uid']
        d_list = []
        for key in ('message', 'subject'):
            for lang, value in data[key].items():
                if not value.strip():
                    # no need to store empty messages
                    continue
                d = self.dbpool.runQuery(
                    "INSERT INTO {key}(history_uid, {key}, language) VALUES (?,?,?)"
                    .format(key=key),
                    (uid, value, lang or None))
                d.addErrback(lambda __: log.error(
                    _("Can't save following {key} in history (uid: {uid}, lang:{lang}):"
                      " {value}").format(
                    key=key, uid=uid, lang=lang, value=value)))
                d_list.append(d)
        try:
            thread = data['extra']['thread']
        except KeyError:
            pass
        else:
            thread_parent = data['extra'].get('thread_parent')
            d = self.dbpool.runQuery(
                "INSERT INTO thread(history_uid, thread_id, parent_id) VALUES (?,?,?)",
                (uid, thread, thread_parent))
            d.addErrback(lambda __: log.error(
                _("Can't save following thread in history (uid: {uid}): thread: "
                  "{thread}), parent:{parent}").format(
                uid=uid, thread=thread, parent=thread_parent)))
            d_list.append(d)
        return defer.DeferredList(d_list)

    def _addToHistoryEb(self, failure_, data):
        failure_.trap(sqlite3.IntegrityError)
        sqlite_msg = failure_.value.args[0]
        if "UNIQUE constraint failed" in sqlite_msg:
            log.debug("message {} is already in history, not storing it again"
                      .format(data['uid']))
            if 'received_timestamp' not in data:
                log.warning(
                    "duplicate message is not delayed, this is maybe a bug: data={}"
                    .format(data))
            # we cancel message to avoid sending duplicate message to frontends
            raise failure.Failure(exceptions.CancelError("Cancelled duplicated message"))
        else:
            log.error("Can't store message in history: {}".format(failure_))

    def _logHistoryError(self, failure_, from_jid, to_jid, data):
        if failure_.check(exceptions.CancelError):
            # we propagate CancelError to avoid sending message to frontends
            raise failure_
        log.error(_(
            "Can't save following message in history: from [{from_jid}] to [{to_jid}] "
            "(uid: {uid})")
            .format(from_jid=from_jid.full(), to_jid=to_jid.full(), uid=data['uid']))

    def addToHistory(self, data, profile):
        """Store a new message in history

        @param data(dict): message data as build by SatMessageProtocol.onMessage
        """
        extra = pickle.dumps({k: v for k, v in data['extra'].items()
                              if k not in NOT_IN_EXTRA}, 0)
        from_jid = data['from']
        to_jid = data['to']
        d = self.dbpool.runQuery(
            "INSERT INTO history(uid, stanza_id, update_uid, profile_id, source, dest, "
            "source_res, dest_res, timestamp, received_timestamp, type, extra) VALUES "
            "(?,?,?,?,?,?,?,?,?,?,?,?)",
            (data['uid'], data['extra'].get('stanza_id'), data['extra'].get('update_uid'),
            self.profiles[profile], data['from'].userhost(), to_jid.userhost(),
            from_jid.resource, to_jid.resource, data['timestamp'],
            data.get('received_timestamp'), data['type'], sqlite3.Binary(extra)))
        d.addCallbacks(self._addToHistoryCb,
                       self._addToHistoryEb,
                       callbackArgs=[data],
                       errbackArgs=[data])
        d.addErrback(self._logHistoryError, from_jid, to_jid, data)
        return d

    def sqliteHistoryToList(self, query_result):
        """Get SQL query result and return a list of message data dicts"""
        result = []
        current = {'uid': None}
        for row in reversed(query_result):
            (uid, stanza_id, update_uid, source, dest, source_res, dest_res, timestamp,
             received_timestamp, type_, extra, message, message_lang, subject,
             subject_lang, thread, thread_parent) = row
            if uid != current['uid']:
                # new message
                try:
                    extra = self._load_pickle(extra or b"")
                except EOFError:
                    extra = {}
                current = {
                    'from': "%s/%s" % (source, source_res) if source_res else source,
                    'to': "%s/%s" % (dest, dest_res) if dest_res else dest,
                    'uid': uid,
                    'message': {},
                    'subject': {},
                    'type': type_,
                    'extra': extra,
                    'timestamp': timestamp,
                    }
                if stanza_id is not None:
                    current['extra']['stanza_id'] = stanza_id
                if update_uid is not None:
                    current['extra']['update_uid'] = update_uid
                if received_timestamp is not None:
                    current['extra']['received_timestamp'] = str(received_timestamp)
                result.append(current)

            if message is not None:
                current['message'][message_lang or ''] = message

            if subject is not None:
                current['subject'][subject_lang or ''] = subject

            if thread is not None:
                current_extra = current['extra']
                current_extra['thread'] = thread
                if thread_parent is not None:
                    current_extra['thread_parent'] = thread_parent
            else:
                if thread_parent is not None:
                    log.error(
                        "Database inconsistency: thread parent without thread (uid: "
                        "{uid}, thread_parent: {parent})"
                        .format(uid=uid, parent=thread_parent))

        return result

    def listDict2listTuple(self, messages_data):
        """Return a list of tuple as used in bridge from a list of messages data"""
        ret = []
        for m in messages_data:
            ret.append((m['uid'], m['timestamp'], m['from'], m['to'], m['message'], m['subject'], m['type'], m['extra']))
        return ret

    def historyGet(self, from_jid, to_jid, limit=None, between=True, filters=None, profile=None):
        """Retrieve messages in history

        @param from_jid (JID): source JID (full, or bare for catchall)
        @param to_jid (JID): dest JID (full, or bare for catchall)
        @param limit (int): maximum number of messages to get:
            - 0 for no message (returns the empty list)
            - None for unlimited
        @param between (bool): confound source and dest (ignore the direction)
        @param filters (dict[unicode, unicode]): pattern to filter the history results
        @param profile (unicode): %(doc_profile)s
        @return: list of tuple as in [messageNew]
        """
        assert profile
        if filters is None:
            filters = {}
        if limit == 0:
            return defer.succeed([])

        query_parts = ["SELECT uid, stanza_id, update_uid, source, dest, source_res, dest_res, timestamp, received_timestamp,\
                        type, extra, message, message.language, subject, subject.language, thread_id, thread.parent_id\
                        FROM history LEFT JOIN message ON history.uid = message.history_uid\
                        LEFT JOIN subject ON history.uid=subject.history_uid\
                        LEFT JOIN thread ON history.uid=thread.history_uid\
                        WHERE profile_id=?"] # FIXME: not sure if it's the best request, messages and subjects can appear several times here
        values = [self.profiles[profile]]

        def test_jid(type_, jid_):
            values.append(jid_.userhost())
            if jid_.resource:
                values.append(jid_.resource)
                return '({type_}=? AND {type_}_res=?)'.format(type_=type_)
            return '{type_}=?'.format(type_=type_)

        if not from_jid and not to_jid:
            # not jid specified, we want all one2one communications
            pass
        elif between:
            if not from_jid or not to_jid:
                # we only have one jid specified, we check all messages
                # from or to this jid
                jid_ = from_jid or to_jid
                query_parts.append("AND ({source} OR {dest})".format(
                    source=test_jid('source', jid_),
                    dest=test_jid('dest' , jid_)))
            else:
                # we have 2 jids specified, we check all communications between
                # those 2 jids
                query_parts.append(
                    "AND (({source_from} AND {dest_to}) "
                    "OR ({source_to} AND {dest_from}))".format(
                    source_from=test_jid('source', from_jid),
                    dest_to=test_jid('dest', to_jid),
                    source_to=test_jid('source', to_jid),
                    dest_from=test_jid('dest', from_jid)))
        else:
            # we want one communication in specific direction (from somebody or
            # to somebody).
            q = []
            if from_jid is not None:
                q.append(test_jid('source', from_jid))
            if to_jid is not None:
                q.append(test_jid('dest', to_jid))
            query_parts.append("AND " + " AND ".join(q))

        if filters:
            if 'timestamp_start' in filters:
                query_parts.append("AND timestamp>= ?")
                values.append(float(filters['timestamp_start']))
            if 'before_uid' in filters:
                query_parts.append("AND history.rowid<(select rowid from history where uid=?)")
                values.append(filters['before_uid'])
            if 'body' in filters:
                # TODO: use REGEXP (function to be defined) instead of GLOB: https://www.sqlite.org/lang_expr.html
                query_parts.append("AND message LIKE ?")
                values.append("%{}%".format(filters['body']))
            if 'search' in filters:
                query_parts.append("AND (message LIKE ? OR source_res LIKE ?)")
                values.extend(["%{}%".format(filters['search'])] * 2)
            if 'types' in filters:
                types = filters['types'].split()
                query_parts.append("AND type IN ({})".format(','.join("?"*len(types))))
                values.extend(types)
            if 'not_types' in filters:
                types = filters['not_types'].split()
                query_parts.append("AND type NOT IN ({})".format(','.join("?"*len(types))))
                values.extend(types)
            if 'last_stanza_id' in filters:
                # this request get the last message with a "stanza_id" that we
                # have in history. This is mainly used to retrieve messages sent
                # while we were offline, using MAM (XEP-0313).
                if (filters['last_stanza_id'] is not True
                    or limit != 1):
                    raise ValueError("Unexpected values for last_stanza_id filter")
                query_parts.append("AND stanza_id IS NOT NULL")


        # timestamp may be identical for 2 close messages (specially when delay is
        # used) that's why we order ties by received_timestamp
        # We'll reverse the order in sqliteHistoryToList
        # we use DESC here so LIMIT keep the last messages
        query_parts.append("ORDER BY timestamp DESC, history.received_timestamp DESC")
        if limit is not None:
            query_parts.append("LIMIT ?")
            values.append(limit)

        d = self.dbpool.runQuery(" ".join(query_parts), values)
        d.addCallback(self.sqliteHistoryToList)
        d.addCallback(self.listDict2listTuple)
        return d

    ## Private values

    def _privateDataEb(self, failure_, operation, namespace, key=None, profile=None):
        """generic errback for data queries"""
        log.error(_("Can't {operation} data in database for namespace {namespace}{and_key}{for_profile}: {msg}").format(
            operation = operation,
            namespace = namespace,
            and_key = (" and key " + key) if key is not None else "",
            for_profile = (' [' + profile + ']') if profile is not None else '',
            msg = failure_))

    def _load_pickle(self, v):
        # FIXME: workaround for Python 3 port, some pickled data are bytes while other are strings
        try:
            return pickle.loads(v, encoding="utf-8")
        except TypeError:
            data = pickle.loads(v.encode('utf-8'), encoding="utf-8")
            log.debug(f"encoding issue in pickled data: {data}")
            return data

    def _generateDataDict(self, query_result, binary):
        if binary:
            return {k: self._load_pickle(v) for k,v in query_result}
        else:
            return dict(query_result)

    def _getPrivateTable(self, binary, profile):
        """Get table to use for private values"""
        table = ['private']

        if profile is None:
            table.append('gen')
        else:
            table.append('ind')

        if binary:
            table.append('bin')

        return '_'.join(table)

    def getPrivates(self, namespace, keys=None, binary=False, profile=None):
        """Get private value(s) from databases

        @param namespace(unicode): namespace of the values
        @param keys(iterable, None): keys of the values to get
            None to get all keys/values
        @param binary(bool): True to deserialise binary values
        @param profile(unicode, None): profile to use for individual values
            None to use general values
        @return (dict[unicode, object]): gotten keys/values
        """
        log.debug(_("getting {type}{binary} private values from database for namespace {namespace}{keys}".format(
            type = "general" if profile is None else "individual",
            binary = " binary" if binary else "",
            namespace = namespace,
            keys = " with keys {}".format(", ".join(keys)) if keys is not None else "")))
        table = self._getPrivateTable(binary, profile)
        query_parts = ["SELECT key,value FROM", table, "WHERE namespace=?"]
        args = [namespace]

        if keys is not None:
            placeholders = ','.join(len(keys) * '?')
            query_parts.append('AND key IN (' + placeholders + ')')
            args.extend(keys)

        if profile is not None:
            query_parts.append('AND profile_id=?')
            args.append(self.profiles[profile])

        d = self.dbpool.runQuery(" ".join(query_parts), args)
        d.addCallback(self._generateDataDict, binary)
        d.addErrback(self._privateDataEb, "get", namespace, profile=profile)
        return d

    def setPrivateValue(self, namespace, key, value, binary=False, profile=None):
        """Set a private value in database

        @param namespace(unicode): namespace of the values
        @param key(unicode): key of the value to set
        @param value(object): value to set
        @param binary(bool): True if it's a binary values
            binary values need to be serialised, used for everything but strings
        @param profile(unicode, None): profile to use for individual value
            if None, it's a general value
        """
        table = self._getPrivateTable(binary, profile)
        query_values_names = ['namespace', 'key', 'value']
        query_values = [namespace, key]

        if binary:
            value = sqlite3.Binary(pickle.dumps(value, 0))

        query_values.append(value)

        if profile is not None:
            query_values_names.append('profile_id')
            query_values.append(self.profiles[profile])

        query_parts = ["REPLACE INTO", table, '(', ','.join(query_values_names), ')',
                       "VALUES (", ",".join('?'*len(query_values_names)), ')']

        d = self.dbpool.runQuery(" ".join(query_parts), query_values)
        d.addErrback(self._privateDataEb, "set", namespace, key, profile=profile)
        return d

    def delPrivateValue(self, namespace, key, binary=False, profile=None):
        """Delete private value from database

        @param category: category of the privateeter
        @param key: key of the private value
        @param binary(bool): True if it's a binary values
        @param profile(unicode, None): profile to use for individual value
            if None, it's a general value
        """
        table = self._getPrivateTable(binary, profile)
        query_parts = ["DELETE FROM", table, "WHERE namespace=? AND key=?"]
        args = [namespace, key]
        if profile is not None:
            query_parts.append("AND profile_id=?")
            args.append(self.profiles[profile])
        d = self.dbpool.runQuery(" ".join(query_parts), args)
        d.addErrback(self._privateDataEb, "delete", namespace, key, profile=profile)
        return d

    def delPrivateNamespace(self, namespace, binary=False, profile=None):
        """Delete all data from a private namespace

        Be really cautious when you use this method, as all data with given namespace are
        removed.
        Params are the same as for delPrivateValue
        """
        table = self._getPrivateTable(binary, profile)
        query_parts = ["DELETE FROM", table, "WHERE namespace=?"]
        args = [namespace]
        if profile is not None:
            query_parts.append("AND profile_id=?")
            args.append(self.profiles[profile])
        d = self.dbpool.runQuery(" ".join(query_parts), args)
        d.addErrback(self._privateDataEb, "delete namespace", namespace, profile=profile)
        return d

    ## Files

    @defer.inlineCallbacks
    def getFiles(self, client, file_id=None, version='', parent=None, type_=None,
                 file_hash=None, hash_algo=None, name=None, namespace=None, mime_type=None,
                 public_id=None, owner=None, access=None, projection=None, unique=False):
        """retrieve files with with given filters

        @param file_id(unicode, None): id of the file
            None to ignore
        @param version(unicode, None): version of the file
            None to ignore
            empty string to look for current version
        @param parent(unicode, None): id of the directory containing the files
            None to ignore
            empty string to look for root files/directories
        @param projection(list[unicode], None): name of columns to retrieve
            None to retrieve all
        @param unique(bool): if True will remove duplicates
        other params are the same as for [setFile]
        @return (list[dict]): files corresponding to filters
        """
        query_parts = ["SELECT"]
        if unique:
            query_parts.append('DISTINCT')
        if projection is None:
            projection = ['id', 'version', 'parent', 'type', 'file_hash', 'hash_algo', 'name',
                          'size', 'namespace', 'media_type', 'media_subtype', 'public_id', 'created', 'modified', 'owner',
                          'access', 'extra']
        query_parts.append(','.join(projection))
        query_parts.append("FROM files WHERE")
        if client is not None:
            filters = ['profile_id=?']
            args = [self.profiles[client.profile]]
        else:
            if public_id is None:
                raise exceptions.InternalError(
                    "client can only be omitted when public_id is set")
            filters = []
            args = []

        if file_id is not None:
            filters.append('id=?')
            args.append(file_id)
        if version is not None:
            filters.append('version=?')
            args.append(version)
        if parent is not None:
            filters.append('parent=?')
            args.append(parent)
        if type_ is not None:
            filters.append('type=?')
            args.append(type_)
        if file_hash is not None:
            filters.append('file_hash=?')
            args.append(file_hash)
        if hash_algo is not None:
            filters.append('hash_algo=?')
            args.append(hash_algo)
        if name is not None:
            filters.append('name=?')
            args.append(name)
        if namespace is not None:
            filters.append('namespace=?')
            args.append(namespace)
        if mime_type is not None:
            if '/' in mime_type:
                filters.extend('media_type=?', 'media_subtype=?')
                args.extend(mime_type.split('/', 1))
            else:
                filters.append('media_type=?')
                args.append(mime_type)
        if public_id is not None:
            filters.append('public_id=?')
            args.append(public_id)
        if owner is not None:
            filters.append('owner=?')
            args.append(owner.full())
        if access is not None:
            raise NotImplementedError('Access check is not implemented yet')
            # a JSON comparison is needed here

        filters = ' AND '.join(filters)
        query_parts.append(filters)
        query = ' '.join(query_parts)

        result = yield self.dbpool.runQuery(query, args)
        files_data = [dict(list(zip(projection, row))) for row in result]
        to_parse = {'access', 'extra'}.intersection(projection)
        to_filter = {'owner'}.intersection(projection)
        if to_parse or to_filter:
            for file_data in files_data:
                for key in to_parse:
                    value = file_data[key]
                    file_data[key] = {} if value is None else json.loads(value)
                owner = file_data.get('owner')
                if owner is not None:
                    file_data['owner'] = jid.JID(owner)
        defer.returnValue(files_data)

    def setFile(self, client, name, file_id, version='', parent=None, type_=C.FILE_TYPE_FILE,
                file_hash=None, hash_algo=None, size=None, namespace=None, mime_type=None,
                public_id=None, created=None, modified=None, owner=None, access=None, extra=None):
        """set a file metadata

        @param client(SatXMPPClient): client owning the file
        @param name(str): name of the file (must not contain "/")
        @param file_id(str): unique id of the file
        @param version(str): version of this file
        @param parent(str): id of the directory containing this file
            None if it is a root file/directory
        @param type_(str): one of:
            - file
            - directory
        @param file_hash(str): unique hash of the payload
        @param hash_algo(str): algorithm used for hashing the file (usually sha-256)
        @param size(int): size in bytes
        @param namespace(str, None): identifier (human readable is better) to group files
            for instance, namespace could be used to group files in a specific photo album
        @param mime_type(str): media type of the file, or None if not known/guessed
        @param public_id(str): ID used to server the file publicly via HTTP
        @param created(int): UNIX time of creation
        @param modified(int,None): UNIX time of last modification, or None to use created date
        @param owner(jid.JID, None): jid of the owner of the file (mainly useful for component)
        @param access(dict, None): serialisable dictionary with access rules. See [memory.memory] for details
        @param extra(dict, None): serialisable dictionary of any extra data
            will be encoded to json in database
        """
        if extra is not None:
            assert isinstance(extra, dict)

        if mime_type is None:
            media_type = media_subtype = None
        elif '/' in mime_type:
            media_type, media_subtype = mime_type.split('/', 1)
        else:
            media_type, media_subtype = mime_type, None

        query = ('INSERT INTO files(id, version, parent, type, file_hash, hash_algo, name, size, namespace, '
                 'media_type, media_subtype, public_id, created, modified, owner, access, extra, profile_id) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)')
        d = self.dbpool.runQuery(query, (file_id, version.strip(), parent, type_,
                                         file_hash, hash_algo,
                                         name, size, namespace,
                                         media_type, media_subtype, public_id, created, modified,
                                         owner.full() if owner is not None else None,
                                         json.dumps(access) if access else None,
                                         json.dumps(extra) if extra else None,
                                         self.profiles[client.profile]))
        d.addErrback(lambda failure: log.error(_("Can't save file metadata for [{profile}]: {reason}".format(profile=client.profile, reason=failure))))
        return d

    async def fileGetUsedSpace(self, client, owner):
        """Get space used by owner of file"""
        query = "SELECT SUM(size) FROM files WHERE owner=? AND type='file' AND profile_id=?"
        ret = await self.dbpool.runQuery(
            query,
            (owner.userhost(), self.profiles[client.profile])
        )
        return ret[0][0] or 0

    def _fileUpdate(self, cursor, file_id, column, update_cb):
        query = 'SELECT {column} FROM files where id=?'.format(column=column)
        for i in range(5):
            cursor.execute(query, [file_id])
            try:
                older_value_raw = cursor.fetchone()[0]
            except TypeError:
                raise exceptions.NotFound
            if older_value_raw is None:
                value = {}
            else:
                value = json.loads(older_value_raw)
            update_cb(value)
            value_raw = json.dumps(value)
            if older_value_raw is None:
                update_query = 'UPDATE files SET {column}=? WHERE id=? AND {column} is NULL'.format(column=column)
                update_args = (value_raw, file_id)
            else:
                update_query = 'UPDATE files SET {column}=? WHERE id=? AND {column}=?'.format(column=column)
                update_args = (value_raw, file_id, older_value_raw)
            try:
                cursor.execute(update_query, update_args)
            except sqlite3.Error:
                pass
            else:
                if cursor.rowcount == 1:
                    break;
            log.warning(_("table not updated, probably due to race condition, trying again ({tries})").format(tries=i+1))
        else:
            log.error(_("Can't update file table"))

    def fileUpdate(self, file_id, column, update_cb):
        """Update a column value using a method to avoid race conditions

        the older value will be retrieved from database, then update_cb will be applied
        to update it, and file will be updated checking that older value has not been changed meanwhile
        by an other user. If it has changed, it tries again a couple of times before failing
        @param column(str): column name (only "access" or "extra" are allowed)
        @param update_cb(callable): method to update the value of the colum
            the method will take older value as argument, and must update it in place
            update_cb must not care about serialization,
            it get the deserialized data (i.e. a Python object) directly
            Note that the callable must be thread-safe
        @raise exceptions.NotFound: there is not file with this id
        """
        if column not in ('access', 'extra'):
            raise exceptions.InternalError('bad column name')
        return self.dbpool.runInteraction(self._fileUpdate, file_id, column, update_cb)

    def fileDelete(self, file_id):
        """Delete file metadata from the database

        @param file_id(unicode): id of the file to delete
        NOTE: file itself must still be removed, this method only handle metadata in
            database
        """
        return self.dbpool.runQuery("DELETE FROM files WHERE id = ?", (file_id,))

    ##Helper methods##

    def __getFirstResult(self, result):
        """Return the first result of a database query
        Useful when we are looking for one specific value"""
        return None if not result else result[0][0]


class Updater(object):
    stmnt_regex = re.compile(r"[\w/' ]+(?:\(.*?\))?[^,]*")
    clean_regex = re.compile(r"^ +|(?<= ) +|(?<=,) +| +$")
    CREATE_SQL = "CREATE TABLE %s (%s)"
    INSERT_SQL = "INSERT INTO %s VALUES (%s)"
    INDEX_SQL = "CREATE INDEX %s ON %s(%s)"
    DROP_SQL = "DROP TABLE %s"
    ALTER_SQL = "ALTER TABLE %s ADD COLUMN %s"
    RENAME_TABLE_SQL = "ALTER TABLE %s RENAME TO %s"

    CONSTRAINTS = ('PRIMARY', 'UNIQUE', 'CHECK', 'FOREIGN')
    TMP_TABLE = "tmp_sat_update"

    def __init__(self, sqlite_storage, sat_version):
        self._sat_version = sat_version
        self.sqlite_storage = sqlite_storage

    @property
    def dbpool(self):
        return self.sqlite_storage.dbpool

    def getLocalVersion(self):
        """ Get local database version

        @return: version (int)
        """
        return self.dbpool.runQuery("PRAGMA user_version").addCallback(lambda ret: int(ret[0][0]))

    def _setLocalVersion(self, version):
        """ Set local database version

        @param version: version (int)
        @return: deferred
        """
        return self.dbpool.runOperation("PRAGMA user_version=%d" % version)

    def getLocalSchema(self):
        """ return raw local schema

        @return: list of strings with CREATE sql statements for local database
        """
        d = self.dbpool.runQuery("select sql from sqlite_master where type = 'table'")
        d.addCallback(lambda result: [row[0] for row in result])
        return d

    @defer.inlineCallbacks
    def checkUpdates(self):
        """ Check if a database schema/content update is needed, according to DATABASE_SCHEMAS

        @return: deferred which fire a list of SQL update statements, or None if no update is needed
        """
        # TODO: only "table" type (i.e. "CREATE" statements) is checked,
        #       "index" should be checked too.
        #       This may be not relevant is we move to a higher level library (alchimia?)
        local_version = yield self.getLocalVersion()
        raw_local_sch = yield self.getLocalSchema()

        local_sch = self.rawStatements2data(raw_local_sch)
        current_sch = DATABASE_SCHEMAS['current']['CREATE']
        local_hash = self.statementHash(local_sch)
        current_hash = self.statementHash(current_sch)

        # Force the update if the schemas are unchanged but a specific update is needed
        force_update = local_hash == current_hash and local_version < CURRENT_DB_VERSION \
                        and {'index', 'specific'}.intersection(DATABASE_SCHEMAS[CURRENT_DB_VERSION])

        if local_hash == current_hash and not force_update:
            if local_version != CURRENT_DB_VERSION:
                log.warning(_("Your local schema is up-to-date, but database versions mismatch, fixing it..."))
                yield self._setLocalVersion(CURRENT_DB_VERSION)
        else:
            # an update is needed

            if local_version == CURRENT_DB_VERSION:
                # Database mismatch and we have the latest version
                if self._sat_version.endswith('D'):
                    # we are in a development version
                    update_data = self.generateUpdateData(local_sch, current_sch, False)
                    log.warning(_("There is a schema mismatch, but as we are on a dev version, database will be updated"))
                    update_raw = yield self.update2raw(update_data, True)
                    defer.returnValue(update_raw)
                else:
                    log.error(_("schema version is up-to-date, but local schema differ from expected current schema"))
                    update_data = self.generateUpdateData(local_sch, current_sch, True)
                    update_raw = yield self.update2raw(update_data)
                    log.warning(_("Here are the commands that should fix the situation, use at your own risk (do a backup before modifying database), you can go to SàT's MUC room at sat@chat.jabberfr.org for help\n### SQL###\n%s\n### END SQL ###\n") % '\n'.join("%s;" % statement for statement in update_raw))
                    raise exceptions.DatabaseError("Database mismatch")
            else:
                if local_version > CURRENT_DB_VERSION:
                    log.error(_(
                        "You database version is higher than the one used in this SàT "
                        "version, are you using several version at the same time? We "
                        "can't run SàT with this database."))
                    sys.exit(1)

                # Database is not up-to-date, we'll do the update
                if force_update:
                    log.info(_("Database content needs a specific processing, local database will be updated"))
                else:
                    log.info(_("Database schema has changed, local database will be updated"))
                update_raw = []
                for version in range(local_version + 1, CURRENT_DB_VERSION + 1):
                    try:
                        update_data = DATABASE_SCHEMAS[version]
                    except KeyError:
                        raise exceptions.InternalError("Missing update definition (version %d)" % version)
                    if "specific" in update_data and update_raw:
                        # if we have a specific, we must commit current statements
                        # because a specific may modify database itself, and the database
                        # must be in the expected state of the previous version.
                        yield self.sqlite_storage.commitStatements(update_raw)
                        del update_raw[:]
                    update_raw_step = yield self.update2raw(update_data)
                    if update_raw_step is not None:
                        # can be None with specifics
                        update_raw.extend(update_raw_step)
                update_raw.append("PRAGMA user_version=%d" % CURRENT_DB_VERSION)
                defer.returnValue(update_raw)

    @staticmethod
    def createData2Raw(data):
        """ Generate SQL statements from statements data

        @param data: dictionary with table as key, and statements data in tuples as value
        @return: list of strings with raw statements
        """
        ret = []
        for table in data:
            defs, constraints = data[table]
            assert isinstance(defs, tuple)
            assert isinstance(constraints, tuple)
            ret.append(Updater.CREATE_SQL % (table, ', '.join(defs + constraints)))
        return ret

    @staticmethod
    def insertData2Raw(data):
        """ Generate SQL statements from statements data

        @param data: dictionary with table as key, and statements data in tuples as value
        @return: list of strings with raw statements
        """
        ret = []
        for table in data:
            values_tuple = data[table]
            assert isinstance(values_tuple, tuple)
            for values in values_tuple:
                assert isinstance(values, tuple)
                ret.append(Updater.INSERT_SQL % (table, ', '.join(values)))
        return ret

    @staticmethod
    def indexData2Raw(data):
        """ Generate SQL statements from statements data

        @param data: dictionary with table as key, and statements data in tuples as value
        @return: list of strings with raw statements
        """
        ret = []
        assert isinstance(data, tuple)
        for table, col_data in data:
            assert isinstance(table, str)
            assert isinstance(col_data, tuple)
            for cols in col_data:
                if isinstance(cols, tuple):
                    assert all([isinstance(c, str) for c in cols])
                    indexed_cols = ','.join(cols)
                elif isinstance(cols, str):
                    indexed_cols = cols
                else:
                    raise exceptions.InternalError("unexpected index columns value")
                index_name = table + '__' + indexed_cols.replace(',', '_')
                ret.append(Updater.INDEX_SQL % (index_name, table, indexed_cols))
        return ret

    def statementHash(self, data):
        """ Generate hash of template data

        useful to compare schemas
        @param data: dictionary of "CREATE" statement, with tables names as key,
                     and tuples of (col_defs, constraints) as values
        @return: hash as string
        """
        hash_ = hashlib.sha1()
        tables = list(data.keys())
        tables.sort()

        def stmnts2str(stmts):
            return ','.join([self.clean_regex.sub('',stmt) for stmt in sorted(stmts)])

        for table in tables:
            col_defs, col_constr = data[table]
            hash_.update(
                ("%s:%s:%s" % (table, stmnts2str(col_defs), stmnts2str(col_constr)))
                .encode('utf-8'))
        return hash_.digest()

    def rawStatements2data(self, raw_statements):
        """ separate "CREATE" statements into dictionary/tuples data

        @param raw_statements: list of CREATE statements as strings
        @return: dictionary with table names as key, and a (col_defs, constraints) tuple
        """
        schema_dict = {}
        for create_statement in raw_statements:
            if not create_statement.startswith("CREATE TABLE "):
                log.warning("Unexpected statement, ignoring it")
                continue
            _create_statement = create_statement[13:]
            table, raw_col_stats = _create_statement.split(' ',1)
            if raw_col_stats[0] != '(' or raw_col_stats[-1] != ')':
                log.warning("Unexpected statement structure, ignoring it")
                continue
            col_stats = [stmt.strip() for stmt in self.stmnt_regex.findall(raw_col_stats[1:-1])]
            col_defs = []
            constraints = []
            for col_stat in col_stats:
                name = col_stat.split(' ',1)[0]
                if name in self.CONSTRAINTS:
                    constraints.append(col_stat)
                else:
                    col_defs.append(col_stat)
            schema_dict[table] = (tuple(col_defs), tuple(constraints))
        return schema_dict

    def generateUpdateData(self, old_data, new_data, modify=False):
        """ Generate data for automatic update between two schema data

        @param old_data: data of the former schema (which must be updated)
        @param new_data: data of the current schema
        @param modify: if True, always use "cols modify" table, else try to ALTER tables
        @return: update data, a dictionary with:
                 - 'create': dictionary of tables to create
                 - 'delete': tuple of tables to delete
                 - 'cols create': dictionary of columns to create (table as key, tuple of columns to create as value)
                 - 'cols delete': dictionary of columns to delete (table as key, tuple of columns to delete as value)
                 - 'cols modify': dictionary of columns to modify (table as key, tuple of old columns to transfert as value). With this table, a new table will be created, and content from the old table will be transfered to it, only cols specified in the tuple will be transfered.
        """

        create_tables_data = {}
        create_cols_data = {}
        modify_cols_data = {}
        delete_cols_data = {}
        old_tables = set(old_data.keys())
        new_tables = set(new_data.keys())

        def getChanges(set_olds, set_news):
            to_create = set_news.difference(set_olds)
            to_delete = set_olds.difference(set_news)
            to_check = set_news.intersection(set_olds)
            return tuple(to_create), tuple(to_delete), tuple(to_check)

        tables_to_create, tables_to_delete, tables_to_check = getChanges(old_tables, new_tables)

        for table in tables_to_create:
            create_tables_data[table] = new_data[table]

        for table in tables_to_check:
            old_col_defs, old_constraints = old_data[table]
            new_col_defs, new_constraints = new_data[table]
            for obj in old_col_defs, old_constraints, new_col_defs, new_constraints:
                if not isinstance(obj, tuple):
                    raise exceptions.InternalError("Columns definitions must be tuples")
            defs_create, defs_delete, ignore = getChanges(set(old_col_defs), set(new_col_defs))
            constraints_create, constraints_delete, ignore = getChanges(set(old_constraints), set(new_constraints))
            created_col_names = set([name.split(' ',1)[0] for name in defs_create])
            deleted_col_names = set([name.split(' ',1)[0] for name in defs_delete])
            if (created_col_names.intersection(deleted_col_names or constraints_create or constraints_delete) or
                (modify and (defs_create or constraints_create or defs_delete or constraints_delete))):
                # we have modified columns, we need to transfer table
                # we determinate which columns are in both schema so we can transfer them
                old_names = set([name.split(' ',1)[0] for name in old_col_defs])
                new_names = set([name.split(' ',1)[0] for name in new_col_defs])
                modify_cols_data[table] = tuple(old_names.intersection(new_names));
            else:
                if defs_create:
                    create_cols_data[table] = (defs_create)
                if defs_delete or constraints_delete:
                    delete_cols_data[table] = (defs_delete)

        return {'create': create_tables_data,
                'delete': tables_to_delete,
                'cols create': create_cols_data,
                'cols delete': delete_cols_data,
                'cols modify': modify_cols_data
                }

    @defer.inlineCallbacks
    def update2raw(self, update, dev_version=False):
        """ Transform update data to raw SQLite statements

        @param update: update data as returned by generateUpdateData
        @param dev_version: if True, update will be done in dev mode: no deletion will be done, instead a message will be shown. This prevent accidental lost of data while working on the code/database.
        @return: list of string with SQL statements needed to update the base
        """
        ret = self.createData2Raw(update.get('create', {}))
        drop = []
        for table in update.get('delete', tuple()):
            drop.append(self.DROP_SQL % table)
        if dev_version:
            if drop:
                log.info("Dev version, SQL NOT EXECUTED:\n--\n%s\n--\n" % "\n".join(drop))
        else:
            ret.extend(drop)

        cols_create = update.get('cols create', {})
        for table in cols_create:
            for col_def in cols_create[table]:
                ret.append(self.ALTER_SQL % (table, col_def))

        cols_delete = update.get('cols delete', {})
        for table in cols_delete:
            log.info("Following columns in table [%s] are not needed anymore, but are kept for dev version: %s" % (table, ", ".join(cols_delete[table])))

        cols_modify = update.get('cols modify', {})
        for table in cols_modify:
            ret.append(self.RENAME_TABLE_SQL % (table, self.TMP_TABLE))
            main, extra = DATABASE_SCHEMAS['current']['CREATE'][table]
            ret.append(self.CREATE_SQL % (table, ', '.join(main + extra)))
            common_cols = ', '.join(cols_modify[table])
            ret.append("INSERT INTO %s (%s) SELECT %s FROM %s" % (table, common_cols, common_cols, self.TMP_TABLE))
            ret.append(self.DROP_SQL % self.TMP_TABLE)

        insert = update.get('insert', {})
        ret.extend(self.insertData2Raw(insert))

        index = update.get('index', tuple())
        ret.extend(self.indexData2Raw(index))

        specific = update.get('specific', None)
        if specific:
            cmds = yield getattr(self, specific)()
            ret.extend(cmds or [])
        defer.returnValue(ret)

    def update_v9(self):
        """Update database from v8 to v9

        (public_id on file with UNIQUE constraint, files indexes fix, media_type split)
        """
        # we have to do a specific update because we can't set UNIQUE constraint when adding a column
        # (see https://sqlite.org/lang_altertable.html#alter_table_add_column)
        log.info("Database update to v9")

        create = {
            'files': (("id TEXT NOT NULL", "public_id TEXT", "version TEXT NOT NULL",
                       "parent TEXT NOT NULL",
                       "type TEXT CHECK(type in ('{file}', '{directory}')) NOT NULL DEFAULT '{file}'".format(
                           file=C.FILE_TYPE_FILE, directory=C.FILE_TYPE_DIRECTORY),
                       "file_hash TEXT", "hash_algo TEXT", "name TEXT NOT NULL", "size INTEGER",
                       "namespace TEXT", "media_type TEXT", "media_subtype TEXT",
                       "created DATETIME NOT NULL", "modified DATETIME",
                       "owner TEXT", "access TEXT", "extra TEXT", "profile_id INTEGER"),
                      ("PRIMARY KEY (id, version)", "FOREIGN KEY(profile_id) REFERENCES profiles(id) ON DELETE CASCADE",
                       "UNIQUE (public_id)")),

        }
        index = tuple({'files': (('profile_id', 'owner', 'media_type', 'media_subtype'),
                                 ('profile_id', 'owner', 'parent'))}.items())
        # XXX: Sqlite doc recommends to do the other way around (i.e. create new table,
        #   copy, drop old table then rename), but the RENAME would then add
        #   "IF NOT EXISTS" which breaks the (admittely fragile) schema comparison.
        # TODO: rework sqlite update management, don't try to automatically detect
        #   update, the database version is now enough.
        statements = ["ALTER TABLE files RENAME TO files_old"]
        statements.extend(Updater.createData2Raw(create))
        cols = ','.join([col_stmt.split()[0] for col_stmt in create['files'][0] if "public_id" not in col_stmt])
        old_cols = cols[:]
        # we need to split mime_type to the new media_type and media_subtype
        old_cols = old_cols.replace(
            'media_type,media_subtype',
            "substr(mime_type, 0, instr(mime_type,'/')),substr(mime_type, instr(mime_type,'/')+1)"
        )
        statements.extend([
            f"INSERT INTO files({cols}) SELECT {old_cols} FROM files_old",
            "DROP TABLE files_old",
        ])
        statements.extend(Updater.indexData2Raw(index))
        return statements

    def update_v8(self):
        """Update database from v7 to v8 (primary keys order changes + indexes)"""
        log.info("Database update to v8")
        statements = ["PRAGMA foreign_keys = OFF"]

        # here is a copy of create and index data, we can't use "current" table
        # because it may change in a future version, which would break the update
        # when doing v8
        create = {
            'param_gen': (
                ("category TEXT", "name TEXT", "value TEXT"),
                ("PRIMARY KEY (category, name)",)),
            'param_ind': (
                ("category TEXT", "name TEXT", "profile_id INTEGER", "value TEXT"),
                ("PRIMARY KEY (profile_id, category, name)", "FOREIGN KEY(profile_id) REFERENCES profiles(id) ON DELETE CASCADE")),
            'private_ind': (
                ("namespace TEXT", "key TEXT", "profile_id INTEGER", "value TEXT"),
                ("PRIMARY KEY (profile_id, namespace, key)", "FOREIGN KEY(profile_id) REFERENCES profiles(id) ON DELETE CASCADE")),
            'private_ind_bin': (
                ("namespace TEXT", "key TEXT", "profile_id INTEGER", "value BLOB"),
                ("PRIMARY KEY (profile_id, namespace, key)", "FOREIGN KEY(profile_id) REFERENCES profiles(id) ON DELETE CASCADE")),
        }
        index = (
            ('history', (('profile_id', 'timestamp'),
            ('profile_id', 'received_timestamp'))),
            ('message', ('history_uid',)),
            ('subject', ('history_uid',)),
            ('thread', ('history_uid',)),
            ('files', ('profile_id', 'mime_type', 'owner', 'parent')))

        for table in ('param_gen', 'param_ind', 'private_ind', 'private_ind_bin'):
            statements.append("ALTER TABLE {0} RENAME TO {0}_old".format(table))
            schema = {table: create[table]}
            cols = [d.split()[0] for d in schema[table][0]]
            statements.extend(Updater.createData2Raw(schema))
            statements.append("INSERT INTO {table}({cols}) "
                              "SELECT {cols} FROM {table}_old".format(
                              table=table,
                              cols=','.join(cols)))
            statements.append("DROP TABLE {}_old".format(table))

        statements.extend(Updater.indexData2Raw(index))
        statements.append("PRAGMA foreign_keys = ON")
        return statements

    @defer.inlineCallbacks
    def update_v7(self):
        """Update database from v6 to v7 (history unique constraint change)"""
        log.info("Database update to v7, this may be long depending on your history "
                 "size, please be patient.")

        log.info("Some cleaning first")
        # we need to fix duplicate stanza_id, as it can result in conflicts with the new schema
        # normally database should not contain any, but better safe than sorry.
        rows = yield self.dbpool.runQuery(
            "SELECT stanza_id, COUNT(*) as c FROM history WHERE stanza_id is not NULL "
            "GROUP BY stanza_id HAVING c>1")
        if rows:
            count = sum([r[1] for r in rows]) - len(rows)
            log.info("{count} duplicate stanzas found, cleaning".format(count=count))
            for stanza_id, count in rows:
                log.info("cleaning duplicate stanza {stanza_id}".format(stanza_id=stanza_id))
                row_uids = yield self.dbpool.runQuery(
                    "SELECT uid FROM history WHERE stanza_id = ? LIMIT ?",
                    (stanza_id, count-1))
                uids = [r[0] for r in row_uids]
                yield self.dbpool.runQuery(
                    "DELETE FROM history WHERE uid IN ({})".format(",".join("?"*len(uids))),
                    uids)

        def deleteInfo(txn):
            # with foreign_keys on, the delete takes ages, so we deactivate it here
            # the time to delete info messages from history.
            txn.execute("PRAGMA foreign_keys = OFF")
            txn.execute("DELETE FROM message WHERE history_uid IN (SELECT uid FROM history WHERE "
                        "type='info')")
            txn.execute("DELETE FROM subject WHERE history_uid IN (SELECT uid FROM history WHERE "
                        "type='info')")
            txn.execute("DELETE FROM thread WHERE history_uid IN (SELECT uid FROM history WHERE "
                        "type='info')")
            txn.execute("DELETE FROM message WHERE history_uid IN (SELECT uid FROM history WHERE "
                        "type='info')")
            txn.execute("DELETE FROM history WHERE type='info'")
            # not sure that is is necessary to reactivate here, but in doubt…
            txn.execute("PRAGMA foreign_keys = ON")

        log.info('Deleting "info" messages (this can take a while)')
        yield self.dbpool.runInteraction(deleteInfo)

        log.info("Cleaning done")

        # we have to rename table we will replace
        # tables referencing history need to be replaced to, else reference would
        # be to the old table (which will be dropped at the end). This buggy behaviour
        # seems to be fixed in new version of Sqlite
        yield self.dbpool.runQuery("ALTER TABLE history RENAME TO history_old")
        yield self.dbpool.runQuery("ALTER TABLE message RENAME TO message_old")
        yield self.dbpool.runQuery("ALTER TABLE subject RENAME TO subject_old")
        yield self.dbpool.runQuery("ALTER TABLE thread RENAME TO thread_old")

        # history
        query = ("CREATE TABLE history (uid TEXT PRIMARY KEY, stanza_id TEXT, "
                 "update_uid TEXT, profile_id INTEGER, source TEXT, dest TEXT, "
                 "source_res TEXT, dest_res TEXT, timestamp DATETIME NOT NULL, "
                 "received_timestamp DATETIME, type TEXT, extra BLOB, "
                 "FOREIGN KEY(profile_id) REFERENCES profiles(id) ON DELETE CASCADE, "
                 "FOREIGN KEY(type) REFERENCES message_types(type), "
                 "UNIQUE (profile_id, stanza_id, source, dest))")
        yield self.dbpool.runQuery(query)

        # message
        query = ("CREATE TABLE message (id INTEGER PRIMARY KEY ASC, history_uid INTEGER"
                 ", message TEXT, language TEXT, FOREIGN KEY(history_uid) REFERENCES "
                 "history(uid) ON DELETE CASCADE)")
        yield self.dbpool.runQuery(query)

        # subject
        query = ("CREATE TABLE subject (id INTEGER PRIMARY KEY ASC, history_uid INTEGER"
                 ", subject TEXT, language TEXT, FOREIGN KEY(history_uid) REFERENCES "
                 "history(uid) ON DELETE CASCADE)")
        yield self.dbpool.runQuery(query)

        # thread
        query = ("CREATE TABLE thread (id INTEGER PRIMARY KEY ASC, history_uid INTEGER"
                 ", thread_id TEXT, parent_id TEXT, FOREIGN KEY(history_uid) REFERENCES "
                 "history(uid) ON DELETE CASCADE)")
        yield self.dbpool.runQuery(query)

        log.info("Now transfering old data to new tables, please be patient.")

        log.info("\nTransfering table history")
        query = ("INSERT INTO history (uid, stanza_id, update_uid, profile_id, source, "
                 "dest, source_res, dest_res, timestamp, received_timestamp, type, extra"
                 ") SELECT uid, stanza_id, update_uid, profile_id, source, dest, "
                 "source_res, dest_res, timestamp, received_timestamp, type, extra "
                 "FROM history_old")
        yield self.dbpool.runQuery(query)

        log.info("\nTransfering table message")
        query = ("INSERT INTO message (id, history_uid, message, language) SELECT id, "
                 "history_uid, message, language FROM message_old")
        yield self.dbpool.runQuery(query)

        log.info("\nTransfering table subject")
        query = ("INSERT INTO subject (id, history_uid, subject, language) SELECT id, "
                 "history_uid, subject, language FROM subject_old")
        yield self.dbpool.runQuery(query)

        log.info("\nTransfering table thread")
        query = ("INSERT INTO thread (id, history_uid, thread_id, parent_id) SELECT id"
                 ", history_uid, thread_id, parent_id FROM thread_old")
        yield self.dbpool.runQuery(query)

        log.info("\nRemoving old tables")
        # because of foreign keys, tables referencing history_old
        # must be deleted first
        yield self.dbpool.runQuery("DROP TABLE thread_old")
        yield self.dbpool.runQuery("DROP TABLE subject_old")
        yield self.dbpool.runQuery("DROP TABLE message_old")
        yield self.dbpool.runQuery("DROP TABLE history_old")
        log.info("\nReducing database size (this can take a while)")
        yield self.dbpool.runQuery("VACUUM")
        log.info("Database update done :)")

    @defer.inlineCallbacks
    def update_v3(self):
        """Update database from v2 to v3 (message refactoring)"""
        # XXX: this update do all the messages in one huge transaction
        #      this is really memory consuming, but was OK on a reasonably
        #      big database for tests. If issues are happening, we can cut it
        #      in smaller transactions using LIMIT and by deleting already updated
        #      messages
        log.info("Database update to v3, this may take a while")

        # we need to fix duplicate timestamp, as it can result in conflicts with the new schema
        rows = yield self.dbpool.runQuery("SELECT timestamp, COUNT(*) as c FROM history GROUP BY timestamp HAVING c>1")
        if rows:
            log.info("fixing duplicate timestamp")
            fixed = []
            for timestamp, __ in rows:
                ids_rows = yield self.dbpool.runQuery("SELECT id from history where timestamp=?", (timestamp,))
                for idx, (id_,) in enumerate(ids_rows):
                    fixed.append(id_)
                    yield self.dbpool.runQuery("UPDATE history SET timestamp=? WHERE id=?", (float(timestamp) + idx * 0.001, id_))
            log.info("fixed messages with ids {}".format(', '.join([str(id_) for id_ in fixed])))

        def historySchema(txn):
            log.info("History schema update")
            txn.execute("ALTER TABLE history RENAME TO tmp_sat_update")
            txn.execute("CREATE TABLE history (uid TEXT PRIMARY KEY, update_uid TEXT, profile_id INTEGER, source TEXT, dest TEXT, source_res TEXT, dest_res TEXT, timestamp DATETIME NOT NULL, received_timestamp DATETIME, type TEXT, extra BLOB, FOREIGN KEY(profile_id) REFERENCES profiles(id) ON DELETE CASCADE, FOREIGN KEY(type) REFERENCES message_types(type), UNIQUE (profile_id, timestamp, source, dest, source_res, dest_res))")
            txn.execute("INSERT INTO history (uid, profile_id, source, dest, source_res, dest_res, timestamp, type, extra) SELECT id, profile_id, source, dest, source_res, dest_res, timestamp, type, extra FROM tmp_sat_update")

        yield self.dbpool.runInteraction(historySchema)

        def newTables(txn):
            log.info("Creating new tables")
            txn.execute("CREATE TABLE message (id INTEGER PRIMARY KEY ASC, history_uid INTEGER, message TEXT, language TEXT, FOREIGN KEY(history_uid) REFERENCES history(uid) ON DELETE CASCADE)")
            txn.execute("CREATE TABLE thread (id INTEGER PRIMARY KEY ASC, history_uid INTEGER, thread_id TEXT, parent_id TEXT, FOREIGN KEY(history_uid) REFERENCES history(uid) ON DELETE CASCADE)")
            txn.execute("CREATE TABLE subject (id INTEGER PRIMARY KEY ASC, history_uid INTEGER, subject TEXT, language TEXT, FOREIGN KEY(history_uid) REFERENCES history(uid) ON DELETE CASCADE)")

        yield self.dbpool.runInteraction(newTables)

        log.info("inserting new message type")
        yield self.dbpool.runQuery("INSERT INTO message_types VALUES (?)", ('info',))

        log.info("messages update")
        rows = yield self.dbpool.runQuery("SELECT id, timestamp, message, extra FROM tmp_sat_update")
        total = len(rows)

        def updateHistory(txn, queries):
            for query, args in iter(queries):
                txn.execute(query, args)

        queries = []
        for idx, row in enumerate(rows, 1):
            if idx % 1000 == 0 or total - idx == 0:
                log.info("preparing message {}/{}".format(idx, total))
            id_, timestamp, message, extra = row
            try:
                extra = self._load_pickle(extra or b"")
            except EOFError:
                extra = {}
            except Exception:
                log.warning("Can't handle extra data for message id {}, ignoring it".format(id_))
                extra = {}

            queries.append(("INSERT INTO message(history_uid, message) VALUES (?,?)", (id_, message)))

            try:
                subject = extra.pop('subject')
            except KeyError:
                pass
            else:
                try:
                    subject = subject
                except UnicodeEncodeError:
                    log.warning("Error while decoding subject, ignoring it")
                    del extra['subject']
                else:
                    queries.append(("INSERT INTO subject(history_uid, subject) VALUES (?,?)", (id_, subject)))

            received_timestamp = extra.pop('timestamp', None)
            try:
                del extra['archive']
            except KeyError:
                # archive was not used
                pass

            queries.append(("UPDATE history SET received_timestamp=?,extra=? WHERE uid=?",(id_, received_timestamp, sqlite3.Binary(pickle.dumps(extra, 0)))))

        yield self.dbpool.runInteraction(updateHistory, queries)

        log.info("Dropping temporary table")
        yield self.dbpool.runQuery("DROP TABLE tmp_sat_update")
        log.info("Database update finished :)")

    def update2raw_v2(self):
        """Update the database from v1 to v2 (add passwords encryptions):

            - the XMPP password value is re-used for the profile password (new parameter)
            - the profile password is stored hashed
            - the XMPP password is stored encrypted, with the profile password as key
            - as there are no other stored passwords yet, it is enough, otherwise we
              would need to encrypt the other passwords as it's done for XMPP password
        """
        xmpp_pass_path = ('Connection', 'Password')

        def encrypt_values(values):
            ret = []
            list_ = []

            def prepare_queries(result, xmpp_password):
                try:
                    id_ = result[0][0]
                except IndexError:
                    log.error("Profile of id %d is referenced in 'param_ind' but it doesn't exist!" % profile_id)
                    return defer.succeed(None)

                sat_password = xmpp_password
                sat_cipher = PasswordHasher.hash(sat_password)
                personal_key = BlockCipher.getRandomKey(base64=True)
                personal_cipher = BlockCipher.encrypt(sat_password, personal_key)
                xmpp_cipher = BlockCipher.encrypt(personal_key, xmpp_password)

                ret.append("INSERT INTO param_ind(category,name,profile_id,value) VALUES ('%s','%s',%s,'%s')" %
                           (C.PROFILE_PASS_PATH[0], C.PROFILE_PASS_PATH[1], id_, sat_cipher))

                ret.append("INSERT INTO private_ind(namespace,key,profile_id,value) VALUES ('%s','%s',%s,'%s')" %
                           (C.MEMORY_CRYPTO_NAMESPACE, C.MEMORY_CRYPTO_KEY, id_, personal_cipher))

                ret.append("REPLACE INTO param_ind(category,name,profile_id,value) VALUES ('%s','%s',%s,'%s')" %
                           (xmpp_pass_path[0], xmpp_pass_path[1], id_, xmpp_cipher))


            for profile_id, xmpp_password in values:
                d = self.dbpool.runQuery("SELECT id FROM profiles WHERE id=?", (profile_id,))
                d.addCallback(prepare_queries, xmpp_password)
                list_.append(d)

            d_list = defer.DeferredList(list_)
            d_list.addCallback(lambda __: ret)
            return d_list

        def updateLiberviaConf(values):
            try:
                profile_id = values[0][0]
            except IndexError:
                return  # no profile called "libervia"

            def cb(selected):
                try:
                    password = selected[0][0]
                except IndexError:
                    log.error("Libervia profile exists but no password is set! Update Libervia configuration will be skipped.")
                    return
                fixConfigOption('libervia', 'passphrase', password, False)
            d = self.dbpool.runQuery("SELECT value FROM param_ind WHERE category=? AND name=? AND profile_id=?", xmpp_pass_path + (profile_id,))
            return d.addCallback(cb)

        d = self.dbpool.runQuery("SELECT id FROM profiles WHERE name='libervia'")
        d.addCallback(updateLiberviaConf)
        d.addCallback(lambda __: self.dbpool.runQuery("SELECT profile_id,value FROM param_ind WHERE category=? AND name=?", xmpp_pass_path))
        d.addCallback(encrypt_values)
        return d
