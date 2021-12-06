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

from ._abstract import ConfigWidgetTab
from HyperStackView.sliders import *


class TabAnimation(ConfigWidgetTab):
    def __init__(self, *args, **kwargs):
        ConfigWidgetTab.__init__(self, title='Animation', *args, **kwargs)

        label = QLabel('Rotation speed')
        layout = QVBoxLayout()

        slider = AnimationAngularSpeedSlider(
            axis=0,
            min_value=-30,
            max_value=30,
            app_state=self.app_state,
            app_state_param='animation_step',
            reset_button_text='Stop',
            suffix='°/fr'
        )
        layout.addWidget(slider)

        slider = AnimationAngularSpeedSlider(
            axis=1,
            min_value=-30,
            max_value=30,
            app_state=self.app_state,
            app_state_param='animation_step',
            reset_button_text='Stop',
            suffix='°/fr'
        )
        layout.addWidget(slider)

        slider = AnimationAngularSpeedSlider(
            axis=2,
            min_value=-30,
            max_value=30,
            app_state=self.app_state,
            app_state_param='animation_step',
            reset_button_text='Stop',
            suffix='°/fr'
        )
        layout.addWidget(slider)

        self.layout.addRow(label, layout)

        label = QLabel('Time increment')
        slider = AnimationTimeSpeedSlider(
            min_value=-8,
            max_value=8,
            decimals=0,
            slider_step=1,
            spin_box_step=1,
            app_state=self.app_state,
            app_state_param='animation_step',
            reset_button_text='Stop',
        )
        self.layout.addRow(label, slider)

        label = QLabel('Frame duration')
        slider = SliderWithNumber(
            min_value=0,
            max_value=2500,
            decimals=0,
            slider_step=1,
            spin_box_step=1,
            suffix=' ms',
            app_state=self.app_state,
            app_state_param='animation_interval',
        )
        self.layout.addRow(label, slider)

        def update_animate_button_icon():
            animate_button.setIcon(QIcon.fromTheme(
                'media-playback-start' if not animate_button.isChecked() else 'media-playback-stop'
            ))

        animate_button = QToolButton()
        self.layout.addRow(animate_button)
        animate_button.setText('Animate')
        animate_button.setCheckable(True)
        self.app_state.signal_for('animation_running').connect(lambda status: animate_button.setChecked(status))
        animate_button.toggled.connect(self.app_state.setter_for('animation_running'))
        animate_button.toggled.connect(update_animate_button_icon)
        animate_button.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        update_animate_button_icon()

        self.refresh_ui()
