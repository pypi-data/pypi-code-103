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

##METHODS_PART##

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

##ASYNC_METHODS_PART##
