# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'hardware_tests.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class Ui_HardwareTestDialog(object):
    def setupUi(self, HardwareTestDialog):
        if not HardwareTestDialog.objectName():
            HardwareTestDialog.setObjectName(u"HardwareTestDialog")
        HardwareTestDialog.resize(754, 426)
        self.verticalLayout = QVBoxLayout(HardwareTestDialog)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.testOutput = QPlainTextEdit(HardwareTestDialog)
        self.testOutput.setObjectName(u"testOutput")
        self.testOutput.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.testOutput.setReadOnly(True)

        self.verticalLayout.addWidget(self.testOutput)

        self.buttonBox = QDialogButtonBox(HardwareTestDialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Close|QDialogButtonBox.Reset)

        self.verticalLayout.addWidget(self.buttonBox)


        self.retranslateUi(HardwareTestDialog)
        self.buttonBox.accepted.connect(HardwareTestDialog.accept)
        self.buttonBox.rejected.connect(HardwareTestDialog.reject)

        QMetaObject.connectSlotsByName(HardwareTestDialog)
    # setupUi

    def retranslateUi(self, HardwareTestDialog):
        HardwareTestDialog.setWindowTitle(QCoreApplication.translate("HardwareTestDialog", u"Hardware Tests", None))
    # retranslateUi

