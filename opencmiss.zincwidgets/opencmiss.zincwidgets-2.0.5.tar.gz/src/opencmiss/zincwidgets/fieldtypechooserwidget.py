"""
   Copyright 2015 University of Auckland

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
from PySide2 import QtWidgets

FieldTypes = ['FieldAbs', 'FieldAcos', 'FieldAdd', 'FieldAlias', 'FieldAnd', 'FieldApply', 'FieldArgumentReal', 'FieldAsin', \
              'FieldAtan', 'FieldAtan2', 'FieldComponent', 'FieldConcatenate', 'FieldConstant', \
              'FieldCoordinateTransformation', 'FieldCos', 'FieldCrossProduct', 'FieldCurl', \
              'FieldDerivative', 'FieldDeterminant', 'FieldDivergence', 'FieldDivide', \
              'FieldDotProduct', 'FieldEdgeDiscontinuity', 'FieldEigenvalues', \
              'FieldEigenvectors', 'FieldEmbedded', 'FieldEqualTo', 'FieldExp', \
              'FieldFibreAxes', 'FieldFindMeshLocation', 'FieldFiniteElement', 'FieldGradient', \
              'FieldGreaterThan', 'FieldIdentity', 'FieldIf', 'FieldIsDefined', 'FieldIsExterior', \
              'FieldIsOnFace', 'FieldLessThan', 'FieldLog', 'FieldMagnitude', 'FieldMatrixInvert', \
              'FieldMatrixMultiply', 'FieldMultiply', 'FieldNodeValue', 'FieldNormalise', 'FieldNot', \
              'FieldOr', 'FieldPower', 'FieldProjection', 'FieldSin', 'FieldSqrt', \
              'FieldStoredMeshLocation', 'FieldStoredString', 'FieldStringConstant', 'FieldSubtract', \
              'FieldSumComponents', 'FieldTan', 'FieldTimeLookup', 'FieldTimeValue', 'FieldTranspose', \
              'FieldVectorCoordinateTransformation', 'FieldXor']


class FieldTypeChooserWidget(QtWidgets.QComboBox):

    def __init__(self, parent=None):
        """
        Call the super class init functions
        """
        QtWidgets.QComboBox.__init__(self, parent)
        self._nullObjectName = "-"
        self._currentFieldType = None
        self._buildFieldTypeList()

    def _buildFieldTypeList(self):
        """
        Rebuilds the list of items in the ComboBox from the material module
        """
        self.blockSignals(True)
        self.clear()
        if self._nullObjectName:
            self.addItem(self._nullObjectName)
        for type in FieldTypes:
            self.addItem(type)
        self.blockSignals(False)
      #  self._displayFieldType()

    def _displayFieldType(self):
        """
        Display the currently chosen field type in the ComboBox
        """
        self.blockSignals(True)
        if self._currentFieldType:
            index = self.findText(self._currentFieldType)
        else:
            index = 0
        self.setCurrentIndex(index)
        self.blockSignals(False)

    def setNullObjectName(self, nullObjectName):
        """
        Enable a null object option with the supplied name e.g. '-' or '<select>'
        Default is None
        """
        self._nullObjectName = nullObjectName

    def getFieldType(self):
        """
        Must call this from currentIndexChanged() slot to get/update current material
        """
        fieldTypeName = self.currentText()
        if self._nullObjectName and (fieldTypeName == self._nullObjectName):
            fieldTypeName = None
        return fieldTypeName
    
    def setFieldType(self, fieldType):
        """
        Set the currently selected field; call after setConditional
        """
        if not fieldType:
            self._currentFieldType = None
        else:
            self._currentFieldType = fieldType
        self._displayFieldType()
    