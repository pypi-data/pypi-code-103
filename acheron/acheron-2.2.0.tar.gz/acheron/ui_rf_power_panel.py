# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'rf_power_panel.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class Ui_RFPowerPanel(object):
    def setupUi(self, RFPowerPanel):
        if not RFPowerPanel.objectName():
            RFPowerPanel.setObjectName(u"RFPowerPanel")
        RFPowerPanel.resize(111, 99)
        self.verticalLayout = QVBoxLayout(RFPowerPanel)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.enableButton = QPushButton(RFPowerPanel)
        self.enableButton.setObjectName(u"enableButton")

        self.verticalLayout.addWidget(self.enableButton)

        self.disableButton = QPushButton(RFPowerPanel)
        self.disableButton.setObjectName(u"disableButton")

        self.verticalLayout.addWidget(self.disableButton)

        self.ctrlVarLayout = QVBoxLayout()
        self.ctrlVarLayout.setObjectName(u"ctrlVarLayout")

        self.verticalLayout.addLayout(self.ctrlVarLayout)

        self.verticalSpacer = QSpacerItem(10, 10, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)


        self.retranslateUi(RFPowerPanel)

        QMetaObject.connectSlotsByName(RFPowerPanel)
    # setupUi

    def retranslateUi(self, RFPowerPanel):
        RFPowerPanel.setWindowTitle(QCoreApplication.translate("RFPowerPanel", u"RF Power Panel", None))
        RFPowerPanel.setTitle(QCoreApplication.translate("RFPowerPanel", u"RF Power", None))
        self.enableButton.setText(QCoreApplication.translate("RFPowerPanel", u"Enable RF Power", None))
        self.disableButton.setText(QCoreApplication.translate("RFPowerPanel", u"Disable RF Power", None))
    # retranslateUi

