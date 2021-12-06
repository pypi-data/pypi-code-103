import functools
import logging
import math

import numpy
import pyqtgraph
from PySide2 import QtCore, QtWidgets

import asphodel
import hyperborea.calibration
from hyperborea.unit_formatter_spinbox import UnitFormatterDoubleSpinBox
from hyperborea.unit_selection_dialog import UnitSelectionDialog

from .ui_calibration_panel import Ui_CalibrationPanel
from .ui_calibration_channel import Ui_CalibrationChannel

logger = logging.getLogger(__name__)


class CalibrationChannel(QtWidgets.QWidget, Ui_CalibrationChannel):
    value_changed = QtCore.Signal()

    def __init__(self, calibration_info, capture_func, unit_formatter,
                 parent=None):
        super().__init__(parent)

        self.calibration_info = calibration_info
        self.capture_func = capture_func
        self.parent = parent

        # create unit formatters for the capture side with 0 resolution
        self.rms_formatter = asphodel.nativelib.create_custom_unit_formatter(
            unit_formatter.conversion_scale, 0.0,
            0.0, unit_formatter.unit_ascii, unit_formatter.unit_utf8,
            unit_formatter.unit_html)
        self.dc_formatter = asphodel.nativelib.create_custom_unit_formatter(
            unit_formatter.conversion_scale, unit_formatter.conversion_offset,
            0.0, unit_formatter.unit_ascii, unit_formatter.unit_utf8,
            unit_formatter.unit_html)

        self.unit_info = None
        self.scale_offset = None  # None or (scale, offset)

        self.setupUi(self)
        self.extra_ui_setup()

        # process the current state
        self.cal_type_updated()

    def extra_ui_setup(self):
        self.calibrationEnabled.toggled.connect(self.update_all)

        self.acRadioButton.toggled.connect(self.cal_type_updated)
        self.linearRadioButton.toggled.connect(self.cal_type_updated)
        self.selectUnit.clicked.connect(self.select_unit)

        self.unit.setText("")

        self.acCapture.clicked.connect(self.ac_capture)
        self.linearCapture.clicked.connect(self.linear_capture)

        self.plotButton.clicked.connect(self.plot_linear)
        self.linearTable.itemSelectionChanged.connect(self.selection_changed)

        self.capturedMagnitude.set_unit_formatter(self.rms_formatter)
        self.capturedOffset.set_unit_formatter(self.dc_formatter)

        self.capturedMagnitude.setMinimum(-math.inf)
        self.capturedMagnitude.setMaximum(math.inf)
        self.capturedOffset.setMinimum(-math.inf)
        self.capturedOffset.setMaximum(math.inf)
        self.actualMagnitude.setMinimum(-math.inf)
        self.actualMagnitude.setMaximum(math.inf)
        self.actualOffset.setMinimum(-math.inf)
        self.actualOffset.setMaximum(math.inf)

        self.capturedMagnitude.valueChanged.connect(self.update_scale_offset)
        self.capturedOffset.valueChanged.connect(self.update_scale_offset)
        self.actualMagnitude.valueChanged.connect(self.update_scale_offset)
        self.actualOffset.valueChanged.connect(self.update_scale_offset)

        header = self.linearTable.horizontalHeader()
        header.setResizeMode(0, QtWidgets.QHeaderView.Stretch)
        header.setResizeMode(1, QtWidgets.QHeaderView.Stretch)
        header.setResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)

    def cal_type_updated(self, _junk=None):
        if self.acRadioButton.isChecked():
            self.stackedWidget.setCurrentWidget(self.acPage)
        else:
            self.stackedWidget.setCurrentWidget(self.linearPage)

        self.update_all()

    def select_unit(self):
        dialog = self.parent.unit_selection_dialog
        ret = dialog.exec_()
        if ret == 0:
            return  # user cancelled

        self.unit_info = dialog.get_unit_info()
        unit_formatter = self.unit_info[1]
        self.unit.setText(unit_formatter.unit_utf8)

        rms_formatter = asphodel.nativelib.create_custom_unit_formatter(
            unit_formatter.conversion_scale, 0.0, 0.0,
            unit_formatter.unit_ascii, unit_formatter.unit_utf8,
            unit_formatter.unit_html)

        self.actualMagnitude.set_unit_formatter(rms_formatter)
        self.actualOffset.set_unit_formatter(unit_formatter)

        row_count = self.linearTable.rowCount()
        for row in range(row_count):
            actual = self.linearTable.cellWidget(row, 1)
            actual.set_unit_formatter(unit_formatter)

        self.update_all()

    def update_enabled(self):
        enabled = self.calibrationEnabled.isChecked()

        self.unitLabel.setEnabled(enabled)
        self.unit.setEnabled(enabled)
        self.selectUnit.setEnabled(enabled)

        if enabled:
            unit_ready = self.unit_info is not None
        else:
            unit_ready = False
        self.acRadioButton.setEnabled(unit_ready)
        self.linearRadioButton.setEnabled(unit_ready)
        self.stackedWidget.setEnabled(unit_ready)
        self.scaleLabel.setEnabled(unit_ready)
        self.scale.setEnabled(unit_ready)
        self.offsetLabel.setEnabled(unit_ready)
        self.offset.setEnabled(unit_ready)

    def update_all(self, _junk=None):
        self.update_enabled()
        self.update_scale_offset()

    def get_ac_scale_offset(self):
        try:
            unscaled_captured_mag = (self.capturedMagnitude.value() /
                                     self.calibration_info.scale)
            unscaled_captured_offset = ((self.capturedOffset.value() -
                                         self.calibration_info.offset) /
                                        self.calibration_info.scale)

            scale = self.actualMagnitude.value() / unscaled_captured_mag

            if scale == 0:
                # invalid
                return None

            offset = (self.actualOffset.value() -
                      unscaled_captured_offset * scale)
            return (scale, offset)
        except ZeroDivisionError:
            return None

    def get_linear_scale_offset(self):
        # least squares regression to fit y = m*x + b, where y is the actual
        # values, x is the captured values, m is the scale and b is the offset.
        # numpy.linalg.lstsq requires A matrix to be [[x 1]]
        try:
            row_count = self.linearTable.rowCount()
            if row_count < 2:
                # not enough points
                return None

            y = numpy.zeros(row_count)
            x = numpy.zeros(row_count)

            for row in range(row_count):
                captured = self.linearTable.cellWidget(row, 0)
                actual = self.linearTable.cellWidget(row, 1)

                unscaled = ((captured.value() - self.calibration_info.offset) /
                            self.calibration_info.scale)

                y[row] = actual.value()
                x[row] = unscaled

            A = numpy.vstack([x, numpy.ones(row_count)]).T
            m, b = numpy.linalg.lstsq(A, y, rcond=None)[0]

            if m == 0 or not math.isfinite(m) or not math.isfinite(b):
                # invalid
                return None

            return (m, b)
        except Exception:
            return None

    def update_scale_offset(self, _junk=None):
        if self.unit_info is None:
            self.scale_offset = None
        elif self.acRadioButton.isChecked():
            self.scale_offset = self.get_ac_scale_offset()
        else:
            self.scale_offset = self.get_linear_scale_offset()

        if self.scale_offset is None:
            self.scale.setText("")
            self.offset.setText("")
            self.plotButton.setEnabled(False)
        else:
            scale, offset = self.scale_offset
            self.scale.setText(str(scale))
            self.offset.setText(str(offset))
            self.plotButton.setEnabled(True)

        self.value_changed.emit()

    def is_valid(self):
        if self.unit_info is None:
            return False

        if self.scale_offset is None:
            return False

        return True

    def ac_capture(self):
        mean, std_dev = self.capture_func()
        if math.isfinite(mean) and math.isfinite(std_dev):
            self.capturedMagnitude.setValue(std_dev)
            self.capturedOffset.setValue(mean)
            self.update_scale_offset()

    def linear_capture(self):
        if self.unit_info is None:
            return

        mean, std_dev = self.capture_func()
        if math.isfinite(mean) and math.isfinite(std_dev):
            captured = UnitFormatterDoubleSpinBox(self)
            captured.set_unit_formatter(self.dc_formatter)
            captured.setMinimum(-math.inf)
            captured.setMaximum(math.inf)
            captured.setValue(mean)
            captured.valueChanged.connect(self.update_scale_offset)

            actual = UnitFormatterDoubleSpinBox(self)
            actual.set_unit_formatter(self.unit_info[1])
            actual.setMinimum(-math.inf)
            actual.setMaximum(math.inf)
            actual.setValue(0.0)
            actual.valueChanged.connect(self.update_scale_offset)

            delete = QtWidgets.QPushButton(self.tr("Delete"))
            delete.clicked.connect(functools.partial(self.delete_cb, delete))

            row = self.linearTable.rowCount()
            self.linearTable.insertRow(row)
            self.linearTable.setCellWidget(row, 0, captured)
            self.linearTable.setCellWidget(row, 1, actual)
            self.linearTable.setCellWidget(row, 2, delete)

            # give it focus
            actual.setFocus()
            actual.selectAll()

            self.update_scale_offset()

    def plot_linear(self):
        if self.scale_offset is None or self.unit_info is None:
            return False

        row_count = self.linearTable.rowCount()
        if row_count < 2:
            # not enough points
            return

        y = numpy.zeros(row_count)
        x = numpy.zeros(row_count)

        for row in range(row_count):
            captured = self.linearTable.cellWidget(row, 0)
            actual = self.linearTable.cellWidget(row, 1)

            y[row] = actual.value()
            x[row] = captured.value()

        # apply the unit formatters
        x = ((x * self.dc_formatter.conversion_scale) +
             self.dc_formatter.conversion_offset)
        actual_unit_formatter = self.unit_info[1]
        y = ((y * actual_unit_formatter.conversion_scale) +
             actual_unit_formatter.conversion_offset)

        # do least squares
        A = numpy.vstack([x, numpy.ones(row_count)]).T
        scale, offset = numpy.linalg.lstsq(A, y, rcond=None)[0]

        # create line
        x_linear = numpy.array([x.min(), x.max()])
        y_linear = x_linear * scale + offset

        dialog = QtWidgets.QDialog(self)
        dialog.resize(500, 500)
        layout = QtWidgets.QVBoxLayout(dialog)
        graphics_layout = pyqtgraph.GraphicsLayoutWidget(dialog)
        layout.addWidget(graphics_layout)
        button_box = QtWidgets.QDialogButtonBox(dialog)
        button_box.setOrientation(QtCore.Qt.Horizontal)
        button_box.setStandardButtons(QtWidgets.QDialogButtonBox.Close)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)

        plot = graphics_layout.addPlot(title="Linear Fit")
        plot.plot(x, y, pen=None, symbol='o', symbolBrush=(255, 0, 0),
                  symbolPen='w', name="Data")
        plot.plot(x_linear, y_linear, pen=(0, 0, 255), name="Fit")

        plot.setLabel("left", actual_unit_formatter.unit_html)
        plot.setLabel("bottom", self.dc_formatter.unit_html)

        dialog.exec_()

    def selection_changed(self):
        if self.linearTable.selectionModel().hasSelection():
            self.deleteRow.setEnabled(True)
        else:
            self.deleteRow.setEnabled(False)

    def delete_cb(self, button):
        row_count = self.linearTable.rowCount()
        for row in range(row_count):
            widget = self.linearTable.cellWidget(row, 2)
            if widget == button:
                self.linearTable.removeRow(row)
                self.linearTable.clearSelection()
                self.update_scale_offset()
                return


class CalibrationPanel(QtWidgets.QGroupBox, Ui_CalibrationPanel):
    def __init__(self, device_info, cals, logger, parent=None):
        super().__init__(parent)

        self.device_info = device_info
        self.cals = cals
        self.logger = logger
        self.parent = parent

        self.setupUi(self)
        self.extra_ui_setup()

    def extra_ui_setup(self):
        self.unit_selection_dialog = UnitSelectionDialog()

        self.saveButton = self.buttonBox.button(
            QtWidgets.QDialogButtonBox.Save)
        self.saveButton.setText(self.tr("Write NVM"))
        self.saveButton.clicked.connect(self.save)

        self.channel_widgets = []  # (name, channel_widget)

        for name, calibration_info, capture_func, unit_formatter in self.cals:
            channel_widget = CalibrationChannel(
                calibration_info, capture_func, unit_formatter, parent=self)
            self.channel_widgets.append((name, channel_widget))
            self.setup_channel_signals(channel_widget)

        if len(self.channel_widgets) == 0:
            pass
        elif len(self.channel_widgets) == 1:
            channel_widget = self.channel_widgets[0][1]
            channel_widget.calibrationEnabled.setChecked(True)
            channel_widget.calibrationEnabled.setVisible(False)
            self.verticalLayout.insertWidget(0, channel_widget)
        else:
            self.tabWidget = QtWidgets.QTabWidget(self)
            self.verticalLayout.insertWidget(0, self.tabWidget)
            for name, channel_widget in self.channel_widgets:
                channel_widget.calibrationEnabled.setChecked(False)
                cal_str = self.tr("Calibrate {}").format(name)
                channel_widget.calibrationEnabled.setText(cal_str)
                self.tabWidget.addTab(channel_widget, name)

    def setup_channel_signals(self, channel_widget):
        channel_widget.value_changed.connect(self.values_updated)

    def is_valid(self):
        all_valid = False
        for _name, channel_widget in self.channel_widgets:
            if channel_widget.calibrationEnabled.isChecked():
                if channel_widget.is_valid():
                    all_valid = True
                else:
                    return False
        return all_valid

    def values_updated(self):
        valid = self.is_valid()
        self.saveButton.setEnabled(valid)

    def save(self):
        settings = self.device_info['settings']

        unit_settings = {}
        float_settings = {}

        for _name, channel_widget in self.channel_widgets:
            if channel_widget.calibrationEnabled.isChecked():
                if channel_widget.is_valid():
                    scale, offset = channel_widget.scale_offset
                    u, f = hyperborea.calibration.get_channel_setting_values(
                        settings, channel_widget.calibration_info,
                        channel_widget.unit_info[0], scale, offset)
                    unit_settings.update(u)
                    float_settings.update(f)

        new_nvm = hyperborea.calibration.update_nvm(
            self.device_info['nvm'], settings,
            unit_settings, float_settings, self.logger)

        self.parent.write_nvm(new_nvm)
