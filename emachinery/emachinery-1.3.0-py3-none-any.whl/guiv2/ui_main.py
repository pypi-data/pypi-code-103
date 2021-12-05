# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'GUI_BASE.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *

from mplwidget import MplWidget
from consolewidget import ConsoleWidget
from qcodeeditor import QCodeEditor

import files_rc

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1000, 1005)
        MainWindow.setMinimumSize(QSize(1000, 720))
        palette = QPalette()
        brush = QBrush(QColor(255, 255, 255, 255))
        brush.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.WindowText, brush)
        brush1 = QBrush(QColor(0, 0, 0, 0))
        brush1.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.Button, brush1)
        brush2 = QBrush(QColor(66, 73, 90, 255))
        brush2.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.Light, brush2)
        brush3 = QBrush(QColor(55, 61, 75, 255))
        brush3.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.Midlight, brush3)
        brush4 = QBrush(QColor(22, 24, 30, 255))
        brush4.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.Dark, brush4)
        brush5 = QBrush(QColor(29, 32, 40, 255))
        brush5.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.Mid, brush5)
        brush6 = QBrush(QColor(210, 210, 210, 255))
        brush6.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.Text, brush6)
        palette.setBrush(QPalette.Active, QPalette.BrightText, brush)
        palette.setBrush(QPalette.Active, QPalette.ButtonText, brush)
        palette.setBrush(QPalette.Active, QPalette.Base, brush1)
        palette.setBrush(QPalette.Active, QPalette.Window, brush1)
        brush7 = QBrush(QColor(0, 0, 0, 255))
        brush7.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.Shadow, brush7)
        brush8 = QBrush(QColor(85, 170, 255, 255))
        brush8.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.Highlight, brush8)
        palette.setBrush(QPalette.Active, QPalette.Link, brush8)
        brush9 = QBrush(QColor(255, 0, 127, 255))
        brush9.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.LinkVisited, brush9)
        palette.setBrush(QPalette.Active, QPalette.AlternateBase, brush4)
        brush10 = QBrush(QColor(44, 49, 60, 255))
        brush10.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.ToolTipBase, brush10)
        palette.setBrush(QPalette.Active, QPalette.ToolTipText, brush6)
        brush11 = QBrush(QColor(210, 210, 210, 128))
        brush11.setStyle(Qt.NoBrush)
#if QT_VERSION >= QT_VERSION_CHECK(5, 12, 0)
        palette.setBrush(QPalette.Active, QPalette.PlaceholderText, brush11)
#endif
        palette.setBrush(QPalette.Inactive, QPalette.WindowText, brush)
        palette.setBrush(QPalette.Inactive, QPalette.Button, brush1)
        palette.setBrush(QPalette.Inactive, QPalette.Light, brush2)
        palette.setBrush(QPalette.Inactive, QPalette.Midlight, brush3)
        palette.setBrush(QPalette.Inactive, QPalette.Dark, brush4)
        palette.setBrush(QPalette.Inactive, QPalette.Mid, brush5)
        palette.setBrush(QPalette.Inactive, QPalette.Text, brush6)
        palette.setBrush(QPalette.Inactive, QPalette.BrightText, brush)
        palette.setBrush(QPalette.Inactive, QPalette.ButtonText, brush)
        palette.setBrush(QPalette.Inactive, QPalette.Base, brush1)
        palette.setBrush(QPalette.Inactive, QPalette.Window, brush1)
        palette.setBrush(QPalette.Inactive, QPalette.Shadow, brush7)
        palette.setBrush(QPalette.Inactive, QPalette.Highlight, brush8)
        palette.setBrush(QPalette.Inactive, QPalette.Link, brush8)
        palette.setBrush(QPalette.Inactive, QPalette.LinkVisited, brush9)
        palette.setBrush(QPalette.Inactive, QPalette.AlternateBase, brush4)
        palette.setBrush(QPalette.Inactive, QPalette.ToolTipBase, brush10)
        palette.setBrush(QPalette.Inactive, QPalette.ToolTipText, brush6)
        brush12 = QBrush(QColor(210, 210, 210, 128))
        brush12.setStyle(Qt.NoBrush)
#if QT_VERSION >= QT_VERSION_CHECK(5, 12, 0)
        palette.setBrush(QPalette.Inactive, QPalette.PlaceholderText, brush12)
#endif
        palette.setBrush(QPalette.Disabled, QPalette.WindowText, brush4)
        palette.setBrush(QPalette.Disabled, QPalette.Button, brush1)
        palette.setBrush(QPalette.Disabled, QPalette.Light, brush2)
        palette.setBrush(QPalette.Disabled, QPalette.Midlight, brush3)
        palette.setBrush(QPalette.Disabled, QPalette.Dark, brush4)
        palette.setBrush(QPalette.Disabled, QPalette.Mid, brush5)
        palette.setBrush(QPalette.Disabled, QPalette.Text, brush4)
        palette.setBrush(QPalette.Disabled, QPalette.BrightText, brush)
        palette.setBrush(QPalette.Disabled, QPalette.ButtonText, brush4)
        palette.setBrush(QPalette.Disabled, QPalette.Base, brush1)
        palette.setBrush(QPalette.Disabled, QPalette.Window, brush1)
        palette.setBrush(QPalette.Disabled, QPalette.Shadow, brush7)
        brush13 = QBrush(QColor(51, 153, 255, 255))
        brush13.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Disabled, QPalette.Highlight, brush13)
        palette.setBrush(QPalette.Disabled, QPalette.Link, brush8)
        palette.setBrush(QPalette.Disabled, QPalette.LinkVisited, brush9)
        palette.setBrush(QPalette.Disabled, QPalette.AlternateBase, brush10)
        palette.setBrush(QPalette.Disabled, QPalette.ToolTipBase, brush10)
        palette.setBrush(QPalette.Disabled, QPalette.ToolTipText, brush6)
        brush14 = QBrush(QColor(210, 210, 210, 128))
        brush14.setStyle(Qt.NoBrush)
#if QT_VERSION >= QT_VERSION_CHECK(5, 12, 0)
        palette.setBrush(QPalette.Disabled, QPalette.PlaceholderText, brush14)
#endif
        MainWindow.setPalette(palette)
        font = QFont()
        font.setFamily(u"Segoe UI")
        font.setPointSize(10)
        MainWindow.setFont(font)
        MainWindow.setStyleSheet(u"QMainWindow {background: transparent; }\n"
"QToolTip {\n"
"	color: #ffffff;\n"
"	background-color: rgba(27, 29, 35, 160);\n"
"	border: 1px solid rgb(40, 40, 40);\n"
"	border-radius: 2px;\n"
"}")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.centralwidget.setStyleSheet(u"background: transparent;\n"
"color: rgb(210, 210, 210);")
        self.horizontalLayout = QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(10, 10, 10, 10)
        self.frame_main = QFrame(self.centralwidget)
        self.frame_main.setObjectName(u"frame_main")
        self.frame_main.setStyleSheet(u"/* LINE EDIT */\n"
"QLineEdit {\n"
"	background-color: rgb(27, 29, 35);\n"
"	border-radius: 5px;\n"
"	border: 2px solid rgb(27, 29, 35);\n"
"	padding-left: 10px;\n"
"}\n"
"QLineEdit:hover {\n"
"	border: 2px solid rgb(64, 71, 88);\n"
"}\n"
"QLineEdit:focus {\n"
"	border: 2px solid rgb(91, 101, 124);\n"
"}\n"
"\n"
"/* SCROLL BARS */\n"
"QScrollBar:horizontal {\n"
"    border: none;\n"
"    background: rgb(52, 59, 72);\n"
"    height: 14px;\n"
"    margin: 0px 21px 0 21px;\n"
"	border-radius: 0px;\n"
"}\n"
"QScrollBar::handle:horizontal {\n"
"    background: rgb(85, 170, 255);\n"
"    min-width: 25px;\n"
"	border-radius: 7px\n"
"}\n"
"QScrollBar::add-line:horizontal {\n"
"    border: none;\n"
"    background: rgb(55, 63, 77);\n"
"    width: 20px;\n"
"	border-top-right-radius: 7px;\n"
"    border-bottom-right-radius: 7px;\n"
"    subcontrol-position: right;\n"
"    subcontrol-origin: margin;\n"
"}\n"
"QScrollBar::sub-line:horizontal {\n"
"    border: none;\n"
"    background: rgb(55, 63, 77);\n"
"    width: 20px;\n"
""
                        "	border-top-left-radius: 7px;\n"
"    border-bottom-left-radius: 7px;\n"
"    subcontrol-position: left;\n"
"    subcontrol-origin: margin;\n"
"}\n"
"QScrollBar::up-arrow:horizontal, QScrollBar::down-arrow:horizontal\n"
"{\n"
"     background: none;\n"
"}\n"
"QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal\n"
"{\n"
"     background: none;\n"
"}\n"
" QScrollBar:vertical {\n"
"	border: none;\n"
"    background: rgb(52, 59, 72);\n"
"    width: 14px;\n"
"    margin: 21px 0 21px 0;\n"
"	border-radius: 0px;\n"
" }\n"
" QScrollBar::handle:vertical {	\n"
"	background: rgb(85, 170, 255);\n"
"    min-height: 25px;\n"
"	border-radius: 7px\n"
" }\n"
" QScrollBar::add-line:vertical {\n"
"     border: none;\n"
"    background: rgb(55, 63, 77);\n"
"     height: 20px;\n"
"	border-bottom-left-radius: 7px;\n"
"    border-bottom-right-radius: 7px;\n"
"     subcontrol-position: bottom;\n"
"     subcontrol-origin: margin;\n"
" }\n"
" QScrollBar::sub-line:vertical {\n"
"	border: none;\n"
"    background: rgb(55, 63"
                        ", 77);\n"
"     height: 20px;\n"
"	border-top-left-radius: 7px;\n"
"    border-top-right-radius: 7px;\n"
"     subcontrol-position: top;\n"
"     subcontrol-origin: margin;\n"
" }\n"
" QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical {\n"
"     background: none;\n"
" }\n"
"\n"
" QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {\n"
"     background: none;\n"
" }\n"
"\n"
"/* CHECKBOX */\n"
"QCheckBox::indicator {\n"
"    border: 3px solid rgb(52, 59, 72);\n"
"	width: 15px;\n"
"	height: 15px;\n"
"	border-radius: 10px;\n"
"    background: rgb(44, 49, 60);\n"
"}\n"
"QCheckBox::indicator:hover {\n"
"    border: 3px solid rgb(58, 66, 81);\n"
"}\n"
"QCheckBox::indicator:checked {\n"
"    background: 3px solid rgb(52, 59, 72);\n"
"	border: 3px solid rgb(52, 59, 72);	\n"
"	background-image: url(:/16x16/icons/16x16/cil-check-alt.png);\n"
"}\n"
"\n"
"/* RADIO BUTTON */\n"
"QRadioButton::indicator {\n"
"    border: 3px solid rgb(52, 59, 72);\n"
"	width: 15px;\n"
"	height: 15px;\n"
"	border-radius"
                        ": 10px;\n"
"    background: rgb(44, 49, 60);\n"
"}\n"
"QRadioButton::indicator:hover {\n"
"    border: 3px solid rgb(58, 66, 81);\n"
"}\n"
"QRadioButton::indicator:checked {\n"
"    background: 3px solid rgb(94, 106, 130);\n"
"	border: 3px solid rgb(52, 59, 72);	\n"
"}\n"
"\n"
"/* COMBOBOX */\n"
"QComboBox{\n"
"	background-color: rgb(27, 29, 35);\n"
"	border-radius: 5px;\n"
"	border: 2px solid rgb(27, 29, 35);\n"
"	padding: 5px;\n"
"	padding-left: 10px;\n"
"}\n"
"QComboBox:hover{\n"
"	border: 2px solid rgb(64, 71, 88);\n"
"}\n"
"QComboBox::drop-down {\n"
"	subcontrol-origin: padding;\n"
"	subcontrol-position: top right;\n"
"	width: 25px; \n"
"	border-left-width: 3px;\n"
"	border-left-color: rgba(39, 44, 54, 150);\n"
"	border-left-style: solid;\n"
"	border-top-right-radius: 3px;\n"
"	border-bottom-right-radius: 3px;	\n"
"	background-image: url(:/16x16/icons/16x16/cil-arrow-bottom.png);\n"
"	background-position: center;\n"
"	background-repeat: no-reperat;\n"
" }\n"
"QComboBox QAbstractItemView {\n"
"	color: rgb("
                        "85, 170, 255);	\n"
"	background-color: rgb(27, 29, 35);\n"
"	padding: 10px;\n"
"	selection-background-color: rgb(39, 44, 54);\n"
"}\n"
"\n"
"/* SLIDERS */\n"
"QSlider::groove:horizontal {\n"
"    border-radius: 9px;\n"
"    height: 18px;\n"
"	margin: 0px;\n"
"	background-color: rgb(52, 59, 72);\n"
"}\n"
"QSlider::groove:horizontal:hover {\n"
"	background-color: rgb(55, 62, 76);\n"
"}\n"
"QSlider::handle:horizontal {\n"
"    background-color: rgb(85, 170, 255);\n"
"    border: none;\n"
"    height: 18px;\n"
"    width: 18px;\n"
"    margin: 0px;\n"
"	border-radius: 9px;\n"
"}\n"
"QSlider::handle:horizontal:hover {\n"
"    background-color: rgb(105, 180, 255);\n"
"}\n"
"QSlider::handle:horizontal:pressed {\n"
"    background-color: rgb(65, 130, 195);\n"
"}\n"
"\n"
"QSlider::groove:vertical {\n"
"    border-radius: 9px;\n"
"    width: 18px;\n"
"    margin: 0px;\n"
"	background-color: rgb(52, 59, 72);\n"
"}\n"
"QSlider::groove:vertical:hover {\n"
"	background-color: rgb(55, 62, 76);\n"
"}\n"
"QSlider::handle:verti"
                        "cal {\n"
"    background-color: rgb(85, 170, 255);\n"
"	border: none;\n"
"    height: 18px;\n"
"    width: 18px;\n"
"    margin: 0px;\n"
"	border-radius: 9px;\n"
"}\n"
"QSlider::handle:vertical:hover {\n"
"    background-color: rgb(105, 180, 255);\n"
"}\n"
"QSlider::handle:vertical:pressed {\n"
"    background-color: rgb(65, 130, 195);\n"
"}\n"
"\n"
"")
        self.frame_main.setFrameShape(QFrame.NoFrame)
        self.frame_main.setFrameShadow(QFrame.Raised)
        self.verticalLayout = QVBoxLayout(self.frame_main)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.frame_top = QFrame(self.frame_main)
        self.frame_top.setObjectName(u"frame_top")
        self.frame_top.setMinimumSize(QSize(0, 65))
        self.frame_top.setMaximumSize(QSize(16777215, 65))
        self.frame_top.setStyleSheet(u"background-color: transparent;")
        self.frame_top.setFrameShape(QFrame.NoFrame)
        self.frame_top.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_3 = QHBoxLayout(self.frame_top)
        self.horizontalLayout_3.setSpacing(0)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.frame_toggle = QFrame(self.frame_top)
        self.frame_toggle.setObjectName(u"frame_toggle")
        self.frame_toggle.setMaximumSize(QSize(70, 16777215))
        self.frame_toggle.setStyleSheet(u"background-color: rgb(27, 29, 35);")
        self.frame_toggle.setFrameShape(QFrame.NoFrame)
        self.frame_toggle.setFrameShadow(QFrame.Raised)
        self.verticalLayout_3 = QVBoxLayout(self.frame_toggle)
        self.verticalLayout_3.setSpacing(0)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.btn_toggle_menu = QPushButton(self.frame_toggle)
        self.btn_toggle_menu.setObjectName(u"btn_toggle_menu")
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btn_toggle_menu.sizePolicy().hasHeightForWidth())
        self.btn_toggle_menu.setSizePolicy(sizePolicy)
        self.btn_toggle_menu.setMinimumSize(QSize(70, 0))
        self.btn_toggle_menu.setStyleSheet(u"QPushButton {\n"
"	background-image: url(:/24x24/icons/24x24/cil-menu.png);\n"
"	background-position: center;\n"
"	background-repeat: no-reperat;\n"
"	border: none;\n"
"	background-color: rgb(27, 29, 35);\n"
"}\n"
"QPushButton:hover {\n"
"	background-color: rgb(33, 37, 43);\n"
"}\n"
"QPushButton:pressed {	\n"
"	background-color: rgb(85, 170, 255);\n"
"}")

        self.verticalLayout_3.addWidget(self.btn_toggle_menu)


        self.horizontalLayout_3.addWidget(self.frame_toggle)

        self.frame_top_right = QFrame(self.frame_top)
        self.frame_top_right.setObjectName(u"frame_top_right")
        self.frame_top_right.setStyleSheet(u"background: transparent;")
        self.frame_top_right.setFrameShape(QFrame.NoFrame)
        self.frame_top_right.setFrameShadow(QFrame.Raised)
        self.verticalLayout_2 = QVBoxLayout(self.frame_top_right)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.frame_top_btns = QFrame(self.frame_top_right)
        self.frame_top_btns.setObjectName(u"frame_top_btns")
        self.frame_top_btns.setMaximumSize(QSize(16777215, 42))
        self.frame_top_btns.setStyleSheet(u"background-color: rgba(27, 29, 35, 200)")
        self.frame_top_btns.setFrameShape(QFrame.NoFrame)
        self.frame_top_btns.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_4 = QHBoxLayout(self.frame_top_btns)
        self.horizontalLayout_4.setSpacing(0)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.horizontalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.frame_label_top_btns = QFrame(self.frame_top_btns)
        self.frame_label_top_btns.setObjectName(u"frame_label_top_btns")
        sizePolicy1 = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.frame_label_top_btns.sizePolicy().hasHeightForWidth())
        self.frame_label_top_btns.setSizePolicy(sizePolicy1)
        self.frame_label_top_btns.setMinimumSize(QSize(200, 0))
        self.frame_label_top_btns.setFrameShape(QFrame.NoFrame)
        self.frame_label_top_btns.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_10 = QHBoxLayout(self.frame_label_top_btns)
        self.horizontalLayout_10.setSpacing(0)
        self.horizontalLayout_10.setObjectName(u"horizontalLayout_10")
        self.horizontalLayout_10.setContentsMargins(5, 0, 10, 0)
        self.frame_icon_top_bar = QFrame(self.frame_label_top_btns)
        self.frame_icon_top_bar.setObjectName(u"frame_icon_top_bar")
        sizePolicy1.setHeightForWidth(self.frame_icon_top_bar.sizePolicy().hasHeightForWidth())
        self.frame_icon_top_bar.setSizePolicy(sizePolicy1)
        self.frame_icon_top_bar.setMinimumSize(QSize(30, 0))
        self.frame_icon_top_bar.setMaximumSize(QSize(30, 30))
        self.frame_icon_top_bar.setStyleSheet(u"background: transparent;\n"
"background-image: url(:/16x16/icons/16x16/cil-terminal.png);\n"
"background-position: center;\n"
"background-repeat: no-repeat;\n"
"")
        self.frame_icon_top_bar.setFrameShape(QFrame.StyledPanel)
        self.frame_icon_top_bar.setFrameShadow(QFrame.Raised)

        self.horizontalLayout_10.addWidget(self.frame_icon_top_bar)

        self.label_title_bar_top = QLabel(self.frame_label_top_btns)
        self.label_title_bar_top.setObjectName(u"label_title_bar_top")
        sizePolicy1.setHeightForWidth(self.label_title_bar_top.sizePolicy().hasHeightForWidth())
        self.label_title_bar_top.setSizePolicy(sizePolicy1)
        self.label_title_bar_top.setMinimumSize(QSize(500, 0))
        font1 = QFont()
        font1.setFamily(u"Segoe UI")
        font1.setPointSize(10)
        font1.setBold(True)
        font1.setWeight(75)
        self.label_title_bar_top.setFont(font1)
        self.label_title_bar_top.setStyleSheet(u"background: transparent;\n"
"")

        self.horizontalLayout_10.addWidget(self.label_title_bar_top)

        self.frame_CBSMplToolBar = QFrame(self.frame_label_top_btns)
        self.frame_CBSMplToolBar.setObjectName(u"frame_CBSMplToolBar")
        sizePolicy1.setHeightForWidth(self.frame_CBSMplToolBar.sizePolicy().hasHeightForWidth())
        self.frame_CBSMplToolBar.setSizePolicy(sizePolicy1)
        self.frame_CBSMplToolBar.setMinimumSize(QSize(200, 0))
        self.frame_CBSMplToolBar.setStyleSheet(u"background-color: transparent;")
        self.frame_CBSMplToolBar.setFrameShape(QFrame.StyledPanel)
        self.frame_CBSMplToolBar.setFrameShadow(QFrame.Raised)
        self.lineEdit_AtTop = QLineEdit(self.frame_CBSMplToolBar)
        self.lineEdit_AtTop.setObjectName(u"lineEdit_AtTop")
        self.lineEdit_AtTop.setGeometry(QRect(40, 10, 113, 20))

        self.horizontalLayout_10.addWidget(self.frame_CBSMplToolBar)


        self.horizontalLayout_4.addWidget(self.frame_label_top_btns)

        self.verticalLayout_CBSMplToolBar = QVBoxLayout()
        self.verticalLayout_CBSMplToolBar.setSpacing(0)
        self.verticalLayout_CBSMplToolBar.setObjectName(u"verticalLayout_CBSMplToolBar")
        self.verticalLayout_CBSMplToolBar.setSizeConstraint(QLayout.SetDefaultConstraint)
        self.verticalLayout_CBSMplToolBar.setContentsMargins(-1, 0, 10, 0)
        self.horizontalLayout_CBSMplToolBar = QHBoxLayout()
        self.horizontalLayout_CBSMplToolBar.setSpacing(0)
        self.horizontalLayout_CBSMplToolBar.setObjectName(u"horizontalLayout_CBSMplToolBar")
        self.horizontalLayout_CBSMplToolBar.setSizeConstraint(QLayout.SetFixedSize)
        self.pushButton_ShowFloatingConsole_AtTop = QPushButton(self.frame_top_btns)
        self.pushButton_ShowFloatingConsole_AtTop.setObjectName(u"pushButton_ShowFloatingConsole_AtTop")
        sizePolicy2 = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Expanding)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.pushButton_ShowFloatingConsole_AtTop.sizePolicy().hasHeightForWidth())
        self.pushButton_ShowFloatingConsole_AtTop.setSizePolicy(sizePolicy2)
        font2 = QFont()
        font2.setFamily(u"Segoe UI")
        font2.setBold(True)
        font2.setWeight(75)
        self.pushButton_ShowFloatingConsole_AtTop.setFont(font2)
        self.pushButton_ShowFloatingConsole_AtTop.setLayoutDirection(Qt.LeftToRight)
        self.pushButton_ShowFloatingConsole_AtTop.setStyleSheet(u"QPushButton {\n"
"	border: 2px solid rgb(52, 59, 72);\n"
"	border-radius: 5px;	\n"
"	background-color: rgb(52, 59, 72);\n"
"}\n"
"QPushButton:hover {\n"
"	background-color: rgb(57, 65, 80);\n"
"	border: 2px solid rgb(61, 70, 86);\n"
"}\n"
"QPushButton:pressed {	\n"
"	background-color: rgb(35, 40, 49);\n"
"	border: 2px solid rgb(43, 50, 61);\n"
"}")

        self.horizontalLayout_CBSMplToolBar.addWidget(self.pushButton_ShowFloatingConsole_AtTop)

        self.pushButton_runPyBasedSimulation_AtTop = QPushButton(self.frame_top_btns)
        self.pushButton_runPyBasedSimulation_AtTop.setObjectName(u"pushButton_runPyBasedSimulation_AtTop")
        sizePolicy2.setHeightForWidth(self.pushButton_runPyBasedSimulation_AtTop.sizePolicy().hasHeightForWidth())
        self.pushButton_runPyBasedSimulation_AtTop.setSizePolicy(sizePolicy2)
        self.pushButton_runPyBasedSimulation_AtTop.setFont(font2)
        self.pushButton_runPyBasedSimulation_AtTop.setLayoutDirection(Qt.LeftToRight)
        self.pushButton_runPyBasedSimulation_AtTop.setStyleSheet(u"QPushButton {\n"
"	border: 2px solid rgb(52, 59, 72);\n"
"	border-radius: 5px;	\n"
"	background-color: rgb(82, 89, 102);\n"
"}\n"
"QPushButton:hover {\n"
"	background-color: rgb(57, 65, 80);\n"
"	border: 2px solid rgb(61, 70, 86);\n"
"}\n"
"QPushButton:pressed {	\n"
"	background-color: rgb(35, 40, 49);\n"
"	border: 2px solid rgb(43, 50, 61);\n"
"}")

        self.horizontalLayout_CBSMplToolBar.addWidget(self.pushButton_runPyBasedSimulation_AtTop)

        self.pushButton_SaveAtTop = QPushButton(self.frame_top_btns)
        self.pushButton_SaveAtTop.setObjectName(u"pushButton_SaveAtTop")
        sizePolicy2.setHeightForWidth(self.pushButton_SaveAtTop.sizePolicy().hasHeightForWidth())
        self.pushButton_SaveAtTop.setSizePolicy(sizePolicy2)
        self.pushButton_SaveAtTop.setFont(font2)
        self.pushButton_SaveAtTop.setLayoutDirection(Qt.LeftToRight)
        self.pushButton_SaveAtTop.setStyleSheet(u"QPushButton {\n"
"	border: 2px solid rgb(52, 59, 72);\n"
"	border-radius: 5px;	\n"
"	background-color: rgb(52, 59, 72);\n"
"}\n"
"QPushButton:hover {\n"
"	background-color: rgb(57, 65, 80);\n"
"	border: 2px solid rgb(61, 70, 86);\n"
"}\n"
"QPushButton:pressed {	\n"
"	background-color: rgb(35, 40, 49);\n"
"	border: 2px solid rgb(43, 50, 61);\n"
"}")

        self.horizontalLayout_CBSMplToolBar.addWidget(self.pushButton_SaveAtTop)

        self.pushButton_runCBasedSimulation_AtTop = QPushButton(self.frame_top_btns)
        self.pushButton_runCBasedSimulation_AtTop.setObjectName(u"pushButton_runCBasedSimulation_AtTop")
        sizePolicy2.setHeightForWidth(self.pushButton_runCBasedSimulation_AtTop.sizePolicy().hasHeightForWidth())
        self.pushButton_runCBasedSimulation_AtTop.setSizePolicy(sizePolicy2)
        self.pushButton_runCBasedSimulation_AtTop.setFont(font2)
        self.pushButton_runCBasedSimulation_AtTop.setLayoutDirection(Qt.LeftToRight)
        self.pushButton_runCBasedSimulation_AtTop.setStyleSheet(u"QPushButton {\n"
"	border: 2px solid rgb(52, 59, 72);\n"
"	border-radius: 5px;	\n"
"	background-color: rgb(82, 89, 102);\n"
"}\n"
"QPushButton:hover {\n"
"	background-color: rgb(57, 65, 80);\n"
"	border: 2px solid rgb(61, 70, 86);\n"
"}\n"
"QPushButton:pressed {	\n"
"	background-color: rgb(35, 40, 49);\n"
"	border: 2px solid rgb(43, 50, 61);\n"
"}")

        self.horizontalLayout_CBSMplToolBar.addWidget(self.pushButton_runCBasedSimulation_AtTop)

        self.pushButton_ACMPlotHereAtTop = QPushButton(self.frame_top_btns)
        self.pushButton_ACMPlotHereAtTop.setObjectName(u"pushButton_ACMPlotHereAtTop")
        sizePolicy2.setHeightForWidth(self.pushButton_ACMPlotHereAtTop.sizePolicy().hasHeightForWidth())
        self.pushButton_ACMPlotHereAtTop.setSizePolicy(sizePolicy2)
        self.pushButton_ACMPlotHereAtTop.setFont(font2)
        self.pushButton_ACMPlotHereAtTop.setLayoutDirection(Qt.LeftToRight)
        self.pushButton_ACMPlotHereAtTop.setStyleSheet(u"QPushButton {\n"
"	border: 2px solid rgb(52, 59, 72);\n"
"	border-radius: 5px;	\n"
"	background-color: rgb(52, 59, 72);\n"
"}\n"
"QPushButton:hover {\n"
"	background-color: rgb(57, 65, 80);\n"
"	border: 2px solid rgb(61, 70, 86);\n"
"}\n"
"QPushButton:pressed {	\n"
"	background-color: rgb(35, 40, 49);\n"
"	border: 2px solid rgb(43, 50, 61);\n"
"}")

        self.horizontalLayout_CBSMplToolBar.addWidget(self.pushButton_ACMPlotHereAtTop)


        self.verticalLayout_CBSMplToolBar.addLayout(self.horizontalLayout_CBSMplToolBar)


        self.horizontalLayout_4.addLayout(self.verticalLayout_CBSMplToolBar)

        self.frame_btns_right = QFrame(self.frame_top_btns)
        self.frame_btns_right.setObjectName(u"frame_btns_right")
        sizePolicy3 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.frame_btns_right.sizePolicy().hasHeightForWidth())
        self.frame_btns_right.setSizePolicy(sizePolicy3)
        self.frame_btns_right.setMaximumSize(QSize(120, 16777215))
        self.frame_btns_right.setFrameShape(QFrame.NoFrame)
        self.frame_btns_right.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_5 = QHBoxLayout(self.frame_btns_right)
        self.horizontalLayout_5.setSpacing(0)
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.horizontalLayout_5.setContentsMargins(0, 0, 0, 0)
        self.btn_minimize = QPushButton(self.frame_btns_right)
        self.btn_minimize.setObjectName(u"btn_minimize")
        sizePolicy2.setHeightForWidth(self.btn_minimize.sizePolicy().hasHeightForWidth())
        self.btn_minimize.setSizePolicy(sizePolicy2)
        self.btn_minimize.setMinimumSize(QSize(40, 0))
        self.btn_minimize.setMaximumSize(QSize(40, 16777215))
        self.btn_minimize.setStyleSheet(u"QPushButton {	\n"
"	border: none;\n"
"	background-color: transparent;\n"
"}\n"
"QPushButton:hover {\n"
"	background-color: rgb(52, 59, 72);\n"
"}\n"
"QPushButton:pressed {	\n"
"	background-color: rgb(85, 170, 255);\n"
"}")
        icon = QIcon()
        icon.addFile(u":/16x16/icons/16x16/cil-window-minimize.png", QSize(), QIcon.Normal, QIcon.Off)
        self.btn_minimize.setIcon(icon)

        self.horizontalLayout_5.addWidget(self.btn_minimize)

        self.btn_maximize_restore = QPushButton(self.frame_btns_right)
        self.btn_maximize_restore.setObjectName(u"btn_maximize_restore")
        sizePolicy2.setHeightForWidth(self.btn_maximize_restore.sizePolicy().hasHeightForWidth())
        self.btn_maximize_restore.setSizePolicy(sizePolicy2)
        self.btn_maximize_restore.setMinimumSize(QSize(40, 0))
        self.btn_maximize_restore.setMaximumSize(QSize(40, 16777215))
        self.btn_maximize_restore.setStyleSheet(u"QPushButton {	\n"
"	border: none;\n"
"	background-color: transparent;\n"
"}\n"
"QPushButton:hover {\n"
"	background-color: rgb(52, 59, 72);\n"
"}\n"
"QPushButton:pressed {	\n"
"	background-color: rgb(85, 170, 255);\n"
"}")
        icon1 = QIcon()
        icon1.addFile(u":/16x16/icons/16x16/cil-window-maximize.png", QSize(), QIcon.Normal, QIcon.Off)
        self.btn_maximize_restore.setIcon(icon1)

        self.horizontalLayout_5.addWidget(self.btn_maximize_restore)

        self.btn_close = QPushButton(self.frame_btns_right)
        self.btn_close.setObjectName(u"btn_close")
        sizePolicy2.setHeightForWidth(self.btn_close.sizePolicy().hasHeightForWidth())
        self.btn_close.setSizePolicy(sizePolicy2)
        self.btn_close.setMinimumSize(QSize(40, 0))
        self.btn_close.setMaximumSize(QSize(40, 16777215))
        self.btn_close.setStyleSheet(u"QPushButton {	\n"
"	border: none;\n"
"	background-color: transparent;\n"
"}\n"
"QPushButton:hover {\n"
"	background-color: rgb(52, 59, 72);\n"
"}\n"
"QPushButton:pressed {	\n"
"	background-color: rgb(85, 170, 255);\n"
"}")
        icon2 = QIcon()
        icon2.addFile(u":/16x16/icons/16x16/cil-x.png", QSize(), QIcon.Normal, QIcon.Off)
        self.btn_close.setIcon(icon2)

        self.horizontalLayout_5.addWidget(self.btn_close)


        self.horizontalLayout_4.addWidget(self.frame_btns_right)


        self.verticalLayout_2.addWidget(self.frame_top_btns)

        self.frame_top_info = QFrame(self.frame_top_right)
        self.frame_top_info.setObjectName(u"frame_top_info")
        self.frame_top_info.setMaximumSize(QSize(16777215, 65))
        self.frame_top_info.setStyleSheet(u"background-color: rgb(39, 44, 54);")
        self.frame_top_info.setFrameShape(QFrame.NoFrame)
        self.frame_top_info.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_8 = QHBoxLayout(self.frame_top_info)
        self.horizontalLayout_8.setSpacing(0)
        self.horizontalLayout_8.setObjectName(u"horizontalLayout_8")
        self.horizontalLayout_8.setContentsMargins(10, 0, 10, 0)
        self.label_top_info_1 = QLabel(self.frame_top_info)
        self.label_top_info_1.setObjectName(u"label_top_info_1")
        self.label_top_info_1.setMaximumSize(QSize(16777215, 15))
        font3 = QFont()
        font3.setFamily(u"Segoe UI")
        self.label_top_info_1.setFont(font3)
        self.label_top_info_1.setStyleSheet(u"color: rgb(98, 103, 111); ")

        self.horizontalLayout_8.addWidget(self.label_top_info_1)

        self.label_top_info_2 = QLabel(self.frame_top_info)
        self.label_top_info_2.setObjectName(u"label_top_info_2")
        self.label_top_info_2.setMinimumSize(QSize(0, 0))
        self.label_top_info_2.setMaximumSize(QSize(250, 20))
        self.label_top_info_2.setFont(font2)
        self.label_top_info_2.setStyleSheet(u"color: rgb(98, 103, 111);")
        self.label_top_info_2.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.horizontalLayout_8.addWidget(self.label_top_info_2)


        self.verticalLayout_2.addWidget(self.frame_top_info)


        self.horizontalLayout_3.addWidget(self.frame_top_right)


        self.verticalLayout.addWidget(self.frame_top)

        self.frame_center = QFrame(self.frame_main)
        self.frame_center.setObjectName(u"frame_center")
        sizePolicy.setHeightForWidth(self.frame_center.sizePolicy().hasHeightForWidth())
        self.frame_center.setSizePolicy(sizePolicy)
        self.frame_center.setStyleSheet(u"background-color: rgb(40, 44, 52);")
        self.frame_center.setFrameShape(QFrame.NoFrame)
        self.frame_center.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_2 = QHBoxLayout(self.frame_center)
        self.horizontalLayout_2.setSpacing(0)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.frame_left_menu = QFrame(self.frame_center)
        self.frame_left_menu.setObjectName(u"frame_left_menu")
        sizePolicy4 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy4.setHorizontalStretch(0)
        sizePolicy4.setVerticalStretch(0)
        sizePolicy4.setHeightForWidth(self.frame_left_menu.sizePolicy().hasHeightForWidth())
        self.frame_left_menu.setSizePolicy(sizePolicy4)
        self.frame_left_menu.setMinimumSize(QSize(70, 0))
        self.frame_left_menu.setMaximumSize(QSize(70, 16777215))
        self.frame_left_menu.setLayoutDirection(Qt.LeftToRight)
        self.frame_left_menu.setStyleSheet(u"background-color: rgb(27, 29, 35);")
        self.frame_left_menu.setFrameShape(QFrame.NoFrame)
        self.frame_left_menu.setFrameShadow(QFrame.Raised)
        self.verticalLayout_5 = QVBoxLayout(self.frame_left_menu)
        self.verticalLayout_5.setSpacing(1)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.verticalLayout_5.setContentsMargins(0, 0, 0, 0)
        self.frame_menus = QFrame(self.frame_left_menu)
        self.frame_menus.setObjectName(u"frame_menus")
        self.frame_menus.setFrameShape(QFrame.NoFrame)
        self.frame_menus.setFrameShadow(QFrame.Raised)
        self.layout_menus = QVBoxLayout(self.frame_menus)
        self.layout_menus.setSpacing(0)
        self.layout_menus.setObjectName(u"layout_menus")
        self.layout_menus.setContentsMargins(0, 0, 0, 0)

        self.verticalLayout_5.addWidget(self.frame_menus, 0, Qt.AlignTop)

        self.frame_extra_menus = QFrame(self.frame_left_menu)
        self.frame_extra_menus.setObjectName(u"frame_extra_menus")
        sizePolicy4.setHeightForWidth(self.frame_extra_menus.sizePolicy().hasHeightForWidth())
        self.frame_extra_menus.setSizePolicy(sizePolicy4)
        self.frame_extra_menus.setFrameShape(QFrame.NoFrame)
        self.frame_extra_menus.setFrameShadow(QFrame.Raised)
        self.layout_menu_bottom = QVBoxLayout(self.frame_extra_menus)
        self.layout_menu_bottom.setSpacing(10)
        self.layout_menu_bottom.setObjectName(u"layout_menu_bottom")
        self.layout_menu_bottom.setContentsMargins(0, 0, 0, 25)
        self.label_user_icon = QLabel(self.frame_extra_menus)
        self.label_user_icon.setObjectName(u"label_user_icon")
        sizePolicy5 = QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        sizePolicy5.setHorizontalStretch(0)
        sizePolicy5.setVerticalStretch(0)
        sizePolicy5.setHeightForWidth(self.label_user_icon.sizePolicy().hasHeightForWidth())
        self.label_user_icon.setSizePolicy(sizePolicy5)
        self.label_user_icon.setMinimumSize(QSize(60, 60))
        self.label_user_icon.setMaximumSize(QSize(60, 60))
        font4 = QFont()
        font4.setFamily(u"Segoe UI")
        font4.setPointSize(12)
        self.label_user_icon.setFont(font4)
        self.label_user_icon.setStyleSheet(u"QLabel {\n"
"	border-radius: 30px;\n"
"	background-color: rgb(44, 49, 60);\n"
"	border: 5px solid rgb(39, 44, 54);\n"
"	background-position: center;\n"
"	background-repeat: no-repeat;\n"
"}")
        self.label_user_icon.setAlignment(Qt.AlignCenter)

        self.layout_menu_bottom.addWidget(self.label_user_icon, 0, Qt.AlignHCenter)


        self.verticalLayout_5.addWidget(self.frame_extra_menus, 0, Qt.AlignBottom)


        self.horizontalLayout_2.addWidget(self.frame_left_menu)

        self.frame_content_right = QFrame(self.frame_center)
        self.frame_content_right.setObjectName(u"frame_content_right")
        self.frame_content_right.setStyleSheet(u"background-color: rgb(44, 49, 60);")
        self.frame_content_right.setFrameShape(QFrame.NoFrame)
        self.frame_content_right.setFrameShadow(QFrame.Raised)
        self.verticalLayout_4 = QVBoxLayout(self.frame_content_right)
        self.verticalLayout_4.setSpacing(0)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.verticalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.frame_content = QFrame(self.frame_content_right)
        self.frame_content.setObjectName(u"frame_content")
        self.frame_content.setFrameShape(QFrame.NoFrame)
        self.frame_content.setFrameShadow(QFrame.Raised)
        self.frame_content.setLineWidth(1)
        self.verticalLayout_9 = QVBoxLayout(self.frame_content)
        self.verticalLayout_9.setSpacing(0)
        self.verticalLayout_9.setObjectName(u"verticalLayout_9")
        self.verticalLayout_9.setContentsMargins(0, 0, 0, 0)
        self.stackedWidget = QStackedWidget(self.frame_content)
        self.stackedWidget.setObjectName(u"stackedWidget")
        self.stackedWidget.setStyleSheet(u"background: transparent;")
        self.page_home = QWidget()
        self.page_home.setObjectName(u"page_home")
        self.verticalLayout_10 = QVBoxLayout(self.page_home)
        self.verticalLayout_10.setObjectName(u"verticalLayout_10")
        self.label_6 = QLabel(self.page_home)
        self.label_6.setObjectName(u"label_6")
        font5 = QFont()
        font5.setFamily(u"Segoe UI")
        font5.setPointSize(40)
        self.label_6.setFont(font5)
        self.label_6.setCursor(QCursor(Qt.ArrowCursor))
        self.label_6.setStyleSheet(u"")
        self.label_6.setAlignment(Qt.AlignCenter)

        self.verticalLayout_10.addWidget(self.label_6)

        self.label_2 = QLabel(self.page_home)
        self.label_2.setObjectName(u"label_2")
        font6 = QFont()
        font6.setFamily(u"Segoe UI")
        font6.setPointSize(24)
        self.label_2.setFont(font6)
        self.label_2.setAlignment(Qt.AlignCenter)

        self.verticalLayout_10.addWidget(self.label_2)

        self.label = QLabel(self.page_home)
        self.label.setObjectName(u"label")
        font7 = QFont()
        font7.setFamily(u"Segoe UI")
        font7.setPointSize(20)
        self.label.setFont(font7)
        self.label.setAlignment(Qt.AlignCenter)

        self.verticalLayout_10.addWidget(self.label)

        self.label_7 = QLabel(self.page_home)
        self.label_7.setObjectName(u"label_7")
        font8 = QFont()
        font8.setFamily(u"Segoe UI")
        font8.setPointSize(15)
        self.label_7.setFont(font8)
        self.label_7.setAlignment(Qt.AlignCenter)

        self.verticalLayout_10.addWidget(self.label_7)

        self.stackedWidget.addWidget(self.page_home)
        self.page_widgets = QWidget()
        self.page_widgets.setObjectName(u"page_widgets")
        self.verticalLayout_6 = QVBoxLayout(self.page_widgets)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.frame = QFrame(self.page_widgets)
        self.frame.setObjectName(u"frame")
        self.frame.setStyleSheet(u"border-radius: 5px;")
        self.frame.setFrameShape(QFrame.StyledPanel)
        self.frame.setFrameShadow(QFrame.Raised)
        self.verticalLayout_15 = QVBoxLayout(self.frame)
        self.verticalLayout_15.setSpacing(0)
        self.verticalLayout_15.setObjectName(u"verticalLayout_15")
        self.verticalLayout_15.setContentsMargins(0, 0, 0, 0)
        self.frame_div_content_1 = QFrame(self.frame)
        self.frame_div_content_1.setObjectName(u"frame_div_content_1")
        self.frame_div_content_1.setMinimumSize(QSize(0, 110))
        self.frame_div_content_1.setMaximumSize(QSize(16777215, 110))
        self.frame_div_content_1.setStyleSheet(u"background-color: rgb(41, 45, 56);\n"
"border-radius: 5px;\n"
"")
        self.frame_div_content_1.setFrameShape(QFrame.NoFrame)
        self.frame_div_content_1.setFrameShadow(QFrame.Raised)
        self.verticalLayout_7 = QVBoxLayout(self.frame_div_content_1)
        self.verticalLayout_7.setSpacing(0)
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.verticalLayout_7.setContentsMargins(0, 0, 0, 0)
        self.frame_title_wid_1 = QFrame(self.frame_div_content_1)
        self.frame_title_wid_1.setObjectName(u"frame_title_wid_1")
        self.frame_title_wid_1.setMaximumSize(QSize(16777215, 35))
        self.frame_title_wid_1.setStyleSheet(u"background-color: rgb(39, 44, 54);")
        self.frame_title_wid_1.setFrameShape(QFrame.StyledPanel)
        self.frame_title_wid_1.setFrameShadow(QFrame.Raised)
        self.verticalLayout_8 = QVBoxLayout(self.frame_title_wid_1)
        self.verticalLayout_8.setObjectName(u"verticalLayout_8")
        self.labelBoxBlenderInstalation = QLabel(self.frame_title_wid_1)
        self.labelBoxBlenderInstalation.setObjectName(u"labelBoxBlenderInstalation")
        self.labelBoxBlenderInstalation.setFont(font1)
        self.labelBoxBlenderInstalation.setStyleSheet(u"")

        self.verticalLayout_8.addWidget(self.labelBoxBlenderInstalation)


        self.verticalLayout_7.addWidget(self.frame_title_wid_1)

        self.frame_content_wid_1 = QFrame(self.frame_div_content_1)
        self.frame_content_wid_1.setObjectName(u"frame_content_wid_1")
        self.frame_content_wid_1.setFrameShape(QFrame.NoFrame)
        self.frame_content_wid_1.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_9 = QHBoxLayout(self.frame_content_wid_1)
        self.horizontalLayout_9.setObjectName(u"horizontalLayout_9")
        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setContentsMargins(-1, -1, -1, 0)
        self.lineEdit = QLineEdit(self.frame_content_wid_1)
        self.lineEdit.setObjectName(u"lineEdit")
        self.lineEdit.setMinimumSize(QSize(0, 30))
        self.lineEdit.setStyleSheet(u"QLineEdit {\n"
"	background-color: rgb(27, 29, 35);\n"
"	border-radius: 5px;\n"
"	border: 2px solid rgb(27, 29, 35);\n"
"	padding-left: 10px;\n"
"}\n"
"QLineEdit:hover {\n"
"	border: 2px solid rgb(64, 71, 88);\n"
"}\n"
"QLineEdit:focus {\n"
"	border: 2px solid rgb(91, 101, 124);\n"
"}")

        self.gridLayout.addWidget(self.lineEdit, 0, 0, 1, 1)

        self.pushButton = QPushButton(self.frame_content_wid_1)
        self.pushButton.setObjectName(u"pushButton")
        self.pushButton.setMinimumSize(QSize(150, 30))
        font9 = QFont()
        font9.setFamily(u"Segoe UI")
        font9.setPointSize(9)
        self.pushButton.setFont(font9)
        self.pushButton.setStyleSheet(u"QPushButton {\n"
"	border: 2px solid rgb(52, 59, 72);\n"
"	border-radius: 5px;	\n"
"	background-color: rgb(52, 59, 72);\n"
"}\n"
"QPushButton:hover {\n"
"	background-color: rgb(57, 65, 80);\n"
"	border: 2px solid rgb(61, 70, 86);\n"
"}\n"
"QPushButton:pressed {	\n"
"	background-color: rgb(35, 40, 49);\n"
"	border: 2px solid rgb(43, 50, 61);\n"
"}")
        icon3 = QIcon()
        icon3.addFile(u":/16x16/icons/16x16/cil-folder-open.png", QSize(), QIcon.Normal, QIcon.Off)
        self.pushButton.setIcon(icon3)

        self.gridLayout.addWidget(self.pushButton, 0, 1, 1, 1)

        self.labelVersion_3 = QLabel(self.frame_content_wid_1)
        self.labelVersion_3.setObjectName(u"labelVersion_3")
        self.labelVersion_3.setStyleSheet(u"color: rgb(98, 103, 111);")
        self.labelVersion_3.setLineWidth(1)
        self.labelVersion_3.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)

        self.gridLayout.addWidget(self.labelVersion_3, 1, 0, 1, 2)


        self.horizontalLayout_9.addLayout(self.gridLayout)


        self.verticalLayout_7.addWidget(self.frame_content_wid_1)


        self.verticalLayout_15.addWidget(self.frame_div_content_1)


        self.verticalLayout_6.addWidget(self.frame)

        self.frame_2 = QFrame(self.page_widgets)
        self.frame_2.setObjectName(u"frame_2")
        self.frame_2.setMinimumSize(QSize(0, 150))
        self.frame_2.setStyleSheet(u"background-color: rgb(39, 44, 54);\n"
"border-radius: 5px;")
        self.frame_2.setFrameShape(QFrame.StyledPanel)
        self.frame_2.setFrameShadow(QFrame.Raised)
        self.verticalLayout_11 = QVBoxLayout(self.frame_2)
        self.verticalLayout_11.setObjectName(u"verticalLayout_11")
        self.gridLayout_2 = QGridLayout()
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.checkBox = QCheckBox(self.frame_2)
        self.checkBox.setObjectName(u"checkBox")
        self.checkBox.setAutoFillBackground(False)
        self.checkBox.setStyleSheet(u"")

        self.gridLayout_2.addWidget(self.checkBox, 0, 0, 1, 1)

        self.radioButton = QRadioButton(self.frame_2)
        self.radioButton.setObjectName(u"radioButton")
        self.radioButton.setStyleSheet(u"")

        self.gridLayout_2.addWidget(self.radioButton, 0, 1, 1, 1)

        self.verticalSlider = QSlider(self.frame_2)
        self.verticalSlider.setObjectName(u"verticalSlider")
        self.verticalSlider.setStyleSheet(u"")
        self.verticalSlider.setOrientation(Qt.Vertical)

        self.gridLayout_2.addWidget(self.verticalSlider, 0, 2, 3, 1)

        self.verticalScrollBar = QScrollBar(self.frame_2)
        self.verticalScrollBar.setObjectName(u"verticalScrollBar")
        self.verticalScrollBar.setStyleSheet(u" QScrollBar:vertical {\n"
"	border: none;\n"
"    background: rgb(52, 59, 72);\n"
"    width: 14px;\n"
"    margin: 21px 0 21px 0;\n"
"	border-radius: 0px;\n"
" }")
        self.verticalScrollBar.setOrientation(Qt.Vertical)

        self.gridLayout_2.addWidget(self.verticalScrollBar, 0, 4, 3, 1)

        self.scrollArea_2 = QScrollArea(self.frame_2)
        self.scrollArea_2.setObjectName(u"scrollArea_2")
        self.scrollArea_2.setStyleSheet(u"QScrollArea {\n"
"	border: none;\n"
"	border-radius: 0px;\n"
"}\n"
"QScrollBar:horizontal {\n"
"    border: none;\n"
"    background: rgb(52, 59, 72);\n"
"    height: 14px;\n"
"    margin: 0px 21px 0 21px;\n"
"	border-radius: 0px;\n"
"}\n"
" QScrollBar:vertical {\n"
"	border: none;\n"
"    background: rgb(52, 59, 72);\n"
"    width: 14px;\n"
"    margin: 21px 0 21px 0;\n"
"	border-radius: 0px;\n"
" }\n"
"")
        self.scrollArea_2.setFrameShape(QFrame.NoFrame)
        self.scrollArea_2.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scrollArea_2.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scrollArea_2.setWidgetResizable(True)
        self.scrollAreaWidgetContents_2 = QWidget()
        self.scrollAreaWidgetContents_2.setObjectName(u"scrollAreaWidgetContents_2")
        self.scrollAreaWidgetContents_2.setGeometry(QRect(0, 0, 218, 218))
        self.horizontalLayout_11 = QHBoxLayout(self.scrollAreaWidgetContents_2)
        self.horizontalLayout_11.setObjectName(u"horizontalLayout_11")
        self.plainTextEdit = QPlainTextEdit(self.scrollAreaWidgetContents_2)
        self.plainTextEdit.setObjectName(u"plainTextEdit")
        self.plainTextEdit.setMinimumSize(QSize(200, 200))
        self.plainTextEdit.setStyleSheet(u"QPlainTextEdit {\n"
"	background-color: rgb(27, 29, 35);\n"
"	border-radius: 5px;\n"
"	padding: 10px;\n"
"}\n"
"QPlainTextEdit:hover {\n"
"	border: 2px solid rgb(64, 71, 88);\n"
"}\n"
"QPlainTextEdit:focus {\n"
"	border: 2px solid rgb(91, 101, 124);\n"
"}")

        self.horizontalLayout_11.addWidget(self.plainTextEdit)

        self.scrollArea_2.setWidget(self.scrollAreaWidgetContents_2)

        self.gridLayout_2.addWidget(self.scrollArea_2, 0, 5, 3, 1)

        self.comboBox = QComboBox(self.frame_2)
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.setObjectName(u"comboBox")
        self.comboBox.setFont(font9)
        self.comboBox.setAutoFillBackground(False)
        self.comboBox.setStyleSheet(u"QComboBox{\n"
"	background-color: rgb(27, 29, 35);\n"
"	border-radius: 5px;\n"
"	border: 2px solid rgb(27, 29, 35);\n"
"	padding: 5px;\n"
"	padding-left: 10px;\n"
"}\n"
"QComboBox:hover{\n"
"	border: 2px solid rgb(64, 71, 88);\n"
"}\n"
"QComboBox QAbstractItemView {\n"
"	color: rgb(85, 170, 255);	\n"
"	background-color: rgb(27, 29, 35);\n"
"	padding: 10px;\n"
"	selection-background-color: rgb(39, 44, 54);\n"
"}")
        self.comboBox.setIconSize(QSize(16, 16))
        self.comboBox.setFrame(True)

        self.gridLayout_2.addWidget(self.comboBox, 1, 0, 1, 2)

        self.horizontalScrollBar = QScrollBar(self.frame_2)
        self.horizontalScrollBar.setObjectName(u"horizontalScrollBar")
        sizePolicy6 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        sizePolicy6.setHorizontalStretch(0)
        sizePolicy6.setVerticalStretch(0)
        sizePolicy6.setHeightForWidth(self.horizontalScrollBar.sizePolicy().hasHeightForWidth())
        self.horizontalScrollBar.setSizePolicy(sizePolicy6)
        self.horizontalScrollBar.setStyleSheet(u"QScrollBar:horizontal {\n"
"    border: none;\n"
"    background: rgb(52, 59, 72);\n"
"    height: 14px;\n"
"    margin: 0px 21px 0 21px;\n"
"	border-radius: 0px;\n"
"}\n"
"")
        self.horizontalScrollBar.setOrientation(Qt.Horizontal)

        self.gridLayout_2.addWidget(self.horizontalScrollBar, 1, 3, 1, 1)

        self.commandLinkButton = QCommandLinkButton(self.frame_2)
        self.commandLinkButton.setObjectName(u"commandLinkButton")
        self.commandLinkButton.setStyleSheet(u"QCommandLinkButton {	\n"
"	color: rgb(85, 170, 255);\n"
"	border-radius: 5px;\n"
"	padding: 5px;\n"
"}\n"
"QCommandLinkButton:hover {	\n"
"	color: rgb(210, 210, 210);\n"
"	background-color: rgb(44, 49, 60);\n"
"}\n"
"QCommandLinkButton:pressed {	\n"
"	color: rgb(210, 210, 210);\n"
"	background-color: rgb(52, 58, 71);\n"
"}")
        icon4 = QIcon()
        icon4.addFile(u":/16x16/icons/16x16/cil-link.png", QSize(), QIcon.Normal, QIcon.Off)
        self.commandLinkButton.setIcon(icon4)

        self.gridLayout_2.addWidget(self.commandLinkButton, 1, 6, 1, 1)

        self.horizontalSlider = QSlider(self.frame_2)
        self.horizontalSlider.setObjectName(u"horizontalSlider")
        self.horizontalSlider.setStyleSheet(u"")
        self.horizontalSlider.setOrientation(Qt.Horizontal)

        self.gridLayout_2.addWidget(self.horizontalSlider, 2, 0, 1, 2)


        self.verticalLayout_11.addLayout(self.gridLayout_2)


        self.verticalLayout_6.addWidget(self.frame_2)

        self.frame_3 = QFrame(self.page_widgets)
        self.frame_3.setObjectName(u"frame_3")
        self.frame_3.setMinimumSize(QSize(0, 150))
        self.frame_3.setFrameShape(QFrame.StyledPanel)
        self.frame_3.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_12 = QHBoxLayout(self.frame_3)
        self.horizontalLayout_12.setSpacing(0)
        self.horizontalLayout_12.setObjectName(u"horizontalLayout_12")
        self.horizontalLayout_12.setContentsMargins(0, 0, 0, 0)
        self.tableWidget = QTableWidget(self.frame_3)
        if (self.tableWidget.columnCount() < 4):
            self.tableWidget.setColumnCount(4)
        __qtablewidgetitem = QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(0, __qtablewidgetitem)
        __qtablewidgetitem1 = QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(1, __qtablewidgetitem1)
        __qtablewidgetitem2 = QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(2, __qtablewidgetitem2)
        __qtablewidgetitem3 = QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(3, __qtablewidgetitem3)
        if (self.tableWidget.rowCount() < 16):
            self.tableWidget.setRowCount(16)
        __qtablewidgetitem4 = QTableWidgetItem()
        __qtablewidgetitem4.setFont(font3);
        self.tableWidget.setVerticalHeaderItem(0, __qtablewidgetitem4)
        __qtablewidgetitem5 = QTableWidgetItem()
        self.tableWidget.setVerticalHeaderItem(1, __qtablewidgetitem5)
        __qtablewidgetitem6 = QTableWidgetItem()
        self.tableWidget.setVerticalHeaderItem(2, __qtablewidgetitem6)
        __qtablewidgetitem7 = QTableWidgetItem()
        self.tableWidget.setVerticalHeaderItem(3, __qtablewidgetitem7)
        __qtablewidgetitem8 = QTableWidgetItem()
        self.tableWidget.setVerticalHeaderItem(4, __qtablewidgetitem8)
        __qtablewidgetitem9 = QTableWidgetItem()
        self.tableWidget.setVerticalHeaderItem(5, __qtablewidgetitem9)
        __qtablewidgetitem10 = QTableWidgetItem()
        self.tableWidget.setVerticalHeaderItem(6, __qtablewidgetitem10)
        __qtablewidgetitem11 = QTableWidgetItem()
        self.tableWidget.setVerticalHeaderItem(7, __qtablewidgetitem11)
        __qtablewidgetitem12 = QTableWidgetItem()
        self.tableWidget.setVerticalHeaderItem(8, __qtablewidgetitem12)
        __qtablewidgetitem13 = QTableWidgetItem()
        self.tableWidget.setVerticalHeaderItem(9, __qtablewidgetitem13)
        __qtablewidgetitem14 = QTableWidgetItem()
        self.tableWidget.setVerticalHeaderItem(10, __qtablewidgetitem14)
        __qtablewidgetitem15 = QTableWidgetItem()
        self.tableWidget.setVerticalHeaderItem(11, __qtablewidgetitem15)
        __qtablewidgetitem16 = QTableWidgetItem()
        self.tableWidget.setVerticalHeaderItem(12, __qtablewidgetitem16)
        __qtablewidgetitem17 = QTableWidgetItem()
        self.tableWidget.setVerticalHeaderItem(13, __qtablewidgetitem17)
        __qtablewidgetitem18 = QTableWidgetItem()
        self.tableWidget.setVerticalHeaderItem(14, __qtablewidgetitem18)
        __qtablewidgetitem19 = QTableWidgetItem()
        self.tableWidget.setVerticalHeaderItem(15, __qtablewidgetitem19)
        __qtablewidgetitem20 = QTableWidgetItem()
        self.tableWidget.setItem(0, 0, __qtablewidgetitem20)
        __qtablewidgetitem21 = QTableWidgetItem()
        self.tableWidget.setItem(0, 1, __qtablewidgetitem21)
        __qtablewidgetitem22 = QTableWidgetItem()
        self.tableWidget.setItem(0, 2, __qtablewidgetitem22)
        __qtablewidgetitem23 = QTableWidgetItem()
        self.tableWidget.setItem(0, 3, __qtablewidgetitem23)
        self.tableWidget.setObjectName(u"tableWidget")
        sizePolicy.setHeightForWidth(self.tableWidget.sizePolicy().hasHeightForWidth())
        self.tableWidget.setSizePolicy(sizePolicy)
        palette1 = QPalette()
        palette1.setBrush(QPalette.Active, QPalette.WindowText, brush6)
        brush15 = QBrush(QColor(39, 44, 54, 255))
        brush15.setStyle(Qt.SolidPattern)
        palette1.setBrush(QPalette.Active, QPalette.Button, brush15)
        palette1.setBrush(QPalette.Active, QPalette.Text, brush6)
        palette1.setBrush(QPalette.Active, QPalette.ButtonText, brush6)
        palette1.setBrush(QPalette.Active, QPalette.Base, brush15)
        palette1.setBrush(QPalette.Active, QPalette.Window, brush15)
        brush16 = QBrush(QColor(210, 210, 210, 128))
        brush16.setStyle(Qt.NoBrush)
#if QT_VERSION >= QT_VERSION_CHECK(5, 12, 0)
        palette1.setBrush(QPalette.Active, QPalette.PlaceholderText, brush16)
#endif
        palette1.setBrush(QPalette.Inactive, QPalette.WindowText, brush6)
        palette1.setBrush(QPalette.Inactive, QPalette.Button, brush15)
        palette1.setBrush(QPalette.Inactive, QPalette.Text, brush6)
        palette1.setBrush(QPalette.Inactive, QPalette.ButtonText, brush6)
        palette1.setBrush(QPalette.Inactive, QPalette.Base, brush15)
        palette1.setBrush(QPalette.Inactive, QPalette.Window, brush15)
        brush17 = QBrush(QColor(210, 210, 210, 128))
        brush17.setStyle(Qt.NoBrush)
#if QT_VERSION >= QT_VERSION_CHECK(5, 12, 0)
        palette1.setBrush(QPalette.Inactive, QPalette.PlaceholderText, brush17)
#endif
        palette1.setBrush(QPalette.Disabled, QPalette.WindowText, brush6)
        palette1.setBrush(QPalette.Disabled, QPalette.Button, brush15)
        palette1.setBrush(QPalette.Disabled, QPalette.Text, brush6)
        palette1.setBrush(QPalette.Disabled, QPalette.ButtonText, brush6)
        palette1.setBrush(QPalette.Disabled, QPalette.Base, brush15)
        palette1.setBrush(QPalette.Disabled, QPalette.Window, brush15)
        brush18 = QBrush(QColor(210, 210, 210, 128))
        brush18.setStyle(Qt.NoBrush)
#if QT_VERSION >= QT_VERSION_CHECK(5, 12, 0)
        palette1.setBrush(QPalette.Disabled, QPalette.PlaceholderText, brush18)
#endif
        self.tableWidget.setPalette(palette1)
        self.tableWidget.setStyleSheet(u"QTableWidget {	\n"
"	background-color: rgb(39, 44, 54);\n"
"	padding: 10px;\n"
"	border-radius: 5px;\n"
"	gridline-color: rgb(44, 49, 60);\n"
"	border-bottom: 1px solid rgb(44, 49, 60);\n"
"}\n"
"QTableWidget::item{\n"
"	border-color: rgb(44, 49, 60);\n"
"	padding-left: 5px;\n"
"	padding-right: 5px;\n"
"	gridline-color: rgb(44, 49, 60);\n"
"}\n"
"QTableWidget::item:selected{\n"
"	background-color: rgb(85, 170, 255);\n"
"}\n"
"QScrollBar:horizontal {\n"
"    border: none;\n"
"    background: rgb(52, 59, 72);\n"
"    height: 14px;\n"
"    margin: 0px 21px 0 21px;\n"
"	border-radius: 0px;\n"
"}\n"
" QScrollBar:vertical {\n"
"	border: none;\n"
"    background: rgb(52, 59, 72);\n"
"    width: 14px;\n"
"    margin: 21px 0 21px 0;\n"
"	border-radius: 0px;\n"
" }\n"
"QHeaderView::section{\n"
"	Background-color: rgb(39, 44, 54);\n"
"	max-width: 30px;\n"
"	border: 1px solid rgb(44, 49, 60);\n"
"	border-style: none;\n"
"    border-bottom: 1px solid rgb(44, 49, 60);\n"
"    border-right: 1px solid rgb(44, 49, 60);\n"
"}\n"
""
                        "QTableWidget::horizontalHeader {	\n"
"	background-color: rgb(81, 255, 0);\n"
"}\n"
"QHeaderView::section:horizontal\n"
"{\n"
"    border: 1px solid rgb(32, 34, 42);\n"
"	background-color: rgb(27, 29, 35);\n"
"	padding: 3px;\n"
"	border-top-left-radius: 7px;\n"
"    border-top-right-radius: 7px;\n"
"}\n"
"QHeaderView::section:vertical\n"
"{\n"
"    border: 1px solid rgb(44, 49, 60);\n"
"}\n"
"")
        self.tableWidget.setFrameShape(QFrame.NoFrame)
        self.tableWidget.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.tableWidget.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        self.tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tableWidget.setAlternatingRowColors(False)
        self.tableWidget.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tableWidget.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tableWidget.setShowGrid(True)
        self.tableWidget.setGridStyle(Qt.SolidLine)
        self.tableWidget.setSortingEnabled(False)
        self.tableWidget.horizontalHeader().setVisible(False)
        self.tableWidget.horizontalHeader().setCascadingSectionResizes(True)
        self.tableWidget.horizontalHeader().setDefaultSectionSize(200)
        self.tableWidget.horizontalHeader().setStretchLastSection(True)
        self.tableWidget.verticalHeader().setVisible(False)
        self.tableWidget.verticalHeader().setCascadingSectionResizes(False)
        self.tableWidget.verticalHeader().setHighlightSections(False)
        self.tableWidget.verticalHeader().setStretchLastSection(True)

        self.horizontalLayout_12.addWidget(self.tableWidget)


        self.verticalLayout_6.addWidget(self.frame_3)

        self.stackedWidget.addWidget(self.page_widgets)
        self.page_namePlateData = QWidget()
        self.page_namePlateData.setObjectName(u"page_namePlateData")
        self.gridLayout_5 = QGridLayout(self.page_namePlateData)
        self.gridLayout_5.setObjectName(u"gridLayout_5")
        self.verticalLayout_12 = QVBoxLayout()
        self.verticalLayout_12.setObjectName(u"verticalLayout_12")
        self.comboBox_MachineType = QComboBox(self.page_namePlateData)
        self.comboBox_MachineType.addItem("")
        self.comboBox_MachineType.addItem("")
        self.comboBox_MachineType.setObjectName(u"comboBox_MachineType")

        self.verticalLayout_12.addWidget(self.comboBox_MachineType)

        self.comboBox_MachineName = QComboBox(self.page_namePlateData)
        self.comboBox_MachineName.setObjectName(u"comboBox_MachineName")

        self.verticalLayout_12.addWidget(self.comboBox_MachineName)

        self.horizontalLayout_13 = QHBoxLayout()
        self.horizontalLayout_13.setObjectName(u"horizontalLayout_13")
        self.verticalLayout_13 = QVBoxLayout()
        self.verticalLayout_13.setObjectName(u"verticalLayout_13")
        self.label_npd = QLabel(self.page_namePlateData)
        self.label_npd.setObjectName(u"label_npd")
        self.label_npd.setFrameShape(QFrame.Panel)
        self.label_npd.setFrameShadow(QFrame.Plain)

        self.verticalLayout_13.addWidget(self.label_npd)

        self.label_npd_2 = QLabel(self.page_namePlateData)
        self.label_npd_2.setObjectName(u"label_npd_2")
        self.label_npd_2.setFrameShape(QFrame.Panel)

        self.verticalLayout_13.addWidget(self.label_npd_2)

        self.label_npd_3 = QLabel(self.page_namePlateData)
        self.label_npd_3.setObjectName(u"label_npd_3")
        self.label_npd_3.setFrameShape(QFrame.Panel)

        self.verticalLayout_13.addWidget(self.label_npd_3)

        self.label_npd_4 = QLabel(self.page_namePlateData)
        self.label_npd_4.setObjectName(u"label_npd_4")
        self.label_npd_4.setFrameShape(QFrame.Panel)

        self.verticalLayout_13.addWidget(self.label_npd_4)


        self.horizontalLayout_13.addLayout(self.verticalLayout_13)

        self.verticalLayout_14 = QVBoxLayout()
        self.verticalLayout_14.setObjectName(u"verticalLayout_14")
        self.lineEdit_npp = QLineEdit(self.page_namePlateData)
        self.lineEdit_npp.setObjectName(u"lineEdit_npp")
        sizePolicy7 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        sizePolicy7.setHorizontalStretch(0)
        sizePolicy7.setVerticalStretch(0)
        sizePolicy7.setHeightForWidth(self.lineEdit_npp.sizePolicy().hasHeightForWidth())
        self.lineEdit_npp.setSizePolicy(sizePolicy7)

        self.verticalLayout_14.addWidget(self.lineEdit_npp)

        self.lineEdit_RatedCurrent = QLineEdit(self.page_namePlateData)
        self.lineEdit_RatedCurrent.setObjectName(u"lineEdit_RatedCurrent")
        sizePolicy7.setHeightForWidth(self.lineEdit_RatedCurrent.sizePolicy().hasHeightForWidth())
        self.lineEdit_RatedCurrent.setSizePolicy(sizePolicy7)

        self.verticalLayout_14.addWidget(self.lineEdit_RatedCurrent)

        self.lineEdit_RatedPower = QLineEdit(self.page_namePlateData)
        self.lineEdit_RatedPower.setObjectName(u"lineEdit_RatedPower")
        sizePolicy7.setHeightForWidth(self.lineEdit_RatedPower.sizePolicy().hasHeightForWidth())
        self.lineEdit_RatedPower.setSizePolicy(sizePolicy7)

        self.verticalLayout_14.addWidget(self.lineEdit_RatedPower)

        self.lineEdit_RatedSpeed = QLineEdit(self.page_namePlateData)
        self.lineEdit_RatedSpeed.setObjectName(u"lineEdit_RatedSpeed")
        sizePolicy7.setHeightForWidth(self.lineEdit_RatedSpeed.sizePolicy().hasHeightForWidth())
        self.lineEdit_RatedSpeed.setSizePolicy(sizePolicy7)

        self.verticalLayout_14.addWidget(self.lineEdit_RatedSpeed)


        self.horizontalLayout_13.addLayout(self.verticalLayout_14)


        self.verticalLayout_12.addLayout(self.horizontalLayout_13)

        self.horizontalLayout_14 = QHBoxLayout()
        self.horizontalLayout_14.setObjectName(u"horizontalLayout_14")
        self.horizontalSpacer_3 = QSpacerItem(40, 20, QSizePolicy.Preferred, QSizePolicy.Minimum)

        self.horizontalLayout_14.addItem(self.horizontalSpacer_3)

        self.pushButton_updateModel = QPushButton(self.page_namePlateData)
        self.pushButton_updateModel.setObjectName(u"pushButton_updateModel")
        self.pushButton_updateModel.setStyleSheet(u"QPushButton {\n"
"	border: 2px solid rgb(52, 59, 72);\n"
"	border-radius: 5px;	\n"
"	background-color: rgb(52, 59, 72);\n"
"}\n"
"QPushButton:hover {\n"
"	background-color: rgb(57, 65, 80);\n"
"	border: 2px solid rgb(61, 70, 86);\n"
"}\n"
"QPushButton:pressed {	\n"
"	background-color: rgb(35, 40, 49);\n"
"	border: 2px solid rgb(43, 50, 61);\n"
"}")

        self.horizontalLayout_14.addWidget(self.pushButton_updateModel)

        self.horizontalSpacer_4 = QSpacerItem(40, 20, QSizePolicy.Preferred, QSizePolicy.Minimum)

        self.horizontalLayout_14.addItem(self.horizontalSpacer_4)


        self.verticalLayout_12.addLayout(self.horizontalLayout_14)


        self.gridLayout_5.addLayout(self.verticalLayout_12, 0, 0, 1, 1)

        self.verticalLayout_27 = QVBoxLayout()
        self.verticalLayout_27.setObjectName(u"verticalLayout_27")
        self.verticalLayout_27.setContentsMargins(0, -1, -1, -1)
        self.label_pushedVariables0 = QLabel(self.page_namePlateData)
        self.label_pushedVariables0.setObjectName(u"label_pushedVariables0")
        sizePolicy7.setHeightForWidth(self.label_pushedVariables0.sizePolicy().hasHeightForWidth())
        self.label_pushedVariables0.setSizePolicy(sizePolicy7)

        self.verticalLayout_27.addWidget(self.label_pushedVariables0)

        self.label_pushedVariables = QLabel(self.page_namePlateData)
        self.label_pushedVariables.setObjectName(u"label_pushedVariables")
        self.label_pushedVariables.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignTop)
        self.label_pushedVariables.setWordWrap(True)

        self.verticalLayout_27.addWidget(self.label_pushedVariables)


        self.gridLayout_5.addLayout(self.verticalLayout_27, 0, 1, 1, 1)

        self.ConsoleWidget = ConsoleWidget(self.page_namePlateData)
        self.ConsoleWidget.setObjectName(u"ConsoleWidget")
        self.ConsoleWidget.setEnabled(True)
        self.ConsoleWidget.setMinimumSize(QSize(500, 300))
        self.ConsoleWidget.setStyleSheet(u"background-color: rgb(85, 0, 127);")

        self.gridLayout_5.addWidget(self.ConsoleWidget, 1, 0, 1, 2)

        self.stackedWidget.addWidget(self.page_namePlateData)
        self.page_controllerTuning = QWidget()
        self.page_controllerTuning.setObjectName(u"page_controllerTuning")
        self.verticalLayout_23 = QVBoxLayout(self.page_controllerTuning)
        self.verticalLayout_23.setObjectName(u"verticalLayout_23")
        self.scrollArea_3 = QScrollArea(self.page_controllerTuning)
        self.scrollArea_3.setObjectName(u"scrollArea_3")
        self.scrollArea_3.setWidgetResizable(True)
        self.scrollAreaWidgetContents_3 = QWidget()
        self.scrollAreaWidgetContents_3.setObjectName(u"scrollAreaWidgetContents_3")
        self.scrollAreaWidgetContents_3.setGeometry(QRect(0, 0, 170, 66))
        self.gridLayout_4 = QGridLayout(self.scrollAreaWidgetContents_3)
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.groupBox_5 = QGroupBox(self.scrollAreaWidgetContents_3)
        self.groupBox_5.setObjectName(u"groupBox_5")
        self.verticalLayoutWidget_9 = QWidget(self.groupBox_5)
        self.verticalLayoutWidget_9.setObjectName(u"verticalLayoutWidget_9")
        self.verticalLayoutWidget_9.setGeometry(QRect(10, 20, 321, 137))
        self.verticalLayout_21 = QVBoxLayout(self.verticalLayoutWidget_9)
        self.verticalLayout_21.setObjectName(u"verticalLayout_21")
        self.verticalLayout_21.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_15 = QHBoxLayout()
        self.horizontalLayout_15.setObjectName(u"horizontalLayout_15")
        self.label_math_delta = QLabel(self.verticalLayoutWidget_9)
        self.label_math_delta.setObjectName(u"label_math_delta")
        font10 = QFont()
        font10.setItalic(False)
        self.label_math_delta.setFont(font10)
        self.label_math_delta.setFrameShape(QFrame.Panel)
        self.label_math_delta.setFrameShadow(QFrame.Plain)
        self.label_math_delta.setTextFormat(Qt.AutoText)
        self.label_math_delta.setAlignment(Qt.AlignCenter)

        self.horizontalLayout_15.addWidget(self.label_math_delta)

        self.lineEdit_dampingFactor_delta = QLineEdit(self.verticalLayoutWidget_9)
        self.lineEdit_dampingFactor_delta.setObjectName(u"lineEdit_dampingFactor_delta")
        self.lineEdit_dampingFactor_delta.setFrame(True)

        self.horizontalLayout_15.addWidget(self.lineEdit_dampingFactor_delta)


        self.verticalLayout_21.addLayout(self.horizontalLayout_15)

        self.horizontalLayout_21 = QHBoxLayout()
        self.horizontalLayout_21.setObjectName(u"horizontalLayout_21")
        self.label_desiredVLBW = QLabel(self.verticalLayoutWidget_9)
        self.label_desiredVLBW.setObjectName(u"label_desiredVLBW")
        self.label_desiredVLBW.setFrameShape(QFrame.Panel)
        self.label_desiredVLBW.setFrameShadow(QFrame.Plain)

        self.horizontalLayout_21.addWidget(self.label_desiredVLBW)

        self.lineEdit_desiredVLBW = QLineEdit(self.verticalLayoutWidget_9)
        self.lineEdit_desiredVLBW.setObjectName(u"lineEdit_desiredVLBW")

        self.horizontalLayout_21.addWidget(self.lineEdit_desiredVLBW)


        self.verticalLayout_21.addLayout(self.horizontalLayout_21)

        self.formLayout_3 = QFormLayout()
        self.formLayout_3.setObjectName(u"formLayout_3")
        self.label_CLTS = QLabel(self.verticalLayoutWidget_9)
        self.label_CLTS.setObjectName(u"label_CLTS")
        self.label_CLTS.setFrameShape(QFrame.Panel)
        self.label_CLTS.setFrameShadow(QFrame.Plain)

        self.formLayout_3.setWidget(0, QFormLayout.LabelRole, self.label_CLTS)

        self.lineEdit_CLTS = QLineEdit(self.verticalLayoutWidget_9)
        self.lineEdit_CLTS.setObjectName(u"lineEdit_CLTS")

        self.formLayout_3.setWidget(0, QFormLayout.FieldRole, self.lineEdit_CLTS)

        self.label_VLTS = QLabel(self.verticalLayoutWidget_9)
        self.label_VLTS.setObjectName(u"label_VLTS")
        self.label_VLTS.setFrameShape(QFrame.Panel)

        self.formLayout_3.setWidget(1, QFormLayout.LabelRole, self.label_VLTS)

        self.lineEdit_VLTS = QLineEdit(self.verticalLayoutWidget_9)
        self.lineEdit_VLTS.setObjectName(u"lineEdit_VLTS")

        self.formLayout_3.setWidget(1, QFormLayout.FieldRole, self.lineEdit_VLTS)


        self.verticalLayout_21.addLayout(self.formLayout_3)

        self.horizontalLayout_16 = QHBoxLayout()
        self.horizontalLayout_16.setObjectName(u"horizontalLayout_16")
        self.horizontalSpacer_13 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_16.addItem(self.horizontalSpacer_13)

        self.pushButton_pidTuner = QPushButton(self.verticalLayoutWidget_9)
        self.pushButton_pidTuner.setObjectName(u"pushButton_pidTuner")
        self.pushButton_pidTuner.setStyleSheet(u"QPushButton {\n"
"	border: 2px solid rgb(52, 59, 72);\n"
"	border-radius: 5px;	\n"
"	background-color: rgb(52, 59, 72);\n"
"}\n"
"QPushButton:hover {\n"
"	background-color: rgb(57, 65, 80);\n"
"	border: 2px solid rgb(61, 70, 86);\n"
"}\n"
"QPushButton:pressed {	\n"
"	background-color: rgb(35, 40, 49);\n"
"	border: 2px solid rgb(43, 50, 61);\n"
"}")

        self.horizontalLayout_16.addWidget(self.pushButton_pidTuner)

        self.horizontalSpacer_14 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_16.addItem(self.horizontalSpacer_14)


        self.verticalLayout_21.addLayout(self.horizontalLayout_16)


        self.gridLayout_4.addWidget(self.groupBox_5, 0, 0, 1, 1)

        self.groupBox_6 = QGroupBox(self.scrollAreaWidgetContents_3)
        self.groupBox_6.setObjectName(u"groupBox_6")
        self.verticalLayoutWidget_8 = QWidget(self.groupBox_6)
        self.verticalLayoutWidget_8.setObjectName(u"verticalLayoutWidget_8")
        self.verticalLayoutWidget_8.setGeometry(QRect(10, 30, 791, 411))
        self.verticalLayout_22 = QVBoxLayout(self.verticalLayoutWidget_8)
        self.verticalLayout_22.setSpacing(1)
        self.verticalLayout_22.setObjectName(u"verticalLayout_22")
        self.verticalLayout_22.setContentsMargins(2, 0, 2, 0)
        self.label_qpix_CLKP = QLabel(self.verticalLayoutWidget_8)
        self.label_qpix_CLKP.setObjectName(u"label_qpix_CLKP")
        self.label_qpix_CLKP.setStyleSheet(u"background: rgb(0, 0, 0)")
        self.label_qpix_CLKP.setScaledContents(False)

        self.verticalLayout_22.addWidget(self.label_qpix_CLKP)

        self.label_qpix_CLKI = QLabel(self.verticalLayoutWidget_8)
        self.label_qpix_CLKI.setObjectName(u"label_qpix_CLKI")
        self.label_qpix_CLKI.setStyleSheet(u"background: rgb(0,0,0)")
        self.label_qpix_CLKI.setScaledContents(False)

        self.verticalLayout_22.addWidget(self.label_qpix_CLKI)

        self.label_qpix_VLKP = QLabel(self.verticalLayoutWidget_8)
        self.label_qpix_VLKP.setObjectName(u"label_qpix_VLKP")
        self.label_qpix_VLKP.setStyleSheet(u"background: rgb(0,0,0)")
        self.label_qpix_VLKP.setScaledContents(False)

        self.verticalLayout_22.addWidget(self.label_qpix_VLKP)

        self.label_qpix_VLKI = QLabel(self.verticalLayoutWidget_8)
        self.label_qpix_VLKI.setObjectName(u"label_qpix_VLKI")
        self.label_qpix_VLKI.setStyleSheet(u"background: rgb(0,0,0)")
        self.label_qpix_VLKI.setScaledContents(False)

        self.verticalLayout_22.addWidget(self.label_qpix_VLKI)

        self.label_qpix_Note1 = QLabel(self.verticalLayoutWidget_8)
        self.label_qpix_Note1.setObjectName(u"label_qpix_Note1")
        self.label_qpix_Note1.setStyleSheet(u"background: rgb(0,0,0)")
        self.label_qpix_Note1.setScaledContents(False)

        self.verticalLayout_22.addWidget(self.label_qpix_Note1)

        self.label_qpix_Note2 = QLabel(self.verticalLayoutWidget_8)
        self.label_qpix_Note2.setObjectName(u"label_qpix_Note2")
        self.label_qpix_Note2.setStyleSheet(u"background: rgb(0,0,0)")
        self.label_qpix_Note2.setScaledContents(False)

        self.verticalLayout_22.addWidget(self.label_qpix_Note2)

        self.label_qpix_Note3 = QLabel(self.verticalLayoutWidget_8)
        self.label_qpix_Note3.setObjectName(u"label_qpix_Note3")
        self.label_qpix_Note3.setStyleSheet(u"background: rgb(0,0,0)")
        self.label_qpix_Note3.setScaledContents(False)

        self.verticalLayout_22.addWidget(self.label_qpix_Note3)


        self.gridLayout_4.addWidget(self.groupBox_6, 0, 1, 3, 1)

        self.groupBox_4 = QGroupBox(self.scrollAreaWidgetContents_3)
        self.groupBox_4.setObjectName(u"groupBox_4")
        self.formLayoutWidget_2 = QWidget(self.groupBox_4)
        self.formLayoutWidget_2.setObjectName(u"formLayoutWidget_2")
        self.formLayoutWidget_2.setGeometry(QRect(10, 20, 282, 176))
        self.formLayout_2 = QFormLayout(self.formLayoutWidget_2)
        self.formLayout_2.setObjectName(u"formLayout_2")
        self.formLayout_2.setSizeConstraint(QLayout.SetDefaultConstraint)
        self.formLayout_2.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        self.formLayout_2.setLabelAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.formLayout_2.setFormAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignTop)
        self.formLayout_2.setHorizontalSpacing(6)
        self.formLayout_2.setContentsMargins(0, 0, 0, 0)
        self.label_8 = QLabel(self.formLayoutWidget_2)
        self.label_8.setObjectName(u"label_8")
        self.label_8.setFont(font10)
        self.label_8.setFrameShape(QFrame.Panel)
        self.label_8.setFrameShadow(QFrame.Plain)
        self.label_8.setTextFormat(Qt.AutoText)
        self.label_8.setAlignment(Qt.AlignCenter)

        self.formLayout_2.setWidget(0, QFormLayout.LabelRole, self.label_8)

        self.lineEdit_CLBW = QLineEdit(self.formLayoutWidget_2)
        self.lineEdit_CLBW.setObjectName(u"lineEdit_CLBW")
        self.lineEdit_CLBW.setFrame(True)
        self.lineEdit_CLBW.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.lineEdit_CLBW.setReadOnly(True)

        self.formLayout_2.setWidget(0, QFormLayout.FieldRole, self.lineEdit_CLBW)

        self.label_10 = QLabel(self.formLayoutWidget_2)
        self.label_10.setObjectName(u"label_10")
        self.label_10.setFrameShape(QFrame.Panel)
        self.label_10.setFrameShadow(QFrame.Plain)

        self.formLayout_2.setWidget(2, QFormLayout.LabelRole, self.label_10)

        self.lineEdit_currentKP = QLineEdit(self.formLayoutWidget_2)
        self.lineEdit_currentKP.setObjectName(u"lineEdit_currentKP")
        self.lineEdit_currentKP.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.lineEdit_currentKP.setReadOnly(True)

        self.formLayout_2.setWidget(2, QFormLayout.FieldRole, self.lineEdit_currentKP)

        self.label_13 = QLabel(self.formLayoutWidget_2)
        self.label_13.setObjectName(u"label_13")
        self.label_13.setFrameShape(QFrame.Panel)
        self.label_13.setFrameShadow(QFrame.Plain)

        self.formLayout_2.setWidget(3, QFormLayout.LabelRole, self.label_13)

        self.lineEdit_currentKI = QLineEdit(self.formLayoutWidget_2)
        self.lineEdit_currentKI.setObjectName(u"lineEdit_currentKI")
        self.lineEdit_currentKI.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.lineEdit_currentKI.setReadOnly(True)

        self.formLayout_2.setWidget(3, QFormLayout.FieldRole, self.lineEdit_currentKI)

        self.label_9 = QLabel(self.formLayoutWidget_2)
        self.label_9.setObjectName(u"label_9")
        self.label_9.setFrameShape(QFrame.Panel)
        self.label_9.setFrameShadow(QFrame.Plain)

        self.formLayout_2.setWidget(4, QFormLayout.LabelRole, self.label_9)

        self.lineEdit_speedKP = QLineEdit(self.formLayoutWidget_2)
        self.lineEdit_speedKP.setObjectName(u"lineEdit_speedKP")
        self.lineEdit_speedKP.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.lineEdit_speedKP.setReadOnly(True)

        self.formLayout_2.setWidget(4, QFormLayout.FieldRole, self.lineEdit_speedKP)

        self.label_14 = QLabel(self.formLayoutWidget_2)
        self.label_14.setObjectName(u"label_14")
        self.label_14.setFrameShape(QFrame.Panel)
        self.label_14.setFrameShadow(QFrame.Plain)

        self.formLayout_2.setWidget(5, QFormLayout.LabelRole, self.label_14)

        self.lineEdit_speedKI = QLineEdit(self.formLayoutWidget_2)
        self.lineEdit_speedKI.setObjectName(u"lineEdit_speedKI")
        self.lineEdit_speedKI.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.lineEdit_speedKI.setReadOnly(True)

        self.formLayout_2.setWidget(5, QFormLayout.FieldRole, self.lineEdit_speedKI)

        self.label_16 = QLabel(self.formLayoutWidget_2)
        self.label_16.setObjectName(u"label_16")
        self.label_16.setFont(font10)
        self.label_16.setFrameShape(QFrame.Panel)
        self.label_16.setFrameShadow(QFrame.Plain)
        self.label_16.setTextFormat(Qt.AutoText)
        self.label_16.setAlignment(Qt.AlignCenter)

        self.formLayout_2.setWidget(1, QFormLayout.LabelRole, self.label_16)

        self.lineEdit_designedVLBW = QLineEdit(self.formLayoutWidget_2)
        self.lineEdit_designedVLBW.setObjectName(u"lineEdit_designedVLBW")
        self.lineEdit_designedVLBW.setFrame(True)
        self.lineEdit_designedVLBW.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.lineEdit_designedVLBW.setReadOnly(True)

        self.formLayout_2.setWidget(1, QFormLayout.FieldRole, self.lineEdit_designedVLBW)


        self.gridLayout_4.addWidget(self.groupBox_4, 1, 0, 1, 1)

        self.groupBox_3 = QGroupBox(self.scrollAreaWidgetContents_3)
        self.groupBox_3.setObjectName(u"groupBox_3")
        self.formLayoutWidget_3 = QWidget(self.groupBox_3)
        self.formLayoutWidget_3.setObjectName(u"formLayoutWidget_3")
        self.formLayoutWidget_3.setGeometry(QRect(20, 20, 160, 100))
        self.formLayout_4 = QFormLayout(self.formLayoutWidget_3)
        self.formLayout_4.setObjectName(u"formLayout_4")
        self.formLayout_4.setContentsMargins(0, 0, 0, 0)
        self.label_15 = QLabel(self.formLayoutWidget_3)
        self.label_15.setObjectName(u"label_15")
        self.label_15.setFrameShape(QFrame.Panel)
        self.label_15.setFrameShadow(QFrame.Plain)

        self.formLayout_4.setWidget(0, QFormLayout.LabelRole, self.label_15)

        self.lineEdit_PC_currentKP = QLineEdit(self.formLayoutWidget_3)
        self.lineEdit_PC_currentKP.setObjectName(u"lineEdit_PC_currentKP")
        self.lineEdit_PC_currentKP.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.lineEdit_PC_currentKP.setReadOnly(True)

        self.formLayout_4.setWidget(0, QFormLayout.FieldRole, self.lineEdit_PC_currentKP)

        self.label_17 = QLabel(self.formLayoutWidget_3)
        self.label_17.setObjectName(u"label_17")
        sizePolicy4.setHeightForWidth(self.label_17.sizePolicy().hasHeightForWidth())
        self.label_17.setSizePolicy(sizePolicy4)
        self.label_17.setFrameShape(QFrame.Panel)
        self.label_17.setFrameShadow(QFrame.Plain)

        self.formLayout_4.setWidget(1, QFormLayout.LabelRole, self.label_17)

        self.lineEdit_PC_currentKI = QLineEdit(self.formLayoutWidget_3)
        self.lineEdit_PC_currentKI.setObjectName(u"lineEdit_PC_currentKI")
        self.lineEdit_PC_currentKI.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.lineEdit_PC_currentKI.setReadOnly(True)

        self.formLayout_4.setWidget(1, QFormLayout.FieldRole, self.lineEdit_PC_currentKI)

        self.label_18 = QLabel(self.formLayoutWidget_3)
        self.label_18.setObjectName(u"label_18")
        sizePolicy4.setHeightForWidth(self.label_18.sizePolicy().hasHeightForWidth())
        self.label_18.setSizePolicy(sizePolicy4)
        self.label_18.setFrameShape(QFrame.Panel)
        self.label_18.setFrameShadow(QFrame.Plain)

        self.formLayout_4.setWidget(2, QFormLayout.LabelRole, self.label_18)

        self.lineEdit_PC_speedKP = QLineEdit(self.formLayoutWidget_3)
        self.lineEdit_PC_speedKP.setObjectName(u"lineEdit_PC_speedKP")
        self.lineEdit_PC_speedKP.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.lineEdit_PC_speedKP.setReadOnly(True)

        self.formLayout_4.setWidget(2, QFormLayout.FieldRole, self.lineEdit_PC_speedKP)

        self.label_19 = QLabel(self.formLayoutWidget_3)
        self.label_19.setObjectName(u"label_19")
        sizePolicy4.setHeightForWidth(self.label_19.sizePolicy().hasHeightForWidth())
        self.label_19.setSizePolicy(sizePolicy4)
        self.label_19.setFrameShape(QFrame.Panel)
        self.label_19.setFrameShadow(QFrame.Plain)

        self.formLayout_4.setWidget(3, QFormLayout.LabelRole, self.label_19)

        self.lineEdit_PC_speedKI = QLineEdit(self.formLayoutWidget_3)
        self.lineEdit_PC_speedKI.setObjectName(u"lineEdit_PC_speedKI")
        self.lineEdit_PC_speedKI.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.lineEdit_PC_speedKI.setReadOnly(True)

        self.formLayout_4.setWidget(3, QFormLayout.FieldRole, self.lineEdit_PC_speedKI)


        self.gridLayout_4.addWidget(self.groupBox_3, 2, 0, 1, 1)

        self.scrollArea_3.setWidget(self.scrollAreaWidgetContents_3)

        self.verticalLayout_23.addWidget(self.scrollArea_3)

        self.stackedWidget.addWidget(self.page_controllerTuning)
        self.page_cBasedSimulation = QWidget()
        self.page_cBasedSimulation.setObjectName(u"page_cBasedSimulation")
        self.verticalLayout_17 = QVBoxLayout(self.page_cBasedSimulation)
        self.verticalLayout_17.setObjectName(u"verticalLayout_17")
        self.scrollArea = QScrollArea(self.page_cBasedSimulation)
        self.scrollArea.setObjectName(u"scrollArea")
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 819, 637))
        self.gridLayout_3 = QGridLayout(self.scrollAreaWidgetContents)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.verticalLayout_32 = QVBoxLayout()
        self.verticalLayout_32.setObjectName(u"verticalLayout_32")
        self.verticalLayout_32.setSizeConstraint(QLayout.SetMinimumSize)
        self.formLayout = QFormLayout()
        self.formLayout.setObjectName(u"formLayout")
        self.formLayout.setSizeConstraint(QLayout.SetMinimumSize)
        self.label__path2boptPython_3 = QLabel(self.scrollAreaWidgetContents)
        self.label__path2boptPython_3.setObjectName(u"label__path2boptPython_3")
        self.label__path2boptPython_3.setFrameShape(QFrame.Panel)
        self.label__path2boptPython_3.setFrameShadow(QFrame.Plain)

        self.formLayout.setWidget(0, QFormLayout.LabelRole, self.label__path2boptPython_3)

        self.lineEdit_path2acmsimc = QLineEdit(self.scrollAreaWidgetContents)
        self.lineEdit_path2acmsimc.setObjectName(u"lineEdit_path2acmsimc")
        sizePolicy4.setHeightForWidth(self.lineEdit_path2acmsimc.sizePolicy().hasHeightForWidth())
        self.lineEdit_path2acmsimc.setSizePolicy(sizePolicy4)

        self.formLayout.setWidget(0, QFormLayout.FieldRole, self.lineEdit_path2acmsimc)

        self.label_11 = QLabel(self.scrollAreaWidgetContents)
        self.label_11.setObjectName(u"label_11")
        sizePolicy4.setHeightForWidth(self.label_11.sizePolicy().hasHeightForWidth())
        self.label_11.setSizePolicy(sizePolicy4)

        self.formLayout.setWidget(1, QFormLayout.LabelRole, self.label_11)

        self.lineEdit_RO_MachineName = QLineEdit(self.scrollAreaWidgetContents)
        self.lineEdit_RO_MachineName.setObjectName(u"lineEdit_RO_MachineName")
        sizePolicy7.setHeightForWidth(self.lineEdit_RO_MachineName.sizePolicy().hasHeightForWidth())
        self.lineEdit_RO_MachineName.setSizePolicy(sizePolicy7)
        self.lineEdit_RO_MachineName.setReadOnly(True)

        self.formLayout.setWidget(1, QFormLayout.FieldRole, self.lineEdit_RO_MachineName)

        self.label_12 = QLabel(self.scrollAreaWidgetContents)
        self.label_12.setObjectName(u"label_12")
        sizePolicy1.setHeightForWidth(self.label_12.sizePolicy().hasHeightForWidth())
        self.label_12.setSizePolicy(sizePolicy1)

        self.formLayout.setWidget(2, QFormLayout.LabelRole, self.label_12)

        self.lineEdit_ControlStrategy = QLineEdit(self.scrollAreaWidgetContents)
        self.lineEdit_ControlStrategy.setObjectName(u"lineEdit_ControlStrategy")
        self.lineEdit_ControlStrategy.setReadOnly(True)

        self.formLayout.setWidget(2, QFormLayout.FieldRole, self.lineEdit_ControlStrategy)

        self.label_EndTime = QLabel(self.scrollAreaWidgetContents)
        self.label_EndTime.setObjectName(u"label_EndTime")
        self.label_EndTime.setFrameShape(QFrame.Panel)
        self.label_EndTime.setFrameShadow(QFrame.Plain)

        self.formLayout.setWidget(3, QFormLayout.LabelRole, self.label_EndTime)

        self.lineEdit_EndTime = QLineEdit(self.scrollAreaWidgetContents)
        self.lineEdit_EndTime.setObjectName(u"lineEdit_EndTime")

        self.formLayout.setWidget(3, QFormLayout.FieldRole, self.lineEdit_EndTime)

        self.label_npd_19 = QLabel(self.scrollAreaWidgetContents)
        self.label_npd_19.setObjectName(u"label_npd_19")
        self.label_npd_19.setFrameShape(QFrame.Panel)

        self.formLayout.setWidget(4, QFormLayout.LabelRole, self.label_npd_19)

        self.lineEdit_LoadInertiaPercentage = QLineEdit(self.scrollAreaWidgetContents)
        self.lineEdit_LoadInertiaPercentage.setObjectName(u"lineEdit_LoadInertiaPercentage")

        self.formLayout.setWidget(4, QFormLayout.FieldRole, self.lineEdit_LoadInertiaPercentage)

        self.label_npd_20 = QLabel(self.scrollAreaWidgetContents)
        self.label_npd_20.setObjectName(u"label_npd_20")
        self.label_npd_20.setFrameShape(QFrame.Panel)

        self.formLayout.setWidget(5, QFormLayout.LabelRole, self.label_npd_20)

        self.lineEdit_LoadTorque = QLineEdit(self.scrollAreaWidgetContents)
        self.lineEdit_LoadTorque.setObjectName(u"lineEdit_LoadTorque")

        self.formLayout.setWidget(5, QFormLayout.FieldRole, self.lineEdit_LoadTorque)

        self.label_npd_21 = QLabel(self.scrollAreaWidgetContents)
        self.label_npd_21.setObjectName(u"label_npd_21")
        self.label_npd_21.setFrameShape(QFrame.Panel)

        self.formLayout.setWidget(6, QFormLayout.LabelRole, self.label_npd_21)

        self.lineEdit_ViscousCoefficient = QLineEdit(self.scrollAreaWidgetContents)
        self.lineEdit_ViscousCoefficient.setObjectName(u"lineEdit_ViscousCoefficient")

        self.formLayout.setWidget(6, QFormLayout.FieldRole, self.lineEdit_ViscousCoefficient)

        self.label_npd_22 = QLabel(self.scrollAreaWidgetContents)
        self.label_npd_22.setObjectName(u"label_npd_22")
        self.label_npd_22.setFrameShape(QFrame.Panel)

        self.formLayout.setWidget(7, QFormLayout.LabelRole, self.label_npd_22)

        self.lineEdit_FluxCmdDetails = QLineEdit(self.scrollAreaWidgetContents)
        self.lineEdit_FluxCmdDetails.setObjectName(u"lineEdit_FluxCmdDetails")

        self.formLayout.setWidget(7, QFormLayout.FieldRole, self.lineEdit_FluxCmdDetails)

        self.label_npd_23 = QLabel(self.scrollAreaWidgetContents)
        self.label_npd_23.setObjectName(u"label_npd_23")
        self.label_npd_23.setFrameShape(QFrame.Panel)

        self.formLayout.setWidget(8, QFormLayout.LabelRole, self.label_npd_23)

        self.lineEdit_FluxCmdSinePartPercentage = QLineEdit(self.scrollAreaWidgetContents)
        self.lineEdit_FluxCmdSinePartPercentage.setObjectName(u"lineEdit_FluxCmdSinePartPercentage")

        self.formLayout.setWidget(8, QFormLayout.FieldRole, self.lineEdit_FluxCmdSinePartPercentage)

        self.label_npd_24 = QLabel(self.scrollAreaWidgetContents)
        self.label_npd_24.setObjectName(u"label_npd_24")
        self.label_npd_24.setFrameShape(QFrame.Panel)

        self.formLayout.setWidget(9, QFormLayout.LabelRole, self.label_npd_24)

        self.lineEdit_DCBusVoltage = QLineEdit(self.scrollAreaWidgetContents)
        self.lineEdit_DCBusVoltage.setObjectName(u"lineEdit_DCBusVoltage")

        self.formLayout.setWidget(9, QFormLayout.FieldRole, self.lineEdit_DCBusVoltage)

        self.label_npd_25 = QLabel(self.scrollAreaWidgetContents)
        self.label_npd_25.setObjectName(u"label_npd_25")
        self.label_npd_25.setFrameShape(QFrame.Panel)

        self.formLayout.setWidget(10, QFormLayout.LabelRole, self.label_npd_25)

        self.lineEdit_OutputDataFileName = QLineEdit(self.scrollAreaWidgetContents)
        self.lineEdit_OutputDataFileName.setObjectName(u"lineEdit_OutputDataFileName")

        self.formLayout.setWidget(10, QFormLayout.FieldRole, self.lineEdit_OutputDataFileName)

        self.checkBox_compileAndRun = QCheckBox(self.scrollAreaWidgetContents)
        self.checkBox_compileAndRun.setObjectName(u"checkBox_compileAndRun")
        self.checkBox_compileAndRun.setChecked(True)

        self.formLayout.setWidget(11, QFormLayout.LabelRole, self.checkBox_compileAndRun)

        self.pushButton_runCBasedSimulation = QPushButton(self.scrollAreaWidgetContents)
        self.pushButton_runCBasedSimulation.setObjectName(u"pushButton_runCBasedSimulation")
        font11 = QFont()
        font11.setBold(True)
        font11.setWeight(75)
        self.pushButton_runCBasedSimulation.setFont(font11)
        self.pushButton_runCBasedSimulation.setAutoFillBackground(False)
        self.pushButton_runCBasedSimulation.setStyleSheet(u"QPushButton {\n"
"	border: 2px solid rgb(52, 59, 72);\n"
"	border-radius: 5px;	\n"
"	background-color: rgb(52, 59, 72);\n"
"}\n"
"QPushButton:hover {\n"
"	background-color: rgb(57, 65, 80);\n"
"	border: 2px solid rgb(61, 70, 86);\n"
"}\n"
"QPushButton:pressed {	\n"
"	background-color: rgb(35, 40, 49);\n"
"	border: 2px solid rgb(43, 50, 61);\n"
"}")

        self.formLayout.setWidget(11, QFormLayout.FieldRole, self.pushButton_runCBasedSimulation)

        self.groupBox_2 = QGroupBox(self.scrollAreaWidgetContents)
        self.groupBox_2.setObjectName(u"groupBox_2")
        sizePolicy7.setHeightForWidth(self.groupBox_2.sizePolicy().hasHeightForWidth())
        self.groupBox_2.setSizePolicy(sizePolicy7)
        self.groupBox_2.setMinimumSize(QSize(0, 170))
        self.groupBox_2.setFlat(False)
        self.groupBox_2.setCheckable(False)
        self.gridLayout_6 = QGridLayout(self.groupBox_2)
        self.gridLayout_6.setObjectName(u"gridLayout_6")
        self.radioButton_Excitation_Velocity = QRadioButton(self.groupBox_2)
        self.radioButton_Excitation_Velocity.setObjectName(u"radioButton_Excitation_Velocity")
        self.radioButton_Excitation_Velocity.setChecked(True)

        self.gridLayout_6.addWidget(self.radioButton_Excitation_Velocity, 0, 0, 1, 1)

        self.radioButton_Excitation_Position = QRadioButton(self.groupBox_2)
        self.radioButton_Excitation_Position.setObjectName(u"radioButton_Excitation_Position")

        self.gridLayout_6.addWidget(self.radioButton_Excitation_Position, 0, 1, 1, 1)

        self.radioButton_Excitation_SweepFrequency = QRadioButton(self.groupBox_2)
        self.radioButton_Excitation_SweepFrequency.setObjectName(u"radioButton_Excitation_SweepFrequency")
        self.radioButton_Excitation_SweepFrequency.setChecked(False)

        self.gridLayout_6.addWidget(self.radioButton_Excitation_SweepFrequency, 0, 2, 1, 1)

        self.tableWidget_Uncertainty = QTableWidget(self.groupBox_2)
        if (self.tableWidget_Uncertainty.columnCount() < 1):
            self.tableWidget_Uncertainty.setColumnCount(1)
        __qtablewidgetitem24 = QTableWidgetItem()
        self.tableWidget_Uncertainty.setHorizontalHeaderItem(0, __qtablewidgetitem24)
        if (self.tableWidget_Uncertainty.rowCount() < 4):
            self.tableWidget_Uncertainty.setRowCount(4)
        __qtablewidgetitem25 = QTableWidgetItem()
        self.tableWidget_Uncertainty.setVerticalHeaderItem(0, __qtablewidgetitem25)
        __qtablewidgetitem26 = QTableWidgetItem()
        self.tableWidget_Uncertainty.setVerticalHeaderItem(1, __qtablewidgetitem26)
        __qtablewidgetitem27 = QTableWidgetItem()
        self.tableWidget_Uncertainty.setVerticalHeaderItem(2, __qtablewidgetitem27)
        __qtablewidgetitem28 = QTableWidgetItem()
        self.tableWidget_Uncertainty.setVerticalHeaderItem(3, __qtablewidgetitem28)
        __qtablewidgetitem29 = QTableWidgetItem()
        self.tableWidget_Uncertainty.setItem(0, 0, __qtablewidgetitem29)
        __qtablewidgetitem30 = QTableWidgetItem()
        self.tableWidget_Uncertainty.setItem(1, 0, __qtablewidgetitem30)
        __qtablewidgetitem31 = QTableWidgetItem()
        self.tableWidget_Uncertainty.setItem(2, 0, __qtablewidgetitem31)
        __qtablewidgetitem32 = QTableWidgetItem()
        self.tableWidget_Uncertainty.setItem(3, 0, __qtablewidgetitem32)
        self.tableWidget_Uncertainty.setObjectName(u"tableWidget_Uncertainty")
        font12 = QFont()
        font12.setFamily(u"Times New Roman")
        self.tableWidget_Uncertainty.setFont(font12)
        self.tableWidget_Uncertainty.setStyleSheet(u"QTableView {\n"
"    selection-background-color: qlineargradient(x1: 0, y1: 0, x2: 0.5, y2: 0.5,\n"
"                                stop: 0 #FF92BB, stop: 1 white);\n"
"}\n"
"\n"
"QHeaderView::section{\n"
"	Background-color:rgb(100,1,1);\n"
"    border-radius:14px;\n"
"}\n"
"\n"
"/* Ref\n"
"https://stackoverflow.com/questions/19198634/pyqt-qtablewidget-horizontalheaderlabel-stylesheet\n"
"*/\n"
"\n"
"QTableView QTableCornerButton::section {\n"
"    background: purple;\n"
"    border: 2px outset green;\n"
"}")
        self.tableWidget_Uncertainty.setFrameShape(QFrame.WinPanel)
        self.tableWidget_Uncertainty.verticalHeader().setMinimumSectionSize(20)
        self.tableWidget_Uncertainty.verticalHeader().setDefaultSectionSize(20)

        self.gridLayout_6.addWidget(self.tableWidget_Uncertainty, 1, 0, 1, 2)

        self.groupBox_sweepFrequency = QGroupBox(self.groupBox_2)
        self.groupBox_sweepFrequency.setObjectName(u"groupBox_sweepFrequency")
        self.groupBox_sweepFrequency.setEnabled(True)
        self.verticalLayout_26 = QVBoxLayout(self.groupBox_sweepFrequency)
        self.verticalLayout_26.setObjectName(u"verticalLayout_26")
        self.verticalLayout_35 = QVBoxLayout()
        self.verticalLayout_35.setObjectName(u"verticalLayout_35")
        self.radioButton_openLoop = QRadioButton(self.groupBox_sweepFrequency)
        self.radioButton_openLoop.setObjectName(u"radioButton_openLoop")
        font13 = QFont()
        font13.setFamily(u"Times New Roman")
        font13.setPointSize(7)
        self.radioButton_openLoop.setFont(font13)
        self.radioButton_openLoop.setAutoExclusive(False)

        self.verticalLayout_35.addWidget(self.radioButton_openLoop)

        self.radioButton_currentLoopOnly = QRadioButton(self.groupBox_sweepFrequency)
        self.radioButton_currentLoopOnly.setObjectName(u"radioButton_currentLoopOnly")
        self.radioButton_currentLoopOnly.setFont(font13)
        self.radioButton_currentLoopOnly.setAutoExclusive(False)

        self.verticalLayout_35.addWidget(self.radioButton_currentLoopOnly)

        self.horizontalLayout_36 = QHBoxLayout()
        self.horizontalLayout_36.setSpacing(0)
        self.horizontalLayout_36.setObjectName(u"horizontalLayout_36")
        self.label_maxFreq2Sweep = QLabel(self.groupBox_sweepFrequency)
        self.label_maxFreq2Sweep.setObjectName(u"label_maxFreq2Sweep")
        sizePolicy8 = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Maximum)
        sizePolicy8.setHorizontalStretch(0)
        sizePolicy8.setVerticalStretch(0)
        sizePolicy8.setHeightForWidth(self.label_maxFreq2Sweep.sizePolicy().hasHeightForWidth())
        self.label_maxFreq2Sweep.setSizePolicy(sizePolicy8)
        self.label_maxFreq2Sweep.setFont(font13)

        self.horizontalLayout_36.addWidget(self.label_maxFreq2Sweep)

        self.lineEdit_maxFreq2Sweep = QLineEdit(self.groupBox_sweepFrequency)
        self.lineEdit_maxFreq2Sweep.setObjectName(u"lineEdit_maxFreq2Sweep")
        sizePolicy7.setHeightForWidth(self.lineEdit_maxFreq2Sweep.sizePolicy().hasHeightForWidth())
        self.lineEdit_maxFreq2Sweep.setSizePolicy(sizePolicy7)
        self.lineEdit_maxFreq2Sweep.setFont(font13)

        self.horizontalLayout_36.addWidget(self.lineEdit_maxFreq2Sweep)


        self.verticalLayout_35.addLayout(self.horizontalLayout_36)


        self.verticalLayout_26.addLayout(self.verticalLayout_35)


        self.gridLayout_6.addWidget(self.groupBox_sweepFrequency, 1, 2, 1, 1)


        self.formLayout.setWidget(12, QFormLayout.SpanningRole, self.groupBox_2)


        self.verticalLayout_32.addLayout(self.formLayout)

        self.tabWidget_3 = QTabWidget(self.scrollAreaWidgetContents)
        self.tabWidget_3.setObjectName(u"tabWidget_3")
        self.tabWidget_3.setStyleSheet(u"\n"
"QTabWidget>QWidget>QWidget{background: rgb(27, 29, 35);}\n"
"\n"
"/* background: rgb(27, 29, 35); */ \n"
"\n"
"QTabWidget::tab-bar {\n"
"    left: 10px; /* move to the right by 5px */\n"
"}\n"
"\n"
"QTabBar::tab {\n"
"    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,\n"
"                                stop: 0 #E1E1E1, stop: 0.4 rgb(27, 29, 35);,\n"
"                                stop: 0.5 #D8D8D8, stop: 1.0 rgb(27, 29, 35););\n"
"    border: 2px solid rgb(27, 29, 35);\n"
"    border-bottom-color: rgb(27, 29, 35); /* same as the pane color */\n"
"    border-top-left-radius: 4px;\n"
"    border-top-right-radius: 4px;\n"
"    min-width: 8ex;\n"
"    padding: 2px;\n"
"}\n"
"\n"
"/* reference:\n"
"https://doc.qt.io/archives/qt-4.8/stylesheet-examples.html#customizing-qtabwidget-and-qtabbar\n"
"*/")
        self.tab_11 = QWidget()
        self.tab_11.setObjectName(u"tab_11")
        self.verticalLayout_19 = QVBoxLayout(self.tab_11)
        self.verticalLayout_19.setObjectName(u"verticalLayout_19")
        self.verticalLayout_18 = QVBoxLayout()
        self.verticalLayout_18.setObjectName(u"verticalLayout_18")
        self.label_PANameSelected = QLabel(self.tab_11)
        self.label_PANameSelected.setObjectName(u"label_PANameSelected")
        self.label_PANameSelected.setFrameShape(QFrame.Panel)
        self.label_PANameSelected.setFrameShadow(QFrame.Plain)

        self.verticalLayout_18.addWidget(self.label_PANameSelected)

        self.horizontalLayout_24 = QHBoxLayout()
        self.horizontalLayout_24.setObjectName(u"horizontalLayout_24")
        self.lineEdit_PAValueSelected_2 = QLineEdit(self.tab_11)
        self.lineEdit_PAValueSelected_2.setObjectName(u"lineEdit_PAValueSelected_2")
        self.lineEdit_PAValueSelected_2.setReadOnly(True)

        self.horizontalLayout_24.addWidget(self.lineEdit_PAValueSelected_2)


        self.verticalLayout_18.addLayout(self.horizontalLayout_24)

        self.horizontalLayout_23 = QHBoxLayout()
        self.horizontalLayout_23.setObjectName(u"horizontalLayout_23")
        self.comboBox_PADataFileSelected_2 = QComboBox(self.tab_11)
        self.comboBox_PADataFileSelected_2.setObjectName(u"comboBox_PADataFileSelected_2")
        sizePolicy9 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        sizePolicy9.setHorizontalStretch(0)
        sizePolicy9.setVerticalStretch(0)
        sizePolicy9.setHeightForWidth(self.comboBox_PADataFileSelected_2.sizePolicy().hasHeightForWidth())
        self.comboBox_PADataFileSelected_2.setSizePolicy(sizePolicy9)
        self.comboBox_PADataFileSelected_2.setStyleSheet(u"background-color: rgb(85, 0, 127);")

        self.horizontalLayout_23.addWidget(self.comboBox_PADataFileSelected_2)

        self.pushButton_123123 = QPushButton(self.tab_11)
        self.pushButton_123123.setObjectName(u"pushButton_123123")
        self.pushButton_123123.setFont(font11)

        self.horizontalLayout_23.addWidget(self.pushButton_123123)


        self.verticalLayout_18.addLayout(self.horizontalLayout_23)


        self.verticalLayout_19.addLayout(self.verticalLayout_18)

        self.tabWidget_3.addTab(self.tab_11, "")
        self.tab_12 = QWidget()
        self.tab_12.setObjectName(u"tab_12")
        self.verticalLayout_20 = QVBoxLayout(self.tab_12)
        self.verticalLayout_20.setObjectName(u"verticalLayout_20")
        self.verticalLayout_36 = QVBoxLayout()
        self.verticalLayout_36.setObjectName(u"verticalLayout_36")
        self.label_PANameSelected_2 = QLabel(self.tab_12)
        self.label_PANameSelected_2.setObjectName(u"label_PANameSelected_2")
        self.label_PANameSelected_2.setFrameShape(QFrame.Panel)
        self.label_PANameSelected_2.setFrameShadow(QFrame.Plain)

        self.verticalLayout_36.addWidget(self.label_PANameSelected_2)

        self.horizontalLayout_38 = QHBoxLayout()
        self.horizontalLayout_38.setObjectName(u"horizontalLayout_38")
        self.lineEdit_PAValueSelected = QLineEdit(self.tab_12)
        self.lineEdit_PAValueSelected.setObjectName(u"lineEdit_PAValueSelected")
        sizePolicy7.setHeightForWidth(self.lineEdit_PAValueSelected.sizePolicy().hasHeightForWidth())
        self.lineEdit_PAValueSelected.setSizePolicy(sizePolicy7)
        self.lineEdit_PAValueSelected.setReadOnly(True)

        self.horizontalLayout_38.addWidget(self.lineEdit_PAValueSelected)


        self.verticalLayout_36.addLayout(self.horizontalLayout_38)

        self.horizontalLayout_39 = QHBoxLayout()
        self.horizontalLayout_39.setObjectName(u"horizontalLayout_39")
        self.comboBox_PADataFileSelected = QComboBox(self.tab_12)
        self.comboBox_PADataFileSelected.setObjectName(u"comboBox_PADataFileSelected")
        sizePolicy10 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)
        sizePolicy10.setHorizontalStretch(0)
        sizePolicy10.setVerticalStretch(0)
        sizePolicy10.setHeightForWidth(self.comboBox_PADataFileSelected.sizePolicy().hasHeightForWidth())
        self.comboBox_PADataFileSelected.setSizePolicy(sizePolicy10)
        self.comboBox_PADataFileSelected.setStyleSheet(u"background-color: rgb(85, 0, 127);")

        self.horizontalLayout_39.addWidget(self.comboBox_PADataFileSelected)

        self.pushButton_ACMPlotHere = QPushButton(self.tab_12)
        self.pushButton_ACMPlotHere.setObjectName(u"pushButton_ACMPlotHere")
        self.pushButton_ACMPlotHere.setFont(font11)
        self.pushButton_ACMPlotHere.setStyleSheet(u"QPushButton {\n"
"	border: 2px solid rgb(52, 59, 72);\n"
"	border-radius: 5px;	\n"
"	background-color: rgb(52, 59, 72);\n"
"}\n"
"QPushButton:hover {\n"
"	background-color: rgb(57, 65, 80);\n"
"	border: 2px solid rgb(61, 70, 86);\n"
"}\n"
"QPushButton:pressed {	\n"
"	background-color: rgb(35, 40, 49);\n"
"	border: 2px solid rgb(43, 50, 61);\n"
"}")

        self.horizontalLayout_39.addWidget(self.pushButton_ACMPlotHere)


        self.verticalLayout_36.addLayout(self.horizontalLayout_39)


        self.verticalLayout_20.addLayout(self.verticalLayout_36)

        self.tabWidget_3.addTab(self.tab_12, "")

        self.verticalLayout_32.addWidget(self.tabWidget_3)


        self.gridLayout_3.addLayout(self.verticalLayout_32, 0, 0, 2, 1)

        self.comboBox_PlotSettingSelect = QComboBox(self.scrollAreaWidgetContents)
        self.comboBox_PlotSettingSelect.addItem("")
        self.comboBox_PlotSettingSelect.setObjectName(u"comboBox_PlotSettingSelect")
        self.comboBox_PlotSettingSelect.setEditable(False)
        self.comboBox_PlotSettingSelect.setMaxVisibleItems(12)

        self.gridLayout_3.addWidget(self.comboBox_PlotSettingSelect, 0, 1, 1, 1)

        self.lineEdit_plotSettingName = QLineEdit(self.scrollAreaWidgetContents)
        self.lineEdit_plotSettingName.setObjectName(u"lineEdit_plotSettingName")
        sizePolicy4.setHeightForWidth(self.lineEdit_plotSettingName.sizePolicy().hasHeightForWidth())
        self.lineEdit_plotSettingName.setSizePolicy(sizePolicy4)
        self.lineEdit_plotSettingName.setMinimumSize(QSize(0, 12))

        self.gridLayout_3.addWidget(self.lineEdit_plotSettingName, 0, 2, 1, 1)

        self.verticalLayout_37 = QVBoxLayout()
        self.verticalLayout_37.setObjectName(u"verticalLayout_37")
        self.horizontalLayout_40 = QHBoxLayout()
        self.horizontalLayout_40.setObjectName(u"horizontalLayout_40")
        self.label__path2boptPython_9 = QLabel(self.scrollAreaWidgetContents)
        self.label__path2boptPython_9.setObjectName(u"label__path2boptPython_9")
        sizePolicy1.setHeightForWidth(self.label__path2boptPython_9.sizePolicy().hasHeightForWidth())
        self.label__path2boptPython_9.setSizePolicy(sizePolicy1)
        self.label__path2boptPython_9.setFrameShape(QFrame.Panel)
        self.label__path2boptPython_9.setFrameShadow(QFrame.Plain)

        self.horizontalLayout_40.addWidget(self.label__path2boptPython_9)

        self.lineEdit_path2ACMPlotLabels = QLineEdit(self.scrollAreaWidgetContents)
        self.lineEdit_path2ACMPlotLabels.setObjectName(u"lineEdit_path2ACMPlotLabels")
        sizePolicy11 = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy11.setHorizontalStretch(0)
        sizePolicy11.setVerticalStretch(0)
        sizePolicy11.setHeightForWidth(self.lineEdit_path2ACMPlotLabels.sizePolicy().hasHeightForWidth())
        self.lineEdit_path2ACMPlotLabels.setSizePolicy(sizePolicy11)
        self.lineEdit_path2ACMPlotLabels.setReadOnly(True)

        self.horizontalLayout_40.addWidget(self.lineEdit_path2ACMPlotLabels)


        self.verticalLayout_37.addLayout(self.horizontalLayout_40)

        self.label_ACMLabels_3 = QLabel(self.scrollAreaWidgetContents)
        self.label_ACMLabels_3.setObjectName(u"label_ACMLabels_3")
        sizePolicy1.setHeightForWidth(self.label_ACMLabels_3.sizePolicy().hasHeightForWidth())
        self.label_ACMLabels_3.setSizePolicy(sizePolicy1)
        self.label_ACMLabels_3.setFont(font11)
        self.label_ACMLabels_3.setFrameShape(QFrame.NoFrame)
        self.label_ACMLabels_3.setFrameShadow(QFrame.Plain)
        self.label_ACMLabels_3.setAlignment(Qt.AlignCenter)

        self.verticalLayout_37.addWidget(self.label_ACMLabels_3)

        self.plainTextEdit_ACMPlotLabels = QCodeEditor(self.scrollAreaWidgetContents)
        self.plainTextEdit_ACMPlotLabels.setObjectName(u"plainTextEdit_ACMPlotLabels")
        sizePolicy12 = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        sizePolicy12.setHorizontalStretch(0)
        sizePolicy12.setVerticalStretch(0)
        sizePolicy12.setHeightForWidth(self.plainTextEdit_ACMPlotLabels.sizePolicy().hasHeightForWidth())
        self.plainTextEdit_ACMPlotLabels.setSizePolicy(sizePolicy12)
        font14 = QFont()
        font14.setFamily(u"Consolas")
        font14.setPointSize(12)
        self.plainTextEdit_ACMPlotLabels.setFont(font14)
        self.plainTextEdit_ACMPlotLabels.setStyleSheet(u"background: rgb(27, 29, 35);\n"
"\n"
"")
        self.plainTextEdit_ACMPlotLabels.setLineWrapMode(QPlainTextEdit.NoWrap)

        self.verticalLayout_37.addWidget(self.plainTextEdit_ACMPlotLabels)


        self.gridLayout_3.addLayout(self.verticalLayout_37, 1, 1, 1, 1)

        self.verticalLayout_38 = QVBoxLayout()
        self.verticalLayout_38.setObjectName(u"verticalLayout_38")
        self.verticalLayout_38.setSizeConstraint(QLayout.SetMaximumSize)
        self.horizontalLayout_41 = QHBoxLayout()
        self.horizontalLayout_41.setObjectName(u"horizontalLayout_41")
        self.label__path2boptPython_10 = QLabel(self.scrollAreaWidgetContents)
        self.label__path2boptPython_10.setObjectName(u"label__path2boptPython_10")
        self.label__path2boptPython_10.setFrameShape(QFrame.Panel)
        self.label__path2boptPython_10.setFrameShadow(QFrame.Plain)

        self.horizontalLayout_41.addWidget(self.label__path2boptPython_10)

        self.lineEdit_path2ACMPlotSignals = QLineEdit(self.scrollAreaWidgetContents)
        self.lineEdit_path2ACMPlotSignals.setObjectName(u"lineEdit_path2ACMPlotSignals")
        self.lineEdit_path2ACMPlotSignals.setReadOnly(True)

        self.horizontalLayout_41.addWidget(self.lineEdit_path2ACMPlotSignals)


        self.verticalLayout_38.addLayout(self.horizontalLayout_41)

        self.label_ACMLabels_4 = QLabel(self.scrollAreaWidgetContents)
        self.label_ACMLabels_4.setObjectName(u"label_ACMLabels_4")
        self.label_ACMLabels_4.setFont(font11)
        self.label_ACMLabels_4.setFrameShape(QFrame.NoFrame)
        self.label_ACMLabels_4.setFrameShadow(QFrame.Plain)
        self.label_ACMLabels_4.setAlignment(Qt.AlignCenter)

        self.verticalLayout_38.addWidget(self.label_ACMLabels_4)

        self.plainTextEdit_ACMPlotDetails = QCodeEditor(self.scrollAreaWidgetContents)
        self.plainTextEdit_ACMPlotDetails.setObjectName(u"plainTextEdit_ACMPlotDetails")
        sizePolicy13 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        sizePolicy13.setHorizontalStretch(0)
        sizePolicy13.setVerticalStretch(0)
        sizePolicy13.setHeightForWidth(self.plainTextEdit_ACMPlotDetails.sizePolicy().hasHeightForWidth())
        self.plainTextEdit_ACMPlotDetails.setSizePolicy(sizePolicy13)
        self.plainTextEdit_ACMPlotDetails.setFont(font14)
        self.plainTextEdit_ACMPlotDetails.setStyleSheet(u"background: transparent;")
        self.plainTextEdit_ACMPlotDetails.setLineWrapMode(QPlainTextEdit.NoWrap)

        self.verticalLayout_38.addWidget(self.plainTextEdit_ACMPlotDetails)


        self.gridLayout_3.addLayout(self.verticalLayout_38, 1, 2, 1, 1)

        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.verticalLayout_17.addWidget(self.scrollArea)

        self.stackedWidget.addWidget(self.page_cBasedSimulation)
        self.page_scope = QWidget()
        self.page_scope.setObjectName(u"page_scope")
        self.horizontalLayout_22 = QHBoxLayout(self.page_scope)
        self.horizontalLayout_22.setSpacing(5)
        self.horizontalLayout_22.setObjectName(u"horizontalLayout_22")
        self.horizontalLayout_22.setContentsMargins(0, 0, 0, 0)
        self.scrollArea_5 = QScrollArea(self.page_scope)
        self.scrollArea_5.setObjectName(u"scrollArea_5")
        self.scrollArea_5.setMinimumSize(QSize(0, 800))
        self.scrollArea_5.setFrameShape(QFrame.NoFrame)
        self.scrollArea_5.setFrameShadow(QFrame.Plain)
        self.scrollArea_5.setWidgetResizable(True)
        self.scrollAreaWidgetContents_5 = QWidget()
        self.scrollAreaWidgetContents_5.setObjectName(u"scrollAreaWidgetContents_5")
        self.scrollAreaWidgetContents_5.setGeometry(QRect(0, 0, 800, 800))
        self.verticalLayout_16 = QVBoxLayout(self.scrollAreaWidgetContents_5)
        self.verticalLayout_16.setSpacing(5)
        self.verticalLayout_16.setObjectName(u"verticalLayout_16")
        self.verticalLayout_16.setContentsMargins(0, 0, 0, 0)
        self.MplWidget_ACMPlot = MplWidget(self.scrollAreaWidgetContents_5)
        self.MplWidget_ACMPlot.setObjectName(u"MplWidget_ACMPlot")
        sizePolicy14 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.MinimumExpanding)
        sizePolicy14.setHorizontalStretch(0)
        sizePolicy14.setVerticalStretch(0)
        sizePolicy14.setHeightForWidth(self.MplWidget_ACMPlot.sizePolicy().hasHeightForWidth())
        self.MplWidget_ACMPlot.setSizePolicy(sizePolicy14)
        self.MplWidget_ACMPlot.setMinimumSize(QSize(800, 800))
        self.MplWidget_ACMPlot.setStyleSheet(u"background-color: rgb(170, 0, 127)")

        self.verticalLayout_16.addWidget(self.MplWidget_ACMPlot)

        self.scrollArea_5.setWidget(self.scrollAreaWidgetContents_5)

        self.horizontalLayout_22.addWidget(self.scrollArea_5)

        self.stackedWidget.addWidget(self.page_scope)
        self.page_plots = QWidget()
        self.page_plots.setObjectName(u"page_plots")
        self.horizontalLayout_17 = QHBoxLayout(self.page_plots)
        self.horizontalLayout_17.setObjectName(u"horizontalLayout_17")
        self.scrollArea_4 = QScrollArea(self.page_plots)
        self.scrollArea_4.setObjectName(u"scrollArea_4")
        self.scrollArea_4.setWidgetResizable(True)
        self.scrollAreaWidgetContents_4 = QWidget()
        self.scrollAreaWidgetContents_4.setObjectName(u"scrollAreaWidgetContents_4")
        self.scrollAreaWidgetContents_4.setGeometry(QRect(0, 0, 98, 28))
        self.verticalLayoutWidget_3 = QWidget(self.scrollAreaWidgetContents_4)
        self.verticalLayoutWidget_3.setObjectName(u"verticalLayoutWidget_3")
        self.verticalLayoutWidget_3.setGeometry(QRect(0, 0, 791, 881))
        self.verticalLayout_inTab2 = QVBoxLayout(self.verticalLayoutWidget_3)
        self.verticalLayout_inTab2.setObjectName(u"verticalLayout_inTab2")
        self.verticalLayout_inTab2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_19 = QHBoxLayout()
        self.horizontalLayout_19.setObjectName(u"horizontalLayout_19")
        self.horizontalSpacer_5 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_19.addItem(self.horizontalSpacer_5)

        self.pushButton_getSignal = QPushButton(self.verticalLayoutWidget_3)
        self.pushButton_getSignal.setObjectName(u"pushButton_getSignal")
        self.pushButton_getSignal.setFont(font11)
        self.pushButton_getSignal.setStyleSheet(u"QPushButton {\n"
"	border: 2px solid rgb(52, 59, 72);\n"
"	border-radius: 5px;	\n"
"	background-color: rgb(52, 59, 72);\n"
"}\n"
"QPushButton:hover {\n"
"	background-color: rgb(57, 65, 80);\n"
"	border: 2px solid rgb(61, 70, 86);\n"
"}\n"
"QPushButton:pressed {	\n"
"	background-color: rgb(35, 40, 49);\n"
"	border: 2px solid rgb(43, 50, 61);\n"
"}")

        self.horizontalLayout_19.addWidget(self.pushButton_getSignal)

        self.horizontalSpacer_6 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_19.addItem(self.horizontalSpacer_6)

        self.checkBox_LissajousPlot_2 = QCheckBox(self.verticalLayoutWidget_3)
        self.checkBox_LissajousPlot_2.setObjectName(u"checkBox_LissajousPlot_2")
        self.checkBox_LissajousPlot_2.setChecked(True)

        self.horizontalLayout_19.addWidget(self.checkBox_LissajousPlot_2)

        self.pushButton_LissajousPlot = QPushButton(self.verticalLayoutWidget_3)
        self.pushButton_LissajousPlot.setObjectName(u"pushButton_LissajousPlot")
        self.pushButton_LissajousPlot.setFont(font11)
        self.pushButton_LissajousPlot.setStyleSheet(u"QPushButton {\n"
"	border: 2px solid rgb(52, 59, 72);\n"
"	border-radius: 5px;	\n"
"	background-color: rgb(52, 59, 72);\n"
"}\n"
"QPushButton:hover {\n"
"	background-color: rgb(57, 65, 80);\n"
"	border: 2px solid rgb(61, 70, 86);\n"
"}\n"
"QPushButton:pressed {	\n"
"	background-color: rgb(35, 40, 49);\n"
"	border: 2px solid rgb(43, 50, 61);\n"
"}")

        self.horizontalLayout_19.addWidget(self.pushButton_LissajousPlot)

        self.lcdNumber_LissajousStart = QLCDNumber(self.verticalLayoutWidget_3)
        self.lcdNumber_LissajousStart.setObjectName(u"lcdNumber_LissajousStart")
        self.lcdNumber_LissajousStart.setSmallDecimalPoint(False)

        self.horizontalLayout_19.addWidget(self.lcdNumber_LissajousStart)

        self.lcdNumber_LissajousEnd = QLCDNumber(self.verticalLayoutWidget_3)
        self.lcdNumber_LissajousEnd.setObjectName(u"lcdNumber_LissajousEnd")

        self.horizontalLayout_19.addWidget(self.lcdNumber_LissajousEnd)

        self.horizontalSpacer_8 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_19.addItem(self.horizontalSpacer_8)


        self.verticalLayout_inTab2.addLayout(self.horizontalLayout_19)

        self.plainTextEdit_LissajousPlotSignals = QCodeEditor(self.verticalLayoutWidget_3)
        self.plainTextEdit_LissajousPlotSignals.setObjectName(u"plainTextEdit_LissajousPlotSignals")
        sizePolicy7.setHeightForWidth(self.plainTextEdit_LissajousPlotSignals.sizePolicy().hasHeightForWidth())
        self.plainTextEdit_LissajousPlotSignals.setSizePolicy(sizePolicy7)
        self.plainTextEdit_LissajousPlotSignals.setFont(font14)
        self.plainTextEdit_LissajousPlotSignals.setStyleSheet(u"QPlainTextEdit, QTextEdit { \n"
"background-color: black;\n"
"color: white ;\n"
"selection-background-color: #ccc}\n"
".error { color: red; }\n"
".in-prompt { color: navy; }\n"
".in-prompt-number { font-weight: bold; }\n"
".out-prompt { color: darkred; }\n"
".out-prompt-number { font-weight: bold; }\n"
"/* .inverted is used to highlight selected completion */\n"
".inverted { background-color: black ; color: white; \n"
"}\n"
"\n"
"/* qtconsole.pdf */")
        self.plainTextEdit_LissajousPlotSignals.setLineWrapMode(QPlainTextEdit.NoWrap)

        self.verticalLayout_inTab2.addWidget(self.plainTextEdit_LissajousPlotSignals)

        self.horizontalSlider_LissajousTimeStart = QSlider(self.verticalLayoutWidget_3)
        self.horizontalSlider_LissajousTimeStart.setObjectName(u"horizontalSlider_LissajousTimeStart")
        self.horizontalSlider_LissajousTimeStart.setMaximum(999)
        self.horizontalSlider_LissajousTimeStart.setSingleStep(1)
        self.horizontalSlider_LissajousTimeStart.setPageStep(1)
        self.horizontalSlider_LissajousTimeStart.setOrientation(Qt.Horizontal)

        self.verticalLayout_inTab2.addWidget(self.horizontalSlider_LissajousTimeStart)

        self.horizontalSlider_LissajousTimeEnd = QSlider(self.verticalLayoutWidget_3)
        self.horizontalSlider_LissajousTimeEnd.setObjectName(u"horizontalSlider_LissajousTimeEnd")
        self.horizontalSlider_LissajousTimeEnd.setMaximum(999)
        self.horizontalSlider_LissajousTimeEnd.setPageStep(1)
        self.horizontalSlider_LissajousTimeEnd.setValue(999)
        self.horizontalSlider_LissajousTimeEnd.setOrientation(Qt.Horizontal)

        self.verticalLayout_inTab2.addWidget(self.horizontalSlider_LissajousTimeEnd)

        self.MplWidget = MplWidget(self.verticalLayoutWidget_3)
        self.MplWidget.setObjectName(u"MplWidget")
        sizePolicy14.setHeightForWidth(self.MplWidget.sizePolicy().hasHeightForWidth())
        self.MplWidget.setSizePolicy(sizePolicy14)
        self.MplWidget.setStyleSheet(u"color: blue;\n"
"background-color: yellow;\n"
"selection-color: yellow;\n"
"selection-background-color: blue;")

        self.verticalLayout_inTab2.addWidget(self.MplWidget)

        self.scrollArea_4.setWidget(self.scrollAreaWidgetContents_4)

        self.horizontalLayout_17.addWidget(self.scrollArea_4)

        self.stackedWidget.addWidget(self.page_plots)
        self.page_bodePlot = QWidget()
        self.page_bodePlot.setObjectName(u"page_bodePlot")
        self.verticalLayout_25 = QVBoxLayout(self.page_bodePlot)
        self.verticalLayout_25.setObjectName(u"verticalLayout_25")
        self.horizontalLayout_25 = QHBoxLayout()
        self.horizontalLayout_25.setObjectName(u"horizontalLayout_25")
        self.horizontalSpacer_15 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_25.addItem(self.horizontalSpacer_15)

        self.pushButton_bodePlot = QPushButton(self.page_bodePlot)
        self.pushButton_bodePlot.setObjectName(u"pushButton_bodePlot")
        self.pushButton_bodePlot.setStyleSheet(u"QPushButton {\n"
"	border: 2px solid rgb(52, 59, 72);\n"
"	border-radius: 5px;	\n"
"	background-color: rgb(52, 59, 72);\n"
"}\n"
"QPushButton:hover {\n"
"	background-color: rgb(57, 65, 80);\n"
"	border: 2px solid rgb(61, 70, 86);\n"
"}\n"
"QPushButton:pressed {	\n"
"	background-color: rgb(35, 40, 49);\n"
"	border: 2px solid rgb(43, 50, 61);\n"
"}")

        self.horizontalLayout_25.addWidget(self.pushButton_bodePlot)

        self.horizontalSpacer_19 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_25.addItem(self.horizontalSpacer_19)


        self.verticalLayout_25.addLayout(self.horizontalLayout_25)

        self.MplWidget_bodePlot = MplWidget(self.page_bodePlot)
        self.MplWidget_bodePlot.setObjectName(u"MplWidget_bodePlot")
        sizePolicy14.setHeightForWidth(self.MplWidget_bodePlot.sizePolicy().hasHeightForWidth())
        self.MplWidget_bodePlot.setSizePolicy(sizePolicy14)

        self.verticalLayout_25.addWidget(self.MplWidget_bodePlot)

        self.stackedWidget.addWidget(self.page_bodePlot)
        self.page_parametricAnalysis = QWidget()
        self.page_parametricAnalysis.setObjectName(u"page_parametricAnalysis")
        self.verticalLayoutWidget_14 = QWidget(self.page_parametricAnalysis)
        self.verticalLayoutWidget_14.setObjectName(u"verticalLayoutWidget_14")
        self.verticalLayoutWidget_14.setGeometry(QRect(0, 0, 791, 851))
        self.verticalLayout_24 = QVBoxLayout(self.verticalLayoutWidget_14)
        self.verticalLayout_24.setObjectName(u"verticalLayout_24")
        self.verticalLayout_24.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_20 = QHBoxLayout()
        self.horizontalLayout_20.setObjectName(u"horizontalLayout_20")
        self.pushButton_runCBasedSimulation4PA = QPushButton(self.verticalLayoutWidget_14)
        self.pushButton_runCBasedSimulation4PA.setObjectName(u"pushButton_runCBasedSimulation4PA")
        self.pushButton_runCBasedSimulation4PA.setFont(font11)
        self.pushButton_runCBasedSimulation4PA.setStyleSheet(u"QPushButton {\n"
"	border: 2px solid rgb(52, 59, 72);\n"
"	border-radius: 5px;	\n"
"	background-color: rgb(52, 59, 72);\n"
"}\n"
"QPushButton:hover {\n"
"	background-color: rgb(57, 65, 80);\n"
"	border: 2px solid rgb(61, 70, 86);\n"
"}\n"
"QPushButton:pressed {	\n"
"	background-color: rgb(35, 40, 49);\n"
"	border: 2px solid rgb(43, 50, 61);\n"
"}")

        self.horizontalLayout_20.addWidget(self.pushButton_runCBasedSimulation4PA)

        self.pushButton_plot4PA = QPushButton(self.verticalLayoutWidget_14)
        self.pushButton_plot4PA.setObjectName(u"pushButton_plot4PA")
        sizePolicy15 = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        sizePolicy15.setHorizontalStretch(0)
        sizePolicy15.setVerticalStretch(0)
        sizePolicy15.setHeightForWidth(self.pushButton_plot4PA.sizePolicy().hasHeightForWidth())
        self.pushButton_plot4PA.setSizePolicy(sizePolicy15)
        self.pushButton_plot4PA.setFont(font11)
        self.pushButton_plot4PA.setStyleSheet(u"QPushButton {\n"
"	border: 2px solid rgb(52, 59, 72);\n"
"	border-radius: 5px;	\n"
"	background-color: rgb(52, 59, 72);\n"
"}\n"
"QPushButton:hover {\n"
"	background-color: rgb(57, 65, 80);\n"
"	border: 2px solid rgb(61, 70, 86);\n"
"}\n"
"QPushButton:pressed {	\n"
"	background-color: rgb(35, 40, 49);\n"
"	border: 2px solid rgb(43, 50, 61);\n"
"}")

        self.horizontalLayout_20.addWidget(self.pushButton_plot4PA)


        self.verticalLayout_24.addLayout(self.horizontalLayout_20)

        self.label_ACMLabels_5 = QLabel(self.verticalLayoutWidget_14)
        self.label_ACMLabels_5.setObjectName(u"label_ACMLabels_5")
        font15 = QFont()
        font15.setFamily(u"Times New Roman")
        font15.setPointSize(12)
        font15.setBold(False)
        font15.setWeight(50)
        self.label_ACMLabels_5.setFont(font15)
        self.label_ACMLabels_5.setFrameShape(QFrame.NoFrame)
        self.label_ACMLabels_5.setFrameShadow(QFrame.Plain)
        self.label_ACMLabels_5.setAlignment(Qt.AlignCenter)

        self.verticalLayout_24.addWidget(self.label_ACMLabels_5)

        self.plainTextEdit_PANames = QCodeEditor(self.verticalLayoutWidget_14)
        self.plainTextEdit_PANames.setObjectName(u"plainTextEdit_PANames")
        sizePolicy9.setHeightForWidth(self.plainTextEdit_PANames.sizePolicy().hasHeightForWidth())
        self.plainTextEdit_PANames.setSizePolicy(sizePolicy9)
        self.plainTextEdit_PANames.setFont(font14)
        self.plainTextEdit_PANames.setLineWrapMode(QPlainTextEdit.NoWrap)

        self.verticalLayout_24.addWidget(self.plainTextEdit_PANames)

        self.label_ACMLabels_6 = QLabel(self.verticalLayoutWidget_14)
        self.label_ACMLabels_6.setObjectName(u"label_ACMLabels_6")
        self.label_ACMLabels_6.setFont(font15)
        self.label_ACMLabels_6.setFrameShape(QFrame.NoFrame)
        self.label_ACMLabels_6.setFrameShadow(QFrame.Plain)
        self.label_ACMLabels_6.setAlignment(Qt.AlignCenter)

        self.verticalLayout_24.addWidget(self.label_ACMLabels_6)

        self.plainTextEdit_PAValues = QCodeEditor(self.verticalLayoutWidget_14)
        self.plainTextEdit_PAValues.setObjectName(u"plainTextEdit_PAValues")
        sizePolicy.setHeightForWidth(self.plainTextEdit_PAValues.sizePolicy().hasHeightForWidth())
        self.plainTextEdit_PAValues.setSizePolicy(sizePolicy)
        self.plainTextEdit_PAValues.setFont(font14)
        self.plainTextEdit_PAValues.setLineWrapMode(QPlainTextEdit.NoWrap)

        self.verticalLayout_24.addWidget(self.plainTextEdit_PAValues)

        self.stackedWidget.addWidget(self.page_parametricAnalysis)
        self.page_PyBasedSimulation = QWidget()
        self.page_PyBasedSimulation.setObjectName(u"page_PyBasedSimulation")
        self.plainTextEdit_NumbaScopeDict = QCodeEditor(self.page_PyBasedSimulation)
        self.plainTextEdit_NumbaScopeDict.setObjectName(u"plainTextEdit_NumbaScopeDict")
        self.plainTextEdit_NumbaScopeDict.setGeometry(QRect(0, 0, 921, 281))
        sizePolicy12.setHeightForWidth(self.plainTextEdit_NumbaScopeDict.sizePolicy().hasHeightForWidth())
        self.plainTextEdit_NumbaScopeDict.setSizePolicy(sizePolicy12)
        self.plainTextEdit_NumbaScopeDict.setFont(font14)
        self.plainTextEdit_NumbaScopeDict.setStyleSheet(u"background: rgb(27, 29, 35);\n"
"\n"
"")
        self.plainTextEdit_NumbaScopeDict.setLineWrapMode(QPlainTextEdit.NoWrap)
        self.plainTextEdit_NumbaScopeDict_2 = QCodeEditor(self.page_PyBasedSimulation)
        self.plainTextEdit_NumbaScopeDict_2.setObjectName(u"plainTextEdit_NumbaScopeDict_2")
        self.plainTextEdit_NumbaScopeDict_2.setGeometry(QRect(0, 280, 921, 511))
        sizePolicy12.setHeightForWidth(self.plainTextEdit_NumbaScopeDict_2.sizePolicy().hasHeightForWidth())
        self.plainTextEdit_NumbaScopeDict_2.setSizePolicy(sizePolicy12)
        self.plainTextEdit_NumbaScopeDict_2.setFont(font14)
        self.plainTextEdit_NumbaScopeDict_2.setStyleSheet(u"background: rgb(27, 29, 35);\n"
"\n"
"")
        self.plainTextEdit_NumbaScopeDict_2.setLineWrapMode(QPlainTextEdit.NoWrap)
        self.plainTextEdit_NumbaScopeDict_2.setReadOnly(True)
        self.stackedWidget.addWidget(self.page_PyBasedSimulation)

        self.verticalLayout_9.addWidget(self.stackedWidget)


        self.verticalLayout_4.addWidget(self.frame_content)

        self.frame_grip = QFrame(self.frame_content_right)
        self.frame_grip.setObjectName(u"frame_grip")
        self.frame_grip.setMinimumSize(QSize(0, 25))
        self.frame_grip.setMaximumSize(QSize(16777215, 25))
        self.frame_grip.setStyleSheet(u"background-color: rgb(33, 37, 43);")
        self.frame_grip.setFrameShape(QFrame.NoFrame)
        self.frame_grip.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_6 = QHBoxLayout(self.frame_grip)
        self.horizontalLayout_6.setSpacing(0)
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.horizontalLayout_6.setContentsMargins(0, 0, 2, 0)
        self.frame_label_bottom = QFrame(self.frame_grip)
        self.frame_label_bottom.setObjectName(u"frame_label_bottom")
        self.frame_label_bottom.setFrameShape(QFrame.NoFrame)
        self.frame_label_bottom.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_7 = QHBoxLayout(self.frame_label_bottom)
        self.horizontalLayout_7.setSpacing(0)
        self.horizontalLayout_7.setObjectName(u"horizontalLayout_7")
        self.horizontalLayout_7.setContentsMargins(10, 0, 10, 0)
        self.label_credits = QLabel(self.frame_label_bottom)
        self.label_credits.setObjectName(u"label_credits")
        self.label_credits.setFont(font3)
        self.label_credits.setStyleSheet(u"color: rgb(98, 103, 111);")

        self.horizontalLayout_7.addWidget(self.label_credits)

        self.label_version = QLabel(self.frame_label_bottom)
        self.label_version.setObjectName(u"label_version")
        self.label_version.setMaximumSize(QSize(100, 16777215))
        self.label_version.setFont(font3)
        self.label_version.setStyleSheet(u"color: rgb(98, 103, 111);")
        self.label_version.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.horizontalLayout_7.addWidget(self.label_version)


        self.horizontalLayout_6.addWidget(self.frame_label_bottom)

        self.frame_size_grip = QFrame(self.frame_grip)
        self.frame_size_grip.setObjectName(u"frame_size_grip")
        self.frame_size_grip.setMaximumSize(QSize(20, 20))
        self.frame_size_grip.setStyleSheet(u"QSizeGrip {\n"
"	background-image: url(:/16x16/icons/16x16/cil-size-grip.png);\n"
"	background-position: center;\n"
"	background-repeat: no-reperat;\n"
"}")
        self.frame_size_grip.setFrameShape(QFrame.NoFrame)
        self.frame_size_grip.setFrameShadow(QFrame.Raised)

        self.horizontalLayout_6.addWidget(self.frame_size_grip)


        self.verticalLayout_4.addWidget(self.frame_grip)


        self.horizontalLayout_2.addWidget(self.frame_content_right)


        self.verticalLayout.addWidget(self.frame_center)


        self.horizontalLayout.addWidget(self.frame_main)

        MainWindow.setCentralWidget(self.centralwidget)
        QWidget.setTabOrder(self.btn_minimize, self.btn_maximize_restore)
        QWidget.setTabOrder(self.btn_maximize_restore, self.btn_close)
        QWidget.setTabOrder(self.btn_close, self.btn_toggle_menu)

        self.retranslateUi(MainWindow)

        self.stackedWidget.setCurrentIndex(9)
        self.tabWidget_3.setCurrentIndex(1)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.btn_toggle_menu.setText("")
        self.label_title_bar_top.setText(QCoreApplication.translate("MainWindow", u"Main Window - Base", None))
        self.pushButton_ShowFloatingConsole_AtTop.setText(QCoreApplication.translate("MainWindow", u"Console", None))
        self.pushButton_runPyBasedSimulation_AtTop.setText(QCoreApplication.translate("MainWindow", u"Numba", None))
        self.pushButton_SaveAtTop.setText(QCoreApplication.translate("MainWindow", u"Save", None))
        self.pushButton_runCBasedSimulation_AtTop.setText(QCoreApplication.translate("MainWindow", u"Build", None))
        self.pushButton_ACMPlotHereAtTop.setText(QCoreApplication.translate("MainWindow", u"Plot", None))
#if QT_CONFIG(tooltip)
        self.btn_minimize.setToolTip(QCoreApplication.translate("MainWindow", u"Minimize", None))
#endif // QT_CONFIG(tooltip)
        self.btn_minimize.setText("")
#if QT_CONFIG(tooltip)
        self.btn_maximize_restore.setToolTip(QCoreApplication.translate("MainWindow", u"Maximize", None))
#endif // QT_CONFIG(tooltip)
        self.btn_maximize_restore.setText("")
#if QT_CONFIG(tooltip)
        self.btn_close.setToolTip(QCoreApplication.translate("MainWindow", u"Close", None))
#endif // QT_CONFIG(tooltip)
        self.btn_close.setText("")
        self.label_top_info_1.setText(QCoreApplication.translate("MainWindow", u"C:\\Program Files\\Blender Foundation\\Blender 2.82", None))
        self.label_top_info_2.setText(QCoreApplication.translate("MainWindow", u"| C Based Simulation", None))
        self.label_user_icon.setText(QCoreApplication.translate("MainWindow", u"CJH", None))
        self.label_6.setText(QCoreApplication.translate("MainWindow", u"emachinery v2", None))
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"by Jiahao Chen", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"Home", None))
        self.label_7.setText(QCoreApplication.translate("MainWindow", u"Page Index 0", None))
        self.labelBoxBlenderInstalation.setText(QCoreApplication.translate("MainWindow", u"BLENDER INSTALLATION", None))
        self.lineEdit.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Your Password", None))
        self.pushButton.setText(QCoreApplication.translate("MainWindow", u"Open Blender", None))
        self.labelVersion_3.setText(QCoreApplication.translate("MainWindow", u"Ex: C:Program FilesBlender FoundationBlender 2.82 blender.exe", None))
        self.checkBox.setText(QCoreApplication.translate("MainWindow", u"CheckBox", None))
        self.radioButton.setText(QCoreApplication.translate("MainWindow", u"RadioButton", None))
        self.comboBox.setItemText(0, QCoreApplication.translate("MainWindow", u"Test 1", None))
        self.comboBox.setItemText(1, QCoreApplication.translate("MainWindow", u"Test 2", None))
        self.comboBox.setItemText(2, QCoreApplication.translate("MainWindow", u"Test 3", None))

        self.commandLinkButton.setText(QCoreApplication.translate("MainWindow", u"CommandLinkButton", None))
        self.commandLinkButton.setDescription(QCoreApplication.translate("MainWindow", u"Open External Link", None))
        ___qtablewidgetitem = self.tableWidget.horizontalHeaderItem(0)
        ___qtablewidgetitem.setText(QCoreApplication.translate("MainWindow", u"0", None));
        ___qtablewidgetitem1 = self.tableWidget.horizontalHeaderItem(1)
        ___qtablewidgetitem1.setText(QCoreApplication.translate("MainWindow", u"1", None));
        ___qtablewidgetitem2 = self.tableWidget.horizontalHeaderItem(2)
        ___qtablewidgetitem2.setText(QCoreApplication.translate("MainWindow", u"2", None));
        ___qtablewidgetitem3 = self.tableWidget.horizontalHeaderItem(3)
        ___qtablewidgetitem3.setText(QCoreApplication.translate("MainWindow", u"3", None));
        ___qtablewidgetitem4 = self.tableWidget.verticalHeaderItem(0)
        ___qtablewidgetitem4.setText(QCoreApplication.translate("MainWindow", u"New Row", None));
        ___qtablewidgetitem5 = self.tableWidget.verticalHeaderItem(1)
        ___qtablewidgetitem5.setText(QCoreApplication.translate("MainWindow", u"New Row", None));
        ___qtablewidgetitem6 = self.tableWidget.verticalHeaderItem(2)
        ___qtablewidgetitem6.setText(QCoreApplication.translate("MainWindow", u"New Row", None));
        ___qtablewidgetitem7 = self.tableWidget.verticalHeaderItem(3)
        ___qtablewidgetitem7.setText(QCoreApplication.translate("MainWindow", u"New Row", None));
        ___qtablewidgetitem8 = self.tableWidget.verticalHeaderItem(4)
        ___qtablewidgetitem8.setText(QCoreApplication.translate("MainWindow", u"New Row", None));
        ___qtablewidgetitem9 = self.tableWidget.verticalHeaderItem(5)
        ___qtablewidgetitem9.setText(QCoreApplication.translate("MainWindow", u"New Row", None));
        ___qtablewidgetitem10 = self.tableWidget.verticalHeaderItem(6)
        ___qtablewidgetitem10.setText(QCoreApplication.translate("MainWindow", u"New Row", None));
        ___qtablewidgetitem11 = self.tableWidget.verticalHeaderItem(7)
        ___qtablewidgetitem11.setText(QCoreApplication.translate("MainWindow", u"New Row", None));
        ___qtablewidgetitem12 = self.tableWidget.verticalHeaderItem(8)
        ___qtablewidgetitem12.setText(QCoreApplication.translate("MainWindow", u"New Row", None));
        ___qtablewidgetitem13 = self.tableWidget.verticalHeaderItem(9)
        ___qtablewidgetitem13.setText(QCoreApplication.translate("MainWindow", u"New Row", None));
        ___qtablewidgetitem14 = self.tableWidget.verticalHeaderItem(10)
        ___qtablewidgetitem14.setText(QCoreApplication.translate("MainWindow", u"New Row", None));
        ___qtablewidgetitem15 = self.tableWidget.verticalHeaderItem(11)
        ___qtablewidgetitem15.setText(QCoreApplication.translate("MainWindow", u"New Row", None));
        ___qtablewidgetitem16 = self.tableWidget.verticalHeaderItem(12)
        ___qtablewidgetitem16.setText(QCoreApplication.translate("MainWindow", u"New Row", None));
        ___qtablewidgetitem17 = self.tableWidget.verticalHeaderItem(13)
        ___qtablewidgetitem17.setText(QCoreApplication.translate("MainWindow", u"New Row", None));
        ___qtablewidgetitem18 = self.tableWidget.verticalHeaderItem(14)
        ___qtablewidgetitem18.setText(QCoreApplication.translate("MainWindow", u"New Row", None));
        ___qtablewidgetitem19 = self.tableWidget.verticalHeaderItem(15)
        ___qtablewidgetitem19.setText(QCoreApplication.translate("MainWindow", u"New Row", None));

        __sortingEnabled = self.tableWidget.isSortingEnabled()
        self.tableWidget.setSortingEnabled(False)
        ___qtablewidgetitem20 = self.tableWidget.item(0, 0)
        ___qtablewidgetitem20.setText(QCoreApplication.translate("MainWindow", u"Test", None));
        ___qtablewidgetitem21 = self.tableWidget.item(0, 1)
        ___qtablewidgetitem21.setText(QCoreApplication.translate("MainWindow", u"Text", None));
        ___qtablewidgetitem22 = self.tableWidget.item(0, 2)
        ___qtablewidgetitem22.setText(QCoreApplication.translate("MainWindow", u"Cell", None));
        ___qtablewidgetitem23 = self.tableWidget.item(0, 3)
        ___qtablewidgetitem23.setText(QCoreApplication.translate("MainWindow", u"Line", None));
        self.tableWidget.setSortingEnabled(__sortingEnabled)

        self.comboBox_MachineType.setItemText(0, QCoreApplication.translate("MainWindow", u"Induction Machine", None))
        self.comboBox_MachineType.setItemText(1, QCoreApplication.translate("MainWindow", u"Synchronous Machine", None))

        self.label_npd.setText(QCoreApplication.translate("MainWindow", u"Number of Pole Pairs", None))
        self.label_npd_2.setText(QCoreApplication.translate("MainWindow", u"Rated Current [Arms]", None))
        self.label_npd_3.setText(QCoreApplication.translate("MainWindow", u"Rated Power [W]", None))
        self.label_npd_4.setText(QCoreApplication.translate("MainWindow", u"Rated Speed [rpm]", None))
        self.lineEdit_npp.setText(QCoreApplication.translate("MainWindow", u"0", None))
        self.lineEdit_RatedCurrent.setText(QCoreApplication.translate("MainWindow", u"0", None))
        self.lineEdit_RatedPower.setText(QCoreApplication.translate("MainWindow", u"0", None))
        self.lineEdit_RatedSpeed.setText(QCoreApplication.translate("MainWindow", u"0", None))
        self.pushButton_updateModel.setText(QCoreApplication.translate("MainWindow", u"Update Model", None))
        self.label_pushedVariables0.setText(QCoreApplication.translate("MainWindow", u"Variables Pushed qtConsole: ", None))
        self.label_pushedVariables.setText(QCoreApplication.translate("MainWindow", u"None", None))
        self.groupBox_5.setTitle(QCoreApplication.translate("MainWindow", u"Input", None))
        self.label_math_delta.setText(QCoreApplication.translate("MainWindow", u"Dampling Factor \u03b4 [1]", None))
        self.lineEdit_dampingFactor_delta.setText(QCoreApplication.translate("MainWindow", u"6.5", None))
        self.label_desiredVLBW.setText(QCoreApplication.translate("MainWindow", u"Desired Velocity Loop Bandwidth [Hz]", None))
        self.lineEdit_desiredVLBW.setText(QCoreApplication.translate("MainWindow", u"40", None))
        self.label_CLTS.setText(QCoreApplication.translate("MainWindow", u"Current Loop TS [1/Hz]", None))
        self.lineEdit_CLTS.setText(QCoreApplication.translate("MainWindow", u"1/10e3", None))
        self.label_VLTS.setText(QCoreApplication.translate("MainWindow", u"Velocity Loop TS [1/Hz]]", None))
        self.lineEdit_VLTS.setText(QCoreApplication.translate("MainWindow", u"4/10e3", None))
        self.pushButton_pidTuner.setText(QCoreApplication.translate("MainWindow", u"Get Output", None))
        self.groupBox_6.setTitle(QCoreApplication.translate("MainWindow", u"Theory", None))
        self.label_qpix_CLKP.setText("")
        self.label_qpix_CLKI.setText("")
        self.label_qpix_VLKP.setText("")
        self.label_qpix_VLKI.setText("")
        self.label_qpix_Note1.setText("")
        self.label_qpix_Note2.setText("")
        self.label_qpix_Note3.setText("")
        self.groupBox_4.setTitle(QCoreApplication.translate("MainWindow", u"Output", None))
        self.label_8.setText(QCoreApplication.translate("MainWindow", u"Current Loop Bandwidth [Hz]", None))
        self.lineEdit_CLBW.setText(QCoreApplication.translate("MainWindow", u"0", None))
        self.label_10.setText(QCoreApplication.translate("MainWindow", u"Current KP", None))
        self.lineEdit_currentKP.setText(QCoreApplication.translate("MainWindow", u"0", None))
        self.label_13.setText(QCoreApplication.translate("MainWindow", u"Current KI", None))
        self.lineEdit_currentKI.setText(QCoreApplication.translate("MainWindow", u"0", None))
        self.label_9.setText(QCoreApplication.translate("MainWindow", u"Speed KP", None))
        self.lineEdit_speedKP.setText(QCoreApplication.translate("MainWindow", u"0", None))
        self.label_14.setText(QCoreApplication.translate("MainWindow", u"Speed KI", None))
        self.lineEdit_speedKI.setText(QCoreApplication.translate("MainWindow", u"0", None))
        self.label_16.setText(QCoreApplication.translate("MainWindow", u"Velocity Loop Bandwidth [Hz]", None))
        self.lineEdit_designedVLBW.setText(QCoreApplication.translate("MainWindow", u"0", None))
        self.groupBox_3.setTitle(QCoreApplication.translate("MainWindow", u"User Tuning", None))
        self.label_15.setText(QCoreApplication.translate("MainWindow", u"\u4e0a\u4f4d\u673aCurrent KP", None))
        self.lineEdit_PC_currentKP.setText(QCoreApplication.translate("MainWindow", u"0", None))
        self.label_17.setText(QCoreApplication.translate("MainWindow", u"\u4e0a\u4f4d\u673aCurrent KI", None))
        self.lineEdit_PC_currentKI.setText(QCoreApplication.translate("MainWindow", u"0", None))
        self.label_18.setText(QCoreApplication.translate("MainWindow", u"\u4e0a\u4f4d\u673aSpeed KP", None))
        self.lineEdit_PC_speedKP.setText(QCoreApplication.translate("MainWindow", u"0", None))
        self.label_19.setText(QCoreApplication.translate("MainWindow", u"\u4e0a\u4f4d\u673aSpeed KI", None))
        self.lineEdit_PC_speedKI.setText(QCoreApplication.translate("MainWindow", u"0", None))
        self.label__path2boptPython_3.setText(QCoreApplication.translate("MainWindow", u"Path to acmsimc", None))
        self.lineEdit_path2acmsimc.setText(QCoreApplication.translate("MainWindow", u"D:\\DrH\\Codes\\emachineryTestPYPI\\emachinery\\acmsimcv5", None))
        self.label_11.setText(QCoreApplication.translate("MainWindow", u"Selected Machine Name", None))
        self.label_12.setText(QCoreApplication.translate("MainWindow", u"Control Strategy", None))
        self.lineEdit_ControlStrategy.setText(QCoreApplication.translate("MainWindow", u"MARINO_2005_ADAPTIVE_SENSORLESS_CONTROL", None))
        self.label_EndTime.setText(QCoreApplication.translate("MainWindow", u"End Time [s]", None))
        self.lineEdit_EndTime.setText(QCoreApplication.translate("MainWindow", u"4", None))
        self.label_npd_19.setText(QCoreApplication.translate("MainWindow", u"Load Inertia Percentage [%]", None))
        self.lineEdit_LoadInertiaPercentage.setText(QCoreApplication.translate("MainWindow", u"16", None))
        self.label_npd_20.setText(QCoreApplication.translate("MainWindow", u"Load Torque [Nm]", None))
        self.lineEdit_LoadTorque.setText(QCoreApplication.translate("MainWindow", u"0.0", None))
        self.label_npd_21.setText(QCoreApplication.translate("MainWindow", u"Viscous Coefficient [Nm/elec.rad*s]", None))
        self.lineEdit_ViscousCoefficient.setText(QCoreApplication.translate("MainWindow", u"0.7e-4", None))
        self.label_npd_22.setText(QCoreApplication.translate("MainWindow", u"Flux Cmd: m0 [%KE], m1 [%m0], \u03c91 [Hz]", None))
        self.lineEdit_FluxCmdDetails.setText(QCoreApplication.translate("MainWindow", u"(100, 0, 10)", None))
        self.label_npd_23.setText(QCoreApplication.translate("MainWindow", u"Flux Cmd. Sine Part Percentage [%]", None))
        self.lineEdit_FluxCmdSinePartPercentage.setText(QCoreApplication.translate("MainWindow", u"0", None))
        self.label_npd_24.setText(QCoreApplication.translate("MainWindow", u"DC Bus Voltage [Vdc]", None))
        self.lineEdit_DCBusVoltage.setText(QCoreApplication.translate("MainWindow", u"48", None))
        self.label_npd_25.setText(QCoreApplication.translate("MainWindow", u"Output File Name Prefix@acmsimc", None))
        self.lineEdit_OutputDataFileName.setText(QCoreApplication.translate("MainWindow", u"DefaultOutputFileName", None))
        self.checkBox_compileAndRun.setText(QCoreApplication.translate("MainWindow", u"Sve Configurations, Compile and Run", None))
        self.pushButton_runCBasedSimulation.setText(QCoreApplication.translate("MainWindow", u"Go!", None))
        self.groupBox_2.setTitle(QCoreApplication.translate("MainWindow", u"Select Excitation:", None))
        self.radioButton_Excitation_Velocity.setText(QCoreApplication.translate("MainWindow", u"Velocity", None))
        self.radioButton_Excitation_Position.setText(QCoreApplication.translate("MainWindow", u"Position", None))
        self.radioButton_Excitation_SweepFrequency.setText(QCoreApplication.translate("MainWindow", u"Sweep Frequency", None))
        ___qtablewidgetitem24 = self.tableWidget_Uncertainty.horizontalHeaderItem(0)
        ___qtablewidgetitem24.setText(QCoreApplication.translate("MainWindow", u"Uncertainty [%]", None));
        ___qtablewidgetitem25 = self.tableWidget_Uncertainty.verticalHeaderItem(0)
        ___qtablewidgetitem25.setText(QCoreApplication.translate("MainWindow", u"rs", None));
        ___qtablewidgetitem26 = self.tableWidget_Uncertainty.verticalHeaderItem(1)
        ___qtablewidgetitem26.setText(QCoreApplication.translate("MainWindow", u"rreq", None));
        ___qtablewidgetitem27 = self.tableWidget_Uncertainty.verticalHeaderItem(2)
        ___qtablewidgetitem27.setText(QCoreApplication.translate("MainWindow", u"Lmu", None));
        ___qtablewidgetitem28 = self.tableWidget_Uncertainty.verticalHeaderItem(3)
        ___qtablewidgetitem28.setText(QCoreApplication.translate("MainWindow", u"Lsigma", None));

        __sortingEnabled1 = self.tableWidget_Uncertainty.isSortingEnabled()
        self.tableWidget_Uncertainty.setSortingEnabled(False)
        ___qtablewidgetitem29 = self.tableWidget_Uncertainty.item(0, 0)
        ___qtablewidgetitem29.setText(QCoreApplication.translate("MainWindow", u"100", None));
        ___qtablewidgetitem30 = self.tableWidget_Uncertainty.item(1, 0)
        ___qtablewidgetitem30.setText(QCoreApplication.translate("MainWindow", u"100", None));
        ___qtablewidgetitem31 = self.tableWidget_Uncertainty.item(2, 0)
        ___qtablewidgetitem31.setText(QCoreApplication.translate("MainWindow", u"100", None));
        ___qtablewidgetitem32 = self.tableWidget_Uncertainty.item(3, 0)
        ___qtablewidgetitem32.setText(QCoreApplication.translate("MainWindow", u"100", None));
        self.tableWidget_Uncertainty.setSortingEnabled(__sortingEnabled1)

        self.groupBox_sweepFrequency.setTitle(QCoreApplication.translate("MainWindow", u"Settings", None))
        self.radioButton_openLoop.setText(QCoreApplication.translate("MainWindow", u"Open loop", None))
        self.radioButton_currentLoopOnly.setText(QCoreApplication.translate("MainWindow", u"Current Loop Only", None))
        self.label_maxFreq2Sweep.setText(QCoreApplication.translate("MainWindow", u"Max Freq [Hz]", None))
        self.lineEdit_maxFreq2Sweep.setText(QCoreApplication.translate("MainWindow", u"200", None))
        self.label_PANameSelected.setText("")
        self.lineEdit_PAValueSelected_2.setText("")
        self.pushButton_123123.setText(QCoreApplication.translate("MainWindow", u"Plot Here", None))
        self.tabWidget_3.setTabText(self.tabWidget_3.indexOf(self.tab_11), QCoreApplication.translate("MainWindow", u"Tab 1", None))
        self.label_PANameSelected_2.setText("")
        self.lineEdit_PAValueSelected.setText("")
        self.pushButton_ACMPlotHere.setText(QCoreApplication.translate("MainWindow", u"Plot Here", None))
        self.tabWidget_3.setTabText(self.tabWidget_3.indexOf(self.tab_12), QCoreApplication.translate("MainWindow", u"Parametric Analysis", None))
        self.comboBox_PlotSettingSelect.setItemText(0, QCoreApplication.translate("MainWindow", u"None", None))

        self.lineEdit_plotSettingName.setText(QCoreApplication.translate("MainWindow", u"untitled", None))
        self.label__path2boptPython_9.setText(QCoreApplication.translate("MainWindow", u"Path to plot labels file", None))
        self.lineEdit_path2ACMPlotLabels.setText(QCoreApplication.translate("MainWindow", u"./plot_setting_files/labels.txt", None))
        self.label_ACMLabels_3.setText(QCoreApplication.translate("MainWindow", u"Labels", None))
        self.plainTextEdit_ACMPlotLabels.setPlainText(QCoreApplication.translate("MainWindow", u"None", None))
        self.label__path2boptPython_10.setText(QCoreApplication.translate("MainWindow", u"Path to plot signals file", None))
        self.lineEdit_path2ACMPlotSignals.setText(QCoreApplication.translate("MainWindow", u"./plot_setting_files/signals.txt", None))
        self.label_ACMLabels_4.setText(QCoreApplication.translate("MainWindow", u"Signals", None))
        self.plainTextEdit_ACMPlotDetails.setPlainText(QCoreApplication.translate("MainWindow", u"None", None))
        self.pushButton_getSignal.setText(QCoreApplication.translate("MainWindow", u"Generate\n"
"Signals", None))
        self.checkBox_LissajousPlot_2.setText(QCoreApplication.translate("MainWindow", u"CheckBox", None))
        self.pushButton_LissajousPlot.setText(QCoreApplication.translate("MainWindow", u"Lissajous Plot", None))
        self.plainTextEdit_LissajousPlotSignals.setPlainText(QCoreApplication.translate("MainWindow", u"[(\"ACM.psi_Amu\",\"ACM.psi_Bmu\"),(\"clest.psi_2[0]\",\"clest.psi_2[1]\")]", None))
        self.pushButton_bodePlot.setText(QCoreApplication.translate("MainWindow", u"Bode Plot by Sweep Freuquency", None))
        self.pushButton_runCBasedSimulation4PA.setText(QCoreApplication.translate("MainWindow", u"Go!", None))
        self.pushButton_plot4PA.setText(QCoreApplication.translate("MainWindow", u"Alreay have data? Plot!", None))
        self.label_ACMLabels_5.setText(QCoreApplication.translate("MainWindow", u"Parameter Name Tuple [e.g., (\"TIME\", \"ESTIMATOR_USED\")]", None))
        self.plainTextEdit_PANames.setPlainText(QCoreApplication.translate("MainWindow", u"()", None))
        self.label_ACMLabels_6.setText(QCoreApplication.translate("MainWindow", u"Values {e.g., [(10,\"HTZ\"), (20,\"OHTANI\"), (30,\"CHEN\")]}", None))
        self.plainTextEdit_PAValues.setPlainText(QCoreApplication.translate("MainWindow", u"[()]", None))
        self.plainTextEdit_NumbaScopeDict.setPlainText(QCoreApplication.translate("MainWindow", u"numba__scope_dict = OD([\n"
"(r'Speed [rpm]',                  ( 'CTRL.cmd_rpm', 'CTRL.omega_elec', 'OB.x[1]'     ,) ),\n"
"(r'Position [rad]',               ( 'ACM.x[3]', 'OB.theta_d' ,)  ),\n"
"(r'$q$-axis current [A]',         ( 'ACM.x[1]', 'CTRL.idq[1]', 'CTRL.cmd_idq[1]'     ,) ),\n"
"(r'$d$-axis current [A]',         ( 'ACM.x[0]', 'CTRL.idq[0]', 'CTRL.cmd_idq[0]'     ,) ),\n"
"(r'$\\alpha\\beta$ current [A]',    ( 'CTRL.iab[0]', 'CTRL.iab[1]',)  ),\n"
"])", None))
        self.plainTextEdit_NumbaScopeDict_2.setPlainText(QCoreApplication.translate("MainWindow", u"Watch_Mapping = [\n"
"    '[A]=ACM.x[0]', # id\n"
"    '[A]=ACM.x[1]', # iq\n"
"    '[rad/s]=ACM.x[2]', # omega_elec\n"
"    '[rad]=ACM.x[3]', # thete_d\n"
"    '[rad]=ACM.x[4]', # theta_mech\n"
"    '[Wb]=ACM.x[5]', # KActive\n"
"    '[A]=CTRL.iab[0]',\n"
"    '[A]=CTRL.iab[1]',\n"
"    '[A]=CTRL.idq[0]',\n"
"    '[A]=CTRL.idq[1]',\n"
"    '[rpm]=CTRL.theta_d',\n"
"    '[rpm]=CTRL.omega_elec',\n"
"    '[rpm]=CTRL.cmd_rpm',\n"
"    '[A]=CTRL.cmd_idq[0]',\n"
"    '[A]=CTRL.cmd_idq[1]',\n"
"    '[rad]=OB.xspeed[0]',  # theta_d\n"
"    '[rpm]=OB.xspeed[1]',  # omega_elec\n"
"    '[Nm]=OB.xspeed[2]',   # -TL\n"
"    '[Nm/s]=OB.xspeed[3]', # DL\n"
"    '[Wb]=CTRL.KActive',\n"
"    '[Wb]=CTRL.KE',\n"
"    '[Wb]=OB.xflux[0]', # stator flux[0]\n"
"    '[Wb]=OB.xflux[1]', # stator flux[1]\n"
"    '[V]=OB.xflux[2]', # I term\n"
"    '[V]=OB.xflux[3]', # I term\n"
"    '[Wb]=OB.active_flux[0]', # active flux[0]\n"
"    '[Wb]=OB.active_flux[1]', # active flux[1]\n"
"    '[rad]=OB.theta_d', # d-axis position\n"
"]", None))
        self.label_credits.setText(QCoreApplication.translate("MainWindow", u"Gui Base Credit to: Wanderson M. Pimenta", None))
        self.label_version.setText(QCoreApplication.translate("MainWindow", u"v2.0.0", None))
    # retranslateUi

