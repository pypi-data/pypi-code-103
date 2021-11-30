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


from sat.core import log as logging
from sat.core.i18n import _
from sat_frontends.quick_frontend import quick_widgets
from ..core import cagou_widget
from ..core.constants import Const as C
from ..core.behaviors import TouchMenuBehavior, FilterBehavior
from ..core.common_widgets import (Identities, ItemWidget, DeviceWidget,
                                       CategorySeparator)
from sat.tools.common import template_xmlui
from cagou.core import xmlui
from sat_frontends.tools import jid
from kivy import properties
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from cagou import G
from functools import partial


log = logging.getLogger(__name__)

PLUGIN_INFO = {
    "name": _("remote control"),
    "main": "RemoteControl",
    "description": _("universal remote control"),
    "icon_symbol": "signal",
}

NOTE_TITLE = _("Media Player Remote Control")


class RemoteItemWidget(ItemWidget):

    def __init__(self, device_jid, node, name, main_wid, **kw):
        self.device_jid = device_jid
        self.node = node
        super(RemoteItemWidget, self).__init__(name=name, main_wid=main_wid, **kw)

    def do_item_action(self, touch):
        self.main_wid.layout.clear_widgets()
        player_wid = MediaPlayerControlWidget(main_wid=self.main_wid, remote_item=self)
        self.main_wid.layout.add_widget(player_wid)


class MediaPlayerControlWidget(BoxLayout):
    main_wid = properties.ObjectProperty()
    remote_item = properties.ObjectProperty()
    status = properties.OptionProperty("play", options=("play", "pause", "stop"))
    title = properties.StringProperty()
    identity = properties.StringProperty()
    command = properties.DictProperty()
    ui_tpl = properties.ObjectProperty()

    @property
    def profile(self):
        return self.main_wid.profile

    def updateUI(self, action_data):
        xmlui_raw = action_data['xmlui']
        ui_tpl = template_xmlui.create(G.host, xmlui_raw)
        self.ui_tpl = ui_tpl
        for prop in ('Title', 'Identity'):
            try:
                setattr(self, prop.lower(), ui_tpl.widgets[prop].value)
            except KeyError:
                log.warning(_("Missing field: {name}").format(name=prop))
        playback_status = self.ui_tpl.widgets['PlaybackStatus'].value
        if playback_status == "Playing":
            self.status = "pause"
        elif playback_status == "Paused":
            self.status = "play"
        elif playback_status == "Stopped":
            self.status = "play"
        else:
            G.host.addNote(
                title=NOTE_TITLE,
                message=_("Unknown playback status: playback_status")
                          .format(playback_status=playback_status),
                level=C.XMLUI_DATA_LVL_WARNING)
        self.commands = {v:k for k,v in ui_tpl.widgets['command'].options}

    def adHocRunCb(self, xmlui_raw):
        ui_tpl = template_xmlui.create(G.host, xmlui_raw)
        data = {xmlui.XMLUIPanel.escape("media_player"): self.remote_item.node,
                "session_id": ui_tpl.session_id}
        G.host.bridge.launchAction(
            ui_tpl.submit_id, data, self.profile,
            callback=self.updateUI,
            errback=self.main_wid.errback)

    def on_remote_item(self, __, remote):
        NS_MEDIA_PLAYER = G.host.ns_map["mediaplayer"]
        G.host.bridge.adHocRun(str(remote.device_jid), NS_MEDIA_PLAYER, self.profile,
                               callback=self.adHocRunCb,
                               errback=self.main_wid.errback)

    def do_cmd(self, command):
        try:
            cmd_value = self.commands[command]
        except KeyError:
            G.host.addNote(
                title=NOTE_TITLE,
                message=_("{command} command is not managed").format(command=command),
                level=C.XMLUI_DATA_LVL_WARNING)
        else:
            data = {xmlui.XMLUIPanel.escape("command"): cmd_value,
                    "session_id": self.ui_tpl.session_id}
            # hidden values are normally transparently managed by XMLUIPanel
            # but here we have to add them by hand
            hidden = {xmlui.XMLUIPanel.escape(k):v
                      for k,v in self.ui_tpl.hidden.items()}
            data.update(hidden)
            G.host.bridge.launchAction(
                self.ui_tpl.submit_id, data, self.profile,
                callback=self.updateUI,
                errback=self.main_wid.errback)


class RemoteDeviceWidget(DeviceWidget):

    def xmluiCb(self, data, cb_id, profile):
        if 'xmlui' in data:
            xml_ui = xmlui.create(
                G.host, data['xmlui'], callback=self.xmluiCb, profile=profile)
            if isinstance(xml_ui, xmlui.XMLUIDialog):
                self.main_wid.showRootWidget()
                xml_ui.show()
            else:
                xml_ui.setCloseCb(self.onClose)
                self.main_wid.layout.add_widget(xml_ui)
        else:
            if data:
                log.warning(_("Unhandled data: {data}").format(data=data))
            self.main_wid.showRootWidget()

    def onClose(self, __, reason):
        if reason == C.XMLUI_DATA_CANCELLED:
            self.main_wid.showRootWidget()
        else:
            self.main_wid.layout.clear_widgets()

    def adHocRunCb(self, data):
        xml_ui = xmlui.create(G.host, data, callback=self.xmluiCb, profile=self.profile)
        xml_ui.setCloseCb(self.onClose)
        self.main_wid.layout.add_widget(xml_ui)

    def do_item_action(self, touch):
        self.main_wid.layout.clear_widgets()
        G.host.bridge.adHocRun(str(self.entity_jid), '', self.profile,
            callback=self.adHocRunCb, errback=self.main_wid.errback)


class DevicesLayout(FloatLayout):
    """Layout used to show devices"""
    layout = properties.ObjectProperty()


class RemoteControl(quick_widgets.QuickWidget, cagou_widget.CagouWidget, FilterBehavior,
                  TouchMenuBehavior):
    SINGLE=False
    layout = properties.ObjectProperty()

    def __init__(self, host, target, profiles):
        quick_widgets.QuickWidget.__init__(self, host, target, profiles)
        cagou_widget.CagouWidget.__init__(self)
        FilterBehavior.__init__(self)
        TouchMenuBehavior.__init__(self)
        self.stack_layout = None
        self.showRootWidget()

    def errback(self, failure_):
        """Generic errback which add a warning note and go back to root widget"""
        G.host.addNote(
            title=NOTE_TITLE,
            message=_("Can't use remote control: {reason}").format(reason=failure_),
            level=C.XMLUI_DATA_LVL_WARNING)
        self.showRootWidget()

    def key_input(self, window, key, scancode, codepoint, modifier):
        if key == 27:
            self.showRootWidget()
            return True

    def showRootWidget(self):
        self.layout.clear_widgets()
        devices_layout = DevicesLayout()
        self.stack_layout = devices_layout.layout
        self.layout.add_widget(devices_layout)
        found = []
        self.get_remotes(found)
        self.discover_devices(found)

    def adHocRemotesGetCb(self, remotes_data, found):
        found.insert(0, remotes_data)
        if len(found) == 2:
            self.show_devices(found)

    def adHocRemotesGetEb(self, failure_, found):
        G.host.errback(failure_, title=_("discovery error"),
                       message=_("can't check remote controllers: {msg}"))
        found.insert(0, [])
        if len(found) == 2:
            self.show_devices(found)

    def get_remotes(self, found):
        self.host.bridge.adHocRemotesGet(
            self.profile,
            callback=partial(self.adHocRemotesGetCb, found=found),
            errback=partial(self.adHocRemotesGetEb,found=found))

    def _discoFindByFeaturesCb(self, data, found):
        found.append(data)
        if len(found) == 2:
            self.show_devices(found)

    def _discoFindByFeaturesEb(self, failure_, found):
        G.host.errback(failure_, title=_("discovery error"),
                       message=_("can't check devices: {msg}"))
        found.append(({}, {}, {}))
        if len(found) == 2:
            self.show_devices(found)

    def discover_devices(self, found):
        """Looks for devices handling file "File Information Sharing" and display them"""
        try:
            namespace = self.host.ns_map['commands']
        except KeyError:
            msg = _("can't find ad-hoc commands namespace, is the plugin running?")
            log.warning(msg)
            G.host.addNote(_("missing plugin"), msg, C.XMLUI_DATA_LVL_ERROR)
            return
        self.host.bridge.discoFindByFeatures(
            [namespace], [], False, True, True, True, False, self.profile,
            callback=partial(self._discoFindByFeaturesCb, found=found),
            errback=partial(self._discoFindByFeaturesEb, found=found))

    def show_devices(self, found):
        remotes_data, (entities_services, entities_own, entities_roster) = found
        if remotes_data:
            title = _("media players remote controls")
            self.stack_layout.add_widget(CategorySeparator(text=title))

        for remote_data in remotes_data:
            device_jid, node, name = remote_data
            wid = RemoteItemWidget(device_jid, node, name, self)
            self.stack_layout.add_widget(wid)

        for entities_map, title in ((entities_services,
                                     _('services')),
                                    (entities_own,
                                     _('your devices')),
                                    (entities_roster,
                                     _('your contacts devices'))):
            if entities_map:
                self.stack_layout.add_widget(CategorySeparator(text=title))
                for entity_str, entity_ids in entities_map.items():
                    entity_jid = jid.JID(entity_str)
                    item = RemoteDeviceWidget(
                        self, entity_jid, Identities(entity_ids))
                    self.stack_layout.add_widget(item)
        if (not remotes_data and not entities_services and not entities_own
            and not entities_roster):
            self.stack_layout.add_widget(Label(
                size_hint=(1, 1),
                halign='center',
                text_size=self.size,
                text=_("No sharing device found")))
