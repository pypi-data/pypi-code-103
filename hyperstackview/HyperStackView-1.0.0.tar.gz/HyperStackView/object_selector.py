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

import re

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

from .color_button import ColorButton


class ObjectSelectorWindow(QDialog):
    def __init__(self, app, app_state, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.app = app
        self.app_state = app_state

        self.layout = QGridLayout()
        self.setLayout(self.layout)

        self.setWindowTitle('Object selector')
        self.setWindowFlags(Qt.WindowStaysOnTopHint)

        self.clipboard = app.clipboard()
        self.clipboard.changed.connect(self._clipboard_changed)

        def bind_checkbox_to_app_state(checkbox, property_name):
            checkbox.clicked.connect(self.app_state.setter_for(property_name))
            self.app_state.signal_for(property_name).connect(checkbox.setChecked)
            checkbox.setChecked(getattr(self.app_state, property_name))

        def bind_radio_to_app_state(checkbox, property_name, radio_value):
            def update_state(checked):
                if checked:
                    setattr(self.app_state, property_name, radio_value)

            checkbox.toggled.connect(update_state)
            self.app_state.signal_for(property_name).connect(lambda value: checkbox.setChecked(value == radio_value))
            checkbox.setChecked(getattr(self.app_state, property_name) == radio_value)

        self.main_section_layout = QGridLayout()
        self.layout.addLayout(self.main_section_layout, 0, 0)
        self.layout.setAlignment(self.main_section_layout, Qt.AlignTop | Qt.AlignJustify)

        self.filter_objects_checkbox = QCheckBox()
        self.filter_objects_checkbox.setText('&Enable object filter')
        bind_checkbox_to_app_state(self.filter_objects_checkbox, 'mask_enabled')
        self.main_section_layout.addWidget(self.filter_objects_checkbox, 0, 0, 1, 2)

        self.object_id_label = QLabel('Current object ID:')
        self.main_section_layout.addWidget(self.object_id_label, 1, 0)

        self.object_id_spin_box = QSpinBox()
        self.main_section_layout.addWidget(self.object_id_spin_box, 1, 1)
        self.object_id_spin_box.valueChanged.connect(self.app_state.setter_for('mask_object'))
        self.app_state.signal_for('mask_object').connect(self.object_id_spin_box.setValue)
        self.object_id_spin_box.setRange(0, 32767)

        self.use_clipboard_checkbox = QCheckBox('Synchronize with clipboard')
        self.main_section_layout.addWidget(self.use_clipboard_checkbox, 2, 0, 1, 2)

        self.mode_group_box = QGroupBox('Object filter mode')
        self.mode_group_box_layout = QVBoxLayout()
        self.mode_group_box.setLayout(self.mode_group_box_layout)
        self.layout.addWidget(self.mode_group_box, 0, 1)
        self.layout.setAlignment(self.mode_group_box, Qt.AlignTop | Qt.AlignJustify)

        self.mode_filter_radio = QRadioButton('&Filter by object ID')
        self.mode_group_box_layout.addWidget(self.mode_filter_radio)
        bind_radio_to_app_state(self.mode_filter_radio, 'mask_mode', 'filter')

        self.mode_highlight_radio = QRadioButton('&Highlight object')
        self.mode_group_box_layout.addWidget(self.mode_highlight_radio)
        bind_radio_to_app_state(self.mode_highlight_radio, 'mask_mode', 'highlight')

        self.highlight_settings_layout = QVBoxLayout()
        self.highlight_settings_layout.setContentsMargins(16, 0, 0, 0)
        self.mode_group_box_layout.addLayout(self.highlight_settings_layout)

        self.blink_checkbox = QCheckBox('&Blink')
        self.highlight_settings_layout.addWidget(self.blink_checkbox)
        self.app_state.signal_for('mask_mode').connect(
            lambda value: self.blink_checkbox.setEnabled(value == 'highlight'))
        self.blink_checkbox.setEnabled(self.app_state.mask_mode == 'highlight')
        bind_checkbox_to_app_state(self.blink_checkbox, 'mask_highlight_blink')

        self.highlight_color_button = ColorButton(self.app_state, self.app.color_picker, 'mask_highlight_color')
        self.highlight_settings_layout.addWidget(self.highlight_color_button)
        self.app_state.signal_for('mask_mode').connect(
            lambda value: self.highlight_color_button.setEnabled(value == 'highlight'))
        self.highlight_color_button.setEnabled(self.app_state.mask_mode == 'highlight')

    def _clipboard_changed(self, mode):
        if self.use_clipboard_checkbox.isChecked():
            text = self.clipboard.text(mode)
            if re.match('^\s*[0-9]+\s*$', text) is not None:
                self.app_state.mask_object = int(text)
