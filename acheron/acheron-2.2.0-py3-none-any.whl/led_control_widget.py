import logging

from PySide2 import QtWidgets

from .update_func_limiter import UpdateFuncLimiter
from .ui_led_control_widget import Ui_LEDControlWidget

logger = logging.getLogger(__name__)


class LEDControlWidget(QtWidgets.QWidget, Ui_LEDControlWidget):
    def __init__(self, set_led, initial_value, parent=None):
        super().__init__(parent)

        self.setting_value = False

        self.updater = UpdateFuncLimiter(set_led, 100, self)

        self.setupUi(self)

        self.setup_callbacks()

        self.set_value(initial_value)

    def setup_callbacks(self):
        self.slider.valueChanged.connect(self.value_changed)

    def set_value(self, value):
        self.setting_value = True
        self.slider.setValue(value)
        self.setting_value = False

    def value_changed(self, _junk=None):
        if not self.setting_value:
            value = self.slider.value()
            self.updater.update(value)
