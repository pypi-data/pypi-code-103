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
from PySide2 import QtCore, QtGui, QtWidgets

from opencmiss.zinc.field import Field
from opencmiss.zinc.graphics import Graphics

from opencmiss.zincwidgets.ui.ui_sceneeditorwidget import Ui_SceneEditorWidget

"""
Zinc Scene Editor Widget

Allows a Zinc Scene object to be edited in Qt / Python.

This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""


class SceneEditorWidget(QtWidgets.QWidget):

    def __init__(self, parent=None):
        """
        Call the super class init functions
        """
        QtWidgets.QWidget.__init__(self, parent)
        self._scene = None
        # Using composition to include the visual element of the GUI.
        self._ui = Ui_SceneEditorWidget()
        self._graphicsItems = None
        self._ui.setupUi(self)

        self._make_connections()

    def _make_connections(self):
        self._ui.region_chooser.currentIndexChanged.connect(self._region_changed)

    def _region_changed(self, index):
        region = self._ui.region_chooser.getRegion()
        self.setScene(region.getScene())

    def setZincRootRegion(self, root_region):
        self._ui.region_chooser.setRootRegion(root_region)
        self.setScene(root_region.getScene())

    def getScene(self):
        """
        Get the scene currently in the editor
        """
        return self._scene

    def setScene(self, scene):
        """
        Set the current scene in the editor
        """
        if not (scene and scene.isValid()):
            self._scene = None
        else:
            self._scene = scene
        self._ui.graphics_editor.setScene(scene)
        if self._scene:
            self._ui.graphics_editor.setGraphics(self._scene.getFirstGraphics())
        self._buildGraphicsList()

    def _getDefaultCoordinateField(self):
        """
        Get the first coordinate field from the current scene
        """
        if self._scene:
            fielditer = self._scene.getRegion().getFieldmodule().createFielditerator()
            field = fielditer.next()
            while field.isValid():
                if field.isTypeCoordinate() and (field.getValueType() == Field.VALUE_TYPE_REAL) and \
                        (field.getNumberOfComponents() <= 3) and field.castFiniteElement().isValid():
                    return field
                field = fielditer.next()
        return None

    def _getGraphicsDisplayName(self, graphics):
        """
        Build a display name from the graphics graphics_type and domain
        """
        graphics_type = graphics.getType()
        fieldDomainType = graphics.getFieldDomainType()
        if graphics_type == Graphics.TYPE_POINTS:
            if fieldDomainType == Field.DOMAIN_TYPE_POINT:
                return "point"
            if fieldDomainType == Field.DOMAIN_TYPE_NODES:
                return "node points"
            if fieldDomainType == Field.DOMAIN_TYPE_DATAPOINTS:
                return "data points"
            return "element points"
        elif graphics_type == Graphics.TYPE_LINES:
            return "lines"
        elif graphics_type == Graphics.TYPE_SURFACES:
            return "surfaces"
        elif graphics_type == Graphics.TYPE_CONTOURS:
            return "contours"
        elif graphics_type == Graphics.TYPE_STREAMLINES:
            return "streamlines"

    def _buildGraphicsList(self):
        """
        Fill the graphics list view with the list of graphics for current region/scene
        """
        if self._graphicsItems is not None:
            self._graphicsItems.clear()  # Must clear or holds on to graphics references
        self._graphicsItems = QtGui.QStandardItemModel(self._ui.graphics_listview)
        selectedIndex = None
        if self._scene:
            selectedGraphics = self._ui.graphics_editor.getGraphics()
            graphics = self._scene.getFirstGraphics()
            while graphics and graphics.isValid():
                name = self._getGraphicsDisplayName(graphics)
                item = QtGui.QStandardItem(name)
                item.setData(graphics)
                item.setCheckable(True)
                item.setEditable(False)
                visible = graphics.getVisibilityFlag()
                item.setCheckState(QtCore.Qt.Checked if visible else QtCore.Qt.Unchecked)
                self._graphicsItems.appendRow(item)
                if graphics == selectedGraphics:
                    selectedIndex = self._graphicsItems.indexFromItem(item)
                graphics = self._scene.getNextGraphics(graphics)
        self._ui.graphics_listview.setModel(self._graphicsItems)
        # self._ui.graphics_listview.setMovement(QtGui.QListView.Snap)
        # self._ui.graphics_listview.setDragDropMode(QtGui.QListView.InternalMove)
        # self._ui.graphics_listview.setDragDropOverwriteMode(False)
        # self._ui.graphics_listview.setDropIndicatorShown(True)
        if selectedIndex:
            self._ui.graphics_listview.setCurrentIndex(selectedIndex)
        self._ui.graphics_listview.show()

    def graphicsListItemClicked(self, modelIndex):
        """
        Either changes visibility flag or selects current graphics
        """
        model = modelIndex.model()
        item = model.item(modelIndex.row())
        graphics = item.data()
        visibilityFlag = item.checkState() == QtCore.Qt.Checked
        graphics.setVisibilityFlag(visibilityFlag)
        selectedModelIndex = self._ui.graphics_listview.currentIndex()
        selectedItem = model.item(selectedModelIndex.row())
        selectedGraphics = selectedItem.data()
        if graphics == selectedGraphics:
            self._ui.graphics_editor.setGraphics(selectedGraphics)

    def addGraphicsEntered(self, name):
        """
        Add a new chosen graphics type
        """
        if not self._scene:
            return
        graphicsType = Graphics.TYPE_INVALID
        fieldDomainType = Field.DOMAIN_TYPE_INVALID
        # name = str(combobox1.currentText())
        if name == "point":
            graphicsType = Graphics.TYPE_POINTS
            fieldDomainType = Field.DOMAIN_TYPE_POINT
        elif name == "node points":
            graphicsType = Graphics.TYPE_POINTS
            fieldDomainType = Field.DOMAIN_TYPE_NODES
        elif name == "data points":
            graphicsType = Graphics.TYPE_POINTS
            fieldDomainType = Field.DOMAIN_TYPE_DATAPOINTS
        elif name == "element points":
            graphicsType = Graphics.TYPE_POINTS
            fieldDomainType = Field.DOMAIN_TYPE_MESH_HIGHEST_DIMENSION
        elif name == "lines":
            graphicsType = Graphics.TYPE_LINES
        elif name == "surfaces":
            graphicsType = Graphics.TYPE_SURFACES
        elif name == "contours":
            graphicsType = Graphics.TYPE_CONTOURS
        elif name == "streamlines":
            graphicsType = Graphics.TYPE_STREAMLINES
        else:
            pass
        if graphicsType != Graphics.TYPE_INVALID:
            self._scene.beginChange()
            graphics = self._scene.createGraphics(graphicsType)
            if fieldDomainType != Field.DOMAIN_TYPE_INVALID:
                graphics.setFieldDomainType(fieldDomainType)
            if fieldDomainType != Field.DOMAIN_TYPE_POINT:
                coordinateField = self._getDefaultCoordinateField()
                if coordinateField is not None:
                    graphics.setCoordinateField(coordinateField)
            self._scene.endChange()
            self._ui.graphics_editor.setGraphics(graphics)
            self._buildGraphicsList()
        self._ui.add_graphics_combobox.setCurrentIndex(0)

    def deleteGraphicsClicked(self):
        """
        Delete the current graphics type
        """
        if not self._scene:
            return
        graphics = self._ui.graphics_editor.getGraphics()
        if graphics:
            nextGraphics = self._scene.getNextGraphics(graphics)
            if not (nextGraphics and nextGraphics.isValid()):
                nextGraphics = self._scene.getPreviousGraphics(graphics)
            if not (nextGraphics and nextGraphics.isValid()):
                nextGraphics = self._scene.getFirstGraphics()
            if nextGraphics == graphics:
                nextGraphics = None
            self._ui.graphics_editor.setGraphics(nextGraphics)
            self._scene.removeGraphics(graphics)
            self._buildGraphicsList()
