import logging

from PySide2 import QtWidgets

import asphodel
from hyperborea.unit_formatter_spinbox import UnitFormatterSpinBox

from .update_func_limiter import UpdateFuncLimiter
from .ui_ctrl_var_widget import Ui_CtrlVarWidget

logger = logging.getLogger(__name__)


class CtrlVarWidget(QtWidgets.QWidget, Ui_CtrlVarWidget):
    def __init__(self, set_setting, name, ctrl_var_info, initial_value,
                 parent=None):
        super().__init__(parent)

        self.ctrl_var_info = ctrl_var_info
        self.setting_value = False

        self.updater = UpdateFuncLimiter(set_setting, 100, self)

        self.setupUi(self)
        self.nameLabel.setText(name)

        self.setup_spinbox(initial_value)
        self.setup_callbacks()

        self.set_value(initial_value)

    def setup_spinbox(self, initial_value):
        scaled_min = (self.ctrl_var_info.minimum * self.ctrl_var_info.scale +
                      self.ctrl_var_info.offset)
        scaled_max = (self.ctrl_var_info.maximum * self.ctrl_var_info.scale +
                      self.ctrl_var_info.offset)
        unit_formatter = asphodel.nativelib.create_unit_formatter(
            self.ctrl_var_info.unit_type, scaled_min, scaled_max,
            self.ctrl_var_info.scale)

        # update the unit formatter's scale and offset with the ctrl var's
        unit_formatter.conversion_offset += (self.ctrl_var_info.offset *
                                             unit_formatter.conversion_scale)
        unit_formatter.conversion_scale *= self.ctrl_var_info.scale

        if unit_formatter.conversion_scale < 0.0:
            self.inverted = True
            unit_formatter.conversion_scale = -unit_formatter.conversion_scale
        else:
            self.inverted = False

        self.spinBox = UnitFormatterSpinBox(unit_formatter, self)
        self.horizontalLayout.addWidget(self.spinBox)

        if not self.inverted:
            minimum = self.ctrl_var_info.minimum
            maximum = self.ctrl_var_info.maximum
            value = initial_value
        else:
            minimum = -self.ctrl_var_info.maximum
            maximum = -self.ctrl_var_info.minimum
            value = -initial_value

        self.spinBox.setMinimum(minimum)
        self.spinBox.setMaximum(maximum)
        self.spinBox.setValue(value)
        self.slider.setMinimum(minimum)
        self.slider.setMaximum(maximum)
        self.slider.setValue(value)

        self.spinBox.valueChanged.connect(self.slider.setValue)
        self.slider.valueChanged.connect(self.spinBox.setValue)

    def setup_callbacks(self):
        self.slider.valueChanged.connect(self.value_changed)

    def set_value(self, value):
        self.setting_value = True
        if not self.inverted:
            self.slider.setValue(value)
        else:
            self.slider.setValue(-value)
        self.setting_value = False

    def value_changed(self, _junk=None):
        if not self.setting_value:
            value = self.slider.value()
            if self.inverted:
                value = -value
            self.updater.update(value)
