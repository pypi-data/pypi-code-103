import logging
import math

from PySide2 import QtWidgets

import asphodel

from .ui_edit_alert_dialog import Ui_EditAlertDialog

logger = logging.getLogger(__name__)


class EditAlertDialog(QtWidgets.QDialog, Ui_EditAlertDialog):
    def __init__(self, alert_enabled, alert_values, subchannel_name,
                 unit_formatter, parent=None):
        self.subchannel_name = subchannel_name
        self.unit_formatter = unit_formatter

        super().__init__(parent)

        self.setupUi(self)
        self.extra_ui_setup(alert_enabled, alert_values)

    def extra_ui_setup(self, alert_enabled, alert_values):
        uf = asphodel.nativelib.create_custom_unit_formatter(
            1.0, 0.0, 0.0, self.unit_formatter.unit_ascii,
            self.unit_formatter.unit_utf8, self.unit_formatter.unit_html)

        self.meanLow.set_unit_formatter(uf)
        self.meanHigh.set_unit_formatter(uf)
        self.stdLow.set_unit_formatter(uf)
        self.stdHigh.set_unit_formatter(uf)

        self.meanLow.setMinimum(-math.inf)
        self.meanHigh.setMinimum(-math.inf)
        self.stdLow.setMinimum(0.0)
        self.stdHigh.setMinimum(0.0)
        self.meanLow.setMaximum(math.inf)
        self.meanHigh.setMaximum(math.inf)
        self.stdLow.setMaximum(math.inf)
        self.stdHigh.setMaximum(math.inf)

        self.alert_ordering = [
            (self.meanLowEnabled, self.meanLow),
            (self.meanHighEnabled, self.meanHigh),
            (self.stdLowEnabled, self.stdLow),
            (self.stdHighEnabled, self.stdHigh)]

        for e, v, (enabled, spinbox) in zip(alert_enabled, alert_values,
                                            self.alert_ordering):
            enabled.setChecked(e)
            spinbox.setValue(v)

    def get_alert_settings(self):
        alert_enabled = []
        alert_values = []

        for enabled, spinbox in self.alert_ordering:
            alert_enabled.append(enabled.isChecked())
            alert_values.append(spinbox.value())

        return alert_enabled, alert_values
