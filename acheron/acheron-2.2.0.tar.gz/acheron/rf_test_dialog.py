import logging

from PySide2 import QtWidgets

from .ui_rf_test_dialog import Ui_RFTestDialog

logger = logging.getLogger(__name__)


class RFTestDialog(QtWidgets.QDialog, Ui_RFTestDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setupUi(self)
        self.extra_ui_setup()

    def extra_ui_setup(self):
        self.test_type_group = QtWidgets.QButtonGroup()
        self.test_type_group.addButton(self.fixedRadioButton)
        self.test_type_group.addButton(self.sweepRadioButton)

        self.test_mode_group = QtWidgets.QButtonGroup()
        self.test_mode_group.addButton(self.txCarrierRadioButton)
        self.test_mode_group.addButton(self.rxCarrierRadioButton)
        self.test_mode_group.addButton(self.txModulatedRadioButton)

        self.fixedChannel.editingFinished.connect(self.check_channels)
        self.startChannel.editingFinished.connect(self.check_channels)
        self.stopChannel.editingFinished.connect(self.check_channels)

        self.fixedRadioButton.setChecked(True)
        self.txCarrierRadioButton.setChecked(True)

    def check_channels(self, junk=None):
        fixed_channel = self.fixedChannel.value()
        if fixed_channel % 2 != 0:
            self.fixedChannel.setValue(fixed_channel - 1)
        start_channel = self.startChannel.value()
        if start_channel % 2 != 0:
            self.startChannel.setValue(start_channel - 1)
        stop_channel = self.stopChannel.value()
        if stop_channel % 2 != 0:
            self.stopChannel.setValue(stop_channel - 1)

    def get_results(self):
        params = {}
        if self.fixedRadioButton.isChecked():
            test_type = "fixed"
            params['channel'] = self.fixedChannel.value()
            params['duration'] = self.fixedDuration.value()
        else:  # self.sweepRadioButton.isChecked()
            test_type = "sweep"
            params['start'] = self.startChannel.value()
            params['stop'] = self.stopChannel.value()
            params['hop_interval'] = self.hopInterval.value()
            params['hop_count'] = self.hopCount.value()

        if self.txCarrierRadioButton.isChecked():
            params['mode'] = 0
        elif self.rxCarrierRadioButton.isChecked():
            params['mode'] = 1
        else:  # self.txModulatedRadioButton.isChecked()
            params['mode'] = 2

        return (test_type, params)
