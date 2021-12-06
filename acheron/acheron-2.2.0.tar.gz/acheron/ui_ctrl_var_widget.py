# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ctrl_var_widget.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class Ui_CtrlVarWidget(object):
    def setupUi(self, CtrlVarWidget):
        if not CtrlVarWidget.objectName():
            CtrlVarWidget.setObjectName(u"CtrlVarWidget")
        CtrlVarWidget.resize(121, 19)
        self.horizontalLayout = QHBoxLayout(CtrlVarWidget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.nameLabel = QLabel(CtrlVarWidget)
        self.nameLabel.setObjectName(u"nameLabel")

        self.horizontalLayout.addWidget(self.nameLabel)

        self.slider = QSlider(CtrlVarWidget)
        self.slider.setObjectName(u"slider")
        self.slider.setMinimumSize(QSize(50, 0))
        self.slider.setOrientation(Qt.Horizontal)

        self.horizontalLayout.addWidget(self.slider)


        self.retranslateUi(CtrlVarWidget)

        QMetaObject.connectSlotsByName(CtrlVarWidget)
    # setupUi

    def retranslateUi(self, CtrlVarWidget):
        CtrlVarWidget.setWindowTitle(QCoreApplication.translate("CtrlVarWidget", u"Ctrl Var Widget", None))
        self.nameLabel.setText(QCoreApplication.translate("CtrlVarWidget", u"Ctrl Var Name", None))
    # retranslateUi

