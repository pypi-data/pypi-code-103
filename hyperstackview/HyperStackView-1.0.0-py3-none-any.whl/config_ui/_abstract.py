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


class ConfigWidgetTab(QScrollArea):
    def __init__(self, window, title):
        QScrollArea.__init__(self)

        self.window = window
        self.app = window.app
        self.app_state = window.app_state

        self.title = title

        self.scrolled_widget = QWidget()
        self.layout = self._create_layout()
        self.scrolled_widget.setLayout(self.layout)
        self.setWidgetResizable(True)
        self.setWidget(self.scrolled_widget)

    def _create_layout(self):
        return QFormLayout()

    def refresh_ui(self):
        pass
