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
from logging import getLogger
from functools import partial
from pathlib import Path
from twisted.spread import pb
from twisted.internet import reactor, defer
from twisted.internet.error import ConnectionRefusedError, ConnectError
from sat.core import exceptions
from sat.tools import config
from sat_frontends.bridge.bridge_frontend import BridgeException

log = getLogger(__name__)


class SignalsHandler(pb.Referenceable):
    def __getattr__(self, name):
        if name.startswith("remote_"):
            log.debug("calling an unregistered signal: {name}".format(name=name[7:]))
            return lambda *args, **kwargs: None

        else:
            raise AttributeError(name)

    def register_signal(self, name, handler, iface="core"):
        log.debug("registering signal {name}".format(name=name))
        method_name = "remote_" + name
        try:
            self.__getattribute__(method_name)
        except AttributeError:
            pass
        else:
            raise exceptions.InternalError(
                "{name} signal handler has been registered twice".format(
                    name=method_name
                )
            )
        setattr(self, method_name, handler)


class Bridge(object):

    def __init__(self):
        self.signals_handler = SignalsHandler()

    def __getattr__(self, name):
        return partial(self.call, name)

    def _generic_errback(self, err):
        log.error(f"bridge error: {err}")

    def _errback(self, failure_, ori_errback):
        """Convert Failure to BridgeException"""
        ori_errback(
            BridgeException(
                name=failure_.type.decode('utf-8'),
                message=str(failure_.value)
            )
        )

    def remoteCallback(self, result, callback):
        """call callback with argument or None

        if result is not None not argument is used,
        else result is used as argument
        @param result: remote call result
        @param callback(callable): method to call on result
        """
        if result is None:
            callback()
        else:
            callback(result)

    def call(self, name, *args, **kwargs):
        """call a remote method

        @param name(str): name of the bridge method
        @param args(list): arguments
            may contain callback and errback as last 2 items
        @param kwargs(dict): keyword arguments
            may contain callback and errback
        """
        callback = errback = None
        if kwargs:
            try:
                callback = kwargs.pop("callback")
            except KeyError:
                pass
            try:
                errback = kwargs.pop("errback")
            except KeyError:
                pass
        elif len(args) >= 2 and callable(args[-1]) and callable(args[-2]):
            errback = args.pop()
            callback = args.pop()
        d = self.root.callRemote(name, *args, **kwargs)
        if callback is not None:
            d.addCallback(self.remoteCallback, callback)
        if errback is not None:
            d.addErrback(errback)

    def _initBridgeEb(self, failure_):
        log.error("Can't init bridge: {msg}".format(msg=failure_))
        return failure_

    def _set_root(self, root):
        """set remote root object

        bridge will then be initialised
        """
        self.root = root
        d = root.callRemote("initBridge", self.signals_handler)
        d.addErrback(self._initBridgeEb)
        return d

    def getRootObjectEb(self, failure_):
        """Call errback with appropriate bridge error"""
        if failure_.check(ConnectionRefusedError, ConnectError):
            raise exceptions.BridgeExceptionNoService
        else:
            raise failure_

    def bridgeConnect(self, callback, errback):
        factory = pb.PBClientFactory()
        conf = config.parseMainConf()
        getConf = partial(config.getConf, conf, "bridge_pb", "")
        conn_type = getConf("connection_type", "unix_socket")
        if conn_type == "unix_socket":
            local_dir = Path(config.getConfig(conf, "", "local_dir")).resolve()
            socket_path = local_dir / "bridge_pb"
            reactor.connectUNIX(str(socket_path), factory)
        elif conn_type == "socket":
            host = getConf("host", "localhost")
            port = int(getConf("port", 8789))
            reactor.connectTCP(host, port, factory)
        else:
            raise ValueError(f"Unknown pb connection type: {conn_type!r}")
        d = factory.getRootObject()
        d.addCallback(self._set_root)
        if callback is not None:
            d.addCallback(lambda __: callback())
        d.addErrback(self.getRootObjectEb)
        if errback is not None:
            d.addErrback(lambda failure_: errback(failure_.value))
        return d

    def register_signal(self, functionName, handler, iface="core"):
        self.signals_handler.register_signal(functionName, handler, iface)


##METHODS_PART##

class AIOSignalsHandler(SignalsHandler):

    def register_signal(self, name, handler, iface="core"):
        async_handler = lambda *args, **kwargs: defer.Deferred.fromFuture(
            asyncio.ensure_future(handler(*args, **kwargs)))
        return super().register_signal(name, async_handler, iface)


class AIOBridge(Bridge):

    def __init__(self):
        self.signals_handler = AIOSignalsHandler()

    def _errback(self, failure_):
        """Convert Failure to BridgeException"""
        raise BridgeException(
            name=failure_.type.decode('utf-8'),
            message=str(failure_.value)
            )

    def call(self, name, *args, **kwargs):
        d = self.root.callRemote(name, *args, *kwargs)
        d.addErrback(self._errback)
        return d.asFuture(asyncio.get_event_loop())

    async def bridgeConnect(self):
        d = super().bridgeConnect(callback=None, errback=None)
        return await d.asFuture(asyncio.get_event_loop())

##ASYNC_METHODS_PART##
