# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'bulk_update_firmware.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class Ui_BulkUpdateFirmwareDialog(object):
    def setupUi(self, BulkUpdateFirmwareDialog):
        if not BulkUpdateFirmwareDialog.objectName():
            BulkUpdateFirmwareDialog.setObjectName(u"BulkUpdateFirmwareDialog")
        BulkUpdateFirmwareDialog.resize(387, 262)
        self.gridLayout = QGridLayout(BulkUpdateFirmwareDialog)
        self.gridLayout.setObjectName(u"gridLayout")
        self.firmwareLabel = QLabel(BulkUpdateFirmwareDialog)
        self.firmwareLabel.setObjectName(u"firmwareLabel")
        font = QFont()
        font.setBold(True)
        font.setWeight(75)
        self.firmwareLabel.setFont(font)

        self.gridLayout.addWidget(self.firmwareLabel, 0, 0, 1, 4)

        self.horizontalSpacer_6 = QSpacerItem(20, 13, QSizePolicy.Fixed, QSizePolicy.Minimum)

        self.gridLayout.addItem(self.horizontalSpacer_6, 1, 0, 1, 1)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.firmwareLocation = QLineEdit(BulkUpdateFirmwareDialog)
        self.firmwareLocation.setObjectName(u"firmwareLocation")

        self.horizontalLayout.addWidget(self.firmwareLocation)

        self.browseButton = QPushButton(BulkUpdateFirmwareDialog)
        self.browseButton.setObjectName(u"browseButton")

        self.horizontalLayout.addWidget(self.browseButton)


        self.gridLayout.addLayout(self.horizontalLayout, 1, 1, 1, 3)

        self.serialRangeLabel = QLabel(BulkUpdateFirmwareDialog)
        self.serialRangeLabel.setObjectName(u"serialRangeLabel")
        self.serialRangeLabel.setFont(font)

        self.gridLayout.addWidget(self.serialRangeLabel, 2, 0, 1, 4)

        self.minSerialLabel = QLabel(BulkUpdateFirmwareDialog)
        self.minSerialLabel.setObjectName(u"minSerialLabel")

        self.gridLayout.addWidget(self.minSerialLabel, 3, 1, 1, 2)

        self.minSerial = QSpinBox(BulkUpdateFirmwareDialog)
        self.minSerial.setObjectName(u"minSerial")
        self.minSerial.setMaximum(2147483647)

        self.gridLayout.addWidget(self.minSerial, 3, 3, 1, 1)

        self.maxSerialLabel = QLabel(BulkUpdateFirmwareDialog)
        self.maxSerialLabel.setObjectName(u"maxSerialLabel")

        self.gridLayout.addWidget(self.maxSerialLabel, 4, 1, 1, 2)

        self.maxSerial = QSpinBox(BulkUpdateFirmwareDialog)
        self.maxSerial.setObjectName(u"maxSerial")
        self.maxSerial.setMaximum(2147483647)
        self.maxSerial.setValue(2147483647)

        self.gridLayout.addWidget(self.maxSerial, 4, 3, 1, 1)

        self.setDeviceModeLabel = QLabel(BulkUpdateFirmwareDialog)
        self.setDeviceModeLabel.setObjectName(u"setDeviceModeLabel")
        self.setDeviceModeLabel.setFont(font)

        self.gridLayout.addWidget(self.setDeviceModeLabel, 6, 0, 1, 4)

        self.setDeviceMode = QCheckBox(BulkUpdateFirmwareDialog)
        self.setDeviceMode.setObjectName(u"setDeviceMode")

        self.gridLayout.addWidget(self.setDeviceMode, 7, 1, 1, 3)

        self.horizontalSpacer_5 = QSpacerItem(20, 13, QSizePolicy.Fixed, QSizePolicy.Minimum)

        self.gridLayout.addItem(self.horizontalSpacer_5, 8, 1, 1, 1)

        self.deviceModeLabel = QLabel(BulkUpdateFirmwareDialog)
        self.deviceModeLabel.setObjectName(u"deviceModeLabel")
        self.deviceModeLabel.setEnabled(False)

        self.gridLayout.addWidget(self.deviceModeLabel, 8, 2, 1, 1)

        self.deviceMode = QSpinBox(BulkUpdateFirmwareDialog)
        self.deviceMode.setObjectName(u"deviceMode")
        self.deviceMode.setEnabled(False)
        self.deviceMode.setMaximum(255)
        self.deviceMode.setValue(2)

        self.gridLayout.addWidget(self.deviceMode, 8, 3, 1, 1)

        self.verticalSpacer_8 = QSpacerItem(369, 2, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.gridLayout.addItem(self.verticalSpacer_8, 9, 0, 1, 4)

        self.buttonBox = QDialogButtonBox(BulkUpdateFirmwareDialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)

        self.gridLayout.addWidget(self.buttonBox, 10, 0, 1, 4)

        self.radioStrengthLabel = QLabel(BulkUpdateFirmwareDialog)
        self.radioStrengthLabel.setObjectName(u"radioStrengthLabel")

        self.gridLayout.addWidget(self.radioStrengthLabel, 5, 1, 1, 2)

        self.radioStrength = QSpinBox(BulkUpdateFirmwareDialog)
        self.radioStrength.setObjectName(u"radioStrength")
        self.radioStrength.setMinimum(-100)
        self.radioStrength.setMaximum(0)
        self.radioStrength.setValue(-100)

        self.gridLayout.addWidget(self.radioStrength, 5, 3, 1, 1)

        self.gridLayout.setColumnStretch(2, 1)
        QWidget.setTabOrder(self.firmwareLocation, self.browseButton)
        QWidget.setTabOrder(self.browseButton, self.minSerial)
        QWidget.setTabOrder(self.minSerial, self.maxSerial)
        QWidget.setTabOrder(self.maxSerial, self.setDeviceMode)
        QWidget.setTabOrder(self.setDeviceMode, self.deviceMode)
        QWidget.setTabOrder(self.deviceMode, self.buttonBox)

        self.retranslateUi(BulkUpdateFirmwareDialog)
        self.buttonBox.accepted.connect(BulkUpdateFirmwareDialog.accept)
        self.buttonBox.rejected.connect(BulkUpdateFirmwareDialog.reject)
        self.setDeviceMode.toggled.connect(self.deviceModeLabel.setEnabled)
        self.setDeviceMode.toggled.connect(self.deviceMode.setEnabled)

        QMetaObject.connectSlotsByName(BulkUpdateFirmwareDialog)
    # setupUi

    def retranslateUi(self, BulkUpdateFirmwareDialog):
        BulkUpdateFirmwareDialog.setWindowTitle(QCoreApplication.translate("BulkUpdateFirmwareDialog", u"Bulk Update Firmware", None))
        self.firmwareLabel.setText(QCoreApplication.translate("BulkUpdateFirmwareDialog", u"Firmware", None))
        self.browseButton.setText(QCoreApplication.translate("BulkUpdateFirmwareDialog", u"Browse...", None))
        self.serialRangeLabel.setText(QCoreApplication.translate("BulkUpdateFirmwareDialog", u"Device Filtering", None))
        self.minSerialLabel.setText(QCoreApplication.translate("BulkUpdateFirmwareDialog", u"Minimum SN", None))
        self.maxSerialLabel.setText(QCoreApplication.translate("BulkUpdateFirmwareDialog", u"Maximum SN", None))
        self.setDeviceModeLabel.setText(QCoreApplication.translate("BulkUpdateFirmwareDialog", u"Set Device Mode", None))
        self.setDeviceMode.setText(QCoreApplication.translate("BulkUpdateFirmwareDialog", u"Set Device Mode After Update", None))
        self.deviceModeLabel.setText(QCoreApplication.translate("BulkUpdateFirmwareDialog", u"Device Mode", None))
        self.radioStrengthLabel.setText(QCoreApplication.translate("BulkUpdateFirmwareDialog", u"Minimum Radio Strength", None))
        self.radioStrength.setSuffix(QCoreApplication.translate("BulkUpdateFirmwareDialog", u" dBm", None))
    # retranslateUi

