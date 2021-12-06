# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'preferences.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *

from hyperborea.unit_preferences import UnitPreferencesWidget


class Ui_PreferencesDialog(object):
    def setupUi(self, PreferencesDialog):
        if not PreferencesDialog.objectName():
            PreferencesDialog.setObjectName(u"PreferencesDialog")
        PreferencesDialog.resize(411, 480)
        self.gridLayout_5 = QGridLayout(PreferencesDialog)
        self.gridLayout_5.setObjectName(u"gridLayout_5")
        self.tabWidget = QTabWidget(PreferencesDialog)
        self.tabWidget.setObjectName(u"tabWidget")
        self.interfaceTab = QWidget()
        self.interfaceTab.setObjectName(u"interfaceTab")
        self.gridLayout_8 = QGridLayout(self.interfaceTab)
        self.gridLayout_8.setObjectName(u"gridLayout_8")
        self.ledsLabel_2 = QLabel(self.interfaceTab)
        self.ledsLabel_2.setObjectName(u"ledsLabel_2")
        font = QFont()
        font.setBold(True)
        font.setWeight(75)
        self.ledsLabel_2.setFont(font)

        self.gridLayout_8.addWidget(self.ledsLabel_2, 0, 0, 1, 2)

        self.horizontalSpacer_6 = QSpacerItem(20, 10, QSizePolicy.Fixed, QSizePolicy.Minimum)

        self.gridLayout_8.addItem(self.horizontalSpacer_6, 1, 0, 1, 1)

        self.darkMode = QRadioButton(self.interfaceTab)
        self.darkMode.setObjectName(u"darkMode")

        self.gridLayout_8.addWidget(self.darkMode, 1, 1, 1, 1)

        self.lightMode = QRadioButton(self.interfaceTab)
        self.lightMode.setObjectName(u"lightMode")

        self.gridLayout_8.addWidget(self.lightMode, 2, 1, 1, 1)

        self.verticalSpacer_12 = QSpacerItem(369, 223, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.gridLayout_8.addItem(self.verticalSpacer_12, 3, 0, 1, 2)

        self.gridLayout_8.setColumnStretch(1, 1)
        self.tabWidget.addTab(self.interfaceTab, "")
        self.streamingTab = QWidget()
        self.streamingTab.setObjectName(u"streamingTab")
        self.gridLayout_3 = QGridLayout(self.streamingTab)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.horizontalSpacer_3 = QSpacerItem(20, 10, QSizePolicy.Fixed, QSizePolicy.Minimum)

        self.gridLayout_3.addItem(self.horizontalSpacer_3, 1, 0, 1, 1)

        self.automaticRGBCheckBox = QCheckBox(self.streamingTab)
        self.automaticRGBCheckBox.setObjectName(u"automaticRGBCheckBox")
        self.automaticRGBCheckBox.setChecked(True)

        self.gridLayout_3.addWidget(self.automaticRGBCheckBox, 1, 1, 1, 1)

        self.ledsLabel = QLabel(self.streamingTab)
        self.ledsLabel.setObjectName(u"ledsLabel")
        self.ledsLabel.setFont(font)

        self.gridLayout_3.addWidget(self.ledsLabel, 0, 0, 1, 2)

        self.verticalSpacer_9 = QSpacerItem(369, 243, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.gridLayout_3.addItem(self.verticalSpacer_9, 5, 0, 1, 2)

        self.downsamplingLabel = QLabel(self.streamingTab)
        self.downsamplingLabel.setObjectName(u"downsamplingLabel")
        self.downsamplingLabel.setFont(font)

        self.gridLayout_3.addWidget(self.downsamplingLabel, 2, 0, 1, 2)

        self.downsampleCheckBox = QCheckBox(self.streamingTab)
        self.downsampleCheckBox.setObjectName(u"downsampleCheckBox")
        self.downsampleCheckBox.setChecked(True)

        self.gridLayout_3.addWidget(self.downsampleCheckBox, 3, 1, 1, 1)

        self.plotMeanCheckBox = QCheckBox(self.streamingTab)
        self.plotMeanCheckBox.setObjectName(u"plotMeanCheckBox")

        self.gridLayout_3.addWidget(self.plotMeanCheckBox, 4, 1, 1, 1)

        self.tabWidget.addTab(self.streamingTab, "")
        self.unitTab = QWidget()
        self.unitTab.setObjectName(u"unitTab")
        self.gridLayout = QGridLayout(self.unitTab)
        self.gridLayout.setObjectName(u"gridLayout")
        self.unitsLabel = QLabel(self.unitTab)
        self.unitsLabel.setObjectName(u"unitsLabel")
        self.unitsLabel.setFont(font)

        self.gridLayout.addWidget(self.unitsLabel, 0, 0, 1, 2)

        self.horizontalSpacer = QSpacerItem(20, 10, QSizePolicy.Fixed, QSizePolicy.Minimum)

        self.gridLayout.addItem(self.horizontalSpacer, 1, 0, 1, 1)

        self.verticalSpacer_7 = QSpacerItem(20, 0, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.gridLayout.addItem(self.verticalSpacer_7, 4, 0, 1, 2)

        self.unitPreferences = UnitPreferencesWidget(self.unitTab)
        self.unitPreferences.setObjectName(u"unitPreferences")

        self.gridLayout.addWidget(self.unitPreferences, 1, 1, 1, 1)

        self.tabWidget.addTab(self.unitTab, "")
        self.outputTab = QWidget()
        self.outputTab.setObjectName(u"outputTab")
        self.gridLayout_2 = QGridLayout(self.outputTab)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.verticalSpacer_8 = QSpacerItem(369, 237, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.gridLayout_2.addItem(self.verticalSpacer_8, 6, 0, 1, 3)

        self.outputLocationLabel = QLabel(self.outputTab)
        self.outputLocationLabel.setObjectName(u"outputLocationLabel")
        self.outputLocationLabel.setFont(font)

        self.gridLayout_2.addWidget(self.outputLocationLabel, 0, 0, 1, 3)

        self.compressionLevel = QSpinBox(self.outputTab)
        self.compressionLevel.setObjectName(u"compressionLevel")
        self.compressionLevel.setMinimum(0)
        self.compressionLevel.setMaximum(9)
        self.compressionLevel.setValue(6)

        self.gridLayout_2.addWidget(self.compressionLevel, 5, 2, 1, 1)

        self.compressionLabel = QLabel(self.outputTab)
        self.compressionLabel.setObjectName(u"compressionLabel")
        self.compressionLabel.setFont(font)

        self.gridLayout_2.addWidget(self.compressionLabel, 3, 0, 1, 3)

        self.compressionLevelLabel = QLabel(self.outputTab)
        self.compressionLevelLabel.setObjectName(u"compressionLevelLabel")

        self.gridLayout_2.addWidget(self.compressionLevelLabel, 5, 1, 1, 1)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.outputLocation = QLineEdit(self.outputTab)
        self.outputLocation.setObjectName(u"outputLocation")

        self.horizontalLayout.addWidget(self.outputLocation)

        self.browseButton = QPushButton(self.outputTab)
        self.browseButton.setObjectName(u"browseButton")

        self.horizontalLayout.addWidget(self.browseButton)


        self.gridLayout_2.addLayout(self.horizontalLayout, 1, 1, 1, 2)

        self.horizontalSpacer_2 = QSpacerItem(20, 10, QSizePolicy.Fixed, QSizePolicy.Minimum)

        self.gridLayout_2.addItem(self.horizontalSpacer_2, 1, 0, 1, 1)

        self.gridLayout_2.setColumnStretch(1, 1)
        self.tabWidget.addTab(self.outputTab, "")
        self.uploadTab = QWidget()
        self.uploadTab.setObjectName(u"uploadTab")
        self.gridLayout_4 = QGridLayout(self.uploadTab)
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.uploadAccessKeyID = QLineEdit(self.uploadTab)
        self.uploadAccessKeyID.setObjectName(u"uploadAccessKeyID")
        self.uploadAccessKeyID.setEnabled(False)

        self.gridLayout_4.addWidget(self.uploadAccessKeyID, 5, 3, 1, 1)

        self.uploadAccessKeyIDLabel = QLabel(self.uploadTab)
        self.uploadAccessKeyIDLabel.setObjectName(u"uploadAccessKeyIDLabel")
        self.uploadAccessKeyIDLabel.setEnabled(False)

        self.gridLayout_4.addWidget(self.uploadAccessKeyIDLabel, 5, 2, 1, 1)

        self.horizontalSpacer_5 = QSpacerItem(20, 10, QSizePolicy.Fixed, QSizePolicy.Minimum)

        self.gridLayout_4.addItem(self.horizontalSpacer_5, 2, 1, 1, 1)

        self.enableUpload = QCheckBox(self.uploadTab)
        self.enableUpload.setObjectName(u"enableUpload")

        self.gridLayout_4.addWidget(self.enableUpload, 1, 1, 1, 3)

        self.uploadSecretAccessKey = QLineEdit(self.uploadTab)
        self.uploadSecretAccessKey.setObjectName(u"uploadSecretAccessKey")
        self.uploadSecretAccessKey.setEnabled(False)
        self.uploadSecretAccessKey.setEchoMode(QLineEdit.PasswordEchoOnEdit)

        self.gridLayout_4.addWidget(self.uploadSecretAccessKey, 6, 3, 1, 1)

        self.s3BucketLabel = QLabel(self.uploadTab)
        self.s3BucketLabel.setObjectName(u"s3BucketLabel")
        self.s3BucketLabel.setEnabled(False)

        self.gridLayout_4.addWidget(self.s3BucketLabel, 2, 2, 1, 1)

        self.s3UploadLabel = QLabel(self.uploadTab)
        self.s3UploadLabel.setObjectName(u"s3UploadLabel")
        self.s3UploadLabel.setFont(font)

        self.gridLayout_4.addWidget(self.s3UploadLabel, 0, 0, 1, 3)

        self.uploadDirectoryLabel = QLabel(self.uploadTab)
        self.uploadDirectoryLabel.setObjectName(u"uploadDirectoryLabel")
        self.uploadDirectoryLabel.setEnabled(False)

        self.gridLayout_4.addWidget(self.uploadDirectoryLabel, 4, 2, 1, 1)

        self.uploadDirectory = QLineEdit(self.uploadTab)
        self.uploadDirectory.setObjectName(u"uploadDirectory")
        self.uploadDirectory.setEnabled(False)

        self.gridLayout_4.addWidget(self.uploadDirectory, 4, 3, 1, 1)

        self.horizontalSpacer_4 = QSpacerItem(20, 10, QSizePolicy.Fixed, QSizePolicy.Minimum)

        self.gridLayout_4.addItem(self.horizontalSpacer_4, 1, 0, 1, 1)

        self.verticalSpacer_10 = QSpacerItem(369, 116, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.gridLayout_4.addItem(self.verticalSpacer_10, 8, 0, 1, 4)

        self.s3Bucket = QLineEdit(self.uploadTab)
        self.s3Bucket.setObjectName(u"s3Bucket")
        self.s3Bucket.setEnabled(False)

        self.gridLayout_4.addWidget(self.s3Bucket, 2, 3, 1, 1)

        self.uploadDeleteOriginal = QCheckBox(self.uploadTab)
        self.uploadDeleteOriginal.setObjectName(u"uploadDeleteOriginal")
        self.uploadDeleteOriginal.setEnabled(False)

        self.gridLayout_4.addWidget(self.uploadDeleteOriginal, 7, 2, 1, 2)

        self.uploadSecretAccessKeyLabel = QLabel(self.uploadTab)
        self.uploadSecretAccessKeyLabel.setObjectName(u"uploadSecretAccessKeyLabel")
        self.uploadSecretAccessKeyLabel.setEnabled(False)

        self.gridLayout_4.addWidget(self.uploadSecretAccessKeyLabel, 6, 2, 1, 1)

        self.awsRegionLabel = QLabel(self.uploadTab)
        self.awsRegionLabel.setObjectName(u"awsRegionLabel")
        self.awsRegionLabel.setEnabled(False)

        self.gridLayout_4.addWidget(self.awsRegionLabel, 3, 2, 1, 1)

        self.awsRegion = QLineEdit(self.uploadTab)
        self.awsRegion.setObjectName(u"awsRegion")
        self.awsRegion.setEnabled(False)

        self.gridLayout_4.addWidget(self.awsRegion, 3, 3, 1, 1)

        self.tabWidget.addTab(self.uploadTab, "")
        self.alertTab = QWidget()
        self.alertTab.setObjectName(u"alertTab")
        self.gridLayout_6 = QGridLayout(self.alertTab)
        self.gridLayout_6.setObjectName(u"gridLayout_6")
        self.horizontalSpacer_7 = QSpacerItem(20, 10, QSizePolicy.Fixed, QSizePolicy.Minimum)

        self.gridLayout_6.addItem(self.horizontalSpacer_7, 1, 0, 1, 1)

        self.alertEmailLabel = QLabel(self.alertTab)
        self.alertEmailLabel.setObjectName(u"alertEmailLabel")
        self.alertEmailLabel.setFont(font)

        self.gridLayout_6.addWidget(self.alertEmailLabel, 0, 0, 1, 3)

        self.verticalSpacer_11 = QSpacerItem(369, 284, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.gridLayout_6.addItem(self.verticalSpacer_11, 3, 0, 1, 3)

        self.smtpWidget = QWidget(self.alertTab)
        self.smtpWidget.setObjectName(u"smtpWidget")
        self.smtpWidget.setEnabled(False)
        sizePolicy = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.smtpWidget.sizePolicy().hasHeightForWidth())
        self.smtpWidget.setSizePolicy(sizePolicy)
        self.gridLayout_7 = QGridLayout(self.smtpWidget)
        self.gridLayout_7.setObjectName(u"gridLayout_7")
        self.gridLayout_7.setContentsMargins(0, 0, 0, 0)
        self.toAddressLabel = QLabel(self.smtpWidget)
        self.toAddressLabel.setObjectName(u"toAddressLabel")

        self.gridLayout_7.addWidget(self.toAddressLabel, 1, 0, 1, 1)

        self.smtpUserLabel = QLabel(self.smtpWidget)
        self.smtpUserLabel.setObjectName(u"smtpUserLabel")

        self.gridLayout_7.addWidget(self.smtpUserLabel, 8, 0, 1, 1)

        self.fromAddress = QLineEdit(self.smtpWidget)
        self.fromAddress.setObjectName(u"fromAddress")

        self.gridLayout_7.addWidget(self.fromAddress, 0, 1, 1, 1)

        self.smtpHost = QLineEdit(self.smtpWidget)
        self.smtpHost.setObjectName(u"smtpHost")

        self.gridLayout_7.addWidget(self.smtpHost, 2, 1, 1, 1)

        self.smtpPasswordLabel = QLabel(self.smtpWidget)
        self.smtpPasswordLabel.setObjectName(u"smtpPasswordLabel")

        self.gridLayout_7.addWidget(self.smtpPasswordLabel, 9, 0, 1, 1)

        self.smtpPassword = QLineEdit(self.smtpWidget)
        self.smtpPassword.setObjectName(u"smtpPassword")
        self.smtpPassword.setEchoMode(QLineEdit.PasswordEchoOnEdit)

        self.gridLayout_7.addWidget(self.smtpPassword, 9, 1, 1, 1)

        self.smtpHostLabel = QLabel(self.smtpWidget)
        self.smtpHostLabel.setObjectName(u"smtpHostLabel")

        self.gridLayout_7.addWidget(self.smtpHostLabel, 2, 0, 1, 1)

        self.useSSL = QRadioButton(self.smtpWidget)
        self.useSSL.setObjectName(u"useSSL")

        self.gridLayout_7.addWidget(self.useSSL, 5, 0, 1, 1)

        self.fromAddressLabel = QLabel(self.smtpWidget)
        self.fromAddressLabel.setObjectName(u"fromAddressLabel")

        self.gridLayout_7.addWidget(self.fromAddressLabel, 0, 0, 1, 1)

        self.smtpPortLabel = QLabel(self.smtpWidget)
        self.smtpPortLabel.setObjectName(u"smtpPortLabel")

        self.gridLayout_7.addWidget(self.smtpPortLabel, 3, 0, 1, 1)

        self.smtpPort = QSpinBox(self.smtpWidget)
        self.smtpPort.setObjectName(u"smtpPort")
        self.smtpPort.setMinimum(1)
        self.smtpPort.setMaximum(65535)

        self.gridLayout_7.addWidget(self.smtpPort, 3, 1, 1, 1)

        self.useSTARTTLS = QRadioButton(self.smtpWidget)
        self.useSTARTTLS.setObjectName(u"useSTARTTLS")
        self.useSTARTTLS.setChecked(True)

        self.gridLayout_7.addWidget(self.useSTARTTLS, 4, 0, 1, 1)

        self.smtpUser = QLineEdit(self.smtpWidget)
        self.smtpUser.setObjectName(u"smtpUser")

        self.gridLayout_7.addWidget(self.smtpUser, 8, 1, 1, 1)

        self.noSecurity = QRadioButton(self.smtpWidget)
        self.noSecurity.setObjectName(u"noSecurity")

        self.gridLayout_7.addWidget(self.noSecurity, 6, 0, 1, 1)

        self.toAddress = QLineEdit(self.smtpWidget)
        self.toAddress.setObjectName(u"toAddress")

        self.gridLayout_7.addWidget(self.toAddress, 1, 1, 1, 1)

        self.useAuthentication = QCheckBox(self.smtpWidget)
        self.useAuthentication.setObjectName(u"useAuthentication")
        self.useAuthentication.setChecked(True)

        self.gridLayout_7.addWidget(self.useAuthentication, 7, 0, 1, 2)

        self.testEmail = QPushButton(self.smtpWidget)
        self.testEmail.setObjectName(u"testEmail")
        self.testEmail.setEnabled(False)

        self.gridLayout_7.addWidget(self.testEmail, 10, 0, 1, 1)


        self.gridLayout_6.addWidget(self.smtpWidget, 2, 2, 1, 1)

        self.horizontalSpacer_8 = QSpacerItem(20, 10, QSizePolicy.Fixed, QSizePolicy.Minimum)

        self.gridLayout_6.addItem(self.horizontalSpacer_8, 2, 1, 1, 1)

        self.enableAlertEmail = QCheckBox(self.alertTab)
        self.enableAlertEmail.setObjectName(u"enableAlertEmail")

        self.gridLayout_6.addWidget(self.enableAlertEmail, 1, 1, 1, 2)

        self.tabWidget.addTab(self.alertTab, "")

        self.gridLayout_5.addWidget(self.tabWidget, 0, 0, 1, 1)

        self.buttonBox = QDialogButtonBox(PreferencesDialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)

        self.gridLayout_5.addWidget(self.buttonBox, 1, 0, 1, 1)

#if QT_CONFIG(shortcut)
        self.toAddressLabel.setBuddy(self.toAddress)
        self.smtpUserLabel.setBuddy(self.smtpUser)
        self.smtpPasswordLabel.setBuddy(self.smtpPassword)
        self.smtpHostLabel.setBuddy(self.smtpHost)
        self.fromAddressLabel.setBuddy(self.fromAddress)
#endif // QT_CONFIG(shortcut)
        QWidget.setTabOrder(self.tabWidget, self.enableAlertEmail)
        QWidget.setTabOrder(self.enableAlertEmail, self.fromAddress)
        QWidget.setTabOrder(self.fromAddress, self.toAddress)
        QWidget.setTabOrder(self.toAddress, self.smtpHost)
        QWidget.setTabOrder(self.smtpHost, self.useSTARTTLS)
        QWidget.setTabOrder(self.useSTARTTLS, self.useSSL)
        QWidget.setTabOrder(self.useSSL, self.noSecurity)
        QWidget.setTabOrder(self.noSecurity, self.useAuthentication)
        QWidget.setTabOrder(self.useAuthentication, self.smtpUser)
        QWidget.setTabOrder(self.smtpUser, self.smtpPassword)
        QWidget.setTabOrder(self.smtpPassword, self.downsampleCheckBox)
        QWidget.setTabOrder(self.downsampleCheckBox, self.automaticRGBCheckBox)
        QWidget.setTabOrder(self.automaticRGBCheckBox, self.outputLocation)
        QWidget.setTabOrder(self.outputLocation, self.browseButton)
        QWidget.setTabOrder(self.browseButton, self.compressionLevel)
        QWidget.setTabOrder(self.compressionLevel, self.enableUpload)
        QWidget.setTabOrder(self.enableUpload, self.uploadSecretAccessKey)
        QWidget.setTabOrder(self.uploadSecretAccessKey, self.uploadDeleteOriginal)
        QWidget.setTabOrder(self.uploadDeleteOriginal, self.s3Bucket)
        QWidget.setTabOrder(self.s3Bucket, self.awsRegion)
        QWidget.setTabOrder(self.awsRegion, self.uploadDirectory)
        QWidget.setTabOrder(self.uploadDirectory, self.uploadAccessKeyID)

        self.retranslateUi(PreferencesDialog)
        self.buttonBox.accepted.connect(PreferencesDialog.accept)
        self.buttonBox.rejected.connect(PreferencesDialog.reject)
        self.enableUpload.toggled.connect(self.s3BucketLabel.setEnabled)
        self.enableUpload.toggled.connect(self.s3Bucket.setEnabled)
        self.enableUpload.toggled.connect(self.uploadDirectoryLabel.setEnabled)
        self.enableUpload.toggled.connect(self.uploadDirectory.setEnabled)
        self.enableUpload.toggled.connect(self.uploadAccessKeyIDLabel.setEnabled)
        self.enableUpload.toggled.connect(self.uploadAccessKeyID.setEnabled)
        self.enableUpload.toggled.connect(self.uploadSecretAccessKeyLabel.setEnabled)
        self.enableUpload.toggled.connect(self.uploadSecretAccessKey.setEnabled)
        self.enableUpload.toggled.connect(self.uploadDeleteOriginal.setEnabled)
        self.enableUpload.toggled.connect(self.awsRegionLabel.setEnabled)
        self.enableUpload.toggled.connect(self.awsRegion.setEnabled)
        self.enableAlertEmail.toggled.connect(self.smtpWidget.setEnabled)
        self.useAuthentication.toggled.connect(self.smtpUser.setEnabled)
        self.useAuthentication.toggled.connect(self.smtpPassword.setEnabled)
        self.useAuthentication.toggled.connect(self.smtpUserLabel.setEnabled)
        self.useAuthentication.toggled.connect(self.smtpPasswordLabel.setEnabled)
        self.enableAlertEmail.toggled.connect(self.testEmail.setEnabled)

        self.tabWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(PreferencesDialog)
    # setupUi

    def retranslateUi(self, PreferencesDialog):
        PreferencesDialog.setWindowTitle(QCoreApplication.translate("PreferencesDialog", u"Preferences", None))
        self.ledsLabel_2.setText(QCoreApplication.translate("PreferencesDialog", u"Display Mode", None))
        self.darkMode.setText(QCoreApplication.translate("PreferencesDialog", u"Dark Mode", None))
        self.lightMode.setText(QCoreApplication.translate("PreferencesDialog", u"Light Mode", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.interfaceTab), QCoreApplication.translate("PreferencesDialog", u"Interface", None))
        self.automaticRGBCheckBox.setText(QCoreApplication.translate("PreferencesDialog", u"Automatically set RGB LEDs when connecting/disconnecting", None))
        self.ledsLabel.setText(QCoreApplication.translate("PreferencesDialog", u"RGB LEDs", None))
        self.downsamplingLabel.setText(QCoreApplication.translate("PreferencesDialog", u"Downsampling (time domain graph only)", None))
        self.downsampleCheckBox.setText(QCoreApplication.translate("PreferencesDialog", u"Downsample high speed channels", None))
        self.plotMeanCheckBox.setText(QCoreApplication.translate("PreferencesDialog", u"Plot 1 second mean", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.streamingTab), QCoreApplication.translate("PreferencesDialog", u"Streaming", None))
        self.unitsLabel.setText(QCoreApplication.translate("PreferencesDialog", u"Display Units", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.unitTab), QCoreApplication.translate("PreferencesDialog", u"Units", None))
        self.outputLocationLabel.setText(QCoreApplication.translate("PreferencesDialog", u"Output Location", None))
        self.compressionLabel.setText(QCoreApplication.translate("PreferencesDialog", u"Compression", None))
        self.compressionLevelLabel.setText(QCoreApplication.translate("PreferencesDialog", u"Compression Level (default 6)", None))
        self.browseButton.setText(QCoreApplication.translate("PreferencesDialog", u"Browse...", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.outputTab), QCoreApplication.translate("PreferencesDialog", u"Output", None))
        self.uploadAccessKeyIDLabel.setText(QCoreApplication.translate("PreferencesDialog", u"AWS Access Key ID", None))
        self.enableUpload.setText(QCoreApplication.translate("PreferencesDialog", u"Enable AWS S3 Upload", None))
        self.s3BucketLabel.setText(QCoreApplication.translate("PreferencesDialog", u"S3 Bucket", None))
        self.s3UploadLabel.setText(QCoreApplication.translate("PreferencesDialog", u"Amazon S3 Upload", None))
        self.uploadDirectoryLabel.setText(QCoreApplication.translate("PreferencesDialog", u"Upload Directory", None))
        self.uploadDeleteOriginal.setText(QCoreApplication.translate("PreferencesDialog", u"Delete original .apd after successful upload", None))
        self.uploadSecretAccessKeyLabel.setText(QCoreApplication.translate("PreferencesDialog", u"AWS Secret Access Key", None))
        self.awsRegionLabel.setText(QCoreApplication.translate("PreferencesDialog", u"S3 Bucket AWS Region", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.uploadTab), QCoreApplication.translate("PreferencesDialog", u"Cloud Upload", None))
        self.alertEmailLabel.setText(QCoreApplication.translate("PreferencesDialog", u"Alert Email", None))
        self.toAddressLabel.setText(QCoreApplication.translate("PreferencesDialog", u"To Address", None))
        self.smtpUserLabel.setText(QCoreApplication.translate("PreferencesDialog", u"SMTP User", None))
        self.smtpPasswordLabel.setText(QCoreApplication.translate("PreferencesDialog", u"SMTP Password", None))
        self.smtpHostLabel.setText(QCoreApplication.translate("PreferencesDialog", u"SMTP Server Host", None))
        self.useSSL.setText(QCoreApplication.translate("PreferencesDialog", u"SSL/TLS", None))
        self.fromAddressLabel.setText(QCoreApplication.translate("PreferencesDialog", u"From Address", None))
        self.smtpPortLabel.setText(QCoreApplication.translate("PreferencesDialog", u"SMTP Server Port", None))
        self.useSTARTTLS.setText(QCoreApplication.translate("PreferencesDialog", u"STARTTLS", None))
        self.noSecurity.setText(QCoreApplication.translate("PreferencesDialog", u"No Security", None))
        self.useAuthentication.setText(QCoreApplication.translate("PreferencesDialog", u"Use Authentication", None))
        self.testEmail.setText(QCoreApplication.translate("PreferencesDialog", u"Send Test Email", None))
        self.enableAlertEmail.setText(QCoreApplication.translate("PreferencesDialog", u"Send email when alert is generated", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.alertTab), QCoreApplication.translate("PreferencesDialog", u"Alerts", None))
    # retranslateUi

