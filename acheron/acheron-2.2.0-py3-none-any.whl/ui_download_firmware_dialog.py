# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'download_firmware_dialog.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class Ui_DownloadFirmwareDialog(object):
    def setupUi(self, DownloadFirmwareDialog):
        if not DownloadFirmwareDialog.objectName():
            DownloadFirmwareDialog.setObjectName(u"DownloadFirmwareDialog")
        DownloadFirmwareDialog.resize(374, 147)
        self.formLayout = QFormLayout(DownloadFirmwareDialog)
        self.formLayout.setObjectName(u"formLayout")
        self.formLayout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        self.boardRadioButton = QRadioButton(DownloadFirmwareDialog)
        self.boardRadioButton.setObjectName(u"boardRadioButton")
        self.boardRadioButton.setChecked(False)

        self.formLayout.setWidget(0, QFormLayout.LabelRole, self.boardRadioButton)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.boardName = QLineEdit(DownloadFirmwareDialog)
        self.boardName.setObjectName(u"boardName")
        self.boardName.setMinimumSize(QSize(200, 0))

        self.horizontalLayout.addWidget(self.boardName)

        self.revLabel = QLabel(DownloadFirmwareDialog)
        self.revLabel.setObjectName(u"revLabel")

        self.horizontalLayout.addWidget(self.revLabel)

        self.boardRev = QSpinBox(DownloadFirmwareDialog)
        self.boardRev.setObjectName(u"boardRev")
        self.boardRev.setMaximum(255)
        self.boardRev.setValue(1)

        self.horizontalLayout.addWidget(self.boardRev)


        self.formLayout.setLayout(0, QFormLayout.FieldRole, self.horizontalLayout)

        self.repoRadioButton = QRadioButton(DownloadFirmwareDialog)
        self.repoRadioButton.setObjectName(u"repoRadioButton")

        self.formLayout.setWidget(1, QFormLayout.LabelRole, self.repoRadioButton)

        self.repoName = QLineEdit(DownloadFirmwareDialog)
        self.repoName.setObjectName(u"repoName")
        self.repoName.setEnabled(False)

        self.formLayout.setWidget(1, QFormLayout.FieldRole, self.repoName)

        self.branchRadioButton = QRadioButton(DownloadFirmwareDialog)
        self.branchRadioButton.setObjectName(u"branchRadioButton")
        self.branchRadioButton.setChecked(True)

        self.formLayout.setWidget(2, QFormLayout.LabelRole, self.branchRadioButton)

        self.branchName = QLineEdit(DownloadFirmwareDialog)
        self.branchName.setObjectName(u"branchName")

        self.formLayout.setWidget(2, QFormLayout.FieldRole, self.branchName)

        self.commitRadioButton = QRadioButton(DownloadFirmwareDialog)
        self.commitRadioButton.setObjectName(u"commitRadioButton")

        self.formLayout.setWidget(3, QFormLayout.LabelRole, self.commitRadioButton)

        self.commitHash = QLineEdit(DownloadFirmwareDialog)
        self.commitHash.setObjectName(u"commitHash")
        self.commitHash.setEnabled(False)

        self.formLayout.setWidget(3, QFormLayout.FieldRole, self.commitHash)

        self.buttonBox = QDialogButtonBox(DownloadFirmwareDialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)

        self.formLayout.setWidget(4, QFormLayout.SpanningRole, self.buttonBox)

        QWidget.setTabOrder(self.boardRadioButton, self.boardName)
        QWidget.setTabOrder(self.boardName, self.boardRev)
        QWidget.setTabOrder(self.boardRev, self.repoRadioButton)
        QWidget.setTabOrder(self.repoRadioButton, self.repoName)
        QWidget.setTabOrder(self.repoName, self.branchRadioButton)
        QWidget.setTabOrder(self.branchRadioButton, self.branchName)
        QWidget.setTabOrder(self.branchName, self.commitRadioButton)
        QWidget.setTabOrder(self.commitRadioButton, self.commitHash)
        QWidget.setTabOrder(self.commitHash, self.buttonBox)

        self.retranslateUi(DownloadFirmwareDialog)
        self.buttonBox.accepted.connect(DownloadFirmwareDialog.accept)
        self.buttonBox.rejected.connect(DownloadFirmwareDialog.reject)
        self.boardRadioButton.toggled.connect(self.boardName.setEnabled)
        self.boardRadioButton.toggled.connect(self.boardRev.setEnabled)
        self.repoRadioButton.toggled.connect(self.repoName.setEnabled)
        self.branchRadioButton.toggled.connect(self.branchName.setEnabled)
        self.commitRadioButton.toggled.connect(self.commitHash.setEnabled)

        QMetaObject.connectSlotsByName(DownloadFirmwareDialog)
    # setupUi

    def retranslateUi(self, DownloadFirmwareDialog):
        DownloadFirmwareDialog.setWindowTitle(QCoreApplication.translate("DownloadFirmwareDialog", u"Download Firmware", None))
        self.boardRadioButton.setText(QCoreApplication.translate("DownloadFirmwareDialog", u"Board", None))
        self.revLabel.setText(QCoreApplication.translate("DownloadFirmwareDialog", u"Rev", None))
        self.repoRadioButton.setText(QCoreApplication.translate("DownloadFirmwareDialog", u"Repository", None))
        self.branchRadioButton.setText(QCoreApplication.translate("DownloadFirmwareDialog", u"Branch", None))
        self.branchName.setText(QCoreApplication.translate("DownloadFirmwareDialog", u"master", None))
        self.commitRadioButton.setText(QCoreApplication.translate("DownloadFirmwareDialog", u"Commit", None))
    # retranslateUi

