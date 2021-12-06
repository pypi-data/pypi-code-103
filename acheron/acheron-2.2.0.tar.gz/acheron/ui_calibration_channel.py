# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'calibration_channel.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *

from hyperborea.unit_formatter_spinbox import UnitFormatterDoubleSpinBox


class Ui_CalibrationChannel(object):
    def setupUi(self, CalibrationChannel):
        if not CalibrationChannel.objectName():
            CalibrationChannel.setObjectName(u"CalibrationChannel")
        CalibrationChannel.resize(195, 254)
        self.verticalLayout = QVBoxLayout(CalibrationChannel)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.calibrationEnabled = QCheckBox(CalibrationChannel)
        self.calibrationEnabled.setObjectName(u"calibrationEnabled")
        self.calibrationEnabled.setChecked(True)

        self.verticalLayout.addWidget(self.calibrationEnabled)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.unitLabel = QLabel(CalibrationChannel)
        self.unitLabel.setObjectName(u"unitLabel")

        self.horizontalLayout_3.addWidget(self.unitLabel)

        self.unit = QLabel(CalibrationChannel)
        self.unit.setObjectName(u"unit")

        self.horizontalLayout_3.addWidget(self.unit)

        self.horizontalSpacer = QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer)

        self.selectUnit = QPushButton(CalibrationChannel)
        self.selectUnit.setObjectName(u"selectUnit")

        self.horizontalLayout_3.addWidget(self.selectUnit)


        self.verticalLayout.addLayout(self.horizontalLayout_3)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.acRadioButton = QRadioButton(CalibrationChannel)
        self.acRadioButton.setObjectName(u"acRadioButton")
        self.acRadioButton.setChecked(True)

        self.horizontalLayout_2.addWidget(self.acRadioButton)

        self.linearRadioButton = QRadioButton(CalibrationChannel)
        self.linearRadioButton.setObjectName(u"linearRadioButton")

        self.horizontalLayout_2.addWidget(self.linearRadioButton)

        self.horizontalSpacer_3 = QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer_3)


        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.stackedWidget = QStackedWidget(CalibrationChannel)
        self.stackedWidget.setObjectName(u"stackedWidget")
        self.linearPage = QWidget()
        self.linearPage.setObjectName(u"linearPage")
        self.verticalLayout_2 = QVBoxLayout(self.linearPage)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.linearCapture = QPushButton(self.linearPage)
        self.linearCapture.setObjectName(u"linearCapture")

        self.horizontalLayout_5.addWidget(self.linearCapture)

        self.horizontalSpacer_6 = QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_5.addItem(self.horizontalSpacer_6)

        self.plotButton = QPushButton(self.linearPage)
        self.plotButton.setObjectName(u"plotButton")
        self.plotButton.setEnabled(False)

        self.horizontalLayout_5.addWidget(self.plotButton)


        self.verticalLayout_2.addLayout(self.horizontalLayout_5)

        self.linearTable = QTableWidget(self.linearPage)
        if (self.linearTable.columnCount() < 3):
            self.linearTable.setColumnCount(3)
        __qtablewidgetitem = QTableWidgetItem()
        self.linearTable.setHorizontalHeaderItem(0, __qtablewidgetitem)
        __qtablewidgetitem1 = QTableWidgetItem()
        self.linearTable.setHorizontalHeaderItem(1, __qtablewidgetitem1)
        __qtablewidgetitem2 = QTableWidgetItem()
        self.linearTable.setHorizontalHeaderItem(2, __qtablewidgetitem2)
        self.linearTable.setObjectName(u"linearTable")
        self.linearTable.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.linearTable.setSelectionMode(QAbstractItemView.NoSelection)
        self.linearTable.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)

        self.verticalLayout_2.addWidget(self.linearTable)

        self.stackedWidget.addWidget(self.linearPage)
        self.acPage = QWidget()
        self.acPage.setObjectName(u"acPage")
        self.formLayout = QFormLayout(self.acPage)
        self.formLayout.setObjectName(u"formLayout")
        self.formLayout.setContentsMargins(0, 0, 0, 0)
        self.capturedMagnitudeLabel = QLabel(self.acPage)
        self.capturedMagnitudeLabel.setObjectName(u"capturedMagnitudeLabel")

        self.formLayout.setWidget(1, QFormLayout.LabelRole, self.capturedMagnitudeLabel)

        self.capturedOffsetLabel = QLabel(self.acPage)
        self.capturedOffsetLabel.setObjectName(u"capturedOffsetLabel")

        self.formLayout.setWidget(2, QFormLayout.LabelRole, self.capturedOffsetLabel)

        self.actualMagnitudeLabel = QLabel(self.acPage)
        self.actualMagnitudeLabel.setObjectName(u"actualMagnitudeLabel")

        self.formLayout.setWidget(3, QFormLayout.LabelRole, self.actualMagnitudeLabel)

        self.actualOffsetLabel = QLabel(self.acPage)
        self.actualOffsetLabel.setObjectName(u"actualOffsetLabel")

        self.formLayout.setWidget(4, QFormLayout.LabelRole, self.actualOffsetLabel)

        self.capturedMagnitude = UnitFormatterDoubleSpinBox(self.acPage)
        self.capturedMagnitude.setObjectName(u"capturedMagnitude")
        self.capturedMagnitude.setValue(1.000000000000000)

        self.formLayout.setWidget(1, QFormLayout.FieldRole, self.capturedMagnitude)

        self.actualMagnitude = UnitFormatterDoubleSpinBox(self.acPage)
        self.actualMagnitude.setObjectName(u"actualMagnitude")
        self.actualMagnitude.setValue(1.000000000000000)

        self.formLayout.setWidget(3, QFormLayout.FieldRole, self.actualMagnitude)

        self.capturedOffset = UnitFormatterDoubleSpinBox(self.acPage)
        self.capturedOffset.setObjectName(u"capturedOffset")

        self.formLayout.setWidget(2, QFormLayout.FieldRole, self.capturedOffset)

        self.actualOffset = UnitFormatterDoubleSpinBox(self.acPage)
        self.actualOffset.setObjectName(u"actualOffset")

        self.formLayout.setWidget(4, QFormLayout.FieldRole, self.actualOffset)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.acCapture = QPushButton(self.acPage)
        self.acCapture.setObjectName(u"acCapture")

        self.horizontalLayout_4.addWidget(self.acCapture)

        self.horizontalSpacer_2 = QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_4.addItem(self.horizontalSpacer_2)


        self.formLayout.setLayout(0, QFormLayout.SpanningRole, self.horizontalLayout_4)

        self.stackedWidget.addWidget(self.acPage)

        self.verticalLayout.addWidget(self.stackedWidget)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setSpacing(6)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.scaleLabel = QLabel(CalibrationChannel)
        self.scaleLabel.setObjectName(u"scaleLabel")

        self.horizontalLayout.addWidget(self.scaleLabel)

        self.scale = QLineEdit(CalibrationChannel)
        self.scale.setObjectName(u"scale")
        self.scale.setReadOnly(True)

        self.horizontalLayout.addWidget(self.scale)

        self.offsetLabel = QLabel(CalibrationChannel)
        self.offsetLabel.setObjectName(u"offsetLabel")

        self.horizontalLayout.addWidget(self.offsetLabel)

        self.offset = QLineEdit(CalibrationChannel)
        self.offset.setObjectName(u"offset")
        self.offset.setReadOnly(True)

        self.horizontalLayout.addWidget(self.offset)


        self.verticalLayout.addLayout(self.horizontalLayout)

        QWidget.setTabOrder(self.calibrationEnabled, self.selectUnit)
        QWidget.setTabOrder(self.selectUnit, self.acRadioButton)
        QWidget.setTabOrder(self.acRadioButton, self.linearRadioButton)
        QWidget.setTabOrder(self.linearRadioButton, self.acCapture)
        QWidget.setTabOrder(self.acCapture, self.capturedMagnitude)
        QWidget.setTabOrder(self.capturedMagnitude, self.capturedOffset)
        QWidget.setTabOrder(self.capturedOffset, self.actualMagnitude)
        QWidget.setTabOrder(self.actualMagnitude, self.actualOffset)
        QWidget.setTabOrder(self.actualOffset, self.linearCapture)
        QWidget.setTabOrder(self.linearCapture, self.linearTable)
        QWidget.setTabOrder(self.linearTable, self.scale)
        QWidget.setTabOrder(self.scale, self.offset)

        self.retranslateUi(CalibrationChannel)

        self.stackedWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(CalibrationChannel)
    # setupUi

    def retranslateUi(self, CalibrationChannel):
        self.calibrationEnabled.setText(QCoreApplication.translate("CalibrationChannel", u"Calibrate channel", None))
        self.unitLabel.setText(QCoreApplication.translate("CalibrationChannel", u"Unit:", None))
        self.unit.setText(QCoreApplication.translate("CalibrationChannel", u"Unit", None))
        self.selectUnit.setText(QCoreApplication.translate("CalibrationChannel", u"Select Unit", None))
        self.acRadioButton.setText(QCoreApplication.translate("CalibrationChannel", u"AC RMS", None))
        self.linearRadioButton.setText(QCoreApplication.translate("CalibrationChannel", u"1st Order Linear", None))
        self.linearCapture.setText(QCoreApplication.translate("CalibrationChannel", u"Capture", None))
        self.plotButton.setText(QCoreApplication.translate("CalibrationChannel", u"Plot", None))
        ___qtablewidgetitem = self.linearTable.horizontalHeaderItem(0)
        ___qtablewidgetitem.setText(QCoreApplication.translate("CalibrationChannel", u"Captured", None));
        ___qtablewidgetitem1 = self.linearTable.horizontalHeaderItem(1)
        ___qtablewidgetitem1.setText(QCoreApplication.translate("CalibrationChannel", u"Actual", None));
        ___qtablewidgetitem2 = self.linearTable.horizontalHeaderItem(2)
        ___qtablewidgetitem2.setText(QCoreApplication.translate("CalibrationChannel", u"Delete", None));
        self.capturedMagnitudeLabel.setText(QCoreApplication.translate("CalibrationChannel", u"Captured RMS Magnitude", None))
        self.capturedOffsetLabel.setText(QCoreApplication.translate("CalibrationChannel", u"Captured DC Offset", None))
        self.actualMagnitudeLabel.setText(QCoreApplication.translate("CalibrationChannel", u"Actual RMS Magnitude", None))
        self.actualOffsetLabel.setText(QCoreApplication.translate("CalibrationChannel", u"Actual DC Offset", None))
        self.acCapture.setText(QCoreApplication.translate("CalibrationChannel", u"Capture", None))
        self.scaleLabel.setText(QCoreApplication.translate("CalibrationChannel", u"Scale", None))
        self.offsetLabel.setText(QCoreApplication.translate("CalibrationChannel", u"Offset", None))
        pass
    # retranslateUi

