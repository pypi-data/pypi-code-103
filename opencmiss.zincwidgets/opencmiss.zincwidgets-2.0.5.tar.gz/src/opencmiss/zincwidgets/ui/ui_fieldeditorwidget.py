# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'fieldeditorwidget.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *

from opencmiss.zincwidgets.fieldchooserwidget import FieldChooserWidget
from opencmiss.zincwidgets.fieldtypechooserwidget import FieldTypeChooserWidget
from opencmiss.zincwidgets.regionchooserwidget import RegionChooserWidget


class Ui_FieldEditorWidget(object):
    def setupUi(self, FieldEditorWidget):
        if not FieldEditorWidget.objectName():
            FieldEditorWidget.setObjectName(u"FieldEditorWidget")
        FieldEditorWidget.setEnabled(True)
        FieldEditorWidget.resize(310, 1030)
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(FieldEditorWidget.sizePolicy().hasHeightForWidth())
        FieldEditorWidget.setSizePolicy(sizePolicy)
        FieldEditorWidget.setMinimumSize(QSize(180, 0))
        self.gridLayout_2 = QGridLayout(FieldEditorWidget)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.field_type_label = QLabel(FieldEditorWidget)
        self.field_type_label.setObjectName(u"field_type_label")
        sizePolicy1 = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Preferred)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.field_type_label.sizePolicy().hasHeightForWidth())
        self.field_type_label.setSizePolicy(sizePolicy1)
        self.field_type_label.setMinimumSize(QSize(100, 27))

        self.gridLayout_2.addWidget(self.field_type_label, 0, 0, 1, 1)

        self.field_type_chooser = FieldTypeChooserWidget(FieldEditorWidget)
        self.field_type_chooser.setObjectName(u"field_type_chooser")
        sizePolicy2 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.field_type_chooser.sizePolicy().hasHeightForWidth())
        self.field_type_chooser.setSizePolicy(sizePolicy2)
        self.field_type_chooser.setSizeAdjustPolicy(QComboBox.AdjustToContents)

        self.gridLayout_2.addWidget(self.field_type_chooser, 0, 1, 1, 1)

        self.sourcefields_groupbox = QGroupBox(FieldEditorWidget)
        self.sourcefields_groupbox.setObjectName(u"sourcefields_groupbox")
        self.gridLayout_4 = QGridLayout(self.sourcefields_groupbox)
        self.gridLayout_4.setContentsMargins(7, 7, 7, 7)
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.number_of_source_fields_label = QLabel(self.sourcefields_groupbox)
        self.number_of_source_fields_label.setObjectName(u"number_of_source_fields_label")

        self.gridLayout_4.addWidget(self.number_of_source_fields_label, 0, 0, 1, 1)

        self.number_of_source_fields_lineedit = QLineEdit(self.sourcefields_groupbox)
        self.number_of_source_fields_lineedit.setObjectName(u"number_of_source_fields_lineedit")
        self.number_of_source_fields_lineedit.setEnabled(False)

        self.gridLayout_4.addWidget(self.number_of_source_fields_lineedit, 0, 1, 1, 1)

        self.region_of_apply_fields_label = QLabel(self.sourcefields_groupbox)
        self.region_of_apply_fields_label.setObjectName(u"region_of_apply_fields_label")

        self.gridLayout_4.addWidget(self.region_of_apply_fields_label, 1, 0, 1, 1)

        self.region_of_apply_fields_chooser = RegionChooserWidget(self.sourcefields_groupbox)
        self.region_of_apply_fields_chooser.setObjectName(u"region_of_apply_fields_chooser")

        self.gridLayout_4.addWidget(self.region_of_apply_fields_chooser, 1, 1, 1, 1)


        self.gridLayout_2.addWidget(self.sourcefields_groupbox, 3, 0, 1, 2)

        self.applyargumentfields_groupbox = QGroupBox(FieldEditorWidget)
        self.applyargumentfields_groupbox.setObjectName(u"applyargumentfields_groupbox")
        self.gridLayout_11 = QGridLayout(self.applyargumentfields_groupbox)
        self.gridLayout_11.setObjectName(u"gridLayout_11")

        self.gridLayout_2.addWidget(self.applyargumentfields_groupbox, 5, 0, 1, 2)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.gridLayout_2.addItem(self.verticalSpacer, 7, 0, 1, 1)

        self.coordinate_system_groupbox = QGroupBox(FieldEditorWidget)
        self.coordinate_system_groupbox.setObjectName(u"coordinate_system_groupbox")
        self.coordinate_system_groupbox.setMaximumSize(QSize(16777215, 16777215))
        self.coordinate_system_groupbox.setFlat(False)
        self.gridLayout = QGridLayout(self.coordinate_system_groupbox)
        self.gridLayout.setObjectName(u"gridLayout")
        self.coordinate_system_type_label = QLabel(self.coordinate_system_groupbox)
        self.coordinate_system_type_label.setObjectName(u"coordinate_system_type_label")

        self.gridLayout.addWidget(self.coordinate_system_type_label, 0, 0, 1, 1)

        self.coordinate_system_type_chooser = FieldChooserWidget(self.coordinate_system_groupbox)
        self.coordinate_system_type_chooser.addItem("")
        self.coordinate_system_type_chooser.addItem("")
        self.coordinate_system_type_chooser.addItem("")
        self.coordinate_system_type_chooser.addItem("")
        self.coordinate_system_type_chooser.addItem("")
        self.coordinate_system_type_chooser.addItem("")
        self.coordinate_system_type_chooser.setObjectName(u"coordinate_system_type_chooser")
        self.coordinate_system_type_chooser.setEditable(False)
        self.coordinate_system_type_chooser.setSizeAdjustPolicy(QComboBox.AdjustToContents)

        self.gridLayout.addWidget(self.coordinate_system_type_chooser, 0, 1, 1, 1)

        self.coordinate_system_focus_label = QLabel(self.coordinate_system_groupbox)
        self.coordinate_system_focus_label.setObjectName(u"coordinate_system_focus_label")

        self.gridLayout.addWidget(self.coordinate_system_focus_label, 1, 0, 1, 1)

        self.coordinate_system_focus_lineedit = QLineEdit(self.coordinate_system_groupbox)
        self.coordinate_system_focus_lineedit.setObjectName(u"coordinate_system_focus_lineedit")

        self.gridLayout.addWidget(self.coordinate_system_focus_lineedit, 1, 1, 1, 1)


        self.gridLayout_2.addWidget(self.coordinate_system_groupbox, 2, 0, 1, 2)

        self.derived_groupbox = QGroupBox(FieldEditorWidget)
        self.derived_groupbox.setObjectName(u"derived_groupbox")
        self.gridLayout_9 = QGridLayout(self.derived_groupbox)
        self.gridLayout_9.setObjectName(u"gridLayout_9")
        self.derived_chooser_1 = QComboBox(self.derived_groupbox)
        self.derived_chooser_1.setObjectName(u"derived_chooser_1")

        self.gridLayout_9.addWidget(self.derived_chooser_1, 1, 2, 1, 1)

        self.derived_combo_label_1 = QLabel(self.derived_groupbox)
        self.derived_combo_label_1.setObjectName(u"derived_combo_label_1")

        self.gridLayout_9.addWidget(self.derived_combo_label_1, 1, 0, 1, 1)

        self.derived_chooser_2 = QComboBox(self.derived_groupbox)
        self.derived_chooser_2.setObjectName(u"derived_chooser_2")

        self.gridLayout_9.addWidget(self.derived_chooser_2, 2, 2, 1, 1)

        self.derived_values_label = QLabel(self.derived_groupbox)
        self.derived_values_label.setObjectName(u"derived_values_label")

        self.gridLayout_9.addWidget(self.derived_values_label, 0, 0, 1, 1)

        self.derived_combo_label_2 = QLabel(self.derived_groupbox)
        self.derived_combo_label_2.setObjectName(u"derived_combo_label_2")

        self.gridLayout_9.addWidget(self.derived_combo_label_2, 2, 0, 1, 1)

        self.derived_values_lineedit = QLineEdit(self.derived_groupbox)
        self.derived_values_lineedit.setObjectName(u"derived_values_lineedit")
        self.derived_values_lineedit.setEnabled(False)

        self.gridLayout_9.addWidget(self.derived_values_lineedit, 0, 2, 1, 1)

        self.derived_combo_label_3 = QLabel(self.derived_groupbox)
        self.derived_combo_label_3.setObjectName(u"derived_combo_label_3")

        self.gridLayout_9.addWidget(self.derived_combo_label_3, 3, 0, 1, 1)

        self.derived_chooser_3 = QComboBox(self.derived_groupbox)
        self.derived_chooser_3.setObjectName(u"derived_chooser_3")

        self.gridLayout_9.addWidget(self.derived_chooser_3, 3, 2, 1, 1)


        self.gridLayout_2.addWidget(self.derived_groupbox, 4, 0, 1, 2)

        self.general_groupbox = QGroupBox(FieldEditorWidget)
        self.general_groupbox.setObjectName(u"general_groupbox")
        self.general_groupbox.setEnabled(True)
        self.general_groupbox.setMaximumSize(QSize(16777215, 16777215))
        self.general_groupbox.setCheckable(False)
        self.gridLayout_3 = QGridLayout(self.general_groupbox)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.type_coordinate_checkbox = QCheckBox(self.general_groupbox)
        self.type_coordinate_checkbox.setObjectName(u"type_coordinate_checkbox")

        self.gridLayout_3.addWidget(self.type_coordinate_checkbox, 1, 0, 1, 1)

        self.managed_checkbox = QCheckBox(self.general_groupbox)
        self.managed_checkbox.setObjectName(u"managed_checkbox")

        self.gridLayout_3.addWidget(self.managed_checkbox, 0, 0, 1, 1)


        self.gridLayout_2.addWidget(self.general_groupbox, 1, 0, 1, 2)

        self.create_group = QGroupBox(FieldEditorWidget)
        self.create_group.setObjectName(u"create_group")
        self.create_group.setMinimumSize(QSize(180, 0))
        self.formLayout = QFormLayout(self.create_group)
        self.formLayout.setObjectName(u"formLayout")
        self.name_label = QLabel(self.create_group)
        self.name_label.setObjectName(u"name_label")

        self.formLayout.setWidget(0, QFormLayout.LabelRole, self.name_label)

        self.create_button = QPushButton(self.create_group)
        self.create_button.setObjectName(u"create_button")

        self.formLayout.setWidget(1, QFormLayout.SpanningRole, self.create_button)

        self.name_lineedit = QLineEdit(self.create_group)
        self.name_lineedit.setObjectName(u"name_lineedit")

        self.formLayout.setWidget(0, QFormLayout.FieldRole, self.name_lineedit)


        self.gridLayout_2.addWidget(self.create_group, 6, 0, 1, 2)


        self.retranslateUi(FieldEditorWidget)

        QMetaObject.connectSlotsByName(FieldEditorWidget)
    # setupUi

    def retranslateUi(self, FieldEditorWidget):
        FieldEditorWidget.setWindowTitle(QCoreApplication.translate("FieldEditorWidget", u"Field Editor", None))
        self.field_type_label.setText(QCoreApplication.translate("FieldEditorWidget", u"Field type:", None))
        self.sourcefields_groupbox.setTitle(QCoreApplication.translate("FieldEditorWidget", u"Source fields:", None))
        self.number_of_source_fields_label.setText(QCoreApplication.translate("FieldEditorWidget", u"Number of source fields:", None))
        self.region_of_apply_fields_label.setText(QCoreApplication.translate("FieldEditorWidget", u"Region of evaluate field:", None))
        self.applyargumentfields_groupbox.setTitle(QCoreApplication.translate("FieldEditorWidget", u"Apply argument fields:", None))
        self.coordinate_system_groupbox.setTitle(QCoreApplication.translate("FieldEditorWidget", u"Coordinate System:", None))
        self.coordinate_system_type_label.setText(QCoreApplication.translate("FieldEditorWidget", u"Type:", None))
        self.coordinate_system_type_chooser.setItemText(0, QCoreApplication.translate("FieldEditorWidget", u"Rectangular Cartesian", None))
        self.coordinate_system_type_chooser.setItemText(1, QCoreApplication.translate("FieldEditorWidget", u"Cylindrial Polar", None))
        self.coordinate_system_type_chooser.setItemText(2, QCoreApplication.translate("FieldEditorWidget", u"Spherical Polar", None))
        self.coordinate_system_type_chooser.setItemText(3, QCoreApplication.translate("FieldEditorWidget", u"Prolate Spheroidal", None))
        self.coordinate_system_type_chooser.setItemText(4, QCoreApplication.translate("FieldEditorWidget", u"Oblate Spheroidal", None))
        self.coordinate_system_type_chooser.setItemText(5, QCoreApplication.translate("FieldEditorWidget", u"Fibre", None))

        self.coordinate_system_focus_label.setText(QCoreApplication.translate("FieldEditorWidget", u"Focus:", None))
        self.derived_groupbox.setTitle(QCoreApplication.translate("FieldEditorWidget", u"Derived Parameters:", None))
        self.derived_combo_label_1.setText(QCoreApplication.translate("FieldEditorWidget", u"Derived combo1", None))
        self.derived_values_label.setText(QCoreApplication.translate("FieldEditorWidget", u"Constant Values:", None))
        self.derived_combo_label_2.setText(QCoreApplication.translate("FieldEditorWidget", u"Derived combo2", None))
        self.derived_combo_label_3.setText(QCoreApplication.translate("FieldEditorWidget", u"Derived combo3", None))
        self.general_groupbox.setTitle("")
        self.type_coordinate_checkbox.setText(QCoreApplication.translate("FieldEditorWidget", u"Is Coordinate", None))
        self.managed_checkbox.setText(QCoreApplication.translate("FieldEditorWidget", u"Managed", None))
        self.create_group.setTitle("")
        self.name_label.setText(QCoreApplication.translate("FieldEditorWidget", u"Name:", None))
        self.create_button.setText(QCoreApplication.translate("FieldEditorWidget", u"Create", None))
    # retranslateUi

