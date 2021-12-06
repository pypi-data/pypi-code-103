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

from PySide6.QtGui import *
from PySide6.QtWidgets import *

from HyperStackView.paths import data_dir
from HyperStackView.sliders import *
from ._abstract import ConfigWidgetTab


class TabView(ConfigWidgetTab):
    def __init__(self, *args, **kwargs):
        ConfigWidgetTab.__init__(self, title='View', *args, **kwargs)

        label = QLabel('View type')
        layout = QVBoxLayout()

        def set_projection_type(proj_type):
            self.app_state.projection_type = proj_type
            self.refresh_ui()

        self.radio_projection = QRadioButton('3D &Projection')
        self.radio_projection.toggled.connect(lambda checked: checked and set_projection_type('3d'))
        layout.addWidget(self.radio_projection)
        self.radio_slice = QRadioButton('Single-&slice view')
        self.radio_slice.toggled.connect(lambda checked: checked and set_projection_type('slice'))
        layout.addWidget(self.radio_slice)
        self.layout.addRow(label, layout)

        label = QLabel('Near plane position')
        slider = SliderWithNumber(
            min_value=-1,
            max_value=2,
            app_state=self.app_state,
            app_state_param='near_plane_screen_z'
        )
        self.layout.addRow(label, slider)

        label = QLabel('Far plane position')
        slider = SliderWithNumber(
            min_value=-1,
            max_value=2,
            app_state=self.app_state,
            app_state_param='far_plane_screen_z'
        )
        self.layout.addRow(label, slider)

        label = QLabel('Perspective')
        slider = SliderWithNumber(
            min_value=0,
            max_value=2,
            app_state=self.app_state,
            app_state_param='perspective'
        )
        self.layout.addRow(label, slider)

        label = QLabel('Z-axis sample count')
        slider = SliderWithNumber(
            min_value=1,
            max_value=1000,
            decimals=0,
            app_state=self.app_state,
            slider_step=1,
            spin_box_step=1,
            app_state_param='z_samples'
        )
        self.layout.addRow(label, slider)

        label = QCheckBox('Background grid')
        slider = SliderWithNumber(
            min_value=0,
            max_value=1,
            app_state=self.app_state,
            slider_step=.01,
            spin_box_step=.01,
            app_state_param='grid_alpha'
        )
        self.layout.addRow(label, slider)
        self.app_state.connect_checkbox('show_grid', label)

        label = QCheckBox('Cube backdrop')
        slider = SliderWithNumber(
            min_value=0,
            max_value=1,
            app_state=self.app_state,
            slider_step=.01,
            spin_box_step=.01,
            app_state_param='bg_cube_alpha'
        )
        self.layout.addRow(label, slider)
        self.app_state.connect_checkbox('show_bg_cube', label)

        label = QLabel()
        label.setPixmap(QPixmap(str(data_dir / 'near_far.png')))
        self.layout.addRow(label)

        self.refresh_ui()

    def refresh_ui(self):
        super().refresh_ui()

        self.radio_projection.setChecked(self.app_state.projection_type == '3d')
        self.radio_slice.setChecked(self.app_state.projection_type == 'slice')
