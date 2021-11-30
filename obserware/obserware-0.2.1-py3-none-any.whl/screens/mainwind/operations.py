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

from PyQt5 import QtGui, QtWidgets
from PyQt5.QtChart import QChart, QPieSeries
from PyQt5.QtCore import QThread
from PyQt5.QtGui import QPainter
from PyQt5.QtWidgets import *

from obserware import __version__
from obserware.readers.mainwind.tab_information import (
    return_cpu_specifications_information, return_feature_flags_information,
    return_obserware_information, return_software_information)
from obserware.readers.mainwind.tab_performance import \
    return_bottombar_onetimed_statistics
from obserware.screens.cputwind.operations import CPUTWind
from obserware.screens.lgptwind.operations import LgPtWind
from obserware.screens.mainwind.interface import Ui_mainwind
from obserware.screens.mainwind.worker import Worker
from obserware.screens.ntwkwind.operations import NtwkWind
from obserware.screens.phptwind.operations import PhPtWind
from obserware.screens.procwind.operations import ProcWind
from obserware.screens.sostwind.operations import SoStWind


class MainWind(QMainWindow, Ui_mainwind):
    def __init__(self):
        QMainWindow.__init__(self)
        self.title = "Obserware v%s" % __version__
        self.setupUi(self)
        self.setWindowTitle(self.title)
        self.cputwind = CPUTWind(parent=self)
        self.sostwind = SoStWind(parent=self)
        self.phptwind = PhPtWind(parent=self)
        self.lgptwind = LgPtWind(parent=self)
        self.ntwkwind = NtwkWind(parent=self)
        self.obj = Worker()
        self.thread = QThread()
        self.cpud_time_series = QPieSeries()
        self.cpud_donut_chart = QChart()
        self.memo_time_series = QPieSeries()
        self.memo_donut_chart = QChart()
        self.swap_time_series = QPieSeries()
        self.swap_donut_chart = QChart()
        self.handle_elements()

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        self.thread.destroyed.connect(sys.exit())

    def handle_elements(self):
        self.cpudtmbt.clicked.connect(self.cputwind.exec)
        self.mmscexbt.clicked.connect(self.sostwind.exec)
        self.swphexbt.clicked.connect(self.phptwind.exec)
        self.swlgexbt.clicked.connect(self.lgptwind.exec)
        self.mmnsexbt.clicked.connect(self.ntwkwind.exec)
        self.proctree.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.proctree.verticalHeader().setVisible(False)
        self.proctree.setColumnWidth(0, 75)
        self.proctree.horizontalHeader().setSectionResizeMode(
            1, QtWidgets.QHeaderView.Stretch
        )
        self.proctree.setColumnWidth(2, 75)
        self.proctree.setColumnWidth(3, 125)
        self.proctree.setColumnWidth(4, 75)
        self.proctree.setColumnWidth(5, 75)
        self.proctree.setColumnWidth(6, 75)
        self.proctree.setColumnWidth(7, 75)
        self.proctree.verticalHeader().setDefaultSectionSize(20)
        self.cntbvers.setText("Version %s" % __version__)
        self.proctree.cellClicked.connect(self.open_process_window)
        self.place_elements_on_information_tab_screen()
        self.prepare_threaded_worker()
        self.prepare_bottombar_contents()
        self.prepare_performance_donut_charts()

    def prepare_threaded_worker(self):
        self.obj.thrdstat.connect(self.place_threaded_statistics_on_screen)
        self.obj.moveToThread(self.thread)
        self.thread.started.connect(self.obj.threaded_statistics_emitter)
        self.thread.start()

    def prepare_bottombar_contents(self):
        retndata = return_bottombar_onetimed_statistics()
        self.userhost.setText("%s@%s" % (retndata["username"], retndata["hostname"]))
        self.kernvers.setText("%s %s" % (retndata["systname"], retndata["rlsename"]))

    def open_process_window(self, rowe, colm):
        try:
            prociden = self.proctree.item(rowe, 0).text()
            self.procwdis = ProcWind(prociden, parent=self)
            self.procwdis.exec()
        except AttributeError:
            pass

    def prepare_performance_donut_charts(self):
        # Preparing CPU graph
        self.cpud_time_series.setHoleSize(0.60)
        cpud_free_slice = self.cpud_time_series.append("Free", 0.0)
        cpud_free_slice.setBrush(QtGui.QColor("#b2d8d8"))
        cpud_used_slice = self.cpud_time_series.append("Used", 0.0)
        cpud_used_slice.setBrush(QtGui.QColor("#008080"))
        self.cpud_donut_chart.legend().hide()
        self.cpud_donut_chart.addSeries(self.cpud_time_series)
        self.cpud_donut_chart.setAnimationOptions(QChart.SeriesAnimations)
        self.cpud_donut_chart.setContentsMargins(-50, -50, -50, -50)
        self.cpudgfvw.setChart(self.cpud_donut_chart)
        self.cpudgfvw.setRenderHint(QPainter.Antialiasing)
        # Preparing Memory graph
        self.memo_time_series.setHoleSize(0.60)
        memo_free_slice = self.memo_time_series.append("Free", 0.0)
        memo_free_slice.setBrush(QtGui.QColor("#b2d8d8"))
        memo_cach_slice = self.memo_time_series.append("Cached", 0.0)
        memo_cach_slice.setBrush(QtGui.QColor("#66b3b3"))
        memo_used_slice = self.memo_time_series.append("Used", 0.0)
        memo_used_slice.setBrush(QtGui.QColor("#008080"))
        self.memo_time_series.append("Free", 0.0)
        self.memo_time_series.append("Used", 0.0)
        self.memo_donut_chart.legend().hide()
        self.memo_donut_chart.addSeries(self.memo_time_series)
        self.memo_donut_chart.setAnimationOptions(QChart.SeriesAnimations)
        self.memo_donut_chart.setContentsMargins(-50, -50, -50, -50)
        self.memogfvw.setChart(self.memo_donut_chart)
        self.memogfvw.setRenderHint(QPainter.Antialiasing)
        # Preparing Swap graph
        self.swap_time_series.setHoleSize(0.60)
        swap_free_slice = self.swap_time_series.append("Free", 0.0)
        swap_free_slice.setBrush(QtGui.QColor("#b2d8d8"))
        swap_used_slice = self.swap_time_series.append("Used", 0.0)
        swap_used_slice.setBrush(QtGui.QColor("#008080"))
        self.swap_time_series.append("Free", 0.0)
        self.swap_time_series.append("Used", 0.0)
        self.swap_donut_chart.legend().hide()
        self.swap_donut_chart.addSeries(self.swap_time_series)
        self.swap_donut_chart.setAnimationOptions(QChart.SeriesAnimations)
        self.swap_donut_chart.setContentsMargins(-50, -50, -50, -50)
        self.swapgfvw.setChart(self.swap_donut_chart)
        self.swapgfvw.setRenderHint(QPainter.Antialiasing)

    def place_threaded_statistics_on_screen(self, statdict):
        # Refresh bottombar statistics
        self.cpudperc.setText(str(statdict["bottomstat"]["cpud_percent"]))
        self.memoperc.setText(str(statdict["bottomstat"]["memo_percent"]))
        self.swapperc.setText(str(statdict["bottomstat"]["swap_percent"]))
        self.diskperc.setText(str(statdict["bottomstat"]["disk_percent"]))
        # Refresh statistics on graph slices
        self.cpud_time_series.slices()[0].setValue(
            100 - statdict["bottomstat"]["cpud_percent"]
        )
        self.cpud_time_series.slices()[1].setValue(
            statdict["bottomstat"]["cpud_percent"]
        )
        self.memo_time_series.slices()[0].setValue(
            statdict["perfscreen"]["memo"]["percentage"]["free"]
        )
        self.memo_time_series.slices()[1].setValue(
            statdict["perfscreen"]["memo"]["percentage"]["cached"]
        )
        self.memo_time_series.slices()[2].setValue(
            statdict["perfscreen"]["memo"]["percentage"]["used"]
        )
        self.swap_time_series.slices()[0].setValue(
            statdict["perfscreen"]["swap"]["percentage"]["free"]
        )
        self.swap_time_series.slices()[1].setValue(
            statdict["perfscreen"]["swap"]["percentage"]["used"]
        )
        # Refresh textual statistics on the performance tab screen - Memory
        self.memouspc.setText(
            "%2.1f%%" % statdict["perfscreen"]["memo"]["percentage"]["used"]
        )
        self.memoccpc.setText(
            "%2.1f%%" % statdict["perfscreen"]["memo"]["percentage"]["cached"]
        )
        self.memofrpc.setText(
            "%2.1f%%" % statdict["perfscreen"]["memo"]["percentage"]["free"]
        )
        self.memousnm.setText(
            "%sMB" % str(statdict["perfscreen"]["memo"]["absolute"]["used"])
        )
        self.memoccnm.setText(
            "%sMB" % str(statdict["perfscreen"]["memo"]["absolute"]["cached"])
        )
        self.memofrnm.setText(
            "%sMB" % str(statdict["perfscreen"]["memo"]["absolute"]["free"])
        )
        self.memottnm.setText(
            "%sMB" % str(statdict["perfscreen"]["memo"]["absolute"]["total"])
        )
        self.memoacnm.setText(
            "%sMB" % str(statdict["perfscreen"]["memo"]["absolute"]["active"])
        )
        self.memobfnm.setText(
            "%sMB" % str(statdict["perfscreen"]["memo"]["absolute"]["buffers"])
        )
        self.memoshnm.setText(
            "%sMB" % str(statdict["perfscreen"]["memo"]["absolute"]["shared"])
        )
        self.memosbnm.setText(
            "%sMB" % str(statdict["perfscreen"]["memo"]["absolute"]["slab"])
        )
        # Refresh textual statistics on the performance tab screen - Swap
        self.swapuspc.setText(
            "%2.1f%%" % statdict["perfscreen"]["swap"]["percentage"]["used"]
        )
        self.swapfrpc.setText(
            "%2.1f%%" % statdict["perfscreen"]["swap"]["percentage"]["free"]
        )
        self.swapusnm.setText(
            "%sMB" % str(statdict["perfscreen"]["swap"]["absolute"]["used"])
        )
        self.swapfrnm.setText(
            "%sMB" % str(statdict["perfscreen"]["swap"]["absolute"]["free"])
        )
        self.swapttnm.setText(
            "%sMB" % str(statdict["perfscreen"]["swap"]["absolute"]["total"])
        )
        self.swapsinm.setText(
            "%sMB" % str(statdict["perfscreen"]["swap"]["absolute"]["sin"])
        )
        self.swapsonm.setText(
            "%sMB" % str(statdict["perfscreen"]["swap"]["absolute"]["sout"])
        )
        # Refresh textual statistics on the performance tab screen - CPU
        self.cpudcsnm.setText(
            str(statdict["perfscreen"]["cpud"]["absolute"]["ctx_switches"])
        )
        self.cpudinnm.setText(
            str(statdict["perfscreen"]["cpud"]["absolute"]["interrupts"])
        )
        self.cpudsinm.setText(
            str(statdict["perfscreen"]["cpud"]["absolute"]["soft_interrupts"])
        )
        self.cpudscnm.setText(
            str(statdict["perfscreen"]["cpud"]["absolute"]["sys_calls"])
        )
        # Refresh process table on the processes tab screen
        self.procqant.setText("%d processes" % statdict["procscreen"]["process_count"])
        self.proctree.setRowCount(0)
        self.proctree.insertRow(0)
        for row, form in enumerate(statdict["procscreen"]["process_list"]):
            for column, item in enumerate(form):
                self.proctree.setItem(row, column, QTableWidgetItem(str(item)))
            self.proctree.insertRow(self.proctree.rowCount())
        self.proctree.setRowCount(self.proctree.rowCount() - 1)

    def place_elements_on_information_tab_screen(self):
        # Return elements
        softdict = return_software_information()
        obsrdict = return_obserware_information()
        cpuidict = return_cpu_specifications_information()
        featlist = return_feature_flags_information()
        # Software - Information tab
        self.softname.setText(str(softdict["name"]))
        self.softvers.setText(str(softdict["version"]))
        self.softhost.setText(str(softdict["hostname"]))
        self.softrlse.setText(str(softdict["release"]))
        self.softrend.setText(str(softdict["rendition"]))
        self.softboot.setText(str(softdict["boottime"]))
        # Obserware - Information tab
        self.obsrvers.setText(str(obsrdict["obsrvers"]))
        self.obsrpyth.setText(str(obsrdict["pythvers"]))
        self.obsrpyqt.setText(str(obsrdict["pyqtvers"]))
        self.obsrpsut.setText(str(obsrdict["psutvers"]))
        self.obsrcpui.setText(str(obsrdict["cpuivers"]))
        self.obsrdist.setText(str(obsrdict["distvers"]))
        # CPU specification - Information tab
        self.cpuiname.setText(str(cpuidict["name"]))
        self.cpuivend.setText(str(cpuidict["vendor"]))
        self.cpuifreq.setText(str(cpuidict["frequency"]))
        self.cpuiqant.setText(str(cpuidict["count"]))
        self.cpuibits.setText(str(cpuidict["bits"]))
        self.cpuiarch.setText(str(cpuidict["arch"]))
        self.cpuistep.setText(str(cpuidict["stepping"]))
        self.cpuimodl.setText(str(cpuidict["model"]))
        self.cpuifmly.setText(str(cpuidict["family"]))
        # Feature flags - Information tab
        for indx in featlist["featflag"]:
            self.fefllist.addItem(indx)
