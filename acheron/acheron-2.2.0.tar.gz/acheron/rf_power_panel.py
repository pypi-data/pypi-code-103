import logging

from PySide2 import QtCore, QtWidgets

from .ui_rf_power_panel import Ui_RFPowerPanel

logger = logging.getLogger(__name__)


class RFPowerPanel(QtWidgets.QGroupBox, Ui_RFPowerPanel):
    connected_signal = QtCore.Signal(bool)
    disconnected_signal = QtCore.Signal()
    status_signal = QtCore.Signal(bool)

    def __init__(self, enable_func, reset_timeout_func, status, parent=None):
        super().__init__(parent)

        self.enable_func = enable_func
        self.reset_timeout_func = reset_timeout_func

        self.setupUi(self)

        self.timeout_timer = QtCore.QTimer(self)
        self.timeout_timer.timeout.connect(self.timeout_cb)

        self.enableButton.clicked.connect(self.enable_callback)
        self.disableButton.clicked.connect(self.disable_callback)

        self.set_status(status)

    def add_ctrl_var_widget(self, widget):
        self.ctrlVarLayout.addWidget(widget)

    def set_status(self, status):
        if status:
            self.enableButton.setEnabled(False)
            self.disableButton.setEnabled(True)
        else:
            self.enableButton.setEnabled(True)
            self.disableButton.setEnabled(False)

    def enable_callback(self):
        self.enableButton.setEnabled(False)
        self.disableButton.setEnabled(True)
        self.enable_func(True)
        self.status_signal.emit(True)

    def disable_callback(self):
        self.enableButton.setEnabled(True)
        self.disableButton.setEnabled(False)
        self.enable_func(False)
        self.status_signal.emit(False)

    def connected(self, device_info):
        self.set_status(device_info['rf_power_status'])
        self.connected_signal.emit(device_info['rf_power_status'])
        self.timeout_timer.start(1000)  # 1 second

    def disconnected(self):
        self.timeout_timer.stop()
        self.disconnected_signal.emit()

    def stop(self):
        # use do a timeout with a low delay so the device can take its
        # boot setting into account for whether it wants to power down
        self.reset_timeout_func(1)
        self.status_signal.emit(False)

    def timeout_cb(self):
        self.reset_timeout_func(5000)  # 5 seconds
