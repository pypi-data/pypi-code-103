# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'about.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class Ui_AboutDialog(object):
    def setupUi(self, AboutDialog):
        if not AboutDialog.objectName():
            AboutDialog.setObjectName(u"AboutDialog")
        AboutDialog.resize(302, 232)
        self.verticalLayout = QVBoxLayout(AboutDialog)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.productLabel = QLabel(AboutDialog)
        self.productLabel.setObjectName(u"productLabel")
        font = QFont()
        font.setBold(True)
        font.setWeight(75)
        self.productLabel.setFont(font)
        self.productLabel.setAlignment(Qt.AlignCenter)

        self.verticalLayout.addWidget(self.productLabel)

        self.companyLabel = QLabel(AboutDialog)
        self.companyLabel.setObjectName(u"companyLabel")
        self.companyLabel.setAlignment(Qt.AlignCenter)
        self.companyLabel.setOpenExternalLinks(True)

        self.verticalLayout.addWidget(self.companyLabel)

        self.copyrightLabel = QLabel(AboutDialog)
        self.copyrightLabel.setObjectName(u"copyrightLabel")
        self.copyrightLabel.setTextFormat(Qt.RichText)
        self.copyrightLabel.setAlignment(Qt.AlignCenter)

        self.verticalLayout.addWidget(self.copyrightLabel)

        self.verticalSpacer_3 = QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Fixed)

        self.verticalLayout.addItem(self.verticalSpacer_3)

        self.version = QLabel(AboutDialog)
        self.version.setObjectName(u"version")
        self.version.setAlignment(Qt.AlignCenter)

        self.verticalLayout.addWidget(self.version)

        self.buildDate = QLabel(AboutDialog)
        self.buildDate.setObjectName(u"buildDate")
        self.buildDate.setAlignment(Qt.AlignCenter)

        self.verticalLayout.addWidget(self.buildDate)

        self.verticalSpacer_2 = QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Fixed)

        self.verticalLayout.addItem(self.verticalSpacer_2)

        self.libraryVersionsLabel = QLabel(AboutDialog)
        self.libraryVersionsLabel.setObjectName(u"libraryVersionsLabel")
        self.libraryVersionsLabel.setFont(font)
        self.libraryVersionsLabel.setAlignment(Qt.AlignCenter)

        self.verticalLayout.addWidget(self.libraryVersionsLabel)

        self.libraryVersions = QLabel(AboutDialog)
        self.libraryVersions.setObjectName(u"libraryVersions")

        self.verticalLayout.addWidget(self.libraryVersions)

        self.verticalSpacer = QSpacerItem(20, 0, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)

        self.buttonBox = QDialogButtonBox(AboutDialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Close)

        self.verticalLayout.addWidget(self.buttonBox)


        self.retranslateUi(AboutDialog)
        self.buttonBox.accepted.connect(AboutDialog.accept)
        self.buttonBox.rejected.connect(AboutDialog.reject)

        QMetaObject.connectSlotsByName(AboutDialog)
    # setupUi

    def retranslateUi(self, AboutDialog):
        AboutDialog.setWindowTitle(QCoreApplication.translate("AboutDialog", u"About Acheron", None))
        self.productLabel.setText(QCoreApplication.translate("AboutDialog", u"Acheron", None))
        self.companyLabel.setText(QCoreApplication.translate("AboutDialog", u"by <a href=\"https://suprocktech.com/\">Suprock Technologies</a>", None))
        self.copyrightLabel.setText(QCoreApplication.translate("AboutDialog", u"&copy; 2021", None))
        self.version.setText(QCoreApplication.translate("AboutDialog", u"Version", None))
        self.buildDate.setText(QCoreApplication.translate("AboutDialog", u"Build Date", None))
        self.libraryVersionsLabel.setText(QCoreApplication.translate("AboutDialog", u"Libraries", None))
        self.libraryVersions.setText(QCoreApplication.translate("AboutDialog", u"library: version", None))
    # retranslateUi

