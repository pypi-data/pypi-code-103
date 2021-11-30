"""
Obserware
Copyright (C) 2021 Akashdeep Dhar

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""


import sys

from PyQt5.QtGui import QFontDatabase
from PyQt5.QtWidgets import QApplication

from obserware.commons import resources
from obserware.screens.mainwind.operations import MainWind


def populate_font_database():
    fontlist = [
        ":/fontrsrc/fonts/intr-bold.ttf",
        ":/fontrsrc/fonts/intr-rlar.ttf",
        ":/fontrsrc/fonts/mono-rlar.ttf",
    ]
    for indx in fontlist:
        QFontDatabase.addApplicationFont(indx)


def main():
    app = QApplication(sys.argv)
    populate_font_database()
    window = MainWind()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
