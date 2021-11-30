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
from PySide2 import QtCore, QtGui, QtWidgets

from opencmiss.argon.argonlogger import ArgonLogger
from opencmiss.zinc.status import OK as ZINC_OK
from opencmiss.zinc.field import Field

from opencmiss.zincwidgets.ui.ui_fieldlisteditorwidget import Ui_FieldListEditorWidget

"""
Zinc Field List Editor Widget

Allows a Zinc Field object to be created/edited in Qt / Python.

This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""


def findArgonRegionFromZincRegion(rootArgonRegion, zincRegion):
    """
    Recursively find ArgonRegion within tree starting at supplied
    argonRegion which wraps the given zincRegion.
    :param rootArgonRegion: Root ArgonRegion of tree to search.
    :param zincRegion: Zinc Region to match.
    :return: ArgonRegion or None
    """
    if rootArgonRegion.getZincRegion() == zincRegion:
        return rootArgonRegion
    for index in range(rootArgonRegion.getChildCount()):
        argonRegion = findArgonRegionFromZincRegion(rootArgonRegion.getChild(index), zincRegion)
        if argonRegion:
            return argonRegion
    return None


class FieldListEditorWidget(QtWidgets.QWidget):

    def __init__(self, parent=None):
        """
        Call the super class init functions
        """
        QtWidgets.QWidget.__init__(self, parent)
        # Using composition to include the visual element of the GUI.
        self._ui = Ui_FieldListEditorWidget()
        self._fieldItems = None
        self._rootArgonRegion = None
        self._argonRegion = None
        self._fieldmodule = None
        self._timekeeper = None
        self._ui.setupUi(self)
        self._makeConnections()
        self._field = None

    @QtCore.Slot(Field, str)
    def editorCreateField(self, field, fieldType):
        self._argonRegion.addFieldTypeToDict(field, fieldType)
        self.setField(field)

    def _makeConnections(self):
        self._ui.region_chooser.currentIndexChanged.connect(self._region_changed)
        self._ui.field_listview.clicked.connect(self.fieldListItemClicked)
        self._ui.add_field_button.clicked.connect(self.addFieldClicked)
        self._ui.delete_field_button.clicked.connect(self.deleteFieldClicked)
        self._ui.field_editor._fieldCreated.connect(self.editorCreateField)

    def getFieldmodule(self):
        """
        Get the fieldmodule currently in the editor
        """
        return self._fieldmodule

    def _fieldmoduleCallback(self, fieldmoduleevent):
        """
        Callback for change in fields; may need to rebuild field list
        """
        changeSummary = fieldmoduleevent.getSummaryFieldChangeFlags()
        # print "_fieldmoduleCallback changeSummary =", changeSummary
        if 0 != (changeSummary & (Field.CHANGE_FLAG_IDENTIFIER | Field.CHANGE_FLAG_ADD | Field.CHANGE_FLAG_REMOVE)):
            self._buildFieldsList()

    def setTimekeeper(self, timekeeper):
        """
        Set the current scene in the editor
        """
        if not (timekeeper and timekeeper.isValid()):
            self._timekeeper = None
        else:
            self._timekeeper = timekeeper
        if self._timekeeper:
            self._ui.field_editor.setTimekeeper(self._timekeeper)

    def _setFieldmodule(self, fieldmodule):
        """
        Set the current scene in the editor
        """
        if not (fieldmodule and fieldmodule.isValid()):
            self._fieldmodule = None
        else:
            self._fieldmodule = fieldmodule
        if self._fieldmodule:
            self._ui.field_editor.setFieldmodule(self._fieldmodule)
        self._buildFieldsList()
        if self._fieldmodule:
            self._fieldmodulenotifier = self._fieldmodule.createFieldmodulenotifier()
            self._fieldmodulenotifier.setCallback(self._fieldmoduleCallback)
        else:
            self._fieldmodulenotifier = None

    def _setArgonRegion(self, argonRegion):
        self._argonRegion = argonRegion
        self._setFieldmodule(self._argonRegion.getZincRegion().getFieldmodule())

    def setRootArgonRegion(self, rootArgonRegion):
        """
        Supply new root region on opening new document.
        :param rootArgonRegion: Root ArgonRegion
        """
        self._rootArgonRegion = rootArgonRegion
        self._ui.region_chooser.setRootRegion(self._rootArgonRegion.getZincRegion())
        self._setArgonRegion(rootArgonRegion)

    def listItemEdited(self, item):
        field = item.data()
        if field and field.isValid():
            newName = item.text()
            oldName = field.getName()
            if newName != oldName:
                if field.setName(newName) != ZINC_OK:
                    item.setText(field.getName())
                self._argonRegion.replaceFieldTypeKey(oldName, newName)

    def _buildFieldsList(self):
        """
        Fill the graphics list view with the list of graphics for current region/scene
        """
        if self._fieldItems is not None:
            self._fieldItems.clear()  # Must clear or holds on to field references
        self._fieldItems = QtGui.QStandardItemModel(self._ui.field_listview)
        selectedIndex = None
        if self._fieldmodule:
            selectedField = self._ui.field_editor.getField()
            fieldIterator = self._fieldmodule.createFielditerator()
            field = fieldIterator.next()
            while field and field.isValid():
                name = field.getName()
                item = QtGui.QStandardItem(name)
                item.setData(field)
                item.setCheckable(False)
                item.setEditable(True)
                self._fieldItems.appendRow(item)
                if selectedField and field == selectedField:
                    selectedIndex = self._fieldItems.indexFromItem(item)
                field = fieldIterator.next()
        self._ui.field_listview.setModel(self._fieldItems)
        self._fieldItems.itemChanged.connect(self.listItemEdited)
        # self._ui.graphics_listview.setMovement(QtGui.QListView.Snap)
        # self._ui.graphics_listview.setDragDropMode(QtGui.QListView.InternalMove)
        # self._ui.graphics_listview.setDragDropOverwriteMode(False)
        # self._ui.graphics_listview.setDropIndicatorShown(True)
        if selectedIndex:
            self._ui.field_listview.setCurrentIndex(selectedIndex)
        self._ui.field_listview.show()

    def _displayField(self):
        if self._field and self._field.isValid():
            selectedIndex = None
            i = 0
            # loop through the items until you get None, which
            # means you've passed the end of the list
            while self._fieldItems.item(i):
                field = self._fieldItems.item(i).data()
                if self._field == field:
                    selectedIndex = self._fieldItems.indexFromItem(self._fieldItems.item(i))
                    break
                i += 1
            if selectedIndex:
                self._ui.field_listview.setCurrentIndex(selectedIndex)
            name = self._field.getName()
            fieldTypeDict = self._argonRegion.getFieldTypeDict()
            if name in fieldTypeDict:
                fieldType = fieldTypeDict[name]
                self._ui.field_editor.setField(self._field, fieldType)
            else:
                self._ui.field_editor.setField(self._field, None)
        else:
            self.field_listview.clearSelection()
            self._ui.field_editor.setField(None, None)

    def _region_changed(self, index):
        zincRegion = self._ui.region_chooser.getRegion()
        argonRegion = findArgonRegionFromZincRegion(self._rootArgonRegion, zincRegion)
        self._setArgonRegion(argonRegion)

    def fieldListItemClicked(self, modelIndex):
        model = modelIndex.model()
        item = model.item(modelIndex.row())
        field = item.data()
        self._field = field
        self._displayField()

    def setField(self, field):
        """
        Set the current selected field
        """
        if not field or not field.isValid():
            self._field = None
        else:
            self._field = field
        self._displayField()

    def addFieldClicked(self):
        """do the add field stuff"""
        self._ui.field_editor.enterCreateMode()

    def deleteFieldClicked(self):
        """
        Unmanage a field which will remove it if not in use.
        If it is in use, restore its previous managed state.
        """
        if self._field and self._field.isValid():
            if self._field.isManaged():
                name = self._field.getName()
                # remove references to field in field editor, list items and field member
                self._ui.field_editor.setField(None, None)
                model = self._ui.field_listview.model()
                item = model.findItems(name)[0]
                item.setData(None)
                self._field.setManaged(False)
                self._field = None
                field = self._fieldmodule.findFieldByName(name)
                if field and field.isValid():
                    ArgonLogger.getLogger().info("Can't delete field '" + name + "' while it is in use")
                    # restore field in editor
                    self._field = field
                    self._field.setManaged(True)
                    item.setData(field)
                    fieldType = None
                    fieldTypeDict = self._argonRegion.getFieldTypeDict()
                    if name in fieldTypeDict:
                        fieldType = fieldTypeDict[name]
                    self._ui.field_editor.setField(self._field, fieldType)
