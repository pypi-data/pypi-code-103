#!/usr/bin/env python3

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

from typing import Dict, List, Union, Coroutine, Any, Optional
from collections import namedtuple
from pathlib import Path
from twisted.internet import defer
from twisted.words.protocols.jabber import jid
from sat.core.xmpp import SatXMPPEntity
from sat.core.i18n import _
from sat.core.constants import Const as C
from sat.core import exceptions
from sat.core.log import getLogger
from sat.memory import persistent
from sat.tools import image
from sat.tools import utils
from sat.tools.common import data_format


log = getLogger(__name__)


IMPORT_NAME = "IDENTITY"


PLUGIN_INFO = {
    C.PI_NAME: "Identity Plugin",
    C.PI_IMPORT_NAME: IMPORT_NAME,
    C.PI_TYPE: C.PLUG_TYPE_MISC,
    C.PI_PROTOCOLS: [],
    C.PI_DEPENDENCIES: [],
    C.PI_RECOMMENDATIONS: ["XEP-0045"],
    C.PI_MAIN: "Identity",
    C.PI_HANDLER: "no",
    C.PI_DESCRIPTION: _("""Identity manager"""),
}

Callback = namedtuple("Callback", ("origin", "get", "set", "priority"))


class Identity:

    def __init__(self, host):
        log.info(_("Plugin Identity initialization"))
        self.host = host
        self._m = host.plugins.get("XEP-0045")
        self.metadata = {
            "avatar": {
                "type": dict,
                # convert avatar path to avatar metadata (and check validity)
                "set_data_filter": self.avatarSetDataFilter,
                # update profile avatar, so all frontends are aware
                "set_post_treatment": self.avatarSetPostTreatment,
                "update_is_new_data": self.avatarUpdateIsNewData,
                "update_data_filter": self.avatarUpdateDataFilter,
                # we store the metadata in database, to restore it on next connection
                # (it is stored only for roster entities)
                "store": True,
            },
            "nicknames": {
                "type": list,
                # accumulate all nicknames from all callbacks in a list instead
                # of returning only the data from the first successful callback
                "get_all": True,
                # append nicknames from roster, resource, etc.
                "get_post_treatment": self.nicknamesGetPostTreatment,
                "update_is_new_data": self.nicknamesUpdateIsNewData,
                "store": True,
            },
        }
        host.trigger.add("roster_update", self._rosterUpdateTrigger)
        host.memory.setSignalOnUpdate("avatar")
        host.memory.setSignalOnUpdate("nicknames")
        host.bridge.addMethod(
            "identityGet",
            ".plugin",
            in_sign="sasbs",
            out_sign="s",
            method=self._getIdentity,
            async_=True,
        )
        host.bridge.addMethod(
            "identitiesGet",
            ".plugin",
            in_sign="asass",
            out_sign="s",
            method=self._getIdentities,
            async_=True,
        )
        host.bridge.addMethod(
            "identitiesBaseGet",
            ".plugin",
            in_sign="s",
            out_sign="s",
            method=self._getBaseIdentities,
            async_=True,
        )
        host.bridge.addMethod(
            "identitySet",
            ".plugin",
            in_sign="ss",
            out_sign="",
            method=self._setIdentity,
            async_=True,
        )
        host.bridge.addMethod(
            "avatarGet",
            ".plugin",
            in_sign="sbs",
            out_sign="s",
            method=self._getAvatar,
            async_=True,
        )
        host.bridge.addMethod(
            "avatarSet",
            ".plugin",
            in_sign="sss",
            out_sign="",
            method=self._setAvatar,
            async_=True,
        )

    async def profileConnecting(self, client):
        client._identity_update_lock = []
        # we restore known identities from database
        client._identity_storage = persistent.LazyPersistentBinaryDict(
            "identity", client.profile)

        stored_data = await client._identity_storage.all()

        self.host.memory.storage.getPrivates(
            namespace="identity", binary=True, profile=client.profile)

        to_delete = []

        for key, value in stored_data.items():
            entity_s, name = key.split('\n')
            if name not in self.metadata.keys():
                log.debug(f"removing {key} from storage: not an allowed metadata name")
                to_delete.append(key)
                continue
            entity = jid.JID(entity_s)

            if name == 'avatar':
                if value is not None:
                    try:
                        cache_uid = value['cache_uid']
                        if not cache_uid:
                            raise ValueError
                        filename = value['filename']
                        if not filename:
                            raise ValueError
                    except (ValueError, KeyError):
                        log.warning(
                            f"invalid data for {entity} avatar, it will be deleted: "
                            f"{value}")
                        to_delete.append(key)
                        continue
                    cache = self.host.common_cache.getMetadata(cache_uid)
                    if cache is None:
                        log.debug(
                            f"purging avatar for {entity}: it is not in cache anymore")
                        to_delete.append(key)
                        continue

            self.host.memory.updateEntityData(
                client, entity, name, value, silent=True
            )

        for key in to_delete:
            await client._identity_storage.adel(key)

    def _rosterUpdateTrigger(self, client, roster_item):
        old_item = client.roster.getItem(roster_item.jid)
        if old_item is None or old_item.name != roster_item.name:
            log.debug(
                f"roster nickname has been updated to {roster_item.name!r} for "
                f"{roster_item.jid}"
            )
            defer.ensureDeferred(
                self.update(
                    client,
                    IMPORT_NAME,
                    "nicknames",
                    [roster_item.name],
                    roster_item.jid
                )
            )
        return True

    def register(
            self,
            origin: str,
            metadata_name: str,
            cb_get: Union[Coroutine, defer.Deferred],
            cb_set: Union[Coroutine, defer.Deferred],
            priority: int=0):
        """Register callbacks to handle identity metadata

        @param origin: namespace of the plugin managing this metadata
        @param metadata_name: name of metadata can be:
            - avatar
            - nicknames
        @param cb_get: method to retrieve a metadata
            the method will get client and metadata names to retrieve as arguments.
        @param cb_set: method to set a metadata
            the method will get client, metadata name to set, and value as argument.
        @param priority: priority of this method for the given metadata.
            methods with bigger priorities will be called first
        """
        if not metadata_name in self.metadata.keys():
            raise ValueError(f"Invalid metadata_name: {metadata_name!r}")
        callback = Callback(origin=origin, get=cb_get, set=cb_set, priority=priority)
        cb_list = self.metadata[metadata_name].setdefault('callbacks', [])
        cb_list.append(callback)
        cb_list.sort(key=lambda c: c.priority, reverse=True)

    def getIdentityJid(self, client, peer_jid):
        """Return jid to use to set identity metadata

        if it's a jid of a room occupant, full jid will be used
        otherwise bare jid will be used
        if None, bare jid of profile will be used
        @return (jid.JID): jid to use for avatar
        """
        if peer_jid is None:
            return client.jid.userhostJID()
        if self._m is None:
            return peer_jid.userhostJID()
        else:
            return self._m.getBareOrFull(client, peer_jid)

    def checkType(self, metadata_name, value):
        """Check that type used for a metadata is the one declared in self.metadata"""
        value_type = self.metadata[metadata_name]["type"]
        if not isinstance(value, value_type):
            raise ValueError(
                f"{value} has wrong type: it is {type(value)} while {value_type} was "
                f"expected")

    async def get(
            self,
            client: SatXMPPEntity,
            metadata_name: str,
            entity: Optional[jid.JID],
            use_cache: bool=True,
            prefilled_values: Optional[Dict[str, Any]]=None
        ):
        """Retrieve identity metadata of an entity

        if metadata is already in cache, it is returned. Otherwise, registered callbacks
        will be tried in priority order (bigger to lower)
        @param metadata_name: name of the metadata
            must be one of self.metadata key
            the name will also be used as entity data name in host.memory
        @param entity: entity for which avatar is requested
            None to use profile's jid
        @param use_cache: if False, cache won't be checked
        @param prefilled_values: map of origin => value to use when `get_all` is set
        """
        entity = self.getIdentityJid(client, entity)
        try:
            metadata = self.metadata[metadata_name]
        except KeyError:
            raise ValueError(f"Invalid metadata name: {metadata_name!r}")
        get_all = metadata.get('get_all', False)
        if use_cache:
            try:
                data = self.host.memory.getEntityDatum(
                    client, entity, metadata_name)
            except (KeyError, exceptions.UnknownEntityError):
                pass
            else:
                return data

        try:
            callbacks = metadata['callbacks']
        except KeyError:
            log.warning(_("No callback registered for {metadata_name}")
                        .format(metadata_name=metadata_name))
            return [] if get_all else None

        if get_all:
            all_data = []
        elif prefilled_values is not None:
            raise exceptions.InternalError(
                "prefilled_values can only be used when `get_all` is set")

        for callback in callbacks:
            try:
                if prefilled_values is not None and callback.origin in prefilled_values:
                    data = prefilled_values[callback.origin]
                    log.debug(
                        f"using prefilled values {data!r} for {metadata_name} with "
                        f"{callback.origin}")
                else:
                    data = await defer.ensureDeferred(callback.get(client, entity))
            except exceptions.CancelError:
                continue
            except Exception as e:
                log.warning(
                    _("Error while trying to get {metadata_name} with {callback}: {e}")
                    .format(callback=callback.get, metadata_name=metadata_name, e=e))
            else:
                if data:
                    self.checkType(metadata_name, data)
                    if get_all:
                        all_data.extend(data)
                    else:
                        break
        else:
            data = None

        if get_all:
            data = all_data

        post_treatment = metadata.get("get_post_treatment")
        if post_treatment is not None:
            data = await utils.asDeferred(post_treatment, client, entity, data)

        self.host.memory.updateEntityData(
            client, entity, metadata_name, data)

        if metadata.get('store', False):
            key = f"{entity}\n{metadata_name}"
            await client._identity_storage.aset(key, data)

        return data

    async def set(self, client, metadata_name, data, entity=None):
        """Set identity metadata for an entity

        Registered callbacks will be tried in priority order (bigger to lower)
        @param metadata_name(str): name of the metadata
            must be one of self.metadata key
            the name will also be used to set entity data in host.memory
        @param data(object): value to set
        @param entity(jid.JID, None): entity for which avatar is requested
            None to use profile's jid
        """
        entity = self.getIdentityJid(client, entity)
        metadata = self.metadata[metadata_name]
        data_filter = metadata.get("set_data_filter")
        if data_filter is not None:
            data = await utils.asDeferred(data_filter, client, entity, data)
        self.checkType(metadata_name, data)

        try:
            callbacks = metadata['callbacks']
        except KeyError:
            log.warning(_("No callback registered for {metadata_name}")
                        .format(metadata_name=metadata_name))
            return exceptions.FeatureNotFound(f"Can't set {metadata_name} for {entity}")

        for callback in callbacks:
            try:
                await defer.ensureDeferred(callback.set(client, data, entity))
            except exceptions.CancelError:
                continue
            except Exception as e:
                log.warning(
                    _("Error while trying to set {metadata_name} with {callback}: {e}")
                    .format(callback=callback.set, metadata_name=metadata_name, e=e))
            else:
                break
        else:
            raise exceptions.FeatureNotFound(f"Can't set {metadata_name} for {entity}")

        post_treatment = metadata.get("set_post_treatment")
        if post_treatment is not None:
            await utils.asDeferred(post_treatment, client, entity, data)

    async def update(
            self,
            client: SatXMPPEntity,
            origin: str,
            metadata_name: str,
            data: Any,
            entity: Optional[jid.JID]
        ):
        """Update a metadata in cache

        This method may be called by plugins when an identity metadata is available.
        @param origin: namespace of the plugin which is source of the metadata
        """
        entity = self.getIdentityJid(client, entity)
        if (entity, metadata_name) in client._identity_update_lock:
            log.debug(f"update is locked for {entity}'s {metadata_name}")
            return
        metadata = self.metadata[metadata_name]

        try:
            cached_data = self.host.memory.getEntityDatum(
                client, entity, metadata_name)
        except (KeyError, exceptions.UnknownEntityError):
            # metadata is not cached, we do the update
            pass
        else:
            # metadata is cached, we check if the new value differs from the cached one
            try:
                update_is_new_data = metadata["update_is_new_data"]
            except KeyError:
                update_is_new_data = self.defaultUpdateIsNewData

            if data is None:
                if cached_data is None:
                    log.debug(
                        f"{metadata_name} for {entity} is already disabled, nothing to "
                        f"do")
                    return
            elif cached_data is None:
                pass
            elif not update_is_new_data(client, entity, cached_data, data):
                log.debug(
                    f"{metadata_name} for {entity} is already in cache, nothing to "
                    f"do")
                return

        # we can't use the cache, so we do the update

        log.debug(f"updating {metadata_name} for {entity}")

        if metadata.get('get_all', False):
            # get_all is set, meaning that we have to check all plugins
            # so we first delete current cache
            try:
                self.host.memory.delEntityDatum(client, entity, metadata_name)
            except (KeyError, exceptions.UnknownEntityError):
                pass
            # then fill it again by calling get, which will retrieve all values
            # we lock update to avoid infinite recursions (update can be called during
            # get callbacks)
            client._identity_update_lock.append((entity, metadata_name))
            await self.get(client, metadata_name, entity, prefilled_values={origin: data})
            client._identity_update_lock.remove((entity, metadata_name))
            return

        if data is not None:
            data_filter = metadata['update_data_filter']
            if data_filter is not None:
                data = await utils.asDeferred(data_filter, client, entity, data)
            self.checkType(metadata_name, data)

        self.host.memory.updateEntityData(client, entity, metadata_name, data)

        if metadata.get('store', False):
            key = f"{entity}\n{metadata_name}"
            await client._identity_storage.aset(key, data)

    def defaultUpdateIsNewData(self, client, entity, cached_data, new_data):
        return new_data != cached_data

    def _getAvatar(self, entity, use_cache, profile):
        client = self.host.getClient(profile)
        entity = jid.JID(entity) if entity else None
        d = defer.ensureDeferred(self.get(client, "avatar", entity, use_cache))
        d.addCallback(lambda data: data_format.serialise(data))
        return d

    def _setAvatar(self, file_path, entity, profile_key=C.PROF_KEY_NONE):
        client = self.host.getClient(profile_key)
        entity = jid.JID(entity) if entity else None
        return defer.ensureDeferred(
            self.set(client, "avatar", file_path, entity))

    async def avatarSetDataFilter(self, client, entity, file_path):
        """Convert avatar file path to dict data"""
        file_path = Path(file_path)
        if not file_path.is_file():
            raise ValueError(f"There is no file at {file_path} to use as avatar")
        avatar_data = {
            'path': file_path,
            'filename': file_path.name,
            'media_type': image.guess_type(file_path),
        }
        media_type = avatar_data['media_type']
        if media_type is None:
            raise ValueError(f"Can't identify type of image at {file_path}")
        if not media_type.startswith('image/'):
            raise ValueError(f"File at {file_path} doesn't appear to be an image")
        return avatar_data

    async def avatarSetPostTreatment(self, client, entity, avatar_data):
        """Update our own avatar"""
        await self.update(client, IMPORT_NAME, "avatar", avatar_data, entity)

    def avatarBuildMetadata(self, path, media_type=None, cache_uid=None):
        """Helper method to generate avatar metadata

        @param path(str, Path, None): path to avatar file
            avatar file must be in cache
            None if avatar is explicitely not set
        @param media_type(str, None): type of the avatar file (MIME type)
        @param cache_uid(str, None): UID of avatar in cache
        @return (dict, None): avatar metadata
            None if avatar is not set
        """
        if path is None:
            return None
        else:
            if cache_uid is None:
                raise ValueError("cache_uid must be set if path is set")
            path = Path(path)
            if media_type is None:
                media_type = image.guess_type(path)

            return {
                "path": path,
                "filename": path.name,
                "media_type": media_type,
                "cache_uid": cache_uid,
            }

    def avatarUpdateIsNewData(self, client, entity, cached_data, new_data):
        return new_data['path'] != cached_data['path']

    async def avatarUpdateDataFilter(self, client, entity, data):
        if not isinstance(data, dict):
            raise ValueError(f"Invalid data type ({type(data)}), a dict is expected")
        mandatory_keys = {'path', 'filename', 'cache_uid'}
        if not data.keys() >= mandatory_keys:
            raise ValueError(f"missing avatar data keys: {mandatory_keys - data.keys()}")
        return data

    async def nicknamesGetPostTreatment(self, client, entity, plugin_nicknames):
        """Prepend nicknames from core locations + set default nickname

        nicknames are checked from many locations, there is always at least
        one nickname. First nickname of the list can be used in priority.
        Nicknames are appended in this order:
            - roster, plugins set nicknames
            - if no nickname is found, user part of jid is then used, or bare jid
              if there is no user part.
        For MUC, room nick is always put first
        """
        # we first check roster
        nicknames = []
        if entity.resource:
            # getIdentityJid let the resource only if the entity is a MUC room
            # occupant jid
            nicknames.append(entity.resource)

        roster_item = client.roster.getItem(entity.userhostJID())
        if roster_item is not None and roster_item.name:
            # user set name has priority over entity set name
            nicknames.append(roster_item.name)

        nicknames.extend(plugin_nicknames)

        if not nicknames:
            if entity.user:
                nicknames.append(entity.user.capitalize())
            else:
                nicknames.append(entity.userhost())

        # we remove duplicates while preserving order with dict
        return list(dict.fromkeys(nicknames))

    def nicknamesUpdateIsNewData(self, client, entity, cached_data, new_nicknames):
        return not set(new_nicknames).issubset(cached_data)

    def _getIdentity(self, entity_s, metadata_filter, use_cache, profile):
        entity = jid.JID(entity_s)
        client = self.host.getClient(profile)
        d = defer.ensureDeferred(
            self.getIdentity(client, entity, metadata_filter, use_cache))
        d.addCallback(data_format.serialise)
        return d

    async def getIdentity(
        self, client, entity=None, metadata_filter=None, use_cache=True):
        """Retrieve identity of an entity

        @param entity(jid.JID, None): entity to check
        @param metadata_filter(list[str], None): if not None or empty, only return
            metadata in this filter
        @param use_cache(bool): if False, cache won't be checked
            should be True most of time, to avoid useless network requests
        @return (dict): identity data
        """
        id_data = {}

        if not metadata_filter:
            metadata_names = self.metadata.keys()
        else:
            metadata_names = metadata_filter

        for metadata_name in metadata_names:
            id_data[metadata_name] = await self.get(
                client, metadata_name, entity, use_cache)

        return id_data

    def _getIdentities(self, entities_s, metadata_filter, profile):
        entities = [jid.JID(e) for e in entities_s]
        client = self.host.getClient(profile)
        d = defer.ensureDeferred(self.getIdentities(client, entities, metadata_filter))
        d.addCallback(lambda d: data_format.serialise({str(j):i for j, i in d.items()}))
        return d

    async def getIdentities(
        self,
        client: SatXMPPEntity,
        entities: List[jid.JID],
        metadata_filter: Optional[List[str]] = None,
    ) -> dict:
        """Retrieve several identities at once

        @param entities: entities from which identities must be retrieved
        @param metadata_filter: same as for [getIdentity]
        @return: identities metadata where key is jid
            if an error happens while retrieve a jid entity, it won't be present in the
            result (and a warning will be logged)
        """
        identities = {}
        get_identity_list = []
        for entity_jid in entities:
            get_identity_list.append(
                defer.ensureDeferred(
                    self.getIdentity(
                        client,
                        entity=entity_jid,
                        metadata_filter=metadata_filter,
                    )
                )
            )
        identities_result = await defer.DeferredList(get_identity_list)
        for idx, (success, identity) in enumerate(identities_result):
            entity_jid = entities[idx]
            if not success:
                log.warning(f"Can't get identity for {entity_jid}")
            else:
                identities[entity_jid] = identity
        return identities

    def _getBaseIdentities(self, profile_key):
        client = self.host.getClient(profile_key)
        d = defer.ensureDeferred(self.getBaseIdentities(client))
        d.addCallback(lambda d: data_format.serialise({str(j):i for j, i in d.items()}))
        return d

    async def getBaseIdentities(
        self,
        client: SatXMPPEntity,
    ) -> dict:
        """Retrieve identities for entities in roster + own identity + invitations

        @param with_guests: if True, get affiliations of people invited by email

        """
        entities = client.roster.getJids() + [client.jid.userhostJID()]

        return await self.getIdentities(
            client,
            entities,
            ['avatar', 'nicknames']
        )

    def _setIdentity(self, id_data_s, profile):
        client = self.host.getClient(profile)
        id_data = data_format.deserialise(id_data_s)
        return defer.ensureDeferred(self.setIdentity(client, id_data))

    async def setIdentity(self, client, id_data):
        """Update profile's identity

        @param id_data(dict): data to update, key can be on of self.metadata keys
        """
        if not id_data.keys() <= self.metadata.keys():
            raise ValueError(
                f"Invalid metadata names: {id_data.keys() - self.metadata.keys()}")
        for metadata_name, data in id_data.items():
            try:
                await self.set(client, metadata_name, data)
            except Exception as e:
                log.warning(
                    _("Can't set metadata {metadata_name!r}: {reason}")
                    .format(metadata_name=metadata_name, reason=e))
