#!/usr/bin/env python3

# Cagou: desktop/mobile frontend for Salut à Toi XMPP client
# Copyright (C) 2016-2021 Jérôme Poisson (goffi@goffi.org)

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
import socket
import json
from functools import partial
from urllib.parse import urlparse
from pathlib import Path
import shutil
import mimetypes
from jnius import autoclass, cast, JavaException
from android import activity
from android.permissions import request_permissions, Permission
from kivy.clock import Clock
from kivy.uix.label import Label
from sat.core.i18n import _
from sat.core import log as logging
from sat.tools.common import data_format
from sat_frontends.tools import jid
from cagou.core.constants import Const as C
from cagou.core import dialog
from cagou import G
from .base import Platform as BasePlatform


log = logging.getLogger(__name__)

# permission that are necessary to have Cagou running properly
PERMISSION_MANDATORY = [
    Permission.READ_EXTERNAL_STORAGE,
    Permission.WRITE_EXTERNAL_STORAGE,
]

service = autoclass('org.libervia.cagou.ServiceBackend')
PythonActivity = autoclass('org.kivy.android.PythonActivity')
mActivity = PythonActivity.mActivity
Intent = autoclass('android.content.Intent')
AndroidString = autoclass('java.lang.String')
Uri = autoclass('android.net.Uri')
ImagesMedia = autoclass('android.provider.MediaStore$Images$Media')
AudioMedia = autoclass('android.provider.MediaStore$Audio$Media')
VideoMedia = autoclass('android.provider.MediaStore$Video$Media')
URLConnection = autoclass('java.net.URLConnection')

DISPLAY_NAME = '_display_name'
DATA = '_data'


STATE_RUNNING = b"running"
STATE_PAUSED = b"paused"
STATE_STOPPED = b"stopped"
SOCKET_DIR = "/data/data/org.libervia.cagou/"
SOCKET_FILE = ".socket"
INTENT_EXTRA_ACTION = AndroidString("org.salut-a-toi.IntentAction")


class Platform(BasePlatform):
    send_button_visible = True

    def __init__(self):
        super().__init__()
        # cache for callbacks to run when profile is plugged
        self.cache = []

    def init_platform(self):
        # sys.platform is "linux" on android by default
        # so we change it to allow backend to detect android
        sys.platform = "android"
        C.PLUGIN_EXT = 'pyc'

    def on_host_init(self, host):
        argument = ''
        service.start(mActivity, argument)

        activity.bind(on_new_intent=self.on_new_intent)
        self.cache.append((self.on_new_intent, mActivity.getIntent()))
        self.last_selected_wid = None
        self.restore_selected_wid = True
        host.addListener('profilePlugged', self.onProfilePlugged)
        host.addListener('selected', self.onSelectedWidget)
        local_dir = Path(host.getConfig('', 'local_dir')).resolve()
        self.tmp_dir = local_dir / 'tmp'
        # we assert to avoid disaster if `/ 'tmp'` is removed by mistake on the line
        # above
        assert self.tmp_dir.resolve() != local_dir
        # we reset tmp dir on each run, to be sure that there is no residual file
        if self.tmp_dir.exists():
            shutil.rmtree(self.tmp_dir)
        self.tmp_dir.mkdir(0o700, parents=True)

    def on_initFrontendState(self):
        # XXX: we use a separated socket instead of bridge because if we
        #      try to call a bridge method in on_pause method, the call data
        #      is not written before the actual pause
        s = self._frontend_status_socket = socket.socket(
            socket.AF_UNIX, socket.SOCK_STREAM)
        s.connect(os.path.join(SOCKET_DIR, SOCKET_FILE))
        s.sendall(STATE_RUNNING)

    def profileAutoconnectGetCb(self, profile=None):
        if profile is not None:
            G.host.options.profile = profile
        G.host.postInit()

    def profileAutoconnectGetEb(self, failure_):
        log.error(f"Error while getting profile to autoconnect: {failure_}")
        G.host.postInit()

    def _show_perm_warning(self, permissions):
        root_wid = G.host.app.root
        perm_warning = Label(
            size_hint=(1, 1),
            text_size=(root_wid.width, root_wid.height),
            font_size='22sp',
            bold=True,
            color=(0.67, 0, 0, 1),
            halign='center',
            valign='center',
            text=_(
            "Requested permissions are mandatory to run Cagou, if you don't "
            "accept them, Cagou can't run properly. Please accept following "
            "permissions, or set them in Android settings for Cagou:\n"
            "{permissions}\n\nCagou will be closed in 20 s").format(
                permissions='\n'.join(p.split('.')[-1] for p in permissions)))
        root_wid.clear_widgets()
        root_wid.add_widget(perm_warning)
        Clock.schedule_once(lambda *args: G.host.app.stop(), 20)

    def permission_cb(self, permissions, grant_results):
        if not all(grant_results):
            # we keep asking until they are accepted, as we can't run properly
            # without them
            # TODO: a message explaining why permission is needed should be printed
            # TODO: the storage permission is mainly used to set download_dir, we should
            #   be able to run Cagou without it.
            if not hasattr(self, 'perms_counter'):
                self.perms_counter = 0
            self.perms_counter += 1
            if self.perms_counter > 5:
                Clock.schedule_once(
                    lambda *args: self._show_perm_warning(permissions),
                    0)
                return

            perm_dict = dict(zip(permissions, grant_results))
            log.warning(
                f"not all mandatory permissions are granted, requesting again: "
                f"{perm_dict}")
            request_permissions(PERMISSION_MANDATORY, callback=self.permission_cb)
            return

        Clock.schedule_once(lambda *args: G.host.bridge.profileAutoconnectGet(
            callback=self.profileAutoconnectGetCb,
            errback=self.profileAutoconnectGetEb),
            0)

    def do_postInit(self):
        request_permissions(PERMISSION_MANDATORY, callback=self.permission_cb)
        return False

    def privateDataGetCb(self, data_s, profile):
        data = data_format.deserialise(data_s, type_check=None)
        if data is not None and self.restore_selected_wid:
            log.debug(f"restoring previous widget {data}")
            try:
                name = data['name']
                target = data['target']
            except KeyError as e:
                log.error(f"Bad data format for selected widget: {e}\ndata={data}")
                return
            if target:
                target = jid.JID(data['target'])
            plugin_info = G.host.getPluginInfo(name=name)
            if plugin_info is None:
                log.warning("Can't restore unknown plugin: {name}")
                return
            factory = plugin_info['factory']
            G.host.switchWidget(
                None,
                factory(plugin_info, target=target, profiles=[profile])
            )

    def onProfilePlugged(self, profile):
        log.debug("ANDROID profilePlugged")
        G.host.bridge.setParam(
            "autoconnect_backend", C.BOOL_TRUE, "Connection", -1, profile,
            callback=lambda: log.info(f"profile {profile} autoconnection set"),
            errback=lambda: log.error(f"can't set {profile} autoconnection"))
        for method, *args in self.cache:
            method(*args)
        del self.cache
        G.host.removeListener("profilePlugged", self.onProfilePlugged)
        # we restore the stored widget if any
        # user will then go back to where they was when the frontend was closed
        G.host.bridge.privateDataGet(
            "cagou", "selected_widget", profile,
            callback=partial(self.privateDataGetCb, profile=profile),
            errback=partial(
                G.host.errback,
                title=_("can't get selected widget"),
                message=_("error while retrieving selected widget: {msg}"))
        )

    def onSelectedWidget(self, wid):
        """Store selected widget in backend, to restore it on next startup"""
        if self.last_selected_wid == None:
            self.last_selected_wid = wid
            # we skip the first selected widget, as we'll restore stored one if possible
            return

        self.last_selected_wid = wid

        try:
            plugin_info = wid.plugin_info
        except AttributeError:
            log.warning(f"No plugin info found for {wid}, can't store selected widget")
            return

        try:
            profile = next(iter(wid.profiles))
        except (AttributeError, StopIteration):
            profile = None

        if profile is None:
            try:
                profile = next(iter(G.host.profiles))
            except StopIteration:
                log.debug("No profile plugged yet, can't store selected widget")
                return
        try:
            target = wid.target
        except AttributeError:
            target = None

        data = {
            "name": plugin_info["name"],
            "target": target,
        }

        G.host.bridge.privateDataSet(
            "cagou", "selected_widget", data_format.serialise(data), profile,
            errback=partial(
                G.host.errback,
                title=_("can set selected widget"),
                message=_("error while setting selected widget: {msg}"))
        )

    def on_pause(self):
        G.host.sync = False
        self._frontend_status_socket.sendall(STATE_PAUSED)
        return True

    def on_resume(self):
        self._frontend_status_socket.sendall(STATE_RUNNING)
        G.host.sync = True

    def on_stop(self):
        self._frontend_status_socket.sendall(STATE_STOPPED)
        self._frontend_status_socket.close()

    def on_key_back_root(self):
        PythonActivity.moveTaskToBack(True)
        return True

    def on_key_back_share(self, share_widget):
        share_widget.close()
        PythonActivity.moveTaskToBack(True)
        return True

    def _disconnect(self, profile):
        G.host.bridge.setParam(
            "autoconnect_backend", C.BOOL_FALSE, "Connection", -1, profile,
            callback=lambda: log.info(f"profile {profile} autoconnection unset"),
            errback=lambda: log.error(f"can't unset {profile} autoconnection"))
        G.host.profiles.unplug(profile)
        G.host.bridge.disconnect(profile)
        G.host.app.showProfileManager()
        G.host.closeUI()

    def _on_disconnect(self):
        current_profile = next(iter(G.host.profiles))
        wid = dialog.ConfirmDialog(
            title=_("Are you sure to disconnect?"),
            message=_(
                "If you disconnect the current user ({profile}), you won't receive "
                "any notification until you connect it again, is this really what you "
                "want?").format(profile=current_profile),
            yes_cb=partial(self._disconnect, profile=current_profile),
            no_cb=G.host.closeUI,
        )
        G.host.showExtraUI(wid)

    def on_extra_menu_init(self, extra_menu):
        extra_menu.addItem(_('disconnect'), self._on_disconnect)

    def updateParamsExtra(self, extra):
        # on Android, we handle autoconnection automatically,
        # user must not modify those parameters
        extra.update(
            {
                "ignore": [
                    ["Connection", "autoconnect_backend"],
                    ["Connection", "autoconnect"],
                    ["Connection", "autodisconnect"],
                ],
            }
        )

    def getColDataFromUri(self, uri, col_name):
        cursor = mActivity.getContentResolver().query(uri, None, None, None, None)
        if cursor is None:
            return None
        try:
            cursor.moveToFirst()
            col_idx = cursor.getColumnIndex(col_name);
            if col_idx == -1:
                return None
            return cursor.getString(col_idx)
        finally:
            cursor.close()

    def getFilenameFromUri(self, uri, media_type):
        filename = self.getColDataFromUri(uri, DISPLAY_NAME)
        if filename is None:
            uri_p = Path(uri.toString())
            filename = uri_p.name or "unnamed"
            if not uri_p.suffix and media_type:
                suffix = mimetypes.guess_extension(media_type, strict=False)
                if suffix:
                    filename = filename + suffix
        return filename

    def getPathFromUri(self, uri):
        # FIXME: using DATA is not recommended (and DATA is deprecated)
        # we should read directly the file with
        # ContentResolver#openFileDescriptor(Uri, String)
        path = self.getColDataFromUri(uri, DATA)
        return uri.getPath() if path is None else path

    def on_new_intent(self, intent):
        log.debug("on_new_intent")
        action = intent.getAction();
        intent_type = intent.getType();
        if action == Intent.ACTION_MAIN:
            action_str = intent.getStringExtra(INTENT_EXTRA_ACTION)
            if action_str is not None:
                action = json.loads(action_str)
                log.debug(f"Extra action found: {action}")
                action_type = action.get('type')
                if action_type == "open":
                    try:
                        widget = action['widget']
                        target = action['target']
                    except KeyError as e:
                        log.warning(f"incomplete action {action}: {e}")
                    else:
                        # we don't want stored selected widget to be displayed after this
                        # one
                        log.debug("cancelling restoration of previous widget")
                        self.restore_selected_wid = False
                        # and now we open the widget linked to the intent
                        current_profile = next(iter(G.host.profiles))
                        Clock.schedule_once(
                            lambda *args: G.host.doAction(
                                widget, jid.JID(target), [current_profile]),
                            0)
                else:
                    log.warning(f"unexpected action: {action}")

            text = None
            uri = None
            path = None
        elif action == Intent.ACTION_SEND:
            # we have receiving data to share, we parse the intent data
            # and show the share widget
            data = {}
            text = intent.getStringExtra(Intent.EXTRA_TEXT)
            if text is not None:
                data['text'] = text

            item = intent.getParcelableExtra(Intent.EXTRA_STREAM)
            if item is not None:
                uri = cast('android.net.Uri', item)
                if uri.getScheme() == 'content':
                    # Android content, we'll dump it to a temporary file
                    filename = self.getFilenameFromUri(uri, intent_type)
                    filepath = self.tmp_dir / filename
                    input_stream = mActivity.getContentResolver().openInputStream(uri)
                    buff = bytearray(4096)
                    with open(filepath, 'wb') as f:
                        while True:
                            ret = input_stream.read(buff, 0, 4096)
                            if ret != -1:
                                f.write(buff[:ret])
                            else:
                                break
                    input_stream.close()
                    data['path'] = path = str(filepath)
                else:
                    data['uri'] = uri.toString()
                    path = self.getPathFromUri(uri)
                    if path is not None and path not in data:
                        data['path'] = path
            else:
                uri = None
                path = None


            Clock.schedule_once(lambda *args: G.host.share(intent_type, data), 0)
        else:
            text = None
            uri = None
            path = None

        msg = (f"NEW INTENT RECEIVED\n"
               f"type: {intent_type}\n"
               f"action: {action}\n"
               f"text: {text}\n"
               f"uri: {uri}\n"
               f"path: {path}")

        log.debug(msg)

    def check_plugin_permissions(self, plug_info, callback, errback):
        perms = plug_info.get("android_permissons")
        if not perms:
            callback()
            return
        perms = [f"android.permission.{p}" if '.' not in p else p for p in perms]

        def request_permissions_cb(permissions, granted):
            if all(granted):
                Clock.schedule_once(lambda *args: callback())
            else:
                Clock.schedule_once(lambda *args: errback())

        request_permissions(perms, callback=request_permissions_cb)

    def open_url(self, url, wid=None):
        parsed_url = urlparse(url)
        if parsed_url.scheme == "aesgcm":
            return super().open_url(url, wid)
        else:
            media_type = mimetypes.guess_type(url, strict=False)[0]
            if media_type is None:
                log.debug(
                    f"media_type for {url!r} not found with python mimetypes, trying "
                    f"guessContentTypeFromName")
                media_type = URLConnection.guessContentTypeFromName(url)
            intent = Intent(Intent.ACTION_VIEW)
            if media_type is not None:
                log.debug(f"file {url!r} is of type {media_type}")
                intent.setDataAndType(Uri.parse(url), media_type)
            else:
                log.debug(f"can't guess media type for {url!r}")
                intent.setData(Uri.parse(url))
            if mActivity.getPackageManager() is not None:
                activity = cast('android.app.Activity', mActivity)
                try:
                    activity.startActivity(intent)
                except JavaException as e:
                    if e.classname != "android.content.ActivityNotFoundException":
                        raise e
                    log.debug(
                        f"activity not found for url {url!r}, we'll try generic opener")
                else:
                    return

        # if nothing else worked, we default to base open_url
        super().open_url(url, wid)
