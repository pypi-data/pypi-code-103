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

from PySide6.QtWidgets import *
import numpy as np


class ColorButton(QPushButton):
    def __init__(self, app_state, color_picker, property_name, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.app_state = app_state
        self.property_name = property_name
        self.color_picker = color_picker

        self.setText('Select color')

        self.app_state.signal_for(property_name).connect(self._update_button_color)
        self._update_button_color(getattr(self.app_state, property_name))

        def show_picker():
            self.color_picker.show(property_name)

        self.clicked.connect(show_picker)

    def _update_button_color(self, color):
        self.setStyleSheet(
            f'background: rgba({",".join(map(str, (np.array(color) * 255).astype(np.int32).tolist()))}, 1.0)')
