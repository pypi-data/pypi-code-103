#!/usr/bin/env python3
#-*- coding: utf-8 -*-

# Copyright (c) 2016 Jérôme Poisson
# Copyright (c) 2015-2016 Adrien Cossa
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
XMPP Message Archive Management protocol.

This protocol is specified in
U{XEP-0313<http://xmpp.org/extensions/xep-0313.html>}.
"""


from zope.interface import implementer

from twisted.words.xish import domish
from twisted.python import log
from twisted.internet import defer
from twisted.words.protocols.jabber import error

from sat_pubsub import const
from sat_pubsub import backend
from wokkel import pubsub

from wokkel import rsm
from wokkel import mam
from wokkel import delay


@implementer(mam.IMAMResource)
class MAMResource(object):
    _errorMap = backend.PubSubResourceFromBackend._errorMap

    def __init__(self, backend_):
        self.backend = backend_

    def _mapErrors(self, failure):
        # XXX: come from backend.PubsubResourceFromBackend
        e = failure.trap(*list(self._errorMap.keys()))

        condition, pubsubCondition, feature = self._errorMap[e]
        msg = failure.value.msg

        if pubsubCondition:
            exc = pubsub.PubSubError(condition, pubsubCondition, feature, msg)
        else:
            exc = error.StanzaError(condition, text=msg)

        raise exc

    def onArchiveRequest(self, mam_request):
        """

        @param mam_request: The MAM archive request.
        @type mam_request: L{MAMQueryReques<wokkel.mam.MAMRequest>}

        @return: A tuple with list of message data (id, element, data) and RSM element
        @rtype: C{tuple}
        """
        # FIXME: bad result ordering
        try:
            pep = mam_request.delegated
        except AttributeError:
            pep = False
        ext_data = {'pep': pep}
        if mam_request.form:
            ext_data['filters'] = list(mam_request.form.fields.values())
        if mam_request.rsm is None:
            if const.VAL_RSM_MAX_DEFAULT != None:
                log.msg("MAM request without RSM limited to {}".format(const.VAL_RSM_MAX_DEFAULT))
                ext_data['rsm'] = rsm.RSMRequest(const.VAL_RSM_MAX_DEFAULT)
        else:
            ext_data['rsm'] = mam_request.rsm

        if mam_request.orderBy:
            ext_data['order_by'] = mam_request.orderBy

        d = defer.ensureDeferred(
            self.backend.getItemsData(mam_request.node, mam_request.sender,
                                      mam_request.recipient, None, None, ext_data)
        )

        def make_message(elt):
            # XXX: http://xmpp.org/extensions/xep-0297.html#sect-idp629952 (rule 3)
            message = domish.Element((const.NS_CLIENT, "message"))
            event = message.addElement((pubsub.NS_PUBSUB_EVENT, "event"))
            items = event.addElement('items')
            items["node"] = mam_request.node
            items.addChild(elt)
            return message

        def cb(items_data):
            msg_data = []
            rsm_elt = None
            attributes = {}
            for item_data in items_data:
                if item_data.item.name == 'set' and item_data.item.uri == rsm.NS_RSM:
                    assert rsm_elt is None
                    rsm_elt = item_data.item
                    if rsm_elt.first:
                        # XXX: we check if it is the last page using initial request data
                        #      and RSM element data. In this case, we must have the
                        #      "complete"
                        #      attribute set to "true".
                        page_max = int(rsm_elt.first['index']) +  mam_request.rsm.max
                        count = int(str(rsm_elt.count))
                        if page_max >= count:
                            # the maximum items which can be displayed is equal to or
                            # above the total number of items, which means we are complete
                            attributes['complete'] = "true"
                    else:
                        log.msg("WARNING: no <first> element in RSM request: {xml}".format(
                            xml = rsm_elt.toXml().encode('utf-8')))
                elif item_data.item.name == 'item':
                    msg_data.append([item_data.item['id'], make_message(item_data.item),
                                     item_data.created])
                else:
                    log.msg("WARNING: unknown element: {}".format(item_data.item.name))
            if pep:
                # we need to send privileged message
                # so me manage the sending ourself, and return
                # an empty msg_data list to avoid double sending
                for data in msg_data:
                    self.forwardPEPMessage(mam_request, *data)
                msg_data = []
            return (msg_data, rsm_elt, attributes)

        d.addErrback(self._mapErrors)
        d.addCallback(cb)
        return d

    def forwardPEPMessage(self, mam_request, id_, elt, created):
        msg = domish.Element((None, 'message'))
        msg['from'] = self.backend.server_jid.full()
        msg['to'] = mam_request.sender.full()
        result = msg.addElement((mam.NS_MAM, 'result'))
        if mam_request.query_id is not None:
            result['queryid'] = mam_request.query_id
        result['id'] = id_
        forward = result.addElement((const.NS_FORWARD, 'forwarded'))
        forward.addChild(delay.Delay(created).toElement())
        forward.addChild(elt)
        self.backend.privilege.sendMessage(msg)

    def onPrefsGetRequest(self, requestor):
        """

        @param requestor: JID of the requestor.
        @type requestor: L{JID<twisted.words.protocols.jabber.jid.JID>}

        @return: The current settings.
        @rtype: L{wokkel.mam.MAMPrefs}
        """
        # TODO: return the actual current settings
        return mam.MAMPrefs()

    def onPrefsSetRequest(self, prefs, requestor):
        """

        @param prefs: The new settings to set.
        @type prefs: L{wokkel.mam.MAMPrefs}

        @param requestor: JID of the requestor.
        @type requestor: L{JID<twisted.words.protocols.jabber.jid.JID>}

        @return: The settings that have actually been set.
        @rtype: L{wokkel.mam.MAMPrefs}
        """
        # TODO: set the new settings and return them
        return mam.MAMPrefs()
