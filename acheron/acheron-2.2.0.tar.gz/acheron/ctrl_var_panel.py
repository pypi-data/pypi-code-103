import logging

from PySide2 import QtWidgets

from .ui_ctrl_var_panel import Ui_CtrlVarPanel

logger = logging.getLogger(__name__)


class CtrlVarPanel(QtWidgets.QGroupBox, Ui_CtrlVarPanel):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setupUi(self)

    def add_ctrl_var_widget(self, widget):
        self.ctrlVarLayout.addWidget(widget)

    def connected(self, device_info):
        pass

    def disconnected(self):
        pass

    def stop(self):
        pass
