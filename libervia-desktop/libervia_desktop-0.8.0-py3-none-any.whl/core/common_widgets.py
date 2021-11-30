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

"""common advanced widgets, which can be reused everywhere."""

from kivy.clock import Clock
from kivy import properties
from kivy.metrics import dp
from kivy.uix.scatterlayout import ScatterLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from sat.core.i18n import _
from sat.core import log as logging
from cagou import G
from .behaviors import TouchMenuItemBehavior

log = logging.getLogger(__name__)


class DelayedBoxLayout(BoxLayout):
    """A BoxLayout with delayed layout, to avoid slowing down during resize"""
    # XXX: thanks to Alexander Taylor for his blog post at
    #      https://blog.kivy.org/2019/07/a-delayed-resize-layout-in-kivy/

    do_layout_event = properties.ObjectProperty(None, allownone=True)
    layout_delay_s = properties.NumericProperty(0.2)
    #: set this to X to force next X layouts to be done without delay
    dont_delay_next_layouts = properties.NumericProperty(0)

    def do_layout(self, *args, **kwargs):
        if self.do_layout_event is not None:
            self.do_layout_event.cancel()
        if self.dont_delay_next_layouts>0:
            self.dont_delay_next_layouts-=1
            super().do_layout()
        else:
            real_do_layout = super().do_layout
            self.do_layout_event = Clock.schedule_once(
                lambda dt: real_do_layout(*args, **kwargs),
                self.layout_delay_s)


class Identities(object):

    def __init__(self, entity_ids):
        identities = {}
        for cat, type_, name in entity_ids:
            identities.setdefault(cat, {}).setdefault(type_, []).append(name)
        client = identities.get('client', {})
        if 'pc' in client:
            self.type = 'desktop'
        elif 'phone' in client:
            self.type = 'phone'
        elif 'web' in client:
            self.type = 'web'
        elif 'console' in client:
            self.type = 'console'
        else:
            self.type = 'desktop'

        self.identities = identities

    @property
    def name(self):
        first_identity = next(iter(self.identities.values()))
        names = next(iter(first_identity.values()))
        return names[0]


class ItemWidget(TouchMenuItemBehavior, BoxLayout):
    name = properties.StringProperty()
    base_width = properties.NumericProperty(dp(100))


class DeviceWidget(ItemWidget):

    def __init__(self, main_wid, entity_jid, identities, **kw):
        self.entity_jid = entity_jid
        self.identities = identities
        own_jid = next(iter(G.host.profiles.values())).whoami
        self.own_device = entity_jid.bare == own_jid.bare
        if self.own_device:
            name = self.identities.name
        elif self.entity_jid.node:
            name = self.entity_jid.node
        elif self.entity_jid == own_jid.domain:
            name = _("your server")
        else:
            name = entity_jid

        super(DeviceWidget, self).__init__(name=name, main_wid=main_wid, **kw)

    @property
    def profile(self):
        return self.main_wid.profile

    def getSymbol(self):
        if self.identities.type == 'desktop':
            return 'desktop'
        elif self.identities.type == 'phone':
            return 'mobile'
        elif self.identities.type == 'web':
            return 'globe'
        elif self.identities.type == 'console':
            return 'terminal'
        else:
            return 'desktop'

    def do_item_action(self, touch):
        pass


class CategorySeparator(Label):
    pass


class ImageViewer(ScatterLayout):
    source = properties.StringProperty()

    def on_touch_down(self, touch):
        if touch.is_double_tap:
            self.reset()
            return True
        return super().on_touch_down(touch)

    def reset(self):
        self.rotation = 0
        self.scale = 1
        self.x = 0
        self.y = 0


class ImagesGallery(BoxLayout):
    """Show list of images in a Carousel, with some controls to downloads"""
    sources = properties.ListProperty()
    carousel = properties.ObjectProperty()
    previous_slide = None

    def on_kv_post(self, __):
        self.on_sources(None, self.sources)
        self.previous_slide = self.carousel.current_slide
        self.carousel.bind(current_slide=self.on_slide_change)

    def on_parent(self, __, parent):
        # we hide the head widget to have full screen
        G.host.app.showHeadWidget(not bool(parent), animation=False)

    def on_sources(self, __, sources):
        if not sources or not self.carousel:
            return
        self.carousel.clear_widgets()
        for source in sources:
            img = ImageViewer(
                source=source,
            )
            self.carousel.add_widget(img)

    def on_slide_change(self, __, slide):
        if isinstance(self.previous_slide, ImageViewer):
            self.previous_slide.reset()

        self.previous_slide = slide

    def key_input(self, window, key, scancode, codepoint, modifier):
        if key == 27:
            G.host.closeUI()
            return True
