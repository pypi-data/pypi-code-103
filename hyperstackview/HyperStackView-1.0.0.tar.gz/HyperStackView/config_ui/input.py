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

from ._abstract import ConfigWidgetTab
from HyperStackView.sliders import *


class TabInput(ConfigWidgetTab):
    def __init__(self, *args, **kwargs):
        ConfigWidgetTab.__init__(self, title='Input', *args, **kwargs)

        label = QLabel('Input range min')
        slider = SliderWithNumber(
            min_value=0,
            max_value=65535,
            slider_step=1,
            spin_box_step=1,
            decimals=0,
            app_state=self.app_state,
            app_state_param='input_min',
        )
        self.layout.addRow(label, slider)

        label = QLabel('Input range max')
        slider = SliderWithNumber(
            min_value=0,
            max_value=65535,
            slider_step=1,
            spin_box_step=1,
            decimals=0,
            app_state=self.app_state,
            app_state_param='input_max',
        )
        self.layout.addRow(label, slider)

        auto_button = QPushButton('Set range &automatically')
        auto_button.clicked.connect(self.auto_range)
        self.layout.addRow(auto_button)

        self.refresh_ui()

    def auto_range(self):
        if self.app_state.base_img is not None and self.app_state.base_img.current_frame is not None:
            min = self.app_state.base_img.current_frame.min()
            max = self.app_state.base_img.current_frame.max()

            self.app_state.input_min = int(min)
            self.app_state.input_max = int(max)