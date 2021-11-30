#!/usr/bin/env python3

# Cagou: a SàT frontend
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

from sat_frontends.quick_frontend import constants
import cagou

# Kivy must not be imported here due to log hijacking see core/kivy_hack.py


class Const(constants.Const):
    APP_NAME = "Libervia Desktop"
    APP_COMPONENT = "desktop/mobile"
    APP_NAME_ALT = "Cagou"
    APP_NAME_FILE = "libervia_desktop"
    APP_VERSION = cagou.__version__
    LOG_OPT_SECTION = APP_NAME.lower()
    CONFIG_SECTION = "desktop"
    WID_SELECTOR = 'selector'
    ICON_SIZES = ('small', 'medium')  # small = 32, medium = 44
    DEFAULT_WIDGET_ICON = '{media}/misc/black.png'

    BTN_HEIGHT = '35dp'

    PLUG_TYPE_WID = 'wid'
    PLUG_TYPE_TRANSFER = 'transfer'

    TRANSFER_UPLOAD = "upload"
    TRANSFER_SEND = "send"

    COLOR_PRIM = (0.98, 0.98, 0.98, 1)
    COLOR_PRIM_LIGHT = (1, 1, 1, 1)
    COLOR_PRIM_DARK = (0.78, 0.78, 0.78, 1)
    COLOR_SEC = (0.27, 0.54, 1.0, 1)
    COLOR_SEC_LIGHT = (0.51, 0.73, 1.0, 1)
    COLOR_SEC_DARK = (0.0, 0.37, 0.8, 1)

    COLOR_INFO = COLOR_PRIM_LIGHT
    COLOR_WARNING = (1.0, 1.0, 0.0, 1)
    COLOR_ERROR = (1.0, 0.0, 0.0, 1)

    COLOR_BTN_LIGHT = (0.4, 0.4, 0.4, 1)

    # values are in dp
    IMG_MAX_WIDTH = 400
    IMG_MAX_HEIGHT = 400

    # files
    FILE_DEST_DOWNLOAD = "DOWNLOAD"
    FILE_DEST_CACHE = "CACHE"
