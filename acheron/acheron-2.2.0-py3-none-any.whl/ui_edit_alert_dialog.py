# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'edit_alert_dialog.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *

from hyperborea.unit_formatter_spinbox import UnitFormatterDoubleSpinBox


class Ui_EditAlertDialog(object):
    def setupUi(self, EditAlertDialog):
        if not EditAlertDialog.objectName():
            EditAlertDialog.setObjectName(u"EditAlertDialog")
        EditAlertDialog.resize(323, 145)
        self.formLayout = QFormLayout(EditAlertDialog)
        self.formLayout.setObjectName(u"formLayout")
        self.meanHighEnabled = QCheckBox(EditAlertDialog)
        self.meanHighEnabled.setObjectName(u"meanHighEnabled")

        self.formLayout.setWidget(0, QFormLayout.LabelRole, self.meanHighEnabled)

        self.meanHigh = UnitFormatterDoubleSpinBox(EditAlertDialog)
        self.meanHigh.setObjectName(u"meanHigh")
        self.meanHigh.setEnabled(False)
        self.meanHigh.setMinimumSize(QSize(200, 0))

        self.formLayout.setWidget(0, QFormLayout.FieldRole, self.meanHigh)

        self.meanLowEnabled = QCheckBox(EditAlertDialog)
        self.meanLowEnabled.setObjectName(u"meanLowEnabled")

        self.formLayout.setWidget(1, QFormLayout.LabelRole, self.meanLowEnabled)

        self.meanLow = UnitFormatterDoubleSpinBox(EditAlertDialog)
        self.meanLow.setObjectName(u"meanLow")
        self.meanLow.setEnabled(False)
        self.meanLow.setMinimumSize(QSize(200, 0))

        self.formLayout.setWidget(1, QFormLayout.FieldRole, self.meanLow)

        self.stdHighEnabled = QCheckBox(EditAlertDialog)
        self.stdHighEnabled.setObjectName(u"stdHighEnabled")

        self.formLayout.setWidget(2, QFormLayout.LabelRole, self.stdHighEnabled)

        self.stdHigh = UnitFormatterDoubleSpinBox(EditAlertDialog)
        self.stdHigh.setObjectName(u"stdHigh")
        self.stdHigh.setEnabled(False)
        self.stdHigh.setMinimumSize(QSize(200, 0))

        self.formLayout.setWidget(2, QFormLayout.FieldRole, self.stdHigh)

        self.stdLowEnabled = QCheckBox(EditAlertDialog)
        self.stdLowEnabled.setObjectName(u"stdLowEnabled")

        self.formLayout.setWidget(3, QFormLayout.LabelRole, self.stdLowEnabled)

        self.stdLow = UnitFormatterDoubleSpinBox(EditAlertDialog)
        self.stdLow.setObjectName(u"stdLow")
        self.stdLow.setEnabled(False)
        self.stdLow.setMinimumSize(QSize(200, 0))

        self.formLayout.setWidget(3, QFormLayout.FieldRole, self.stdLow)

        self.buttonBox = QDialogButtonBox(EditAlertDialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)

        self.formLayout.setWidget(4, QFormLayout.SpanningRole, self.buttonBox)


        self.retranslateUi(EditAlertDialog)
        self.buttonBox.accepted.connect(EditAlertDialog.accept)
        self.buttonBox.rejected.connect(EditAlertDialog.reject)
        self.meanHighEnabled.toggled.connect(self.meanHigh.setEnabled)
        self.meanLowEnabled.toggled.connect(self.meanLow.setEnabled)
        self.stdHighEnabled.toggled.connect(self.stdHigh.setEnabled)
        self.stdLowEnabled.toggled.connect(self.stdLow.setEnabled)

        QMetaObject.connectSlotsByName(EditAlertDialog)
    # setupUi

    def retranslateUi(self, EditAlertDialog):
        EditAlertDialog.setWindowTitle(QCoreApplication.translate("EditAlertDialog", u"Edit Alerts", None))
        self.meanHighEnabled.setText(QCoreApplication.translate("EditAlertDialog", u"Mean High Alert", None))
        self.meanLowEnabled.setText(QCoreApplication.translate("EditAlertDialog", u"Mean Low Alert", None))
        self.stdHighEnabled.setText(QCoreApplication.translate("EditAlertDialog", u"Std High Alert", None))
        self.stdLowEnabled.setText(QCoreApplication.translate("EditAlertDialog", u"Std Low Alert", None))
    # retranslateUi

