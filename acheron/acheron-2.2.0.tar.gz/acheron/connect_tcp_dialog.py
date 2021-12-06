import logging

from PySide2 import QtCore, QtWidgets

from .ui_connect_tcp_dialog import Ui_ConnectTCPDialog

logger = logging.getLogger(__name__)


class ConnectTCPDialog(QtWidgets.QDialog, Ui_ConnectTCPDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.settings = QtCore.QSettings()

        self.setupUi(self)
        self.extra_ui_setup()

    def extra_ui_setup(self):
        # load initial values from settings
        hostname = self.settings.value("connectHostname")
        if hostname and type(hostname) == str:
            self.hostname.setText(hostname.strip())

        port = self.settings.value("connectPort")
        if port is not None:
            try:
                port = int(port)
                self.port.setValue(port)
            except ValueError:
                pass

        serial = self.settings.value("connectSerial")
        if serial and type(serial) == str:
            self.serial.setText(serial.strip())

        self.hostname.textEdited.connect(self.values_updated)

        self.values_updated()

    def is_valid(self):
        if not self.hostname.text().strip():
            return False

        return True

    def done(self, r):
        if r and not self.is_valid():
            return

        # save settings
        self.settings.setValue("connectHostname", self.hostname.text().strip())
        self.settings.setValue("connectPort", self.port.value())
        self.settings.setValue("connectSerial", self.serial.text().strip())

        super().done(r)

    def values_updated(self, _junk=None):
        ok_button = self.buttonBox.button(QtWidgets.QDialogButtonBox.Ok)
        if self.is_valid():
            ok_button.setEnabled(True)
        else:
            ok_button.setEnabled(False)

    def get_results(self):
        results = {'hostname': self.hostname.text().strip(),
                   'port': self.port.value()}

        sn = self.serial.text().strip()
        if len(sn) != 0:
            results['serial_number'] = sn
        else:
            results['serial_number'] = None

        return results
