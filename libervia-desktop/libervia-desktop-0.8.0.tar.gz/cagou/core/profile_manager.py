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
log = logging.getLogger(__name__)
from .constants import Const as C
from sat_frontends.quick_frontend.quick_profile_manager import QuickProfileManager
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.metrics import sp
from kivy import properties
from cagou import G


class ProfileItem(ToggleButton):
    ps = properties.ObjectProperty()
    index = properties.NumericProperty(0)


class NewProfileScreen(Screen):
    profile_name = properties.ObjectProperty(None)
    jid = properties.ObjectProperty(None)
    password = properties.ObjectProperty(None)
    error_msg = properties.StringProperty('')

    def __init__(self, pm):
        super(NewProfileScreen, self).__init__(name='new_profile')
        self.pm = pm

    def onCreationFailure(self, failure):
        msg = [l for l in str(failure).split('\n') if l][-1]
        self.error_msg = str(msg)

    def onCreationSuccess(self, profile):
        self.pm.profiles_screen.reload()
        G.host.bridge.profileStartSession(
            self.password.text, profile,
            callback=lambda __: self._sessionStarted(profile),
            errback=self.onCreationFailure)

    def _sessionStarted(self, profile):
        jid = self.jid.text.strip()
        G.host.bridge.setParam("JabberID", jid, "Connection", -1, profile)
        G.host.bridge.setParam("Password", self.password.text, "Connection", -1, profile)
        self.pm.screen_manager.transition.direction = 'right'
        self.pm.screen_manager.current = 'profiles'

    def doCreate(self):
        name = self.profile_name.text.strip()
        # XXX: we use XMPP password for profile password to simplify
        #      if user want to change profile password, he can do it in preferences
        G.host.bridge.profileCreate(
            name, self.password.text, '',
            callback=lambda: self.onCreationSuccess(name),
            errback=self.onCreationFailure)


class DeleteProfilesScreen(Screen):

    def __init__(self, pm):
        self.pm = pm
        super(DeleteProfilesScreen, self).__init__(name='delete_profiles')

    def doDelete(self):
        """This method will delete *ALL* selected profiles"""
        to_delete = self.pm.getProfiles()
        deleted = [0]

        def deleteInc():
            deleted[0] += 1
            if deleted[0] == len(to_delete):
                self.pm.profiles_screen.reload()
                self.pm.screen_manager.transition.direction = 'right'
                self.pm.screen_manager.current = 'profiles'

        for profile in to_delete:
            log.info("Deleteing profile [{}]".format(profile))
            G.host.bridge.asyncDeleteProfile(
                profile, callback=deleteInc, errback=deleteInc)


class ProfilesScreen(Screen):
    layout = properties.ObjectProperty(None)
    profiles = properties.ListProperty()

    def __init__(self, pm):
        self.pm = pm
        super(ProfilesScreen, self).__init__(name='profiles')
        self.reload()

    def _profilesListGetCb(self, profiles):
        profiles.sort()
        self.profiles = profiles
        for idx, profile in enumerate(profiles):
            item = ProfileItem(ps=self, index=idx, text=profile, group='profiles')
            self.layout.add_widget(item)

    def converter(self, row_idx, obj):
        return {'text': obj,
                'size_hint_y': None,
                'height': sp(40)}

    def reload(self):
        """Reload profiles list"""
        self.layout.clear_widgets()
        G.host.bridge.profilesListGet(callback=self._profilesListGetCb)


class ProfileManager(QuickProfileManager, BoxLayout):
    selected = properties.ObjectProperty(None)

    def __init__(self, autoconnect=None):
        QuickProfileManager.__init__(self, G.host, autoconnect)
        BoxLayout.__init__(self, orientation="vertical")
        self.screen_manager = ScreenManager()
        self.profiles_screen = ProfilesScreen(self)
        self.new_profile_screen = NewProfileScreen(self)
        self.delete_profiles_screen = DeleteProfilesScreen(self)
        self.xmlui_screen = Screen(name='xmlui')
        self.screen_manager.add_widget(self.profiles_screen)
        self.screen_manager.add_widget(self.xmlui_screen)
        self.screen_manager.add_widget(self.new_profile_screen)
        self.screen_manager.add_widget(self.delete_profiles_screen)
        self.add_widget(self.screen_manager)

    def closeUI(self, xmlui, reason=None):
        self.screen_manager.transition.direction = 'right'
        self.screen_manager.current = 'profiles'

    def showUI(self, xmlui):
        xmlui.setCloseCb(self.closeUI)
        if xmlui.type == 'popup':
            xmlui.bind(on_touch_up=lambda obj, value: self.closeUI(xmlui))
        self.xmlui_screen.clear_widgets()
        self.xmlui_screen.add_widget(xmlui)
        self.screen_manager.transition.direction = 'left'
        self.screen_manager.current = 'xmlui'

    def selectProfile(self, profile_item):
        if not profile_item.selected:
            return
        def authenticate_cb(data, cb_id, profile):
            if not C.bool(data.pop('validated', C.BOOL_FALSE)):
                # profile didn't validate, we unselect it
                profile_item.state = 'normal'
                self.selected = ''
            else:
                # state may have been modified so we need to be sure it's down
                profile_item.state = 'down'
                self.selected = profile_item
            G.host.actionManager(data, callback=authenticate_cb, ui_show_cb=self.showUI,
                                 profile=profile)

        G.host.launchAction(C.AUTHENTICATE_PROFILE_ID, callback=authenticate_cb,
                            profile=profile_item.text)

    def getProfiles(self):
        # for now we restrict to a single profile in Cagou
        # TODO: handle multi-profiles
        return [self.selected.text] if self.selected else []
