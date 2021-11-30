"""
   Copyright 2016 University of Auckland

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""
from PySide2 import QtCore, QtWidgets

from copy import copy
from numbers import Number

from opencmiss.argon.argonlogger import ArgonLogger
from opencmiss.zinc.element import Element
from opencmiss.zinc.field import FieldEdgeDiscontinuity, FieldFindMeshLocation
from opencmiss.zinc.node import Node
from opencmiss.zinc.status import OK as ZINC_OK

from opencmiss.zincwidgets.fieldconditions import *
from opencmiss.zincwidgets.fieldchooserwidget import FieldChooserWidget
from opencmiss.zincwidgets.ui.ui_fieldeditorwidget import Ui_FieldEditorWidget

STRING_FLOAT_FORMAT = '{:.5g}'
MeasureType = ["C1", "G1", "Surface Normal"]
SearchMode = ["Exact", "Nearest"]
MeshName = ["mesh1d", "mesh2d", "mesh3d"]
FaceType = ["all", "any face", "no face", "xi1 = 0", "xi1 = 1", "xi2 = 0", "xi2 = 1", "xi3 = 0", "xi3 = 0"]
ValueType = ["value", "d_ds1", "d_ds2", "d2_ds1ds2", "d_ds3", "d2_ds1ds3", "d2_ds2ds3", "d3_ds1ds2ds3"]

FieldTypeToNumberofSourcesList = {
    'FieldAlias': 1, 'FieldLog': 1, 'FieldExp': 1, 'FieldAbs': 1, 'FieldIdentity': 1, 'FieldApply': 1, 'FieldArgumentReal': 0,
    'FieldCoordinateTransformation': 1, 'FieldIsDefined': 1, 'FieldNot': 1,
    'FieldDeterminant': 1, 'FieldEigenvalues': 1, 'FieldEigenvectors': 1,
    'FieldMatrixInvert': 1, 'FieldTranspose': 1, 'FieldSin': 1, 'FieldCos': 1,
    'FieldTan': 1, 'FieldAsin': 1, 'FieldAcos': 1, 'FieldAtan': 1, 'FieldMagnitude': 1,
    'FieldNormalise': 1, 'FieldSumComponents': 1, 'FieldSqrt': 1, 'FieldAdd': 2, 'FieldPower': 2,
    'FieldMultiply': 2, 'FieldDivide': 2, 'FieldSubtract': 2, 'FieldVectorCoordinateTransformation': 2,
    'FieldCurl': 2, 'FieldDivergence': 2, 'FieldGradient': 2, 'FieldFibreAxes': 2,
    'FieldAnd': 2, 'FieldEqualTo': 2, 'FieldGreaterThan': 2, 'FieldLessThan': 2,
    'FieldOr': 2, 'FieldXor': 2, 'FieldProjection': 2, 'FieldMatrixMultiply': 2,
    'FieldTimeLookup': 2, 'FieldAtan2': 2, 'FieldDotProduct': 2, 'FieldComponent': 1,
    'FieldConcatenate': -1, 'FieldIf': 3, 'FieldConstant': 0, 'FieldStringConstant': 0,
    'FieldDerivative': 1, 'FieldEmbedded': 2, 'FieldStoredString': 0, 'FieldIsExterior': 0,
    'FieldIsOnFace': 0, 'FieldEdgeDiscontinuity': 2, 'FieldNodeValue': 1,
    'FieldStoredMeshLocation': 0, 'FieldFindMeshLocation': 2, 'FieldCrossProduct': -1,
    'FieldTimeValue': 0, 'FieldFiniteElement': 0}


class FieldEditorWidget(QtWidgets.QWidget):
    _fieldCreated = QtCore.Signal(Field, str)

    def __init__(self, parent=None):
        """
        Call the super class init functions
        """
        QtWidgets.QWidget.__init__(self, parent)
        self._field = None
        self._fieldmodule = None
        # Using composition to include the visual element of the GUI.
        self.ui = Ui_FieldEditorWidget()
        self.ui.setupUi(self)
        # base graphics attributes
        self.ui.field_type_chooser.setNullObjectName('-')
        self.ui.coordinate_system_type_chooser.setNullObjectName('-')
        self._bindFieldButton = None
        self._sourceFieldChoosers = []
        self._fieldType = None
        self._createMode = True
        self._timekeeper = None
        self._updateWidgets()
        self._makeConnections()

    def _makeConnections(self):
        self.ui.coordinate_system_type_chooser.currentIndexChanged.connect(self.coordinateSystemTypeChanged)
        self.ui.coordinate_system_focus_lineedit.editingFinished.connect(self.coordinateSystemFocusEntered)
        self.ui.number_of_source_fields_lineedit.editingFinished.connect(self.numberOfSourceFieldsEntered)
        self.ui.region_of_apply_fields_chooser.currentIndexChanged.connect(self.applyFieldRegionChanged)
        self.ui.type_coordinate_checkbox.stateChanged.connect(self.typeCoordinateClicked)
        self.ui.managed_checkbox.stateChanged.connect(self.managedClicked)
        self.ui.derived_chooser_1.currentIndexChanged.connect(self.derivedChooser1Changed)
        self.ui.derived_chooser_3.currentIndexChanged.connect(self.derivedChooser3Changed)
        self.ui.field_type_chooser.currentIndexChanged.connect(self.fieldTypeChanged)
        self.ui.create_button.clicked.connect(self.createFieldPressed)
        self.ui.derived_values_lineedit.editingFinished.connect(self.derivedValuesEntered)

    def derivedValuesEntered(self):
        """
        Set derived values
        """
        if self._fieldType == 'FieldComponent':
            values = self._parseVectorInteger(self.ui.derived_values_lineedit)
            if self._field and self._field.isValid():
                numberOfComponents = self._field.getNumberOfComponents()
                derivedField = self._field.castComponent()
                if numberOfComponents == len(values):
                    for i in range(0, numberOfComponents):
                        derivedField.setSourceComponentIndex(i + 1, values[i])
                else:
                    values = []
                    for i in range(1, 1 + numberOfComponents):
                        values.append(derivedField.getSourceComponentIndex(i))
            self._displayVectorInteger(self.ui.derived_values_lineedit, values)
        elif self._fieldType == 'FieldMatrixMultiply' or self._fieldType == 'FieldTranspose' \
                or self._fieldType == "FieldFiniteElement" or self._fieldType == "FieldNodeValue" \
                or self._fieldType == "FieldDerivative" or self._fieldType == "FieldArgumentReal":
            try:
                value = int(self.ui.derived_values_lineedit.text())
            except:
                value = 0
            if 1 > value:
                self.ui.derived_values_lineedit.setText("")
                ArgonLogger.getLogger().error("Value must be a positive integer")
            else:
                self.ui.derived_values_lineedit.setText(str(value))
        elif self._fieldType == 'FieldStringConstant':
            if self._field and self._field.isValid():
                text = self.ui.derived_values_lineedit.text()
                fieldcache = self._fieldmodule.createFieldcache()
                self._field.assignString(fieldcache, text)
                text = self._field.evaluateString(fieldcache)
                self.ui.derived_values_lineedit.setText(text)
        elif self._fieldType == "FieldConstant":
            values = self._parseVector(self.ui.derived_values_lineedit)
            if self._field and self._field.isValid():
                numberOfComponents = self._field.getNumberOfComponents()
                fieldcache = self._fieldmodule.createFieldcache()
                if numberOfComponents == len(values):
                    self._field.assignReal(fieldcache, values)
                else:
                    returnedValues = self._field.evaluateReal(fieldcache, numberOfComponents)
                    values = returnedValues[1]
            self._displayVector(self.ui.derived_values_lineedit, values)

    def createField(self):
        returnedField = None
        errorMessage = ""
        sourceFields = []
        if self._fieldType == "FieldConcatenate" or self._fieldType == "FieldCrossProduct":
            numberOfSourceFields = int(self.ui.number_of_source_fields_lineedit.text())
        else:
            numberOfSourceFields = FieldTypeToNumberofSourcesList[self._fieldType]
        for i in range(0, numberOfSourceFields):
            sourceFields.append(self._sourceFieldChoosers[i][1].getField())
        if self._fieldType == "FieldLog" or self._fieldType == "FieldSqrt" or self._fieldType == "FieldExp" or \
                self._fieldType == "FieldAbs" or self._fieldType == "FieldIdentity" or \
                self._fieldType == "FieldNot" or self._fieldType == "FieldSin" or \
                self._fieldType == "FieldCoordinateTransformation" or self._fieldType == "FieldAlias" or \
                self._fieldType == "FieldCos" or self._fieldType == "FieldTan" or self._fieldType == "FieldAsin" or \
                self._fieldType == "FieldAcos" or self._fieldType == "FieldAtan" or self._fieldType == "FieldMagnitude" or \
                self._fieldType == "FieldNormalise" or self._fieldType == "FieldSumComponents" or \
                self._fieldType == "FieldDeterminant" or self._fieldType == "FieldIsDefined" or \
                self._fieldType == "FieldEigenvalues" or self._fieldType == "FieldMatrixInvert":
            if sourceFields[0] and sourceFields[0].isValid():
                methodToCall = getattr(self._fieldmodule, "create" + self._fieldType)
                returnedField = methodToCall(sourceFields[0])
            else:
                errorMessage = " Missing source field(s)."
        elif self._fieldType == "FieldEigenvectors":
            if sourceFields[0] and sourceFields[0].isValid():
                eigenvaluesField = sourceFields[0].castEigenvalues()
                if eigenvaluesField and eigenvaluesField.isValid():
                    returnedField = self._fieldmodule.createFieldEigenvectors(eigenvaluesField)
                else:
                    errorMessage = " Invalid eigenvalues field."
            else:
                errorMessage = " Missing source field(s)."
        elif self._fieldType == "FieldAdd" or self._fieldType == "FieldPower" or self._fieldType == "FieldMultiply" or \
                self._fieldType == "FieldDivide" or self._fieldType == "FieldSubtract" or self._fieldType == "FieldAnd" or \
                self._fieldType == "FieldGreaterThan" or self._fieldType == "FieldLessThan" or self._fieldType == "FieldOr" or \
                self._fieldType == "FieldXor" or self._fieldType == "FieldAtan2" or self._fieldType == "FieldDotProduct" or \
                self._fieldType == 'FieldVectorCoordinateTransformation' or self._fieldType == 'FieldCurl' or \
                self._fieldType == 'FieldDivergence' or self._fieldType == 'FieldEmbedded' or self._fieldType == 'FieldGradient' or \
                self._fieldType == "FieldFibreAxes" or self._fieldType == "FieldProjection" or self._fieldType == "FieldTimeLookup" or \
                self._fieldType == "FieldEqualTo":
            if sourceFields[0] and sourceFields[0].isValid() and \
                    sourceFields[1] and sourceFields[1].isValid():
                methodToCall = getattr(self._fieldmodule, "create" + self._fieldType)
                returnedField = methodToCall(sourceFields[0], sourceFields[1])
            else:
                errorMessage = " Missing source field(s)."
        elif self._fieldType == "FieldIf":
            if sourceFields[0] and sourceFields[0].isValid() and \
                    sourceFields[1] and sourceFields[1].isValid() and \
                    sourceFields[2] and sourceFields[2].isValid():
                methodToCall = getattr(self._fieldmodule, "create" + self._fieldType)
                returnedField = methodToCall(sourceFields[0], sourceFields[1], sourceFields[2])
            else:
                errorMessage = " Missing source field(s)."
        elif self._fieldType == 'FieldComponent':
            if sourceFields[0] and sourceFields[0].isValid():
                values = self._parseVectorInteger(self.ui.derived_values_lineedit)
                if len(values) > 0:
                    returnedField = self._fieldmodule.createFieldComponent(sourceFields[0], values)
                else:
                    errorMessage = " Missing component index(es)."
            else:
                errorMessage = " Missing source field(s)."
        elif self._fieldType == "FieldConstant":
            values = self._parseVector(self.ui.derived_values_lineedit)
            if len(values) > 0:
                returnedField = self._fieldmodule.createFieldConstant(values)
            else:
                errorMessage = " Missing values."
        elif self._fieldType == "FieldStringConstant":
            text = self.ui.derived_values_lineedit.text()
            if text:
                returnedField = self._fieldmodule.createFieldStringConstant(text)
        elif self._fieldType == "FieldStoredString" or self._fieldType == "FieldIsExterior":
            methodToCall = getattr(self._fieldmodule, "create" + self._fieldType)
            returnedField = methodToCall()
        elif self._fieldType == "FieldMatrixMultiply":
            if sourceFields[0] and sourceFields[0].isValid() and \
                    sourceFields[1] and sourceFields[1].isValid():
                value = int(self.ui.derived_values_lineedit.text())
                returnedField = self._fieldmodule.createFieldMatrixMultiply( \
                    value, sourceFields[0], sourceFields[1])
            else:
                errorMessage = " Missing source field(s)."
        elif self._fieldType == "FieldDerivative":
            if sourceFields[0] and sourceFields[0].isValid():
                value = int(self.ui.derived_values_lineedit.text())
                returnedField = self._fieldmodule.createFieldDerivative(sourceFields[0], value)
            else:
                errorMessage = " Missing source field(s)."
        elif self._fieldType == "FieldTranspose":
            if sourceFields[0] and sourceFields[0].isValid():
                value = int(self.ui.derived_values_lineedit.text())
                returnedField = self._fieldmodule.createFieldTranspose(value, sourceFields[0])
            else:
                errorMessage = " Missing source field(s)."
        elif self._fieldType == "FieldFiniteElement" or self._fieldType == "FieldArgumentReal":
            value = int(self.ui.derived_values_lineedit.text())
            methodToCall = getattr(self._fieldmodule, "create" + self._fieldType)
            returnedField = methodToCall(value)
        elif self._fieldType == "FieldEdgeDiscontinuity":
            if sourceFields[0] and sourceFields[0].isValid():
                returnedField = self._fieldmodule.createFieldEdgeDiscontinuity(sourceFields[0])
                if returnedField and returnedField.isValid():
                    returnedField.setMeasure(self.getDerivedChooser1Value())
                    if sourceFields[1] and sourceFields[1].isValid():
                        returnedField.setConditionalField(sourceFields[1])
            else:
                errorMessage = " Missing source field(s)."
        elif self._fieldType == "FieldNodeValue":
            if sourceFields[0] and sourceFields[0].isValid():
                versionNumber = int(self.ui.derived_values_lineedit.text())
                if versionNumber > 0:
                    valueLabel = self.getDerivedChooser1Value()
                    returnedField = self._fieldmodule.createFieldNodeValue(sourceFields[0], \
                                                                           valueLabel, versionNumber)
                else:
                    errorMessage = " version number must be starting from 1."
            else:
                errorMessage = " Missing source field(s)."
        elif self._fieldType == "FieldIsOnFace":
            faceType = self.getDerivedChooser1Value()
            returnedField = self._fieldmodule.createFieldIsOnFace(faceType)
        elif self._fieldType == "FieldStoredMeshLocation":
            meshDimension = self.getDerivedChooser1Value()
            mesh = self._fieldmodule.findMeshByDimension(meshDimension)
            if mesh and mesh.isValid():
                returnedField = self._fieldmodule.createFieldStoredMeshLocation(mesh)
            else:
                errorMessage = " Invalid mesh."
        elif self._fieldType == "FieldFindMeshLocation":
            if sourceFields[0] and sourceFields[0].isValid() and \
                    sourceFields[1] and sourceFields[1].isValid():
                meshName = self.getDerivedChooser2Value()
                mesh = self._fieldmodule.findMeshByName(meshName)
                if mesh and mesh.isValid():
                    returnedField = self._fieldmodule.createFieldFindMeshLocation( \
                        sourceFields[0], sourceFields[1], mesh)
                    if returnedField and returnedField.isValid():
                        searchMode = self.getDerivedChooser1Value()
                        returnedField.setSearchMode(searchMode)
                        searchMeshName = self.getDerivedChooser3Value()
                        searchMesh = self._fieldmodule.findMeshByName(searchMeshName)
                        returnedField.setSearchMesh(searchMesh)
                else:
                    errorMessage = " Invalid mesh."
            else:
                errorMessage = " Missing source field(s)."
        elif self._fieldType == "FieldConcatenate" or self._fieldType == "FieldCrossProduct":
            valid = True
            for i in range(0, numberOfSourceFields):
                if not (sourceFields[i] and sourceFields[i].isValid()):
                    valid = False
                    break
            if valid:
                methodToCall = getattr(self._fieldmodule, "create" + self._fieldType)
                returnedField = methodToCall(sourceFields)
            else:
                errorMessage = " Missing source field(s)."
        elif self._fieldType == "FieldTimeValue":
            if self._timekeeper and self._timekeeper.isValid():
                returnedField = self._fieldmodule.createFieldTimeValue(self._timekeeper)
            else:
                errorMessage = " Missing timekeeper."

        elif self._fieldType == "FieldApply":
            if sourceFields[0] and sourceFields[0].isValid():
                methodToCall = getattr(self._fieldmodule, "create" + self._fieldType)
                returnedField = methodToCall(sourceFields[0])
            else:
                errorMessage = " Missing source field(s)."

        if returnedField and returnedField.isValid():
            returnedField.setManaged(True)
        else:
            ArgonLogger.getLogger().error("Can't create " + self._fieldType + "." + errorMessage)
        return returnedField

    def createFieldPressed(self):
        if self._createMode and self._fieldmodule:
            if self._fieldType:
                self._fieldmodule.beginChange()
                returnedField = self.createField()
                if returnedField and returnedField.isValid():
                    # if 0:
                    #     text, ok = QtWidgets.QInputDialog.getText(self, 'Field Name Dialog', 'Enter field name:')
                    #     if ok:
                    #         returnedField.setName(text)
                    #         self._fieldCreated.emit(returnedField, self._fieldType)
                    #     else:
                    #         returnedField.setManaged(False)
                    #         returnedField = None
                    # else:
                    if returnedField.getName() != self.ui.name_lineedit.text():
                        returnedField.setName(self.ui.name_lineedit.text())
                    self._fieldCreated.emit(returnedField, self._fieldType)
                self._fieldmodule.endChange()
            else:
                ArgonLogger.getLogger().error("Must select a field type.")

    def getDerivedChooser1Value(self):
        index = self.ui.derived_chooser_1.currentIndex()
        if self._fieldType == "FieldEdgeDiscontinuity":
            return index + FieldEdgeDiscontinuity.MEASURE_C1
        elif self._fieldType == "FieldFindMeshLocation":
            return index + FieldFindMeshLocation.SEARCH_MODE_EXACT
        elif self._fieldType == "FieldStoredMeshLocation":
            return index + 1
        elif self._fieldType == "FieldIsOnFace":
            return index + Element.FACE_TYPE_ALL
        elif self._fieldType == "FieldNodeValue":
            return index + Node.VALUE_LABEL_VALUE
        return 1

    def getDerivedChooser2Value(self):
        if self._fieldType == "FieldFindMeshLocation":
            return self.ui.derived_chooser_2.currentText()
        return None

    def getDerivedChooser3Value(self):
        index = self.ui.derived_chooser_3.currentIndex()
        if self._fieldType == "FieldFindMeshLocation":
            return self.ui.derived_chooser_3.currentText()
        return None

    def derivedChooser1Changed(self, index):
        if self._field and self._field.isValid():
            if self._fieldType == "FieldEdgeDiscontinuity":
                derivedField = self._field.castEdgetDiscontinuity()
                derivedField.setMeasure(index + FieldEdgeDiscontinuity.MEASURE_C1)
            elif self._fieldType == "FieldFindMeshLocation":
                derivedField = self._field.castFindMeshLocation()
                derivedField.setSearchMode(index + FieldFindMeshLocation.SEARCH_MODE_EXACT)

    def derivedChooser3Changed(self, index):
        if self._field and self._field.isValid():
            if self._fieldType == "FieldFindMeshLocation":
                derivedField = self._field.castFindMeshLocation()
                searchMeshName = self.getDerivedChooser3Value()
                searchMesh = self._fieldmodule.findMeshByName(searchMeshName)
                result = derivedField.setSearchMesh(searchMesh)
                if result != ZINC_OK:
                    # invalid mesh e.g. higher dimension --> restore previous value
                    searchMeshName = derivedField.getSearchMesh().getName()
                    self._setChooserText(self.ui.derived_chooser_3, searchMeshName)

    def sourceField2Changed(self, index):
        if self._field and self._field.isValid():
            if self._fieldType == "FieldEdgeDiscontinuity":
                derivedField = self._field.castEdgetDiscontinuity()
                derivedField.setConditionalField(self._sourceFieldChoosers[1][1].getField())

    def _updateChooser(self, chooser, items):
        """
        Rebuilds the list of items in the ComboBox from the material module
        """
        chooser.blockSignals(True)
        chooser.clear()
        for item in items:
            chooser.addItem(item)
        chooser.blockSignals(False)

    #  self._displayFieldType()

    def _setChooserValue(self, chooser, index):
        chooser.blockSignals(True)
        chooser.setCurrentIndex(index)
        chooser.blockSignals(False)

    def _setChooserText(self, chooser, text):
        chooser.blockSignals(True)
        index = chooser.findText(text)
        chooser.setCurrentIndex(index)
        chooser.blockSignals(False)

    def display_derived(self):
        # print self._fieldType
        # self.ui.derived_groupbox.setTitle(QtWidgets.QApplication.translate("FieldEditorWidget", self._fieldType + ":", None))
        """ hide everything at the beginning """
        self.ui.derived_chooser_1.hide()
        self.ui.derived_chooser_2.hide()
        self.ui.derived_chooser_3.hide()
        self.ui.derived_values_lineedit.hide()
        self.ui.derived_values_label.hide()
        self.ui.derived_combo_label_1.hide()
        self.ui.derived_combo_label_2.hide()
        self.ui.derived_combo_label_3.hide()
        self.ui.derived_groupbox.hide()
        self.ui.applyargumentfields_groupbox.hide()
        if self._fieldType == 'FieldComponent':
            self.ui.derived_values_label.setText(QtWidgets.QApplication.translate("FieldEditorWidget", "Component Indexes:", None))
            self.ui.derived_values_lineedit.show()
            if self._field and self._field.isValid():
                numberOfComponents = self._field.getNumberOfComponents()
                derivedField = self._field.castComponent()
                values = []
                for i in range(1, 1 + numberOfComponents):
                    values.append(derivedField.getSourceComponentIndex(i))
                self._displayVectorInteger(self.ui.derived_values_lineedit, values)
            else:
                self.ui.derived_values_lineedit.setPlaceholderText("Enter values")
                self._sourceFieldChoosers[0][1].setConditional(FieldIsRealValued)
            self.ui.derived_values_lineedit.setEnabled(True)
            self.ui.derived_values_label.show()
            self.ui.derived_groupbox.show()
        elif self._fieldType == 'FieldEdgeDiscontinuity':
            self._updateChooser(self.ui.derived_chooser_1, MeasureType)
            index = 0
            conditionaField = self._sourceFieldChoosers[1][1].getField()
            self._sourceFieldChoosers[1][1].setConditional(FieldIsScalar)
            if self._field and self._field.isValid():
                index = self._field.castEdgeDiscontinuity().getMeasure() - FieldEdgeDiscontinuity.MEASURE_C1
                self._sourceFieldChoosers[1][1].setField(conditionaField)
                self._sourceFieldChoosers[1][1].currentIndexChanged.connect(self.sourceField2Changed)
            else:
                self._sourceFieldChoosers[0][1].setConditional(FieldIsRealValued)
            self._setChooserValue(self.ui.derived_chooser_1, index)
            self.ui.derived_combo_label_1.setText(QtWidgets.QApplication.translate("FieldEditorWidget", "Measure:", None))
            self._sourceFieldChoosers[1][0].setText(QtWidgets.QApplication.translate("FieldEditorWidget", "Conditional Field:", None))
            self._sourceFieldChoosers[1][1].setEnabled(True)
            self.ui.derived_combo_label_1.show()
            self.ui.derived_chooser_1.show()
            self.ui.derived_groupbox.show()
        elif self._fieldType == 'FieldFindMeshLocation':
            self._updateChooser(self.ui.derived_chooser_1, SearchMode)
            self.ui.derived_combo_label_1.setText(QtWidgets.QApplication.translate("FieldEditorWidget", "Search Mode:", None))
            self._updateChooser(self.ui.derived_chooser_2, MeshName)
            self.ui.derived_combo_label_2.setText(QtWidgets.QApplication.translate("FieldEditorWidget", "Mesh:", None))
            searchMeshNames = copy(MeshName)
            field_iterator = self._fieldmodule.createFielditerator()
            field = field_iterator.next()
            while field.isValid():
                if field.castElementGroup().isValid():
                    searchMeshNames.append(field.getName())
                field = field_iterator.next()
            self._updateChooser(self.ui.derived_chooser_3, searchMeshNames)
            self.ui.derived_combo_label_3.setText(QtWidgets.QApplication.translate("FieldEditorWidget", "Search mesh:", None))
            index = 0
            if self._field and self._field.isValid():
                derivedField = self._field.castFindMeshLocation()
                index = derivedField.getSearchMode() - FieldFindMeshLocation.SEARCH_MODE_EXACT
                self._setChooserValue(self.ui.derived_chooser_1, index)
                meshName = derivedField.getMesh().getName()
                self._setChooserText(self.ui.derived_chooser_2, meshName)
                self.ui.derived_chooser_2.setEnabled(False)
                searchMeshName = derivedField.getSearchMesh().getName()
                self._setChooserText(self.ui.derived_chooser_3, searchMeshName)
            else:
                self.ui.derived_chooser_2.setEnabled(True)
                self._sourceFieldChoosers[0][1].setConditional(FieldIsRealValued)
                self._sourceFieldChoosers[1][1].setConditional(FieldIsRealValued)
                self._setChooserText(self.ui.derived_chooser_2, MeshName[-1])  # default to mesh3d
                self._setChooserText(self.ui.derived_chooser_3, MeshName[-1])  # default to mesh3d
            self.ui.derived_chooser_1.setEnabled(True)
            self.ui.derived_combo_label_1.show()
            self.ui.derived_chooser_1.show()
            self.ui.derived_combo_label_2.show()
            self.ui.derived_chooser_2.show()
            self.ui.derived_combo_label_3.show()
            self.ui.derived_chooser_3.show()
            self._sourceFieldChoosers[1][0].setText(QtWidgets.QApplication.translate("FieldEditorWidget", "Mesh Field:", None))
            self.ui.derived_groupbox.show()
        elif self._fieldType == 'FieldStoredMeshLocation':
            self._updateChooser(self.ui.derived_chooser_1, MeshName)
            if self._field and self._field.isValid():
                derivedField = self._field.castStoredMeshLocation()
                meshName = derivedField.getMesh().getName()
                self._setChooserText(self.ui.derived_chooser_1, meshName)
                self.ui.derived_chooser_1.setEnabled(False)
            else:
                self.ui.derived_chooser_1.setEnabled(True)
                self._setChooserText(self.ui.derived_chooser_1, MeshName[-1])  # default to mesh3d
            self.ui.derived_combo_label_1.setText(QtWidgets.QApplication.translate("FieldEditorWidget", "Mesh:", None))
            self.ui.derived_combo_label_1.show()
            self.ui.derived_chooser_1.show()
            self.ui.derived_groupbox.show()
            self.ui.derived_groupbox.show()
        elif self._fieldType == 'FieldDerivative':
            self.ui.derived_values_label.setText(QtWidgets.QApplication.translate("FieldEditorWidget", "Xi Index:", None))
            self.ui.derived_values_lineedit.show()
            self.ui.derived_values_label.show()
            self.ui.derived_groupbox.show()
            if not self._field or not self._field.isValid():
                self._sourceFieldChoosers[0][1].setConditional(FieldIsRealValued)
                self.ui.derived_values_lineedit.setEnabled(True)
                self.ui.derived_values_lineedit.setText("")
            else:
                self.ui.derived_values_lineedit.setEnabled(False)
        elif self._fieldType == 'FieldMatrixMultiply' or self._fieldType == 'FieldTranspose':
            self.ui.derived_values_label.setText(QtWidgets.QApplication.translate("FieldEditorWidget", "Number of Rows:", None))
            self.ui.derived_values_lineedit.show()
            self.ui.derived_values_label.show()
            self.ui.derived_groupbox.show()
            if not self._field or not self._field.isValid():
                self._sourceFieldChoosers[0][1].setConditional(FieldIsRealValued)
                if self._fieldType == 'FieldMatrixMultiply':
                    self._sourceFieldChoosers[1][1].setConditional(FieldIsRealValued)
                self.ui.derived_values_lineedit.setEnabled(True)
                self.ui.derived_values_lineedit.setText("")
            else:
                self.ui.derived_values_lineedit.setEnabled(False)
        elif self._fieldType == 'FieldStringConstant':
            if self._field and self._field.isValid():
                text = ""
                fieldcache = self._fieldmodule.createFieldcache()
                text = self._field.evaluateString(fieldcache)
                self.ui.derived_values_lineedit.setText(text)
            else:
                self.ui.derived_values_lineedit.setPlaceholderText("Enter strings")
            self.ui.derived_values_label.setText(QtWidgets.QApplication.translate("FieldEditorWidget", "String Values:", None))
            self.ui.derived_values_lineedit.show()
            self.ui.derived_values_label.show()
            self.ui.derived_values_lineedit.setEnabled(True)
            self.ui.derived_groupbox.show()
        elif self._fieldType == 'FieldVectorCoordinateTransformation':
            self._sourceFieldChoosers[0][0].setText(QtWidgets.QApplication.translate("FieldEditorWidget", "Vector Field:", None))
            self._sourceFieldChoosers[1][0].setText(QtWidgets.QApplication.translate("FieldEditorWidget", "Coordinate Field:", None))
            if not self._field or not self._field.isValid():
                self._sourceFieldChoosers[0][1].setConditional(FieldIsOrientationScaleCapable)
                self._sourceFieldChoosers[1][1].setConditional(FieldIsCoordinateCapable)
        elif self._fieldType == 'FieldCurl':
            self._sourceFieldChoosers[0][0].setText(QtWidgets.QApplication.translate("FieldEditorWidget", "Vector Field:", None))
            self._sourceFieldChoosers[1][0].setText(QtWidgets.QApplication.translate("FieldEditorWidget", "Coordinate Field:", None))
            if not self._field or not self._field.isValid():
                self._sourceFieldChoosers[0][1].setConditional(FieldIsRCAndThreeComponents)
                self._sourceFieldChoosers[1][1].setConditional(FieldIsRCAndThreeComponents)
        elif self._fieldType == 'FieldDivergence':
            self._sourceFieldChoosers[0][0].setText(QtWidgets.QApplication.translate("FieldEditorWidget", "Vector Field:", None))
            self._sourceFieldChoosers[1][0].setText(QtWidgets.QApplication.translate("FieldEditorWidget", "Coordinate Field:", None))
            if not self._field or not self._field.isValid():
                self._sourceFieldChoosers[0][1].setConditional(FieldIsRCAndCoordinateCapable)
                self._sourceFieldChoosers[1][1].setConditional(FieldIsRCAndCoordinateCapable)
        elif self._fieldType == 'FieldEmbedded':
            self._sourceFieldChoosers[1][0].setText(QtWidgets.QApplication.translate("FieldEditorWidget", "Embedded Location:", None))
            if not self._field or not self._field.isValid():
                self._sourceFieldChoosers[0][1].setConditional(FieldIsRealValued)
                self._sourceFieldChoosers[1][1].setConditional(FieldIsMeshLocation)
        elif self._fieldType == "FieldIsOnFace":
            if self._field and self._field.isValid():
                self.ui.derived_chooser_1.setEnabled(False)
            else:
                self.ui.derived_chooser_1.setEnabled(True)
            self._updateChooser(self.ui.derived_chooser_1, FaceType)
            self.ui.derived_combo_label_1.setText(QtWidgets.QApplication.translate("FieldEditorWidget", "Face Type:", None))
            self.ui.derived_combo_label_1.show()
            self.ui.derived_chooser_1.show()
            self.ui.derived_groupbox.show()
        elif self._fieldType == "FieldNodeValue":
            self.ui.derived_values_label.setText(QtWidgets.QApplication.translate("FieldEditorWidget", "Version Number:", None))
            self.ui.derived_values_lineedit.show()
            self.ui.derived_values_label.show()
            self._updateChooser(self.ui.derived_chooser_1, ValueType)
            if self._field and self._field.isValid():
                self.ui.derived_chooser_1.setEnabled(False)
                self.ui.derived_values_lineedit.setEnabled(False)
                self.ui.derived_values_lineedit.setText("")
            else:
                self.ui.derived_chooser_1.setEnabled(True)
                self.ui.derived_values_lineedit.setEnabled(True)
                self.ui.derived_values_lineedit.setPlaceholderText("Enter Version Number")
                self._sourceFieldChoosers[0][1].setConditional(FieldIsFiniteElement)
            self.ui.derived_combo_label_1.setText(QtWidgets.QApplication.translate("FieldEditorWidget", "Value Type:", None))
            self.ui.derived_combo_label_1.show()
            self.ui.derived_chooser_1.show()
            self.ui.derived_groupbox.show()
        elif self._fieldType == "FieldConstant":
            if self._field and self._field.isValid():
                text = ""
                valuesCount = self._field.getNumberOfComponents()
                fieldcache = self._fieldmodule.createFieldcache()
                values = self._field.evaluateReal(fieldcache, valuesCount)
                self._displayVector(self.ui.derived_values_lineedit, values[1])
            else:
                self.ui.derived_values_lineedit.setPlaceholderText("Enter values")
            self.ui.derived_values_label.setText(QtWidgets.QApplication.translate("FieldEditorWidget", "Constant Values:", None))
            self.ui.derived_values_lineedit.show()
            self.ui.derived_values_label.show()
            self.ui.derived_values_lineedit.setEnabled(True)
            self.ui.derived_groupbox.show()
        elif self._fieldType == "FieldGradient":
            self._sourceFieldChoosers[1][0].setText(QtWidgets.QApplication.translate("FieldEditorWidget", "Coordinate Field:", None))
            if not self._field or not self._field.isValid():
                self._sourceFieldChoosers[0][1].setConditional(FieldIsRealValued)
                self._sourceFieldChoosers[1][1].setConditional(FieldIsCoordinateCapable)
        elif self._fieldType == "FieldFibreAxes":
            self._sourceFieldChoosers[0][0].setText(QtWidgets.QApplication.translate("FieldEditorWidget", "Fibre Field:", None))
            self._sourceFieldChoosers[1][0].setText(QtWidgets.QApplication.translate("FieldEditorWidget", "Coordinate Field:", None))
            if not self._field or not self._field.isValid():
                self._sourceFieldChoosers[0][1].setConditional(FieldIsCoordinateCapable)
                self._sourceFieldChoosers[1][1].setConditional(FieldIsCoordinateCapable)
        elif self._fieldType == "FieldEigenvectors":
            self._sourceFieldChoosers[0][0].setText(QtWidgets.QApplication.translate("FieldEditorWidget", "Eigenvalues Field:", None))
            if not self._field or not self._field.isValid():
                self._sourceFieldChoosers[0][1].setConditional(FieldIsEigenvalues)
        elif self._fieldType == "FieldProjection":
            self._sourceFieldChoosers[1][0].setText(QtWidgets.QApplication.translate("FieldEditorWidget", "Projection Matrix Field:", None))
            if not self._field or not self._field.isValid():
                self._sourceFieldChoosers[0][1].setConditional(FieldIsRealValued)
                self._sourceFieldChoosers[1][1].setConditional(FieldIsRealValued)
        elif self._fieldType == "FieldTimeLookup":
            self._sourceFieldChoosers[1][0].setText(QtWidgets.QApplication.translate("FieldEditorWidget", "Time Field:", None))
            if not self._field or not self._field.isValid():
                self._sourceFieldChoosers[1][1].setConditional(FieldIsScalar)
        elif self._fieldType == "FieldFiniteElement" or self._fieldType == "FieldArgumentReal":
            if self._field and self._field.isValid():
                text = str(self._field.getNumberOfComponents())
                self.ui.derived_values_lineedit.setText(text)
                self.ui.derived_values_lineedit.setEnabled(False)
                self.ui.type_coordinate_checkbox.show()
            else:
                self.ui.derived_values_lineedit.setPlaceholderText("Enter values")
                self.ui.derived_values_lineedit.setEnabled(True)
            self.ui.derived_values_label.setText(QtWidgets.QApplication.translate("FieldEditorWidget", "Number Of Components:", None))
            self.ui.derived_values_lineedit.show()
            self.ui.derived_values_label.show()

            self.ui.derived_groupbox.show()

        elif self._fieldType == "FieldApply":
            if self._field and self._field.isValid():
                evaluateField = self._sourceFieldChoosers[0][1].getField()
                evaluateFieldmodule = evaluateField.getFieldmodule()
                fieldIterator = evaluateFieldmodule.createFielditerator()
                field = fieldIterator.next()
                self._argumentFieldPairs = []
                index = 0
                while field.isValid():
                    if field.castArgumentReal().isValid() and evaluateField.dependsOnField(field):
                    # this is an argument field which must be bound to a source field
                        self.displayArgumentFieldsChoosers(index, field)
                        index += 2
                    field = fieldIterator.next()
                if self._bindFieldButton == None:
                    self._bindFieldButton = QtWidgets.QPushButton(self.ui.applyargumentfields_groupbox)
                    self._bindFieldButton.setObjectName(u"bindFieldButton")
                    self._bindFieldButton.setText(u"Bind Field")
                    self._bindFieldButton.clicked.connect(self.bindField)
                    self.ui.gridLayout_11.addWidget(self._bindFieldButton, index, 0, 1, 2)
                self.ui.applyargumentfields_groupbox.show()
            else:
                self.ui.applyargumentfields_groupbox.hide()

        else:
            if self._field and self._field.isValid():
                numberOfSourceFields = self._field.getNumberOfSourceFields()
                for i in range(0, numberOfSourceFields):
                    self._sourceFieldChoosers[i][0].setText(
                        QtWidgets.QApplication.translate("FieldEditorWidget", "Source Field " + str(i + 1), None))
            else:
                if self._fieldType == "FieldLog" or self._fieldType == "FieldSqrt" or self._fieldType == "FieldExp" or \
                        self._fieldType == "FieldAbs" or self._fieldType == "FieldIdentity" or self._fieldType == "FieldConcatenate" or \
                        self._fieldType == "FieldCrossProduct" or self._fieldType == "FieldNot" or self._fieldType == "FieldSin" or \
                        self._fieldType == "FieldCos" or self._fieldType == "FieldTan" or self._fieldType == "FieldAsin" or \
                        self._fieldType == "FieldAcos" or self._fieldType == "FieldAtan" or self._fieldType == "FieldMagnitude" or \
                        self._fieldType == "FieldNormalise" or self._fieldType == "FieldSumComponents" or \
                        self._fieldType == "FieldCoordinateTransformation":
                    self._sourceFieldChoosers[0][1].setConditional(FieldIsRealValued)
                elif self._fieldType == "FieldAdd" or self._fieldType == "FieldPower" or self._fieldType == "FieldMultiply" or \
                        self._fieldType == "FieldDivide" or self._fieldType == "FieldSubtract" or self._fieldType == "FieldIf" or \
                        self._fieldType == "FieldAnd" or \
                        self._fieldType == "FieldGreaterThan" or self._fieldType == "FieldLessThan" or self._fieldType == "FieldOr" or \
                        self._fieldType == "FieldXor" or self._fieldType == "FieldAtan2" or self._fieldType == "FieldDotProduct":
                    self._sourceFieldChoosers[0][1].setConditional(FieldIsRealValued)
                    self._sourceFieldChoosers[1][1].setConditional(FieldIsRealValued)
                elif self._fieldType == "FieldDeterminant":
                    self._sourceFieldChoosers[0][1].setConditional(FieldIsDeterminantEligible)
                elif self._fieldType == "FieldEigenvalues" or self._fieldType == "FieldMatrixInvert":
                    self._sourceFieldChoosers[0][1].setConditional(FieldIsSquareMatrix)

    def bindField(self):
        applyField = self._field.castApply()
        if applyField.isValid():
            for fieldPair in self._argumentFieldPairs:
                applyField.setBindArgumentSourceField(fieldPair[0].getField(),fieldPair[1].getField())
        self._updateWidgets()

    def displaySourceFieldsChoosers(self, numberOfSourceFields):
        self.ui.region_of_apply_fields_label.hide()
        self.ui.region_of_apply_fields_chooser.hide()
        numberOfExistingWidgets = len(self._sourceFieldChoosers)
        if self._fieldType == "FieldConcatenate" or self._fieldType == "FieldCrossProduct":
            if numberOfSourceFields == -1:
                numberOfSourceFields = 1
            self.ui.number_of_source_fields_lineedit.setEnabled(True)
        else:
            self.ui.number_of_source_fields_lineedit.setEnabled(False)
        if self._fieldType == "FieldApply":
            self.ui.region_of_apply_fields_label.show()
            self.ui.region_of_apply_fields_chooser.show()
            self.ui.region_of_apply_fields_chooser.setRootRegion(self._fieldmodule.getRegion().getRoot())
            self.ui.region_of_apply_fields_chooser.setEnabled(True)
            evaluateRegion = self._fieldmodule.getRegion()
            if self._field and self._field.isValid():
                evaluateField = self._field.getSourceField(1)
                if (evaluateField) and evaluateField.isValid():
                    evaluateRegion = evaluateField.getFieldmodule().getRegion()
                self.ui.region_of_apply_fields_chooser.setEnabled(False)
            self.ui.region_of_apply_fields_chooser.setRegion(evaluateRegion)

        if numberOfSourceFields > numberOfExistingWidgets:
            for i in range(numberOfExistingWidgets, numberOfSourceFields):
                index = i + 2
                sourceFieldLabel = QtWidgets.QLabel(self.ui.sourcefields_groupbox)
                sourceFieldLabel.setObjectName("sourcefield_label" + str(index))
                self.ui.gridLayout_4.addWidget(sourceFieldLabel, index, 0, 1, 1)
                sourceFieldChooser = FieldChooserWidget(self.ui.sourcefields_groupbox)
                sourceFieldChooser.setSizeAdjustPolicy(QtWidgets.QComboBox.AdjustToContents)
                sourceFieldChooser.setObjectName("sourcefield_chooser" + str(index))
                self.ui.gridLayout_4.addWidget(sourceFieldChooser, index, 1, 1, 1)
                sourceFieldChooser.allowUnmanagedField(True)
                sourceFieldChooser.setNullObjectName("-")
                sourceFieldChooser.setRegion(self._fieldmodule.getRegion())
                self._sourceFieldChoosers.append([sourceFieldLabel, sourceFieldChooser])
        numberOfExistingWidgets = len(self._sourceFieldChoosers)
        for i in range(0, numberOfSourceFields):
            self._sourceFieldChoosers[i][0].show()
            self._sourceFieldChoosers[i][0].setText(QtWidgets.QApplication.translate("FieldEditorWidget", "Source Field " + str(i + 1), None))
            self._sourceFieldChoosers[i][1].show()
            if self._field and self._field.isValid():
                self._sourceFieldChoosers[i][1].setConditional(None)
                sourceField = self._field.getSourceField(i + 1)
                if (sourceField) and sourceField.isValid():
                    sourceRegion = sourceField.getFieldmodule().getRegion()
                    self._sourceFieldChoosers[i][1].setRegion(sourceRegion)
                self._sourceFieldChoosers[i][1].setField(sourceField)
                self._sourceFieldChoosers[i][1].setEnabled(False)
            else:
                self._sourceFieldChoosers[i][1].setField(None)
                self._sourceFieldChoosers[i][1].setEnabled(True)
            self._sourceFieldChoosers[i][1].disconnect(self._sourceFieldChoosers[i][1])
        for i in range(numberOfSourceFields, numberOfExistingWidgets):
            self._sourceFieldChoosers[i][0].hide()
            self._sourceFieldChoosers[i][1].hide()
            self._sourceFieldChoosers[i][1].setField(None)
            self._sourceFieldChoosers[i][1].disconnect(self._sourceFieldChoosers[i][1])
        self.ui.number_of_source_fields_lineedit.setText(str(numberOfSourceFields))

    def applyFieldRegionChanged(self, index):
        self._sourceFieldChoosers[0][1].setRegion(self.ui.region_of_apply_fields_chooser.getRegion())

    def displayArgumentFieldsChoosers(self, index, argument_field):
        argumentFieldLabel = QtWidgets.QLabel(self.ui.applyargumentfields_groupbox)
        argumentFieldLabel.setObjectName("argumentfield_label" + str(index))
        argumentFieldLabel.setText(QtWidgets.QApplication.translate("FieldEditorWidget", "Bind Argument Field " + str(int(index/2 + 1)), None))
        self.ui.gridLayout_11.addWidget(argumentFieldLabel, index, 0, 1, 1)
        argumentFieldChooser = FieldChooserWidget(self.ui.applyargumentfields_groupbox)
        argumentFieldChooser.setSizeAdjustPolicy(QtWidgets.QComboBox.AdjustToContents)
        argumentFieldChooser.setObjectName("argumentfield_chooser" + str(index))
        argumentFieldChooser.setRegion(argument_field.getFieldmodule().getRegion())
        argumentFieldChooser.setConditional(None)
        argumentFieldChooser.setField(argument_field)
        argumentFieldChooser.setEnabled(False)
        argumentFieldChooser.disconnect(argumentFieldChooser)
        self.ui.gridLayout_11.addWidget(argumentFieldChooser, index, 1, 1, 1)

        sourceFieldLabel = QtWidgets.QLabel(self.ui.applyargumentfields_groupbox)
        sourceFieldLabel.setObjectName("applysourcefield_label" + str(index))
        sourceFieldLabel.setText(QtWidgets.QApplication.translate("FieldEditorWidget", "Bind Source Field " + str(int(index/2 + 1)), None))
        self.ui.gridLayout_11.addWidget(sourceFieldLabel, index + 1, 0, 1, 1)
        sourceFieldChooser = FieldChooserWidget(self.ui.applyargumentfields_groupbox)
        sourceFieldChooser.setSizeAdjustPolicy(QtWidgets.QComboBox.AdjustToContents)
        sourceFieldChooser.setObjectName("applysourcefield_chooser" + str(index))
        self.ui.gridLayout_11.addWidget(sourceFieldChooser, index + 1, 1, 1, 1)
        sourceFieldChooser.allowUnmanagedField(True)
        sourceFieldChooser.setNullObjectName("-")
        sourceFieldChooser.setRegion(self._fieldmodule.getRegion())

        self._argumentFieldPairs.append([argumentFieldChooser, sourceFieldChooser])

    def displaySourceFields(self):
        numberOfSourceFields = 0
        if self._field and self._field.isValid():
            numberOfSourceFields = self._field.getNumberOfSourceFields()
        elif self._fieldType and self._createMode:
            numberOfSourceFields = FieldTypeToNumberofSourcesList[self._fieldType]
        self.displaySourceFieldsChoosers(numberOfSourceFields)

    def _coordinateSystemDisplay(self):
        type = Field.COORDINATE_SYSTEM_TYPE_RECTANGULAR_CARTESIAN
        foucs = 0
        if self._field and self._field.isValid():
            type = self._field.getCoordinateSystemType()
            foucs = self._field.getCoordinateSystemFocus()
            newText = STRING_FLOAT_FORMAT.format(foucs)
            self.ui.coordinate_system_focus_lineedit.setText(newText)
            if type == Field.COORDINATE_SYSTEM_TYPE_PROLATE_SPHEROIDAL or type == Field.COORDINATE_SYSTEM_TYPE_OBLATE_SPHEROIDAL:
                self.ui.coordinate_system_focus_lineedit.setEnabled(True)
            else:
                self.ui.coordinate_system_focus_lineedit.setEnabled(False)
            self.ui.coordinate_system_type_chooser.blockSignals(True)
            self.ui.coordinate_system_type_chooser.setCurrentIndex(type - Field.COORDINATE_SYSTEM_TYPE_RECTANGULAR_CARTESIAN)
            self.ui.coordinate_system_type_chooser.blockSignals(False)
            self.ui.coordinate_system_groupbox.show()
        else:
            self.ui.coordinate_system_groupbox.hide()

    def _getNumberOfFields(self):
        numberOfFields = 0
        if self._fieldmodule and self._fieldmodule.isValid():
            iterator = self._fieldmodule.createFielditerator()
            field = iterator.next()
            while field.isValid():
                numberOfFields += 1
                field = iterator.next()
        return numberOfFields

    def _updateWidgets(self):
        # base graphics attributes
        isManaged = False
        isTypeCoordinate = False
        self.ui.managed_checkbox.hide()
        self.ui.type_coordinate_checkbox.hide()
        if self._field:
            isManaged = self._field.isManaged()
            isTypeCoordinate = self._field.isTypeCoordinate()
        if self._fieldType or self._field:
            self.ui.managed_checkbox.blockSignals(True)
            self.ui.managed_checkbox.setCheckState(QtCore.Qt.Checked if isManaged else QtCore.Qt.Unchecked)
            self.ui.managed_checkbox.blockSignals(False)
            self.ui.type_coordinate_checkbox.blockSignals(True)
            self.ui.type_coordinate_checkbox.setCheckState(QtCore.Qt.Checked if isTypeCoordinate else QtCore.Qt.Unchecked)
            self.ui.type_coordinate_checkbox.blockSignals(False)
            self.displaySourceFields()
            self._coordinateSystemDisplay()
            self.ui.general_groupbox.show()
            self.ui.derived_groupbox.show()
            self.ui.sourcefields_groupbox.show()
            self.display_derived()
        else:
            self.ui.general_groupbox.hide()
            self.ui.coordinate_system_groupbox.hide()
            self.ui.derived_groupbox.hide()
            self.ui.applyargumentfields_groupbox.hide()
            self.ui.sourcefields_groupbox.hide()
        self.ui.field_type_chooser.setFieldType(self._fieldType)
        if self._createMode == True:
            self.ui.create_button.show()
            self.ui.field_type_chooser.setEnabled(True)
            self.ui.name_label.show()
            self.ui.name_lineedit.show()
            numberOfFields = self._getNumberOfFields()
            tempname = "temp" + str(numberOfFields + 1)
            self.ui.name_lineedit.setText(tempname)
        else:
            self.ui.field_type_chooser.setEnabled(False)
            self.ui.create_button.hide()
            self.ui.name_label.hide()
            self.ui.name_lineedit.hide()

    def setTimekeeper(self, timekeeper):
        """
        Set when timekeeper changes
        """
        self._timekeeper = timekeeper

    def setFieldmodule(self, fieldmodule):
        """
        Set when fieldmodule changes to initialised widgets dependent on fieldmodule
        """
        self._fieldmodule = fieldmodule
        for i in range(0, len(self._sourceFieldChoosers)):
            self._sourceFieldChoosers[i][1].setRegion(self._fieldmodule.getRegion())
        self._updateWidgets()

    def getField(self):
        """
        Get the field currently in the editor
        """
        return self._field

    def setField(self, field, fieldType):
        """
        Set the field to be edited
        """
        if field and field.isValid():
            self._field = field
            self._fieldType = fieldType
            self._createMode = False
        else:
            self._field = None
            self._fieldType = None
            self._createMode = True
        self._updateWidgets()

    def _displayVectorInteger(self, widget, values):
        """
        Display real vector values in a widget. Also handle scalar
        """
        if isinstance(values, Number):
            newText = int(values)
        else:
            newText = ", ".join(str(value) for value in values)
        widget.setText(newText)

    def _parseVectorInteger(self, widget):
        """
        Return integer vector from comma separated text in line edit widget
        """
        text = widget.text()
        try:
            values = [int(value) for value in text.split(',')]
        except:
            ArgonLogger.getLogger().error("Value must be one or more integers")
            values = []
        return values

    def _displayVector(self, widget, values, numberFormat=STRING_FLOAT_FORMAT):
        """
        Display real vector values in a widget. Also handle scalar
        """
        if isinstance(values, Number):
            newText = STRING_FLOAT_FORMAT.format(values)
        else:
            newText = ", ".join(numberFormat.format(value) for value in values)
        widget.setText(newText)

    def _parseVector(self, widget):
        """
        Return real vector from comma separated text in line edit widget
        """
        text = widget.text()
        try:
            values = [float(value) for value in text.split(',')]
        except:
            ArgonLogger.getLogger().error("Value must be one or more real numbers")
            values = []
        return values

    def coordinateSystemTypeChanged(self, index):
        if self._field:
            self._field.setCoordinateSystemType(index + Field.COORDINATE_SYSTEM_TYPE_RECTANGULAR_CARTESIAN)

    def managedClicked(self, isChecked):
        """
        The managed radio button was clicked
        """
        if self._field:
            self._field.setManaged(isChecked)

    def typeCoordinateClicked(self, isChecked):
        """
        type coordinate clicked 
        """
        if self._field:
            self._field.setTypeCoordinate(isChecked)

    def coordinateSystemFocusEntered(self):
        """
        Set coordinate system focus text in widget
        """
        coordinateSystemFocusText = self.ui.coordinate_system_focus_lineedit.text()
        try:
            coordinateSystemFocus = float(coordinateSystemFocusText)
            self._field.setCoordinateSystemFocus(coordinateSystemFocus)
        except:
            print("Invalid coordinate system focus", coordinateSystemFocusText)
        self._coordinateSystemDisplay()

    def fieldTypeChanged(self):
        self._fieldType = self.ui.field_type_chooser.getFieldType()
        self._updateWidgets()

    def numberOfSourceFieldsEntered(self):
        numberOfSourceFieldsText = self.ui.number_of_source_fields_lineedit.text()
        try:
            numberOfSourceFields = int(numberOfSourceFieldsText)
        except:
            print("Invalid number of source fields", numberOfSourceFieldsText)
        if self._fieldType == "FieldCrossProduct" and numberOfSourceFields > 3:
            numberOfSourceFields = 3
            self.ui.number_of_source_fields_lineedit.setText(str(numberOfSourceFields))
        self.displaySourceFieldsChoosers(numberOfSourceFields)
        if self._fieldType == "FieldConcatenate" and self._fieldType == "FieldCrossProduct":
            for i in range(0, numberOfSourceFields):
                self._sourceFieldChoosers[i][1].setConditional(FieldIsRealValued)

    def enterCreateMode(self):
        """
        Set coordinate system focus text in widget
        """
        self._createMode = True
        self._field = None
        self._fieldType = None
        self._updateWidgets()
