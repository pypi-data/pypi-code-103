# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ctrl_var_panel.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class Ui_CtrlVarPanel(object):
    def setupUi(self, CtrlVarPanel):
        if not CtrlVarPanel.objectName():
            CtrlVarPanel.setObjectName(u"CtrlVarPanel")
        CtrlVarPanel.resize(99, 41)
        self.verticalLayout = QVBoxLayout(CtrlVarPanel)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.ctrlVarLayout = QVBoxLayout()
        self.ctrlVarLayout.setObjectName(u"ctrlVarLayout")

        self.verticalLayout.addLayout(self.ctrlVarLayout)

        self.verticalSpacer = QSpacerItem(10, 10, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)


        self.retranslateUi(CtrlVarPanel)

        QMetaObject.connectSlotsByName(CtrlVarPanel)
    # setupUi

    def retranslateUi(self, CtrlVarPanel):
        CtrlVarPanel.setWindowTitle(QCoreApplication.translate("CtrlVarPanel", u"Control Variable Panel", None))
        CtrlVarPanel.setTitle(QCoreApplication.translate("CtrlVarPanel", u"Control Variables", None))
    # retranslateUi

