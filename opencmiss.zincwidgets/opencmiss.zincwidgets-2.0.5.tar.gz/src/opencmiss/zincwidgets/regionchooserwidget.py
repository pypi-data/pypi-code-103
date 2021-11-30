"""
Zinc Region Chooser Widget

Widget for choosing a region from a region tree, derived from QComboBox

This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""

from PySide2 import QtCore, QtWidgets


class RegionChooserWidget(QtWidgets.QComboBox):

    def __init__(self, parent=None):
        """
        Call the super class init functions
        """
        QtWidgets.QComboBox.__init__(self, parent)
        self._rootRegion = None
        self._region = None

        self._make_connections()

    def _make_connections(self):
        self.activated.connect(self._buildRegionList)

    def _getRegionIndex(self, findRegion, region, count):
        """
        Recursive function to determine the index of findRegion in the tree under region, starting
        at count. The index matches the position in the combobox.
        :return index, count. Index of findRegion under region tree or None if not found,
        and count of regions searched.
        """
        if region == findRegion:
            return count, None
        child = region.getFirstChild()
        while child.isValid():
            count = count + 1
            found, count = self._getRegionIndex(findRegion, child, count)
            if found is not None:
                return found, None
            child = child.getNextSibling()

        return None, count

    def _addRegionToListRecursive(self, region, parentPath):
        name = region.getName()
        if name is None:
            self.addItem('/')
            path = ''
        else:
            path = parentPath + region.getName()
            self.addItem(path)
        child = region.getFirstChild()
        while child.isValid():
            self._addRegionToListRecursive(child, path + '/')
            child = child.getNextSibling()

    def _buildRegionList(self):
        """
        Rebuilds the list of items in the ComboBox from the region tree
        """
        self.blockSignals(True)
        self.clear()
        self._addRegionToListRecursive(self._rootRegion, '/')
        self.blockSignals(False)
        self.setRegion(self._region)

    def _displayRegion(self):
        """
        Display the currently chosen region in the ComboBox
        """
        self.blockSignals(True)
        count, _ = self._getRegionIndex(self._region, self._rootRegion, 0)
        self.setCurrentIndex(count)
        self.blockSignals(False)

    def getRootRegion(self):
        return self._rootRegion

    def setRootRegion(self, rootRegion):
        """
        Sets the root region that this widget chooses regions from.
        Also sets current region to rootRegion.
        """
        self._rootRegion = rootRegion
        self._region = rootRegion
        self._buildRegionList()

    def getRegion(self):
        """
        Must call this from client's currentIndexChanged() slot to get/update current region
        """
        regionPath = str(self.currentText())
        self._region = self._rootRegion.findSubregionAtPath(regionPath)
        if not self._region.isValid():
            self._region = None;
        return self._region

    def setRegion(self, region):
        """
        Set the currently selected region.
        """
        count, _ = self._getRegionIndex(region, self._rootRegion, 0)
        if count is None:
            return
        self._region = region
        self._displayRegion()
