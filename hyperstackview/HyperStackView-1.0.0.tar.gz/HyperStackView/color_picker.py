# HyperStackView -- application for rendering 3D raster images
# Copyright (C) 2021  Jiří Wolker
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import numpy as np
from PySide6.QtGui import *
from PySide6.QtWidgets import *


class ColorPicker(QColorDialog):
    def __init__(self, app_state, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.app_state = app_state
        self._property_name = None

        self.currentColorChanged.connect(self._store_new_color)

    def _store_new_color(self, color):
        if self._property_name is not None:
            color_floats = [
                color.red() / 255,
                color.green() / 255,
                color.blue() / 255
            ]

            setattr(self.app_state, self._property_name, color_floats)

    def bind_to_property(self, property_name):
        self._property_name = property_name
        self._reload_color()

    def _reload_color(self):
        if self._property_name is not None:
            r, g, b = map(int, (np.array(getattr(self.app_state, self._property_name)) * 255).tolist())
            self.setCurrentColor(QColor(r, g, b))

    def show(self, property_name=None):
        if property_name is not None:
            self.bind_to_property(property_name)

        super().show()
