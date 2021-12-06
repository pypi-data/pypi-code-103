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


class TabPosition(ConfigWidgetTab):
    def __init__(self, *args, **kwargs):
        ConfigWidgetTab.__init__(self, title='Position', *args, **kwargs)

        label = QLabel('Rotation')
        layout = QHBoxLayout()

        slider = RotationSliderWithNumber(
            axis=0,
            min_value=-180,
            max_value=179,
            app_state=self.app_state,
            app_state_param='rotation',
            layout_direction=QBoxLayout.Direction.TopToBottom
        )
        layout.addWidget(slider)

        slider = RotationSliderWithNumber(
            axis=1,
            min_value=-180,
            max_value=179,
            app_state=self.app_state,
            app_state_param='rotation',
            layout_direction=QBoxLayout.Direction.TopToBottom
        )
        layout.addWidget(slider)

        slider = RotationSliderWithNumber(
            axis=2,
            min_value=-180,
            max_value=179,
            app_state=self.app_state,
            app_state_param='rotation',
            layout_direction=QBoxLayout.Direction.TopToBottom
        )
        layout.addWidget(slider)

        self.layout.addRow(label, layout)

        label = QLabel('Scale')
        slider = SliderWithNumber(
            min_value=.01,
            max_value=10,
            app_state=self.app_state,
            app_state_param='scale'
        )
        self.layout.addRow(label, slider)

        self.refresh_ui()
