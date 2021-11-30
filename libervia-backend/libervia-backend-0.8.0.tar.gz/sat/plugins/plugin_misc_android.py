#!/usr/bin/env python3

# SAT plugin for file tansfer
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
import os
import os.path
import json
from pathlib import Path
from zope.interface import implementer
from twisted.names import client as dns_client
from twisted.python.procutils import which
from twisted.internet import defer
from twisted.internet import reactor
from twisted.internet import protocol
from twisted.internet import abstract
from twisted.internet import error as int_error
from twisted.internet import _sslverify
from sat.core.i18n import _, D_
from sat.core.constants import Const as C
from sat.core.log import getLogger
from sat.core import exceptions
from sat.tools.common import async_process
from sat.memory import params


log = getLogger(__name__)

PLUGIN_INFO = {
    C.PI_NAME: "Android",
    C.PI_IMPORT_NAME: "android",
    C.PI_TYPE: C.PLUG_TYPE_MISC,
    C.PI_RECOMMENDATIONS: ["XEP-0352"],
    C.PI_MAIN: "AndroidPlugin",
    C.PI_HANDLER: "no",
    C.PI_DESCRIPTION: D_(
        """Manage Android platform specificities, like pause or notifications"""
    ),
}

if sys.platform != "android":
    raise exceptions.CancelError("this module is not needed on this platform")


import re
import certifi
from plyer import vibrator
from android import api_version
from plyer.platforms.android import activity
from plyer.platforms.android.notification import AndroidNotification
from jnius import autoclass
from android.broadcast import BroadcastReceiver
from android import python_act


Context = autoclass('android.content.Context')
ConnectivityManager = autoclass('android.net.ConnectivityManager')
MediaPlayer = autoclass('android.media.MediaPlayer')
AudioManager = autoclass('android.media.AudioManager')

# notifications
AndroidString = autoclass('java.lang.String')
PendingIntent = autoclass('android.app.PendingIntent')
Intent = autoclass('android.content.Intent')

# DNS
# regex to find dns server prop with "getprop"
RE_DNS = re.compile(r"^\[net\.[a-z0-9]+\.dns[0-4]\]: \[(.*)\]$", re.MULTILINE)
SystemProperties = autoclass('android.os.SystemProperties')

#: delay between a pause event and sending the inactive indication to server, in seconds
#: we don't send the indication immediately because user can be just checking something
#: quickly on an other app.
CSI_DELAY = 30

PARAM_RING_CATEGORY = "Notifications"
PARAM_RING_NAME = "sound"
PARAM_RING_LABEL = D_("sound on notifications")
RING_OPTS = {
    "normal": D_("Normal"),
    "never": D_("Never"),
}
PARAM_VIBRATE_CATEGORY = "Notifications"
PARAM_VIBRATE_NAME = "vibrate"
PARAM_VIBRATE_LABEL = D_("Vibrate on notifications")
VIBRATION_OPTS = {
    "always": D_("Always"),
    "vibrate": D_("In vibrate mode"),
    "never": D_("Never"),
}
SOCKET_DIR = "/data/data/org.libervia.cagou/"
SOCKET_FILE = ".socket"
STATE_RUNNING = b"running"
STATE_PAUSED = b"paused"
STATE_STOPPED = b"stopped"
STATES = (STATE_RUNNING, STATE_PAUSED, STATE_STOPPED)
NET_TYPE_NONE = "no network"
NET_TYPE_WIFI = "wifi"
NET_TYPE_MOBILE = "mobile"
NET_TYPE_OTHER = "other"
INTENT_EXTRA_ACTION = AndroidString("org.salut-a-toi.IntentAction")


@implementer(_sslverify.IOpenSSLTrustRoot)
class AndroidTrustPaths:

    def _addCACertsToContext(self, context):
        # twisted doesn't have access to Android root certificates
        # we use certifi to work around that (same thing is done in Kivy)
        context.load_verify_locations(certifi.where())


def platformTrust():
    return AndroidTrustPaths()


class Notification(AndroidNotification):
    # We extend plyer's AndroidNotification instead of creating directly with jnius
    # because it already handles issues like backward compatibility, and we just want to
    # slightly modify the behaviour.

    @staticmethod
    def _set_open_behavior(notification, sat_action):
        # we reproduce plyer's AndroidNotification._set_open_behavior
        # bu we add SàT specific extra action data

        app_context = activity.getApplication().getApplicationContext()
        notification_intent = Intent(app_context, python_act)

        notification_intent.setFlags(Intent.FLAG_ACTIVITY_SINGLE_TOP)
        notification_intent.setAction(Intent.ACTION_MAIN)
        notification_intent.addCategory(Intent.CATEGORY_LAUNCHER)
        if sat_action is not None:
            action_data = AndroidString(json.dumps(sat_action).encode())
            log.debug(f"adding extra {INTENT_EXTRA_ACTION} ==> {action_data}")
            notification_intent = notification_intent.putExtra(
                INTENT_EXTRA_ACTION, action_data)

        # we use PendingIntent.FLAG_UPDATE_CURRENT here, otherwise extra won't be set
        # in the new intent (the old ACTION_MAIN intent will be reused). This differs
        # from plyers original behaviour which set no flag here
        pending_intent = PendingIntent.getActivity(
            app_context, 0, notification_intent, PendingIntent.FLAG_UPDATE_CURRENT
        )

        notification.setContentIntent(pending_intent)
        notification.setAutoCancel(True)

    def _notify(self, **kwargs):
        # we reproduce plyer's AndroidNotification._notify behaviour here
        # and we add handling of "sat_action" attribute (SàT specific).
        # we also set, where suitable, default values to empty string instead of
        # original None, as a string is expected (in plyer the empty string is used
        # in the generic "notify" method).
        sat_action = kwargs.pop("sat_action", None)
        noti = None
        message = kwargs.get('message', '').encode('utf-8')
        ticker = kwargs.get('ticker', '').encode('utf-8')
        title = AndroidString(
            kwargs.get('title', '').encode('utf-8')
        )
        icon = kwargs.get('app_icon', '')

        if kwargs.get('toast', False):
            self._toast(message)
            return
        else:
            noti = self._build_notification(title)

        noti.setContentTitle(title)
        noti.setContentText(AndroidString(message))
        noti.setTicker(AndroidString(ticker))

        self._set_icons(noti, icon=icon)
        self._set_open_behavior(noti, sat_action)

        self._open_notification(noti)


class FrontendStateProtocol(protocol.Protocol):

    def __init__(self, android_plugin):
        self.android_plugin = android_plugin

    def dataReceived(self, data):
        if data in STATES:
            self.android_plugin.state = data
        else:
            log.warning("Unexpected data: {data}".format(data=data))


class FrontendStateFactory(protocol.Factory):

    def __init__(self, android_plugin):
        self.android_plugin = android_plugin

    def buildProtocol(self, addr):
        return FrontendStateProtocol(self.android_plugin)



class AndroidPlugin(object):

    params = """
    <params>
    <individual>
    <category name="{category_name}" label="{category_label}">
        <param name="{ring_param_name}" label="{ring_param_label}" type="list" security="0">
            {ring_options}
        </param>
        <param name="{vibrate_param_name}" label="{vibrate_param_label}" type="list" security="0">
            {vibrate_options}
        </param>
     </category>
    </individual>
    </params>
    """.format(
        category_name=PARAM_VIBRATE_CATEGORY,
        category_label=D_(PARAM_VIBRATE_CATEGORY),
        vibrate_param_name=PARAM_VIBRATE_NAME,
        vibrate_param_label=PARAM_VIBRATE_LABEL,
        vibrate_options=params.makeOptions(VIBRATION_OPTS, "always"),
        ring_param_name=PARAM_RING_NAME,
        ring_param_label=PARAM_RING_LABEL,
        ring_options=params.makeOptions(RING_OPTS, "normal"),
    )

    def __init__(self, host):
        log.info(_("plugin Android initialization"))
        log.info(f"using Android API {api_version}")
        self.host = host
        self._csi = host.plugins.get('XEP-0352')
        self._csi_timer = None
        host.memory.updateParams(self.params)
        try:
            os.mkdir(SOCKET_DIR, 0o700)
        except OSError as e:
            if e.errno == 17:
                # dir already exists
                pass
            else:
                raise e
        self._state = None
        factory = FrontendStateFactory(self)
        socket_path = os.path.join(SOCKET_DIR, SOCKET_FILE)
        try:
            reactor.listenUNIX(socket_path, factory)
        except int_error.CannotListenError as e:
            if e.socketError.errno == 98:
                # the address is already in use, we need to remove it
                os.unlink(socket_path)
                reactor.listenUNIX(socket_path, factory)
            else:
                raise e
        # we set a low priority because we want the notification to be sent after all
        # plugins have done their job
        host.trigger.add("messageReceived", self.messageReceivedTrigger, priority=-1000)

        # profiles autoconnection
        host.bridge.addMethod(
            "profileAutoconnectGet",
            ".plugin",
            in_sign="",
            out_sign="s",
            method=self._profileAutoconnectGet,
            async_=True,
        )

        # audio manager, to get ring status
        self.am = activity.getSystemService(Context.AUDIO_SERVICE)

        # sound notification
        media_dir = Path(host.memory.getConfig("", "media_dir"))
        assert media_dir is not None
        notif_path = media_dir / "sounds" / "notifications" / "music-box.mp3"
        self.notif_player = MediaPlayer()
        self.notif_player.setDataSource(str(notif_path))
        self.notif_player.setAudioStreamType(AudioManager.STREAM_NOTIFICATION)
        self.notif_player.prepare()

        # SSL fix
        _sslverify.platformTrust = platformTrust
        log.info("SSL Android patch applied")

        # DNS fix
        defer.ensureDeferred(self.updateResolver())

        # Connectivity handling
        self.cm = activity.getSystemService(Context.CONNECTIVITY_SERVICE)
        self._net_type = None
        d = defer.ensureDeferred(self._checkConnectivity())
        d.addErrback(host.logErrback)

        # XXX: we need to keep a reference to BroadcastReceiver to avoid
        #     "XXX has no attribute 'invoke'" error (looks like the same issue as
        #     https://github.com/kivy/pyjnius/issues/59)
        self.br = BroadcastReceiver(
            callback=lambda *args, **kwargs: reactor.callFromThread(
                self.onConnectivityChange
            ),
            actions=["android.net.conn.CONNECTIVITY_CHANGE"]
        )
        self.br.start()

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, new_state):
        log.debug(f"frontend state has changed: {new_state.decode()}")
        previous_state = self._state
        self._state = new_state
        if new_state == STATE_RUNNING:
            self._onRunning(previous_state)
        elif new_state == STATE_PAUSED:
            self._onPaused(previous_state)
        elif new_state == STATE_STOPPED:
            self._onStopped(previous_state)

    @property
    def cagou_active(self):
        return self._state == STATE_RUNNING

    def _onRunning(self, previous_state):
        if previous_state is not None:
            self.host.bridge.bridgeReactivateSignals()
        self.setActive()

    def _onPaused(self, previous_state):
        self.host.bridge.bridgeDeactivateSignals()
        self.setInactive()

    def _onStopped(self, previous_state):
        self.setInactive()

    def _notifyMessage(self, mess_data, client):
        """Send notification when suitable

        notification is sent if:
            - there is a message and it is not a groupchat
            - message is not coming from ourself
        """
        if (mess_data["message"] and mess_data["type"] != C.MESS_TYPE_GROUPCHAT
            and not mess_data["from"].userhostJID() == client.jid.userhostJID()):
            message = next(iter(mess_data["message"].values()))
            try:
                subject = next(iter(mess_data["subject"].values()))
            except StopIteration:
                subject = D_("new message from {contact}").format(
                    contact = mess_data['from'])

            notification = Notification()
            notification._notify(
                title=subject,
                message=message,
                sat_action={
                    "type": "open",
                    "widget": "chat",
                    "target": mess_data["from"].userhost(),
                },
            )

            ringer_mode = self.am.getRingerMode()
            vibrate_mode = ringer_mode == AudioManager.RINGER_MODE_VIBRATE

            ring_setting = self.host.memory.getParamA(
                PARAM_RING_NAME,
                PARAM_RING_CATEGORY,
                profile_key=client.profile
            )

            if ring_setting != 'never' and ringer_mode == AudioManager.RINGER_MODE_NORMAL:
                self.notif_player.start()

            vibration_setting = self.host.memory.getParamA(
                PARAM_VIBRATE_NAME,
                PARAM_VIBRATE_CATEGORY,
                profile_key=client.profile
            )
            if (vibration_setting == 'always'
                or vibration_setting == 'vibrate' and vibrate_mode):
                    try:
                        vibrator.vibrate()
                    except Exception as e:
                        log.warning("Can't use vibrator: {e}".format(e=e))
        return mess_data

    def messageReceivedTrigger(self, client, message_elt, post_treat):
        if not self.cagou_active:
            # we only send notification is the frontend is not displayed
            post_treat.addCallback(self._notifyMessage, client)

        return True

    # Profile autoconnection

    def _profileAutoconnectGet(self):
        return defer.ensureDeferred(self.profileAutoconnectGet())

    async def _getProfilesAutoconnect(self):
        autoconnect_dict = await self.host.memory.storage.getIndParamValues(
            category='Connection', name='autoconnect_backend',
        )
        return [p for p, v in autoconnect_dict.items() if C.bool(v)]

    async def profileAutoconnectGet(self):
        """Return profile to connect automatically by frontend, if any"""
        profiles_autoconnect = await self._getProfilesAutoconnect()
        if not profiles_autoconnect:
            return None
        if len(profiles_autoconnect) > 1:
            log.warning(
                f"More that one profiles with backend autoconnection set found, picking "
                f"up first one (full list: {profiles_autoconnect!r})")
        return profiles_autoconnect[0]

    # CSI

    def _setInactive(self):
        self._csi_timer = None
        for client in self.host.getClients(C.PROF_KEY_ALL):
            self._csi.setInactive(client)

    def setInactive(self):
        if self._csi is None or self._csi_timer is not None:
            return
        self._csi_timer = reactor.callLater(CSI_DELAY, self._setInactive)

    def setActive(self):
        if self._csi is None:
            return
        if self._csi_timer is not None:
            self._csi_timer.cancel()
            self._csi_timer = None
        for client in self.host.getClients(C.PROF_KEY_ALL):
            self._csi.setActive(client)

    # Connectivity

    async def _handleNetworkChange(self, net_type):
        """Notify the clients about network changes.

        This way the client can disconnect/reconnect transport, or change delays
        """
        log.debug(f"handling network change ({net_type})")
        if net_type == NET_TYPE_NONE:
            for client in self.host.getClients(C.PROF_KEY_ALL):
                client.networkDisabled()
        else:
            # DNS servers may have changed
            await self.updateResolver()
            # client may be there but disabled (e.g. with stream management)
            for client in self.host.getClients(C.PROF_KEY_ALL):
                log.debug(f"enabling network for {client.profile}")
                client.networkEnabled()

            # profiles may have been disconnected and then purged, we try
            # to reconnect them in case
            profiles_autoconnect = await self._getProfilesAutoconnect()
            for profile in profiles_autoconnect:
                if not self.host.isConnected(profile):
                    log.info(f"{profile} is not connected, reconnecting it")
                    try:
                        await self.host.connect(profile)
                    except Exception as e:
                        log.error(f"Can't connect profile {profile}: {e}")

    async def _checkConnectivity(self):
        active_network = self.cm.getActiveNetworkInfo()
        if active_network is None:
            net_type = NET_TYPE_NONE
        else:
            net_type_android = active_network.getType()
            if net_type_android == ConnectivityManager.TYPE_WIFI:
                net_type = NET_TYPE_WIFI
            elif net_type_android == ConnectivityManager.TYPE_MOBILE:
                net_type = NET_TYPE_MOBILE
            else:
                net_type = NET_TYPE_OTHER

        if net_type != self._net_type:
            log.info("connectivity has changed")
            self._net_type = net_type
            if net_type == NET_TYPE_NONE:
                log.info("no network active")
            elif net_type == NET_TYPE_WIFI:
                log.info("WIFI activated")
            elif net_type == NET_TYPE_MOBILE:
                log.info("mobile data activated")
            else:
                log.info("network activated (type={net_type_android})"
                    .format(net_type_android=net_type_android))
        else:
            log.debug("_checkConnectivity called without network change ({net_type})"
                .format(net_type = net_type))

        # we always call _handleNetworkChange even if there is not connectivity change
        # to be sure to reconnect when necessary
        await self._handleNetworkChange(net_type)


    def onConnectivityChange(self):
        log.debug("onConnectivityChange called")
        d = defer.ensureDeferred(self._checkConnectivity())
        d.addErrback(self.host.logErrback)

    async def updateResolver(self):
        # There is no "/etc/resolv.conf" on Android, which confuse Twisted and makes
        # SRV record checking unusable. We fixe that by checking DNS server used, and
        # updating Twisted's resolver accordingly
        dns_servers = await self.getDNSServers()

        log.info(
            "Patching Twisted to use Android DNS resolver ({dns_servers})".format(
            dns_servers=', '.join([s[0] for s in dns_servers]))
        )
        dns_client.theResolver = dns_client.createResolver(servers=dns_servers)

    async def getDNSServers(self):
        servers = []

        if api_version < 26:
            # thanks to A-IV at https://stackoverflow.com/a/11362271 for the way to go
            log.debug("Old API, using SystemProperties to find DNS")
            for idx in range(1, 5):
                addr = SystemProperties.get(f'net.dns{idx}')
                if abstract.isIPAddress(addr):
                    servers.append((addr, 53))
        else:
            log.debug(f"API {api_version} >= 26, using getprop to find DNS")
            # use of getprop inspired by various solutions at
            # https://stackoverflow.com/q/3070144
            # it's the most simple option, and it fit wells with async_process
            getprop_paths = which('getprop')
            if getprop_paths:
                try:
                    getprop_path = getprop_paths[0]
                    props = await async_process.run(getprop_path)
                    servers = [(ip, 53) for ip in RE_DNS.findall(props.decode())
                               if abstract.isIPAddress(ip)]
                except Exception as e:
                    log.warning(f"Can't use \"getprop\" to find DNS server: {e}")
        if not servers:
            # FIXME: Cloudflare's 1.1.1.1 seems to have a better privacy policy, to be
            #   checked.
            log.warning(
                "no server found, we have to use factory Google DNS, this is not ideal "
                "for privacy"
            )
            servers.append(('8.8.8.8', 53), ('8.8.4.4', 53))
        return servers
