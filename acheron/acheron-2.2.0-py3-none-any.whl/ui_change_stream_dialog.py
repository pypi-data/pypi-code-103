# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'change_stream_dialog.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class Ui_ChangeStreamDialog(object):
    def setupUi(self, ChangeStreamDialog):
        if not ChangeStreamDialog.objectName():
            ChangeStreamDialog.setObjectName(u"ChangeStreamDialog")
        ChangeStreamDialog.resize(403, 49)
        self.verticalLayout_2 = QVBoxLayout(ChangeStreamDialog)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")

        self.verticalLayout_2.addLayout(self.verticalLayout)

        self.buttonBox = QDialogButtonBox(ChangeStreamDialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)

        self.verticalLayout_2.addWidget(self.buttonBox)


        self.retranslateUi(ChangeStreamDialog)
        self.buttonBox.accepted.connect(ChangeStreamDialog.accept)
        self.buttonBox.rejected.connect(ChangeStreamDialog.reject)

        QMetaObject.connectSlotsByName(ChangeStreamDialog)
    # setupUi

    def retranslateUi(self, ChangeStreamDialog):
        ChangeStreamDialog.setWindowTitle(QCoreApplication.translate("ChangeStreamDialog", u"Change Streams", None))
    # retranslateUi

