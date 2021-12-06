import logging

from PySide2 import QtWidgets

from .ui_remote_panel import Ui_RemotePanel

logger = logging.getLogger(__name__)


class RemotePanel(QtWidgets.QGroupBox, Ui_RemotePanel):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.device_tab = parent

        self.setupUi(self)

        self.goToParentButton.clicked.connect(self.show_radio_tab)

    def connected(self, device_info):
        self.device_tab.radio_tab.radio_panel.remote_connected(device_info)

    def disconnected(self):
        pass

    def stop(self):
        pass

    def show_radio_tab(self):
        self.device_tab.plotmain.show_tab(self.device_tab.radio_tab)
