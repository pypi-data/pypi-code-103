#!/usr//bin/env python2


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

"""generic dialogs"""

from sat.core.i18n import _
from cagou.core.constants import Const as C
from kivy.uix.boxlayout import BoxLayout
from kivy import properties
from sat.core import log as logging

log = logging.getLogger(__name__)


class MessageDialog(BoxLayout):
    title = properties.StringProperty()
    message = properties.StringProperty()
    level = properties.OptionProperty(C.XMLUI_DATA_LVL_INFO, options=C.XMLUI_DATA_LVLS)
    close_cb = properties.ObjectProperty()


class ConfirmDialog(BoxLayout):
    title = properties.StringProperty()
    message = properties.StringProperty(_("Are you sure?"))
    # callback for no/cancel
    no_cb = properties.ObjectProperty()
    # callback for yes/ok
    yes_cb = properties.ObjectProperty()
