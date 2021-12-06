# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'device_tab.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *

from pyqtgraph import GraphicsLayoutWidget


class Ui_DeviceTab(object):
    def setupUi(self, DeviceTab):
        if not DeviceTab.objectName():
            DeviceTab.setObjectName(u"DeviceTab")
        DeviceTab.resize(1046, 537)
        self.actionSetUserTag1 = QAction(DeviceTab)
        self.actionSetUserTag1.setObjectName(u"actionSetUserTag1")
        self.actionSetUserTag2 = QAction(DeviceTab)
        self.actionSetUserTag2.setObjectName(u"actionSetUserTag2")
        self.actionEditDeviceSettings = QAction(DeviceTab)
        self.actionEditDeviceSettings.setObjectName(u"actionEditDeviceSettings")
        self.actionShowDeviceInfo = QAction(DeviceTab)
        self.actionShowDeviceInfo.setObjectName(u"actionShowDeviceInfo")
        self.actionFirmwareLatestStable = QAction(DeviceTab)
        self.actionFirmwareLatestStable.setObjectName(u"actionFirmwareLatestStable")
        self.actionFirmwareLatestStable.setEnabled(False)
        self.actionShowPacketStats = QAction(DeviceTab)
        self.actionShowPacketStats.setObjectName(u"actionShowPacketStats")
        self.actionChangeActiveStreams = QAction(DeviceTab)
        self.actionChangeActiveStreams.setObjectName(u"actionChangeActiveStreams")
        self.actionRunTests = QAction(DeviceTab)
        self.actionRunTests.setObjectName(u"actionRunTests")
        self.actionSetDeviceMode = QAction(DeviceTab)
        self.actionSetDeviceMode.setObjectName(u"actionSetDeviceMode")
        self.actionSetDeviceMode.setEnabled(False)
        self.actionFirmwareFromBranch = QAction(DeviceTab)
        self.actionFirmwareFromBranch.setObjectName(u"actionFirmwareFromBranch")
        self.actionFirmwareFromBranch.setEnabled(False)
        self.actionFirmwareFromCommit = QAction(DeviceTab)
        self.actionFirmwareFromCommit.setObjectName(u"actionFirmwareFromCommit")
        self.actionFirmwareFromCommit.setEnabled(False)
        self.actionFirmwareFromFile = QAction(DeviceTab)
        self.actionFirmwareFromFile.setObjectName(u"actionFirmwareFromFile")
        self.actionFirmwareFromFile.setEnabled(False)
        self.actionForceRunBootloader = QAction(DeviceTab)
        self.actionForceRunBootloader.setObjectName(u"actionForceRunBootloader")
        self.actionForceRunBootloader.setEnabled(False)
        self.actionForceRunApplication = QAction(DeviceTab)
        self.actionForceRunApplication.setObjectName(u"actionForceRunApplication")
        self.actionForceRunApplication.setEnabled(False)
        self.actionForceReset = QAction(DeviceTab)
        self.actionForceReset.setObjectName(u"actionForceReset")
        self.actionRaiseException = QAction(DeviceTab)
        self.actionRaiseException.setObjectName(u"actionRaiseException")
        self.actionRecoverNVM = QAction(DeviceTab)
        self.actionRecoverNVM.setObjectName(u"actionRecoverNVM")
        self.actionCalibrate = QAction(DeviceTab)
        self.actionCalibrate.setObjectName(u"actionCalibrate")
        self.actionCalibrate.setCheckable(True)
        self.actionCalibrate.setEnabled(False)
        self.actionShakerCalibrate = QAction(DeviceTab)
        self.actionShakerCalibrate.setObjectName(u"actionShakerCalibrate")
        self.actionShakerCalibrate.setEnabled(False)
        self.actionCopySerialNumber = QAction(DeviceTab)
        self.actionCopySerialNumber.setObjectName(u"actionCopySerialNumber")
        self.actionFlushLostPackets = QAction(DeviceTab)
        self.actionFlushLostPackets.setObjectName(u"actionFlushLostPackets")
        self.actionRFTest = QAction(DeviceTab)
        self.actionRFTest.setObjectName(u"actionRFTest")
        self.verticalLayout_2 = QVBoxLayout(DeviceTab)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setSpacing(3)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(6, 6, 6, 6)
        self.graphChannelLabel = QLabel(DeviceTab)
        self.graphChannelLabel.setObjectName(u"graphChannelLabel")

        self.horizontalLayout.addWidget(self.graphChannelLabel)

        self.graphChannelComboBox = QComboBox(DeviceTab)
        self.graphChannelComboBox.setObjectName(u"graphChannelComboBox")
        self.graphChannelComboBox.setMinimumSize(QSize(150, 0))
        self.graphChannelComboBox.setMaxVisibleItems(20)

        self.horizontalLayout.addWidget(self.graphChannelComboBox)

        self.horizontalSpacer_2 = QSpacerItem(20, 1, QSizePolicy.Fixed, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer_2)

        self.fftSubchannelLabel = QLabel(DeviceTab)
        self.fftSubchannelLabel.setObjectName(u"fftSubchannelLabel")

        self.horizontalLayout.addWidget(self.fftSubchannelLabel)

        self.fftSubchannelComboBox = QComboBox(DeviceTab)
        self.fftSubchannelComboBox.setObjectName(u"fftSubchannelComboBox")
        self.fftSubchannelComboBox.setMinimumSize(QSize(150, 0))
        self.fftSubchannelComboBox.setMaxVisibleItems(20)

        self.horizontalLayout.addWidget(self.fftSubchannelComboBox)

        self.horizontalSpacer_5 = QSpacerItem(20, 1, QSizePolicy.MinimumExpanding, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer_5)

        self.nvmModifiedIndicator = QLabel(DeviceTab)
        self.nvmModifiedIndicator.setObjectName(u"nvmModifiedIndicator")
        self.nvmModifiedIndicator.setStyleSheet(u"QLabel {\n"
"	background-color: yellow;\n"
"	color: black;\n"
"	font-weight: bold;\n"
"	font-size: 12px;\n"
"    border: 1px solid;\n"
"}")
        self.nvmModifiedIndicator.setMargin(5)

        self.horizontalLayout.addWidget(self.nvmModifiedIndicator)

        self.bootloaderIndicator = QLabel(DeviceTab)
        self.bootloaderIndicator.setObjectName(u"bootloaderIndicator")
        self.bootloaderIndicator.setStyleSheet(u"QLabel {\n"
"	background-color: yellow;\n"
"	color: black;\n"
"	font-weight: bold;\n"
"	font-size: 12px;\n"
"    border: 1px solid;\n"
"}")
        self.bootloaderIndicator.setMargin(5)

        self.horizontalLayout.addWidget(self.bootloaderIndicator)

        self.horizontalSpacer = QSpacerItem(20, 1, QSizePolicy.Fixed, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.editDeviceSettings = QToolButton(DeviceTab)
        self.editDeviceSettings.setObjectName(u"editDeviceSettings")
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.editDeviceSettings.sizePolicy().hasHeightForWidth())
        self.editDeviceSettings.setSizePolicy(sizePolicy)
        self.editDeviceSettings.setIconSize(QSize(24, 24))
        self.editDeviceSettings.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)

        self.horizontalLayout.addWidget(self.editDeviceSettings)

        self.menuButton = QPushButton(DeviceTab)
        self.menuButton.setObjectName(u"menuButton")
        self.menuButton.setEnabled(False)
        sizePolicy1 = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.menuButton.sizePolicy().hasHeightForWidth())
        self.menuButton.setSizePolicy(sizePolicy1)

        self.horizontalLayout.addWidget(self.menuButton)

        self.closeButton = QPushButton(DeviceTab)
        self.closeButton.setObjectName(u"closeButton")
        sizePolicy1.setHeightForWidth(self.closeButton.sizePolicy().hasHeightForWidth())
        self.closeButton.setSizePolicy(sizePolicy1)

        self.horizontalLayout.addWidget(self.closeButton)


        self.verticalLayout_2.addLayout(self.horizontalLayout)

        self.stackedWidget = QStackedWidget(DeviceTab)
        self.stackedWidget.setObjectName(u"stackedWidget")
        self.disconnectPage = QWidget()
        self.disconnectPage.setObjectName(u"disconnectPage")
        self.horizontalLayout_4 = QHBoxLayout(self.disconnectPage)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.horizontalSpacer_6 = QSpacerItem(0, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_4.addItem(self.horizontalSpacer_6)

        self.verticalLayout_3 = QVBoxLayout()
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalSpacer_4 = QSpacerItem(20, 0, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_3.addItem(self.verticalSpacer_4)

        self.statusLabel = QLabel(self.disconnectPage)
        self.statusLabel.setObjectName(u"statusLabel")
        font = QFont()
        font.setBold(True)
        font.setWeight(75)
        self.statusLabel.setFont(font)
        self.statusLabel.setAlignment(Qt.AlignCenter)

        self.verticalLayout_3.addWidget(self.statusLabel)

        self.statusProgressBar = QProgressBar(self.disconnectPage)
        self.statusProgressBar.setObjectName(u"statusProgressBar")
        sizePolicy2 = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.statusProgressBar.sizePolicy().hasHeightForWidth())
        self.statusProgressBar.setSizePolicy(sizePolicy2)
        self.statusProgressBar.setMinimumSize(QSize(175, 0))
        self.statusProgressBar.setValue(24)
        self.statusProgressBar.setAlignment(Qt.AlignCenter)

        self.verticalLayout_3.addWidget(self.statusProgressBar)

        self.verticalSpacer_2 = QSpacerItem(20, 0, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_3.addItem(self.verticalSpacer_2)


        self.horizontalLayout_4.addLayout(self.verticalLayout_3)

        self.horizontalSpacer_3 = QSpacerItem(0, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_4.addItem(self.horizontalSpacer_3)

        self.stackedWidget.addWidget(self.disconnectPage)
        self.displayPage = QWidget()
        self.displayPage.setObjectName(u"displayPage")
        self.verticalLayout = QVBoxLayout(self.displayPage)
        self.verticalLayout.setSpacing(3)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.panelLayout = QHBoxLayout()
        self.panelLayout.setSpacing(6)
        self.panelLayout.setObjectName(u"panelLayout")
        self.graphicsLayout = GraphicsLayoutWidget(self.displayPage)
        self.graphicsLayout.setObjectName(u"graphicsLayout")

        self.panelLayout.addWidget(self.graphicsLayout)

        self.panelLayout.setStretch(0, 1)

        self.verticalLayout.addLayout(self.panelLayout)

        self.horizontalLayout_6 = QHBoxLayout()
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.line_2 = QFrame(self.displayPage)
        self.line_2.setObjectName(u"line_2")
        self.line_2.setFrameShape(QFrame.HLine)
        self.line_2.setFrameShadow(QFrame.Sunken)

        self.horizontalLayout_6.addWidget(self.line_2)

        self.collapseButton = QPushButton(self.displayPage)
        self.collapseButton.setObjectName(u"collapseButton")

        self.horizontalLayout_6.addWidget(self.collapseButton)

        self.line = QFrame(self.displayPage)
        self.line.setObjectName(u"line")
        self.line.setFrameShape(QFrame.HLine)
        self.line.setFrameShadow(QFrame.Sunken)

        self.horizontalLayout_6.addWidget(self.line)

        self.horizontalLayout_6.setStretch(0, 1)
        self.horizontalLayout_6.setStretch(2, 1)

        self.verticalLayout.addLayout(self.horizontalLayout_6)

        self.bottomGroup = QWidget(self.displayPage)
        self.bottomGroup.setObjectName(u"bottomGroup")
        self.horizontalLayout_3 = QHBoxLayout(self.bottomGroup)
        self.horizontalLayout_3.setSpacing(6)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalLayout_3.setContentsMargins(3, 0, 3, 3)
        self.channelGroupBox = QGroupBox(self.bottomGroup)
        self.channelGroupBox.setObjectName(u"channelGroupBox")
        self.channelGroupBox.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignTop)
        self.verticalLayout_8 = QVBoxLayout(self.channelGroupBox)
        self.verticalLayout_8.setSpacing(0)
        self.verticalLayout_8.setObjectName(u"verticalLayout_8")
        self.verticalLayout_8.setContentsMargins(6, 6, 6, 6)
        self.channelLayout = QGridLayout()
        self.channelLayout.setSpacing(3)
        self.channelLayout.setObjectName(u"channelLayout")
        self.meanLabel = QLabel(self.channelGroupBox)
        self.meanLabel.setObjectName(u"meanLabel")
        self.meanLabel.setMinimumSize(QSize(100, 0))
        self.meanLabel.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.channelLayout.addWidget(self.meanLabel, 0, 1, 1, 1)

        self.samplingRateLabel = QLabel(self.channelGroupBox)
        self.samplingRateLabel.setObjectName(u"samplingRateLabel")
        self.samplingRateLabel.setMinimumSize(QSize(75, 0))
        self.samplingRateLabel.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.channelLayout.addWidget(self.samplingRateLabel, 0, 3, 1, 1)

        self.stdDevLabel = QLabel(self.channelGroupBox)
        self.stdDevLabel.setObjectName(u"stdDevLabel")
        self.stdDevLabel.setMinimumSize(QSize(100, 0))
        self.stdDevLabel.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.channelLayout.addWidget(self.stdDevLabel, 0, 2, 1, 1)

        self.channelLabel = QLabel(self.channelGroupBox)
        self.channelLabel.setObjectName(u"channelLabel")
        self.channelLabel.setMinimumSize(QSize(0, 0))

        self.channelLayout.addWidget(self.channelLabel, 0, 0, 1, 1)


        self.verticalLayout_8.addLayout(self.channelLayout)

        self.verticalSpacer = QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_8.addItem(self.verticalSpacer)


        self.horizontalLayout_3.addWidget(self.channelGroupBox)

        self.deviceInfoGroupBox = QGroupBox(self.bottomGroup)
        self.deviceInfoGroupBox.setObjectName(u"deviceInfoGroupBox")
        self.gridLayout = QGridLayout(self.deviceInfoGroupBox)
        self.gridLayout.setObjectName(u"gridLayout")
        self.boardInfoLabel = QLabel(self.deviceInfoGroupBox)
        self.boardInfoLabel.setObjectName(u"boardInfoLabel")

        self.gridLayout.addWidget(self.boardInfoLabel, 2, 0, 1, 1)

        self.buildInfoLabel = QLabel(self.deviceInfoGroupBox)
        self.buildInfoLabel.setObjectName(u"buildInfoLabel")

        self.gridLayout.addWidget(self.buildInfoLabel, 5, 0, 1, 1)

        self.branchLabel = QLabel(self.deviceInfoGroupBox)
        self.branchLabel.setObjectName(u"branchLabel")

        self.gridLayout.addWidget(self.branchLabel, 7, 0, 1, 1)

        self.serialNumberLabel = QLabel(self.deviceInfoGroupBox)
        self.serialNumberLabel.setObjectName(u"serialNumberLabel")

        self.gridLayout.addWidget(self.serialNumberLabel, 0, 0, 1, 1)

        self.buildInfo = QLabel(self.deviceInfoGroupBox)
        self.buildInfo.setObjectName(u"buildInfo")
        self.buildInfo.setCursor(QCursor(Qt.IBeamCursor))
        self.buildInfo.setTextInteractionFlags(Qt.LinksAccessibleByMouse|Qt.TextSelectableByMouse)

        self.gridLayout.addWidget(self.buildInfo, 5, 1, 1, 2)

        self.serialNumber = QLabel(self.deviceInfoGroupBox)
        self.serialNumber.setObjectName(u"serialNumber")
        self.serialNumber.setCursor(QCursor(Qt.IBeamCursor))
        self.serialNumber.setTextInteractionFlags(Qt.LinksAccessibleByMouse|Qt.TextSelectableByMouse)

        self.gridLayout.addWidget(self.serialNumber, 0, 1, 1, 1)

        self.userTag1 = QLabel(self.deviceInfoGroupBox)
        self.userTag1.setObjectName(u"userTag1")
        self.userTag1.setCursor(QCursor(Qt.IBeamCursor))
        self.userTag1.setTextInteractionFlags(Qt.LinksAccessibleByMouse|Qt.TextSelectableByMouse)

        self.gridLayout.addWidget(self.userTag1, 3, 1, 1, 1)

        self.setUserTag2 = QToolButton(self.deviceInfoGroupBox)
        self.setUserTag2.setObjectName(u"setUserTag2")

        self.gridLayout.addWidget(self.setUserTag2, 4, 2, 1, 1)

        self.buildDate = QLabel(self.deviceInfoGroupBox)
        self.buildDate.setObjectName(u"buildDate")
        self.buildDate.setCursor(QCursor(Qt.IBeamCursor))
        self.buildDate.setTextInteractionFlags(Qt.LinksAccessibleByMouse|Qt.TextSelectableByMouse)

        self.gridLayout.addWidget(self.buildDate, 6, 1, 1, 2)

        self.userTag2Label = QLabel(self.deviceInfoGroupBox)
        self.userTag2Label.setObjectName(u"userTag2Label")

        self.gridLayout.addWidget(self.userTag2Label, 4, 0, 1, 1)

        self.verticalSpacer_5 = QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.gridLayout.addItem(self.verticalSpacer_5, 9, 0, 1, 3)

        self.boardInfo = QLabel(self.deviceInfoGroupBox)
        self.boardInfo.setObjectName(u"boardInfo")
        self.boardInfo.setCursor(QCursor(Qt.IBeamCursor))
        self.boardInfo.setTextInteractionFlags(Qt.LinksAccessibleByMouse|Qt.TextSelectableByMouse)

        self.gridLayout.addWidget(self.boardInfo, 2, 1, 1, 2)

        self.userTag2 = QLabel(self.deviceInfoGroupBox)
        self.userTag2.setObjectName(u"userTag2")
        self.userTag2.setCursor(QCursor(Qt.IBeamCursor))
        self.userTag2.setTextInteractionFlags(Qt.LinksAccessibleByMouse|Qt.TextSelectableByMouse)

        self.gridLayout.addWidget(self.userTag2, 4, 1, 1, 1)

        self.branch = QLabel(self.deviceInfoGroupBox)
        self.branch.setObjectName(u"branch")
        self.branch.setTextInteractionFlags(Qt.LinksAccessibleByMouse|Qt.TextSelectableByMouse)

        self.gridLayout.addWidget(self.branch, 7, 1, 1, 2)

        self.deviceInfo = QToolButton(self.deviceInfoGroupBox)
        self.deviceInfo.setObjectName(u"deviceInfo")

        self.gridLayout.addWidget(self.deviceInfo, 10, 2, 1, 1)

        self.userTag1Label = QLabel(self.deviceInfoGroupBox)
        self.userTag1Label.setObjectName(u"userTag1Label")

        self.gridLayout.addWidget(self.userTag1Label, 3, 0, 1, 1)

        self.copySerialNumber = QToolButton(self.deviceInfoGroupBox)
        self.copySerialNumber.setObjectName(u"copySerialNumber")

        self.gridLayout.addWidget(self.copySerialNumber, 0, 2, 1, 1)

        self.setUserTag1 = QToolButton(self.deviceInfoGroupBox)
        self.setUserTag1.setObjectName(u"setUserTag1")

        self.gridLayout.addWidget(self.setUserTag1, 3, 2, 1, 1)

        self.buildDateLabel = QLabel(self.deviceInfoGroupBox)
        self.buildDateLabel.setObjectName(u"buildDateLabel")

        self.gridLayout.addWidget(self.buildDateLabel, 6, 0, 1, 1)

        self.batteryLabel = QLabel(self.deviceInfoGroupBox)
        self.batteryLabel.setObjectName(u"batteryLabel")

        self.gridLayout.addWidget(self.batteryLabel, 8, 0, 1, 1)

        self.battery = QLabel(self.deviceInfoGroupBox)
        self.battery.setObjectName(u"battery")
        self.battery.setTextInteractionFlags(Qt.LinksAccessibleByMouse|Qt.TextSelectableByMouse)

        self.gridLayout.addWidget(self.battery, 8, 1, 1, 2)


        self.horizontalLayout_3.addWidget(self.deviceInfoGroupBox)

        self.LEDGroupBox = QGroupBox(self.bottomGroup)
        self.LEDGroupBox.setObjectName(u"LEDGroupBox")
        self.LEDGroupBox.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignTop)
        self.verticalLayout_7 = QVBoxLayout(self.LEDGroupBox)
        self.verticalLayout_7.setSpacing(0)
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.verticalLayout_7.setContentsMargins(6, 6, 6, 6)
        self.LEDLayout = QVBoxLayout()
        self.LEDLayout.setObjectName(u"LEDLayout")

        self.verticalLayout_7.addLayout(self.LEDLayout)

        self.verticalSpacer_3 = QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_7.addItem(self.verticalSpacer_3)


        self.horizontalLayout_3.addWidget(self.LEDGroupBox)

        self.logGroupBox = QGroupBox(self.bottomGroup)
        self.logGroupBox.setObjectName(u"logGroupBox")
        self.verticalLayout_9 = QVBoxLayout(self.logGroupBox)
        self.verticalLayout_9.setObjectName(u"verticalLayout_9")
        self.verticalLayout_9.setContentsMargins(6, 6, 6, 6)
        self.logList = QListWidget(self.logGroupBox)
        self.logList.setObjectName(u"logList")
        sizePolicy3 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Ignored)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.logList.sizePolicy().hasHeightForWidth())
        self.logList.setSizePolicy(sizePolicy3)
        self.logList.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)

        self.verticalLayout_9.addWidget(self.logList)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(-1, 0, -1, -1)
        self.horizontalSpacer_4 = QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer_4)

        self.recentLostPacketsLabel = QLabel(self.logGroupBox)
        self.recentLostPacketsLabel.setObjectName(u"recentLostPacketsLabel")

        self.horizontalLayout_2.addWidget(self.recentLostPacketsLabel)

        self.recentLostPackets = QLineEdit(self.logGroupBox)
        self.recentLostPackets.setObjectName(u"recentLostPackets")
        sizePolicy2.setHeightForWidth(self.recentLostPackets.sizePolicy().hasHeightForWidth())
        self.recentLostPackets.setSizePolicy(sizePolicy2)
        self.recentLostPackets.setMaximumSize(QSize(60, 16777215))
        self.recentLostPackets.setMaxLength(10)
        self.recentLostPackets.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.recentLostPackets.setReadOnly(True)

        self.horizontalLayout_2.addWidget(self.recentLostPackets)

        self.flushLostPackets = QToolButton(self.logGroupBox)
        self.flushLostPackets.setObjectName(u"flushLostPackets")

        self.horizontalLayout_2.addWidget(self.flushLostPackets)

        self.lostPacketDetails = QToolButton(self.logGroupBox)
        self.lostPacketDetails.setObjectName(u"lostPacketDetails")

        self.horizontalLayout_2.addWidget(self.lostPacketDetails)


        self.verticalLayout_9.addLayout(self.horizontalLayout_2)

        self.verticalLayout_9.setStretch(0, 1)

        self.horizontalLayout_3.addWidget(self.logGroupBox)

        self.horizontalLayout_3.setStretch(3, 1)

        self.verticalLayout.addWidget(self.bottomGroup)

        self.verticalLayout.setStretch(0, 1)
        self.stackedWidget.addWidget(self.displayPage)

        self.verticalLayout_2.addWidget(self.stackedWidget)


        self.retranslateUi(DeviceTab)

        self.stackedWidget.setCurrentIndex(1)


        QMetaObject.connectSlotsByName(DeviceTab)
    # setupUi

    def retranslateUi(self, DeviceTab):
        DeviceTab.setWindowTitle(QCoreApplication.translate("DeviceTab", u"Device Tab", None))
        self.actionSetUserTag1.setText(QCoreApplication.translate("DeviceTab", u"Set User Tag 1", None))
        self.actionSetUserTag2.setText(QCoreApplication.translate("DeviceTab", u"Set User Tag 2", None))
#if QT_CONFIG(tooltip)
        self.actionSetUserTag2.setToolTip(QCoreApplication.translate("DeviceTab", u"Set User Tag 2", None))
#endif // QT_CONFIG(tooltip)
        self.actionEditDeviceSettings.setText(QCoreApplication.translate("DeviceTab", u"Edit Device Settings", None))
        self.actionShowDeviceInfo.setText(QCoreApplication.translate("DeviceTab", u"More Device Info", None))
#if QT_CONFIG(tooltip)
        self.actionShowDeviceInfo.setToolTip(QCoreApplication.translate("DeviceTab", u"More Device Info", None))
#endif // QT_CONFIG(tooltip)
        self.actionFirmwareLatestStable.setText(QCoreApplication.translate("DeviceTab", u"Latest Stable", None))
#if QT_CONFIG(tooltip)
        self.actionFirmwareLatestStable.setToolTip(QCoreApplication.translate("DeviceTab", u"Update Firmware From Latest Stable", None))
#endif // QT_CONFIG(tooltip)
        self.actionShowPacketStats.setText(QCoreApplication.translate("DeviceTab", u"Show Packet Stats", None))
        self.actionChangeActiveStreams.setText(QCoreApplication.translate("DeviceTab", u"Change Active Streams", None))
        self.actionRunTests.setText(QCoreApplication.translate("DeviceTab", u"Run Hardware Tests", None))
        self.actionSetDeviceMode.setText(QCoreApplication.translate("DeviceTab", u"Set Device Mode", None))
        self.actionFirmwareFromBranch.setText(QCoreApplication.translate("DeviceTab", u"From Branch", None))
#if QT_CONFIG(tooltip)
        self.actionFirmwareFromBranch.setToolTip(QCoreApplication.translate("DeviceTab", u"Update Firmware From Branch", None))
#endif // QT_CONFIG(tooltip)
        self.actionFirmwareFromCommit.setText(QCoreApplication.translate("DeviceTab", u"From Specific Commit", None))
#if QT_CONFIG(tooltip)
        self.actionFirmwareFromCommit.setToolTip(QCoreApplication.translate("DeviceTab", u"Update Firmware From Specific Commit", None))
#endif // QT_CONFIG(tooltip)
        self.actionFirmwareFromFile.setText(QCoreApplication.translate("DeviceTab", u"From File", None))
#if QT_CONFIG(tooltip)
        self.actionFirmwareFromFile.setToolTip(QCoreApplication.translate("DeviceTab", u"Update Firmware From File", None))
#endif // QT_CONFIG(tooltip)
        self.actionForceRunBootloader.setText(QCoreApplication.translate("DeviceTab", u"Force Run Bootloader", None))
        self.actionForceRunApplication.setText(QCoreApplication.translate("DeviceTab", u"Force Run Application", None))
#if QT_CONFIG(tooltip)
        self.actionForceRunApplication.setToolTip(QCoreApplication.translate("DeviceTab", u"Force Run Application", None))
#endif // QT_CONFIG(tooltip)
        self.actionForceReset.setText(QCoreApplication.translate("DeviceTab", u"Force Reset", None))
#if QT_CONFIG(tooltip)
        self.actionForceReset.setToolTip(QCoreApplication.translate("DeviceTab", u"Force Reset", None))
#endif // QT_CONFIG(tooltip)
        self.actionRaiseException.setText(QCoreApplication.translate("DeviceTab", u"Raise Exception", None))
#if QT_CONFIG(tooltip)
        self.actionRaiseException.setToolTip(QCoreApplication.translate("DeviceTab", u"Raise Exception", None))
#endif // QT_CONFIG(tooltip)
        self.actionRecoverNVM.setText(QCoreApplication.translate("DeviceTab", u"Recover NVM", None))
#if QT_CONFIG(tooltip)
        self.actionRecoverNVM.setToolTip(QCoreApplication.translate("DeviceTab", u"Recover NVM", None))
#endif // QT_CONFIG(tooltip)
        self.actionCalibrate.setText(QCoreApplication.translate("DeviceTab", u"Start Calibration", None))
        self.actionShakerCalibrate.setText(QCoreApplication.translate("DeviceTab", u"1g RMS Shaker Calibration", None))
#if QT_CONFIG(tooltip)
        self.actionShakerCalibrate.setToolTip(QCoreApplication.translate("DeviceTab", u"1g RMS Shaker Calibration", None))
#endif // QT_CONFIG(tooltip)
        self.actionCopySerialNumber.setText(QCoreApplication.translate("DeviceTab", u"Copy Serial Number", None))
        self.actionFlushLostPackets.setText(QCoreApplication.translate("DeviceTab", u"Flush Lost Packets", None))
#if QT_CONFIG(tooltip)
        self.actionFlushLostPackets.setToolTip(QCoreApplication.translate("DeviceTab", u"Flush Lost Packets", None))
#endif // QT_CONFIG(tooltip)
        self.actionRFTest.setText(QCoreApplication.translate("DeviceTab", u"RF Test", None))
#if QT_CONFIG(tooltip)
        self.actionRFTest.setToolTip(QCoreApplication.translate("DeviceTab", u"RF Test", None))
#endif // QT_CONFIG(tooltip)
        self.graphChannelLabel.setText(QCoreApplication.translate("DeviceTab", u"Graph Channel:", None))
        self.fftSubchannelLabel.setText(QCoreApplication.translate("DeviceTab", u"Frequency Subchannel:", None))
        self.nvmModifiedIndicator.setText(QCoreApplication.translate("DeviceTab", u"NVM Modified", None))
        self.bootloaderIndicator.setText(QCoreApplication.translate("DeviceTab", u"Bootloader", None))
        self.editDeviceSettings.setText(QCoreApplication.translate("DeviceTab", u"PushButton", None))
        self.menuButton.setText(QCoreApplication.translate("DeviceTab", u"Menu", None))
        self.closeButton.setText(QCoreApplication.translate("DeviceTab", u"Close", None))
        self.statusLabel.setText(QCoreApplication.translate("DeviceTab", u"Disconnected", None))
        self.collapseButton.setText(QCoreApplication.translate("DeviceTab", u"Collapse", None))
        self.channelGroupBox.setTitle(QCoreApplication.translate("DeviceTab", u"Channels", None))
        self.meanLabel.setText(QCoreApplication.translate("DeviceTab", u"Mean (1s)", None))
        self.samplingRateLabel.setText(QCoreApplication.translate("DeviceTab", u"Sampling Rate", None))
        self.stdDevLabel.setText(QCoreApplication.translate("DeviceTab", u"Std Dev (1s)", None))
        self.channelLabel.setText("")
        self.deviceInfoGroupBox.setTitle(QCoreApplication.translate("DeviceTab", u"Device Info", None))
        self.boardInfoLabel.setText(QCoreApplication.translate("DeviceTab", u"Board Info:", None))
        self.buildInfoLabel.setText(QCoreApplication.translate("DeviceTab", u"Build Info:", None))
        self.branchLabel.setText(QCoreApplication.translate("DeviceTab", u"Branch:", None))
        self.serialNumberLabel.setText(QCoreApplication.translate("DeviceTab", u"Serial Number:", None))
        self.buildInfo.setText(QCoreApplication.translate("DeviceTab", u"Build Info", None))
        self.serialNumber.setText(QCoreApplication.translate("DeviceTab", u"Serial Number", None))
        self.userTag1.setText(QCoreApplication.translate("DeviceTab", u"User Tag 1", None))
        self.setUserTag2.setText(QCoreApplication.translate("DeviceTab", u"Set", None))
        self.buildDate.setText(QCoreApplication.translate("DeviceTab", u"Build Date", None))
        self.userTag2Label.setText(QCoreApplication.translate("DeviceTab", u"User Tag 2:", None))
        self.boardInfo.setText(QCoreApplication.translate("DeviceTab", u"Board Info", None))
        self.userTag2.setText(QCoreApplication.translate("DeviceTab", u"User Tag 2", None))
        self.branch.setText(QCoreApplication.translate("DeviceTab", u"branch", None))
        self.deviceInfo.setText(QCoreApplication.translate("DeviceTab", u"More", None))
        self.userTag1Label.setText(QCoreApplication.translate("DeviceTab", u"User Tag 1:", None))
        self.copySerialNumber.setText(QCoreApplication.translate("DeviceTab", u"Copy", None))
        self.setUserTag1.setText(QCoreApplication.translate("DeviceTab", u"Set", None))
        self.buildDateLabel.setText(QCoreApplication.translate("DeviceTab", u"Build Date:", None))
        self.batteryLabel.setText(QCoreApplication.translate("DeviceTab", u"Battery:", None))
        self.battery.setText(QCoreApplication.translate("DeviceTab", u"battery", None))
        self.LEDGroupBox.setTitle(QCoreApplication.translate("DeviceTab", u"LEDs", None))
        self.logGroupBox.setTitle(QCoreApplication.translate("DeviceTab", u"Log", None))
        self.recentLostPacketsLabel.setText(QCoreApplication.translate("DeviceTab", u"Lost Packets (last 20 s):", None))
        self.recentLostPackets.setText(QCoreApplication.translate("DeviceTab", u"0", None))
    # retranslateUi

