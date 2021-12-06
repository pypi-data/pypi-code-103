import logging
import os

from PySide2 import QtCore, QtWidgets

from .ui_bulk_update_firmware import Ui_BulkUpdateFirmwareDialog

logger = logging.getLogger(__name__)


class BulkUpdateFirmwareDialog(QtWidgets.QDialog, Ui_BulkUpdateFirmwareDialog):
    def __init__(self, has_scan_power, parent=None):
        super().__init__(parent)

        self.has_scan_power = has_scan_power

        self.setupUi(self)
        self.extra_ui_setup()

    def extra_ui_setup(self):
        self.browseButton.clicked.connect(self.browse_cb)

        self.firmwareLocation.textChanged.connect(self.values_updated)

        self.minSerial.valueChanged.connect(self.min_updated)
        self.maxSerial.valueChanged.connect(self.max_updated)

        self.values_updated()

        if self.has_scan_power:
            self.radioStrength.setEnabled(True)
            self.radioStrengthLabel.setEnabled(True)
        else:
            self.radioStrength.setEnabled(False)
            self.radioStrengthLabel.setEnabled(False)

    def browse_cb(self):
        base_dir = os.path.dirname(self.firmwareLocation.text())

        if not base_dir:
            settings = QtCore.QSettings()
            base_dir = settings.value("fileSaveDirectory")
            if base_dir and type(base_dir) == str:
                if not os.path.isdir(base_dir):
                    base_dir = None

        if not base_dir:
            base_dir = ""

        # ask the user for the file name
        caption = self.tr("Open Firmware File")
        file_filter = self.tr("Firmware Files (*.firmware);;All Files (*.*)")
        val = QtWidgets.QFileDialog.getOpenFileName(self, caption, base_dir,
                                                    file_filter)
        output_path = val[0]

        if output_path:
            self.firmwareLocation.setText(output_path)

    def is_valid(self):
        firmware_location = self.firmwareLocation.text()
        if not os.path.isfile(firmware_location):
            return False

        return True

    def done(self, r):
        if r and not self.is_valid():
            return
        super().done(r)

    def values_updated(self, _junk=None):
        ok_button = self.buttonBox.button(QtWidgets.QDialogButtonBox.Ok)
        if self.is_valid():
            ok_button.setEnabled(True)
        else:
            ok_button.setEnabled(False)

    def min_updated(self, _junk=None):
        new_min = self.minSerial.value()
        if new_min > self.maxSerial.value():
            self.maxSerial.setValue(new_min)

    def max_updated(self, _junk=None):
        new_max = self.maxSerial.value()
        if new_max < self.minSerial.value():
            self.minSerial.setValue(new_max)

    def get_results(self):
        results = {}

        results['firmware_location'] = self.firmwareLocation.text()

        results['min_serial'] = self.minSerial.value()
        results['max_serial'] = self.maxSerial.value()
        if self.has_scan_power:
            results['radio_strength'] = self.radioStrength.value()
        else:
            results['radio_strength'] = None

        if self.setDeviceMode.isChecked():
            results['device_mode'] = self.deviceMode.value()
        else:
            results['device_mode'] = None

        return results
