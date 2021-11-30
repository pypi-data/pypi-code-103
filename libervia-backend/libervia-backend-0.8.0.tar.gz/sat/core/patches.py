import copy
from twisted.words.protocols.jabber import xmlstream, sasl, client as tclient, jid
from wokkel import client
from sat.core.constants import Const as C
from sat.core.log import getLogger

log = getLogger(__name__)

"""This module applies monkey patches to Twisted and Wokkel
   First part handle certificate validation during XMPP connectionand are temporary
   (until merged upstream).
   Second part add a trigger point to send and onElement method of XmlStream
   """


## certificate validation patches


class XMPPClient(client.XMPPClient):

    def __init__(self, jid, password, host=None, port=5222,
                 tls_required=True, configurationForTLS=None):
        self.jid = jid
        self.domain = jid.host.encode('idna')
        self.host = host
        self.port = port

        factory = HybridClientFactory(
            jid, password, tls_required=tls_required,
            configurationForTLS=configurationForTLS)

        client.StreamManager.__init__(self, factory)


def HybridClientFactory(jid, password, tls_required=True, configurationForTLS=None):
    a = HybridAuthenticator(jid, password, tls_required, configurationForTLS)

    return xmlstream.XmlStreamFactory(a)


class HybridAuthenticator(client.HybridAuthenticator):
    res_binding = True

    def __init__(self, jid, password, tls_required=True, configurationForTLS=None):
        xmlstream.ConnectAuthenticator.__init__(self, jid.host)
        self.jid = jid
        self.password = password
        self.tls_required = tls_required
        self.configurationForTLS = configurationForTLS

    def associateWithStream(self, xs):
        xmlstream.ConnectAuthenticator.associateWithStream(self, xs)

        tlsInit = xmlstream.TLSInitiatingInitializer(
            xs, required=self.tls_required, configurationForTLS=self.configurationForTLS)
        xs.initializers = [client.client.CheckVersionInitializer(xs),
                           tlsInit,
                           CheckAuthInitializer(xs, self.res_binding)]


# XmlStream triggers


class XmlStream(xmlstream.XmlStream):
    """XmlStream which allows to add hooks"""

    def __init__(self, authenticator):
        xmlstream.XmlStream.__init__(self, authenticator)
        # hooks at this level should not modify content
        # so it's not needed to handle priority as with triggers
        self._onElementHooks = []
        self._sendHooks = []

    def addHook(self, hook_type, callback):
        """Add a send or receive hook"""
        conflict_msg = f"Hook conflict: can't add {hook_type} hook {callback}"
        if hook_type == C.STREAM_HOOK_RECEIVE:
            if callback not in self._onElementHooks:
                self._onElementHooks.append(callback)
            else:
                log.warning(conflict_msg)
        elif hook_type == C.STREAM_HOOK_SEND:
            if callback not in self._sendHooks:
                self._sendHooks.append(callback)
            else:
                log.warning(conflict_msg)
        else:
            raise ValueError(f"Invalid hook type: {hook_type}")

    def onElement(self, element):
        for hook in self._onElementHooks:
            hook(element)
        xmlstream.XmlStream.onElement(self, element)

    def send(self, obj):
        for hook in self._sendHooks:
            hook(obj)
        xmlstream.XmlStream.send(self, obj)


# Binding activation (needed for stream management, XEP-0198)


class CheckAuthInitializer(client.CheckAuthInitializer):

    def __init__(self, xs, res_binding):
        super(CheckAuthInitializer, self).__init__(xs)
        self.res_binding = res_binding

    def initialize(self):
        # XXX: modification of client.CheckAuthInitializer which has optional
        #      resource binding, and which doesn't do deprecated
        #      SessionInitializer
        if (sasl.NS_XMPP_SASL, 'mechanisms') in self.xmlstream.features:
            inits = [(sasl.SASLInitiatingInitializer, True)]
            if self.res_binding:
                inits.append((tclient.BindInitializer, True)),

            for initClass, required in inits:
                init = initClass(self.xmlstream)
                init.required = required
                self.xmlstream.initializers.append(init)
        elif (tclient.NS_IQ_AUTH_FEATURE, 'auth') in self.xmlstream.features:
            self.xmlstream.initializers.append(
                    tclient.IQAuthInitializer(self.xmlstream))
        else:
            raise Exception("No available authentication method found")


# jid fix

def internJID(jidstring):
    """
    Return interned JID.

    @rtype: L{JID}
    """
    # XXX: this interJID return a copy of the cached jid
    #      this avoid modification of cached jid as JID is mutable
    # TODO: propose this upstream

    if jidstring in jid.__internJIDs:
        return copy.copy(jid.__internJIDs[jidstring])
    else:
        j = jid.JID(jidstring)
        jid.__internJIDs[jidstring] = j
        return copy.copy(j)


def apply():
    # certificate validation
    client.XMPPClient = XMPPClient
    # XmlStream triggers
    xmlstream.XmlStreamFactory.protocol = XmlStream
    # jid fix
    jid.internJID = internJID
