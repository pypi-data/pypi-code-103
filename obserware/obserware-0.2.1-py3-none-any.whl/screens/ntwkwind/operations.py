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


from PyQt5 import QtGui
from PyQt5.QtCore import QThread
from PyQt5.QtWidgets import *

from obserware import __version__
from obserware.screens.ntwkwind.interface import Ui_ntwkwind
from obserware.screens.ntwkwind.worker import (GlobalNetworkRateWorker,
                                               PerNICThreadedStatisticsWorker,
                                               Worker)


class NtwkWind(QDialog, Ui_ntwkwind):
    def __init__(self, parent=None):
        super(NtwkWind, self).__init__(parent)
        self.title = "Network Statistics - Obserware v%s" % __version__
        self.setupUi(self)
        self.setWindowTitle(self.title)
        self.genw, self.gnrw, self.ptsw = (
            Worker(),
            GlobalNetworkRateWorker(),
            PerNICThreadedStatisticsWorker(),
        )
        self.genwthrd, self.gnrwthrd, self.ptswthrd = QThread(), QThread(), QThread()
        self.ntwktree.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.ntwktree.verticalHeader().setDefaultSectionSize(20)
        self.handle_elements()

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        self.genwthrd.destroyed.connect(self.hide)
        self.gnrwthrd.destroyed.connect(self.hide)
        self.ptswthrd.destroyed.connect(self.hide)

    def handle_elements(self):
        self.prepare_threaded_worker()

    def prepare_threaded_worker(self):
        self.genw.thrdstat.connect(self.place_threaded_statistics_on_screen)
        self.gnrw.thrdstat.connect(self.place_global_network_rate_on_screen)
        self.ptsw.thrdstat.connect(self.place_pernic_threaded_statistics_on_screen)
        self.genw.moveToThread(self.genwthrd)
        self.gnrw.moveToThread(self.gnrwthrd)
        self.ptsw.moveToThread(self.ptswthrd)
        self.genwthrd.started.connect(self.genw.threaded_statistics_emitter)
        self.gnrwthrd.started.connect(self.gnrw.threaded_statistics_emitter)
        self.ptswthrd.started.connect(self.ptsw.threaded_statistics_emitter)
        self.genwthrd.start()
        self.gnrwthrd.start()
        self.ptswthrd.start()

    def place_threaded_statistics_on_screen(self, statdict):
        self.nwbtrxnm.setText(str(statdict["provider"]["secodata"]["bytes_recv"]))
        self.nwbttxnm.setText(str(statdict["provider"]["secodata"]["bytes_sent"]))
        self.nwpkrxnm.setText(str(statdict["provider"]["secodata"]["packets_recv"]))
        self.nwpktxnm.setText(str(statdict["provider"]["secodata"]["packets_sent"]))
        self.nwerrxnm.setText(str(statdict["provider"]["secodata"]["errin"]))
        self.nwertxnm.setText(str(statdict["provider"]["secodata"]["errout"]))
        self.nwdprxnm.setText(str(statdict["provider"]["secodata"]["dropin"]))
        self.nwdptxnm.setText(str(statdict["provider"]["secodata"]["dropout"]))

    def place_global_network_rate_on_screen(self, statdict):
        self.nwrxkbnm.setText(
            "%.2f" % statdict["provider"]["globrate"]["rate_bytes_recv"]
        )
        self.nwtxkbnm.setText(
            "%.2f" % statdict["provider"]["globrate"]["rate_bytes_sent"]
        )
        self.nwrxpknm.setText(
            str(statdict["provider"]["globrate"]["rate_packets_recv"])
        )
        self.nwtxpknm.setText(
            str(statdict["provider"]["globrate"]["rate_packets_sent"])
        )

    def place_pernic_threaded_statistics_on_screen(self, statdict):
        self.ntwkqant.setText("%d NIC(s)" % statdict["provider"]["niccount"])
        self.ntwktree.setRowCount(0)
        self.ntwktree.insertRow(0)
        for row, form in enumerate(statdict["provider"]["tertdata"]):
            for column, item in enumerate(form):
                self.ntwktree.setItem(row, column, QTableWidgetItem(str(item)))
            self.ntwktree.insertRow(self.ntwktree.rowCount())
        self.ntwktree.setRowCount(self.ntwktree.rowCount() - 1)
