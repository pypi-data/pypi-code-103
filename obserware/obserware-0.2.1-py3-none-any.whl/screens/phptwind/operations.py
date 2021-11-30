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
from obserware.screens.phptwind.interface import Ui_phptwind
from obserware.screens.phptwind.worker import Worker


class PhPtWind(QDialog, Ui_phptwind):
    def __init__(self, parent=None):
        super(PhPtWind, self).__init__(parent)
        self.title = "Physical Partitions - Obserware v%s" % __version__
        self.setupUi(self)
        self.setWindowTitle(self.title)
        self.obj = Worker()
        self.thread = QThread()
        self.phpttree.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.phpttree.setColumnWidth(0, 125)
        self.phpttree.horizontalHeader().setSectionResizeMode(
            1, QtWidgets.QHeaderView.Stretch
        )
        self.phpttree.setColumnWidth(2, 150)
        self.phpttree.setColumnWidth(3, 75)
        self.phpttree.setColumnWidth(4, 75)
        self.phpttree.verticalHeader().setDefaultSectionSize(20)
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
        self.phptqant.setText("%d unit(s)" % statdict["provider"]["partqant"])
        self.phpttree.setRowCount(0)
        self.phpttree.insertRow(0)
        for row, form in enumerate(statdict["provider"]["partlist"]):
            for column, item in enumerate(form):
                self.phpttree.setItem(row, column, QTableWidgetItem(str(item)))
            self.phpttree.insertRow(self.phpttree.rowCount())
        self.phpttree.setRowCount(self.phpttree.rowCount() - 1)
