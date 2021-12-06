# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'connect_tcp_dialog.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class Ui_ConnectTCPDialog(object):
    def setupUi(self, ConnectTCPDialog):
        if not ConnectTCPDialog.objectName():
            ConnectTCPDialog.setObjectName(u"ConnectTCPDialog")
        ConnectTCPDialog.resize(341, 119)
        self.formLayout = QFormLayout(ConnectTCPDialog)
        self.formLayout.setObjectName(u"formLayout")
        self.hostnameLabel = QLabel(ConnectTCPDialog)
        self.hostnameLabel.setObjectName(u"hostnameLabel")

        self.formLayout.setWidget(0, QFormLayout.LabelRole, self.hostnameLabel)

        self.hostname = QLineEdit(ConnectTCPDialog)
        self.hostname.setObjectName(u"hostname")
        self.hostname.setMinimumSize(QSize(200, 0))

        self.formLayout.setWidget(0, QFormLayout.FieldRole, self.hostname)

        self.portLabel = QLabel(ConnectTCPDialog)
        self.portLabel.setObjectName(u"portLabel")

        self.formLayout.setWidget(1, QFormLayout.LabelRole, self.portLabel)

        self.port = QSpinBox(ConnectTCPDialog)
        self.port.setObjectName(u"port")
        self.port.setMinimum(1)
        self.port.setMaximum(65535)
        self.port.setValue(5760)

        self.formLayout.setWidget(1, QFormLayout.FieldRole, self.port)

        self.serialLabel = QLabel(ConnectTCPDialog)
        self.serialLabel.setObjectName(u"serialLabel")

        self.formLayout.setWidget(2, QFormLayout.LabelRole, self.serialLabel)

        self.serial = QLineEdit(ConnectTCPDialog)
        self.serial.setObjectName(u"serial")

        self.formLayout.setWidget(2, QFormLayout.FieldRole, self.serial)

        self.buttonBox = QDialogButtonBox(ConnectTCPDialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)

        self.formLayout.setWidget(3, QFormLayout.SpanningRole, self.buttonBox)


        self.retranslateUi(ConnectTCPDialog)
        self.buttonBox.accepted.connect(ConnectTCPDialog.accept)
        self.buttonBox.rejected.connect(ConnectTCPDialog.reject)

        QMetaObject.connectSlotsByName(ConnectTCPDialog)
    # setupUi

    def retranslateUi(self, ConnectTCPDialog):
        ConnectTCPDialog.setWindowTitle(QCoreApplication.translate("ConnectTCPDialog", u"Connect TCP Device", None))
        self.hostnameLabel.setText(QCoreApplication.translate("ConnectTCPDialog", u"Hostname", None))
#if QT_CONFIG(tooltip)
        self.portLabel.setToolTip(QCoreApplication.translate("ConnectTCPDialog", u"Default: 5760", None))
#endif // QT_CONFIG(tooltip)
        self.portLabel.setText(QCoreApplication.translate("ConnectTCPDialog", u"Port", None))
#if QT_CONFIG(tooltip)
        self.port.setToolTip(QCoreApplication.translate("ConnectTCPDialog", u"Default: 5760", None))
#endif // QT_CONFIG(tooltip)
        self.serialLabel.setText(QCoreApplication.translate("ConnectTCPDialog", u"Serial Number (Optional)", None))
    # retranslateUi

