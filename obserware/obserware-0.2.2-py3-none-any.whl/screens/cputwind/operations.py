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


from PyQt5 import QtGui, QtWidgets
from PyQt5.QtCore import QThread
from PyQt5.QtWidgets import *

from obserware import __version__
from obserware.screens.cputwind.interface import Ui_cputwind
from obserware.screens.cputwind.worker import Worker


class CPUTWind(QDialog, Ui_cputwind):
    def __init__(self, parent=None):
        super(CPUTWind, self).__init__(parent)
        self.title = "CPU Times - Obserware v%s" % __version__
        self.setupUi(self)
        self.setWindowTitle(self.title)
        self.obj = Worker()
        self.thread = QThread()
        self.cputtree.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.cputtree.verticalHeader().setVisible(False)
        self.cputtree.horizontalHeader().setSectionResizeMode(
            0, QtWidgets.QHeaderView.Stretch
        )
        self.cputtree.setColumnWidth(1, 55)
        self.cputtree.setColumnWidth(2, 55)
        self.cputtree.setColumnWidth(3, 55)
        self.cputtree.setColumnWidth(4, 55)
        self.cputtree.setColumnWidth(5, 55)
        self.cputtree.setColumnWidth(6, 55)
        self.cputtree.setColumnWidth(7, 55)
        self.cputtree.setColumnWidth(8, 55)
        self.cputtree.setColumnWidth(9, 55)
        self.cputtree.setColumnWidth(10, 55)
        self.cputtree.verticalHeader().setDefaultSectionSize(20)
        self.handle_elements()

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        self.thread.destroyed.connect(self.hide)

    def handle_elements(self):
        self.prepare_threaded_worker()

    def prepare_threaded_worker(self):
        self.obj.thrdstat.connect(self.place_threaded_statistics_on_screen)
        self.obj.moveToThread(self.thread)
        self.thread.started.connect(self.obj.threaded_statistics_emitter)
        self.thread.start()

    def place_threaded_statistics_on_screen(self, statdict):
        # Refresh process table on the processes tab screen
        self.cputqant.setText("%d CPU(s)" % statdict["provider"]["cpucount"])
        self.cputtree.setRowCount(0)
        self.cputtree.insertRow(0)
        for row, form in enumerate(statdict["provider"]["timelist"]):
            for column, item in enumerate(form):
                self.cputtree.setItem(row, column, QTableWidgetItem(str(item)))
            self.cputtree.insertRow(self.cputtree.rowCount())
        self.cputtree.setRowCount(self.cputtree.rowCount() - 1)
