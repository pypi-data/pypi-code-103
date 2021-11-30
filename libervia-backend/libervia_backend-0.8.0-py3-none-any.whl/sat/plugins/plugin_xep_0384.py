#!/usr/bin/env python3

# SAT plugin for OMEMO encryption
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

import logging
import random
import base64
from functools import partial
from xml.sax.saxutils import quoteattr
from sat.core.i18n import _, D_
from sat.core.constants import Const as C
from sat.core.log import getLogger
from sat.core import exceptions
from twisted.internet import defer, reactor
from twisted.words.xish import domish
from twisted.words.protocols.jabber import jid
from twisted.words.protocols.jabber import error as jabber_error
from sat.memory import persistent
from sat.tools import xml_tools
try:
    import omemo
    from omemo import exceptions as omemo_excpt
    from omemo.extendedpublicbundle import ExtendedPublicBundle
except ImportError:
    raise exceptions.MissingModule(
        'Missing module omemo, please download/install it. You can use '
        '"pip install omemo"'
    )
try:
    from omemo_backend_signal import BACKEND as omemo_backend
except ImportError:
    raise exceptions.MissingModule(
        'Missing module omemo-backend-signal, please download/install it. You can use '
        '"pip install omemo-backend-signal"'
    )

log = getLogger(__name__)

PLUGIN_INFO = {
    C.PI_NAME: "OMEMO",
    C.PI_IMPORT_NAME: "XEP-0384",
    C.PI_TYPE: "SEC",
    C.PI_PROTOCOLS: ["XEP-0384"],
    C.PI_DEPENDENCIES: ["XEP-0163", "XEP-0280", "XEP-0334", "XEP-0060"],
    C.PI_RECOMMENDATIONS: ["XEP-0045", "XEP-0359", C.TEXT_CMDS],
    C.PI_MAIN: "OMEMO",
    C.PI_HANDLER: "no",
    C.PI_DESCRIPTION: _("""Implementation of OMEMO"""),
}

OMEMO_MIN_VER = (0, 11, 0)
NS_OMEMO = "eu.siacs.conversations.axolotl"
NS_OMEMO_DEVICES = NS_OMEMO + ".devicelist"
NS_OMEMO_BUNDLE = NS_OMEMO + ".bundles:{device_id}"
KEY_STATE = "STATE"
KEY_DEVICE_ID = "DEVICE_ID"
KEY_SESSION = "SESSION"
KEY_TRUST = "TRUST"
# devices which have been automatically trusted by policy like BTBV
KEY_AUTO_TRUST = "AUTO_TRUST"
# list of peer bare jids where trust UI has been used at least once
# this is useful to activate manual trust with BTBV policy
KEY_MANUAL_TRUST = "MANUAL_TRUST"
KEY_ACTIVE_DEVICES = "DEVICES"
KEY_INACTIVE_DEVICES = "INACTIVE_DEVICES"
KEY_ALL_JIDS = "ALL_JIDS"
# time before plaintext cache for MUC is expired
# expressed in seconds, reset on each new MUC message
MUC_CACHE_TTL = 60 * 5

PARAM_CATEGORY = "Security"
PARAM_NAME = "omemo_policy"


# we want to manage log emitted by omemo module ourselves

class SatHandler(logging.Handler):

    def emit(self, record):
        log.log(record.levelname, record.getMessage())

    @staticmethod
    def install():
        omemo_sm_logger = logging.getLogger("omemo.SessionManager")
        omemo_sm_logger.propagate = False
        omemo_sm_logger.addHandler(SatHandler())


SatHandler.install()


def b64enc(data):
    return base64.b64encode(bytes(bytearray(data))).decode("US-ASCII")


def promise2Deferred(promise_):
    """Create a Deferred and fire it when promise is resolved

    @param promise_(promise.Promise): promise to convert
    @return (defer.Deferred): deferred instance linked to the promise
    """
    d = defer.Deferred()
    promise_.then(d.callback, d.errback)
    return d


class OmemoStorage(omemo.Storage):

    def __init__(self, client, device_id, all_jids):
        self.own_bare_jid_s = client.jid.userhost()
        self.device_id = device_id
        self.all_jids = all_jids
        self.data = client._xep_0384_data

    @property
    def is_async(self):
        return True

    def setCb(self, deferred, callback):
        """Associate Deferred and callback

        callback of omemo.Storage expect a boolean with success state then result
        Deferred on the other hand use 2 methods for callback and errback
        This method use partial to call callback with boolean then result when
        Deferred is called
        """
        deferred.addCallback(partial(callback, True))
        deferred.addErrback(partial(callback, False))

    def _checkJid(self, bare_jid):
        """Check if jid is known, and store it if not

        @param bare_jid(unicode): bare jid to check
        @return (D): Deferred fired when jid is stored
        """
        if bare_jid in self.all_jids:
            return defer.succeed(None)
        else:
            self.all_jids.add(bare_jid)
            d = self.data.force(KEY_ALL_JIDS, self.all_jids)
            return d

    def loadOwnData(self, callback):
        callback(True, {'own_bare_jid': self.own_bare_jid_s,
                        'own_device_id': self.device_id})

    def storeOwnData(self, callback, own_bare_jid, own_device_id):
        if own_bare_jid != self.own_bare_jid_s or own_device_id != self.device_id:
            raise exceptions.InternalError('bare jid or device id inconsistency!')
        callback(True, None)

    def loadState(self, callback):
        d = self.data.get(KEY_STATE)
        self.setCb(d, callback)

    def storeState(self, callback, state):
        d = self.data.force(KEY_STATE, state)
        self.setCb(d, callback)

    def loadSession(self, callback, bare_jid, device_id):
        key = '\n'.join([KEY_SESSION, bare_jid, str(device_id)])
        d = self.data.get(key)
        self.setCb(d, callback)

    def storeSession(self, callback, bare_jid, device_id, session):
        key = '\n'.join([KEY_SESSION, bare_jid, str(device_id)])
        d = self.data.force(key, session)
        self.setCb(d, callback)

    def deleteSession(self, callback, bare_jid, device_id):
        key = '\n'.join([KEY_SESSION, bare_jid, str(device_id)])
        d = self.data.remove(key)
        self.setCb(d, callback)

    def loadActiveDevices(self, callback, bare_jid):
        key = '\n'.join([KEY_ACTIVE_DEVICES, bare_jid])
        d = self.data.get(key, {})
        if callback is not None:
            self.setCb(d, callback)
        return d

    def loadInactiveDevices(self, callback, bare_jid):
        key = '\n'.join([KEY_INACTIVE_DEVICES, bare_jid])
        d = self.data.get(key, {})
        if callback is not None:
            self.setCb(d, callback)
        return d

    def storeActiveDevices(self, callback, bare_jid, devices):
        key = '\n'.join([KEY_ACTIVE_DEVICES, bare_jid])
        d = self._checkJid(bare_jid)
        d.addCallback(lambda _: self.data.force(key, devices))
        self.setCb(d, callback)

    def storeInactiveDevices(self, callback, bare_jid, devices):
        key = '\n'.join([KEY_INACTIVE_DEVICES, bare_jid])
        d = self._checkJid(bare_jid)
        d.addCallback(lambda _: self.data.force(key, devices))
        self.setCb(d, callback)

    def storeTrust(self, callback, bare_jid, device_id, trust):
        key = '\n'.join([KEY_TRUST, bare_jid, str(device_id)])
        d = self.data.force(key, trust)
        self.setCb(d, callback)

    def loadTrust(self, callback, bare_jid, device_id):
        key = '\n'.join([KEY_TRUST, bare_jid, str(device_id)])
        d = self.data.get(key)
        if callback is not None:
            self.setCb(d, callback)
        return d

    def listJIDs(self, callback):
        d = defer.succeed(self.all_jids)
        if callback is not None:
            self.setCb(d, callback)
        return d

    def _deleteJID_logResults(self, results):
        failed = [success for success, __ in results if not success]
        if failed:
            log.warning(
                "delete JID failed for {failed_count} on {total_count} operations"
                .format(failed_count=len(failed), total_count=len(results)))
        else:
            log.info(
                "Delete JID operation succeed ({total_count} operations)."
                .format(total_count=len(results)))

    def _deleteJID_gotDevices(self, results, bare_jid):
        assert len(results) == 2
        active_success, active_devices = results[0]
        inactive_success, inactive_devices = results[0]
        d_list = []
        for success, devices in results:
            if not success:
                log.warning("Can't retrieve devices for {bare_jid}: {reason}"
                    .format(bare_jid=bare_jid, reason=active_devices))
            else:
                for device_id in devices:
                    for key in (KEY_SESSION, KEY_TRUST):
                        k = '\n'.join([key, bare_jid, str(device_id)])
                        d_list.append(self.data.remove(k))

        d_list.append(self.data.remove(KEY_ACTIVE_DEVICES, bare_jid))
        d_list.append(self.data.remove(KEY_INACTIVE_DEVICES, bare_jid))
        d_list.append(lambda __: self.all_jids.discard(bare_jid))
        # FIXME: there is a risk of race condition here,
        #        if self.all_jids is modified between discard and force)
        d_list.append(lambda __: self.data.force(KEY_ALL_JIDS, self.all_jids))
        d = defer.DeferredList(d_list)
        d.addCallback(self._deleteJID_logResults)
        return d

    def deleteJID(self, callback, bare_jid):
        """Retrieve all (in)actives devices of bare_jid, and delete all related keys"""
        d_list = []

        key = '\n'.join([KEY_ACTIVE_DEVICES, bare_jid])
        d_list.append(self.data.get(key, []))

        key = '\n'.join([KEY_INACTIVE_DEVICES, bare_jid])
        d_inactive = self.data.get(key, {})
        # inactive devices are returned as a dict mapping from devices_id to timestamp
        # but we only need devices ids
        d_inactive.addCallback(lambda devices: [k for k, __ in devices])

        d_list.append(d_inactive)
        d = defer.DeferredList(d_list)
        d.addCallback(self._deleteJID_gotDevices, bare_jid)
        if callback is not None:
            self.setCb(d, callback)
        return d


class SatOTPKPolicy(omemo.DefaultOTPKPolicy):
    pass


class OmemoSession:
    """Wrapper to use omemo.OmemoSession with Deferred"""

    def __init__(self, session):
        self._session = session

    @property
    def republish_bundle(self):
        return self._session.republish_bundle

    @property
    def public_bundle(self):
        return self._session.public_bundle

    @classmethod
    def create(cls, client, storage, my_device_id = None):
        omemo_session_p = omemo.SessionManager.create(
            storage,
            SatOTPKPolicy,
            omemo_backend,
            client.jid.userhost(),
            my_device_id)
        d = promise2Deferred(omemo_session_p)
        d.addCallback(lambda session: cls(session))
        return d

    def newDeviceList(self, jid, devices):
        jid = jid.userhost()
        new_device_p = self._session.newDeviceList(jid, devices)
        return promise2Deferred(new_device_p)

    def getDevices(self, bare_jid=None):
        bare_jid = bare_jid.userhost()
        get_devices_p = self._session.getDevices(bare_jid=bare_jid)
        return promise2Deferred(get_devices_p)

    def buildSession(self, bare_jid, device, bundle):
        bare_jid = bare_jid.userhost()
        build_session_p = self._session.buildSession(bare_jid, int(device), bundle)
        return promise2Deferred(build_session_p)

    def deleteSession(self, bare_jid, device):
        bare_jid = bare_jid.userhost()
        delete_session_p = self._session.deleteSession(
            bare_jid=bare_jid, device=int(device))
        return promise2Deferred(delete_session_p)

    def encryptMessage(self, bare_jids, message, bundles=None, expect_problems=None):
        """Encrypt a message

        @param bare_jids(iterable[jid.JID]): destinees of the message
        @param message(unicode): message to encode
        @param bundles(dict[jid.JID, dict[int, ExtendedPublicBundle]):
            entities => devices => bundles map
        @return D(dict): encryption data
        """
        bare_jids = [e.userhost() for e in bare_jids]
        if bundles is not None:
            bundles = {e.userhost(): v for e, v in bundles.items()}
        encrypt_mess_p = self._session.encryptMessage(
            bare_jids=bare_jids,
            plaintext=message.encode(),
            bundles=bundles,
            expect_problems=expect_problems)
        return promise2Deferred(encrypt_mess_p)

    def encryptRatchetForwardingMessage(
        self, bare_jids, bundles=None, expect_problems=None):
        bare_jids = [e.userhost() for e in bare_jids]
        if bundles is not None:
            bundles = {e.userhost(): v for e, v in bundles.items()}
        encrypt_ratchet_fwd_p = self._session.encryptRatchetForwardingMessage(
            bare_jids=bare_jids,
            bundles=bundles,
            expect_problems=expect_problems)
        return promise2Deferred(encrypt_ratchet_fwd_p)

    def decryptMessage(self, bare_jid, device, iv, message, is_pre_key_message,
                       ciphertext, additional_information=None, allow_untrusted=False):
        bare_jid = bare_jid.userhost()
        decrypt_mess_p = self._session.decryptMessage(
            bare_jid=bare_jid,
            device=int(device),
            iv=iv,
            message=message,
            is_pre_key_message=is_pre_key_message,
            ciphertext=ciphertext,
            additional_information=additional_information,
            allow_untrusted=allow_untrusted
            )
        return promise2Deferred(decrypt_mess_p)

    def decryptRatchetForwardingMessage(
        self, bare_jid, device, iv, message, is_pre_key_message,
        additional_information=None, allow_untrusted=False):
        bare_jid = bare_jid.userhost()
        decrypt_ratchet_fwd_p = self._session.decryptRatchetForwardingMessage(
            bare_jid=bare_jid,
            device=int(device),
            iv=iv,
            message=message,
            is_pre_key_message=is_pre_key_message,
            additional_information=additional_information,
            allow_untrusted=allow_untrusted
            )
        return promise2Deferred(decrypt_ratchet_fwd_p)

    def setTrust(self, bare_jid, device, key, trusted):
        bare_jid = bare_jid.userhost()
        setTrust_p = self._session.setTrust(
            bare_jid=bare_jid,
            device=int(device),
            key=key,
            trusted=trusted,
        )
        return promise2Deferred(setTrust_p)

    def resetTrust(self, bare_jid, device):
        bare_jid = bare_jid.userhost()
        resetTrust_p = self._session.resetTrust(
            bare_jid=bare_jid,
            device=int(device),
        )
        return promise2Deferred(resetTrust_p)

    def getTrustForJID(self, bare_jid):
        bare_jid = bare_jid.userhost()
        get_trust_p = self._session.getTrustForJID(bare_jid=bare_jid)
        return promise2Deferred(get_trust_p)


class OMEMO:

    params = """
    <params>
    <individual>
    <category name="{category_name}" label="{category_label}">
        <param name="{param_name}" label={param_label} type="list" security="3">
            <option value="manual" label={opt_manual_lbl} />
            <option value="btbv" label={opt_btbv_lbl} selected="true" />
        </param>
     </category>
    </individual>
    </params>
    """.format(
        category_name=PARAM_CATEGORY,
        category_label=D_("Security"),
        param_name=PARAM_NAME,
        param_label=quoteattr(D_("OMEMO default trust policy")),
        opt_manual_lbl=quoteattr(D_("Manual trust (more secure)")),
        opt_btbv_lbl=quoteattr(
            D_("Blind Trust Before Verification (more user friendly)")),
    )

    def __init__(self, host):
        log.info(_("OMEMO plugin initialization (omemo module v{version})").format(
            version=omemo.__version__))
        version = tuple(map(int, omemo.__version__.split('.')[:3]))
        if version < OMEMO_MIN_VER:
            log.warning(_(
                "Your version of omemo module is too old: {v[0]}.{v[1]}.{v[2]} is "
                "minimum required, please update.").format(v=OMEMO_MIN_VER))
            raise exceptions.CancelError("module is too old")
        self.host = host
        host.memory.updateParams(self.params)
        self._p_hints = host.plugins["XEP-0334"]
        self._p_carbons = host.plugins["XEP-0280"]
        self._p = host.plugins["XEP-0060"]
        self._m = host.plugins.get("XEP-0045")
        self._sid = host.plugins.get("XEP-0359")
        host.trigger.add("messageReceived", self._messageReceivedTrigger, priority=100050)
        host.trigger.add("sendMessageData", self._sendMessageDataTrigger)
        self.host.registerEncryptionPlugin(self, "OMEMO", NS_OMEMO, 100)
        pep = host.plugins['XEP-0163']
        pep.addPEPEvent(
            "OMEMO_DEVICES", NS_OMEMO_DEVICES,
            lambda itemsEvent, profile: defer.ensureDeferred(
                self.onNewDevices(itemsEvent, profile))
        )
        try:
            self.text_cmds = self.host.plugins[C.TEXT_CMDS]
        except KeyError:
            log.info(_("Text commands not available"))
        else:
            self.text_cmds.registerTextCommands(self)

    # Text commands #

    async def cmd_omemo_reset(self, client, mess_data):
        """reset OMEMO session (use only if encryption is broken)

        @command(one2one):
        """
        if not client.encryption.isEncryptionRequested(mess_data, NS_OMEMO):
            feedback = _(
                "You need to have OMEMO encryption activated to reset the session")
            self.text_cmds.feedBack(client, feedback, mess_data)
            return False
        to_jid = mess_data["to"].userhostJID()
        session = client._xep_0384_session
        devices = await session.getDevices(to_jid)

        for device in devices['active']:
            log.debug(f"deleting session for device {device}")
            await session.deleteSession(to_jid, device=device)

        log.debug("Sending an empty message to trigger key exchange")
        await client.sendMessage(to_jid, {'': ''})

        feedback = _("OMEMO session has been reset")
        self.text_cmds.feedBack(client, feedback, mess_data)
        return False

    async def trustUICb(
            self, xmlui_data, trust_data, expect_problems=None, profile=C.PROF_KEY_NONE):
        if C.bool(xmlui_data.get('cancelled', 'false')):
            return {}
        client = self.host.getClient(profile)
        session = client._xep_0384_session
        stored_data = client._xep_0384_data
        manual_trust = await stored_data.get(KEY_MANUAL_TRUST, set())
        auto_trusted_cache = {}
        answer = xml_tools.XMLUIResult2DataFormResult(xmlui_data)
        blind_trust = C.bool(answer.get('blind_trust', C.BOOL_FALSE))
        for key, value in answer.items():
            if key.startswith('trust_'):
                trust_id = key[6:]
            else:
                continue
            data = trust_data[trust_id]
            if blind_trust:
                # user request to restore blind trust for this entity
                # so if the entity is present in manual trust, we remove it
                if data["jid"].full() in manual_trust:
                    manual_trust.remove(data["jid"].full())
                    await stored_data.aset(KEY_MANUAL_TRUST, manual_trust)
            elif data["jid"].full() not in manual_trust:
                # validating this trust UI implies that we activate manual mode for
                # this entity (used for BTBV policy)
                manual_trust.add(data["jid"].full())
                await stored_data.aset(KEY_MANUAL_TRUST, manual_trust)
            trust = C.bool(value)

            if not trust:
                # if device is not trusted, we check if it must be removed from auto
                # trusted devices list
                bare_jid_s = data['jid'].userhost()
                key = f"{KEY_AUTO_TRUST}\n{bare_jid_s}"
                if bare_jid_s not in auto_trusted_cache:
                    auto_trusted_cache[bare_jid_s] = await stored_data.get(
                        key, default=set())
                auto_trusted = auto_trusted_cache[bare_jid_s]
                if data['device'] in auto_trusted:
                    # as we don't trust this device anymore, we can remove it from the
                    # list of automatically trusted devices
                    auto_trusted.remove(data['device'])
                    await stored_data.aset(key, auto_trusted)
                    log.info(D_(
                        "device {device} from {peer_jid} is not an auto-trusted device "
                        "anymore").format(device=data['device'], peer_jid=bare_jid_s))

            await session.setTrust(
                data["jid"],
                data["device"],
                data["ik"],
                trusted=trust,
            )
            if not trust and expect_problems is not None:
                expect_problems.setdefault(data['jid'].userhost(), set()).add(
                    data['device']
                )
        return {}

    async def getTrustUI(self, client, entity_jid=None, trust_data=None, submit_id=None):
        """Generate a XMLUI to manage trust

        @param entity_jid(None, jid.JID): jid of entity to manage
            None to use trust_data
        @param trust_data(None, dict): devices data:
            None to use entity_jid
            else a dict mapping from trust ids (unicode) to devices data,
            where a device data must have the following keys:
                - jid(jid.JID): bare jid of the device owner
                - device(int): device id
                - ik(bytes): identity key
            and may have the following key:
                - trusted(bool): True if device is trusted
        @param submit_id(None, unicode): submit_id to use
            if None set UI callback to trustUICb
        @return D(xmlui): trust management form
        """
        # we need entity_jid xor trust_data
        assert entity_jid and not trust_data or not entity_jid and trust_data
        if entity_jid and entity_jid.resource:
            raise ValueError("A bare jid is expected")

        session = client._xep_0384_session
        stored_data = client._xep_0384_data

        if trust_data is None:
            cache = client._xep_0384_cache.setdefault(entity_jid, {})
            trust_data = {}
            if self._m is not None and self._m.isJoinedRoom(client, entity_jid):
                trust_jids = self.getJIDsForRoom(client, entity_jid)
            else:
                trust_jids = [entity_jid]
            for trust_jid in trust_jids:
                trust_session_data = await session.getTrustForJID(trust_jid)
                bare_jid_s = trust_jid.userhost()
                for device_id, trust_info in trust_session_data['active'].items():
                    if trust_info is None:
                        # device has never been (un)trusted, we have to retrieve its
                        # fingerprint (i.e. identity key or "ik") through public bundle
                        if device_id not in cache:
                            bundles, missing = await self.getBundles(client,
                                                                     trust_jid,
                                                                     [device_id])
                            if device_id not in bundles:
                                log.warning(_(
                                    "Can't find bundle for device {device_id} of user "
                                    "{bare_jid}, ignoring").format(device_id=device_id,
                                                                    bare_jid=bare_jid_s))
                                continue
                            cache[device_id] = bundles[device_id]
                        # TODO: replace False below by None when undecided
                        #       trusts are handled
                        trust_info = {
                            "key": cache[device_id].ik,
                            "trusted": False
                        }

                    ik = trust_info["key"]
                    trust_id = str(hash((bare_jid_s, device_id, ik)))
                    trust_data[trust_id] = {
                        "jid": trust_jid,
                        "device": device_id,
                        "ik": ik,
                        "trusted": trust_info["trusted"],
                        }

        if submit_id is None:
            submit_id = self.host.registerCallback(
                lambda data, profile: defer.ensureDeferred(
                    self.trustUICb(data, trust_data=trust_data, profile=profile)),
                with_data=True,
                one_shot=True)
        xmlui = xml_tools.XMLUI(
            panel_type = C.XMLUI_FORM,
            title = D_("OMEMO trust management"),
            submit_id = submit_id
        )
        xmlui.addText(D_(
            "This is OMEMO trusting system. You'll see below the devices of your "
            "contacts, and a checkbox to trust them or not. A trusted device "
            "can read your messages in plain text, so be sure to only validate "
            "devices that you are sure are belonging to your contact. It's better "
            "to do this when you are next to your contact and her/his device, so "
            "you can check the \"fingerprint\" (the number next to the device) "
            "yourself. Do *not* validate a device if the fingerprint is wrong!"))

        xmlui.changeContainer("label")
        xmlui.addLabel(D_("This device ID"))
        xmlui.addText(str(client._xep_0384_device_id))
        xmlui.addLabel(D_("This device fingerprint"))
        ik_hex = session.public_bundle.ik.hex().upper()
        fp_human = ' '.join([ik_hex[i:i+8] for i in range(0, len(ik_hex), 8)])
        xmlui.addText(fp_human)
        xmlui.addEmpty()
        xmlui.addEmpty()

        if entity_jid is not None:
            omemo_policy = self.host.memory.getParamA(
                PARAM_NAME, PARAM_CATEGORY, profile_key=client.profile
            )
            if omemo_policy == 'btbv':
                xmlui.addLabel(D_("Automatically trust new devices?"))
                # blind trust is always disabled when UI is requested
                # as submitting UI is a verification which should disable it.
                xmlui.addBool("blind_trust", value=C.BOOL_FALSE)
                xmlui.addEmpty()
                xmlui.addEmpty()

        auto_trust_cache = {}

        for trust_id, data in trust_data.items():
            bare_jid_s = data['jid'].userhost()
            if bare_jid_s not in auto_trust_cache:
                key = f"{KEY_AUTO_TRUST}\n{bare_jid_s}"
                auto_trust_cache[bare_jid_s] = await stored_data.get(key, set())
            xmlui.addLabel(D_("Contact"))
            xmlui.addJid(data['jid'])
            xmlui.addLabel(D_("Device ID"))
            xmlui.addText(str(data['device']))
            xmlui.addLabel(D_("Fingerprint"))
            ik_hex = data['ik'].hex().upper()
            fp_human = ' '.join([ik_hex[i:i+8] for i in range(0, len(ik_hex), 8)])
            xmlui.addText(fp_human)
            xmlui.addLabel(D_("Trust this device?"))
            xmlui.addBool("trust_{}".format(trust_id),
                          value=C.boolConst(data.get('trusted', False)))
            if data['device'] in auto_trust_cache[bare_jid_s]:
                xmlui.addEmpty()
                xmlui.addLabel(D_("(automatically trusted)"))


            xmlui.addEmpty()
            xmlui.addEmpty()

        return xmlui

    async def profileConnected(self, client):
        if self._m is not None:
            # we keep plain text message for MUC messages we send
            # as we can't encrypt for our own device
            client._xep_0384_muc_cache = {}
            # and we keep them only for some time, in case something goes wrong
            # with the MUC
            client._xep_0384_muc_cache_timer = None

        # FIXME: is _xep_0384_ready needed? can we use profileConnecting?
        #        Workflow should be checked
        client._xep_0384_ready = defer.Deferred()
        # we first need to get devices ids (including our own)
        persistent_dict = persistent.LazyPersistentBinaryDict("XEP-0384", client.profile)
        client._xep_0384_data = persistent_dict
        # all known devices of profile
        devices = await self.getDevices(client)
        # and our own device id
        device_id = await persistent_dict.get(KEY_DEVICE_ID)
        if device_id is None:
            log.info(_("We have no identity for this device yet, let's generate one"))
            # we have a new device, we create device_id
            device_id = random.randint(1, 2**31-1)
            # we check that it's really unique
            while device_id in devices:
                device_id = random.randint(1, 2**31-1)
            # and we save it
            persistent_dict[KEY_DEVICE_ID] = device_id

        log.debug(f"our OMEMO device id is {device_id}")

        if device_id not in devices:
            log.debug(f"our device id ({device_id}) is not in the list, adding it")
            devices.add(device_id)
            await defer.ensureDeferred(self.setDevices(client, devices))

        all_jids = await persistent_dict.get(KEY_ALL_JIDS, set())

        omemo_storage = OmemoStorage(client, device_id, all_jids)
        omemo_session = await OmemoSession.create(client, omemo_storage, device_id)
        client._xep_0384_cache = {}
        client._xep_0384_session = omemo_session
        client._xep_0384_device_id = device_id
        await omemo_session.newDeviceList(client.jid, devices)
        if omemo_session.republish_bundle:
            log.info(_("Saving public bundle for this device ({device_id})").format(
                device_id=device_id))
            await defer.ensureDeferred(
                self.setBundle(client, omemo_session.public_bundle, device_id)
            )
        client._xep_0384_ready.callback(None)
        del client._xep_0384_ready


    ## XMPP PEP nodes manipulation

    # devices

    def parseDevices(self, items):
        """Parse devices found in items

        @param items(iterable[domish.Element]): items as retrieved by getItems
        @return set[int]: parsed devices
        """
        devices = set()
        if len(items) > 1:
            log.warning(_("OMEMO devices list is stored in more that one items, "
                          "this is not expected"))
        if items:
            try:
                list_elt = next(items[0].elements(NS_OMEMO, 'list'))
            except StopIteration:
                log.warning(_("no list element found in OMEMO devices list"))
                return devices
            for device_elt in list_elt.elements(NS_OMEMO, 'device'):
                try:
                    device_id = int(device_elt['id'])
                except KeyError:
                    log.warning(_('device element is missing "id" attribute: {elt}')
                                .format(elt=device_elt.toXml()))
                except ValueError:
                    log.warning(_('invalid device id: {device_id}').format(
                        device_id=device_elt['id']))
                else:
                    devices.add(device_id)
        return devices

    @defer.inlineCallbacks
    def getDevices(self, client, entity_jid=None):
        """Retrieve list of registered OMEMO devices

        @param entity_jid(jid.JID, None): get devices from this entity
            None to get our own devices
        @return (set(int)): list of devices
        """
        if entity_jid is not None:
            assert not entity_jid.resource
        try:
            items, metadata = yield self._p.getItems(client, entity_jid, NS_OMEMO_DEVICES)
        except exceptions.NotFound:
            log.info(_("there is no node to handle OMEMO devices"))
            defer.returnValue(set())

        devices = self.parseDevices(items)
        defer.returnValue(devices)

    async def setDevices(self, client, devices):
        log.debug(f"setting devices with {', '.join(str(d) for d in devices)}")
        list_elt = domish.Element((NS_OMEMO, 'list'))
        for device in devices:
            device_elt = list_elt.addElement('device')
            device_elt['id'] = str(device)
        try:
            await self._p.sendItem(
                client, None, NS_OMEMO_DEVICES, list_elt,
                item_id=self._p.ID_SINGLETON,
                extra={
                    self._p.EXTRA_PUBLISH_OPTIONS: {self._p.OPT_MAX_ITEMS: 1},
                    self._p.EXTRA_ON_PRECOND_NOT_MET: "publish_without_options",
                }
            )
        except Exception as e:
            log.warning(_("Can't set devices: {reason}").format(reason=e))

    # bundles

    @defer.inlineCallbacks
    def getBundles(self, client, entity_jid, devices_ids):
        """Retrieve public bundles of an entity devices

        @param entity_jid(jid.JID): bare jid of entity
        @param devices_id(iterable[int]): ids of the devices bundles to retrieve
        @return (tuple(dict[int, ExtendedPublicBundle], list(int))):
            - bundles collection:
                * key is device_id
                * value is parsed bundle
            - set of bundles not found
        """
        assert not entity_jid.resource
        bundles = {}
        missing = set()
        for device_id in devices_ids:
            node = NS_OMEMO_BUNDLE.format(device_id=device_id)
            try:
                items, metadata = yield self._p.getItems(client, entity_jid, node)
            except exceptions.NotFound:
                log.warning(_("Bundle missing for device {device_id}")
                    .format(device_id=device_id))
                missing.add(device_id)
                continue
            except jabber_error.StanzaError as e:
                log.warning(_("Can't get bundle for device {device_id}: {reason}")
                    .format(device_id=device_id, reason=e))
                continue
            if not items:
                log.warning(_("no item found in node {node}, can't get public bundle "
                              "for device {device_id}").format(node=node,
                                                                device_id=device_id))
                continue
            if len(items) > 1:
                log.warning(_("more than one item found in {node}, "
                              "this is not expected").format(node=node))
            item = items[0]
            try:
                bundle_elt = next(item.elements(NS_OMEMO, 'bundle'))
                signedPreKeyPublic_elt = next(bundle_elt.elements(
                    NS_OMEMO, 'signedPreKeyPublic'))
                signedPreKeySignature_elt = next(bundle_elt.elements(
                    NS_OMEMO, 'signedPreKeySignature'))
                identityKey_elt = next(bundle_elt.elements(
                    NS_OMEMO, 'identityKey'))
                prekeys_elt =  next(bundle_elt.elements(
                    NS_OMEMO, 'prekeys'))
            except StopIteration:
                log.warning(_("invalid bundle for device {device_id}, ignoring").format(
                    device_id=device_id))
                continue

            try:
                spkPublic = base64.b64decode(str(signedPreKeyPublic_elt))
                spkSignature = base64.b64decode(
                    str(signedPreKeySignature_elt))

                ik = base64.b64decode(str(identityKey_elt))
                spk = {
                    "key": spkPublic,
                    "id": int(signedPreKeyPublic_elt['signedPreKeyId'])
                }
                otpks = []
                for preKeyPublic_elt in prekeys_elt.elements(NS_OMEMO, 'preKeyPublic'):
                    preKeyPublic = base64.b64decode(str(preKeyPublic_elt))
                    otpk = {
                        "key": preKeyPublic,
                        "id": int(preKeyPublic_elt['preKeyId'])
                    }
                    otpks.append(otpk)

            except Exception as e:
                log.warning(_("error while decoding key for device {device_id}: {msg}")
                            .format(device_id=device_id, msg=e))
                continue

            bundles[device_id] = ExtendedPublicBundle.parse(omemo_backend, ik, spk,
                                                            spkSignature, otpks)

        defer.returnValue((bundles, missing))

    async def setBundle(self, client, bundle, device_id):
        """Set public bundle for this device.

        @param bundle(ExtendedPublicBundle): bundle to publish
        """
        log.debug(_("updating bundle for {device_id}").format(device_id=device_id))
        bundle = bundle.serialize(omemo_backend)
        bundle_elt = domish.Element((NS_OMEMO, 'bundle'))
        signedPreKeyPublic_elt = bundle_elt.addElement(
            "signedPreKeyPublic",
            content=b64enc(bundle["spk"]['key']))
        signedPreKeyPublic_elt['signedPreKeyId'] = str(bundle["spk"]['id'])

        bundle_elt.addElement(
            "signedPreKeySignature",
            content=b64enc(bundle["spk_signature"]))

        bundle_elt.addElement(
            "identityKey",
            content=b64enc(bundle["ik"]))

        prekeys_elt = bundle_elt.addElement('prekeys')
        for otpk in bundle["otpks"]:
            preKeyPublic_elt = prekeys_elt.addElement(
                'preKeyPublic',
                content=b64enc(otpk["key"]))
            preKeyPublic_elt['preKeyId'] = str(otpk['id'])

        node = NS_OMEMO_BUNDLE.format(device_id=device_id)
        try:
            await self._p.sendItem(
                client, None, node, bundle_elt, item_id=self._p.ID_SINGLETON,
                extra={
                    self._p.EXTRA_PUBLISH_OPTIONS: {self._p.OPT_MAX_ITEMS: 1},
                    self._p.EXTRA_ON_PRECOND_NOT_MET: "publish_without_options",
                }
            )
        except Exception as e:
            log.warning(_("Can't set bundle: {reason}").format(reason=e))

    ## PEP node events callbacks

    async def onNewDevices(self, itemsEvent, profile):
        log.debug("devices list has been updated")
        client = self.host.getClient(profile)
        try:
            omemo_session = client._xep_0384_session
        except AttributeError:
            await client._xep_0384_ready
            omemo_session = client._xep_0384_session
        entity = itemsEvent.sender

        devices = self.parseDevices(itemsEvent.items)
        await omemo_session.newDeviceList(entity, devices)

        if entity == client.jid.userhostJID():
            own_device = client._xep_0384_device_id
            if own_device not in devices:
                log.warning(_("Our own device is missing from devices list, fixing it"))
                devices.add(own_device)
                await self.setDevices(client, devices)

    ## triggers

    async def policyBTBV(self, client, feedback_jid, expect_problems, undecided):
        session = client._xep_0384_session
        stored_data = client._xep_0384_data
        for pb in undecided.values():
            peer_jid = jid.JID(pb.bare_jid)
            device = pb.device
            ik = pb.ik
            key = f"{KEY_AUTO_TRUST}\n{pb.bare_jid}"
            auto_trusted = await stored_data.get(key, default=set())
            auto_trusted.add(device)
            await stored_data.aset(key, auto_trusted)
            await session.setTrust(peer_jid, device, ik, True)

        user_msg =  D_(
            "Not all destination devices are trusted, unknown devices will be blind "
            "trusted due to the OMEMO Blind Trust Before Verification policy. If you "
            "want a more secure workflow, please activate \"manual\" OMEMO policy in "
            "settings' \"Security\" tab.\nFollowing fingerprint have been automatically "
            "trusted:\n{devices}"
        ).format(
            devices = ', '.join(
                f"- {pb.device} ({pb.bare_jid}): {pb.ik.hex().upper()}"
                for pb in undecided.values()
            )
        )
        client.feedback(feedback_jid, user_msg)

    async def policyManual(self, client, feedback_jid, expect_problems, undecided):
        trust_data = {}
        for trust_id, data in undecided.items():
            trust_data[trust_id] = {
                'jid': jid.JID(data.bare_jid),
                'device':  data.device,
                'ik': data.ik}

        user_msg =  D_("Not all destination devices are trusted, we can't encrypt "
                       "message in such a situation. Please indicate if you trust "
                       "those devices or not in the trust manager before we can "
                       "send this message")
        client.feedback(feedback_jid, user_msg)
        xmlui = await self.getTrustUI(client, trust_data=trust_data, submit_id="")

        answer = await xml_tools.deferXMLUI(
            self.host,
            xmlui,
            action_extra={
                "meta_encryption_trust": NS_OMEMO,
            },
            profile=client.profile)
        await self.trustUICb(answer, trust_data, expect_problems, client.profile)

    async def handleProblems(
        self, client, feedback_jid, bundles, expect_problems, problems):
        """Try to solve problems found by EncryptMessage

        @param feedback_jid(jid.JID): bare jid where the feedback message must be sent
        @param bundles(dict): bundles data as used in EncryptMessage
            already filled with known bundles, missing bundles
            need to be added to it
            This dict is updated
        @param problems(list): exceptions raised by EncryptMessage
        @param expect_problems(dict): known problems to expect, used in encryptMessage
            This dict will list devices where problems can be ignored
            (those devices won't receive the encrypted data)
            This dict is updated
        """
        # FIXME: not all problems are handled yet
        undecided = {}
        missing_bundles = {}
        found_bundles = None
        cache = client._xep_0384_cache
        for problem in problems:
            if isinstance(problem, omemo_excpt.TrustException):
                if problem.problem == 'undecided':
                    undecided[str(hash(problem))] = problem
                elif problem.problem == 'untrusted':
                    expect_problems.setdefault(problem.bare_jid, set()).add(
                        problem.device)
                    log.info(_(
                        "discarding untrusted device {device_id} with key {device_key} "
                        "for {entity}").format(
                            device_id=problem.device,
                            device_key=problem.ik.hex().upper(),
                            entity=problem.bare_jid,
                        )
                    )
                else:
                    log.error(
                        f"Unexpected trust problem: {problem.problem!r} for device "
                        f"{problem.device} for {problem.bare_jid}, ignoring device")
                    expect_problems.setdefault(problem.bare_jid, set()).add(
                        problem.device)
            elif isinstance(problem, omemo_excpt.MissingBundleException):
                pb_entity = jid.JID(problem.bare_jid)
                entity_cache = cache.setdefault(pb_entity, {})
                entity_bundles = bundles.setdefault(pb_entity, {})
                if problem.device in entity_cache:
                    entity_bundles[problem.device] = entity_cache[problem.device]
                else:
                    found_bundles, missing = await self.getBundles(
                        client, pb_entity, [problem.device])
                    entity_cache.update(bundles)
                    entity_bundles.update(found_bundles)
                    if problem.device in missing:
                        missing_bundles.setdefault(pb_entity, set()).add(
                            problem.device)
                        expect_problems.setdefault(problem.bare_jid, set()).add(
                            problem.device)
            elif isinstance(problem, omemo_excpt.NoEligibleDevicesException):
                if undecided or found_bundles:
                    # we may have new devices after this run, so let's continue for now
                    continue
                else:
                    raise problem
            else:
                raise problem

        for peer_jid, devices in missing_bundles.items():
            devices_s = [str(d) for d in devices]
            log.warning(
                _("Can't retrieve bundle for device(s) {devices} of entity {peer}, "
                  "the message will not be readable on this/those device(s)").format(
                    devices=", ".join(devices_s), peer=peer_jid.full()))
            client.feedback(
                feedback_jid,
                D_("You're destinee {peer} has missing encryption data on some of "
                   "his/her device(s) (bundle on device {devices}), the message won't  "
                   "be readable on this/those device.").format(
                   peer=peer_jid.full(), devices=", ".join(devices_s)))

        if undecided:
            omemo_policy = self.host.memory.getParamA(
                PARAM_NAME, PARAM_CATEGORY, profile_key=client.profile
            )
            if omemo_policy == 'btbv':
                # we first separate entities which have been trusted manually
                manual_trust = await client._xep_0384_data.get(KEY_MANUAL_TRUST)
                if manual_trust:
                    manual_undecided = {}
                    for hash_, pb in undecided.items():
                        if pb.bare_jid in manual_trust:
                            manual_undecided[hash_] = pb
                    for hash_ in manual_undecided:
                        del undecided[hash_]
                else:
                    manual_undecided = None

                if undecided:
                    # we do the automatic trust here
                    await self.policyBTBV(
                        client, feedback_jid, expect_problems, undecided)
                if manual_undecided:
                    # here user has to manually trust new devices from entities already
                    # verified
                    await self.policyManual(
                        client, feedback_jid, expect_problems, manual_undecided)
            elif omemo_policy == 'manual':
                await self.policyManual(
                    client, feedback_jid, expect_problems, undecided)
            else:
                raise exceptions.InternalError(f"Unexpected OMEMO policy: {omemo_policy}")

    async def encryptMessage(self, client, entity_bare_jids, message, feedback_jid=None):
        if feedback_jid is None:
            if len(entity_bare_jids) != 1:
                log.error(
                    "feedback_jid must be provided when message is encrypted for more "
                    "than one entities")
                feedback_jid = entity_bare_jids[0]
        omemo_session = client._xep_0384_session
        expect_problems = {}
        bundles = {}
        loop_idx = 0
        try:
            while True:
                if loop_idx > 10:
                    msg = _("Too many iterations in encryption loop")
                    log.error(msg)
                    raise exceptions.InternalError(msg)
                # encryptMessage may fail, in case of e.g. trust issue or missing bundle
                try:
                    if not message:
                        encrypted = await omemo_session.encryptRatchetForwardingMessage(
                            entity_bare_jids,
                            bundles,
                            expect_problems = expect_problems)
                    else:
                        encrypted = await omemo_session.encryptMessage(
                            entity_bare_jids,
                            message,
                            bundles,
                            expect_problems = expect_problems)
                except omemo_excpt.EncryptionProblemsException as e:
                    # we know the problem to solve, we can try to fix them
                    await self.handleProblems(
                        client,
                        feedback_jid=feedback_jid,
                        bundles=bundles,
                        expect_problems=expect_problems,
                        problems=e.problems)
                    loop_idx += 1
                else:
                    break
        except Exception as e:
            msg = _("Can't encrypt message for {entities}: {reason}".format(
                entities=', '.join(e.full() for e in entity_bare_jids), reason=e))
            log.warning(msg)
            extra = {C.MESS_EXTRA_INFO: C.EXTRA_INFO_ENCR_ERR}
            client.feedback(feedback_jid, msg, extra)
            raise e

        defer.returnValue(encrypted)

    @defer.inlineCallbacks
    def _messageReceivedTrigger(self, client, message_elt, post_treat):
        try:
            encrypted_elt = next(message_elt.elements(NS_OMEMO, "encrypted"))
        except StopIteration:
            # no OMEMO message here
            defer.returnValue(True)

        # we have an encrypted message let's decrypt it

        from_jid = jid.JID(message_elt['from'])

        if message_elt.getAttribute("type") == C.MESS_TYPE_GROUPCHAT:
            # with group chat, we must get the real jid for decryption
            # and use the room as feedback_jid

            if self._m is None:
                # plugin XEP-0045 (MUC) is not available
                defer.returnValue(True)

            room_jid = from_jid.userhostJID()
            feedback_jid = room_jid
            if self._sid is not None:
                mess_id = self._sid.getOriginId(message_elt)
            else:
                mess_id = None

            if mess_id is None:
                mess_id = message_elt.getAttribute('id')
            cache_key = (room_jid, mess_id)

            try:
                room = self._m.getRoom(client, room_jid)
            except exceptions.NotFound:
                log.warning(
                    f"Received an OMEMO encrypted msg from a room {room_jid} which has "
                    f"not been joined, ignoring")
                defer.returnValue(True)

            user = room.getUser(from_jid.resource)
            if user is None:
                log.warning(f"Can't find user {user} in room {room_jid}, ignoring")
                defer.returnValue(True)
            if not user.entity:
                log.warning(
                    f"Real entity of user {user} in room {room_jid} can't be established,"
                    f" OMEMO encrypted message can't be decrypted")
                defer.returnValue(True)

            # now we have real jid of the entity, we use it instead of from_jid
            from_jid = user.entity.userhostJID()

        else:
            # we have a one2one message, we can user "from" and "to" normally

            if from_jid.userhostJID() == client.jid.userhostJID():
                feedback_jid = jid.JID(message_elt['to'])
            else:
                feedback_jid = from_jid


        if (message_elt.getAttribute("type") == C.MESS_TYPE_GROUPCHAT
            and mess_id is not None
            and cache_key in client._xep_0384_muc_cache):
            plaintext = client._xep_0384_muc_cache.pop(cache_key)
            if not client._xep_0384_muc_cache:
                client._xep_0384_muc_cache_timer.cancel()
                client._xep_0384_muc_cache_timer = None
        else:
            try:
                omemo_session = client._xep_0384_session
            except AttributeError:
                # on startup, message can ve received before session actually exists
                # so we need to synchronise here
                yield client._xep_0384_ready
                omemo_session = client._xep_0384_session

            device_id = client._xep_0384_device_id
            try:
                header_elt = next(encrypted_elt.elements(NS_OMEMO, 'header'))
                iv_elt = next(header_elt.elements(NS_OMEMO, 'iv'))
            except StopIteration:
                log.warning(_("Invalid OMEMO encrypted stanza, ignoring: {xml}")
                    .format(xml=message_elt.toXml()))
                defer.returnValue(False)
            try:
                s_device_id = header_elt['sid']
            except KeyError:
                log.warning(_("Invalid OMEMO encrypted stanza, missing sender device ID, "
                              "ignoring: {xml}")
                    .format(xml=message_elt.toXml()))
                defer.returnValue(False)
            try:
                key_elt = next((e for e in header_elt.elements(NS_OMEMO, 'key')
                                if int(e['rid']) == device_id))
            except StopIteration:
                log.warning(_("This OMEMO encrypted stanza has not been encrypted "
                              "for our device (device_id: {device_id}, fingerprint: "
                              "{fingerprint}): {xml}").format(
                              device_id=device_id,
                              fingerprint=omemo_session.public_bundle.ik.hex().upper(),
                              xml=encrypted_elt.toXml()))
                user_msg = (D_("An OMEMO message from {sender} has not been encrypted for "
                               "our device, we can't decrypt it").format(
                               sender=from_jid.full()))
                extra = {C.MESS_EXTRA_INFO: C.EXTRA_INFO_DECR_ERR}
                client.feedback(feedback_jid, user_msg, extra)
                defer.returnValue(False)
            except ValueError as e:
                log.warning(_("Invalid recipient ID: {msg}".format(msg=e)))
                defer.returnValue(False)
            is_pre_key = C.bool(key_elt.getAttribute('prekey', 'false'))
            payload_elt = next(encrypted_elt.elements(NS_OMEMO, 'payload'), None)
            additional_information = {
                "from_storage": bool(message_elt.delay)
            }

            kwargs = {
                "bare_jid": from_jid.userhostJID(),
                "device": s_device_id,
                "iv": base64.b64decode(bytes(iv_elt)),
                "message": base64.b64decode(bytes(key_elt)),
                "is_pre_key_message": is_pre_key,
                "additional_information":  additional_information,
            }

            try:
                if payload_elt is None:
                    omemo_session.decryptRatchetForwardingMessage(**kwargs)
                    plaintext = None
                else:
                    kwargs["ciphertext"] = base64.b64decode(bytes(payload_elt))
                    try:
                        plaintext = yield omemo_session.decryptMessage(**kwargs)
                    except omemo_excpt.TrustException:
                        post_treat.addCallback(client.encryption.markAsUntrusted)
                        kwargs['allow_untrusted'] = True
                        plaintext = yield omemo_session.decryptMessage(**kwargs)
                    else:
                        post_treat.addCallback(client.encryption.markAsTrusted)
                    plaintext = plaintext.decode()
            except Exception as e:
                log.warning(_("Can't decrypt message: {reason}\n{xml}").format(
                    reason=e, xml=message_elt.toXml()))
                user_msg = (D_(
                    "An OMEMO message from {sender} can't be decrypted: {reason}")
                    .format(sender=from_jid.full(), reason=e))
                extra = {C.MESS_EXTRA_INFO: C.EXTRA_INFO_DECR_ERR}
                client.feedback(feedback_jid, user_msg, extra)
                defer.returnValue(False)
            finally:
                if omemo_session.republish_bundle:
                    # we don't wait for the Deferred (i.e. no yield) on purpose
                    # there is no need to block the whole message workflow while
                    # updating the bundle
                    defer.ensureDeferred(
                        self.setBundle(client, omemo_session.public_bundle, device_id)
                    )

        message_elt.children.remove(encrypted_elt)
        if plaintext:
            message_elt.addElement("body", content=plaintext)
        post_treat.addCallback(client.encryption.markAsEncrypted, namespace=NS_OMEMO)
        defer.returnValue(True)

    def getJIDsForRoom(self, client, room_jid):
        if self._m is None:
            exceptions.InternalError("XEP-0045 plugin missing, can't encrypt for group chat")
        room = self._m.getRoom(client, room_jid)
        return [u.entity.userhostJID() for u in room.roster.values()]

    def _expireMUCCache(self, client):
        client._xep_0384_muc_cache_timer = None
        for (room_jid, uid), msg in client._xep_0384_muc_cache.items():
            client.feedback(
                room_jid,
                D_("Our message with UID {uid} has not been received in time, it has "
                   "probably been lost. The message was: {msg!r}").format(
                    uid=uid, msg=str(msg)))

        client._xep_0384_muc_cache.clear()
        log.warning("Cache for OMEMO MUC has expired")

    @defer.inlineCallbacks
    def _sendMessageDataTrigger(self, client, mess_data):
        encryption = mess_data.get(C.MESS_KEY_ENCRYPTION)
        if encryption is None or encryption['plugin'].namespace != NS_OMEMO:
            return
        message_elt = mess_data["xml"]
        if mess_data['type'] == C.MESS_TYPE_GROUPCHAT:
            feedback_jid = room_jid = mess_data['to']
            to_jids = self.getJIDsForRoom(client, room_jid)
        else:
            feedback_jid = to_jid = mess_data["to"].userhostJID()
            to_jids = [to_jid]
        log.debug("encrypting message")
        body = None
        for child in list(message_elt.children):
            if child.name == "body":
                # we remove all unencrypted body,
                # and will only encrypt the first one
                if body is None:
                    body = child
                message_elt.children.remove(child)
            elif child.name == "html":
                # we don't want any XHTML-IM element
                message_elt.children.remove(child)

        if body is None:
            log.warning("No message found")
            return

        body = str(body)

        if mess_data['type'] == C.MESS_TYPE_GROUPCHAT:
            key = (room_jid, mess_data['uid'])
            # XXX: we can't encrypt message for our own device for security reason
            #      so we keep the plain text version in cache until we receive the
            #      message. We don't send it directly to bridge to keep a workflow
            #      similar to plain text MUC, so when we see it in frontend we know
            #      that it has been sent correctly.
            client._xep_0384_muc_cache[key] = body
            timer = client._xep_0384_muc_cache_timer
            if timer is None:
                client._xep_0384_muc_cache_timer = reactor.callLater(
                    MUC_CACHE_TTL, self._expireMUCCache, client)
            else:
                timer.reset(MUC_CACHE_TTL)
            # we use origin-id when possible, to identifiy the message in a stable way
            if self._sid is not None:
                self._sid.addOriginId(message_elt, mess_data['uid'])

        encryption_data = yield defer.ensureDeferred(self.encryptMessage(
            client, to_jids, body, feedback_jid=feedback_jid))

        encrypted_elt = message_elt.addElement((NS_OMEMO, 'encrypted'))
        header_elt = encrypted_elt.addElement('header')
        header_elt['sid'] = str(encryption_data['sid'])

        for key_data in encryption_data['keys'].values():
            for rid, data in key_data.items():
                key_elt = header_elt.addElement(
                    'key',
                    content=b64enc(data['data'])
                )
                key_elt['rid'] = str(rid)
                if data['pre_key']:
                    key_elt['prekey'] = 'true'

        header_elt.addElement(
            'iv',
            content=b64enc(encryption_data['iv']))
        try:
            encrypted_elt.addElement(
                'payload',
                content=b64enc(encryption_data['payload']))
        except KeyError:
            pass
