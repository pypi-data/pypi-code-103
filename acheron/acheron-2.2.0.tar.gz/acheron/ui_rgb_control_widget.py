# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'rgb_control_widget.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class Ui_RGBControlWidget(object):
    def setupUi(self, RGBControlWidget):
        if not RGBControlWidget.objectName():
            RGBControlWidget.setObjectName(u"RGBControlWidget")
        RGBControlWidget.resize(182, 198)
        self.verticalLayout = QVBoxLayout(RGBControlWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName(u"gridLayout")
        self.whiteButton = QPushButton(RGBControlWidget)
        self.whiteButton.setObjectName(u"whiteButton")
        sizePolicy = QSizePolicy(QSizePolicy.Ignored, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.whiteButton.sizePolicy().hasHeightForWidth())
        self.whiteButton.setSizePolicy(sizePolicy)
        self.whiteButton.setMinimumSize(QSize(30, 0))

        self.gridLayout.addWidget(self.whiteButton, 0, 1, 1, 1)

        self.redButton = QPushButton(RGBControlWidget)
        self.redButton.setObjectName(u"redButton")
        sizePolicy.setHeightForWidth(self.redButton.sizePolicy().hasHeightForWidth())
        self.redButton.setSizePolicy(sizePolicy)
        self.redButton.setMinimumSize(QSize(30, 0))

        self.gridLayout.addWidget(self.redButton, 1, 0, 1, 1)

        self.greenButton = QPushButton(RGBControlWidget)
        self.greenButton.setObjectName(u"greenButton")
        sizePolicy.setHeightForWidth(self.greenButton.sizePolicy().hasHeightForWidth())
        self.greenButton.setSizePolicy(sizePolicy)
        self.greenButton.setMinimumSize(QSize(30, 0))

        self.gridLayout.addWidget(self.greenButton, 1, 1, 1, 1)

        self.blueButton = QPushButton(RGBControlWidget)
        self.blueButton.setObjectName(u"blueButton")
        sizePolicy.setHeightForWidth(self.blueButton.sizePolicy().hasHeightForWidth())
        self.blueButton.setSizePolicy(sizePolicy)
        self.blueButton.setMinimumSize(QSize(30, 0))

        self.gridLayout.addWidget(self.blueButton, 1, 2, 1, 1)

        self.cyanButton = QPushButton(RGBControlWidget)
        self.cyanButton.setObjectName(u"cyanButton")
        sizePolicy.setHeightForWidth(self.cyanButton.sizePolicy().hasHeightForWidth())
        self.cyanButton.setSizePolicy(sizePolicy)
        self.cyanButton.setMinimumSize(QSize(30, 0))

        self.gridLayout.addWidget(self.cyanButton, 2, 0, 1, 1)

        self.magentaButton = QPushButton(RGBControlWidget)
        self.magentaButton.setObjectName(u"magentaButton")
        sizePolicy.setHeightForWidth(self.magentaButton.sizePolicy().hasHeightForWidth())
        self.magentaButton.setSizePolicy(sizePolicy)
        self.magentaButton.setMinimumSize(QSize(30, 0))

        self.gridLayout.addWidget(self.magentaButton, 2, 1, 1, 1)

        self.yellowButton = QPushButton(RGBControlWidget)
        self.yellowButton.setObjectName(u"yellowButton")
        sizePolicy.setHeightForWidth(self.yellowButton.sizePolicy().hasHeightForWidth())
        self.yellowButton.setSizePolicy(sizePolicy)
        self.yellowButton.setMinimumSize(QSize(30, 0))

        self.gridLayout.addWidget(self.yellowButton, 2, 2, 1, 1)

        self.blackButton = QPushButton(RGBControlWidget)
        self.blackButton.setObjectName(u"blackButton")
        sizePolicy.setHeightForWidth(self.blackButton.sizePolicy().hasHeightForWidth())
        self.blackButton.setSizePolicy(sizePolicy)
        self.blackButton.setMinimumSize(QSize(30, 0))

        self.gridLayout.addWidget(self.blackButton, 3, 1, 1, 1)


        self.verticalLayout.addLayout(self.gridLayout)

        self.gridLayout_2 = QGridLayout()
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.blueLabel = QLabel(RGBControlWidget)
        self.blueLabel.setObjectName(u"blueLabel")

        self.gridLayout_2.addWidget(self.blueLabel, 2, 0, 1, 1)

        self.blueSlider = QSlider(RGBControlWidget)
        self.blueSlider.setObjectName(u"blueSlider")
        sizePolicy1 = QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.blueSlider.sizePolicy().hasHeightForWidth())
        self.blueSlider.setSizePolicy(sizePolicy1)
        self.blueSlider.setMinimumSize(QSize(100, 0))
        self.blueSlider.setMaximum(255)
        self.blueSlider.setOrientation(Qt.Horizontal)

        self.gridLayout_2.addWidget(self.blueSlider, 2, 1, 1, 1)

        self.blueSpinBox = QSpinBox(RGBControlWidget)
        self.blueSpinBox.setObjectName(u"blueSpinBox")
        self.blueSpinBox.setMaximum(255)

        self.gridLayout_2.addWidget(self.blueSpinBox, 2, 2, 1, 1)

        self.greenLabel = QLabel(RGBControlWidget)
        self.greenLabel.setObjectName(u"greenLabel")

        self.gridLayout_2.addWidget(self.greenLabel, 1, 0, 1, 1)

        self.redSpinBox = QSpinBox(RGBControlWidget)
        self.redSpinBox.setObjectName(u"redSpinBox")
        self.redSpinBox.setMaximum(255)

        self.gridLayout_2.addWidget(self.redSpinBox, 0, 2, 1, 1)

        self.redLabel = QLabel(RGBControlWidget)
        self.redLabel.setObjectName(u"redLabel")

        self.gridLayout_2.addWidget(self.redLabel, 0, 0, 1, 1)

        self.redSlider = QSlider(RGBControlWidget)
        self.redSlider.setObjectName(u"redSlider")
        sizePolicy1.setHeightForWidth(self.redSlider.sizePolicy().hasHeightForWidth())
        self.redSlider.setSizePolicy(sizePolicy1)
        self.redSlider.setMinimumSize(QSize(100, 0))
        self.redSlider.setMaximum(255)
        self.redSlider.setOrientation(Qt.Horizontal)

        self.gridLayout_2.addWidget(self.redSlider, 0, 1, 1, 1)

        self.greenSpinBox = QSpinBox(RGBControlWidget)
        self.greenSpinBox.setObjectName(u"greenSpinBox")
        self.greenSpinBox.setMaximum(255)

        self.gridLayout_2.addWidget(self.greenSpinBox, 1, 2, 1, 1)

        self.greenSlider = QSlider(RGBControlWidget)
        self.greenSlider.setObjectName(u"greenSlider")
        sizePolicy1.setHeightForWidth(self.greenSlider.sizePolicy().hasHeightForWidth())
        self.greenSlider.setSizePolicy(sizePolicy1)
        self.greenSlider.setMinimumSize(QSize(100, 0))
        self.greenSlider.setMaximum(255)
        self.greenSlider.setOrientation(Qt.Horizontal)

        self.gridLayout_2.addWidget(self.greenSlider, 1, 1, 1, 1)


        self.verticalLayout.addLayout(self.gridLayout_2)

#if QT_CONFIG(shortcut)
        self.blueLabel.setBuddy(self.blueSlider)
        self.greenLabel.setBuddy(self.greenSlider)
        self.redLabel.setBuddy(self.redSlider)
#endif // QT_CONFIG(shortcut)

        self.retranslateUi(RGBControlWidget)
        self.redSlider.valueChanged.connect(self.redSpinBox.setValue)
        self.greenSlider.valueChanged.connect(self.greenSpinBox.setValue)
        self.blueSlider.valueChanged.connect(self.blueSpinBox.setValue)
        self.redSpinBox.valueChanged.connect(self.redSlider.setValue)
        self.greenSpinBox.valueChanged.connect(self.greenSlider.setValue)
        self.blueSpinBox.valueChanged.connect(self.blueSlider.setValue)

        QMetaObject.connectSlotsByName(RGBControlWidget)
    # setupUi

    def retranslateUi(self, RGBControlWidget):
        RGBControlWidget.setWindowTitle(QCoreApplication.translate("RGBControlWidget", u"RGB Control Widget", None))
        self.whiteButton.setText(QCoreApplication.translate("RGBControlWidget", u"White", None))
        self.redButton.setText(QCoreApplication.translate("RGBControlWidget", u"Red", None))
        self.greenButton.setText(QCoreApplication.translate("RGBControlWidget", u"Green", None))
        self.blueButton.setText(QCoreApplication.translate("RGBControlWidget", u"Blue", None))
        self.cyanButton.setText(QCoreApplication.translate("RGBControlWidget", u"Cyan", None))
        self.magentaButton.setText(QCoreApplication.translate("RGBControlWidget", u"Magenta", None))
        self.yellowButton.setText(QCoreApplication.translate("RGBControlWidget", u"Yellow", None))
        self.blackButton.setText(QCoreApplication.translate("RGBControlWidget", u"Black", None))
        self.blueLabel.setText(QCoreApplication.translate("RGBControlWidget", u"Blue", None))
        self.greenLabel.setText(QCoreApplication.translate("RGBControlWidget", u"Green", None))
        self.redLabel.setText(QCoreApplication.translate("RGBControlWidget", u"Red", None))
    # retranslateUi

