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
import time
import calendar
import uuid
import mimetypes
from typing import Tuple
from urllib.parse import urlparse, unquote
from functools import partial
from pathlib import Path
import shortuuid
from sat.core.i18n import _
from sat.core.constants import Const as C
from sat.memory import cache
from twisted.internet import defer, error as internet_error
from twisted.internet import ssl
from twisted.words.protocols.jabber.xmlstream import XMPPHandler
from twisted.words.protocols.jabber import xmlstream
from twisted.words.protocols.jabber import error
from twisted.words.protocols.jabber import jid
from twisted.words.xish import domish
from twisted.python import failure
from wokkel import client as wokkel_client, disco, xmppim, generic, iwokkel
from wokkel import component
from wokkel import delay
from sat.core.log import getLogger
from sat.core import exceptions
from sat.memory import encryption
from sat.memory import persistent
from sat.tools import xml_tools
from sat.tools import utils
from sat.tools.common import data_format
from zope.interface import implementer

log = getLogger(__name__)


NS_X_DATA = "jabber:x:data"
NS_DISCO_INFO = "http://jabber.org/protocol/disco#info"
NS_XML_ELEMENT = "urn:xmpp:xml-element"
NS_ROSTER_VER = "urn:xmpp:features:rosterver"
# we use 2 "@" which is illegal in a jid, to be sure we are not mixing keys
# with roster jids
ROSTER_VER_KEY = "@version@"


class ClientPluginWrapper:
    """Use a plugin with default value if plugin is missing"""

    def __init__(self, client, plugin_name, missing):
        self.client = client
        self.plugin = client.host_app.plugins.get(plugin_name)
        if self.plugin is None:
            self.plugin_name = plugin_name
        self.missing = missing

    def __getattr__(self, attr):
        if self.plugin is None:
            missing = self.missing
            if isinstance(missing, type) and issubclass(missing, Exception):
                raise missing(f"plugin {self.plugin_name!r} is not available")
            elif isinstance(missing, Exception):
                raise missing
            else:
                return lambda *args, **kwargs: missing
        return partial(getattr(self.plugin, attr), self.client)


class SatXMPPEntity:
    """Common code for Client and Component"""
    # profile is added there when startConnection begins and removed when it is finished
    profiles_connecting = set()

    def __init__(self, host_app, profile, max_retries):
        factory = self.factory

        # we monkey patch clientConnectionLost to handle networkEnabled/networkDisabled
        # and to allow plugins to tune reconnection mechanism
        clientConnectionFailed_ori = factory.clientConnectionFailed
        clientConnectionLost_ori = factory.clientConnectionLost
        factory.clientConnectionFailed = partial(
            self.connectionTerminated, term_type="failed", cb=clientConnectionFailed_ori)
        factory.clientConnectionLost = partial(
            self.connectionTerminated, term_type="lost", cb=clientConnectionLost_ori)

        factory.maxRetries = max_retries
        factory.maxDelay = 30
        # when self._connected_d is None, we are not connected
        # else, it's a deferred which fire on disconnection
        self._connected_d = None
        self.profile = profile
        self.host_app = host_app
        self.cache = cache.Cache(host_app, profile)
        self.mess_id2uid = {}  # map from message id to uid used in history.
                               # Key: (full_jid, message_id) Value: uid
        # this Deferred fire when entity is connected
        self.conn_deferred = defer.Deferred()
        self._progress_cb = {}  # callback called when a progress is requested
                                # (key = progress id)
        self.actions = {}  # used to keep track of actions for retrieval (key = action_id)
        self.encryption = encryption.EncryptionHandler(self)

    def __str__(self):
        return f"Client for profile {self.profile}"

    def __repr__(self):
        return f"{super().__repr__()} - profile: {self.profile!r}"

    ## initialisation ##

    @defer.inlineCallbacks
    def _callConnectionTriggers(self):
        """Call conneting trigger prepare connected trigger

        @param plugins(iterable): plugins to use
        @return (list[object, callable]): plugin to trigger tuples with:
            - plugin instance
            - profileConnected* triggers (to call after connection)
        """
        plugin_conn_cb = []
        for plugin in self._getPluginsList():
            # we check if plugin handle client mode
            if plugin.is_handler:
                plugin.getHandler(self).setHandlerParent(self)

            # profileConnecting/profileConnected methods handling

            # profile connecting is called right now (before actually starting client)
            connecting_cb = getattr(plugin, "profileConnecting", None)
            if connecting_cb is not None:
                yield utils.asDeferred(connecting_cb, self)

            # profile connected is called after client is ready and roster is got
            connected_cb = getattr(plugin, "profileConnected", None)
            if connected_cb is not None:
                plugin_conn_cb.append((plugin, connected_cb))

        defer.returnValue(plugin_conn_cb)

    def _getPluginsList(self):
        """Return list of plugin to use

        need to be implemented by subclasses
        this list is used to call profileConnect* triggers
        @return(iterable[object]): plugins to use
        """
        raise NotImplementedError

    def _createSubProtocols(self):
        return

    def entityConnected(self):
        """Called once connection is done

        may return a Deferred, to perform initialisation tasks
        """
        return

    @classmethod
    async def startConnection(cls, host, profile, max_retries):
        """instantiate the entity and start the connection"""
        # FIXME: reconnection doesn't seems to be handled correclty
        #        (client is deleted then recreated from scratch)
        #        most of methods called here should be called once on first connection
        #        (e.g. adding subprotocols)
        #        but client should not be deleted except if session is finished
        #        (independently of connection/deconnection)
        if profile in cls.profiles_connecting:
            raise exceptions.CancelError(f"{profile} is already being connected")
        cls.profiles_connecting.add(profile)
        try:
            try:
                port = int(
                    host.memory.getParamA(
                        C.FORCE_PORT_PARAM, "Connection", profile_key=profile
                    )
                )
            except ValueError:
                log.debug(_("Can't parse port value, using default value"))
                port = (
                    None
                )  # will use default value 5222 or be retrieved from a DNS SRV record

            password = await host.memory.asyncGetParamA(
                "Password", "Connection", profile_key=profile
            )

            entity_jid_s = await host.memory.asyncGetParamA(
                "JabberID", "Connection", profile_key=profile)
            entity_jid = jid.JID(entity_jid_s)

            if not entity_jid.resource and not cls.is_component and entity_jid.user:
                # if no resource is specified, we create our own instead of using
                # server returned one, as it will then stay stable in case of
                # reconnection. we only do that for client and if there is a user part, to
                # let server decide for anonymous login
                resource_dict = await host.memory.storage.getPrivates(
                    "core:xmpp", ["resource"] , profile=profile)
                try:
                    resource = resource_dict["resource"]
                except KeyError:
                    resource = f"{C.APP_NAME_FILE}.{shortuuid.uuid()}"
                    await host.memory.storage.setPrivateValue(
                        "core:xmpp", "resource", resource, profile=profile)

                log.info(_("We'll use the stable resource {resource}").format(
                    resource=resource))
                entity_jid.resource = resource

            if profile in host.profiles:
                if host.profiles[profile].isConnected():
                    raise exceptions.InternalError(
                        f"There is already a connected profile of name {profile!r} in "
                        f"host")
                log.debug(
                    "removing unconnected profile {profile!r}")
                del host.profiles[profile]
            entity = host.profiles[profile] = cls(
                host, profile, entity_jid, password,
                host.memory.getParamA(C.FORCE_SERVER_PARAM, "Connection",
                                      profile_key=profile) or None,
                port, max_retries,
                )

            await entity.encryption.loadSessions()

            entity._createSubProtocols()

            entity.fallBack = SatFallbackHandler(host)
            entity.fallBack.setHandlerParent(entity)

            entity.versionHandler = SatVersionHandler(C.APP_NAME, host.full_version)
            entity.versionHandler.setHandlerParent(entity)

            entity.identityHandler = SatIdentityHandler()
            entity.identityHandler.setHandlerParent(entity)

            log.debug(_("setting plugins parents"))

            plugin_conn_cb = await entity._callConnectionTriggers()

            entity.startService()

            await entity.conn_deferred

            await defer.maybeDeferred(entity.entityConnected)

            # Call profileConnected callback for all plugins,
            # and print error message if any of them fails
            conn_cb_list = []
            for __, callback in plugin_conn_cb:
                conn_cb_list.append(utils.asDeferred(callback, entity))
            list_d = defer.DeferredList(conn_cb_list)

            def logPluginResults(results):
                all_succeed = all([success for success, result in results])
                if not all_succeed:
                    log.error(_("Plugins initialisation error"))
                    for idx, (success, result) in enumerate(results):
                        if not success:
                            log.error(
                                "error (plugin %(name)s): %(failure)s"
                                % {
                                    "name": plugin_conn_cb[idx][0]._info["import_name"],
                                    "failure": result,
                                }
                            )

            await list_d.addCallback(
                logPluginResults
            )  # FIXME: we should have a timeout here, and a way to know if a plugin freeze
            # TODO: mesure launch time of each plugin
        finally:
            cls.profiles_connecting.remove(profile)

    def _disconnectionCb(self, __):
        self._connected_d = None

    def _disconnectionEb(self, failure_):
        log.error(_("Error while disconnecting: {}".format(failure_)))

    def _authd(self, xmlstream):
        super(SatXMPPEntity, self)._authd(xmlstream)
        log.debug(_("{profile} identified").format(profile=self.profile))
        self.streamInitialized()

    def _finish_connection(self, __):
        if self.conn_deferred.called:
            # can happen in case of forced disconnection by server
            log.debug(f"{self} has already been connected")
        else:
            self.conn_deferred.callback(None)

    def streamInitialized(self):
        """Called after _authd"""
        log.debug(_("XML stream is initialized"))
        if not self.host_app.trigger.point("xml_init", self):
            return
        self.postStreamInit()

    def postStreamInit(self):
        """Workflow after stream initalisation."""
        log.info(
            _("********** [{profile}] CONNECTED **********").format(profile=self.profile)
        )

        # the following Deferred is used to know when we are connected
        # so we need to be set it to None when connection is lost
        self._connected_d = defer.Deferred()
        self._connected_d.addCallback(self._cleanConnection)
        self._connected_d.addCallback(self._disconnectionCb)
        self._connected_d.addErrback(self._disconnectionEb)

        # we send the signal to the clients
        self.host_app.bridge.connected(self.jid.full(), self.profile)

        self.disco = SatDiscoProtocol(self)
        self.disco.setHandlerParent(self)
        self.discoHandler = disco.DiscoHandler()
        self.discoHandler.setHandlerParent(self)
        disco_d = defer.succeed(None)

        if not self.host_app.trigger.point("Disco handled", disco_d, self.profile):
            return

        disco_d.addCallback(self._finish_connection)

    def initializationFailed(self, reason):
        log.error(
            _(
                "ERROR: XMPP connection failed for profile '%(profile)s': %(reason)s"
                % {"profile": self.profile, "reason": reason}
            )
        )
        self.conn_deferred.errback(reason.value)
        try:
            super(SatXMPPEntity, self).initializationFailed(reason)
        except:
            # we already chained an errback, no need to raise an exception
            pass

    ## connection ##

    def connectionTerminated(self, connector, reason, term_type, cb):
        """Display disconnection reason, and call factory method

        This method is monkey patched to factory, allowing plugins to handle finely
        reconnection with the triggers.
        @param connector(twisted.internet.base.BaseConnector): current connector
        @param reason(failure.Failure): why connection has been terminated
        @param term_type(unicode): on of 'failed' or 'lost'
        @param cb(callable): original factory method

        @trigger connection_failed(connector, reason): connection can't be established
        @trigger connection_lost(connector, reason): connection was available but it not
            anymore
        """
        # we save connector because it may be deleted when connection will be dropped
        # if reconnection is disabled
        self._saved_connector = connector
        if reason is not None and not isinstance(reason.value,
                                                 internet_error.ConnectionDone):
            try:
                reason_str = str(reason.value)
            except Exception:
                # FIXME: workaround for Android were p4a strips docstrings
                #        while Twisted use docstring in __str__
                # TODO: create a ticket upstream, Twisted should work when optimization
                #       is used
                reason_str = str(reason.value.__class__)
            log.warning(f"[{self.profile}] Connection {term_type}: {reason_str}")
        if not self.host_app.trigger.point("connection_" + term_type, connector, reason):
            return
        return cb(connector, reason)

    def networkDisabled(self):
        """Indicate that network has been completely disabled

        In other words, internet is not available anymore and transport must be stopped.
        Retrying is disabled too, as it makes no sense to try without network, and it may
        use resources (notably battery on mobiles).
        """
        log.info(_("stopping connection because of network disabled"))
        self.factory.continueTrying = 0
        self._network_disabled = True
        if self.xmlstream is not None:
            self.xmlstream.transport.abortConnection()

    def networkEnabled(self):
        """Indicate that network has been (re)enabled

        This happens when e.g. user activate WIFI connection.
        """
        try:
            connector = self._saved_connector
            network_disabled = self._network_disabled
        except AttributeError:
            # connection has not been stopped by networkDisabled
            # we don't have to restart it
            log.debug(f"no connection to restart [{self.profile}]")
            return
        else:
            del self._network_disabled
            if not network_disabled:
                raise exceptions.InternalError("network_disabled should be True")
        log.info(_("network is available, trying to connect"))
        # we want to be sure to start fresh
        self.factory.resetDelay()
        # we have a saved connector, meaning the connection has been stopped previously
        # we can now try to reconnect
        connector.connect()

    def _connected(self, xs):
        send_hooks = []
        receive_hooks = []
        self.host_app.trigger.point(
            "stream_hooks", self, receive_hooks, send_hooks)
        for hook in receive_hooks:
            xs.addHook(C.STREAM_HOOK_RECEIVE, hook)
        for hook in send_hooks:
            xs.addHook(C.STREAM_HOOK_SEND, hook)
        super(SatXMPPEntity, self)._connected(xs)

    def disconnectProfile(self, reason):
        if self._connected_d is not None:
            self.host_app.bridge.disconnected(
                self.profile
            )  # we send the signal to the clients
            log.info(
                _("********** [{profile}] DISCONNECTED **********").format(
                    profile=self.profile
                )
            )
            # we purge only if no new connection attempt is expected
            if not self.factory.continueTrying:
                log.debug("continueTrying not set, purging entity")
                self._connected_d.callback(None)
                # and we remove references to this client
                self.host_app.purgeEntity(self.profile)

        if not self.conn_deferred.called:
            if reason is None:
                err = error.StreamError("Server unexpectedly closed the connection")
            else:
                err = reason
                try:
                    if err.value.args[0][0][2] == "certificate verify failed":
                        err = exceptions.InvalidCertificate(
                            _("Your server certificate is not valid "
                              "(its identity can't be checked).\n\n"
                              "This should never happen and may indicate that "
                              "somebody is trying to spy on you.\n"
                              "Please contact your server administrator."))
                        self.factory.stopTrying()
                        try:
                            # with invalid certificate, we should not retry to connect
                            # so we delete saved connector to avoid reconnection if
                            # networkEnabled is called.
                            del self._saved_connector
                        except AttributeError:
                            pass
                except (IndexError, TypeError):
                    pass
            self.conn_deferred.errback(err)

    def _disconnected(self, reason):
        super(SatXMPPEntity, self)._disconnected(reason)
        if not self.host_app.trigger.point("disconnected", self, reason):
            return
        self.disconnectProfile(reason)

    @defer.inlineCallbacks
    def _cleanConnection(self, __):
        """method called on disconnection

        used to call profileDisconnected* triggers
        """
        trigger_name = "profileDisconnected"
        for plugin in self._getPluginsList():
            disconnected_cb = getattr(plugin, trigger_name, None)
            if disconnected_cb is not None:
                yield disconnected_cb(self)

    def isConnected(self):
        """Return True is client is fully connected

        client is considered fully connected if transport is started and all plugins
        are initialised
        """
        try:
            transport_connected = bool(self.xmlstream.transport.connected)
        except AttributeError:
            return False

        return self._connected_d is not None and transport_connected

    def entityDisconnect(self):
        if not self.host_app.trigger.point("disconnecting", self):
            return
        log.info(_("Disconnecting..."))
        self.stopService()
        if self._connected_d is not None:
            return self._connected_d
        else:
            return defer.succeed(None)

    ## sending ##

    def IQ(self, type_="set", timeout=60):
        """shortcut to create an IQ element managing deferred

        @param type_(unicode): IQ type ('set' or 'get')
        @param timeout(None, int): timeout in seconds
        @return((D)domish.Element: result stanza
            errback is called if an error stanza is returned
        """
        iq_elt = xmlstream.IQ(self.xmlstream, type_)
        iq_elt.timeout = timeout
        return iq_elt

    def sendError(self, iq_elt, condition, text=None, appCondition=None):
        """Send error stanza build from iq_elt

        @param iq_elt(domish.Element): initial IQ element
        @param condition(unicode): error condition
        """
        iq_error_elt = error.StanzaError(
            condition, text=text, appCondition=appCondition
        ).toResponse(iq_elt)
        self.xmlstream.send(iq_error_elt)

    def generateMessageXML(self, data, post_xml_treatments=None):
        """Generate <message/> stanza from message data

        @param data(dict): message data
            domish element will be put in data['xml']
            following keys are needed:
                - from
                - to
                - uid: can be set to '' if uid attribute is not wanted
                - message
                - type
                - subject
                - extra
        @param post_xml_treatments(Deferred): a Deferred which will be called with data
            once XML is generated
        @return (dict) message data
        """
        data["xml"] = message_elt = domish.Element((None, "message"))
        message_elt["to"] = data["to"].full()
        message_elt["from"] = data["from"].full()
        message_elt["type"] = data["type"]
        if data["uid"]:  # key must be present but can be set to ''
            # by a plugin to avoid id on purpose
            message_elt["id"] = data["uid"]
        for lang, subject in data["subject"].items():
            subject_elt = message_elt.addElement("subject", content=subject)
            if lang:
                subject_elt[(C.NS_XML, "lang")] = lang
        for lang, message in data["message"].items():
            body_elt = message_elt.addElement("body", content=message)
            if lang:
                body_elt[(C.NS_XML, "lang")] = lang
        try:
            thread = data["extra"]["thread"]
        except KeyError:
            if "thread_parent" in data["extra"]:
                raise exceptions.InternalError(
                    "thread_parent found while there is not associated thread"
                )
        else:
            thread_elt = message_elt.addElement("thread", content=thread)
            try:
                thread_elt["parent"] = data["extra"]["thread_parent"]
            except KeyError:
                pass

        if post_xml_treatments is not None:
            post_xml_treatments.callback(data)
        return data

    def addPostXmlCallbacks(self, post_xml_treatments):
        """Used to add class level callbacks at the end of the workflow

        @param post_xml_treatments(D): the same Deferred as in sendMessage trigger
        """
        raise NotImplementedError

    def sendMessage(
            self, to_jid, message, subject=None, mess_type="auto", extra=None, uid=None,
            no_trigger=False):
        r"""Send a message to an entity

        @param to_jid(jid.JID): destinee of the message
        @param message(dict): message body, key is the language (use '' when unknown)
        @param subject(dict): message subject, key is the language (use '' when unknown)
        @param mess_type(str): one of standard message type (cf RFC 6121 §5.2.2) or:
            - auto: for automatic type detection
            - info: for information ("info_type" can be specified in extra)
        @param extra(dict, None): extra data. Key can be:
            - info_type: information type, can be
                TODO
        @param uid(unicode, None): unique id:
            should be unique at least in this XMPP session
            if None, an uuid will be generated
        @param no_trigger (bool): if True, sendMessage[suffix] trigger will no be used
            useful when a message need to be sent without any modification
            /!\ this will also skip encryption methods!
        """
        if subject is None:
            subject = {}
        if extra is None:
            extra = {}

        assert mess_type in C.MESS_TYPE_ALL

        data = {  # dict is similar to the one used in client.onMessage
            "from": self.jid,
            "to": to_jid,
            "uid": uid or str(uuid.uuid4()),
            "message": message,
            "subject": subject,
            "type": mess_type,
            "extra": extra,
            "timestamp": time.time(),
        }
        # XXX: plugin can add their pre XML treatments to this deferred
        pre_xml_treatments = defer.Deferred()
        # XXX: plugin can add their post XML treatments to this deferred
        post_xml_treatments = defer.Deferred()

        if data["type"] == C.MESS_TYPE_AUTO:
            # we try to guess the type
            if data["subject"]:
                data["type"] = C.MESS_TYPE_NORMAL
            elif not data["to"].resource:  # if to JID has a resource,
                                           # the type is not 'groupchat'
                # we may have a groupchat message, we check if the we know this jid
                try:
                    entity_type = self.host_app.memory.getEntityDatum(
                        self, data["to"], C.ENTITY_TYPE
                    )
                    # FIXME: should entity_type manage resources ?
                except (exceptions.UnknownEntityError, KeyError):
                    entity_type = "contact"

                if entity_type == C.ENTITY_TYPE_MUC:
                    data["type"] = C.MESS_TYPE_GROUPCHAT
                else:
                    data["type"] = C.MESS_TYPE_CHAT
            else:
                data["type"] == C.MESS_TYPE_CHAT
            data["type"] == C.MESS_TYPE_CHAT if data["subject"] else C.MESS_TYPE_NORMAL

        # FIXME: send_only is used by libervia's OTR plugin to avoid
        #        the triggers from frontend, and no_trigger do the same
        #        thing internally, this could be unified
        send_only = data["extra"].get("send_only", False)

        if not no_trigger and not send_only:
            # is the session encrypted? If so we indicate it in data
            self.encryption.setEncryptionFlag(data)

            if not self.host_app.trigger.point(
                "sendMessage" + self.trigger_suffix,
                self,
                data,
                pre_xml_treatments,
                post_xml_treatments,
            ):
                return defer.succeed(None)

        log.debug(_("Sending message (type {type}, to {to})")
                    .format(type=data["type"], to=to_jid.full()))

        pre_xml_treatments.addCallback(lambda __: self.generateMessageXML(data, post_xml_treatments))
        pre_xml_treatments.addCallback(lambda __: post_xml_treatments)
        pre_xml_treatments.addErrback(self._cancelErrorTrap)
        post_xml_treatments.addCallback(lambda __: self.sendMessageData(data))
        if send_only:
            log.debug(_("Triggers, storage and echo have been inhibited by the "
                        "'send_only' parameter"))
        else:
            self.addPostXmlCallbacks(post_xml_treatments)
            post_xml_treatments.addErrback(self._cancelErrorTrap)
            post_xml_treatments.addErrback(self.host_app.logErrback)
        pre_xml_treatments.callback(data)
        return pre_xml_treatments

    def _cancelErrorTrap(self, failure):
        """A message sending can be cancelled by a plugin treatment"""
        failure.trap(exceptions.CancelError)

    def isMessagePrintable(self, mess_data):
        """Return True if a message contain payload to show in frontends"""
        return (
            mess_data["message"] or mess_data["subject"]
            or mess_data["extra"].get(C.MESS_KEY_ATTACHMENTS)
            or mess_data["type"] == C.MESS_TYPE_INFO
        )

    def messageAddToHistory(self, data):
        """Store message into database (for local history)

        @param data: message data dictionnary
        @param client: profile's client
        """
        if data["type"] != C.MESS_TYPE_GROUPCHAT:
            # we don't add groupchat message to history, as we get them back
            # and they will be added then

            # we need a message to store
            if self.isMessagePrintable(data):
                self.host_app.memory.addToHistory(self, data)
            else:
                log.warning(
                    "No message found"
                )  # empty body should be managed by plugins before this point
        return data

    def messageGetBridgeArgs(self, data):
        """Generate args to use with bridge from data dict"""
        return (data["uid"], data["timestamp"], data["from"].full(),
                data["to"].full(), data["message"], data["subject"],
                data["type"], data_format.serialise(data["extra"]))


    def messageSendToBridge(self, data):
        """Send message to bridge, so frontends can display it

        @param data: message data dictionnary
        @param client: profile's client
        """
        if data["type"] != C.MESS_TYPE_GROUPCHAT:
            # we don't send groupchat message to bridge, as we get them back
            # and they will be added the

            # we need a message to send something
            if self.isMessagePrintable(data):

                # We send back the message, so all frontends are aware of it
                self.host_app.bridge.messageNew(
                    *self.messageGetBridgeArgs(data),
                    profile=self.profile
                )
            else:
                log.warning(_("No message found"))
        return data

    ## helper methods ##

    def p(self, plugin_name, missing=exceptions.MissingModule):
        """Get a plugin if available

        @param plugin_name(str): name of the plugin
        @param missing(object): value to return if plugin is missing
            if it is a subclass of Exception, it will be raised with a helping str as
            argument.
        @return (object): requested plugin wrapper, or default value
            The plugin wrapper will return the method with client set as first
            positional argument
        """
        return ClientPluginWrapper(self, plugin_name, missing)


@implementer(iwokkel.IDisco)
class SatXMPPClient(SatXMPPEntity, wokkel_client.XMPPClient):
    trigger_suffix = ""
    is_component = False

    def __init__(self, host_app, profile, user_jid, password, host=None,
                 port=C.XMPP_C2S_PORT, max_retries=C.XMPP_MAX_RETRIES):
        # XXX: DNS SRV records are checked when the host is not specified.
        # If no SRV record is found, the host is directly extracted from the JID.
        self.started = time.time()

        # Currently, we use "client/pc/Salut à Toi", but as
        # SàT is multi-frontends and can be used on mobile devices, as a bot,
        # with a web frontend,
        # etc., we should implement a way to dynamically update identities through the
        # bridge
        self.identities = [disco.DiscoIdentity("client", "pc", C.APP_NAME)]
        if sys.platform == "android":
            # for now we consider Android devices to be always phones
            self.identities = [disco.DiscoIdentity("client", "phone", C.APP_NAME)]

        hosts_map = host_app.memory.getConfig(None, "hosts_dict", {})
        if host is None and user_jid.host in hosts_map:
            host_data = hosts_map[user_jid.host]
            if isinstance(host_data, str):
                host = host_data
            elif isinstance(host_data, dict):
                if "host" in host_data:
                    host = host_data["host"]
                if "port" in host_data:
                    port = host_data["port"]
            else:
                log.warning(
                    _("invalid data used for host: {data}").format(data=host_data)
                )
                host_data = None
            if host_data is not None:
                log.info(
                    "using {host}:{port} for host {host_ori} as requested in config"
                    .format(host_ori=user_jid.host, host=host, port=port)
                )

        self.check_certificate = host_app.memory.getParamA(
            "check_certificate", "Connection", profile_key=profile)

        if self.check_certificate:
            tls_required, configurationForTLS = True, None
        else:
            tls_required = False
            configurationForTLS = ssl.CertificateOptions(trustRoot=None)

        wokkel_client.XMPPClient.__init__(
            self, user_jid, password, host or None, port or C.XMPP_C2S_PORT,
            tls_required=tls_required, configurationForTLS=configurationForTLS
        )
        SatXMPPEntity.__init__(self, host_app, profile, max_retries)

        if not self.check_certificate:
            msg = (_("Certificate validation is deactivated, this is unsecure and "
                "somebody may be spying on you. If you have no good reason to disable "
                "certificate validation, please activate \"Check certificate\" in your "
                "settings in \"Connection\" tab."))
            xml_tools.quickNote(host_app, self, msg, _("Security notice"),
                level = C.XMLUI_DATA_LVL_WARNING)


    def _getPluginsList(self):
        for p in self.host_app.plugins.values():
            if C.PLUG_MODE_CLIENT in p._info["modes"]:
                yield p

    def _createSubProtocols(self):
        self.messageProt = SatMessageProtocol(self.host_app)
        self.messageProt.setHandlerParent(self)

        self.roster = SatRosterProtocol(self.host_app)
        self.roster.setHandlerParent(self)

        self.presence = SatPresenceProtocol(self.host_app)
        self.presence.setHandlerParent(self)

    @classmethod
    async def startConnection(cls, host, profile, max_retries):
        try:
            await super(SatXMPPClient, cls).startConnection(host, profile, max_retries)
        except exceptions.CancelError as e:
            log.warning(f"startConnection cancelled: {e}")
            return
        entity = host.profiles[profile]
        # we finally send our presence
        entity.presence.available()

    def entityConnected(self):
        # we want to be sure that we got the roster
        return self.roster.got_roster

    def addPostXmlCallbacks(self, post_xml_treatments):
        post_xml_treatments.addCallback(self.messageProt.completeAttachments)
        post_xml_treatments.addCallback(self.messageAddToHistory)
        post_xml_treatments.addCallback(self.messageSendToBridge)

    def send(self, obj):
        # original send method accept string
        # but we restrict to domish.Element to make trigger treatments easier
        assert isinstance(obj, domish.Element)
        # XXX: this trigger is the last one before sending stanza on wire
        #      it is intended for things like end 2 end encryption.
        #      *DO NOT* cancel (i.e. return False) without very good reason
        #      (out of band transmission for instance).
        #      e2e should have a priority of 0 here, and out of band transmission
        #      a lower priority
        #  FIXME: trigger not used yet, can be uncommented when e2e full stanza
        #         encryption is implemented
        #  if not self.host_app.trigger.point("send", self, obj):
        #      return
        super(SatXMPPClient, self).send(obj)

    @defer.inlineCallbacks
    def sendMessageData(self, mess_data):
        """Convenient method to send message data to stream

        This method will send mess_data[u'xml'] to stream, but a trigger is there
        The trigger can't be cancelled, it's a good place for e2e encryption which
        don't handle full stanza encryption
        This trigger can return a Deferred (it's an asyncPoint)
        @param mess_data(dict): message data as constructed by onMessage workflow
        @return (dict): mess_data (so it can be used in a deferred chain)
        """
        # XXX: This is the last trigger before u"send" (last but one globally)
        #      for sending message.
        #      This is intented for e2e encryption which doesn't do full stanza
        #      encryption (e.g. OTR)
        #      This trigger point can't cancel the method
        yield self.host_app.trigger.asyncPoint("sendMessageData", self, mess_data,
            triggers_no_cancel=True)
        self.send(mess_data["xml"])
        defer.returnValue(mess_data)

    def feedback(self, to_jid, message, extra=None):
        """Send message to frontends

        This message will be an info message, not recorded in history.
        It can be used to give feedback of a command
        @param to_jid(jid.JID): destinee jid
        @param message(unicode): message to send to frontends
        @param extra(None, dict): extra data to use
            in particular, info subtype can be specified with MESS_EXTRA_INFO
        """
        if extra is None:
            extra = {}
        self.host_app.bridge.messageNew(
            uid=str(uuid.uuid4()),
            timestamp=time.time(),
            from_jid=self.jid.full(),
            to_jid=to_jid.full(),
            message={"": message},
            subject={},
            mess_type=C.MESS_TYPE_INFO,
            extra=data_format.serialise(extra),
            profile=self.profile,
        )

    def _finish_connection(self, __):
        d = self.roster.requestRoster()
        d.addCallback(lambda __: super(SatXMPPClient, self)._finish_connection(__))


@implementer(iwokkel.IDisco)
class SatXMPPComponent(SatXMPPEntity, component.Component):
    """XMPP component

    This component are similar but not identical to clients.
    An entry point plugin is launched after component is connected.
    Component need to instantiate MessageProtocol itself
    """

    trigger_suffix = (
        "Component"
    )  # used for to distinguish some trigger points set in SatXMPPEntity
    is_component = True
    sendHistory = (
        False
    )  # XXX: set to True from entry plugin to keep messages in history for received
       #      messages

    def __init__(self, host_app, profile, component_jid, password, host=None, port=None,
                 max_retries=C.XMPP_MAX_RETRIES):
        self.started = time.time()
        if port is None:
            port = C.XMPP_COMPONENT_PORT

        ## entry point ##
        entry_point = host_app.memory.getEntryPoint(profile)
        try:
            self.entry_plugin = host_app.plugins[entry_point]
        except KeyError:
            raise exceptions.NotFound(
                _("The requested entry point ({entry_point}) is not available").format(
                    entry_point=entry_point
                )
            )

        self.identities = [disco.DiscoIdentity("component", "generic", C.APP_NAME)]
        # jid is set automatically on bind by Twisted for Client, but not for Component
        self.jid = component_jid
        if host is None:
            try:
                host = component_jid.host.split(".", 1)[1]
            except IndexError:
                raise ValueError("Can't guess host from jid, please specify a host")
        # XXX: component.Component expect unicode jid, while Client expect jid.JID.
        #      this is not consistent, so we use jid.JID for SatXMPP*
        component.Component.__init__(self, host, port, component_jid.full(), password)
        SatXMPPEntity.__init__(self, host_app, profile, max_retries)

    def _buildDependencies(self, current, plugins, required=True):
        """build recursively dependencies needed for a plugin

        this method build list of plugin needed for a component and raises
        errors if they are not available or not allowed for components
        @param current(object): parent plugin to check
            use entry_point for first call
        @param plugins(list): list of validated plugins, will be filled by the method
            give an empty list for first call
        @param required(bool): True if plugin is mandatory
            for recursive calls only, should not be modified by inital caller
        @raise InternalError: one of the plugin is not handling components
        @raise KeyError: one plugin should be present in self.host_app.plugins but it
                         is not
        """
        if C.PLUG_MODE_COMPONENT not in current._info["modes"]:
            if not required:
                return
            else:
                log.error(
                    _(
                        "Plugin {current_name} is needed for {entry_name}, "
                        "but it doesn't handle component mode"
                    ).format(
                        current_name=current._info["import_name"],
                        entry_name=self.entry_plugin._info["import_name"],
                    )
                )
                raise exceptions.InternalError(_("invalid plugin mode"))

        for import_name in current._info.get(C.PI_DEPENDENCIES, []):
            # plugins are already loaded as dependencies
            # so we know they are in self.host_app.plugins
            dep = self.host_app.plugins[import_name]
            self._buildDependencies(dep, plugins)

        for import_name in current._info.get(C.PI_RECOMMENDATIONS, []):
            # here plugins are only recommendations,
            # so they may not exist in self.host_app.plugins
            try:
                dep = self.host_app.plugins[import_name]
            except KeyError:
                continue
            self._buildDependencies(dep, plugins, required=False)

        if current not in plugins:
            # current can be required for several plugins and so
            # it can already be present in the list
            plugins.append(current)

    def _getPluginsList(self):
        # XXX: for component we don't launch all plugins triggers
        #      but only the ones from which there is a dependency
        plugins = []
        self._buildDependencies(self.entry_plugin, plugins)
        return plugins

    def entityConnected(self):
        # we can now launch entry point
        try:
            start_cb = self.entry_plugin.componentStart
        except AttributeError:
            return
        else:
            return start_cb(self)

    def addPostXmlCallbacks(self, post_xml_treatments):
        if self.sendHistory:
            post_xml_treatments.addCallback(self.messageAddToHistory)

    def getOwnerFromJid(self, to_jid: jid.JID) -> jid.JID:
        """Retrieve "owner" of a component resource from the destination jid of the request

        This method needs plugin XEP-0106 for unescaping, if you use it you must add the
        plugin to your dependencies.
        A "user" part must be present in "to_jid" (otherwise, the component itself is addressed)
        @param to_jid: destination JID of the request
        """
        try:
            unescape = self.host_app.plugins['XEP-0106'].unescape
        except KeyError:
            raise exceptions.MissingPlugin("Plugin XEP-0106 is needed to retrieve owner")
        else:
            user = unescape(to_jid.user)
        if '@' in user:
            # a full jid is specified
            return jid.JID(user)
        else:
            # only user part is specified, we use our own host to build the full jid
            return jid.JID(None, (user, self.host, None))

    def getOwnerAndPeer(self, iq_elt: domish.Element) -> Tuple[jid.JID, jid.JID]:
        """Retrieve owner of a component jid, and the jid of the requesting peer

        "owner" is found by either unescaping full jid from node, or by combining node
        with our host.
        Peer jid is the requesting jid from the IQ element
        @param iq_elt: IQ stanza sent from the requested
        @return: owner and peer JIDs
        """
        to_jid = jid.JID(iq_elt['to'])
        if to_jid.user:
            owner = self.getOwnerFromJid(to_jid)
        else:
            owner = jid.JID(iq_elt["from"]).userhostJID()

        peer_jid = jid.JID(iq_elt["from"])
        return peer_jid, owner



class SatMessageProtocol(xmppim.MessageProtocol):

    def __init__(self, host):
        xmppim.MessageProtocol.__init__(self)
        self.host = host

    @property
    def client(self):
        return self.parent

    def parseMessage(self, message_elt):
        """Parse a message XML and return message_data

        @param message_elt(domish.Element): raw <message> xml
        @param client(SatXMPPClient, None): client to map message id to uid
            if None, mapping will not be done
        @return(dict): message data
        """
        if message_elt.name != "message":
            log.warning(_(
                "parseMessage used with a non <message/> stanza, ignoring: {xml}"
                .format(xml=message_elt.toXml())))
            return {}

        if message_elt.uri is None:
            # wokkel element parsing strip out root namespace
            message_elt.defaultUri = message_elt.uri = C.NS_CLIENT
            for c in message_elt.elements():
                if c.uri is None:
                    c.uri = C.NS_CLIENT
        elif message_elt.uri != C.NS_CLIENT:
            log.warning(_(
                "received <message> with a wrong namespace: {xml}"
                .format(xml=message_elt.toXml())))

        client = self.parent

        if not message_elt.hasAttribute('to'):
            message_elt['to'] = client.jid.full()

        message = {}
        subject = {}
        extra = {}
        data = {
            "from": jid.JID(message_elt["from"]),
            "to": jid.JID(message_elt["to"]),
            "uid": message_elt.getAttribute(
                "uid", str(uuid.uuid4())
            ),  # XXX: uid is not a standard attribute but may be added by plugins
            "message": message,
            "subject": subject,
            "type": message_elt.getAttribute("type", "normal"),
            "extra": extra,
        }

        try:
            message_id = data["extra"]["message_id"] = message_elt["id"]
        except KeyError:
            pass
        else:
            client.mess_id2uid[(data["from"], message_id)] = data["uid"]

        # message
        for e in message_elt.elements(C.NS_CLIENT, "body"):
            message[e.getAttribute((C.NS_XML, "lang"), "")] = str(e)

        # subject
        for e in message_elt.elements(C.NS_CLIENT, "subject"):
            subject[e.getAttribute((C.NS_XML, "lang"), "")] = str(e)

        # delay and timestamp
        try:
            received_timestamp = message_elt._received_timestamp
        except AttributeError:
            # message_elt._received_timestamp should have been set in onMessage
            # but if parseMessage is called directly, it can be missing
            log.debug("missing received timestamp for {message_elt}".format(
                message_elt=message_elt))
            received_timestamp = time.time()

        try:
            delay_elt = next(message_elt.elements(delay.NS_DELAY, "delay"))
        except StopIteration:
            data["timestamp"] = received_timestamp
        else:
            parsed_delay = delay.Delay.fromElement(delay_elt)
            data["timestamp"] = calendar.timegm(parsed_delay.stamp.utctimetuple())
            data["received_timestamp"] = received_timestamp
            if parsed_delay.sender:
                data["delay_sender"] = parsed_delay.sender.full()

        self.host.trigger.point("message_parse", client,  message_elt, data)
        return data

    def _onMessageStartWorkflow(self, cont, client, message_elt, post_treat):
        """Parse message and do post treatments

        It is the first callback called after messageReceived trigger
        @param cont(bool): workflow will continue only if this is True
        @param message_elt(domish.Element): message stanza
            may have be modified by triggers
        @param post_treat(defer.Deferred): post parsing treatments
        """
        if not cont:
            return
        data = self.parseMessage(message_elt)
        post_treat.addCallback(self.completeAttachments)
        post_treat.addCallback(self.skipEmptyMessage)
        post_treat.addCallback(self.addToHistory)
        post_treat.addCallback(self.bridgeSignal, data)
        post_treat.addErrback(self.cancelErrorTrap)
        post_treat.callback(data)

    def onMessage(self, message_elt):
        # TODO: handle threads
        message_elt._received_timestamp = time.time()
        client = self.parent
        if not "from" in message_elt.attributes:
            message_elt["from"] = client.jid.host
        log.debug(_("got message from: {from_}").format(from_=message_elt["from"]))

        # plugin can add their treatments to this deferred
        post_treat = defer.Deferred()

        d = self.host.trigger.asyncPoint(
            "messageReceived", client, message_elt, post_treat
        )

        d.addCallback(self._onMessageStartWorkflow, client, message_elt, post_treat)

    def completeAttachments(self, data):
        """Complete missing metadata of attachments"""
        for attachment in data['extra'].get(C.MESS_KEY_ATTACHMENTS, []):
            if "name" not in attachment:
                name = (Path(unquote(urlparse(attachment['url']).path)).name
                        or C.FILE_DEFAULT_NAME)
                attachment["name"] = name
            if C.MESS_KEY_ATTACHMENTS_MEDIA_TYPE not in attachment:
                media_type = mimetypes.guess_type(attachment['name'], strict=False)[0]
                if media_type:
                    attachment[C.MESS_KEY_ATTACHMENTS_MEDIA_TYPE] = media_type

        return data

    def skipEmptyMessage(self, data):
        if not data["message"] and not data["extra"] and not data["subject"]:
            raise failure.Failure(exceptions.CancelError("Cancelled empty message"))
        return data

    def addToHistory(self, data):
        if data.pop("history", None) == C.HISTORY_SKIP:
            log.debug("history is skipped as requested")
            data["extra"]["history"] = C.HISTORY_SKIP
        else:
            # we need a message to store
            if self.parent.isMessagePrintable(data):
                return self.host.memory.addToHistory(self.parent, data)
            else:
                log.debug("not storing empty message to history: {data}"
                    .format(data=data))

    def bridgeSignal(self, __, data):
        try:
            data["extra"]["received_timestamp"] = str(data["received_timestamp"])
            data["extra"]["delay_sender"] = data["delay_sender"]
        except KeyError:
            pass
        if self.client.encryption.isEncrypted(data):
            data["extra"]["encrypted"] = True
        if data is not None:
            if self.parent.isMessagePrintable(data):
                self.host.bridge.messageNew(
                    data["uid"],
                    data["timestamp"],
                    data["from"].full(),
                    data["to"].full(),
                    data["message"],
                    data["subject"],
                    data["type"],
                    data_format.serialise(data["extra"]),
                    profile=self.parent.profile,
                )
            else:
                log.debug("Discarding bridge signal for empty message: {data}".format(
                    data=data))
        return data

    def cancelErrorTrap(self, failure_):
        """A message sending can be cancelled by a plugin treatment"""
        failure_.trap(exceptions.CancelError)


class SatRosterProtocol(xmppim.RosterClientProtocol):

    def __init__(self, host):
        xmppim.RosterClientProtocol.__init__(self)
        self.host = host
        self.got_roster = defer.Deferred()  # called when roster is received and ready
        # XXX: the two following dicts keep a local copy of the roster
        self._jids = {}  # map from jids to RosterItem: key=jid value=RosterItem
        self._groups = {}  # map from groups to jids: key=group value=set of jids

    def __contains__(self, entity_jid):
        return self.isJidInRoster(entity_jid)

    @property
    def versioning(self):
        """True if server support roster versioning"""
        return (NS_ROSTER_VER, 'ver') in self.parent.xmlstream.features

    @property
    def roster_cache(self):
        """Cache of roster from storage

        This property return a new PersistentDict on each call, it must be loaded
        manually if necessary
        """
        return persistent.PersistentDict(NS_ROSTER_VER, self.parent.profile)

    def _registerItem(self, item):
        """Register item in local cache

        item must be already registered in self._jids before this method is called
        @param item (RosterIem): item added
        """
        log.debug("registering item: {}".format(item.entity.full()))
        if item.entity.resource:
            log.warning(
                "Received a roster item with a resource, this is not common but not "
                "restricted by RFC 6121, this case may be not well tested."
            )
        if not item.subscriptionTo:
            if not item.subscriptionFrom:
                log.info(
                    _("There's no subscription between you and [{}]!").format(
                        item.entity.full()
                    )
                )
            else:
                log.info(_("You are not subscribed to [{}]!").format(item.entity.full()))
        if not item.subscriptionFrom:
            log.info(_("[{}] is not subscribed to you!").format(item.entity.full()))

        for group in item.groups:
            self._groups.setdefault(group, set()).add(item.entity)

    @defer.inlineCallbacks
    def _cacheRoster(self, version):
        """Serialise local roster and save it to storage

        @param version(unicode): version of roster in local cache
        """
        roster_cache = self.roster_cache
        yield roster_cache.clear()
        roster_cache[ROSTER_VER_KEY] = version
        for roster_jid, roster_item in self._jids.items():
            roster_jid_s = roster_jid.full()
            roster_item_elt = roster_item.toElement().toXml()
            roster_cache[roster_jid_s] = roster_item_elt

    @defer.inlineCallbacks
    def resync(self):
        """Ask full roster to resync database

        this should not be necessary, but may be used if user suspsect roster
        to be somehow corrupted
        """
        roster_cache = self.roster_cache
        yield roster_cache.clear()
        self._jids.clear()
        self._groups.clear()
        yield self.requestRoster()

    @defer.inlineCallbacks
    def requestRoster(self):
        """Ask the server for Roster list """
        if self.versioning:
            log.info(_("our server support roster versioning, we use it"))
            roster_cache = self.roster_cache
            yield roster_cache.load()
            try:
                version = roster_cache[ROSTER_VER_KEY]
            except KeyError:
                log.info(_("no roster in cache, we start fresh"))
                # u"" means we use versioning without valid roster in cache
                version = ""
            else:
                log.info(_("We have roster v{version} in cache").format(version=version))
                # we deserialise cached roster to our local cache
                for roster_jid_s, roster_item_elt_s in roster_cache.items():
                    if roster_jid_s == ROSTER_VER_KEY:
                        continue
                    roster_jid = jid.JID(roster_jid_s)
                    roster_item_elt = generic.parseXml(roster_item_elt_s.encode('utf-8'))
                    roster_item = xmppim.RosterItem.fromElement(roster_item_elt)
                    self._jids[roster_jid] = roster_item
                    self._registerItem(roster_item)
        else:
            log.warning(_("our server doesn't support roster versioning"))
            version = None

        log.debug("requesting roster")
        roster = yield self.getRoster(version=version)
        if roster is None:
            log.debug("empty roster result received, we'll get roster item with roster "
                      "pushes")
        else:
            # a full roster is received
            self._groups.clear()
            self._jids = roster
            for item in roster.values():
                if not item.subscriptionTo and not item.subscriptionFrom and not item.ask:
                    # XXX: current behaviour: we don't want contact in our roster list
                    # if there is no presence subscription
                    # may change in the future
                    log.info(
                        "Removing contact {} from roster because there is no presence "
                        "subscription".format(
                            item.jid
                        )
                    )
                    self.removeItem(item.entity)  # FIXME: to be checked
                else:
                    self._registerItem(item)
            yield self._cacheRoster(roster.version)

        if not self.got_roster.called:
            # got_roster may already be called if we use resync()
            self.got_roster.callback(None)

    def removeItem(self, to_jid):
        """Remove a contact from roster list
        @param to_jid: a JID instance
        @return: Deferred
        """
        return xmppim.RosterClientProtocol.removeItem(self, to_jid)

    def getAttributes(self, item):
        """Return dictionary of attributes as used in bridge from a RosterItem

        @param item: RosterItem
        @return: dictionary of attributes
        """
        item_attr = {
            "to": str(item.subscriptionTo),
            "from": str(item.subscriptionFrom),
            "ask": str(item.ask),
        }
        if item.name:
            item_attr["name"] = item.name
        return item_attr

    def setReceived(self, request):
        item = request.item
        entity = item.entity
        log.info(_("adding {entity} to roster").format(entity=entity.full()))
        if request.version is not None:
            # we update the cache in storage
            roster_cache = self.roster_cache
            roster_cache[entity.full()] = item.toElement().toXml()
            roster_cache[ROSTER_VER_KEY] = request.version

        try:  # update the cache for the groups the contact has been removed from
            left_groups = set(self._jids[entity].groups).difference(item.groups)
            for group in left_groups:
                jids_set = self._groups[group]
                jids_set.remove(entity)
                if not jids_set:
                    del self._groups[group]
        except KeyError:
            pass  # no previous item registration (or it's been cleared)
        self._jids[entity] = item
        self._registerItem(item)
        self.host.bridge.newContact(
            entity.full(), self.getAttributes(item), item.groups, self.parent.profile
        )

    def removeReceived(self, request):
        entity = request.item.entity
        log.info(_("removing {entity} from roster").format(entity=entity.full()))
        if request.version is not None:
            # we update the cache in storage
            roster_cache = self.roster_cache
            try:
                del roster_cache[request.item.entity.full()]
            except KeyError:
                # because we don't use load(), cache won't have the key, but it
                # will be deleted from storage anyway
                pass
            roster_cache[ROSTER_VER_KEY] = request.version

        # we first remove item from local cache (self._groups and self._jids)
        try:
            item = self._jids.pop(entity)
        except KeyError:
            log.error(
                "Received a roster remove event for an item not in cache ({})".format(
                    entity
                )
            )
            return
        for group in item.groups:
            try:
                jids_set = self._groups[group]
                jids_set.remove(entity)
                if not jids_set:
                    del self._groups[group]
            except KeyError:
                log.warning(
                    f"there is no cache for the group [{group}] of the removed roster "
                    f"item [{entity}]"
                )

        # then we send the bridge signal
        self.host.bridge.contactDeleted(entity.full(), self.parent.profile)

    def getGroups(self):
        """Return a list of groups"""
        return list(self._groups.keys())

    def getItem(self, entity_jid):
        """Return RosterItem for a given jid

        @param entity_jid(jid.JID): jid of the contact
        @return(RosterItem, None): RosterItem instance
            None if contact is not in cache
        """
        return self._jids.get(entity_jid, None)

    def getJids(self):
        """Return all jids of the roster"""
        return list(self._jids.keys())

    def isJidInRoster(self, entity_jid):
        """Return True if jid is in roster"""
        if not isinstance(entity_jid, jid.JID):
            raise exceptions.InternalError(
                f"a JID is expected, not {type(entity_jid)}: {entity_jid!r}")
        return entity_jid in self._jids

    def isPresenceAuthorised(self, entity_jid):
        """Return True if entity is authorised to see our presence"""
        try:
            item = self._jids[entity_jid.userhostJID()]
        except KeyError:
            return False
        return item.subscriptionFrom

    def getItems(self):
        """Return all items of the roster"""
        return list(self._jids.values())

    def getJidsFromGroup(self, group):
        try:
            return self._groups[group]
        except KeyError:
            raise exceptions.UnknownGroupError(group)

    def getJidsSet(self, type_, groups=None):
        """Helper method to get a set of jids

        @param type_(unicode): one of:
            C.ALL: get all jids from roster
            C.GROUP: get jids from groups (listed in "groups")
        @groups(list[unicode]): list of groups used if type_==C.GROUP
        @return (set(jid.JID)): set of selected jids
        """
        if type_ == C.ALL and groups is not None:
            raise ValueError("groups must not be set for {} type".format(C.ALL))

        if type_ == C.ALL:
            return set(self.getJids())
        elif type_ == C.GROUP:
            jids = set()
            for group in groups:
                jids.update(self.getJidsFromGroup(group))
            return jids
        else:
            raise ValueError("Unexpected type_ {}".format(type_))

    def getNick(self, entity_jid):
        """Return a nick name for an entity

        return nick choosed by user if available
        else return user part of entity_jid
        """
        item = self.getItem(entity_jid)
        if item is None:
            return entity_jid.user
        else:
            return item.name or entity_jid.user


class SatPresenceProtocol(xmppim.PresenceClientProtocol):

    def __init__(self, host):
        xmppim.PresenceClientProtocol.__init__(self)
        self.host = host

    @property
    def client(self):
        return self.parent

    def send(self, obj):
        presence_d = defer.succeed(None)
        if not self.host.trigger.point("Presence send", self.parent, obj, presence_d):
            return
        presence_d.addCallback(lambda __: super(SatPresenceProtocol, self).send(obj))
        return presence_d

    def availableReceived(self, entity, show=None, statuses=None, priority=0):
        if not statuses:
            statuses = {}

        if None in statuses:  # we only want string keys
            statuses[C.PRESENCE_STATUSES_DEFAULT] = statuses.pop(None)

        if not self.host.trigger.point(
            "presence_received", self.parent, entity, show, priority, statuses
        ):
            return

        self.host.memory.setPresenceStatus(
            entity, show or "", int(priority), statuses, self.parent.profile
        )

        # now it's time to notify frontends
        self.host.bridge.presenceUpdate(
            entity.full(), show or "", int(priority), statuses, self.parent.profile
        )

    def unavailableReceived(self, entity, statuses=None):
        log.debug(
            _("presence update for [%(entity)s] (unavailable, statuses=%(statuses)s)")
            % {"entity": entity, C.PRESENCE_STATUSES: statuses}
        )

        if not statuses:
            statuses = {}

        if None in statuses:  # we only want string keys
            statuses[C.PRESENCE_STATUSES_DEFAULT] = statuses.pop(None)

        if not self.host.trigger.point(
            "presence_received", self.parent, entity, C.PRESENCE_UNAVAILABLE, 0, statuses,
        ):
            return

        # now it's time to notify frontends
        # if the entity is not known yet in this session or is already unavailable,
        # there is no need to send an unavailable signal
        try:
            presence = self.host.memory.getEntityDatum(
                self.client, entity, "presence"
            )
        except (KeyError, exceptions.UnknownEntityError):
            # the entity has not been seen yet in this session
            pass
        else:
            if presence.show != C.PRESENCE_UNAVAILABLE:
                self.host.bridge.presenceUpdate(
                    entity.full(),
                    C.PRESENCE_UNAVAILABLE,
                    0,
                    statuses,
                    self.parent.profile,
                )

        self.host.memory.setPresenceStatus(
            entity, C.PRESENCE_UNAVAILABLE, 0, statuses, self.parent.profile
        )

    def available(self, entity=None, show=None, statuses=None, priority=None):
        """Set a presence and statuses.

        @param entity (jid.JID): entity
        @param show (unicode): value in ('unavailable', '', 'away', 'xa', 'chat', 'dnd')
        @param statuses (dict{unicode: unicode}): multilingual statuses with
            the entry key beeing a language code on 2 characters or "default".
        """
        if priority is None:
            try:
                priority = int(
                    self.host.memory.getParamA(
                        "Priority", "Connection", profile_key=self.parent.profile
                    )
                )
            except ValueError:
                priority = 0

        if statuses is None:
            statuses = {}

        # default for us is None for wokkel
        # so we must temporarily switch to wokkel's convention...
        if C.PRESENCE_STATUSES_DEFAULT in statuses:
            statuses[None] = statuses.pop(C.PRESENCE_STATUSES_DEFAULT)

        presence_elt = xmppim.AvailablePresence(entity, show, statuses, priority)

        # ... before switching back
        if None in statuses:
            statuses["default"] = statuses.pop(None)

        if not self.host.trigger.point("presence_available", presence_elt, self.parent):
            return
        return self.send(presence_elt)

    @defer.inlineCallbacks
    def subscribed(self, entity):
        yield self.parent.roster.got_roster
        xmppim.PresenceClientProtocol.subscribed(self, entity)
        self.host.memory.delWaitingSub(entity.userhost(), self.parent.profile)
        item = self.parent.roster.getItem(entity)
        if (
            not item or not item.subscriptionTo
        ):  # we automatically subscribe to 'to' presence
            log.debug(_('sending automatic "from" subscription request'))
            self.subscribe(entity)

    def unsubscribed(self, entity):
        xmppim.PresenceClientProtocol.unsubscribed(self, entity)
        self.host.memory.delWaitingSub(entity.userhost(), self.parent.profile)

    def subscribedReceived(self, entity):
        log.debug(_("subscription approved for [%s]") % entity.userhost())
        self.host.bridge.subscribe("subscribed", entity.userhost(), self.parent.profile)

    def unsubscribedReceived(self, entity):
        log.debug(_("unsubscription confirmed for [%s]") % entity.userhost())
        self.host.bridge.subscribe("unsubscribed", entity.userhost(), self.parent.profile)

    @defer.inlineCallbacks
    def subscribeReceived(self, entity):
        log.debug(_("subscription request from [%s]") % entity.userhost())
        yield self.parent.roster.got_roster
        item = self.parent.roster.getItem(entity)
        if item and item.subscriptionTo:
            # We automatically accept subscription if we are already subscribed to
            # contact presence
            log.debug(_("sending automatic subscription acceptance"))
            self.subscribed(entity)
        else:
            self.host.memory.addWaitingSub(
                "subscribe", entity.userhost(), self.parent.profile
            )
            self.host.bridge.subscribe(
                "subscribe", entity.userhost(), self.parent.profile
            )

    @defer.inlineCallbacks
    def unsubscribeReceived(self, entity):
        log.debug(_("unsubscription asked for [%s]") % entity.userhost())
        yield self.parent.roster.got_roster
        item = self.parent.roster.getItem(entity)
        if item and item.subscriptionFrom:  # we automatically remove contact
            log.debug(_("automatic contact deletion"))
            self.host.delContact(entity, self.parent.profile)
        self.host.bridge.subscribe("unsubscribe", entity.userhost(), self.parent.profile)


@implementer(iwokkel.IDisco)
class SatDiscoProtocol(disco.DiscoClientProtocol):

    def __init__(self, host):
        disco.DiscoClientProtocol.__init__(self)

    def getDiscoInfo(self, requestor, target, nodeIdentifier=""):
        # those features are implemented in Wokkel (or sat_tmp.wokkel)
        # and thus are always available
        return [disco.DiscoFeature(NS_X_DATA),
                disco.DiscoFeature(NS_XML_ELEMENT),
                disco.DiscoFeature(NS_DISCO_INFO)]

    def getDiscoItems(self, requestor, target, nodeIdentifier=""):
        return []


class SatFallbackHandler(generic.FallbackHandler):
    def __init__(self, host):
        generic.FallbackHandler.__init__(self)

    def iqFallback(self, iq):
        if iq.handled is True:
            return
        log.debug("iqFallback: xml = [%s]" % (iq.toXml()))
        generic.FallbackHandler.iqFallback(self, iq)


class SatVersionHandler(generic.VersionHandler):

    def getDiscoInfo(self, requestor, target, node):
        # XXX: We need to work around wokkel's behaviour (namespace not added if there
        #      is a node) as it cause issues with XEP-0115 & PEP (XEP-0163): there is a
        #      node when server ask for disco info, and not when we generate the key, so
        #      the hash is used with different disco features, and when the server (seen
        #      on ejabberd) generate its own hash for security check it reject our
        #      features (resulting in e.g. no notification on PEP)
        return generic.VersionHandler.getDiscoInfo(self, requestor, target, None)


@implementer(iwokkel.IDisco)
class SatIdentityHandler(XMPPHandler):
    """Manage disco Identity of SàT."""
    # TODO: dynamic identity update (see docstring). Note that a XMPP entity can have
    #       several identities

    def getDiscoInfo(self, requestor, target, nodeIdentifier=""):
        return self.parent.identities

    def getDiscoItems(self, requestor, target, nodeIdentifier=""):
        return []
