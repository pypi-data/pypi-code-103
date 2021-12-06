import logging

from PySide2 import QtWidgets

from .update_func_limiter import UpdateFuncLimiter
from .ui_rgb_control_widget import Ui_RGBControlWidget

logger = logging.getLogger(__name__)


class RGBControlWidget(QtWidgets.QWidget, Ui_RGBControlWidget):
    def __init__(self, set_rgb, initial_values, parent=None):
        super().__init__(parent)

        self.setting_color = False

        self.updater = UpdateFuncLimiter(set_rgb, 100, self)

        self.setupUi(self)

        self.setup_callbacks()

        self.set_values(initial_values)

    def setup_callbacks(self):
        def setup_button(button, rgb):
            button.clicked.connect(lambda: self.set_color_from_button(rgb))
        setup_button(self.whiteButton, (255, 255, 255))
        setup_button(self.redButton, (255, 0, 0))
        setup_button(self.greenButton, (0, 255, 0))
        setup_button(self.blueButton, (0, 0, 255))
        setup_button(self.cyanButton, (0, 255, 255))
        setup_button(self.magentaButton, (255, 0, 255))
        setup_button(self.yellowButton, (255, 255, 0))
        setup_button(self.blackButton, (0, 0, 0))
        self.redSlider.valueChanged.connect(self.color_changed)
        self.greenSlider.valueChanged.connect(self.color_changed)
        self.blueSlider.valueChanged.connect(self.color_changed)

    def set_values(self, values):
        self.setting_color = True
        self.redSlider.setValue(values[0])
        self.greenSlider.setValue(values[1])
        self.blueSlider.setValue(values[2])
        self.setting_color = False

    def set_color_from_button(self, values):
        self.set_values(values)
        self.updater.update(values)

    def color_changed(self, _junk=None):
        if not self.setting_color:
            values = (self.redSlider.value(), self.greenSlider.value(),
                      self.blueSlider.value())
            self.updater.update(values)
