import logging
import os

from PySide2 import QtCore, QtGui, QtWidgets

import hyperborea.alert
from hyperborea.preferences import read_bool_setting
from hyperborea.preferences import read_int_setting
from hyperborea.preferences import write_bool_setting

from .ui_preferences import Ui_PreferencesDialog

logger = logging.getLogger(__name__)


original_palette = None


def set_style(app, dark_mode=True):
    app.setStyle("Fusion")

    global original_palette
    if original_palette is None:
        original_palette = app.palette()

    # Now use a palette to switch to dark colors:
    if dark_mode:
        palette = QtGui.QPalette()
        palette.setColor(QtGui.QPalette.Window, QtGui.QColor(53, 53, 53))
        palette.setColor(QtGui.QPalette.WindowText, QtCore.Qt.white)
        palette.setColor(QtGui.QPalette.Base, QtGui.QColor(25, 25, 25))
        palette.setColor(QtGui.QPalette.AlternateBase,
                         QtGui.QColor(53, 53, 53))
        palette.setColor(QtGui.QPalette.ToolTipBase, QtCore.Qt.white)
        palette.setColor(QtGui.QPalette.ToolTipText, QtCore.Qt.white)
        palette.setColor(QtGui.QPalette.Text, QtCore.Qt.white)
        palette.setColor(QtGui.QPalette.Button, QtGui.QColor(53, 53, 53))
        palette.setColor(QtGui.QPalette.ButtonText, QtCore.Qt.white)
        palette.setColor(QtGui.QPalette.BrightText, QtCore.Qt.red)
        palette.setColor(QtGui.QPalette.Link, QtGui.QColor(42, 130, 218))
        palette.setColor(QtGui.QPalette.Highlight, QtGui.QColor(31, 97, 163))
        palette.setColor(QtGui.QPalette.HighlightedText, QtCore.Qt.white)

        palette.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.WindowText,
                         QtCore.Qt.darkGray)
        palette.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.Text,
                         QtCore.Qt.darkGray)
        palette.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.ButtonText,
                         QtCore.Qt.darkGray)
        palette.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.Light,
                         QtCore.Qt.black)

        app.setPalette(palette)
    else:
        app.setPalette(original_palette)


class PreferencesDialog(QtWidgets.QDialog, Ui_PreferencesDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.settings = QtCore.QSettings()

        self.setupUi(self)

        # this is easily forgotten in Qt Designer
        self.tabWidget.setCurrentIndex(0)

        self.accepted.connect(self.write_settings)
        self.browseButton.clicked.connect(self.browse_cb)
        self.testEmail.clicked.connect(self.test_email_cb)
        self.darkMode.toggled.connect(self.dark_mode_updated)
        self.lightMode.toggled.connect(self.dark_mode_updated)

        self.read_settings()

    def browse_cb(self):
        base_dir = self.outputLocation.text()
        base_dir = QtWidgets.QFileDialog.getExistingDirectory(self,
                                                              dir=base_dir)

        if base_dir:
            self.outputLocation.setText(base_dir)

    def test_email_cb(self):
        email_options = {
            'from_address': self.fromAddress.text().strip(),
            'to_address': self.toAddress.text().strip(),
            'smtp_host': self.smtpHost.text().strip(),
            'smtp_port': self.smtpPort.value(),
            'use_auth': self.useAuthentication.isChecked(),
            'smtp_user': self.smtpUser.text().strip(),
            'smtp_password': self.smtpPassword.text().strip()}

        if self.useSTARTTLS.isChecked():
            email_options['security'] = 'starttls'
        elif self.useSSL.isChecked():
            email_options['security'] = 'ssl'
        else:
            email_options['security'] = ''

        try:
            QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
            hyperborea.alert.send_test_email(email_options)
            QtWidgets.QApplication.restoreOverrideCursor()
            logger.info("Sent test email successfully")
            QtWidgets.QMessageBox.information(self, self.tr("Sent"),
                                              self.tr("Email Sent!"))
        except Exception as e:
            QtWidgets.QApplication.restoreOverrideCursor()
            logger.exception("Error sending test email.")
            error_str = str(e) + "\nSee log for more details."
            QtWidgets.QMessageBox.critical(self, self.tr("Error"), error_str)

    def dark_mode_updated(self, _junk=None):
        dark_mode = self.darkMode.isChecked()
        set_style(QtWidgets.QApplication.instance(), dark_mode)

    def read_settings(self):
        self.unitPreferences.read_settings()

        dark_mode = read_bool_setting(self.settings, "DarkMode", True)
        if dark_mode:
            self.darkMode.setChecked(True)
        else:
            self.lightMode.setChecked(True)

        base_dir = self.settings.value("BasePath")
        if not base_dir:
            documents_path = QtCore.QStandardPaths.writableLocation(
                QtCore.QStandardPaths.DocumentsLocation)
            app_name = QtWidgets.QApplication.applicationName()
            base_dir = os.path.join(documents_path, app_name + " Data")
        base_dir = os.path.normpath(base_dir)
        self.outputLocation.setText(base_dir)
        self.outputLocation.setCursorPosition(0)

        auto_rgb = read_bool_setting(self.settings, "AutoRGB", True)
        self.automaticRGBCheckBox.setChecked(auto_rgb)

        downsample = read_bool_setting(self.settings, "Downsample", True)
        self.downsampleCheckBox.setChecked(downsample)
        plot_mean = read_bool_setting(self.settings, "PlotMean", False)
        self.plotMeanCheckBox.setChecked(plot_mean)

        compression_level = read_int_setting(self.settings,
                                             "CompressionLevel", 6)
        self.compressionLevel.setValue(compression_level)

        self.settings.beginGroup("Upload")
        upload_enabled = read_bool_setting(self.settings, "Enabled", False)
        self.enableUpload.setChecked(upload_enabled)
        s3_bucket = self.settings.value("S3Bucket")
        if s3_bucket:
            self.s3Bucket.setText(s3_bucket.strip())
        aws_region = self.settings.value("AWSRegion")
        if aws_region:
            self.awsRegion.setText(aws_region.strip())
        upload_directory = self.settings.value("Directory")
        if upload_directory:
            self.uploadDirectory.setText(upload_directory.strip())
        access_key_id = self.settings.value("AccessKeyID")
        if access_key_id:
            self.uploadAccessKeyID.setText(access_key_id.strip())
        secret_access_key = self.settings.value("SecretAccessKey")
        if secret_access_key:
            self.uploadSecretAccessKey.setText(secret_access_key.strip())
        delete_original = read_bool_setting(self.settings, "DeleteOriginal",
                                            False)
        self.uploadDeleteOriginal.setChecked(delete_original)
        self.settings.endGroup()

        self.settings.beginGroup("AlertEmail")
        email_enabled = read_bool_setting(self.settings, "Enabled", False)
        self.enableAlertEmail.setChecked(email_enabled)
        from_address = self.settings.value("FromAddress")
        if from_address:
            self.fromAddress.setText(from_address.strip())
        to_address = self.settings.value("ToAddress")
        if to_address:
            self.toAddress.setText(to_address.strip())
        smtp_host = self.settings.value("SMTPHost")
        if smtp_host:
            self.smtpHost.setText(smtp_host.strip())
        smtp_port = read_int_setting(self.settings, "SMTPPort", 587)
        self.smtpPort.setValue(smtp_port)
        security = self.settings.value("Security")
        if security:
            security = security.strip()
        if security == "STARTTLS":
            self.useSTARTTLS.setChecked(True)
        elif security == "SSL":
            self.useSSL.setChecked(True)
        elif security == "None":
            self.noSecurity.setChecked(True)
        else:
            self.useSTARTTLS.setChecked(True)  # default
        use_auth = read_bool_setting(self.settings, "UseAuth", True)
        self.useAuthentication.setChecked(use_auth)
        smtp_user = self.settings.value("SMTPUser")
        if smtp_user:
            self.smtpUser.setText(smtp_user.strip())
        smtp_password = self.settings.value("SMTPPassword")
        if smtp_password:
            self.smtpPassword.setText(smtp_password.strip())
        self.settings.endGroup()

    def write_settings(self):
        self.unitPreferences.write_settings()

        dark_mode = self.darkMode.isChecked()
        write_bool_setting(self.settings, "DarkMode", dark_mode)

        base_dir = self.outputLocation.text()
        self.settings.setValue("BasePath", base_dir)

        auto_rgb = self.automaticRGBCheckBox.isChecked()
        write_bool_setting(self.settings, "AutoRGB", auto_rgb)

        downsample = self.downsampleCheckBox.isChecked()
        write_bool_setting(self.settings, "Downsample", downsample)
        plot_mean = self.plotMeanCheckBox.isChecked()
        write_bool_setting(self.settings, "PlotMean", plot_mean)

        compression_level = self.compressionLevel.value()
        self.settings.setValue("CompressionLevel", compression_level)

        self.settings.beginGroup("Upload")
        upload_enabled = self.enableUpload.isChecked()
        write_bool_setting(self.settings, "Enabled", upload_enabled)
        s3_bucket = self.s3Bucket.text().strip()
        self.settings.setValue("S3Bucket", s3_bucket)
        aws_region = self.awsRegion.text().strip()
        self.settings.setValue("AWSRegion", aws_region)
        upload_directory = self.uploadDirectory.text().strip()
        self.settings.setValue("Directory", upload_directory)
        access_key_id = self.uploadAccessKeyID.text().strip()
        self.settings.setValue("AccessKeyID", access_key_id)
        secret_access_key = self.uploadSecretAccessKey.text().strip()
        self.settings.setValue("SecretAccessKey", secret_access_key)
        delete_original = self.uploadDeleteOriginal.isChecked()
        write_bool_setting(self.settings, "DeleteOriginal", delete_original)
        self.settings.endGroup()

        self.settings.beginGroup("AlertEmail")
        email_enabled = self.enableAlertEmail.isChecked()
        write_bool_setting(self.settings, "Enabled", email_enabled)
        from_address = self.fromAddress.text().strip()
        self.settings.setValue("FromAddress", from_address)
        to_address = self.toAddress.text().strip()
        self.settings.setValue("ToAddress", to_address)
        smtp_host = self.smtpHost.text().strip()
        self.settings.setValue("SMTPHost", smtp_host)
        smtp_port = self.smtpPort.value()
        self.settings.setValue("SMTPPort", smtp_port)
        if self.useSTARTTLS.isChecked():
            self.settings.setValue("Security", "STARTTLS")
        elif self.useSSL.isChecked():
            self.settings.setValue("Security", "SSL")
        else:
            self.settings.setValue("Security", "None")
        use_auth = self.useAuthentication.isChecked()
        write_bool_setting(self.settings, "UseAuth", use_auth)
        if use_auth:
            smtp_user = self.smtpUser.text().strip()
            self.settings.setValue("SMTPUser", smtp_user)
            smtp_password = self.smtpPassword.text().strip()
            self.settings.setValue("SMTPPassword", smtp_password)
        else:
            self.settings.setValue("SMTPUser", "")
            self.settings.setValue("SMTPPassword", "")
        self.settings.endGroup()
