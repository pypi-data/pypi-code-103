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


import dataclasses
from functools import partial
from pathlib import Path
from twisted.spread import jelly, pb
from twisted.internet import reactor
from sat.core.log import getLogger
from sat.tools import config

log = getLogger(__name__)


## jelly hack
# we monkey patch jelly to handle namedtuple
ori_jelly = jelly._Jellier.jelly


def fixed_jelly(self, obj):
    """this method fix handling of namedtuple"""
    if isinstance(obj, tuple) and not obj is tuple:
        obj = tuple(obj)
    return ori_jelly(self, obj)


jelly._Jellier.jelly = fixed_jelly


@dataclasses.dataclass(eq=False)
class HandlerWrapper:
    # we use a wrapper to keep signals handlers because RemoteReference doesn't support
    # comparison (other than equality), making it unusable with a list
    handler: pb.RemoteReference


class PBRoot(pb.Root):
    def __init__(self):
        self.signals_handlers = []

    def remote_initBridge(self, signals_handler):
        self.signals_handlers.append(HandlerWrapper(signals_handler))
        log.info("registered signal handler")

    def sendSignalEb(self, failure_, signal_name):
        if not failure_.check(pb.PBConnectionLost):
            log.error(
                f"Error while sending signal {signal_name}: {failure_}",
            )

    def sendSignal(self, name, args, kwargs):
        to_remove = []
        for wrapper in self.signals_handlers:
            handler = wrapper.handler
            try:
                d = handler.callRemote(name, *args, **kwargs)
            except pb.DeadReferenceError:
                to_remove.append(wrapper)
            else:
                d.addErrback(self.sendSignalEb, name)
        if to_remove:
            for wrapper in to_remove:
                log.debug("Removing signal handler for dead frontend")
                self.signals_handlers.remove(wrapper)

    def _bridgeDeactivateSignals(self):
        if hasattr(self, "signals_paused"):
            log.warning("bridge signals already deactivated")
            if self.signals_handler:
                self.signals_paused.extend(self.signals_handler)
        else:
            self.signals_paused = self.signals_handlers
        self.signals_handlers = []
        log.debug("bridge signals have been deactivated")

    def _bridgeReactivateSignals(self):
        try:
            self.signals_handlers = self.signals_paused
        except AttributeError:
            log.debug("signals were already activated")
        else:
            del self.signals_paused
            log.debug("bridge signals have been reactivated")

##METHODS_PART##


class Bridge(object):
    def __init__(self):
        log.info("Init Perspective Broker...")
        self.root = PBRoot()
        conf = config.parseMainConf()
        getConf = partial(config.getConf, conf, "bridge_pb", "")
        conn_type = getConf("connection_type", "unix_socket")
        if conn_type == "unix_socket":
            local_dir = Path(config.getConfig(conf, "", "local_dir")).resolve()
            socket_path = local_dir / "bridge_pb"
            log.info(f"using UNIX Socket at {socket_path}")
            reactor.listenUNIX(
                str(socket_path), pb.PBServerFactory(self.root), mode=0o600
            )
        elif conn_type == "socket":
            port = int(getConf("port", 8789))
            log.info(f"using TCP Socket at port {port}")
            reactor.listenTCP(port, pb.PBServerFactory(self.root))
        else:
            raise ValueError(f"Unknown pb connection type: {conn_type!r}")

    def sendSignal(self, name, *args, **kwargs):
        self.root.sendSignal(name, args, kwargs)

    def remote_initBridge(self, signals_handler):
        self.signals_handlers.append(signals_handler)
        log.info("registered signal handler")

    def register_method(self, name, callback):
        log.debug("registering PB bridge method [%s]" % name)
        setattr(self.root, "remote_" + name, callback)
        #  self.root.register_method(name, callback)

    def addMethod(
            self, name, int_suffix, in_sign, out_sign, method, async_=False, doc={}
    ):
        """Dynamically add a method to PB Bridge"""
        # FIXME: doc parameter is kept only temporary, the time to remove it from calls
        log.debug("Adding method {name} to PB bridge".format(name=name))
        self.register_method(name, method)

    def addSignal(self, name, int_suffix, signature, doc={}):
        log.debug("Adding signal {name} to PB bridge".format(name=name))
        setattr(
            self, name, lambda *args, **kwargs: self.sendSignal(name, *args, **kwargs)
        )

    def bridgeDeactivateSignals(self):
        """Stop sending signals to bridge

        Mainly used for mobile frontends, when the frontend is paused
        """
        self.root._bridgeDeactivateSignals()

    def bridgeReactivateSignals(self):
        """Send again signals to bridge

        Should only be used after bridgeDeactivateSignals has been called
        """
        self.root._bridgeReactivateSignals()

    def _debug(self, action, params, profile):
        self.sendSignal("_debug", action, params, profile)

    def actionNew(self, action_data, id, security_limit, profile):
        self.sendSignal("actionNew", action_data, id, security_limit, profile)

    def connected(self, jid_s, profile):
        self.sendSignal("connected", jid_s, profile)

    def contactDeleted(self, entity_jid, profile):
        self.sendSignal("contactDeleted", entity_jid, profile)

    def disconnected(self, profile):
        self.sendSignal("disconnected", profile)

    def entityDataUpdated(self, jid, name, value, profile):
        self.sendSignal("entityDataUpdated", jid, name, value, profile)

    def messageEncryptionStarted(self, to_jid, encryption_data, profile_key):
        self.sendSignal("messageEncryptionStarted", to_jid, encryption_data, profile_key)

    def messageEncryptionStopped(self, to_jid, encryption_data, profile_key):
        self.sendSignal("messageEncryptionStopped", to_jid, encryption_data, profile_key)

    def messageNew(self, uid, timestamp, from_jid, to_jid, message, subject, mess_type, extra, profile):
        self.sendSignal("messageNew", uid, timestamp, from_jid, to_jid, message, subject, mess_type, extra, profile)

    def newContact(self, contact_jid, attributes, groups, profile):
        self.sendSignal("newContact", contact_jid, attributes, groups, profile)

    def paramUpdate(self, name, value, category, profile):
        self.sendSignal("paramUpdate", name, value, category, profile)

    def presenceUpdate(self, entity_jid, show, priority, statuses, profile):
        self.sendSignal("presenceUpdate", entity_jid, show, priority, statuses, profile)

    def progressError(self, id, error, profile):
        self.sendSignal("progressError", id, error, profile)

    def progressFinished(self, id, metadata, profile):
        self.sendSignal("progressFinished", id, metadata, profile)

    def progressStarted(self, id, metadata, profile):
        self.sendSignal("progressStarted", id, metadata, profile)

    def subscribe(self, sub_type, entity_jid, profile):
        self.sendSignal("subscribe", sub_type, entity_jid, profile)
