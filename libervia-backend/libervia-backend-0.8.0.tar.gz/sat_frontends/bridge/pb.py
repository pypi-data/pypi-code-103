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


    def actionsGet(self, profile_key="@DEFAULT@", callback=None, errback=None):
        d = self.root.callRemote("actionsGet", profile_key)
        if callback is not None:
            d.addCallback(callback)
        if errback is None:
            d.addErrback(self._generic_errback)
        else:
            d.addErrback(self._errback, ori_errback=errback)

    def addContact(self, entity_jid, profile_key="@DEFAULT@", callback=None, errback=None):
        d = self.root.callRemote("addContact", entity_jid, profile_key)
        if callback is not None:
            d.addCallback(lambda __: callback())
        if errback is None:
            d.addErrback(self._generic_errback)
        else:
            d.addErrback(self._errback, ori_errback=errback)

    def asyncDeleteProfile(self, profile, callback=None, errback=None):
        d = self.root.callRemote("asyncDeleteProfile", profile)
        if callback is not None:
            d.addCallback(lambda __: callback())
        if errback is None:
            d.addErrback(self._generic_errback)
        else:
            d.addErrback(self._errback, ori_errback=errback)

    def asyncGetParamA(self, name, category, attribute="value", security_limit=-1, profile_key="@DEFAULT@", callback=None, errback=None):
        d = self.root.callRemote("asyncGetParamA", name, category, attribute, security_limit, profile_key)
        if callback is not None:
            d.addCallback(callback)
        if errback is None:
            d.addErrback(self._generic_errback)
        else:
            d.addErrback(self._errback, ori_errback=errback)

    def asyncGetParamsValuesFromCategory(self, category, security_limit=-1, app="", extra="", profile_key="@DEFAULT@", callback=None, errback=None):
        d = self.root.callRemote("asyncGetParamsValuesFromCategory", category, security_limit, app, extra, profile_key)
        if callback is not None:
            d.addCallback(callback)
        if errback is None:
            d.addErrback(self._generic_errback)
        else:
            d.addErrback(self._errback, ori_errback=errback)

    def connect(self, profile_key="@DEFAULT@", password='', options={}, callback=None, errback=None):
        d = self.root.callRemote("connect", profile_key, password, options)
        if callback is not None:
            d.addCallback(callback)
        if errback is None:
            d.addErrback(self._generic_errback)
        else:
            d.addErrback(self._errback, ori_errback=errback)

    def contactGet(self, arg_0, profile_key="@DEFAULT@", callback=None, errback=None):
        d = self.root.callRemote("contactGet", arg_0, profile_key)
        if callback is not None:
            d.addCallback(callback)
        if errback is None:
            d.addErrback(self._generic_errback)
        else:
            d.addErrback(self._errback, ori_errback=errback)

    def delContact(self, entity_jid, profile_key="@DEFAULT@", callback=None, errback=None):
        d = self.root.callRemote("delContact", entity_jid, profile_key)
        if callback is not None:
            d.addCallback(lambda __: callback())
        if errback is None:
            d.addErrback(self._generic_errback)
        else:
            d.addErrback(self._errback, ori_errback=errback)

    def devicesInfosGet(self, bare_jid, profile_key, callback=None, errback=None):
        d = self.root.callRemote("devicesInfosGet", bare_jid, profile_key)
        if callback is not None:
            d.addCallback(callback)
        if errback is None:
            d.addErrback(self._generic_errback)
        else:
            d.addErrback(self._errback, ori_errback=errback)

    def discoFindByFeatures(self, namespaces, identities, bare_jid=False, service=True, roster=True, own_jid=True, local_device=False, profile_key="@DEFAULT@", callback=None, errback=None):
        d = self.root.callRemote("discoFindByFeatures", namespaces, identities, bare_jid, service, roster, own_jid, local_device, profile_key)
        if callback is not None:
            d.addCallback(callback)
        if errback is None:
            d.addErrback(self._generic_errback)
        else:
            d.addErrback(self._errback, ori_errback=errback)

    def discoInfos(self, entity_jid, node=u'', use_cache=True, profile_key="@DEFAULT@", callback=None, errback=None):
        d = self.root.callRemote("discoInfos", entity_jid, node, use_cache, profile_key)
        if callback is not None:
            d.addCallback(callback)
        if errback is None:
            d.addErrback(self._generic_errback)
        else:
            d.addErrback(self._errback, ori_errback=errback)

    def discoItems(self, entity_jid, node=u'', use_cache=True, profile_key="@DEFAULT@", callback=None, errback=None):
        d = self.root.callRemote("discoItems", entity_jid, node, use_cache, profile_key)
        if callback is not None:
            d.addCallback(callback)
        if errback is None:
            d.addErrback(self._generic_errback)
        else:
            d.addErrback(self._errback, ori_errback=errback)

    def disconnect(self, profile_key="@DEFAULT@", callback=None, errback=None):
        d = self.root.callRemote("disconnect", profile_key)
        if callback is not None:
            d.addCallback(lambda __: callback())
        if errback is None:
            d.addErrback(self._generic_errback)
        else:
            d.addErrback(self._errback, ori_errback=errback)

    def encryptionNamespaceGet(self, arg_0, callback=None, errback=None):
        d = self.root.callRemote("encryptionNamespaceGet", arg_0)
        if callback is not None:
            d.addCallback(callback)
        if errback is None:
            d.addErrback(self._generic_errback)
        else:
            d.addErrback(self._errback, ori_errback=errback)

    def encryptionPluginsGet(self, callback=None, errback=None):
        d = self.root.callRemote("encryptionPluginsGet")
        if callback is not None:
            d.addCallback(callback)
        if errback is None:
            d.addErrback(self._generic_errback)
        else:
            d.addErrback(self._errback, ori_errback=errback)

    def encryptionTrustUIGet(self, to_jid, namespace, profile_key, callback=None, errback=None):
        d = self.root.callRemote("encryptionTrustUIGet", to_jid, namespace, profile_key)
        if callback is not None:
            d.addCallback(callback)
        if errback is None:
            d.addErrback(self._generic_errback)
        else:
            d.addErrback(self._errback, ori_errback=errback)

    def getConfig(self, section, name, callback=None, errback=None):
        d = self.root.callRemote("getConfig", section, name)
        if callback is not None:
            d.addCallback(callback)
        if errback is None:
            d.addErrback(self._generic_errback)
        else:
            d.addErrback(self._errback, ori_errback=errback)

    def getContacts(self, profile_key="@DEFAULT@", callback=None, errback=None):
        d = self.root.callRemote("getContacts", profile_key)
        if callback is not None:
            d.addCallback(callback)
        if errback is None:
            d.addErrback(self._generic_errback)
        else:
            d.addErrback(self._errback, ori_errback=errback)

    def getContactsFromGroup(self, group, profile_key="@DEFAULT@", callback=None, errback=None):
        d = self.root.callRemote("getContactsFromGroup", group, profile_key)
        if callback is not None:
            d.addCallback(callback)
        if errback is None:
            d.addErrback(self._generic_errback)
        else:
            d.addErrback(self._errback, ori_errback=errback)

    def getEntitiesData(self, jids, keys, profile, callback=None, errback=None):
        d = self.root.callRemote("getEntitiesData", jids, keys, profile)
        if callback is not None:
            d.addCallback(callback)
        if errback is None:
            d.addErrback(self._generic_errback)
        else:
            d.addErrback(self._errback, ori_errback=errback)

    def getEntityData(self, jid, keys, profile, callback=None, errback=None):
        d = self.root.callRemote("getEntityData", jid, keys, profile)
        if callback is not None:
            d.addCallback(callback)
        if errback is None:
            d.addErrback(self._generic_errback)
        else:
            d.addErrback(self._errback, ori_errback=errback)

    def getFeatures(self, profile_key, callback=None, errback=None):
        d = self.root.callRemote("getFeatures", profile_key)
        if callback is not None:
            d.addCallback(callback)
        if errback is None:
            d.addErrback(self._generic_errback)
        else:
            d.addErrback(self._errback, ori_errback=errback)

    def getMainResource(self, contact_jid, profile_key="@DEFAULT@", callback=None, errback=None):
        d = self.root.callRemote("getMainResource", contact_jid, profile_key)
        if callback is not None:
            d.addCallback(callback)
        if errback is None:
            d.addErrback(self._generic_errback)
        else:
            d.addErrback(self._errback, ori_errback=errback)

    def getParamA(self, name, category, attribute="value", profile_key="@DEFAULT@", callback=None, errback=None):
        d = self.root.callRemote("getParamA", name, category, attribute, profile_key)
        if callback is not None:
            d.addCallback(callback)
        if errback is None:
            d.addErrback(self._generic_errback)
        else:
            d.addErrback(self._errback, ori_errback=errback)

    def getParamsCategories(self, callback=None, errback=None):
        d = self.root.callRemote("getParamsCategories")
        if callback is not None:
            d.addCallback(callback)
        if errback is None:
            d.addErrback(self._generic_errback)
        else:
            d.addErrback(self._errback, ori_errback=errback)

    def getParamsUI(self, security_limit=-1, app='', extra='', profile_key="@DEFAULT@", callback=None, errback=None):
        d = self.root.callRemote("getParamsUI", security_limit, app, extra, profile_key)
        if callback is not None:
            d.addCallback(callback)
        if errback is None:
            d.addErrback(self._generic_errback)
        else:
            d.addErrback(self._errback, ori_errback=errback)

    def getPresenceStatuses(self, profile_key="@DEFAULT@", callback=None, errback=None):
        d = self.root.callRemote("getPresenceStatuses", profile_key)
        if callback is not None:
            d.addCallback(callback)
        if errback is None:
            d.addErrback(self._generic_errback)
        else:
            d.addErrback(self._errback, ori_errback=errback)

    def getReady(self, callback=None, errback=None):
        d = self.root.callRemote("getReady")
        if callback is not None:
            d.addCallback(lambda __: callback())
        if errback is None:
            d.addErrback(self._generic_errback)
        else:
            d.addErrback(self._errback, ori_errback=errback)

    def getVersion(self, callback=None, errback=None):
        d = self.root.callRemote("getVersion")
        if callback is not None:
            d.addCallback(callback)
        if errback is None:
            d.addErrback(self._generic_errback)
        else:
            d.addErrback(self._errback, ori_errback=errback)

    def getWaitingSub(self, profile_key="@DEFAULT@", callback=None, errback=None):
        d = self.root.callRemote("getWaitingSub", profile_key)
        if callback is not None:
            d.addCallback(callback)
        if errback is None:
            d.addErrback(self._generic_errback)
        else:
            d.addErrback(self._errback, ori_errback=errback)

    def historyGet(self, from_jid, to_jid, limit, between=True, filters='', profile="@NONE@", callback=None, errback=None):
        d = self.root.callRemote("historyGet", from_jid, to_jid, limit, between, filters, profile)
        if callback is not None:
            d.addCallback(callback)
        if errback is None:
            d.addErrback(self._generic_errback)
        else:
            d.addErrback(self._errback, ori_errback=errback)

    def imageCheck(self, arg_0, callback=None, errback=None):
        d = self.root.callRemote("imageCheck", arg_0)
        if callback is not None:
            d.addCallback(callback)
        if errback is None:
            d.addErrback(self._generic_errback)
        else:
            d.addErrback(self._errback, ori_errback=errback)

    def imageConvert(self, source, dest, arg_2, extra, callback=None, errback=None):
        d = self.root.callRemote("imageConvert", source, dest, arg_2, extra)
        if callback is not None:
            d.addCallback(callback)
        if errback is None:
            d.addErrback(self._generic_errback)
        else:
            d.addErrback(self._errback, ori_errback=errback)

    def imageGeneratePreview(self, image_path, profile_key, callback=None, errback=None):
        d = self.root.callRemote("imageGeneratePreview", image_path, profile_key)
        if callback is not None:
            d.addCallback(callback)
        if errback is None:
            d.addErrback(self._generic_errback)
        else:
            d.addErrback(self._errback, ori_errback=errback)

    def imageResize(self, image_path, width, height, callback=None, errback=None):
        d = self.root.callRemote("imageResize", image_path, width, height)
        if callback is not None:
            d.addCallback(callback)
        if errback is None:
            d.addErrback(self._generic_errback)
        else:
            d.addErrback(self._errback, ori_errback=errback)

    def isConnected(self, profile_key="@DEFAULT@", callback=None, errback=None):
        d = self.root.callRemote("isConnected", profile_key)
        if callback is not None:
            d.addCallback(callback)
        if errback is None:
            d.addErrback(self._generic_errback)
        else:
            d.addErrback(self._errback, ori_errback=errback)

    def launchAction(self, callback_id, data, profile_key="@DEFAULT@", callback=None, errback=None):
        d = self.root.callRemote("launchAction", callback_id, data, profile_key)
        if callback is not None:
            d.addCallback(callback)
        if errback is None:
            d.addErrback(self._generic_errback)
        else:
            d.addErrback(self._errback, ori_errback=errback)

    def loadParamsTemplate(self, filename, callback=None, errback=None):
        d = self.root.callRemote("loadParamsTemplate", filename)
        if callback is not None:
            d.addCallback(callback)
        if errback is None:
            d.addErrback(self._generic_errback)
        else:
            d.addErrback(self._errback, ori_errback=errback)

    def menuHelpGet(self, menu_id, language, callback=None, errback=None):
        d = self.root.callRemote("menuHelpGet", menu_id, language)
        if callback is not None:
            d.addCallback(callback)
        if errback is None:
            d.addErrback(self._generic_errback)
        else:
            d.addErrback(self._errback, ori_errback=errback)

    def menuLaunch(self, menu_type, path, data, security_limit, profile_key, callback=None, errback=None):
        d = self.root.callRemote("menuLaunch", menu_type, path, data, security_limit, profile_key)
        if callback is not None:
            d.addCallback(callback)
        if errback is None:
            d.addErrback(self._generic_errback)
        else:
            d.addErrback(self._errback, ori_errback=errback)

    def menusGet(self, language, security_limit, callback=None, errback=None):
        d = self.root.callRemote("menusGet", language, security_limit)
        if callback is not None:
            d.addCallback(callback)
        if errback is None:
            d.addErrback(self._generic_errback)
        else:
            d.addErrback(self._errback, ori_errback=errback)

    def messageEncryptionGet(self, to_jid, profile_key, callback=None, errback=None):
        d = self.root.callRemote("messageEncryptionGet", to_jid, profile_key)
        if callback is not None:
            d.addCallback(callback)
        if errback is None:
            d.addErrback(self._generic_errback)
        else:
            d.addErrback(self._errback, ori_errback=errback)

    def messageEncryptionStart(self, to_jid, namespace='', replace=False, profile_key="@NONE@", callback=None, errback=None):
        d = self.root.callRemote("messageEncryptionStart", to_jid, namespace, replace, profile_key)
        if callback is not None:
            d.addCallback(lambda __: callback())
        if errback is None:
            d.addErrback(self._generic_errback)
        else:
            d.addErrback(self._errback, ori_errback=errback)

    def messageEncryptionStop(self, to_jid, profile_key, callback=None, errback=None):
        d = self.root.callRemote("messageEncryptionStop", to_jid, profile_key)
        if callback is not None:
            d.addCallback(lambda __: callback())
        if errback is None:
            d.addErrback(self._generic_errback)
        else:
            d.addErrback(self._errback, ori_errback=errback)

    def messageSend(self, to_jid, message, subject={}, mess_type="auto", extra={}, profile_key="@NONE@", callback=None, errback=None):
        d = self.root.callRemote("messageSend", to_jid, message, subject, mess_type, extra, profile_key)
        if callback is not None:
            d.addCallback(lambda __: callback())
        if errback is None:
            d.addErrback(self._generic_errback)
        else:
            d.addErrback(self._errback, ori_errback=errback)

    def namespacesGet(self, callback=None, errback=None):
        d = self.root.callRemote("namespacesGet")
        if callback is not None:
            d.addCallback(callback)
        if errback is None:
            d.addErrback(self._generic_errback)
        else:
            d.addErrback(self._errback, ori_errback=errback)

    def paramsRegisterApp(self, xml, security_limit=-1, app='', callback=None, errback=None):
        d = self.root.callRemote("paramsRegisterApp", xml, security_limit, app)
        if callback is not None:
            d.addCallback(lambda __: callback())
        if errback is None:
            d.addErrback(self._generic_errback)
        else:
            d.addErrback(self._errback, ori_errback=errback)

    def privateDataDelete(self, namespace, key, arg_2, callback=None, errback=None):
        d = self.root.callRemote("privateDataDelete", namespace, key, arg_2)
        if callback is not None:
            d.addCallback(lambda __: callback())
        if errback is None:
            d.addErrback(self._generic_errback)
        else:
            d.addErrback(self._errback, ori_errback=errback)

    def privateDataGet(self, namespace, key, profile_key, callback=None, errback=None):
        d = self.root.callRemote("privateDataGet", namespace, key, profile_key)
        if callback is not None:
            d.addCallback(callback)
        if errback is None:
            d.addErrback(self._generic_errback)
        else:
            d.addErrback(self._errback, ori_errback=errback)

    def privateDataSet(self, namespace, key, data, profile_key, callback=None, errback=None):
        d = self.root.callRemote("privateDataSet", namespace, key, data, profile_key)
        if callback is not None:
            d.addCallback(lambda __: callback())
        if errback is None:
            d.addErrback(self._generic_errback)
        else:
            d.addErrback(self._errback, ori_errback=errback)

    def profileCreate(self, profile, password='', component='', callback=None, errback=None):
        d = self.root.callRemote("profileCreate", profile, password, component)
        if callback is not None:
            d.addCallback(lambda __: callback())
        if errback is None:
            d.addErrback(self._generic_errback)
        else:
            d.addErrback(self._errback, ori_errback=errback)

    def profileIsSessionStarted(self, profile_key="@DEFAULT@", callback=None, errback=None):
        d = self.root.callRemote("profileIsSessionStarted", profile_key)
        if callback is not None:
            d.addCallback(callback)
        if errback is None:
            d.addErrback(self._generic_errback)
        else:
            d.addErrback(self._errback, ori_errback=errback)

    def profileNameGet(self, profile_key="@DEFAULT@", callback=None, errback=None):
        d = self.root.callRemote("profileNameGet", profile_key)
        if callback is not None:
            d.addCallback(callback)
        if errback is None:
            d.addErrback(self._generic_errback)
        else:
            d.addErrback(self._errback, ori_errback=errback)

    def profileSetDefault(self, profile, callback=None, errback=None):
        d = self.root.callRemote("profileSetDefault", profile)
        if callback is not None:
            d.addCallback(lambda __: callback())
        if errback is None:
            d.addErrback(self._generic_errback)
        else:
            d.addErrback(self._errback, ori_errback=errback)

    def profileStartSession(self, password='', profile_key="@DEFAULT@", callback=None, errback=None):
        d = self.root.callRemote("profileStartSession", password, profile_key)
        if callback is not None:
            d.addCallback(callback)
        if errback is None:
            d.addErrback(self._generic_errback)
        else:
            d.addErrback(self._errback, ori_errback=errback)

    def profilesListGet(self, clients=True, components=False, callback=None, errback=None):
        d = self.root.callRemote("profilesListGet", clients, components)
        if callback is not None:
            d.addCallback(callback)
        if errback is None:
            d.addErrback(self._generic_errback)
        else:
            d.addErrback(self._errback, ori_errback=errback)

    def progressGet(self, id, profile, callback=None, errback=None):
        d = self.root.callRemote("progressGet", id, profile)
        if callback is not None:
            d.addCallback(callback)
        if errback is None:
            d.addErrback(self._generic_errback)
        else:
            d.addErrback(self._errback, ori_errback=errback)

    def progressGetAll(self, profile, callback=None, errback=None):
        d = self.root.callRemote("progressGetAll", profile)
        if callback is not None:
            d.addCallback(callback)
        if errback is None:
            d.addErrback(self._generic_errback)
        else:
            d.addErrback(self._errback, ori_errback=errback)

    def progressGetAllMetadata(self, profile, callback=None, errback=None):
        d = self.root.callRemote("progressGetAllMetadata", profile)
        if callback is not None:
            d.addCallback(callback)
        if errback is None:
            d.addErrback(self._generic_errback)
        else:
            d.addErrback(self._errback, ori_errback=errback)

    def rosterResync(self, profile_key="@DEFAULT@", callback=None, errback=None):
        d = self.root.callRemote("rosterResync", profile_key)
        if callback is not None:
            d.addCallback(lambda __: callback())
        if errback is None:
            d.addErrback(self._generic_errback)
        else:
            d.addErrback(self._errback, ori_errback=errback)

    def saveParamsTemplate(self, filename, callback=None, errback=None):
        d = self.root.callRemote("saveParamsTemplate", filename)
        if callback is not None:
            d.addCallback(callback)
        if errback is None:
            d.addErrback(self._generic_errback)
        else:
            d.addErrback(self._errback, ori_errback=errback)

    def sessionInfosGet(self, profile_key, callback=None, errback=None):
        d = self.root.callRemote("sessionInfosGet", profile_key)
        if callback is not None:
            d.addCallback(callback)
        if errback is None:
            d.addErrback(self._generic_errback)
        else:
            d.addErrback(self._errback, ori_errback=errback)

    def setParam(self, name, value, category, security_limit=-1, profile_key="@DEFAULT@", callback=None, errback=None):
        d = self.root.callRemote("setParam", name, value, category, security_limit, profile_key)
        if callback is not None:
            d.addCallback(lambda __: callback())
        if errback is None:
            d.addErrback(self._generic_errback)
        else:
            d.addErrback(self._errback, ori_errback=errback)

    def setPresence(self, to_jid='', show='', statuses={}, profile_key="@DEFAULT@", callback=None, errback=None):
        d = self.root.callRemote("setPresence", to_jid, show, statuses, profile_key)
        if callback is not None:
            d.addCallback(lambda __: callback())
        if errback is None:
            d.addErrback(self._generic_errback)
        else:
            d.addErrback(self._errback, ori_errback=errback)

    def subscription(self, sub_type, entity, profile_key="@DEFAULT@", callback=None, errback=None):
        d = self.root.callRemote("subscription", sub_type, entity, profile_key)
        if callback is not None:
            d.addCallback(lambda __: callback())
        if errback is None:
            d.addErrback(self._generic_errback)
        else:
            d.addErrback(self._errback, ori_errback=errback)

    def updateContact(self, entity_jid, name, groups, profile_key="@DEFAULT@", callback=None, errback=None):
        d = self.root.callRemote("updateContact", entity_jid, name, groups, profile_key)
        if callback is not None:
            d.addCallback(lambda __: callback())
        if errback is None:
            d.addErrback(self._generic_errback)
        else:
            d.addErrback(self._errback, ori_errback=errback)


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

    def actionsGet(self, profile_key="@DEFAULT@"):
        d = self.root.callRemote("actionsGet", profile_key)
        d.addErrback(self._errback)
        return d.asFuture(asyncio.get_event_loop())

    def addContact(self, entity_jid, profile_key="@DEFAULT@"):
        d = self.root.callRemote("addContact", entity_jid, profile_key)
        d.addErrback(self._errback)
        return d.asFuture(asyncio.get_event_loop())

    def asyncDeleteProfile(self, profile):
        d = self.root.callRemote("asyncDeleteProfile", profile)
        d.addErrback(self._errback)
        return d.asFuture(asyncio.get_event_loop())

    def asyncGetParamA(self, name, category, attribute="value", security_limit=-1, profile_key="@DEFAULT@"):
        d = self.root.callRemote("asyncGetParamA", name, category, attribute, security_limit, profile_key)
        d.addErrback(self._errback)
        return d.asFuture(asyncio.get_event_loop())

    def asyncGetParamsValuesFromCategory(self, category, security_limit=-1, app="", extra="", profile_key="@DEFAULT@"):
        d = self.root.callRemote("asyncGetParamsValuesFromCategory", category, security_limit, app, extra, profile_key)
        d.addErrback(self._errback)
        return d.asFuture(asyncio.get_event_loop())

    def connect(self, profile_key="@DEFAULT@", password='', options={}):
        d = self.root.callRemote("connect", profile_key, password, options)
        d.addErrback(self._errback)
        return d.asFuture(asyncio.get_event_loop())

    def contactGet(self, arg_0, profile_key="@DEFAULT@"):
        d = self.root.callRemote("contactGet", arg_0, profile_key)
        d.addErrback(self._errback)
        return d.asFuture(asyncio.get_event_loop())

    def delContact(self, entity_jid, profile_key="@DEFAULT@"):
        d = self.root.callRemote("delContact", entity_jid, profile_key)
        d.addErrback(self._errback)
        return d.asFuture(asyncio.get_event_loop())

    def devicesInfosGet(self, bare_jid, profile_key):
        d = self.root.callRemote("devicesInfosGet", bare_jid, profile_key)
        d.addErrback(self._errback)
        return d.asFuture(asyncio.get_event_loop())

    def discoFindByFeatures(self, namespaces, identities, bare_jid=False, service=True, roster=True, own_jid=True, local_device=False, profile_key="@DEFAULT@"):
        d = self.root.callRemote("discoFindByFeatures", namespaces, identities, bare_jid, service, roster, own_jid, local_device, profile_key)
        d.addErrback(self._errback)
        return d.asFuture(asyncio.get_event_loop())

    def discoInfos(self, entity_jid, node=u'', use_cache=True, profile_key="@DEFAULT@"):
        d = self.root.callRemote("discoInfos", entity_jid, node, use_cache, profile_key)
        d.addErrback(self._errback)
        return d.asFuture(asyncio.get_event_loop())

    def discoItems(self, entity_jid, node=u'', use_cache=True, profile_key="@DEFAULT@"):
        d = self.root.callRemote("discoItems", entity_jid, node, use_cache, profile_key)
        d.addErrback(self._errback)
        return d.asFuture(asyncio.get_event_loop())

    def disconnect(self, profile_key="@DEFAULT@"):
        d = self.root.callRemote("disconnect", profile_key)
        d.addErrback(self._errback)
        return d.asFuture(asyncio.get_event_loop())

    def encryptionNamespaceGet(self, arg_0):
        d = self.root.callRemote("encryptionNamespaceGet", arg_0)
        d.addErrback(self._errback)
        return d.asFuture(asyncio.get_event_loop())

    def encryptionPluginsGet(self):
        d = self.root.callRemote("encryptionPluginsGet")
        d.addErrback(self._errback)
        return d.asFuture(asyncio.get_event_loop())

    def encryptionTrustUIGet(self, to_jid, namespace, profile_key):
        d = self.root.callRemote("encryptionTrustUIGet", to_jid, namespace, profile_key)
        d.addErrback(self._errback)
        return d.asFuture(asyncio.get_event_loop())

    def getConfig(self, section, name):
        d = self.root.callRemote("getConfig", section, name)
        d.addErrback(self._errback)
        return d.asFuture(asyncio.get_event_loop())

    def getContacts(self, profile_key="@DEFAULT@"):
        d = self.root.callRemote("getContacts", profile_key)
        d.addErrback(self._errback)
        return d.asFuture(asyncio.get_event_loop())

    def getContactsFromGroup(self, group, profile_key="@DEFAULT@"):
        d = self.root.callRemote("getContactsFromGroup", group, profile_key)
        d.addErrback(self._errback)
        return d.asFuture(asyncio.get_event_loop())

    def getEntitiesData(self, jids, keys, profile):
        d = self.root.callRemote("getEntitiesData", jids, keys, profile)
        d.addErrback(self._errback)
        return d.asFuture(asyncio.get_event_loop())

    def getEntityData(self, jid, keys, profile):
        d = self.root.callRemote("getEntityData", jid, keys, profile)
        d.addErrback(self._errback)
        return d.asFuture(asyncio.get_event_loop())

    def getFeatures(self, profile_key):
        d = self.root.callRemote("getFeatures", profile_key)
        d.addErrback(self._errback)
        return d.asFuture(asyncio.get_event_loop())

    def getMainResource(self, contact_jid, profile_key="@DEFAULT@"):
        d = self.root.callRemote("getMainResource", contact_jid, profile_key)
        d.addErrback(self._errback)
        return d.asFuture(asyncio.get_event_loop())

    def getParamA(self, name, category, attribute="value", profile_key="@DEFAULT@"):
        d = self.root.callRemote("getParamA", name, category, attribute, profile_key)
        d.addErrback(self._errback)
        return d.asFuture(asyncio.get_event_loop())

    def getParamsCategories(self):
        d = self.root.callRemote("getParamsCategories")
        d.addErrback(self._errback)
        return d.asFuture(asyncio.get_event_loop())

    def getParamsUI(self, security_limit=-1, app='', extra='', profile_key="@DEFAULT@"):
        d = self.root.callRemote("getParamsUI", security_limit, app, extra, profile_key)
        d.addErrback(self._errback)
        return d.asFuture(asyncio.get_event_loop())

    def getPresenceStatuses(self, profile_key="@DEFAULT@"):
        d = self.root.callRemote("getPresenceStatuses", profile_key)
        d.addErrback(self._errback)
        return d.asFuture(asyncio.get_event_loop())

    def getReady(self):
        d = self.root.callRemote("getReady")
        d.addErrback(self._errback)
        return d.asFuture(asyncio.get_event_loop())

    def getVersion(self):
        d = self.root.callRemote("getVersion")
        d.addErrback(self._errback)
        return d.asFuture(asyncio.get_event_loop())

    def getWaitingSub(self, profile_key="@DEFAULT@"):
        d = self.root.callRemote("getWaitingSub", profile_key)
        d.addErrback(self._errback)
        return d.asFuture(asyncio.get_event_loop())

    def historyGet(self, from_jid, to_jid, limit, between=True, filters='', profile="@NONE@"):
        d = self.root.callRemote("historyGet", from_jid, to_jid, limit, between, filters, profile)
        d.addErrback(self._errback)
        return d.asFuture(asyncio.get_event_loop())

    def imageCheck(self, arg_0):
        d = self.root.callRemote("imageCheck", arg_0)
        d.addErrback(self._errback)
        return d.asFuture(asyncio.get_event_loop())

    def imageConvert(self, source, dest, arg_2, extra):
        d = self.root.callRemote("imageConvert", source, dest, arg_2, extra)
        d.addErrback(self._errback)
        return d.asFuture(asyncio.get_event_loop())

    def imageGeneratePreview(self, image_path, profile_key):
        d = self.root.callRemote("imageGeneratePreview", image_path, profile_key)
        d.addErrback(self._errback)
        return d.asFuture(asyncio.get_event_loop())

    def imageResize(self, image_path, width, height):
        d = self.root.callRemote("imageResize", image_path, width, height)
        d.addErrback(self._errback)
        return d.asFuture(asyncio.get_event_loop())

    def isConnected(self, profile_key="@DEFAULT@"):
        d = self.root.callRemote("isConnected", profile_key)
        d.addErrback(self._errback)
        return d.asFuture(asyncio.get_event_loop())

    def launchAction(self, callback_id, data, profile_key="@DEFAULT@"):
        d = self.root.callRemote("launchAction", callback_id, data, profile_key)
        d.addErrback(self._errback)
        return d.asFuture(asyncio.get_event_loop())

    def loadParamsTemplate(self, filename):
        d = self.root.callRemote("loadParamsTemplate", filename)
        d.addErrback(self._errback)
        return d.asFuture(asyncio.get_event_loop())

    def menuHelpGet(self, menu_id, language):
        d = self.root.callRemote("menuHelpGet", menu_id, language)
        d.addErrback(self._errback)
        return d.asFuture(asyncio.get_event_loop())

    def menuLaunch(self, menu_type, path, data, security_limit, profile_key):
        d = self.root.callRemote("menuLaunch", menu_type, path, data, security_limit, profile_key)
        d.addErrback(self._errback)
        return d.asFuture(asyncio.get_event_loop())

    def menusGet(self, language, security_limit):
        d = self.root.callRemote("menusGet", language, security_limit)
        d.addErrback(self._errback)
        return d.asFuture(asyncio.get_event_loop())

    def messageEncryptionGet(self, to_jid, profile_key):
        d = self.root.callRemote("messageEncryptionGet", to_jid, profile_key)
        d.addErrback(self._errback)
        return d.asFuture(asyncio.get_event_loop())

    def messageEncryptionStart(self, to_jid, namespace='', replace=False, profile_key="@NONE@"):
        d = self.root.callRemote("messageEncryptionStart", to_jid, namespace, replace, profile_key)
        d.addErrback(self._errback)
        return d.asFuture(asyncio.get_event_loop())

    def messageEncryptionStop(self, to_jid, profile_key):
        d = self.root.callRemote("messageEncryptionStop", to_jid, profile_key)
        d.addErrback(self._errback)
        return d.asFuture(asyncio.get_event_loop())

    def messageSend(self, to_jid, message, subject={}, mess_type="auto", extra={}, profile_key="@NONE@"):
        d = self.root.callRemote("messageSend", to_jid, message, subject, mess_type, extra, profile_key)
        d.addErrback(self._errback)
        return d.asFuture(asyncio.get_event_loop())

    def namespacesGet(self):
        d = self.root.callRemote("namespacesGet")
        d.addErrback(self._errback)
        return d.asFuture(asyncio.get_event_loop())

    def paramsRegisterApp(self, xml, security_limit=-1, app=''):
        d = self.root.callRemote("paramsRegisterApp", xml, security_limit, app)
        d.addErrback(self._errback)
        return d.asFuture(asyncio.get_event_loop())

    def privateDataDelete(self, namespace, key, arg_2):
        d = self.root.callRemote("privateDataDelete", namespace, key, arg_2)
        d.addErrback(self._errback)
        return d.asFuture(asyncio.get_event_loop())

    def privateDataGet(self, namespace, key, profile_key):
        d = self.root.callRemote("privateDataGet", namespace, key, profile_key)
        d.addErrback(self._errback)
        return d.asFuture(asyncio.get_event_loop())

    def privateDataSet(self, namespace, key, data, profile_key):
        d = self.root.callRemote("privateDataSet", namespace, key, data, profile_key)
        d.addErrback(self._errback)
        return d.asFuture(asyncio.get_event_loop())

    def profileCreate(self, profile, password='', component=''):
        d = self.root.callRemote("profileCreate", profile, password, component)
        d.addErrback(self._errback)
        return d.asFuture(asyncio.get_event_loop())

    def profileIsSessionStarted(self, profile_key="@DEFAULT@"):
        d = self.root.callRemote("profileIsSessionStarted", profile_key)
        d.addErrback(self._errback)
        return d.asFuture(asyncio.get_event_loop())

    def profileNameGet(self, profile_key="@DEFAULT@"):
        d = self.root.callRemote("profileNameGet", profile_key)
        d.addErrback(self._errback)
        return d.asFuture(asyncio.get_event_loop())

    def profileSetDefault(self, profile):
        d = self.root.callRemote("profileSetDefault", profile)
        d.addErrback(self._errback)
        return d.asFuture(asyncio.get_event_loop())

    def profileStartSession(self, password='', profile_key="@DEFAULT@"):
        d = self.root.callRemote("profileStartSession", password, profile_key)
        d.addErrback(self._errback)
        return d.asFuture(asyncio.get_event_loop())

    def profilesListGet(self, clients=True, components=False):
        d = self.root.callRemote("profilesListGet", clients, components)
        d.addErrback(self._errback)
        return d.asFuture(asyncio.get_event_loop())

    def progressGet(self, id, profile):
        d = self.root.callRemote("progressGet", id, profile)
        d.addErrback(self._errback)
        return d.asFuture(asyncio.get_event_loop())

    def progressGetAll(self, profile):
        d = self.root.callRemote("progressGetAll", profile)
        d.addErrback(self._errback)
        return d.asFuture(asyncio.get_event_loop())

    def progressGetAllMetadata(self, profile):
        d = self.root.callRemote("progressGetAllMetadata", profile)
        d.addErrback(self._errback)
        return d.asFuture(asyncio.get_event_loop())

    def rosterResync(self, profile_key="@DEFAULT@"):
        d = self.root.callRemote("rosterResync", profile_key)
        d.addErrback(self._errback)
        return d.asFuture(asyncio.get_event_loop())

    def saveParamsTemplate(self, filename):
        d = self.root.callRemote("saveParamsTemplate", filename)
        d.addErrback(self._errback)
        return d.asFuture(asyncio.get_event_loop())

    def sessionInfosGet(self, profile_key):
        d = self.root.callRemote("sessionInfosGet", profile_key)
        d.addErrback(self._errback)
        return d.asFuture(asyncio.get_event_loop())

    def setParam(self, name, value, category, security_limit=-1, profile_key="@DEFAULT@"):
        d = self.root.callRemote("setParam", name, value, category, security_limit, profile_key)
        d.addErrback(self._errback)
        return d.asFuture(asyncio.get_event_loop())

    def setPresence(self, to_jid='', show='', statuses={}, profile_key="@DEFAULT@"):
        d = self.root.callRemote("setPresence", to_jid, show, statuses, profile_key)
        d.addErrback(self._errback)
        return d.asFuture(asyncio.get_event_loop())

    def subscription(self, sub_type, entity, profile_key="@DEFAULT@"):
        d = self.root.callRemote("subscription", sub_type, entity, profile_key)
        d.addErrback(self._errback)
        return d.asFuture(asyncio.get_event_loop())

    def updateContact(self, entity_jid, name, groups, profile_key="@DEFAULT@"):
        d = self.root.callRemote("updateContact", entity_jid, name, groups, profile_key)
        d.addErrback(self._errback)
        return d.asFuture(asyncio.get_event_loop())
