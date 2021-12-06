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

from HyperStackView.color_button import ColorButton
from ._abstract import ConfigWidgetTab
from HyperStackView.sliders import *


class TabProcessing(ConfigWidgetTab):
    def __init__(self, *args, **kwargs):
        ConfigWidgetTab.__init__(self, title='Processing', *args, **kwargs)

        for output_id, output_name in [
            ('max', '&Maximum value'),
            ('avg', '&Average value'),
        ]:
            def update_checkbox_handler(checkbox):
                def slot(status):
                    checkbox.setChecked(status)

                return slot

            output_checkbox = QCheckBox()
            output_checkbox.setText(f'“{output_name}” output')
            self.layout.addRow(output_checkbox)
            self.app_state.signal_for(f'{output_id}_enabled').connect(update_checkbox_handler(output_checkbox))
            output_checkbox.toggled.connect(self.app_state.setter_for(f'{output_id}_enabled'))
            output_checkbox.setChecked(getattr(self.app_state, f'{output_id}_enabled'))

            label = QLabel('Color')
            color_button = ColorButton(self.app_state, self.app.color_picker, f'{output_id}_color')
            self.layout.addRow(label, color_button)

            brightness_slider = SliderWithNumber(
                min_value=-1,
                max_value=1,
                slider_step=.01,
                spin_box_step=.01,
                app_state=self.app_state,
                app_state_param=f'{output_id}_brightness'
            )
            self.layout.addRow('Brightness', brightness_slider)

            contrast_slider = SliderWithNumber(
                min_value=0,
                max_value=10,
                slider_step=.01,
                spin_box_step=.01,
                app_state=self.app_state,
                app_state_param=f'{output_id}_contrast'
            )
            self.layout.addRow('Contrast', contrast_slider)

            gamma_slider = SliderWithNumber(
                min_value=0,
                max_value=10,
                slider_step=.01,
                spin_box_step=.01,
                app_state=self.app_state,
                app_state_param=f'{output_id}_gamma'
            )
            self.layout.addRow('Gamma', gamma_slider)

        self._init_binary_ui()

        self.refresh_ui()

    def _init_binary_ui(self):
        def update_checkbox_handler(checkbox):
            def slot(status):
                checkbox.setChecked(status)

            return slot

        output_checkbox = QCheckBox()
        output_checkbox.setText('“Shaded binary” output')
        self.layout.addRow(output_checkbox)
        self.app_state.signal_for('binary_enabled').connect(update_checkbox_handler(output_checkbox))
        output_checkbox.toggled.connect(self.app_state.setter_for('binary_enabled'))
        output_checkbox.setChecked(getattr(self.app_state, 'binary_enabled'))

        label = QLabel('Object')
        object_color_button = ColorButton(self.app_state, self.app.color_picker, 'binary_object_color')
        self.layout.addRow(label, object_color_button)

        sample_size_slider = SliderWithNumber(
            min_value=.01,
            max_value=.2,
            slider_step=.01,
            spin_box_step=.01,
            app_state=self.app_state,
            app_state_param='binary_sample_size'
        )
        self.layout.addRow('Sample size', sample_size_slider)

        contrast_slider = SliderWithNumber(
            min_value=0,
            max_value=1,
            slider_step=.02,
            spin_box_step=.01,
            app_state=self.app_state,
            app_state_param='binary_contrast'
        )
        self.layout.addRow('Contrast', contrast_slider)

        smoothness_slider = SliderWithNumber(
            min_value=.001,
            max_value=.02,
            slider_step=.001,
            spin_box_step=.001,
            decimals=3,
            app_state=self.app_state,
            app_state_param='binary_smoothness'
        )
        self.layout.addRow('Smoothness', smoothness_slider)
