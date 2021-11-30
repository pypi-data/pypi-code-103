#!/usr/bin/env python3

# SàT communication bridge
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

import asyncio
import dbus
import ast
from sat.core.i18n import _
from sat.tools import config
from sat.core.log import getLogger
from sat.core.exceptions import BridgeExceptionNoService, BridgeInitError
from dbus.mainloop.glib import DBusGMainLoop
from .bridge_frontend import BridgeException


DBusGMainLoop(set_as_default=True)
log = getLogger(__name__)


# Interface prefix
const_INT_PREFIX = config.getConfig(
    config.parseMainConf(),
    "",
    "bridge_dbus_int_prefix",
    "org.libervia.Libervia")
const_ERROR_PREFIX = const_INT_PREFIX + ".error"
const_OBJ_PATH = '/org/libervia/Libervia/bridge'
const_CORE_SUFFIX = ".core"
const_PLUGIN_SUFFIX = ".plugin"
const_TIMEOUT = 120


def dbus_to_bridge_exception(dbus_e):
    """Convert a DBusException to a BridgeException.

    @param dbus_e (DBusException)
    @return: BridgeException
    """
    full_name = dbus_e.get_dbus_name()
    if full_name.startswith(const_ERROR_PREFIX):
        name = dbus_e.get_dbus_name()[len(const_ERROR_PREFIX) + 1:]
    else:
        name = full_name
    # XXX: dbus_e.args doesn't contain the original DBusException args, but we
    # receive its serialized form in dbus_e.args[0]. From that we can rebuild
    # the original arguments list thanks to ast.literal_eval (secure eval).
    message = dbus_e.get_dbus_message()  # similar to dbus_e.args[0]
    try:
        message, condition = ast.literal_eval(message)
    except (SyntaxError, ValueError, TypeError):
        condition = ''
    return BridgeException(name, message, condition)


class Bridge:

    def bridgeConnect(self, callback, errback):
        try:
            self.sessions_bus = dbus.SessionBus()
            self.db_object = self.sessions_bus.get_object(const_INT_PREFIX,
                                                          const_OBJ_PATH)
            self.db_core_iface = dbus.Interface(self.db_object,
                                                dbus_interface=const_INT_PREFIX + const_CORE_SUFFIX)
            self.db_plugin_iface = dbus.Interface(self.db_object,
                                                  dbus_interface=const_INT_PREFIX + const_PLUGIN_SUFFIX)
        except dbus.exceptions.DBusException as e:
            if e._dbus_error_name in ('org.freedesktop.DBus.Error.ServiceUnknown',
                                      'org.freedesktop.DBus.Error.Spawn.ExecFailed'):
                errback(BridgeExceptionNoService())
            elif e._dbus_error_name == 'org.freedesktop.DBus.Error.NotSupported':
                log.error(_("D-Bus is not launched, please see README to see instructions on how to launch it"))
                errback(BridgeInitError)
            else:
                errback(e)
        else:
            callback()
        #props = self.db_core_iface.getProperties()

    def register_signal(self, functionName, handler, iface="core"):
        if iface == "core":
            self.db_core_iface.connect_to_signal(functionName, handler)
        elif iface == "plugin":
            self.db_plugin_iface.connect_to_signal(functionName, handler)
        else:
            log.error(_('Unknown interface'))

    def __getattribute__(self, name):
        """ usual __getattribute__ if the method exists, else try to find a plugin method """
        try:
            return object.__getattribute__(self, name)
        except AttributeError:
            # The attribute is not found, we try the plugin proxy to find the requested method

            def getPluginMethod(*args, **kwargs):
                # We first check if we have an async call. We detect this in two ways:
                #   - if we have the 'callback' and 'errback' keyword arguments
                #   - or if the last two arguments are callable

                async_ = False
                args = list(args)

                if kwargs:
                    if 'callback' in kwargs:
                        async_ = True
                        _callback = kwargs.pop('callback')
                        _errback = kwargs.pop('errback', lambda failure: log.error(str(failure)))
                    try:
                        args.append(kwargs.pop('profile'))
                    except KeyError:
                        try:
                            args.append(kwargs.pop('profile_key'))
                        except KeyError:
                            pass
                    # at this point, kwargs should be empty
                    if kwargs:
                        log.warning("unexpected keyword arguments, they will be ignored: {}".format(kwargs))
                elif len(args) >= 2 and callable(args[-1]) and callable(args[-2]):
                    async_ = True
                    _errback = args.pop()
                    _callback = args.pop()

                method = getattr(self.db_plugin_iface, name)

                if async_:
                    kwargs['timeout'] = const_TIMEOUT
                    kwargs['reply_handler'] = _callback
                    kwargs['error_handler'] = lambda err: _errback(dbus_to_bridge_exception(err))

                try:
                    return method(*args, **kwargs)
                except ValueError as e:
                    if e.args[0].startswith("Unable to guess signature"):
                        # XXX: if frontend is started too soon after backend, the
                        #   inspection misses methods (notably plugin dynamically added
                        #   methods). The following hack works around that by redoing the
                        #   cache of introspected methods signatures.
                        log.debug("using hack to work around inspection issue")
                        proxy = self.db_plugin_iface.proxy_object
                        IN_PROGRESS = proxy.INTROSPECT_STATE_INTROSPECT_IN_PROGRESS
                        proxy._introspect_state = IN_PROGRESS
                        proxy._Introspect()
                        return self.db_plugin_iface.get_dbus_method(name)(*args, **kwargs)
                    raise e

            return getPluginMethod

    def actionsGet(self, profile_key="@DEFAULT@", callback=None, errback=None):
        if callback is None:
            error_handler = None
        else:
            if errback is None:
                errback = log.error
            error_handler = lambda err:errback(dbus_to_bridge_exception(err))
        kwargs={}
        if callback is not None:
            kwargs['timeout'] = const_TIMEOUT
            kwargs['reply_handler'] = callback
            kwargs['error_handler'] = error_handler
        return self.db_core_iface.actionsGet(profile_key, **kwargs)

    def addContact(self, entity_jid, profile_key="@DEFAULT@", callback=None, errback=None):
        if callback is None:
            error_handler = None
        else:
            if errback is None:
                errback = log.error
            error_handler = lambda err:errback(dbus_to_bridge_exception(err))
        kwargs={}
        if callback is not None:
            kwargs['timeout'] = const_TIMEOUT
            kwargs['reply_handler'] = callback
            kwargs['error_handler'] = error_handler
        return self.db_core_iface.addContact(entity_jid, profile_key, **kwargs)

    def asyncDeleteProfile(self, profile, callback=None, errback=None):
        if callback is None:
            error_handler = None
        else:
            if errback is None:
                errback = log.error
            error_handler = lambda err:errback(dbus_to_bridge_exception(err))
        return self.db_core_iface.asyncDeleteProfile(profile, timeout=const_TIMEOUT, reply_handler=callback, error_handler=error_handler)

    def asyncGetParamA(self, name, category, attribute="value", security_limit=-1, profile_key="@DEFAULT@", callback=None, errback=None):
        if callback is None:
            error_handler = None
        else:
            if errback is None:
                errback = log.error
            error_handler = lambda err:errback(dbus_to_bridge_exception(err))
        return str(self.db_core_iface.asyncGetParamA(name, category, attribute, security_limit, profile_key, timeout=const_TIMEOUT, reply_handler=callback, error_handler=error_handler))

    def asyncGetParamsValuesFromCategory(self, category, security_limit=-1, app="", extra="", profile_key="@DEFAULT@", callback=None, errback=None):
        if callback is None:
            error_handler = None
        else:
            if errback is None:
                errback = log.error
            error_handler = lambda err:errback(dbus_to_bridge_exception(err))
        return self.db_core_iface.asyncGetParamsValuesFromCategory(category, security_limit, app, extra, profile_key, timeout=const_TIMEOUT, reply_handler=callback, error_handler=error_handler)

    def connect(self, profile_key="@DEFAULT@", password='', options={}, callback=None, errback=None):
        if callback is None:
            error_handler = None
        else:
            if errback is None:
                errback = log.error
            error_handler = lambda err:errback(dbus_to_bridge_exception(err))
        return self.db_core_iface.connect(profile_key, password, options, timeout=const_TIMEOUT, reply_handler=callback, error_handler=error_handler)

    def contactGet(self, arg_0, profile_key="@DEFAULT@", callback=None, errback=None):
        if callback is None:
            error_handler = None
        else:
            if errback is None:
                errback = log.error
            error_handler = lambda err:errback(dbus_to_bridge_exception(err))
        return self.db_core_iface.contactGet(arg_0, profile_key, timeout=const_TIMEOUT, reply_handler=callback, error_handler=error_handler)

    def delContact(self, entity_jid, profile_key="@DEFAULT@", callback=None, errback=None):
        if callback is None:
            error_handler = None
        else:
            if errback is None:
                errback = log.error
            error_handler = lambda err:errback(dbus_to_bridge_exception(err))
        return self.db_core_iface.delContact(entity_jid, profile_key, timeout=const_TIMEOUT, reply_handler=callback, error_handler=error_handler)

    def devicesInfosGet(self, bare_jid, profile_key, callback=None, errback=None):
        if callback is None:
            error_handler = None
        else:
            if errback is None:
                errback = log.error
            error_handler = lambda err:errback(dbus_to_bridge_exception(err))
        return str(self.db_core_iface.devicesInfosGet(bare_jid, profile_key, timeout=const_TIMEOUT, reply_handler=callback, error_handler=error_handler))

    def discoFindByFeatures(self, namespaces, identities, bare_jid=False, service=True, roster=True, own_jid=True, local_device=False, profile_key="@DEFAULT@", callback=None, errback=None):
        if callback is None:
            error_handler = None
        else:
            if errback is None:
                errback = log.error
            error_handler = lambda err:errback(dbus_to_bridge_exception(err))
        return self.db_core_iface.discoFindByFeatures(namespaces, identities, bare_jid, service, roster, own_jid, local_device, profile_key, timeout=const_TIMEOUT, reply_handler=callback, error_handler=error_handler)

    def discoInfos(self, entity_jid, node=u'', use_cache=True, profile_key="@DEFAULT@", callback=None, errback=None):
        if callback is None:
            error_handler = None
        else:
            if errback is None:
                errback = log.error
            error_handler = lambda err:errback(dbus_to_bridge_exception(err))
        return self.db_core_iface.discoInfos(entity_jid, node, use_cache, profile_key, timeout=const_TIMEOUT, reply_handler=callback, error_handler=error_handler)

    def discoItems(self, entity_jid, node=u'', use_cache=True, profile_key="@DEFAULT@", callback=None, errback=None):
        if callback is None:
            error_handler = None
        else:
            if errback is None:
                errback = log.error
            error_handler = lambda err:errback(dbus_to_bridge_exception(err))
        return self.db_core_iface.discoItems(entity_jid, node, use_cache, profile_key, timeout=const_TIMEOUT, reply_handler=callback, error_handler=error_handler)

    def disconnect(self, profile_key="@DEFAULT@", callback=None, errback=None):
        if callback is None:
            error_handler = None
        else:
            if errback is None:
                errback = log.error
            error_handler = lambda err:errback(dbus_to_bridge_exception(err))
        return self.db_core_iface.disconnect(profile_key, timeout=const_TIMEOUT, reply_handler=callback, error_handler=error_handler)

    def encryptionNamespaceGet(self, arg_0, callback=None, errback=None):
        if callback is None:
            error_handler = None
        else:
            if errback is None:
                errback = log.error
            error_handler = lambda err:errback(dbus_to_bridge_exception(err))
        kwargs={}
        if callback is not None:
            kwargs['timeout'] = const_TIMEOUT
            kwargs['reply_handler'] = callback
            kwargs['error_handler'] = error_handler
        return str(self.db_core_iface.encryptionNamespaceGet(arg_0, **kwargs))

    def encryptionPluginsGet(self, callback=None, errback=None):
        if callback is None:
            error_handler = None
        else:
            if errback is None:
                errback = log.error
            error_handler = lambda err:errback(dbus_to_bridge_exception(err))
        kwargs={}
        if callback is not None:
            kwargs['timeout'] = const_TIMEOUT
            kwargs['reply_handler'] = callback
            kwargs['error_handler'] = error_handler
        return str(self.db_core_iface.encryptionPluginsGet(**kwargs))

    def encryptionTrustUIGet(self, to_jid, namespace, profile_key, callback=None, errback=None):
        if callback is None:
            error_handler = None
        else:
            if errback is None:
                errback = log.error
            error_handler = lambda err:errback(dbus_to_bridge_exception(err))
        return str(self.db_core_iface.encryptionTrustUIGet(to_jid, namespace, profile_key, timeout=const_TIMEOUT, reply_handler=callback, error_handler=error_handler))

    def getConfig(self, section, name, callback=None, errback=None):
        if callback is None:
            error_handler = None
        else:
            if errback is None:
                errback = log.error
            error_handler = lambda err:errback(dbus_to_bridge_exception(err))
        kwargs={}
        if callback is not None:
            kwargs['timeout'] = const_TIMEOUT
            kwargs['reply_handler'] = callback
            kwargs['error_handler'] = error_handler
        return str(self.db_core_iface.getConfig(section, name, **kwargs))

    def getContacts(self, profile_key="@DEFAULT@", callback=None, errback=None):
        if callback is None:
            error_handler = None
        else:
            if errback is None:
                errback = log.error
            error_handler = lambda err:errback(dbus_to_bridge_exception(err))
        return self.db_core_iface.getContacts(profile_key, timeout=const_TIMEOUT, reply_handler=callback, error_handler=error_handler)

    def getContactsFromGroup(self, group, profile_key="@DEFAULT@", callback=None, errback=None):
        if callback is None:
            error_handler = None
        else:
            if errback is None:
                errback = log.error
            error_handler = lambda err:errback(dbus_to_bridge_exception(err))
        kwargs={}
        if callback is not None:
            kwargs['timeout'] = const_TIMEOUT
            kwargs['reply_handler'] = callback
            kwargs['error_handler'] = error_handler
        return self.db_core_iface.getContactsFromGroup(group, profile_key, **kwargs)

    def getEntitiesData(self, jids, keys, profile, callback=None, errback=None):
        if callback is None:
            error_handler = None
        else:
            if errback is None:
                errback = log.error
            error_handler = lambda err:errback(dbus_to_bridge_exception(err))
        kwargs={}
        if callback is not None:
            kwargs['timeout'] = const_TIMEOUT
            kwargs['reply_handler'] = callback
            kwargs['error_handler'] = error_handler
        return self.db_core_iface.getEntitiesData(jids, keys, profile, **kwargs)

    def getEntityData(self, jid, keys, profile, callback=None, errback=None):
        if callback is None:
            error_handler = None
        else:
            if errback is None:
                errback = log.error
            error_handler = lambda err:errback(dbus_to_bridge_exception(err))
        kwargs={}
        if callback is not None:
            kwargs['timeout'] = const_TIMEOUT
            kwargs['reply_handler'] = callback
            kwargs['error_handler'] = error_handler
        return self.db_core_iface.getEntityData(jid, keys, profile, **kwargs)

    def getFeatures(self, profile_key, callback=None, errback=None):
        if callback is None:
            error_handler = None
        else:
            if errback is None:
                errback = log.error
            error_handler = lambda err:errback(dbus_to_bridge_exception(err))
        return self.db_core_iface.getFeatures(profile_key, timeout=const_TIMEOUT, reply_handler=callback, error_handler=error_handler)

    def getMainResource(self, contact_jid, profile_key="@DEFAULT@", callback=None, errback=None):
        if callback is None:
            error_handler = None
        else:
            if errback is None:
                errback = log.error
            error_handler = lambda err:errback(dbus_to_bridge_exception(err))
        kwargs={}
        if callback is not None:
            kwargs['timeout'] = const_TIMEOUT
            kwargs['reply_handler'] = callback
            kwargs['error_handler'] = error_handler
        return str(self.db_core_iface.getMainResource(contact_jid, profile_key, **kwargs))

    def getParamA(self, name, category, attribute="value", profile_key="@DEFAULT@", callback=None, errback=None):
        if callback is None:
            error_handler = None
        else:
            if errback is None:
                errback = log.error
            error_handler = lambda err:errback(dbus_to_bridge_exception(err))
        kwargs={}
        if callback is not None:
            kwargs['timeout'] = const_TIMEOUT
            kwargs['reply_handler'] = callback
            kwargs['error_handler'] = error_handler
        return str(self.db_core_iface.getParamA(name, category, attribute, profile_key, **kwargs))

    def getParamsCategories(self, callback=None, errback=None):
        if callback is None:
            error_handler = None
        else:
            if errback is None:
                errback = log.error
            error_handler = lambda err:errback(dbus_to_bridge_exception(err))
        kwargs={}
        if callback is not None:
            kwargs['timeout'] = const_TIMEOUT
            kwargs['reply_handler'] = callback
            kwargs['error_handler'] = error_handler
        return self.db_core_iface.getParamsCategories(**kwargs)

    def getParamsUI(self, security_limit=-1, app='', extra='', profile_key="@DEFAULT@", callback=None, errback=None):
        if callback is None:
            error_handler = None
        else:
            if errback is None:
                errback = log.error
            error_handler = lambda err:errback(dbus_to_bridge_exception(err))
        return str(self.db_core_iface.getParamsUI(security_limit, app, extra, profile_key, timeout=const_TIMEOUT, reply_handler=callback, error_handler=error_handler))

    def getPresenceStatuses(self, profile_key="@DEFAULT@", callback=None, errback=None):
        if callback is None:
            error_handler = None
        else:
            if errback is None:
                errback = log.error
            error_handler = lambda err:errback(dbus_to_bridge_exception(err))
        kwargs={}
        if callback is not None:
            kwargs['timeout'] = const_TIMEOUT
            kwargs['reply_handler'] = callback
            kwargs['error_handler'] = error_handler
        return self.db_core_iface.getPresenceStatuses(profile_key, **kwargs)

    def getReady(self, callback=None, errback=None):
        if callback is None:
            error_handler = None
        else:
            if errback is None:
                errback = log.error
            error_handler = lambda err:errback(dbus_to_bridge_exception(err))
        return self.db_core_iface.getReady(timeout=const_TIMEOUT, reply_handler=callback, error_handler=error_handler)

    def getVersion(self, callback=None, errback=None):
        if callback is None:
            error_handler = None
        else:
            if errback is None:
                errback = log.error
            error_handler = lambda err:errback(dbus_to_bridge_exception(err))
        kwargs={}
        if callback is not None:
            kwargs['timeout'] = const_TIMEOUT
            kwargs['reply_handler'] = callback
            kwargs['error_handler'] = error_handler
        return str(self.db_core_iface.getVersion(**kwargs))

    def getWaitingSub(self, profile_key="@DEFAULT@", callback=None, errback=None):
        if callback is None:
            error_handler = None
        else:
            if errback is None:
                errback = log.error
            error_handler = lambda err:errback(dbus_to_bridge_exception(err))
        kwargs={}
        if callback is not None:
            kwargs['timeout'] = const_TIMEOUT
            kwargs['reply_handler'] = callback
            kwargs['error_handler'] = error_handler
        return self.db_core_iface.getWaitingSub(profile_key, **kwargs)

    def historyGet(self, from_jid, to_jid, limit, between=True, filters='', profile="@NONE@", callback=None, errback=None):
        if callback is None:
            error_handler = None
        else:
            if errback is None:
                errback = log.error
            error_handler = lambda err:errback(dbus_to_bridge_exception(err))
        return self.db_core_iface.historyGet(from_jid, to_jid, limit, between, filters, profile, timeout=const_TIMEOUT, reply_handler=callback, error_handler=error_handler)

    def imageCheck(self, arg_0, callback=None, errback=None):
        if callback is None:
            error_handler = None
        else:
            if errback is None:
                errback = log.error
            error_handler = lambda err:errback(dbus_to_bridge_exception(err))
        kwargs={}
        if callback is not None:
            kwargs['timeout'] = const_TIMEOUT
            kwargs['reply_handler'] = callback
            kwargs['error_handler'] = error_handler
        return str(self.db_core_iface.imageCheck(arg_0, **kwargs))

    def imageConvert(self, source, dest, arg_2, extra, callback=None, errback=None):
        if callback is None:
            error_handler = None
        else:
            if errback is None:
                errback = log.error
            error_handler = lambda err:errback(dbus_to_bridge_exception(err))
        return str(self.db_core_iface.imageConvert(source, dest, arg_2, extra, timeout=const_TIMEOUT, reply_handler=callback, error_handler=error_handler))

    def imageGeneratePreview(self, image_path, profile_key, callback=None, errback=None):
        if callback is None:
            error_handler = None
        else:
            if errback is None:
                errback = log.error
            error_handler = lambda err:errback(dbus_to_bridge_exception(err))
        return str(self.db_core_iface.imageGeneratePreview(image_path, profile_key, timeout=const_TIMEOUT, reply_handler=callback, error_handler=error_handler))

    def imageResize(self, image_path, width, height, callback=None, errback=None):
        if callback is None:
            error_handler = None
        else:
            if errback is None:
                errback = log.error
            error_handler = lambda err:errback(dbus_to_bridge_exception(err))
        return str(self.db_core_iface.imageResize(image_path, width, height, timeout=const_TIMEOUT, reply_handler=callback, error_handler=error_handler))

    def isConnected(self, profile_key="@DEFAULT@", callback=None, errback=None):
        if callback is None:
            error_handler = None
        else:
            if errback is None:
                errback = log.error
            error_handler = lambda err:errback(dbus_to_bridge_exception(err))
        kwargs={}
        if callback is not None:
            kwargs['timeout'] = const_TIMEOUT
            kwargs['reply_handler'] = callback
            kwargs['error_handler'] = error_handler
        return self.db_core_iface.isConnected(profile_key, **kwargs)

    def launchAction(self, callback_id, data, profile_key="@DEFAULT@", callback=None, errback=None):
        if callback is None:
            error_handler = None
        else:
            if errback is None:
                errback = log.error
            error_handler = lambda err:errback(dbus_to_bridge_exception(err))
        return self.db_core_iface.launchAction(callback_id, data, profile_key, timeout=const_TIMEOUT, reply_handler=callback, error_handler=error_handler)

    def loadParamsTemplate(self, filename, callback=None, errback=None):
        if callback is None:
            error_handler = None
        else:
            if errback is None:
                errback = log.error
            error_handler = lambda err:errback(dbus_to_bridge_exception(err))
        kwargs={}
        if callback is not None:
            kwargs['timeout'] = const_TIMEOUT
            kwargs['reply_handler'] = callback
            kwargs['error_handler'] = error_handler
        return self.db_core_iface.loadParamsTemplate(filename, **kwargs)

    def menuHelpGet(self, menu_id, language, callback=None, errback=None):
        if callback is None:
            error_handler = None
        else:
            if errback is None:
                errback = log.error
            error_handler = lambda err:errback(dbus_to_bridge_exception(err))
        kwargs={}
        if callback is not None:
            kwargs['timeout'] = const_TIMEOUT
            kwargs['reply_handler'] = callback
            kwargs['error_handler'] = error_handler
        return str(self.db_core_iface.menuHelpGet(menu_id, language, **kwargs))

    def menuLaunch(self, menu_type, path, data, security_limit, profile_key, callback=None, errback=None):
        if callback is None:
            error_handler = None
        else:
            if errback is None:
                errback = log.error
            error_handler = lambda err:errback(dbus_to_bridge_exception(err))
        return self.db_core_iface.menuLaunch(menu_type, path, data, security_limit, profile_key, timeout=const_TIMEOUT, reply_handler=callback, error_handler=error_handler)

    def menusGet(self, language, security_limit, callback=None, errback=None):
        if callback is None:
            error_handler = None
        else:
            if errback is None:
                errback = log.error
            error_handler = lambda err:errback(dbus_to_bridge_exception(err))
        kwargs={}
        if callback is not None:
            kwargs['timeout'] = const_TIMEOUT
            kwargs['reply_handler'] = callback
            kwargs['error_handler'] = error_handler
        return self.db_core_iface.menusGet(language, security_limit, **kwargs)

    def messageEncryptionGet(self, to_jid, profile_key, callback=None, errback=None):
        if callback is None:
            error_handler = None
        else:
            if errback is None:
                errback = log.error
            error_handler = lambda err:errback(dbus_to_bridge_exception(err))
        kwargs={}
        if callback is not None:
            kwargs['timeout'] = const_TIMEOUT
            kwargs['reply_handler'] = callback
            kwargs['error_handler'] = error_handler
        return str(self.db_core_iface.messageEncryptionGet(to_jid, profile_key, **kwargs))

    def messageEncryptionStart(self, to_jid, namespace='', replace=False, profile_key="@NONE@", callback=None, errback=None):
        if callback is None:
            error_handler = None
        else:
            if errback is None:
                errback = log.error
            error_handler = lambda err:errback(dbus_to_bridge_exception(err))
        return self.db_core_iface.messageEncryptionStart(to_jid, namespace, replace, profile_key, timeout=const_TIMEOUT, reply_handler=callback, error_handler=error_handler)

    def messageEncryptionStop(self, to_jid, profile_key, callback=None, errback=None):
        if callback is None:
            error_handler = None
        else:
            if errback is None:
                errback = log.error
            error_handler = lambda err:errback(dbus_to_bridge_exception(err))
        return self.db_core_iface.messageEncryptionStop(to_jid, profile_key, timeout=const_TIMEOUT, reply_handler=callback, error_handler=error_handler)

    def messageSend(self, to_jid, message, subject={}, mess_type="auto", extra={}, profile_key="@NONE@", callback=None, errback=None):
        if callback is None:
            error_handler = None
        else:
            if errback is None:
                errback = log.error
            error_handler = lambda err:errback(dbus_to_bridge_exception(err))
        return self.db_core_iface.messageSend(to_jid, message, subject, mess_type, extra, profile_key, timeout=const_TIMEOUT, reply_handler=callback, error_handler=error_handler)

    def namespacesGet(self, callback=None, errback=None):
        if callback is None:
            error_handler = None
        else:
            if errback is None:
                errback = log.error
            error_handler = lambda err:errback(dbus_to_bridge_exception(err))
        kwargs={}
        if callback is not None:
            kwargs['timeout'] = const_TIMEOUT
            kwargs['reply_handler'] = callback
            kwargs['error_handler'] = error_handler
        return self.db_core_iface.namespacesGet(**kwargs)

    def paramsRegisterApp(self, xml, security_limit=-1, app='', callback=None, errback=None):
        if callback is None:
            error_handler = None
        else:
            if errback is None:
                errback = log.error
            error_handler = lambda err:errback(dbus_to_bridge_exception(err))
        kwargs={}
        if callback is not None:
            kwargs['timeout'] = const_TIMEOUT
            kwargs['reply_handler'] = callback
            kwargs['error_handler'] = error_handler
        return self.db_core_iface.paramsRegisterApp(xml, security_limit, app, **kwargs)

    def privateDataDelete(self, namespace, key, arg_2, callback=None, errback=None):
        if callback is None:
            error_handler = None
        else:
            if errback is None:
                errback = log.error
            error_handler = lambda err:errback(dbus_to_bridge_exception(err))
        return self.db_core_iface.privateDataDelete(namespace, key, arg_2, timeout=const_TIMEOUT, reply_handler=callback, error_handler=error_handler)

    def privateDataGet(self, namespace, key, profile_key, callback=None, errback=None):
        if callback is None:
            error_handler = None
        else:
            if errback is None:
                errback = log.error
            error_handler = lambda err:errback(dbus_to_bridge_exception(err))
        return str(self.db_core_iface.privateDataGet(namespace, key, profile_key, timeout=const_TIMEOUT, reply_handler=callback, error_handler=error_handler))

    def privateDataSet(self, namespace, key, data, profile_key, callback=None, errback=None):
        if callback is None:
            error_handler = None
        else:
            if errback is None:
                errback = log.error
            error_handler = lambda err:errback(dbus_to_bridge_exception(err))
        return self.db_core_iface.privateDataSet(namespace, key, data, profile_key, timeout=const_TIMEOUT, reply_handler=callback, error_handler=error_handler)

    def profileCreate(self, profile, password='', component='', callback=None, errback=None):
        if callback is None:
            error_handler = None
        else:
            if errback is None:
                errback = log.error
            error_handler = lambda err:errback(dbus_to_bridge_exception(err))
        return self.db_core_iface.profileCreate(profile, password, component, timeout=const_TIMEOUT, reply_handler=callback, error_handler=error_handler)

    def profileIsSessionStarted(self, profile_key="@DEFAULT@", callback=None, errback=None):
        if callback is None:
            error_handler = None
        else:
            if errback is None:
                errback = log.error
            error_handler = lambda err:errback(dbus_to_bridge_exception(err))
        kwargs={}
        if callback is not None:
            kwargs['timeout'] = const_TIMEOUT
            kwargs['reply_handler'] = callback
            kwargs['error_handler'] = error_handler
        return self.db_core_iface.profileIsSessionStarted(profile_key, **kwargs)

    def profileNameGet(self, profile_key="@DEFAULT@", callback=None, errback=None):
        if callback is None:
            error_handler = None
        else:
            if errback is None:
                errback = log.error
            error_handler = lambda err:errback(dbus_to_bridge_exception(err))
        kwargs={}
        if callback is not None:
            kwargs['timeout'] = const_TIMEOUT
            kwargs['reply_handler'] = callback
            kwargs['error_handler'] = error_handler
        return str(self.db_core_iface.profileNameGet(profile_key, **kwargs))

    def profileSetDefault(self, profile, callback=None, errback=None):
        if callback is None:
            error_handler = None
        else:
            if errback is None:
                errback = log.error
            error_handler = lambda err:errback(dbus_to_bridge_exception(err))
        kwargs={}
        if callback is not None:
            kwargs['timeout'] = const_TIMEOUT
            kwargs['reply_handler'] = callback
            kwargs['error_handler'] = error_handler
        return self.db_core_iface.profileSetDefault(profile, **kwargs)

    def profileStartSession(self, password='', profile_key="@DEFAULT@", callback=None, errback=None):
        if callback is None:
            error_handler = None
        else:
            if errback is None:
                errback = log.error
            error_handler = lambda err:errback(dbus_to_bridge_exception(err))
        return self.db_core_iface.profileStartSession(password, profile_key, timeout=const_TIMEOUT, reply_handler=callback, error_handler=error_handler)

    def profilesListGet(self, clients=True, components=False, callback=None, errback=None):
        if callback is None:
            error_handler = None
        else:
            if errback is None:
                errback = log.error
            error_handler = lambda err:errback(dbus_to_bridge_exception(err))
        kwargs={}
        if callback is not None:
            kwargs['timeout'] = const_TIMEOUT
            kwargs['reply_handler'] = callback
            kwargs['error_handler'] = error_handler
        return self.db_core_iface.profilesListGet(clients, components, **kwargs)

    def progressGet(self, id, profile, callback=None, errback=None):
        if callback is None:
            error_handler = None
        else:
            if errback is None:
                errback = log.error
            error_handler = lambda err:errback(dbus_to_bridge_exception(err))
        kwargs={}
        if callback is not None:
            kwargs['timeout'] = const_TIMEOUT
            kwargs['reply_handler'] = callback
            kwargs['error_handler'] = error_handler
        return self.db_core_iface.progressGet(id, profile, **kwargs)

    def progressGetAll(self, profile, callback=None, errback=None):
        if callback is None:
            error_handler = None
        else:
            if errback is None:
                errback = log.error
            error_handler = lambda err:errback(dbus_to_bridge_exception(err))
        kwargs={}
        if callback is not None:
            kwargs['timeout'] = const_TIMEOUT
            kwargs['reply_handler'] = callback
            kwargs['error_handler'] = error_handler
        return self.db_core_iface.progressGetAll(profile, **kwargs)

    def progressGetAllMetadata(self, profile, callback=None, errback=None):
        if callback is None:
            error_handler = None
        else:
            if errback is None:
                errback = log.error
            error_handler = lambda err:errback(dbus_to_bridge_exception(err))
        kwargs={}
        if callback is not None:
            kwargs['timeout'] = const_TIMEOUT
            kwargs['reply_handler'] = callback
            kwargs['error_handler'] = error_handler
        return self.db_core_iface.progressGetAllMetadata(profile, **kwargs)

    def rosterResync(self, profile_key="@DEFAULT@", callback=None, errback=None):
        if callback is None:
            error_handler = None
        else:
            if errback is None:
                errback = log.error
            error_handler = lambda err:errback(dbus_to_bridge_exception(err))
        return self.db_core_iface.rosterResync(profile_key, timeout=const_TIMEOUT, reply_handler=callback, error_handler=error_handler)

    def saveParamsTemplate(self, filename, callback=None, errback=None):
        if callback is None:
            error_handler = None
        else:
            if errback is None:
                errback = log.error
            error_handler = lambda err:errback(dbus_to_bridge_exception(err))
        kwargs={}
        if callback is not None:
            kwargs['timeout'] = const_TIMEOUT
            kwargs['reply_handler'] = callback
            kwargs['error_handler'] = error_handler
        return self.db_core_iface.saveParamsTemplate(filename, **kwargs)

    def sessionInfosGet(self, profile_key, callback=None, errback=None):
        if callback is None:
            error_handler = None
        else:
            if errback is None:
                errback = log.error
            error_handler = lambda err:errback(dbus_to_bridge_exception(err))
        return self.db_core_iface.sessionInfosGet(profile_key, timeout=const_TIMEOUT, reply_handler=callback, error_handler=error_handler)

    def setParam(self, name, value, category, security_limit=-1, profile_key="@DEFAULT@", callback=None, errback=None):
        if callback is None:
            error_handler = None
        else:
            if errback is None:
                errback = log.error
            error_handler = lambda err:errback(dbus_to_bridge_exception(err))
        kwargs={}
        if callback is not None:
            kwargs['timeout'] = const_TIMEOUT
            kwargs['reply_handler'] = callback
            kwargs['error_handler'] = error_handler
        return self.db_core_iface.setParam(name, value, category, security_limit, profile_key, **kwargs)

    def setPresence(self, to_jid='', show='', statuses={}, profile_key="@DEFAULT@", callback=None, errback=None):
        if callback is None:
            error_handler = None
        else:
            if errback is None:
                errback = log.error
            error_handler = lambda err:errback(dbus_to_bridge_exception(err))
        kwargs={}
        if callback is not None:
            kwargs['timeout'] = const_TIMEOUT
            kwargs['reply_handler'] = callback
            kwargs['error_handler'] = error_handler
        return self.db_core_iface.setPresence(to_jid, show, statuses, profile_key, **kwargs)

    def subscription(self, sub_type, entity, profile_key="@DEFAULT@", callback=None, errback=None):
        if callback is None:
            error_handler = None
        else:
            if errback is None:
                errback = log.error
            error_handler = lambda err:errback(dbus_to_bridge_exception(err))
        kwargs={}
        if callback is not None:
            kwargs['timeout'] = const_TIMEOUT
            kwargs['reply_handler'] = callback
            kwargs['error_handler'] = error_handler
        return self.db_core_iface.subscription(sub_type, entity, profile_key, **kwargs)

    def updateContact(self, entity_jid, name, groups, profile_key="@DEFAULT@", callback=None, errback=None):
        if callback is None:
            error_handler = None
        else:
            if errback is None:
                errback = log.error
            error_handler = lambda err:errback(dbus_to_bridge_exception(err))
        kwargs={}
        if callback is not None:
            kwargs['timeout'] = const_TIMEOUT
            kwargs['reply_handler'] = callback
            kwargs['error_handler'] = error_handler
        return self.db_core_iface.updateContact(entity_jid, name, groups, profile_key, **kwargs)


class AIOBridge(Bridge):

    def register_signal(self, functionName, handler, iface="core"):
        loop = asyncio.get_running_loop()
        async_handler = lambda *args: asyncio.run_coroutine_threadsafe(handler(*args), loop)
        return super().register_signal(functionName, async_handler, iface)

    def __getattribute__(self, name):
        """ usual __getattribute__ if the method exists, else try to find a plugin method """
        try:
            return object.__getattribute__(self, name)
        except AttributeError:
            # The attribute is not found, we try the plugin proxy to find the requested method
            def getPluginMethod(*args, **kwargs):
                loop = asyncio.get_running_loop()
                fut = loop.create_future()
                method = getattr(self.db_plugin_iface, name)
                reply_handler = lambda ret=None: loop.call_soon_threadsafe(
                    fut.set_result, ret)
                error_handler = lambda err: loop.call_soon_threadsafe(
                    fut.set_exception, dbus_to_bridge_exception(err))
                try:
                    method(
                        *args,
                        **kwargs,
                        timeout=const_TIMEOUT,
                        reply_handler=reply_handler,
                        error_handler=error_handler
                    )
                except ValueError as e:
                    if e.args[0].startswith("Unable to guess signature"):
                        # same hack as for Bridge.__getattribute__
                        log.warning("using hack to work around inspection issue")
                        proxy = self.db_plugin_iface.proxy_object
                        IN_PROGRESS = proxy.INTROSPECT_STATE_INTROSPECT_IN_PROGRESS
                        proxy._introspect_state = IN_PROGRESS
                        proxy._Introspect()
                        self.db_plugin_iface.get_dbus_method(name)(
                            *args,
                            **kwargs,
                            timeout=const_TIMEOUT,
                            reply_handler=reply_handler,
                            error_handler=error_handler
                        )

                    else:
                        raise e
                return fut

            return getPluginMethod

    def bridgeConnect(self):
        loop = asyncio.get_running_loop()
        fut = loop.create_future()
        super().bridgeConnect(
            callback=lambda: loop.call_soon_threadsafe(fut.set_result, None),
            errback=lambda e: loop.call_soon_threadsafe(fut.set_exception, e)
        )
        return fut

    def actionsGet(self, profile_key="@DEFAULT@"):
        loop = asyncio.get_running_loop()
        fut = loop.create_future()
        reply_handler = lambda ret=None: loop.call_soon_threadsafe(fut.set_result, ret)
        error_handler = lambda err: loop.call_soon_threadsafe(fut.set_exception, dbus_to_bridge_exception(err))
        self.db_core_iface.actionsGet(profile_key, timeout=const_TIMEOUT, reply_handler=reply_handler, error_handler=error_handler)
        return fut

    def addContact(self, entity_jid, profile_key="@DEFAULT@"):
        loop = asyncio.get_running_loop()
        fut = loop.create_future()
        reply_handler = lambda ret=None: loop.call_soon_threadsafe(fut.set_result, ret)
        error_handler = lambda err: loop.call_soon_threadsafe(fut.set_exception, dbus_to_bridge_exception(err))
        self.db_core_iface.addContact(entity_jid, profile_key, timeout=const_TIMEOUT, reply_handler=reply_handler, error_handler=error_handler)
        return fut

    def asyncDeleteProfile(self, profile):
        loop = asyncio.get_running_loop()
        fut = loop.create_future()
        reply_handler = lambda ret=None: loop.call_soon_threadsafe(fut.set_result, ret)
        error_handler = lambda err: loop.call_soon_threadsafe(fut.set_exception, dbus_to_bridge_exception(err))
        self.db_core_iface.asyncDeleteProfile(profile, timeout=const_TIMEOUT, reply_handler=reply_handler, error_handler=error_handler)
        return fut

    def asyncGetParamA(self, name, category, attribute="value", security_limit=-1, profile_key="@DEFAULT@"):
        loop = asyncio.get_running_loop()
        fut = loop.create_future()
        reply_handler = lambda ret=None: loop.call_soon_threadsafe(fut.set_result, ret)
        error_handler = lambda err: loop.call_soon_threadsafe(fut.set_exception, dbus_to_bridge_exception(err))
        self.db_core_iface.asyncGetParamA(name, category, attribute, security_limit, profile_key, timeout=const_TIMEOUT, reply_handler=reply_handler, error_handler=error_handler)
        return fut

    def asyncGetParamsValuesFromCategory(self, category, security_limit=-1, app="", extra="", profile_key="@DEFAULT@"):
        loop = asyncio.get_running_loop()
        fut = loop.create_future()
        reply_handler = lambda ret=None: loop.call_soon_threadsafe(fut.set_result, ret)
        error_handler = lambda err: loop.call_soon_threadsafe(fut.set_exception, dbus_to_bridge_exception(err))
        self.db_core_iface.asyncGetParamsValuesFromCategory(category, security_limit, app, extra, profile_key, timeout=const_TIMEOUT, reply_handler=reply_handler, error_handler=error_handler)
        return fut

    def connect(self, profile_key="@DEFAULT@", password='', options={}):
        loop = asyncio.get_running_loop()
        fut = loop.create_future()
        reply_handler = lambda ret=None: loop.call_soon_threadsafe(fut.set_result, ret)
        error_handler = lambda err: loop.call_soon_threadsafe(fut.set_exception, dbus_to_bridge_exception(err))
        self.db_core_iface.connect(profile_key, password, options, timeout=const_TIMEOUT, reply_handler=reply_handler, error_handler=error_handler)
        return fut

    def contactGet(self, arg_0, profile_key="@DEFAULT@"):
        loop = asyncio.get_running_loop()
        fut = loop.create_future()
        reply_handler = lambda ret=None: loop.call_soon_threadsafe(fut.set_result, ret)
        error_handler = lambda err: loop.call_soon_threadsafe(fut.set_exception, dbus_to_bridge_exception(err))
        self.db_core_iface.contactGet(arg_0, profile_key, timeout=const_TIMEOUT, reply_handler=reply_handler, error_handler=error_handler)
        return fut

    def delContact(self, entity_jid, profile_key="@DEFAULT@"):
        loop = asyncio.get_running_loop()
        fut = loop.create_future()
        reply_handler = lambda ret=None: loop.call_soon_threadsafe(fut.set_result, ret)
        error_handler = lambda err: loop.call_soon_threadsafe(fut.set_exception, dbus_to_bridge_exception(err))
        self.db_core_iface.delContact(entity_jid, profile_key, timeout=const_TIMEOUT, reply_handler=reply_handler, error_handler=error_handler)
        return fut

    def devicesInfosGet(self, bare_jid, profile_key):
        loop = asyncio.get_running_loop()
        fut = loop.create_future()
        reply_handler = lambda ret=None: loop.call_soon_threadsafe(fut.set_result, ret)
        error_handler = lambda err: loop.call_soon_threadsafe(fut.set_exception, dbus_to_bridge_exception(err))
        self.db_core_iface.devicesInfosGet(bare_jid, profile_key, timeout=const_TIMEOUT, reply_handler=reply_handler, error_handler=error_handler)
        return fut

    def discoFindByFeatures(self, namespaces, identities, bare_jid=False, service=True, roster=True, own_jid=True, local_device=False, profile_key="@DEFAULT@"):
        loop = asyncio.get_running_loop()
        fut = loop.create_future()
        reply_handler = lambda ret=None: loop.call_soon_threadsafe(fut.set_result, ret)
        error_handler = lambda err: loop.call_soon_threadsafe(fut.set_exception, dbus_to_bridge_exception(err))
        self.db_core_iface.discoFindByFeatures(namespaces, identities, bare_jid, service, roster, own_jid, local_device, profile_key, timeout=const_TIMEOUT, reply_handler=reply_handler, error_handler=error_handler)
        return fut

    def discoInfos(self, entity_jid, node=u'', use_cache=True, profile_key="@DEFAULT@"):
        loop = asyncio.get_running_loop()
        fut = loop.create_future()
        reply_handler = lambda ret=None: loop.call_soon_threadsafe(fut.set_result, ret)
        error_handler = lambda err: loop.call_soon_threadsafe(fut.set_exception, dbus_to_bridge_exception(err))
        self.db_core_iface.discoInfos(entity_jid, node, use_cache, profile_key, timeout=const_TIMEOUT, reply_handler=reply_handler, error_handler=error_handler)
        return fut

    def discoItems(self, entity_jid, node=u'', use_cache=True, profile_key="@DEFAULT@"):
        loop = asyncio.get_running_loop()
        fut = loop.create_future()
        reply_handler = lambda ret=None: loop.call_soon_threadsafe(fut.set_result, ret)
        error_handler = lambda err: loop.call_soon_threadsafe(fut.set_exception, dbus_to_bridge_exception(err))
        self.db_core_iface.discoItems(entity_jid, node, use_cache, profile_key, timeout=const_TIMEOUT, reply_handler=reply_handler, error_handler=error_handler)
        return fut

    def disconnect(self, profile_key="@DEFAULT@"):
        loop = asyncio.get_running_loop()
        fut = loop.create_future()
        reply_handler = lambda ret=None: loop.call_soon_threadsafe(fut.set_result, ret)
        error_handler = lambda err: loop.call_soon_threadsafe(fut.set_exception, dbus_to_bridge_exception(err))
        self.db_core_iface.disconnect(profile_key, timeout=const_TIMEOUT, reply_handler=reply_handler, error_handler=error_handler)
        return fut

    def encryptionNamespaceGet(self, arg_0):
        loop = asyncio.get_running_loop()
        fut = loop.create_future()
        reply_handler = lambda ret=None: loop.call_soon_threadsafe(fut.set_result, ret)
        error_handler = lambda err: loop.call_soon_threadsafe(fut.set_exception, dbus_to_bridge_exception(err))
        self.db_core_iface.encryptionNamespaceGet(arg_0, timeout=const_TIMEOUT, reply_handler=reply_handler, error_handler=error_handler)
        return fut

    def encryptionPluginsGet(self):
        loop = asyncio.get_running_loop()
        fut = loop.create_future()
        reply_handler = lambda ret=None: loop.call_soon_threadsafe(fut.set_result, ret)
        error_handler = lambda err: loop.call_soon_threadsafe(fut.set_exception, dbus_to_bridge_exception(err))
        self.db_core_iface.encryptionPluginsGet(timeout=const_TIMEOUT, reply_handler=reply_handler, error_handler=error_handler)
        return fut

    def encryptionTrustUIGet(self, to_jid, namespace, profile_key):
        loop = asyncio.get_running_loop()
        fut = loop.create_future()
        reply_handler = lambda ret=None: loop.call_soon_threadsafe(fut.set_result, ret)
        error_handler = lambda err: loop.call_soon_threadsafe(fut.set_exception, dbus_to_bridge_exception(err))
        self.db_core_iface.encryptionTrustUIGet(to_jid, namespace, profile_key, timeout=const_TIMEOUT, reply_handler=reply_handler, error_handler=error_handler)
        return fut

    def getConfig(self, section, name):
        loop = asyncio.get_running_loop()
        fut = loop.create_future()
        reply_handler = lambda ret=None: loop.call_soon_threadsafe(fut.set_result, ret)
        error_handler = lambda err: loop.call_soon_threadsafe(fut.set_exception, dbus_to_bridge_exception(err))
        self.db_core_iface.getConfig(section, name, timeout=const_TIMEOUT, reply_handler=reply_handler, error_handler=error_handler)
        return fut

    def getContacts(self, profile_key="@DEFAULT@"):
        loop = asyncio.get_running_loop()
        fut = loop.create_future()
        reply_handler = lambda ret=None: loop.call_soon_threadsafe(fut.set_result, ret)
        error_handler = lambda err: loop.call_soon_threadsafe(fut.set_exception, dbus_to_bridge_exception(err))
        self.db_core_iface.getContacts(profile_key, timeout=const_TIMEOUT, reply_handler=reply_handler, error_handler=error_handler)
        return fut

    def getContactsFromGroup(self, group, profile_key="@DEFAULT@"):
        loop = asyncio.get_running_loop()
        fut = loop.create_future()
        reply_handler = lambda ret=None: loop.call_soon_threadsafe(fut.set_result, ret)
        error_handler = lambda err: loop.call_soon_threadsafe(fut.set_exception, dbus_to_bridge_exception(err))
        self.db_core_iface.getContactsFromGroup(group, profile_key, timeout=const_TIMEOUT, reply_handler=reply_handler, error_handler=error_handler)
        return fut

    def getEntitiesData(self, jids, keys, profile):
        loop = asyncio.get_running_loop()
        fut = loop.create_future()
        reply_handler = lambda ret=None: loop.call_soon_threadsafe(fut.set_result, ret)
        error_handler = lambda err: loop.call_soon_threadsafe(fut.set_exception, dbus_to_bridge_exception(err))
        self.db_core_iface.getEntitiesData(jids, keys, profile, timeout=const_TIMEOUT, reply_handler=reply_handler, error_handler=error_handler)
        return fut

    def getEntityData(self, jid, keys, profile):
        loop = asyncio.get_running_loop()
        fut = loop.create_future()
        reply_handler = lambda ret=None: loop.call_soon_threadsafe(fut.set_result, ret)
        error_handler = lambda err: loop.call_soon_threadsafe(fut.set_exception, dbus_to_bridge_exception(err))
        self.db_core_iface.getEntityData(jid, keys, profile, timeout=const_TIMEOUT, reply_handler=reply_handler, error_handler=error_handler)
        return fut

    def getFeatures(self, profile_key):
        loop = asyncio.get_running_loop()
        fut = loop.create_future()
        reply_handler = lambda ret=None: loop.call_soon_threadsafe(fut.set_result, ret)
        error_handler = lambda err: loop.call_soon_threadsafe(fut.set_exception, dbus_to_bridge_exception(err))
        self.db_core_iface.getFeatures(profile_key, timeout=const_TIMEOUT, reply_handler=reply_handler, error_handler=error_handler)
        return fut

    def getMainResource(self, contact_jid, profile_key="@DEFAULT@"):
        loop = asyncio.get_running_loop()
        fut = loop.create_future()
        reply_handler = lambda ret=None: loop.call_soon_threadsafe(fut.set_result, ret)
        error_handler = lambda err: loop.call_soon_threadsafe(fut.set_exception, dbus_to_bridge_exception(err))
        self.db_core_iface.getMainResource(contact_jid, profile_key, timeout=const_TIMEOUT, reply_handler=reply_handler, error_handler=error_handler)
        return fut

    def getParamA(self, name, category, attribute="value", profile_key="@DEFAULT@"):
        loop = asyncio.get_running_loop()
        fut = loop.create_future()
        reply_handler = lambda ret=None: loop.call_soon_threadsafe(fut.set_result, ret)
        error_handler = lambda err: loop.call_soon_threadsafe(fut.set_exception, dbus_to_bridge_exception(err))
        self.db_core_iface.getParamA(name, category, attribute, profile_key, timeout=const_TIMEOUT, reply_handler=reply_handler, error_handler=error_handler)
        return fut

    def getParamsCategories(self):
        loop = asyncio.get_running_loop()
        fut = loop.create_future()
        reply_handler = lambda ret=None: loop.call_soon_threadsafe(fut.set_result, ret)
        error_handler = lambda err: loop.call_soon_threadsafe(fut.set_exception, dbus_to_bridge_exception(err))
        self.db_core_iface.getParamsCategories(timeout=const_TIMEOUT, reply_handler=reply_handler, error_handler=error_handler)
        return fut

    def getParamsUI(self, security_limit=-1, app='', extra='', profile_key="@DEFAULT@"):
        loop = asyncio.get_running_loop()
        fut = loop.create_future()
        reply_handler = lambda ret=None: loop.call_soon_threadsafe(fut.set_result, ret)
        error_handler = lambda err: loop.call_soon_threadsafe(fut.set_exception, dbus_to_bridge_exception(err))
        self.db_core_iface.getParamsUI(security_limit, app, extra, profile_key, timeout=const_TIMEOUT, reply_handler=reply_handler, error_handler=error_handler)
        return fut

    def getPresenceStatuses(self, profile_key="@DEFAULT@"):
        loop = asyncio.get_running_loop()
        fut = loop.create_future()
        reply_handler = lambda ret=None: loop.call_soon_threadsafe(fut.set_result, ret)
        error_handler = lambda err: loop.call_soon_threadsafe(fut.set_exception, dbus_to_bridge_exception(err))
        self.db_core_iface.getPresenceStatuses(profile_key, timeout=const_TIMEOUT, reply_handler=reply_handler, error_handler=error_handler)
        return fut

    def getReady(self):
        loop = asyncio.get_running_loop()
        fut = loop.create_future()
        reply_handler = lambda ret=None: loop.call_soon_threadsafe(fut.set_result, ret)
        error_handler = lambda err: loop.call_soon_threadsafe(fut.set_exception, dbus_to_bridge_exception(err))
        self.db_core_iface.getReady(timeout=const_TIMEOUT, reply_handler=reply_handler, error_handler=error_handler)
        return fut

    def getVersion(self):
        loop = asyncio.get_running_loop()
        fut = loop.create_future()
        reply_handler = lambda ret=None: loop.call_soon_threadsafe(fut.set_result, ret)
        error_handler = lambda err: loop.call_soon_threadsafe(fut.set_exception, dbus_to_bridge_exception(err))
        self.db_core_iface.getVersion(timeout=const_TIMEOUT, reply_handler=reply_handler, error_handler=error_handler)
        return fut

    def getWaitingSub(self, profile_key="@DEFAULT@"):
        loop = asyncio.get_running_loop()
        fut = loop.create_future()
        reply_handler = lambda ret=None: loop.call_soon_threadsafe(fut.set_result, ret)
        error_handler = lambda err: loop.call_soon_threadsafe(fut.set_exception, dbus_to_bridge_exception(err))
        self.db_core_iface.getWaitingSub(profile_key, timeout=const_TIMEOUT, reply_handler=reply_handler, error_handler=error_handler)
        return fut

    def historyGet(self, from_jid, to_jid, limit, between=True, filters='', profile="@NONE@"):
        loop = asyncio.get_running_loop()
        fut = loop.create_future()
        reply_handler = lambda ret=None: loop.call_soon_threadsafe(fut.set_result, ret)
        error_handler = lambda err: loop.call_soon_threadsafe(fut.set_exception, dbus_to_bridge_exception(err))
        self.db_core_iface.historyGet(from_jid, to_jid, limit, between, filters, profile, timeout=const_TIMEOUT, reply_handler=reply_handler, error_handler=error_handler)
        return fut

    def imageCheck(self, arg_0):
        loop = asyncio.get_running_loop()
        fut = loop.create_future()
        reply_handler = lambda ret=None: loop.call_soon_threadsafe(fut.set_result, ret)
        error_handler = lambda err: loop.call_soon_threadsafe(fut.set_exception, dbus_to_bridge_exception(err))
        self.db_core_iface.imageCheck(arg_0, timeout=const_TIMEOUT, reply_handler=reply_handler, error_handler=error_handler)
        return fut

    def imageConvert(self, source, dest, arg_2, extra):
        loop = asyncio.get_running_loop()
        fut = loop.create_future()
        reply_handler = lambda ret=None: loop.call_soon_threadsafe(fut.set_result, ret)
        error_handler = lambda err: loop.call_soon_threadsafe(fut.set_exception, dbus_to_bridge_exception(err))
        self.db_core_iface.imageConvert(source, dest, arg_2, extra, timeout=const_TIMEOUT, reply_handler=reply_handler, error_handler=error_handler)
        return fut

    def imageGeneratePreview(self, image_path, profile_key):
        loop = asyncio.get_running_loop()
        fut = loop.create_future()
        reply_handler = lambda ret=None: loop.call_soon_threadsafe(fut.set_result, ret)
        error_handler = lambda err: loop.call_soon_threadsafe(fut.set_exception, dbus_to_bridge_exception(err))
        self.db_core_iface.imageGeneratePreview(image_path, profile_key, timeout=const_TIMEOUT, reply_handler=reply_handler, error_handler=error_handler)
        return fut

    def imageResize(self, image_path, width, height):
        loop = asyncio.get_running_loop()
        fut = loop.create_future()
        reply_handler = lambda ret=None: loop.call_soon_threadsafe(fut.set_result, ret)
        error_handler = lambda err: loop.call_soon_threadsafe(fut.set_exception, dbus_to_bridge_exception(err))
        self.db_core_iface.imageResize(image_path, width, height, timeout=const_TIMEOUT, reply_handler=reply_handler, error_handler=error_handler)
        return fut

    def isConnected(self, profile_key="@DEFAULT@"):
        loop = asyncio.get_running_loop()
        fut = loop.create_future()
        reply_handler = lambda ret=None: loop.call_soon_threadsafe(fut.set_result, ret)
        error_handler = lambda err: loop.call_soon_threadsafe(fut.set_exception, dbus_to_bridge_exception(err))
        self.db_core_iface.isConnected(profile_key, timeout=const_TIMEOUT, reply_handler=reply_handler, error_handler=error_handler)
        return fut

    def launchAction(self, callback_id, data, profile_key="@DEFAULT@"):
        loop = asyncio.get_running_loop()
        fut = loop.create_future()
        reply_handler = lambda ret=None: loop.call_soon_threadsafe(fut.set_result, ret)
        error_handler = lambda err: loop.call_soon_threadsafe(fut.set_exception, dbus_to_bridge_exception(err))
        self.db_core_iface.launchAction(callback_id, data, profile_key, timeout=const_TIMEOUT, reply_handler=reply_handler, error_handler=error_handler)
        return fut

    def loadParamsTemplate(self, filename):
        loop = asyncio.get_running_loop()
        fut = loop.create_future()
        reply_handler = lambda ret=None: loop.call_soon_threadsafe(fut.set_result, ret)
        error_handler = lambda err: loop.call_soon_threadsafe(fut.set_exception, dbus_to_bridge_exception(err))
        self.db_core_iface.loadParamsTemplate(filename, timeout=const_TIMEOUT, reply_handler=reply_handler, error_handler=error_handler)
        return fut

    def menuHelpGet(self, menu_id, language):
        loop = asyncio.get_running_loop()
        fut = loop.create_future()
        reply_handler = lambda ret=None: loop.call_soon_threadsafe(fut.set_result, ret)
        error_handler = lambda err: loop.call_soon_threadsafe(fut.set_exception, dbus_to_bridge_exception(err))
        self.db_core_iface.menuHelpGet(menu_id, language, timeout=const_TIMEOUT, reply_handler=reply_handler, error_handler=error_handler)
        return fut

    def menuLaunch(self, menu_type, path, data, security_limit, profile_key):
        loop = asyncio.get_running_loop()
        fut = loop.create_future()
        reply_handler = lambda ret=None: loop.call_soon_threadsafe(fut.set_result, ret)
        error_handler = lambda err: loop.call_soon_threadsafe(fut.set_exception, dbus_to_bridge_exception(err))
        self.db_core_iface.menuLaunch(menu_type, path, data, security_limit, profile_key, timeout=const_TIMEOUT, reply_handler=reply_handler, error_handler=error_handler)
        return fut

    def menusGet(self, language, security_limit):
        loop = asyncio.get_running_loop()
        fut = loop.create_future()
        reply_handler = lambda ret=None: loop.call_soon_threadsafe(fut.set_result, ret)
        error_handler = lambda err: loop.call_soon_threadsafe(fut.set_exception, dbus_to_bridge_exception(err))
        self.db_core_iface.menusGet(language, security_limit, timeout=const_TIMEOUT, reply_handler=reply_handler, error_handler=error_handler)
        return fut

    def messageEncryptionGet(self, to_jid, profile_key):
        loop = asyncio.get_running_loop()
        fut = loop.create_future()
        reply_handler = lambda ret=None: loop.call_soon_threadsafe(fut.set_result, ret)
        error_handler = lambda err: loop.call_soon_threadsafe(fut.set_exception, dbus_to_bridge_exception(err))
        self.db_core_iface.messageEncryptionGet(to_jid, profile_key, timeout=const_TIMEOUT, reply_handler=reply_handler, error_handler=error_handler)
        return fut

    def messageEncryptionStart(self, to_jid, namespace='', replace=False, profile_key="@NONE@"):
        loop = asyncio.get_running_loop()
        fut = loop.create_future()
        reply_handler = lambda ret=None: loop.call_soon_threadsafe(fut.set_result, ret)
        error_handler = lambda err: loop.call_soon_threadsafe(fut.set_exception, dbus_to_bridge_exception(err))
        self.db_core_iface.messageEncryptionStart(to_jid, namespace, replace, profile_key, timeout=const_TIMEOUT, reply_handler=reply_handler, error_handler=error_handler)
        return fut

    def messageEncryptionStop(self, to_jid, profile_key):
        loop = asyncio.get_running_loop()
        fut = loop.create_future()
        reply_handler = lambda ret=None: loop.call_soon_threadsafe(fut.set_result, ret)
        error_handler = lambda err: loop.call_soon_threadsafe(fut.set_exception, dbus_to_bridge_exception(err))
        self.db_core_iface.messageEncryptionStop(to_jid, profile_key, timeout=const_TIMEOUT, reply_handler=reply_handler, error_handler=error_handler)
        return fut

    def messageSend(self, to_jid, message, subject={}, mess_type="auto", extra={}, profile_key="@NONE@"):
        loop = asyncio.get_running_loop()
        fut = loop.create_future()
        reply_handler = lambda ret=None: loop.call_soon_threadsafe(fut.set_result, ret)
        error_handler = lambda err: loop.call_soon_threadsafe(fut.set_exception, dbus_to_bridge_exception(err))
        self.db_core_iface.messageSend(to_jid, message, subject, mess_type, extra, profile_key, timeout=const_TIMEOUT, reply_handler=reply_handler, error_handler=error_handler)
        return fut

    def namespacesGet(self):
        loop = asyncio.get_running_loop()
        fut = loop.create_future()
        reply_handler = lambda ret=None: loop.call_soon_threadsafe(fut.set_result, ret)
        error_handler = lambda err: loop.call_soon_threadsafe(fut.set_exception, dbus_to_bridge_exception(err))
        self.db_core_iface.namespacesGet(timeout=const_TIMEOUT, reply_handler=reply_handler, error_handler=error_handler)
        return fut

    def paramsRegisterApp(self, xml, security_limit=-1, app=''):
        loop = asyncio.get_running_loop()
        fut = loop.create_future()
        reply_handler = lambda ret=None: loop.call_soon_threadsafe(fut.set_result, ret)
        error_handler = lambda err: loop.call_soon_threadsafe(fut.set_exception, dbus_to_bridge_exception(err))
        self.db_core_iface.paramsRegisterApp(xml, security_limit, app, timeout=const_TIMEOUT, reply_handler=reply_handler, error_handler=error_handler)
        return fut

    def privateDataDelete(self, namespace, key, arg_2):
        loop = asyncio.get_running_loop()
        fut = loop.create_future()
        reply_handler = lambda ret=None: loop.call_soon_threadsafe(fut.set_result, ret)
        error_handler = lambda err: loop.call_soon_threadsafe(fut.set_exception, dbus_to_bridge_exception(err))
        self.db_core_iface.privateDataDelete(namespace, key, arg_2, timeout=const_TIMEOUT, reply_handler=reply_handler, error_handler=error_handler)
        return fut

    def privateDataGet(self, namespace, key, profile_key):
        loop = asyncio.get_running_loop()
        fut = loop.create_future()
        reply_handler = lambda ret=None: loop.call_soon_threadsafe(fut.set_result, ret)
        error_handler = lambda err: loop.call_soon_threadsafe(fut.set_exception, dbus_to_bridge_exception(err))
        self.db_core_iface.privateDataGet(namespace, key, profile_key, timeout=const_TIMEOUT, reply_handler=reply_handler, error_handler=error_handler)
        return fut

    def privateDataSet(self, namespace, key, data, profile_key):
        loop = asyncio.get_running_loop()
        fut = loop.create_future()
        reply_handler = lambda ret=None: loop.call_soon_threadsafe(fut.set_result, ret)
        error_handler = lambda err: loop.call_soon_threadsafe(fut.set_exception, dbus_to_bridge_exception(err))
        self.db_core_iface.privateDataSet(namespace, key, data, profile_key, timeout=const_TIMEOUT, reply_handler=reply_handler, error_handler=error_handler)
        return fut

    def profileCreate(self, profile, password='', component=''):
        loop = asyncio.get_running_loop()
        fut = loop.create_future()
        reply_handler = lambda ret=None: loop.call_soon_threadsafe(fut.set_result, ret)
        error_handler = lambda err: loop.call_soon_threadsafe(fut.set_exception, dbus_to_bridge_exception(err))
        self.db_core_iface.profileCreate(profile, password, component, timeout=const_TIMEOUT, reply_handler=reply_handler, error_handler=error_handler)
        return fut

    def profileIsSessionStarted(self, profile_key="@DEFAULT@"):
        loop = asyncio.get_running_loop()
        fut = loop.create_future()
        reply_handler = lambda ret=None: loop.call_soon_threadsafe(fut.set_result, ret)
        error_handler = lambda err: loop.call_soon_threadsafe(fut.set_exception, dbus_to_bridge_exception(err))
        self.db_core_iface.profileIsSessionStarted(profile_key, timeout=const_TIMEOUT, reply_handler=reply_handler, error_handler=error_handler)
        return fut

    def profileNameGet(self, profile_key="@DEFAULT@"):
        loop = asyncio.get_running_loop()
        fut = loop.create_future()
        reply_handler = lambda ret=None: loop.call_soon_threadsafe(fut.set_result, ret)
        error_handler = lambda err: loop.call_soon_threadsafe(fut.set_exception, dbus_to_bridge_exception(err))
        self.db_core_iface.profileNameGet(profile_key, timeout=const_TIMEOUT, reply_handler=reply_handler, error_handler=error_handler)
        return fut

    def profileSetDefault(self, profile):
        loop = asyncio.get_running_loop()
        fut = loop.create_future()
        reply_handler = lambda ret=None: loop.call_soon_threadsafe(fut.set_result, ret)
        error_handler = lambda err: loop.call_soon_threadsafe(fut.set_exception, dbus_to_bridge_exception(err))
        self.db_core_iface.profileSetDefault(profile, timeout=const_TIMEOUT, reply_handler=reply_handler, error_handler=error_handler)
        return fut

    def profileStartSession(self, password='', profile_key="@DEFAULT@"):
        loop = asyncio.get_running_loop()
        fut = loop.create_future()
        reply_handler = lambda ret=None: loop.call_soon_threadsafe(fut.set_result, ret)
        error_handler = lambda err: loop.call_soon_threadsafe(fut.set_exception, dbus_to_bridge_exception(err))
        self.db_core_iface.profileStartSession(password, profile_key, timeout=const_TIMEOUT, reply_handler=reply_handler, error_handler=error_handler)
        return fut

    def profilesListGet(self, clients=True, components=False):
        loop = asyncio.get_running_loop()
        fut = loop.create_future()
        reply_handler = lambda ret=None: loop.call_soon_threadsafe(fut.set_result, ret)
        error_handler = lambda err: loop.call_soon_threadsafe(fut.set_exception, dbus_to_bridge_exception(err))
        self.db_core_iface.profilesListGet(clients, components, timeout=const_TIMEOUT, reply_handler=reply_handler, error_handler=error_handler)
        return fut

    def progressGet(self, id, profile):
        loop = asyncio.get_running_loop()
        fut = loop.create_future()
        reply_handler = lambda ret=None: loop.call_soon_threadsafe(fut.set_result, ret)
        error_handler = lambda err: loop.call_soon_threadsafe(fut.set_exception, dbus_to_bridge_exception(err))
        self.db_core_iface.progressGet(id, profile, timeout=const_TIMEOUT, reply_handler=reply_handler, error_handler=error_handler)
        return fut

    def progressGetAll(self, profile):
        loop = asyncio.get_running_loop()
        fut = loop.create_future()
        reply_handler = lambda ret=None: loop.call_soon_threadsafe(fut.set_result, ret)
        error_handler = lambda err: loop.call_soon_threadsafe(fut.set_exception, dbus_to_bridge_exception(err))
        self.db_core_iface.progressGetAll(profile, timeout=const_TIMEOUT, reply_handler=reply_handler, error_handler=error_handler)
        return fut

    def progressGetAllMetadata(self, profile):
        loop = asyncio.get_running_loop()
        fut = loop.create_future()
        reply_handler = lambda ret=None: loop.call_soon_threadsafe(fut.set_result, ret)
        error_handler = lambda err: loop.call_soon_threadsafe(fut.set_exception, dbus_to_bridge_exception(err))
        self.db_core_iface.progressGetAllMetadata(profile, timeout=const_TIMEOUT, reply_handler=reply_handler, error_handler=error_handler)
        return fut

    def rosterResync(self, profile_key="@DEFAULT@"):
        loop = asyncio.get_running_loop()
        fut = loop.create_future()
        reply_handler = lambda ret=None: loop.call_soon_threadsafe(fut.set_result, ret)
        error_handler = lambda err: loop.call_soon_threadsafe(fut.set_exception, dbus_to_bridge_exception(err))
        self.db_core_iface.rosterResync(profile_key, timeout=const_TIMEOUT, reply_handler=reply_handler, error_handler=error_handler)
        return fut

    def saveParamsTemplate(self, filename):
        loop = asyncio.get_running_loop()
        fut = loop.create_future()
        reply_handler = lambda ret=None: loop.call_soon_threadsafe(fut.set_result, ret)
        error_handler = lambda err: loop.call_soon_threadsafe(fut.set_exception, dbus_to_bridge_exception(err))
        self.db_core_iface.saveParamsTemplate(filename, timeout=const_TIMEOUT, reply_handler=reply_handler, error_handler=error_handler)
        return fut

    def sessionInfosGet(self, profile_key):
        loop = asyncio.get_running_loop()
        fut = loop.create_future()
        reply_handler = lambda ret=None: loop.call_soon_threadsafe(fut.set_result, ret)
        error_handler = lambda err: loop.call_soon_threadsafe(fut.set_exception, dbus_to_bridge_exception(err))
        self.db_core_iface.sessionInfosGet(profile_key, timeout=const_TIMEOUT, reply_handler=reply_handler, error_handler=error_handler)
        return fut

    def setParam(self, name, value, category, security_limit=-1, profile_key="@DEFAULT@"):
        loop = asyncio.get_running_loop()
        fut = loop.create_future()
        reply_handler = lambda ret=None: loop.call_soon_threadsafe(fut.set_result, ret)
        error_handler = lambda err: loop.call_soon_threadsafe(fut.set_exception, dbus_to_bridge_exception(err))
        self.db_core_iface.setParam(name, value, category, security_limit, profile_key, timeout=const_TIMEOUT, reply_handler=reply_handler, error_handler=error_handler)
        return fut

    def setPresence(self, to_jid='', show='', statuses={}, profile_key="@DEFAULT@"):
        loop = asyncio.get_running_loop()
        fut = loop.create_future()
        reply_handler = lambda ret=None: loop.call_soon_threadsafe(fut.set_result, ret)
        error_handler = lambda err: loop.call_soon_threadsafe(fut.set_exception, dbus_to_bridge_exception(err))
        self.db_core_iface.setPresence(to_jid, show, statuses, profile_key, timeout=const_TIMEOUT, reply_handler=reply_handler, error_handler=error_handler)
        return fut

    def subscription(self, sub_type, entity, profile_key="@DEFAULT@"):
        loop = asyncio.get_running_loop()
        fut = loop.create_future()
        reply_handler = lambda ret=None: loop.call_soon_threadsafe(fut.set_result, ret)
        error_handler = lambda err: loop.call_soon_threadsafe(fut.set_exception, dbus_to_bridge_exception(err))
        self.db_core_iface.subscription(sub_type, entity, profile_key, timeout=const_TIMEOUT, reply_handler=reply_handler, error_handler=error_handler)
        return fut

    def updateContact(self, entity_jid, name, groups, profile_key="@DEFAULT@"):
        loop = asyncio.get_running_loop()
        fut = loop.create_future()
        reply_handler = lambda ret=None: loop.call_soon_threadsafe(fut.set_result, ret)
        error_handler = lambda err: loop.call_soon_threadsafe(fut.set_exception, dbus_to_bridge_exception(err))
        self.db_core_iface.updateContact(entity_jid, name, groups, profile_key, timeout=const_TIMEOUT, reply_handler=reply_handler, error_handler=error_handler)
        return fut
