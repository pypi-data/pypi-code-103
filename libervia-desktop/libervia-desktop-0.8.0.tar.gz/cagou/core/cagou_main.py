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


import os.path
import glob
import sys
from pathlib import Path
from urllib import parse as urlparse
from functools import partial
from sat.core.i18n import _
from . import kivy_hack
kivy_hack.do_hack()
from .constants import Const as C
from sat.core import log as logging
from sat.core import exceptions
from sat_frontends.quick_frontend.quick_app import QuickApp
from sat_frontends.quick_frontend import quick_widgets
from sat_frontends.quick_frontend import quick_chat
from sat_frontends.quick_frontend import quick_utils
from sat_frontends.tools import jid
from sat.tools import utils as sat_utils
from sat.tools import config
from sat.tools.common import data_format
from sat.tools.common import dynamic_import
from sat.tools.common import files_utils
import kivy
kivy.require('1.11.0')
import kivy.support
main_config = config.parseMainConf(log_filenames=True)
bridge_name = config.getConfig(main_config, '', 'bridge', 'dbus')
# FIXME: event loop is choosen according to bridge_name, a better way should be used
if 'dbus' in bridge_name:
    kivy.support.install_gobject_iteration()
elif bridge_name in ('pb', 'embedded'):
    kivy.support.install_twisted_reactor()
from kivy.app import App
from kivy.lang import Builder
from kivy import properties
from . import xmlui
from .profile_manager import ProfileManager
from kivy.clock import Clock
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.screenmanager import (ScreenManager, Screen,
                                    FallOutTransition, RiseInTransition)
from kivy.uix.dropdown import DropDown
from kivy.uix.behaviors import ButtonBehavior
from kivy.core.window import Window
from kivy.animation import Animation
from kivy.metrics import dp
from .cagou_widget import CagouWidget
from .share_widget import ShareWidget
from . import widgets_handler
from .common import IconButton
from . import dialog
from importlib import import_module
import sat
import cagou
import cagou.plugins
import cagou.kv


log = logging.getLogger(__name__)


try:
    from plyer import notification
except ImportError:
    notification = None
    log.warning(_("Can't import plyer, some features disabled"))


## platform specific settings ##

from . import platform_
local_platform = platform_.create()
local_platform.init_platform()


## General Configuration ##

# we want white background by default
Window.clearcolor = (1, 1, 1, 1)


class NotifsIcon(IconButton):
    notifs = properties.ListProperty()

    def on_release(self):
        callback, args, kwargs = self.notifs.pop(0)
        callback(*args, **kwargs)

    def addNotif(self, callback, *args, **kwargs):
        self.notifs.append((callback, args, kwargs))


class Note(Label):
    title = properties.StringProperty()
    message = properties.StringProperty()
    level = properties.OptionProperty(C.XMLUI_DATA_LVL_DEFAULT,
                                      options=list(C.XMLUI_DATA_LVLS))
    symbol = properties.StringProperty()
    action = properties.ObjectProperty()


class NoteDrop(ButtonBehavior, BoxLayout):
    title = properties.StringProperty()
    message = properties.StringProperty()
    level = properties.OptionProperty(C.XMLUI_DATA_LVL_DEFAULT,
                                      options=list(C.XMLUI_DATA_LVLS))
    symbol = properties.StringProperty()
    action = properties.ObjectProperty()

    def on_press(self):
        if self.action is not None:
            self.parent.parent.select(self.action)


class NotesDrop(DropDown):
    clear_btn = properties.ObjectProperty()

    def __init__(self, notes):
        super(NotesDrop, self).__init__()
        self.notes = notes

    def open(self, widget):
        self.clear_widgets()
        for n in self.notes:
            kwargs = {
                'title': n.title,
                'message': n.message,
                'level': n.level
            }
            if n.symbol is not None:
                kwargs['symbol'] = n.symbol
            if n.action is not None:
                kwargs['action'] = n.action
            self.add_widget(NoteDrop(title=n.title, message=n.message, level=n.level,
                                     symbol=n.symbol, action=n.action))
        self.add_widget(self.clear_btn)
        super(NotesDrop, self).open(widget)

    def on_select(self, action_kwargs):
        app = App.get_running_app()
        app.host.doAction(**action_kwargs)


class RootHeadWidget(BoxLayout):
    """Notifications widget"""
    manager = properties.ObjectProperty()
    notifs_icon = properties.ObjectProperty()
    notes = properties.ListProperty()
    HEIGHT = dp(35)

    def __init__(self):
        super(RootHeadWidget, self).__init__()
        self.notes_last = None
        self.notes_event = None
        self.notes_drop = NotesDrop(self.notes)

    def addNotif(self, callback, *args, **kwargs):
        """add a notification with a callback attached

        when notification is pressed, callback is called
        @param *args, **kwargs: arguments of callback
        """
        self.notifs_icon.addNotif(callback, *args, **kwargs)

    def addNote(self, title, message, level, symbol, action):
        kwargs = {
            'title': title,
            'message': message,
            'level': level
        }
        if symbol is not None:
            kwargs['symbol'] = symbol
        if action is not None:
            kwargs['action'] = action
        note = Note(**kwargs)
        self.notes.append(note)
        if self.notes_event is None:
            self.notes_event = Clock.schedule_interval(self._displayNextNote, 5)
            self._displayNextNote()

    def addNotifUI(self, ui):
        self.notifs_icon.addNotif(ui.show, force=True)

    def addNotifWidget(self, widget):
        app = App.get_running_app()
        self.notifs_icon.addNotif(app.host.showExtraUI, widget=widget)

    def _displayNextNote(self, __=None):
        screen = Screen()
        try:
            idx = self.notes.index(self.notes_last) + 1
        except ValueError:
            idx = 0
        try:
            note = self.notes_last = self.notes[idx]
        except IndexError:
            self.notes_event.cancel()
            self.notes_event = None
        else:
            screen.add_widget(note)
        self.manager.switch_to(screen)


class RootBody(BoxLayout):
    pass


class CagouRootWidget(FloatLayout):
    root_body = properties.ObjectProperty

    def __init__(self, main_widget):
        super(CagouRootWidget, self).__init__()
        # header
        self.head_widget = RootHeadWidget()
        self.root_body.add_widget(self.head_widget)
        # body
        self._manager = ScreenManager()
        # main widgets
        main_screen = Screen(name='main')
        main_screen.add_widget(main_widget)
        self._manager.add_widget(main_screen)
        # backend XMLUI (popups, forms, etc)
        xmlui_screen = Screen(name='xmlui')
        self._manager.add_widget(xmlui_screen)
        # extra (file chooser, audio record, etc)
        extra_screen = Screen(name='extra')
        self._manager.add_widget(extra_screen)
        self.root_body.add_widget(self._manager)

    def changeWidget(self, widget, screen_name="main"):
        """change main widget"""
        if self._manager.transition.is_active:
            # FIXME: workaround for what seems a Kivy bug
            # TODO: report this upstream
            self._manager.transition.stop()
        screen = self._manager.get_screen(screen_name)
        screen.clear_widgets()
        screen.add_widget(widget)

    def show(self, screen="main"):
        if self._manager.transition.is_active:
            # FIXME: workaround for what seems a Kivy bug
            # TODO: report this upstream
            self._manager.transition.stop()
        if self._manager.current == screen:
            return
        if screen == "main":
            self._manager.transition = FallOutTransition()
        else:
            self._manager.transition = RiseInTransition()
        self._manager.current = screen

    def newAction(self, handler, action_data, id_, security_limit, profile):
        """Add a notification for an action"""
        self.head_widget.addNotif(handler, action_data, id_, security_limit, profile)

    def addNote(self, title, message, level, symbol, action):
        self.head_widget.addNote(title, message, level, symbol, action)

    def addNotifUI(self, ui):
        self.head_widget.addNotifUI(ui)

    def addNotifWidget(self, widget):
        self.head_widget.addNotifWidget(widget)


class CagouApp(App):
    """Kivy App for Cagou"""
    c_prim = properties.ListProperty(C.COLOR_PRIM)
    c_prim_light = properties.ListProperty(C.COLOR_PRIM_LIGHT)
    c_prim_dark = properties.ListProperty(C.COLOR_PRIM_DARK)
    c_sec = properties.ListProperty(C.COLOR_SEC)
    c_sec_light = properties.ListProperty(C.COLOR_SEC_LIGHT)
    c_sec_dark = properties.ListProperty(C.COLOR_SEC_DARK)
    connected = properties.BooleanProperty(False)
    # we have to put those constants here and not in core/constants.py
    # because of the use of dp(), which would import Kivy too early
    # and prevent the log hack
    MARGIN_LEFT = MARGIN_RIGHT = dp(10)

    def _install_settings_keys(self, window):
        # we don't want default Kivy's behaviour of displaying
        # a settings screen when pressing F1 or platform specific key
        return

    def build(self):
        Window.bind(on_keyboard=self.key_input)
        Window.bind(on_dropfile=self.on_dropfile)
        wid = CagouRootWidget(Label(text=_("Loading please wait")))
        local_platform.on_app_build(wid)
        return wid

    def showProfileManager(self):
        self._profile_manager = ProfileManager()
        self.root.changeWidget(self._profile_manager)

    def expand(self, path, *args, **kwargs):
        """expand path and replace known values

        useful in kv. Values which can be used:
            - {media}: media dir
        @param path(unicode): path to expand
        @param *args: additional arguments used in format
        @param **kwargs: additional keyword arguments used in format
        """
        return os.path.expanduser(path).format(*args, media=self.host.media_dir, **kwargs)

    def initFrontendState(self):
        """Init state to handle paused/stopped/running on mobile OSes"""
        local_platform.on_initFrontendState()

    def on_pause(self):
        return local_platform.on_pause()

    def on_resume(self):
        return local_platform.on_resume()

    def on_stop(self):
        return local_platform.on_stop()

    def showHeadWidget(self, show=None, animation=True):
        """Show/Hide the head widget

        @param show(bool, None): True to show, False to hide, None to switch
        @param animation(bool): animate the show/hide if True
        """
        head = self.root.head_widget
        if bool(self.root.head_widget.height) == show:
            return
        if head.height:
            if animation:
                Animation(height=0, opacity=0, duration=0.3).start(head)
            else:
                head.height = head.opacity = 0
        else:
            if animation:
                Animation(height=head.HEIGHT, opacity=1, duration=0.3).start(head)
            else:
                head.height = head.HEIGHT
                head.opacity = 1

    def key_input(self, window, key, scancode, codepoint, modifier):

        # we first check if selected widget handles the key
        if ((self.host.selected_widget is not None
             and hasattr(self.host.selected_widget, 'key_input')
             and self.host.selected_widget.key_input(window, key, scancode, codepoint,
                 modifier))):
            return True

        if key == 27:
            if ((self.host.selected_widget is None
                 or self.host.selected_widget.__class__ == self.host.default_class)):
                # we are on root widget, or nothing is selected
                return local_platform.on_key_back_root()

            # we disable [esc] handling, because default action is to quit app
            return True
        elif key == 292:
            # F11: full screen
            if not Window.fullscreen:
                Window.fullscreen = 'auto'
            else:
                Window.fullscreen = False
            return True
        elif key == 110 and 'alt' in modifier:
            # M-n we hide/show notifications
            self.showHeadWidget()
            return True
        else:
            return False

    def on_dropfile(self, __, file_path):
        if self.host.selected_widget is not None:
            try:
                on_drop_file = self.host.selected_widget.on_drop_file
            except AttributeError:
                log.info(
                    f"Select widget {self.host.selected_widget} doesn't handle file "
                    f"dropping")
            else:
                on_drop_file(Path(file_path.decode()))


class Cagou(QuickApp):
    MB_HANDLE = False
    AUTO_RESYNC = False

    def __init__(self):
        if bridge_name == 'embedded':
            from sat.core import sat_main
            self.sat = sat_main.SAT()

        bridge_module = dynamic_import.bridge(bridge_name, 'sat_frontends.bridge')
        if bridge_module is None:
            log.error(f"Can't import {bridge_name} bridge")
            sys.exit(3)
        else:
            log.debug(f"Loading {bridge_name} bridge")
        super(Cagou, self).__init__(bridge_factory=bridge_module.Bridge,
                                    xmlui=xmlui,
                                    check_options=quick_utils.check_options,
                                    connect_bridge=False)
        self._import_kv()
        self.app = CagouApp()
        self.app.host = self
        self.media_dir = self.app.media_dir = config.getConfig(main_config, '',
                                                               'media_dir')
        self.downloads_dir = self.app.downloads_dir = config.getConfig(main_config, '',
                                                                       'downloads_dir')
        if not os.path.exists(self.downloads_dir):
            try:
                os.makedirs(self.downloads_dir)
            except OSError as e:
                log.warnings(_("Can't create downloads dir: {reason}").format(reason=e))
        self.app.default_avatar = os.path.join(self.media_dir, "misc/default_avatar.png")
        self.app.icon = os.path.join(self.media_dir,
                                     "icons/muchoslava/png/cagou_profil_bleu_96.png")
        # main widgets plugins
        self._plg_wids = []
        # transfer widgets plugins
        self._plg_wids_transfer = []
        self._import_plugins()
        # visible widgets by classes
        self._visible_widgets = {}
        # used to keep track of last selected widget in "main" screen when changing
        # root screen
        self._selected_widget_main = None
        self.backend_version = sat.__version__  # will be replaced by getVersion()
        if C.APP_VERSION.endswith('D'):
            self.version = "{} {}".format(
                C.APP_VERSION,
                sat_utils.getRepositoryData(cagou)
            )
        else:
            self.version = C.APP_VERSION

        self.tls_validation =  not C.bool(config.getConfig(main_config,
                                                           C.CONFIG_SECTION,
                                                           'no_certificate_validation',
                                                           C.BOOL_FALSE))
        if not self.tls_validation:
            from cagou.core import patches
            patches.disable_tls_validation()
            log.warning("SSL certificate validation is disabled, this is unsecure!")

        local_platform.on_host_init(self)

    @property
    def visible_widgets(self):
        for w_list in self._visible_widgets.values():
            for w in w_list:
                yield w

    @property
    def default_class(self):
        if self.default_wid is None:
            return None
        return self.default_wid['main']

    @QuickApp.sync.setter
    def sync(self, state):
        QuickApp.sync.fset(self, state)
        # widget are resynchronised in onVisible event,
        # so we must call resync for widgets which are already visible
        if state:
            for w in self.visible_widgets:
                try:
                    resync = w.resync
                except AttributeError:
                    pass
                else:
                    resync()
            self.contact_lists.fill()

    def getConfig(self, section, name, default=None):
        return config.getConfig(main_config, section, name, default)

    def onBridgeConnected(self):
        super(Cagou, self).onBridgeConnected()
        self.registerSignal("otrState", iface="plugin")

    def _bridgeEb(self, failure):
        if bridge_name == "pb" and sys.platform == "android":
            try:
                self.retried += 1
            except AttributeError:
                self.retried = 1
            if ((isinstance(failure, exceptions.BridgeExceptionNoService)
                 and self.retried < 100)):
                if self.retried % 20 == 0:
                    log.debug("backend not ready, retrying ({})".format(self.retried))
                Clock.schedule_once(lambda __: self.connectBridge(), 0.05)
                return
        super(Cagou, self)._bridgeEb(failure)

    def run(self):
        self.connectBridge()
        self.app.bind(on_stop=self.onStop)
        self.app.run()

    def onStop(self, obj):
        try:
            sat_instance = self.sat
        except AttributeError:
            pass
        else:
            sat_instance.stopService()

    def _getVersionCb(self, version):
        self.backend_version = version

    def onBackendReady(self):
        super().onBackendReady()
        self.app.showProfileManager()
        self.bridge.getVersion(callback=self._getVersionCb)
        self.app.initFrontendState()
        if local_platform.do_postInit():
            self.postInit()

    def postInit(self, __=None):
        # FIXME: resize doesn't work with SDL2 on android, so we use below_target for now
        self.app.root_window.softinput_mode = "below_target"
        profile_manager = self.app._profile_manager
        del self.app._profile_manager
        super(Cagou, self).postInit(profile_manager)

    def profilePlugged(self, profile):
        super().profilePlugged(profile)
        # FIXME: this won't work with multiple profiles
        self.app.connected = self.profiles[profile].connected

    def _bookmarksListCb(self, bookmarks_dict, profile):
        bookmarks = set()
        for data in bookmarks_dict.values():
            bookmarks.update({jid.JID(k) for k in data.keys()})
        self.profiles[profile]._bookmarks = sorted(bookmarks)

    def profileConnected(self, profile):
        self.bridge.bookmarksList(
            "muc", "all", profile,
            callback=partial(self._bookmarksListCb, profile=profile),
            errback=partial(self.errback, title=_("Bookmark error")))

    def _defaultFactoryMain(self, plugin_info, target, profiles):
        """default factory used to create main widgets instances

        used when PLUGIN_INFO["factory"] is not set
        @param plugin_info(dict): plugin datas
        @param target: QuickWidget target
        @param profiles(iterable): list of profiles
        """
        main_cls = plugin_info['main']
        return self.widgets.getOrCreateWidget(main_cls,
                                              target,
                                              on_new_widget=None,
                                              profiles=iter(self.profiles))

    def _defaultFactoryTransfer(self, plugin_info, callback, cancel_cb, profiles):
        """default factory used to create transfer widgets instances

        @param plugin_info(dict): plugin datas
        @param callback(callable): method to call with path to file to transfer
        @param cancel_cb(callable): call when transfer is cancelled
            transfer widget must be used as first argument
        @param profiles(iterable): list of profiles
            None if not specified
        """
        main_cls = plugin_info['main']
        return main_cls(callback=callback, cancel_cb=cancel_cb)

    ## plugins & kv import ##

    def _import_kv(self):
        """import all kv files in cagou.kv"""
        path = os.path.dirname(cagou.kv.__file__)
        kv_files = glob.glob(os.path.join(path, "*.kv"))
        # we want to be sure that base.kv is loaded first
        # as it override some Kivy widgets properties
        for kv_file in kv_files:
            if kv_file.endswith('base.kv'):
                kv_files.remove(kv_file)
                kv_files.insert(0, kv_file)
                break
        else:
            raise exceptions.InternalError("base.kv is missing")

        for kv_file in kv_files:
            Builder.load_file(kv_file)
            log.debug(f"kv file {kv_file} loaded")

    def _import_plugins(self):
        """import all plugins"""
        self.default_wid = None
        plugins_path = os.path.dirname(cagou.plugins.__file__)
        plugin_glob = "plugin*." + C.PLUGIN_EXT
        plug_lst = [os.path.splitext(p)[0] for p in
                    map(os.path.basename, glob.glob(os.path.join(plugins_path,
                                                                 plugin_glob)))]

        imported_names_main = set()  # used to avoid loading 2 times
                                     # plugin with same import name
        imported_names_transfer = set()
        for plug in plug_lst:
            plugin_path = 'cagou.plugins.' + plug

            # we get type from plugin name
            suff = plug[7:]
            if '_' not in suff:
                log.error("invalid plugin name: {}, skipping".format(plug))
                continue
            plugin_type = suff[:suff.find('_')]

            # and select the variable to use according to type
            if plugin_type == C.PLUG_TYPE_WID:
                imported_names = imported_names_main
                default_factory = self._defaultFactoryMain
            elif plugin_type == C.PLUG_TYPE_TRANSFER:
                imported_names = imported_names_transfer
                default_factory = self._defaultFactoryTransfer
            else:
                log.error("unknown plugin type {type_} for plugin {file_}, skipping"
                    .format(
                    type_ = plugin_type,
                    file_ = plug
                    ))
                continue
            plugins_set = self._getPluginsSet(plugin_type)

            mod = import_module(plugin_path)
            try:
                plugin_info = mod.PLUGIN_INFO
            except AttributeError:
                plugin_info = {}

            plugin_info['plugin_file'] = plug
            plugin_info['plugin_type'] = plugin_type

            if 'platforms' in plugin_info:
                if sys.platform not in plugin_info['platforms']:
                    log.info("{plugin_file} is not used on this platform, skipping"
                             .format(**plugin_info))
                    continue

            # import name is used to differentiate plugins
            if 'import_name' not in plugin_info:
                plugin_info['import_name'] = plug
            if plugin_info['import_name'] in imported_names:
                log.warning(_("there is already a plugin named {}, "
                              "ignoring new one").format(plugin_info['import_name']))
                continue
            if plugin_info['import_name'] == C.WID_SELECTOR:
                if plugin_type != C.PLUG_TYPE_WID:
                    log.error("{import_name} import name can only be used with {type_} "
                              "type, skipping {name}".format(type_=C.PLUG_TYPE_WID,
                                                              **plugin_info))
                    continue
                # if WidgetSelector exists, it will be our default widget
                self.default_wid = plugin_info

            # we want everything optional, so we use plugin file name
            # if actual name is not found
            if 'name' not in plugin_info:
                name_start = 8 + len(plugin_type)
                plugin_info['name'] = plug[name_start:]

            # we need to load the kv file
            if 'kv_file' not in plugin_info:
                plugin_info['kv_file'] = '{}.kv'.format(plug)
            kv_path = os.path.join(plugins_path, plugin_info['kv_file'])
            if not os.path.exists(kv_path):
                log.debug("no kv found for {plugin_file}".format(**plugin_info))
            else:
                Builder.load_file(kv_path)

            # what is the main class ?
            main_cls = getattr(mod, plugin_info['main'])
            plugin_info['main'] = main_cls

            # factory is used to create the instance
            # if not found, we use a defaut one with getOrCreateWidget
            if 'factory' not in plugin_info:
                plugin_info['factory'] = default_factory

            # icons
            for size in ('small', 'medium'):
                key = 'icon_{}'.format(size)
                try:
                    path = plugin_info[key]
                except KeyError:
                    path = C.DEFAULT_WIDGET_ICON.format(media=self.media_dir)
                else:
                    path = path.format(media=self.media_dir)
                    if not os.path.isfile(path):
                        path = C.DEFAULT_WIDGET_ICON.format(media=self.media_dir)
                plugin_info[key] = path

            plugins_set.append(plugin_info)
        if not self._plg_wids:
            log.error(_("no widget plugin found"))
            return

        # we want widgets sorted by names
        self._plg_wids.sort(key=lambda p: p['name'].lower())
        self._plg_wids_transfer.sort(key=lambda p: p['name'].lower())

        if self.default_wid is None:
            # we have no selector widget, we use the first widget as default
            self.default_wid = self._plg_wids[0]

    def _getPluginsSet(self, type_):
        if type_ == C.PLUG_TYPE_WID:
            return self._plg_wids
        elif type_ == C.PLUG_TYPE_TRANSFER:
            return self._plg_wids_transfer
        else:
            raise KeyError("{} plugin type is unknown".format(type_))

    def getPluggedWidgets(self, type_=C.PLUG_TYPE_WID, except_cls=None):
        """get available widgets plugin infos

        @param type_(unicode): type of widgets to get
            one of C.PLUG_TYPE_* constant
        @param except_cls(None, class): if not None,
            widgets from this class will be excluded
        @return (iter[dict]): available widgets plugin infos
        """
        plugins_set = self._getPluginsSet(type_)
        for plugin_data in plugins_set:
            if plugin_data['main'] == except_cls:
                continue
            yield plugin_data

    def getPluginInfo(self, type_=C.PLUG_TYPE_WID, **kwargs):
        """get first plugin info corresponding to filters

        @param type_(unicode): type of widgets to get
            one of C.PLUG_TYPE_* constant
        @param **kwargs: filter(s) to use, each key present here must also
            exist and be of the same value in requested plugin info
        @return (dict, None): found plugin info or None
        """
        plugins_set = self._getPluginsSet(type_)
        for plugin_info in plugins_set:
            for k, w in kwargs.items():
                try:
                    if plugin_info[k] != w:
                        continue
                except KeyError:
                    continue
                return plugin_info

    ## widgets handling

    def newWidget(self, widget):
        log.debug("new widget created: {}".format(widget))
        if isinstance(widget, quick_chat.QuickChat) and widget.type == C.CHAT_GROUP:
            self.addNote("", _("room {} has been joined").format(widget.target))

    def switchWidget(self, old, new=None):
        """Replace old widget by new one

        @param old(CagouWidget, None): CagouWidget instance or a child
            None to select automatically widget to switch
        @param new(CagouWidget): new widget instance
            None to use default widget
        @return (CagouWidget): new widget
        """
        if old is None:
            old = self.getWidgetToSwitch()
        if new is None:
            factory = self.default_wid['factory']
            try:
                profiles = old.profiles
            except AttributeError:
                profiles = None
            new = factory(self.default_wid, None, profiles=profiles)
        to_change = None
        if isinstance(old, CagouWidget):
            to_change = old
        else:
            for w in old.walk_reverse():
                if isinstance(w, CagouWidget):
                    to_change = w
                    break

        if to_change is None:
            raise exceptions.InternalError("no CagouWidget found when "
                                           "trying to switch widget")

        # selected_widget can be modified in changeWidget, so we need to set it before
        self.selected_widget = new
        if to_change == new:
            log.debug("switchWidget called with old==new, nothing to do")
            return new
        to_change.whwrapper.changeWidget(new)
        return new

    def _addVisibleWidget(self, widget):
        """declare a widget visible

        for internal use only!
        """
        assert isinstance(widget, CagouWidget)
        log.debug(f"Visible widget: {widget}")
        self._visible_widgets.setdefault(widget.__class__, set()).add(widget)
        log.debug(f"visible widgets list: {self.getVisibleList(None)}")
        widget.onVisible()

    def _removeVisibleWidget(self, widget, ignore_missing=False):
        """declare a widget not visible anymore

        for internal use only!
        """
        log.debug(f"Widget not visible anymore: {widget}")
        try:
            self._visible_widgets[widget.__class__].remove(widget)
        except KeyError as e:
            if not ignore_missing:
                log.error(f"trying to remove a not visible widget ({widget}): {e}")
            return
        log.debug(f"visible widgets list: {self.getVisibleList(None)}")
        if isinstance(widget, CagouWidget):
            widget.onNotVisible()
        if isinstance(widget, quick_widgets.QuickWidget):
            self.widgets.deleteWidget(widget)

    def getVisibleList(self, cls):
        """get list of visible widgets for a given class

        @param cls(type): type of widgets to get
            None to get all visible widgets
        @return (set[type]): visible widgets of this class
        """
        if cls is None:
            ret = set()
            for widgets in self._visible_widgets.values():
                for w in widgets:
                    ret.add(w)
            return ret
        try:
            return self._visible_widgets[cls]
        except KeyError:
            return set()

    def deleteUnusedWidgetInstances(self, widget):
        """Delete instance of this widget which are not attached to a WHWrapper

        @param widget(quick_widgets.QuickWidget): reference widget
            other instance of this widget will be deleted if they have no parent
        """
        to_delete = []
        if isinstance(widget, quick_widgets.QuickWidget):
            for w in self.widgets.getWidgetInstances(widget):
                if w.whwrapper is None and w != widget:
                    to_delete.append(w)
            for w in to_delete:
                log.debug("cleaning widget: {wid}".format(wid=w))
                self.widgets.deleteWidget(w)

    def getOrClone(self, widget, **kwargs):
        """Get a QuickWidget if it is not in a WHWrapper, else clone it

        if an other instance of this widget exist without being in a WHWrapper
        (i.e. if it is not already in use) it will be used.
        """
        if widget.whwrapper is None:
            if widget.parent is not None:
                widget.parent.remove_widget(widget)
            self.deleteUnusedWidgetInstances(widget)
            return widget
        for w in self.widgets.getWidgetInstances(widget):
            if w.whwrapper is None:
                if w.parent is not None:
                    w.parent.remove_widget(w)
                self.deleteUnusedWidgetInstances(w)
                return w
        targets = list(widget.targets)
        w = self.widgets.getOrCreateWidget(widget.__class__,
                                           targets[0],
                                           on_new_widget=None,
                                           on_existing_widget=C.WIDGET_RECREATE,
                                           profiles=widget.profiles,
                                           **kwargs)
        for t in targets[1:]:
            w.addTarget(t)
        return w

    def getWidgetToSwitch(self):
        """Choose best candidate when we need to switch widget and old is not specified

        @return (CagouWidget): widget to switch
        """
        if (self._selected_widget_main is not None
            and self._selected_widget_main.whwrapper is not None):
            # we are not on the main screen, we want to switch a widget from main screen
            return self._selected_widget_main
        elif (self.selected_widget is not None
              and isinstance(self.selected_widget, CagouWidget)
              and self.selected_widget.whwrapper is not None):
            return self.selected_widget
        # no widget is selected we check if we have any default widget
        default_cls = self.default_class
        for w in self.visible_widgets:
            if isinstance(w, default_cls):
                return w

        # no default widget found, we return the first widget
        return next(iter(self.visible_widgets))

    def doAction(self, action, target, profiles):
        """Launch an action handler by a plugin

        @param action(unicode): action to do, can be:
            - chat: open a chat widget
        @param target(unicode): target of the action
        @param profiles(list[unicode]): profiles to use
        @return (CagouWidget, None): new widget
        """
        try:
            # FIXME: Q&D way to get chat plugin, should be replaced by a clean method
            #        in host
            plg_infos = [p for p in self.getPluggedWidgets()
                         if action in p['import_name']][0]
        except IndexError:
            log.warning("No plugin widget found to do {action}".format(action=action))
        else:
            try:
                # does the widget already exist?
                wid = next(self.widgets.getWidgets(
                    plg_infos['main'],
                    target=target,
                    profiles=profiles))
            except StopIteration:
                # no, let's create a new one
                factory = plg_infos['factory']
                wid = factory(plg_infos, target=target, profiles=profiles)

            return self.switchWidget(None, wid)

    ## bridge handlers ##

    def otrStateHandler(self, state, dest_jid, profile):
        """OTR state has changed for on destinee"""
        # XXX: this method could be in QuickApp but it's here as
        #      it's only used by Cagou so far
        dest_jid = jid.JID(dest_jid)
        bare_jid = dest_jid.bare
        for widget in self.widgets.getWidgets(quick_chat.QuickChat, profiles=(profile,)):
            if widget.type == C.CHAT_ONE2ONE and widget.target == bare_jid:
                widget.onOTRState(state, dest_jid, profile)

    def _debugHandler(self, action, parameters, profile):
        if action == "visible_widgets_dump":
            from pprint import pformat
            log.info("Visible widgets dump:\n{data}".format(
                data=pformat(self._visible_widgets)))
        else:
            return super(Cagou, self)._debugHandler(action, parameters, profile)

    def connectedHandler(self, jid_s, profile):
        # FIXME: this won't work with multiple profiles
        super().connectedHandler(jid_s, profile)
        self.app.connected = True

    def disconnectedHandler(self, profile):
        # FIXME: this won't work with multiple profiles
        super().disconnectedHandler(profile)
        self.app.connected = False

    ## misc ##

    def plugging_profiles(self):
        self.widgets_handler = widgets_handler.WidgetsHandler()
        self.app.root.changeWidget(self.widgets_handler)

    def setPresenceStatus(self, show='', status=None, profile=C.PROF_KEY_NONE):
        log.info("Profile presence status set to {show}/{status}".format(show=show,
                                                                          status=status))

    def errback(self, failure_, title=_('error'),
                message=_('error while processing: {msg}')):
        self.addNote(title, message.format(msg=failure_), level=C.XMLUI_DATA_LVL_WARNING)

    def addNote(self, title, message, level=C.XMLUI_DATA_LVL_INFO, symbol=None,
        action=None):
        """add a note (message which disappear) to root widget's header"""
        self.app.root.addNote(title, message, level, symbol, action)

    def addNotifUI(self, ui):
        """add a notification with a XMLUI attached

        @param ui(xmlui.XMLUIPanel): XMLUI instance to show when notification is selected
        """
        self.app.root.addNotifUI(ui)

    def addNotifWidget(self, widget):
        """add a notification with a Kivy widget attached

        @param widget(kivy.uix.Widget): widget to attach to notification
        """
        self.app.root.addNotifWidget(widget)

    def showUI(self, ui):
        """show a XMLUI"""
        self.app.root.changeWidget(ui, "xmlui")
        self.app.root.show("xmlui")
        self._selected_widget_main = self.selected_widget
        self.selected_widget = ui

    def showExtraUI(self, widget):
        """show any extra widget"""
        self.app.root.changeWidget(widget, "extra")
        self.app.root.show("extra")
        self._selected_widget_main = self.selected_widget
        self.selected_widget = widget

    def closeUI(self):
        self.app.root.show()
        self.selected_widget = self._selected_widget_main
        self._selected_widget_main = None
        screen = self.app.root._manager.get_screen("extra")
        screen.clear_widgets()

    def getDefaultAvatar(self, entity=None):
        return self.app.default_avatar

    def _dialog_cb(self, cb, *args, **kwargs):
        """generic dialog callback

        close dialog then call the callback with given arguments
        """
        def callback():
            self.closeUI()
            cb(*args, **kwargs)
        return callback

    def showDialog(self, message, title, type="info", answer_cb=None, answer_data=None):
        if type in ('info', 'warning', 'error'):
            self.addNote(title, message, type)
        elif type == "yes/no":
            wid = dialog.ConfirmDialog(title=title, message=message,
                                       yes_cb=self._dialog_cb(answer_cb,
                                                              True,
                                                              answer_data),
                                       no_cb=self._dialog_cb(answer_cb,
                                                             False,
                                                             answer_data)
                                       )
            self.addNotifWidget(wid)
        else:
            log.warning(_("unknown dialog type: {dialog_type}").format(dialog_type=type))

    def share(self, media_type, data):
        share_wid = ShareWidget(media_type=media_type, data=data)
        try:
            self.showExtraUI(share_wid)
        except Exception as e:
            log.error(e)
            self.closeUI()

    def downloadURL(
        self, url, callback, errback=None, options=None, dest=C.FILE_DEST_DOWNLOAD,
        profile=C.PROF_KEY_NONE):
        """Download an URL (decrypt it if necessary)

        @param url(str, parse.SplitResult): url to download
        @param callback(callable): method to call when download is complete
        @param errback(callable, None): method to call in case of error
            if None, default errback will be called
        @param dest(str): where the file should be downloaded:
            - C.FILE_DEST_DOWNLOAD: in platform download directory
            - C.FILE_DEST_CACHE: in SàT cache
        @param options(dict, None): options to pass to bridge.fileDownloadComplete
        """
        if not isinstance(url, urlparse.ParseResult):
            url = urlparse.urlparse(url)
        if errback is None:
            errback = partial(
                self.errback,
                title=_("Download error"),
                message=_("Error while downloading {url}: {{msg}}").format(url=url.geturl()))
        name = Path(url.path).name.strip() or C.FILE_DEFAULT_NAME
        log.info(f"downloading/decrypting file {name!r}")
        if dest == C.FILE_DEST_DOWNLOAD:
            dest_path = files_utils.get_unique_name(Path(self.downloads_dir)/name)
        elif dest == C.FILE_DEST_CACHE:
            dest_path = ''
        else:
            raise exceptions.InternalError(f"Invalid dest_path: {dest_path!r}")
        self.bridge.fileDownloadComplete(
            url.geturl(),
            str(dest_path),
            '' if not options else data_format.serialise(options),
            profile,
            callback=callback,
            errback=errback
        )

    def notify(self, type_, entity=None, message=None, subject=None, callback=None,
               cb_args=None, widget=None, profile=C.PROF_KEY_NONE):
        super().notify(
            type_=type_, entity=entity, message=message, subject=subject,
            callback=callback, cb_args=cb_args, widget=widget, profile=profile)
        self.desktop_notif(message, title=subject)

    def desktop_notif(self, message, title='', duration=5):
        global notification
        if notification is not None:
            try:
                log.debug(
                    f"sending desktop notification (duration: {duration}):\n"
                    f"{title}\n"
                    f"{message}"
                )
                notification.notify(title=title,
                                    message=message,
                                    app_name=C.APP_NAME,
                                    app_icon=self.app.icon,
                                    timeout=duration)
            except Exception as e:
                log.warning(_("Can't use notifications, disabling: {msg}").format(
                    msg = e))
                notification = None

    def getParentWHWrapper(self, wid):
        """Retrieve parent WHWrapper instance managing a widget

        @param wid(Widget): widget to check
        @return (WHWrapper, None): found instance if any, else None
        """
        wh = self.getAncestorWidget(wid, widgets_handler.WHWrapper)
        if wh is None:
            # we may have a screen
            try:
                sm = wid.screen_manager
            except (exceptions.InternalError, exceptions.NotFound):
                return None
            else:
                wh = self.getAncestorWidget(sm, widgets_handler.WHWrapper)
        return wh

    def getAncestorWidget(self, wid, cls):
        """Retrieve an ancestor of given class

        @param wid(Widget): current widget
        @param cls(type): class of the ancestor to retrieve
        @return (Widget, None): found instance or None
        """
        parent = wid.parent
        while parent and not isinstance(parent, cls):
            parent = parent.parent
        return parent
