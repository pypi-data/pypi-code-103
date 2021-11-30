#!/usr/bin/env python3

# Libervia: an XMPP client
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

import sys
import os.path
import uuid
import hashlib
import copy
from pathlib import Path
from typing import Optional, List, Tuple, Dict
import sat
from sat.core.i18n import _, D_, languageSwitch
from sat.core import patches
patches.apply()
from twisted.application import service
from twisted.internet import defer
from twisted.words.protocols.jabber import jid
from twisted.internet import reactor
from wokkel.xmppim import RosterItem
from sat.core import xmpp
from sat.core import exceptions
from sat.core.log import getLogger

from sat.core.constants import Const as C
from sat.memory import memory
from sat.memory import cache
from sat.memory import encryption
from sat.tools import async_trigger as trigger
from sat.tools import utils
from sat.tools import image
from sat.tools.common import dynamic_import
from sat.tools.common import regex
from sat.tools.common import data_format
from sat.stdui import ui_contact_list, ui_profile_manager
import sat.plugins


try:
    from collections import OrderedDict  # only available from python 2.7
except ImportError:
    from ordereddict import OrderedDict

log = getLogger(__name__)

class SAT(service.Service):
    def _init(self):
        # we don't use __init__ to avoid doule initialisation with twistd
        # this _init is called in startService
        log.info(f"{C.APP_NAME} {self.full_version}")
        self._cb_map = {}  # map from callback_id to callbacks
        self._menus = (
            OrderedDict()
        )  # dynamic menus. key: callback_id, value: menu data (dictionnary)
        self._menus_paths = {}  # path to id. key: (menu_type, lower case tuple of path),
                                # value: menu id
        self.initialised = defer.Deferred()
        self.profiles = {}
        self.plugins = {}
        # map for short name to whole namespace,
        # extended by plugins with registerNamespace
        self.ns_map = {
            "x-data": xmpp.NS_X_DATA,
            "disco#info": xmpp.NS_DISCO_INFO,
        }

        self.memory = memory.Memory(self)

        # trigger are used to change SàT behaviour
        self.trigger = (
            trigger.TriggerManager()
        )

        bridge_name = (
            os.getenv("LIBERVIA_BRIDGE_NAME")
            or self.memory.getConfig("", "bridge", "dbus")
        )

        bridge_module = dynamic_import.bridge(bridge_name)
        if bridge_module is None:
            log.error("Can't find bridge module of name {}".format(bridge_name))
            sys.exit(1)
        log.info("using {} bridge".format(bridge_name))
        try:
            self.bridge = bridge_module.Bridge()
        except exceptions.BridgeInitError:
            log.error("Bridge can't be initialised, can't start SàT core")
            sys.exit(1)
        self.bridge.register_method("getReady", lambda: self.initialised)
        self.bridge.register_method("getVersion", lambda: self.full_version)
        self.bridge.register_method("getFeatures", self.getFeatures)
        self.bridge.register_method("profileNameGet", self.memory.getProfileName)
        self.bridge.register_method("profilesListGet", self.memory.getProfilesList)
        self.bridge.register_method("getEntityData", self.memory._getEntityData)
        self.bridge.register_method("getEntitiesData", self.memory._getEntitiesData)
        self.bridge.register_method("profileCreate", self.memory.createProfile)
        self.bridge.register_method("asyncDeleteProfile", self.memory.asyncDeleteProfile)
        self.bridge.register_method("profileStartSession", self.memory.startSession)
        self.bridge.register_method(
            "profileIsSessionStarted", self.memory._isSessionStarted
        )
        self.bridge.register_method("profileSetDefault", self.memory.profileSetDefault)
        self.bridge.register_method("connect", self._connect)
        self.bridge.register_method("disconnect", self.disconnect)
        self.bridge.register_method("contactGet", self._contactGet)
        self.bridge.register_method("getContacts", self.getContacts)
        self.bridge.register_method("getContactsFromGroup", self.getContactsFromGroup)
        self.bridge.register_method("getMainResource", self.memory._getMainResource)
        self.bridge.register_method(
            "getPresenceStatuses", self.memory._getPresenceStatuses
        )
        self.bridge.register_method("getWaitingSub", self.memory.getWaitingSub)
        self.bridge.register_method("messageSend", self._messageSend)
        self.bridge.register_method("messageEncryptionStart",
                                    self._messageEncryptionStart)
        self.bridge.register_method("messageEncryptionStop",
                                    self._messageEncryptionStop)
        self.bridge.register_method("messageEncryptionGet",
                                    self._messageEncryptionGet)
        self.bridge.register_method("encryptionNamespaceGet",
                                    self._encryptionNamespaceGet)
        self.bridge.register_method("encryptionPluginsGet", self._encryptionPluginsGet)
        self.bridge.register_method("encryptionTrustUIGet", self._encryptionTrustUIGet)
        self.bridge.register_method("getConfig", self._getConfig)
        self.bridge.register_method("setParam", self.setParam)
        self.bridge.register_method("getParamA", self.memory.getStringParamA)
        self.bridge.register_method("privateDataGet", self.memory._privateDataGet)
        self.bridge.register_method("privateDataSet", self.memory._privateDataSet)
        self.bridge.register_method("privateDataDelete", self.memory._privateDataDelete)
        self.bridge.register_method("asyncGetParamA", self.memory.asyncGetStringParamA)
        self.bridge.register_method(
            "asyncGetParamsValuesFromCategory",
            self.memory._getParamsValuesFromCategory,
        )
        self.bridge.register_method("getParamsUI", self.memory._getParamsUI)
        self.bridge.register_method(
            "getParamsCategories", self.memory.getParamsCategories
        )
        self.bridge.register_method("paramsRegisterApp", self.memory.paramsRegisterApp)
        self.bridge.register_method("historyGet", self.memory._historyGet)
        self.bridge.register_method("setPresence", self._setPresence)
        self.bridge.register_method("subscription", self.subscription)
        self.bridge.register_method("addContact", self._addContact)
        self.bridge.register_method("updateContact", self._updateContact)
        self.bridge.register_method("delContact", self._delContact)
        self.bridge.register_method("rosterResync", self._rosterResync)
        self.bridge.register_method("isConnected", self.isConnected)
        self.bridge.register_method("launchAction", self.launchCallback)
        self.bridge.register_method("actionsGet", self.actionsGet)
        self.bridge.register_method("progressGet", self._progressGet)
        self.bridge.register_method("progressGetAll", self._progressGetAll)
        self.bridge.register_method("menusGet", self.getMenus)
        self.bridge.register_method("menuHelpGet", self.getMenuHelp)
        self.bridge.register_method("menuLaunch", self._launchMenu)
        self.bridge.register_method("discoInfos", self.memory.disco._discoInfos)
        self.bridge.register_method("discoItems", self.memory.disco._discoItems)
        self.bridge.register_method("discoFindByFeatures", self._findByFeatures)
        self.bridge.register_method("saveParamsTemplate", self.memory.save_xml)
        self.bridge.register_method("loadParamsTemplate", self.memory.load_xml)
        self.bridge.register_method("sessionInfosGet", self.getSessionInfos)
        self.bridge.register_method("devicesInfosGet", self._getDevicesInfos)
        self.bridge.register_method("namespacesGet", self.getNamespaces)
        self.bridge.register_method("imageCheck", self._imageCheck)
        self.bridge.register_method("imageResize", self._imageResize)
        self.bridge.register_method("imageGeneratePreview", self._imageGeneratePreview)
        self.bridge.register_method("imageConvert", self._imageConvert)

        self.memory.initialized.addCallback(lambda __: defer.ensureDeferred(self._postMemoryInit()))

    @property
    def version(self):
        """Return the short version of SàT"""
        return C.APP_VERSION

    @property
    def full_version(self):
        """Return the full version of SàT

        In developement mode, release name and extra data are returned too
        """
        version = self.version
        if version[-1] == "D":
            # we are in debug version, we add extra data
            try:
                return self._version_cache
            except AttributeError:
                self._version_cache = "{} « {} » ({})".format(
                    version, C.APP_RELEASE_NAME, utils.getRepositoryData(sat)
                )
                return self._version_cache
        else:
            return version

    @property
    def bridge_name(self):
        return os.path.splitext(os.path.basename(self.bridge.__file__))[0]

    async def _postMemoryInit(self):
        """Method called after memory initialization is done"""
        self.common_cache = cache.Cache(self, None)
        log.info(_("Memory initialised"))
        try:
            self._import_plugins()
            ui_contact_list.ContactList(self)
            ui_profile_manager.ProfileManager(self)
        except Exception as e:
            log.error(f"Could not initialize backend: {e}")
            sys.exit(1)
        self._addBaseMenus()

        self.initialised.callback(None)
        log.info(_("Backend is ready"))

        # profile autoconnection must be done after self.initialised is called because
        # startSession waits for it.
        autoconnect_dict = await self.memory.storage.getIndParamValues(
            category='Connection', name='autoconnect_backend',
        )
        profiles_autoconnect = [p for p, v in autoconnect_dict.items() if C.bool(v)]
        if not self.trigger.point("profilesAutoconnect", profiles_autoconnect):
            return
        if profiles_autoconnect:
            log.info(D_(
                "Following profiles will be connected automatically: {profiles}"
                ).format(profiles= ', '.join(profiles_autoconnect)))
        connect_d_list = []
        for profile in profiles_autoconnect:
            connect_d_list.append(defer.ensureDeferred(self.connect(profile)))

        if connect_d_list:
            results = await defer.DeferredList(connect_d_list)
            for idx, (success, result) in enumerate(results):
                if not success:
                    profile = profiles_autoconnect[0]
                    log.warning(
                        _("Can't autoconnect profile {profile}: {reason}").format(
                            profile = profile,
                            reason = result)
                    )

    def _addBaseMenus(self):
        """Add base menus"""
        encryption.EncryptionHandler._importMenus(self)

    def _unimport_plugin(self, plugin_path):
        """remove a plugin from sys.modules if it is there"""
        try:
            del sys.modules[plugin_path]
        except KeyError:
            pass

    def _import_plugins(self):
        """Import all plugins found in plugins directory"""
        # FIXME: module imported but cancelled should be deleted
        # TODO: make this more generic and reusable in tools.common
        # FIXME: should use imp
        # TODO: do not import all plugins if no needed: component plugins are not needed
        #       if we just use a client, and plugin blacklisting should be possible in
        #       sat.conf
        plugins_path = Path(sat.plugins.__file__).parent
        plugins_to_import = {}  # plugins we still have to import
        for plug_path in plugins_path.glob("plugin_*"):
            if plug_path.is_dir():
                init_path = plug_path / f"__init__.{C.PLUGIN_EXT}"
                if not init_path.exists():
                    log.warning(
                        f"{plug_path} doesn't appear to be a package, can't load it")
                    continue
                plug_name = plug_path.name
            elif plug_path.is_file():
                if plug_path.suffix != f".{C.PLUGIN_EXT}":
                    continue
                plug_name = plug_path.stem
            else:
                log.warning(
                    f"{plug_path} is not a file or a dir, ignoring it")
                continue
            if not plug_name.isidentifier():
                log.warning(
                    f"{plug_name!r} is not a valid name for a plugin, ignoring it")
                continue
            plugin_path = f"sat.plugins.{plug_name}"
            try:
                __import__(plugin_path)
            except exceptions.MissingModule as e:
                self._unimport_plugin(plugin_path)
                log.warning(
                    "Can't import plugin [{path}] because of an unavailale third party "
                    "module:\n{msg}".format(
                        path=plugin_path, msg=e
                    )
                )
                continue
            except exceptions.CancelError as e:
                log.info(
                    "Plugin [{path}] cancelled its own import: {msg}".format(
                        path=plugin_path, msg=e
                    )
                )
                self._unimport_plugin(plugin_path)
                continue
            except Exception:
                import traceback

                log.error(
                    _("Can't import plugin [{path}]:\n{error}").format(
                        path=plugin_path, error=traceback.format_exc()
                    )
                )
                self._unimport_plugin(plugin_path)
                continue
            mod = sys.modules[plugin_path]
            plugin_info = mod.PLUGIN_INFO
            import_name = plugin_info["import_name"]

            plugin_modes = plugin_info["modes"] = set(
                plugin_info.setdefault("modes", C.PLUG_MODE_DEFAULT)
            )
            if not plugin_modes.intersection(C.PLUG_MODE_BOTH):
                log.error(
                    f"Can't import plugin at {plugin_path}, invalid {C.PI_MODES!r} "
                    f"value: {plugin_modes!r}"
                )
                continue

            # if the plugin is an entry point, it must work in component mode
            if plugin_info["type"] == C.PLUG_TYPE_ENTRY_POINT:
                # if plugin is an entrypoint, we cache it
                if C.PLUG_MODE_COMPONENT not in plugin_modes:
                    log.error(
                        _(
                            "{type} type must be used with {mode} mode, ignoring plugin"
                        ).format(type=C.PLUG_TYPE_ENTRY_POINT, mode=C.PLUG_MODE_COMPONENT)
                    )
                    self._unimport_plugin(plugin_path)
                    continue

            if import_name in plugins_to_import:
                log.error(
                    _(
                        "Name conflict for import name [{import_name}], can't import "
                        "plugin [{name}]"
                    ).format(**plugin_info)
                )
                continue
            plugins_to_import[import_name] = (plugin_path, mod, plugin_info)
        while True:
            try:
                self._import_plugins_from_dict(plugins_to_import)
            except ImportError:
                pass
            if not plugins_to_import:
                break

    def _import_plugins_from_dict(
        self, plugins_to_import, import_name=None, optional=False
    ):
        """Recursively import and their dependencies in the right order

        @param plugins_to_import(dict): key=import_name and values=(plugin_path, module,
                                        plugin_info)
        @param import_name(unicode, None): name of the plugin to import as found in
                                           PLUGIN_INFO['import_name']
        @param optional(bool): if False and plugin is not found, an ImportError exception
                               is raised
        """
        if import_name in self.plugins:
            log.debug("Plugin {} already imported, passing".format(import_name))
            return
        if not import_name:
            import_name, (plugin_path, mod, plugin_info) = plugins_to_import.popitem()
        else:
            if not import_name in plugins_to_import:
                if optional:
                    log.warning(
                        _("Recommended plugin not found: {}").format(import_name)
                    )
                    return
                msg = "Dependency not found: {}".format(import_name)
                log.error(msg)
                raise ImportError(msg)
            plugin_path, mod, plugin_info = plugins_to_import.pop(import_name)
        dependencies = plugin_info.setdefault("dependencies", [])
        recommendations = plugin_info.setdefault("recommendations", [])
        for to_import in dependencies + recommendations:
            if to_import not in self.plugins:
                log.debug(
                    "Recursively import dependency of [%s]: [%s]"
                    % (import_name, to_import)
                )
                try:
                    self._import_plugins_from_dict(
                        plugins_to_import, to_import, to_import not in dependencies
                    )
                except ImportError as e:
                    log.warning(
                        _("Can't import plugin {name}: {error}").format(
                            name=plugin_info["name"], error=e
                        )
                    )
                    if optional:
                        return
                    raise e
        log.info("importing plugin: {}".format(plugin_info["name"]))
        # we instanciate the plugin here
        try:
            self.plugins[import_name] = getattr(mod, plugin_info["main"])(self)
        except Exception as e:
            log.warning(
                'Error while loading plugin "{name}", ignoring it: {error}'.format(
                    name=plugin_info["name"], error=e
                )
            )
            if optional:
                return
            raise ImportError("Error during initiation")
        if C.bool(plugin_info.get(C.PI_HANDLER, C.BOOL_FALSE)):
            self.plugins[import_name].is_handler = True
        else:
            self.plugins[import_name].is_handler = False
        # we keep metadata as a Class attribute
        self.plugins[import_name]._info = plugin_info
        # TODO: test xmppclient presence and register handler parent

    def pluginsUnload(self):
        """Call unload method on every loaded plugin, if exists

        @return (D): A deferred which return None when all method have been called
        """
        # TODO: in the futur, it should be possible to hot unload a plugin
        #       pluging depending on the unloaded one should be unloaded too
        #       for now, just a basic call on plugin.unload is done
        defers_list = []
        for plugin in self.plugins.values():
            try:
                unload = plugin.unload
            except AttributeError:
                continue
            else:
                defers_list.append(defer.maybeDeferred(unload))
        return defers_list

    def _connect(self, profile_key, password="", options=None):
        profile = self.memory.getProfileName(profile_key)
        return defer.ensureDeferred(self.connect(profile, password, options))

    async def connect(
        self, profile, password="", options=None, max_retries=C.XMPP_MAX_RETRIES):
        """Connect a profile (i.e. connect client.component to XMPP server)

        Retrieve the individual parameters, authenticate the profile
        and initiate the connection to the associated XMPP server.
        @param profile: %(doc_profile)s
        @param password (string): the SàT profile password
        @param options (dict): connection options. Key can be:
            -
        @param max_retries (int): max number of connection retries
        @return (D(bool)):
            - True if the XMPP connection was already established
            - False if the XMPP connection has been initiated (it may still fail)
        @raise exceptions.PasswordError: Profile password is wrong
        """
        if options is None:
            options = {}

        await self.memory.startSession(password, profile)

        if self.isConnected(profile):
            log.info(_("already connected !"))
            return True

        if self.memory.isComponent(profile):
            await xmpp.SatXMPPComponent.startConnection(self, profile, max_retries)
        else:
            await xmpp.SatXMPPClient.startConnection(self, profile, max_retries)

        return False

    def disconnect(self, profile_key):
        """disconnect from jabber server"""
        # FIXME: client should not be deleted if only disconnected
        #        it shoud be deleted only when session is finished
        if not self.isConnected(profile_key):
            # isConnected is checked here and not on client
            # because client is deleted when session is ended
            log.info(_("not connected !"))
            return defer.succeed(None)
        client = self.getClient(profile_key)
        return client.entityDisconnect()

    def getFeatures(self, profile_key=C.PROF_KEY_NONE):
        """Get available features

        Return list of activated plugins and plugin specific data
        @param profile_key: %(doc_profile_key)s
            C.PROF_KEY_NONE can be used to have general plugins data (i.e. not profile
            dependent)
        @return (dict)[Deferred]: features data where:
            - key is plugin import name, present only for activated plugins
            - value is a an other dict, when meaning is specific to each plugin.
                this dict is return by plugin's getFeature method.
                If this method doesn't exists, an empty dict is returned.
        """
        try:
            # FIXME: there is no method yet to check profile session
            #        as soon as one is implemented, it should be used here
            self.getClient(profile_key)
        except KeyError:
            log.warning("Requesting features for a profile outside a session")
            profile_key = C.PROF_KEY_NONE
        except exceptions.ProfileNotSetError:
            pass

        features = []
        for import_name, plugin in self.plugins.items():
            try:
                features_d = defer.maybeDeferred(plugin.getFeatures, profile_key)
            except AttributeError:
                features_d = defer.succeed({})
            features.append(features_d)

        d_list = defer.DeferredList(features)

        def buildFeatures(result, import_names):
            assert len(result) == len(import_names)
            ret = {}
            for name, (success, data) in zip(import_names, result):
                if success:
                    ret[name] = data
                else:
                    log.warning(
                        "Error while getting features for {name}: {failure}".format(
                            name=name, failure=data
                        )
                    )
                    ret[name] = {}
            return ret

        d_list.addCallback(buildFeatures, list(self.plugins.keys()))
        return d_list

    def _contactGet(self, entity_jid_s, profile_key):
        client = self.getClient(profile_key)
        entity_jid = jid.JID(entity_jid_s)
        return defer.ensureDeferred(self.getContact(client, entity_jid))

    async def getContact(self, client, entity_jid):
        # we want to be sure that roster has been received
        await client.roster.got_roster
        item = client.roster.getItem(entity_jid)
        if item is None:
            raise exceptions.NotFound(f"{entity_jid} is not in roster!")
        return (client.roster.getAttributes(item), list(item.groups))

    def getContacts(self, profile_key):
        client = self.getClient(profile_key)

        def got_roster(__):
            ret = []
            for item in client.roster.getItems():  # we get all items for client's roster
                # and convert them to expected format
                attr = client.roster.getAttributes(item)
                # we use full() and not userhost() because jid with resources are allowed
                # in roster, even if it's not common.
                ret.append([item.entity.full(), attr, item.groups])
            return ret

        return client.roster.got_roster.addCallback(got_roster)

    def getContactsFromGroup(self, group, profile_key):
        client = self.getClient(profile_key)
        return [jid_.full() for jid_ in client.roster.getJidsFromGroup(group)]

    def purgeEntity(self, profile):
        """Remove reference to a profile client/component and purge cache

        the garbage collector can then free the memory
        """
        try:
            del self.profiles[profile]
        except KeyError:
            log.error(_("Trying to remove reference to a client not referenced"))
        else:
            self.memory.purgeProfileSession(profile)

    def startService(self):
        self._init()
        log.info("Salut à toi ô mon frère !")

    def stopService(self):
        log.info("Salut aussi à Rantanplan")
        return self.pluginsUnload()

    def run(self):
        log.debug(_("running app"))
        reactor.run()

    def stop(self):
        log.debug(_("stopping app"))
        reactor.stop()

    ## Misc methods ##

    def getJidNStream(self, profile_key):
        """Convenient method to get jid and stream from profile key
        @return: tuple (jid, xmlstream) from profile, can be None"""
        # TODO: deprecate this method (getClient is enough)
        profile = self.memory.getProfileName(profile_key)
        if not profile or not self.profiles[profile].isConnected():
            return (None, None)
        return (self.profiles[profile].jid, self.profiles[profile].xmlstream)

    def getClient(self, profile_key):
        """Convenient method to get client from profile key

        @return: client or None if it doesn't exist
        @raise exceptions.ProfileKeyUnknown: the profile or profile key doesn't exist
        @raise exceptions.NotFound: client is not available
            This happen if profile has not been used yet
        """
        profile = self.memory.getProfileName(profile_key)
        if not profile:
            raise exceptions.ProfileKeyUnknown
        try:
            return self.profiles[profile]
        except KeyError:
            raise exceptions.NotFound(profile_key)

    def getClients(self, profile_key):
        """Convenient method to get list of clients from profile key

        Manage list through profile_key like C.PROF_KEY_ALL
        @param profile_key: %(doc_profile_key)s
        @return: list of clients
        """
        if not profile_key:
            raise exceptions.DataError(_("profile_key must not be empty"))
        try:
            profile = self.memory.getProfileName(profile_key, True)
        except exceptions.ProfileUnknownError:
            return []
        if profile == C.PROF_KEY_ALL:
            return list(self.profiles.values())
        elif profile[0] == "@":  #  only profile keys can start with "@"
            raise exceptions.ProfileKeyUnknown
        return [self.profiles[profile]]

    def _getConfig(self, section, name):
        """Get the main configuration option

        @param section: section of the config file (None or '' for DEFAULT)
        @param name: name of the option
        @return: unicode representation of the option
        """
        return str(self.memory.getConfig(section, name, ""))

    def logErrback(self, failure_, msg=_("Unexpected error: {failure_}")):
        """Generic errback logging

        @param msg(unicode): error message ("failure_" key will be use for format)
        can be used as last errback to show unexpected error
        """
        log.error(msg.format(failure_=failure_))
        return failure_

    #  namespaces

    def registerNamespace(self, short_name, namespace):
        """associate a namespace to a short name"""
        if short_name in self.ns_map:
            raise exceptions.ConflictError("this short name is already used")
        log.debug(f"registering namespace {short_name} => {namespace}")
        self.ns_map[short_name] = namespace

    def getNamespaces(self):
        return self.ns_map

    def getNamespace(self, short_name):
        try:
            return self.ns_map[short_name]
        except KeyError:
            raise exceptions.NotFound("namespace {short_name} is not registered"
                                      .format(short_name=short_name))

    def getSessionInfos(self, profile_key):
        """compile interesting data on current profile session"""
        client = self.getClient(profile_key)
        data = {
            "jid": client.jid.full(),
            "started": str(int(client.started))
            }
        return defer.succeed(data)

    def _getDevicesInfos(self, bare_jid, profile_key):
        client = self.getClient(profile_key)
        if not bare_jid:
            bare_jid = None
        d = defer.ensureDeferred(self.getDevicesInfos(client, bare_jid))
        d.addCallback(lambda data: data_format.serialise(data))
        return d

    async def getDevicesInfos(self, client, bare_jid=None):
        """compile data on an entity devices

        @param bare_jid(jid.JID, None): bare jid of entity to check
            None to use client own jid
        @return (list[dict]): list of data, one item per resource.
            Following keys can be set:
                - resource(str): resource name
        """
        own_jid = client.jid.userhostJID()
        if bare_jid is None:
            bare_jid = own_jid
        else:
            bare_jid = jid.JID(bare_jid)
        resources = self.memory.getAllResources(client, bare_jid)
        if bare_jid == own_jid:
            # our own jid is not stored in memory's cache
            resources.add(client.jid.resource)
        ret_data = []
        for resource in resources:
            res_jid = copy.copy(bare_jid)
            res_jid.resource = resource
            cache_data = self.memory.getEntityData(client, res_jid)
            res_data = {
                "resource": resource,
            }
            try:
                presence = cache_data['presence']
            except KeyError:
                pass
            else:
                res_data['presence'] = {
                    "show": presence.show,
                    "priority": presence.priority,
                    "statuses": presence.statuses,
                }

            disco = await self.getDiscoInfos(client, res_jid)

            for (category, type_), name in disco.identities.items():
                identities = res_data.setdefault('identities', [])
                identities.append({
                    "name": name,
                    "category": category,
                    "type": type_,
                })

            ret_data.append(res_data)

        return ret_data

    # images

    def _imageCheck(self, path):
        report = image.check(self, path)
        return data_format.serialise(report)

    def _imageResize(self, path, width, height):
        d = image.resize(path, (width, height))
        d.addCallback(lambda new_image_path: str(new_image_path))
        return d

    def _imageGeneratePreview(self, path, profile_key):
        client = self.getClient(profile_key)
        d = defer.ensureDeferred(self.imageGeneratePreview(client, Path(path)))
        d.addCallback(lambda preview_path: str(preview_path))
        return d

    async def imageGeneratePreview(self, client, path):
        """Helper method to generate in cache a preview of an image

        @param path(Path): path to the image
        @return (Path): path to the generated preview
        """
        report = image.check(self, path, max_size=(300, 300))

        if not report['too_large']:
            # in the unlikely case that image is already smaller than a preview
            preview_path = path
        else:
            # we use hash as id, to re-use potentially existing preview
            path_hash = hashlib.sha256(str(path).encode()).hexdigest()
            uid = f"{path.stem}_{path_hash}_preview"
            filename = f"{uid}{path.suffix.lower()}"
            metadata = client.cache.getMetadata(uid=uid)
            if metadata is not None:
                preview_path = metadata['path']
            else:
                with client.cache.cacheData(
                    source='HOST_PREVIEW',
                    uid=uid,
                    filename=filename) as cache_f:

                    preview_path = await image.resize(
                        path,
                        new_size=report['recommended_size'],
                        dest=cache_f
                    )

        return preview_path

    def _imageConvert(self, source, dest, extra, profile_key):
        client = self.getClient(profile_key) if profile_key else None
        source = Path(source)
        dest = None if not dest else Path(dest)
        extra = data_format.deserialise(extra)
        d = defer.ensureDeferred(self.imageConvert(client, source, dest, extra))
        d.addCallback(lambda dest_path: str(dest_path))
        return d

    async def imageConvert(self, client, source, dest=None, extra=None):
        """Helper method to convert an image from one format to an other

        @param client(SatClient, None): client to use for caching
            this parameter is only used if dest is None
            if client is None, common cache will be used insted of profile cache
        @param source(Path): path to the image to convert
        @param dest(None, Path, file): where to save the converted file
            - None: use a cache file (uid generated from hash of source)
                file will be converted to PNG
            - Path: path to the file to create/overwrite
            - file: a file object which must be opened for writing in binary mode
        @param extra(dict, None): conversion options
            see [image.convert] for details
        @return (Path): path to the converted image
        @raise ValueError: an issue happened with source of dest
        """
        if not source.is_file:
            raise ValueError(f"Source file {source} doesn't exist!")
        if dest is None:
            # we use hash as id, to re-use potentially existing conversion
            path_hash = hashlib.sha256(str(source).encode()).hexdigest()
            uid = f"{source.stem}_{path_hash}_convert_png"
            filename = f"{uid}.png"
            if client is None:
                cache = self.common_cache
            else:
                cache = client.cache
            metadata = cache.getMetadata(uid=uid)
            if metadata is not None:
                # there is already a conversion for this image in cache
                return metadata['path']
            else:
                with cache.cacheData(
                    source='HOST_IMAGE_CONVERT',
                    uid=uid,
                    filename=filename) as cache_f:

                    converted_path = await image.convert(
                        source,
                        dest=cache_f,
                        extra=extra
                    )
                return converted_path
        else:
            return await image.convert(source, dest, extra)


    # local dirs

    def getLocalPath(
        self,
        client,
        dir_name: str,
        *extra_path,
        **kwargs
    ) -> Path:
        """Retrieve path for local data

        if path doesn't exist, it will be created
        @param client(SatXMPPClient, None): client instance
            used when profile is set, can be None if profile is False
        @param dir_name(unicode): name of the main path directory
        @param component(bool): if True, path will be prefixed with C.COMPONENTS_DIR
        @param profile(bool): if True, path will be suffixed by profile name
        @param *extra_path: extra path element(s) to use
        @return: path
        """
        # FIXME: component and profile are parsed with **kwargs because of python 2
        #   limitations. Once moved to python 3, this can be fixed
        component = kwargs.pop("component", False)
        profile = kwargs.pop("profile", True)
        assert not kwargs

        path_elts = [self.memory.getConfig("", "local_dir")]
        if component:
            path_elts.append(C.COMPONENTS_DIR)
        path_elts.append(regex.pathEscape(dir_name))
        if extra_path:
            path_elts.extend([regex.pathEscape(p) for p in extra_path])
        if profile:
            regex.pathEscape(client.profile)
        local_path = Path(*path_elts)
        local_path.mkdir(0o700, parents=True, exist_ok=True)
        return local_path

    ## Client management ##

    def setParam(self, name, value, category, security_limit, profile_key):
        """set wanted paramater and notice observers"""
        self.memory.setParam(name, value, category, security_limit, profile_key)

    def isConnected(self, profile_key):
        """Return connection status of profile

        @param profile_key: key_word or profile name to determine profile name
        @return: True if connected
        """
        profile = self.memory.getProfileName(profile_key)
        if not profile:
            log.error(_("asking connection status for a non-existant profile"))
            raise exceptions.ProfileUnknownError(profile_key)
        if profile not in self.profiles:
            return False
        return self.profiles[profile].isConnected()

    ## Encryption ##

    def registerEncryptionPlugin(self, *args, **kwargs):
        return encryption.EncryptionHandler.registerPlugin(*args, **kwargs)

    def _messageEncryptionStart(self, to_jid_s, namespace, replace=False,
                                profile_key=C.PROF_KEY_NONE):
        client = self.getClient(profile_key)
        to_jid = jid.JID(to_jid_s)
        return defer.ensureDeferred(
            client.encryption.start(to_jid, namespace or None, replace))

    def _messageEncryptionStop(self, to_jid_s, profile_key=C.PROF_KEY_NONE):
        client = self.getClient(profile_key)
        to_jid = jid.JID(to_jid_s)
        return defer.ensureDeferred(
            client.encryption.stop(to_jid))

    def _messageEncryptionGet(self, to_jid_s, profile_key=C.PROF_KEY_NONE):
        client = self.getClient(profile_key)
        to_jid = jid.JID(to_jid_s)
        session_data = client.encryption.getSession(to_jid)
        return client.encryption.getBridgeData(session_data)

    def _encryptionNamespaceGet(self, name):
        return encryption.EncryptionHandler.getNSFromName(name)

    def _encryptionPluginsGet(self):
        plugins = encryption.EncryptionHandler.getPlugins()
        ret = []
        for p in plugins:
            ret.append({
                "name": p.name,
                "namespace": p.namespace,
                "priority": p.priority,
                "directed": p.directed,
                })
        return data_format.serialise(ret)

    def _encryptionTrustUIGet(self, to_jid_s, namespace, profile_key):
        client = self.getClient(profile_key)
        to_jid = jid.JID(to_jid_s)
        d = defer.ensureDeferred(
            client.encryption.getTrustUI(to_jid, namespace=namespace or None))
        d.addCallback(lambda xmlui: xmlui.toXml())
        return d

    ## XMPP methods ##

    def _messageSend(
            self, to_jid_s, message, subject=None, mess_type="auto", extra_s="",
            profile_key=C.PROF_KEY_NONE):
        client = self.getClient(profile_key)
        to_jid = jid.JID(to_jid_s)
        return client.sendMessage(
            to_jid,
            message,
            subject,
            mess_type,
            data_format.deserialise(extra_s)
        )

    def _setPresence(self, to="", show="", statuses=None, profile_key=C.PROF_KEY_NONE):
        return self.setPresence(jid.JID(to) if to else None, show, statuses, profile_key)

    def setPresence(self, to_jid=None, show="", statuses=None,
                    profile_key=C.PROF_KEY_NONE):
        """Send our presence information"""
        if statuses is None:
            statuses = {}
        profile = self.memory.getProfileName(profile_key)
        assert profile
        priority = int(
            self.memory.getParamA("Priority", "Connection", profile_key=profile)
        )
        self.profiles[profile].presence.available(to_jid, show, statuses, priority)
        # XXX: FIXME: temporary fix to work around openfire 3.7.0 bug (presence is not
        #             broadcasted to generating resource)
        if "" in statuses:
            statuses[C.PRESENCE_STATUSES_DEFAULT] = statuses.pop("")
        self.bridge.presenceUpdate(
            self.profiles[profile].jid.full(), show, int(priority), statuses, profile
        )

    def subscription(self, subs_type, raw_jid, profile_key):
        """Called to manage subscription
        @param subs_type: subsciption type (cf RFC 3921)
        @param raw_jid: unicode entity's jid
        @param profile_key: profile"""
        profile = self.memory.getProfileName(profile_key)
        assert profile
        to_jid = jid.JID(raw_jid)
        log.debug(
            _("subsciption request [%(subs_type)s] for %(jid)s")
            % {"subs_type": subs_type, "jid": to_jid.full()}
        )
        if subs_type == "subscribe":
            self.profiles[profile].presence.subscribe(to_jid)
        elif subs_type == "subscribed":
            self.profiles[profile].presence.subscribed(to_jid)
        elif subs_type == "unsubscribe":
            self.profiles[profile].presence.unsubscribe(to_jid)
        elif subs_type == "unsubscribed":
            self.profiles[profile].presence.unsubscribed(to_jid)

    def _addContact(self, to_jid_s, profile_key):
        return self.addContact(jid.JID(to_jid_s), profile_key)

    def addContact(self, to_jid, profile_key):
        """Add a contact in roster list"""
        profile = self.memory.getProfileName(profile_key)
        assert profile
        # presence is sufficient, as a roster push will be sent according to
        # RFC 6121 §3.1.2
        self.profiles[profile].presence.subscribe(to_jid)

    def _updateContact(self, to_jid_s, name, groups, profile_key):
        client = self.getClient(profile_key)
        return self.updateContact(client, jid.JID(to_jid_s), name, groups)

    def updateContact(self, client, to_jid, name, groups):
        """update a contact in roster list"""
        roster_item = RosterItem(to_jid)
        roster_item.name = name or u''
        roster_item.groups = set(groups)
        if not self.trigger.point("roster_update", client, roster_item):
            return
        return client.roster.setItem(roster_item)

    def _delContact(self, to_jid_s, profile_key):
        return self.delContact(jid.JID(to_jid_s), profile_key)

    def delContact(self, to_jid, profile_key):
        """Remove contact from roster list"""
        profile = self.memory.getProfileName(profile_key)
        assert profile
        self.profiles[profile].presence.unsubscribe(to_jid)  # is not asynchronous
        return self.profiles[profile].roster.removeItem(to_jid)

    def _rosterResync(self, profile_key):
        client = self.getClient(profile_key)
        return client.roster.resync()

    ## Discovery ##
    # discovery methods are shortcuts to self.memory.disco
    # the main difference with client.disco is that self.memory.disco manage cache

    def hasFeature(self, *args, **kwargs):
        return self.memory.disco.hasFeature(*args, **kwargs)

    def checkFeature(self, *args, **kwargs):
        return self.memory.disco.checkFeature(*args, **kwargs)

    def checkFeatures(self, *args, **kwargs):
        return self.memory.disco.checkFeatures(*args, **kwargs)

    def getDiscoInfos(self, *args, **kwargs):
        return self.memory.disco.getInfos(*args, **kwargs)

    def getDiscoItems(self, *args, **kwargs):
        return self.memory.disco.getItems(*args, **kwargs)

    def findServiceEntity(self, *args, **kwargs):
        return self.memory.disco.findServiceEntity(*args, **kwargs)

    def findServiceEntities(self, *args, **kwargs):
        return self.memory.disco.findServiceEntities(*args, **kwargs)

    def findFeaturesSet(self, *args, **kwargs):
        return self.memory.disco.findFeaturesSet(*args, **kwargs)

    def _findByFeatures(self, namespaces, identities, bare_jids, service, roster, own_jid,
                        local_device, profile_key):
        client = self.getClient(profile_key)
        return defer.ensureDeferred(self.findByFeatures(
            client, namespaces, identities, bare_jids, service, roster, own_jid,
            local_device))

    async def findByFeatures(
        self,
        client: xmpp.SatXMPPEntity,
        namespaces: List[str],
        identities: Optional[List[Tuple[str, str]]]=None,
        bare_jids: bool=False,
        service: bool=True,
        roster: bool=True,
        own_jid: bool=True,
        local_device: bool=False
    ) -> Tuple[
        Dict[jid.JID, Tuple[str, str, str]],
        Dict[jid.JID, Tuple[str, str, str]],
        Dict[jid.JID, Tuple[str, str, str]]
    ]:
        """Retrieve all services or contacts managing a set a features

        @param namespaces: features which must be handled
        @param identities: if not None or empty,
            only keep those identities
            tuple must be (category, type)
        @param bare_jids: retrieve only bare_jids if True
            if False, retrieve full jid of connected devices
        @param service: if True return service from our server
        @param roster: if True, return entities in roster
            full jid of all matching resources available will be returned
        @param own_jid: if True, return profile's jid resources
        @param local_device: if True, return profile's jid local resource
            (i.e. client.jid)
        @return: found entities in a tuple with:
            - service entities
            - own entities
            - roster entities
            Each element is a dict mapping from jid to a tuple with category, type and
            name of the entity
        """
        assert isinstance(namespaces, list)
        if not identities:
            identities = None
        if not namespaces and not identities:
            raise exceptions.DataError(
                "at least one namespace or one identity must be set"
            )
        found_service = {}
        found_own = {}
        found_roster = {}
        if service:
            services_jids = await self.findFeaturesSet(client, namespaces)
            services_jids = list(services_jids)  # we need a list to map results below
            services_infos  = await defer.DeferredList(
                [self.getDiscoInfos(client, service_jid) for service_jid in services_jids]
            )

            for idx, (success, infos) in enumerate(services_infos):
                service_jid = services_jids[idx]
                if not success:
                    log.warning(
                        _("Can't find features for service {service_jid}, ignoring")
                        .format(service_jid=service_jid.full()))
                    continue
                if (identities is not None
                    and not set(infos.identities.keys()).issuperset(identities)):
                    continue
                found_identities = [
                    (cat, type_, name or "")
                    for (cat, type_), name in infos.identities.items()
                ]
                found_service[service_jid.full()] = found_identities

        to_find = []
        if own_jid:
            to_find.append((found_own, [client.jid.userhostJID()]))
        if roster:
            to_find.append((found_roster, client.roster.getJids()))

        for found, jids in to_find:
            full_jids = []
            disco_defers = []

            for jid_ in jids:
                if jid_.resource:
                    if bare_jids:
                        continue
                    resources = [jid_.resource]
                else:
                    if bare_jids:
                        resources = [None]
                    else:
                        try:
                            resources = self.memory.getAvailableResources(client, jid_)
                        except exceptions.UnknownEntityError:
                            continue
                        if not resources and jid_ == client.jid.userhostJID() and own_jid:
                            # small hack to avoid missing our own resource when this
                            # method is called at the very beginning of the session
                            # and our presence has not been received yet
                            resources = [client.jid.resource]
                for resource in resources:
                    full_jid = jid.JID(tuple=(jid_.user, jid_.host, resource))
                    if full_jid == client.jid and not local_device:
                        continue
                    full_jids.append(full_jid)

                    disco_defers.append(self.getDiscoInfos(client, full_jid))

            d_list = defer.DeferredList(disco_defers)
            # XXX: 10 seconds may be too low for slow connections (e.g. mobiles)
            #      but for discovery, that's also the time the user will wait the first time
            #      before seing the page, if something goes wrong.
            d_list.addTimeout(10, reactor)
            infos_data = await d_list

            for idx, (success, infos) in enumerate(infos_data):
                full_jid = full_jids[idx]
                if not success:
                    log.warning(
                        _("Can't retrieve {full_jid} infos, ignoring")
                        .format(full_jid=full_jid.full()))
                    continue
                if infos.features.issuperset(namespaces):
                    if identities is not None and not set(
                        infos.identities.keys()
                    ).issuperset(identities):
                        continue
                    found_identities = [
                        (cat, type_, name or "")
                        for (cat, type_), name in infos.identities.items()
                    ]
                    found[full_jid.full()] = found_identities

        return (found_service, found_own, found_roster)

    ## Generic HMI ##

    def _killAction(self, keep_id, client):
        log.debug("Killing action {} for timeout".format(keep_id))
        client.actions[keep_id]

    def actionNew(
        self,
        action_data,
        security_limit=C.NO_SECURITY_LIMIT,
        keep_id=None,
        profile=C.PROF_KEY_NONE,
    ):
        """Shortcut to bridge.actionNew which generate and id and keep for retrieval

        @param action_data(dict): action data (see bridge documentation)
        @param security_limit: %(doc_security_limit)s
        @param keep_id(None, unicode): if not None, used to keep action for differed
            retrieval. Must be set to the callback_id.
            Action will be deleted after 30 min.
        @param profile: %(doc_profile)s
        """
        id_ = str(uuid.uuid4())
        if keep_id is not None:
            client = self.getClient(profile)
            action_timer = reactor.callLater(60 * 30, self._killAction, keep_id, client)
            client.actions[keep_id] = (action_data, id_, security_limit, action_timer)

        self.bridge.actionNew(action_data, id_, security_limit, profile)

    def actionsGet(self, profile):
        """Return current non answered actions

        @param profile: %(doc_profile)s
        """
        client = self.getClient(profile)
        return [action_tuple[:-1] for action_tuple in client.actions.values()]

    def registerProgressCb(
        self, progress_id, callback, metadata=None, profile=C.PROF_KEY_NONE
    ):
        """Register a callback called when progress is requested for id"""
        if metadata is None:
            metadata = {}
        client = self.getClient(profile)
        if progress_id in client._progress_cb:
            raise exceptions.ConflictError("Progress ID is not unique !")
        client._progress_cb[progress_id] = (callback, metadata)

    def removeProgressCb(self, progress_id, profile):
        """Remove a progress callback"""
        client = self.getClient(profile)
        try:
            del client._progress_cb[progress_id]
        except KeyError:
            log.error(_("Trying to remove an unknow progress callback"))

    def _progressGet(self, progress_id, profile):
        data = self.progressGet(progress_id, profile)
        return {k: str(v) for k, v in data.items()}

    def progressGet(self, progress_id, profile):
        """Return a dict with progress information

        @param progress_id(unicode): unique id of the progressing element
        @param profile: %(doc_profile)s
        @return (dict): data with the following keys:
            'position' (int): current possition
            'size' (int): end_position
            if id doesn't exists (may be a finished progression), and empty dict is
            returned
        """
        client = self.getClient(profile)
        try:
            data = client._progress_cb[progress_id][0](progress_id, profile)
        except KeyError:
            data = {}
        return data

    def _progressGetAll(self, profile_key):
        progress_all = self.progressGetAll(profile_key)
        for profile, progress_dict in progress_all.items():
            for progress_id, data in progress_dict.items():
                for key, value in data.items():
                    data[key] = str(value)
        return progress_all

    def progressGetAllMetadata(self, profile_key):
        """Return all progress metadata at once

        @param profile_key: %(doc_profile)s
            if C.PROF_KEY_ALL is used, all progress metadata from all profiles are
            returned
        @return (dict[dict[dict]]): a dict which map profile to progress_dict
            progress_dict map progress_id to progress_data
            progress_metadata is the same dict as sent by [progressStarted]
        """
        clients = self.getClients(profile_key)
        progress_all = {}
        for client in clients:
            profile = client.profile
            progress_dict = {}
            progress_all[profile] = progress_dict
            for (
                progress_id,
                (__, progress_metadata),
            ) in client._progress_cb.items():
                progress_dict[progress_id] = progress_metadata
        return progress_all

    def progressGetAll(self, profile_key):
        """Return all progress status at once

        @param profile_key: %(doc_profile)s
            if C.PROF_KEY_ALL is used, all progress status from all profiles are returned
        @return (dict[dict[dict]]): a dict which map profile to progress_dict
            progress_dict map progress_id to progress_data
            progress_data is the same dict as returned by [progressGet]
        """
        clients = self.getClients(profile_key)
        progress_all = {}
        for client in clients:
            profile = client.profile
            progress_dict = {}
            progress_all[profile] = progress_dict
            for progress_id, (progress_cb, __) in client._progress_cb.items():
                progress_dict[progress_id] = progress_cb(progress_id, profile)
        return progress_all

    def registerCallback(self, callback, *args, **kwargs):
        """Register a callback.

        @param callback(callable): method to call
        @param kwargs: can contain:
            with_data(bool): True if the callback use the optional data dict
            force_id(unicode): id to avoid generated id. Can lead to name conflict, avoid
                               if possible
            one_shot(bool): True to delete callback once it has been called
        @return: id of the registered callback
        """
        callback_id = kwargs.pop("force_id", None)
        if callback_id is None:
            callback_id = str(uuid.uuid4())
        else:
            if callback_id in self._cb_map:
                raise exceptions.ConflictError(_("id already registered"))
        self._cb_map[callback_id] = (callback, args, kwargs)

        if "one_shot" in kwargs:  # One Shot callback are removed after 30 min

            def purgeCallback():
                try:
                    self.removeCallback(callback_id)
                except KeyError:
                    pass

            reactor.callLater(1800, purgeCallback)

        return callback_id

    def removeCallback(self, callback_id):
        """ Remove a previously registered callback
        @param callback_id: id returned by [registerCallback] """
        log.debug("Removing callback [%s]" % callback_id)
        del self._cb_map[callback_id]

    def launchCallback(self, callback_id, data=None, profile_key=C.PROF_KEY_NONE):
        """Launch a specific callback

        @param callback_id: id of the action (callback) to launch
        @param data: optional data
        @profile_key: %(doc_profile_key)s
        @return: a deferred which fire a dict where key can be:
            - xmlui: a XMLUI need to be displayed
            - validated: if present, can be used to launch a callback, it can have the
                values
                - C.BOOL_TRUE
                - C.BOOL_FALSE
        """
        #  FIXME: security limit need to be checked here
        try:
            client = self.getClient(profile_key)
        except exceptions.NotFound:
            # client is not available yet
            profile = self.memory.getProfileName(profile_key)
            if not profile:
                raise exceptions.ProfileUnknownError(
                    _("trying to launch action with a non-existant profile")
                )
        else:
            profile = client.profile
            # we check if the action is kept, and remove it
            try:
                action_tuple = client.actions[callback_id]
            except KeyError:
                pass
            else:
                action_tuple[-1].cancel()  # the last item is the action timer
                del client.actions[callback_id]

        try:
            callback, args, kwargs = self._cb_map[callback_id]
        except KeyError:
            raise exceptions.DataError("Unknown callback id {}".format(callback_id))

        if kwargs.get("with_data", False):
            if data is None:
                raise exceptions.DataError("Required data for this callback is missing")
            args, kwargs = (
                list(args)[:],
                kwargs.copy(),
            )  # we don't want to modify the original (kw)args
            args.insert(0, data)
            kwargs["profile"] = profile
            del kwargs["with_data"]

        if kwargs.pop("one_shot", False):
            self.removeCallback(callback_id)

        return utils.asDeferred(callback, *args, **kwargs)

    # Menus management

    def _getMenuCanonicalPath(self, path):
        """give canonical form of path

        canonical form is a tuple of the path were every element is stripped and lowercase
        @param path(iterable[unicode]): untranslated path to menu
        @return (tuple[unicode]): canonical form of path
        """
        return tuple((p.lower().strip() for p in path))

    def importMenu(self, path, callback, security_limit=C.NO_SECURITY_LIMIT,
                   help_string="", type_=C.MENU_GLOBAL):
        r"""register a new menu for frontends

        @param path(iterable[unicode]): path to go to the menu
            (category/subcategory/.../item) (e.g.: ("File", "Open"))
            /!\ use D_() instead of _() for translations (e.g. (D_("File"), D_("Open")))
            untranslated/lower case path can be used to identity a menu, for this reason
            it must be unique independently of case.
        @param callback(callable): method to be called when menuitem is selected, callable
            or a callback id (string) as returned by [registerCallback]
        @param security_limit(int): %(doc_security_limit)s
            /!\ security_limit MUST be added to data in launchCallback if used #TODO
        @param help_string(unicode): string used to indicate what the menu do (can be
            show as a tooltip).
            /!\ use D_() instead of _() for translations
        @param type(unicode): one of:
            - C.MENU_GLOBAL: classical menu, can be shown in a menubar on top (e.g.
                something like File/Open)
            - C.MENU_ROOM: like a global menu, but only shown in multi-user chat
                menu_data must contain a "room_jid" data
            - C.MENU_SINGLE: like a global menu, but only shown in one2one chat
                menu_data must contain a "jid" data
            - C.MENU_JID_CONTEXT: contextual menu, used with any jid (e.g.: ad hoc
                commands, jid is already filled)
                menu_data must contain a "jid" data
            - C.MENU_ROSTER_JID_CONTEXT: like JID_CONTEXT, but restricted to jids in
                roster.
                menu_data must contain a "room_jid" data
            - C.MENU_ROSTER_GROUP_CONTEXT: contextual menu, used with group (e.g.: publish
                microblog, group is already filled)
                menu_data must contain a "group" data
        @return (unicode): menu_id (same as callback_id)
        """

        if callable(callback):
            callback_id = self.registerCallback(callback, with_data=True)
        elif isinstance(callback, str):
            # The callback is already registered
            callback_id = callback
            try:
                callback, args, kwargs = self._cb_map[callback_id]
            except KeyError:
                raise exceptions.DataError("Unknown callback id")
            kwargs["with_data"] = True  # we have to be sure that we use extra data
        else:
            raise exceptions.DataError("Unknown callback type")

        for menu_data in self._menus.values():
            if menu_data["path"] == path and menu_data["type"] == type_:
                raise exceptions.ConflictError(
                    _("A menu with the same path and type already exists")
                )

        path_canonical = self._getMenuCanonicalPath(path)
        menu_key = (type_, path_canonical)

        if menu_key in self._menus_paths:
            raise exceptions.ConflictError(
                "this menu path is already used: {path} ({menu_key})".format(
                    path=path_canonical, menu_key=menu_key
                )
            )

        menu_data = {
            "path": tuple(path),
            "path_canonical": path_canonical,
            "security_limit": security_limit,
            "help_string": help_string,
            "type": type_,
        }

        self._menus[callback_id] = menu_data
        self._menus_paths[menu_key] = callback_id

        return callback_id

    def getMenus(self, language="", security_limit=C.NO_SECURITY_LIMIT):
        """Return all menus registered

        @param language: language used for translation, or empty string for default
        @param security_limit: %(doc_security_limit)s
        @return: array of tuple with:
            - menu id (same as callback_id)
            - menu type
            - raw menu path (array of strings)
            - translated menu path
            - extra (dict(unicode, unicode)): extra data where key can be:
                - icon: name of the icon to use (TODO)
                - help_url: link to a page with more complete documentation (TODO)
        """
        ret = []
        for menu_id, menu_data in self._menus.items():
            type_ = menu_data["type"]
            path = menu_data["path"]
            menu_security_limit = menu_data["security_limit"]
            if security_limit != C.NO_SECURITY_LIMIT and (
                menu_security_limit == C.NO_SECURITY_LIMIT
                or menu_security_limit > security_limit
            ):
                continue
            languageSwitch(language)
            path_i18n = [_(elt) for elt in path]
            languageSwitch()
            extra = {}  # TODO: manage extra data like icon
            ret.append((menu_id, type_, path, path_i18n, extra))

        return ret

    def _launchMenu(self, menu_type, path, data=None, security_limit=C.NO_SECURITY_LIMIT,
                    profile_key=C.PROF_KEY_NONE):
        client = self.getClient(profile_key)
        return self.launchMenu(client, menu_type, path, data, security_limit)

    def launchMenu(self, client, menu_type, path, data=None,
        security_limit=C.NO_SECURITY_LIMIT):
        """launch action a menu action

        @param menu_type(unicode): type of menu to launch
        @param path(iterable[unicode]): canonical path of the menu
        @params data(dict): menu data
        @raise NotFound: this path is not known
        """
        # FIXME: manage security_limit here
        #        defaut security limit should be high instead of C.NO_SECURITY_LIMIT
        canonical_path = self._getMenuCanonicalPath(path)
        menu_key = (menu_type, canonical_path)
        try:
            callback_id = self._menus_paths[menu_key]
        except KeyError:
            raise exceptions.NotFound(
                "Can't find menu {path} ({menu_type})".format(
                    path=canonical_path, menu_type=menu_type
                )
            )
        return self.launchCallback(callback_id, data, client.profile)

    def getMenuHelp(self, menu_id, language=""):
        """return the help string of the menu

        @param menu_id: id of the menu (same as callback_id)
        @param language: language used for translation, or empty string for default
        @param return: translated help

        """
        try:
            menu_data = self._menus[menu_id]
        except KeyError:
            raise exceptions.DataError("Trying to access an unknown menu")
        languageSwitch(language)
        help_string = _(menu_data["help_string"])
        languageSwitch()
        return help_string
