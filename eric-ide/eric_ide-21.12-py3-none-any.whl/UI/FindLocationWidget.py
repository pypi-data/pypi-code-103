# -*- coding: utf-8 -*-

# Copyright (c) 2004 - 2021 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a dialog to search for files.
"""

import os
import sys

from PyQt6.QtCore import pyqtSignal, pyqtSlot, Qt, QUrl
from PyQt6.QtGui import QDesktopServices, QImageReader
from PyQt6.QtWidgets import (
    QWidget, QHeaderView, QApplication, QTreeWidgetItem
)

from EricWidgets.EricPathPicker import EricPathPickerModes

from .Ui_FindLocationWidget import Ui_FindLocationWidget

import UI.PixmapCache
from Utilities import direntries
import Utilities


class FindLocationWidget(QWidget, Ui_FindLocationWidget):
    """
    Class implementing a widget to search for files.
    
    The occurrences found are displayed in a QTreeWidget showing the
    filename and the pathname. The file will be opened upon a double click
    onto the respective entry of the list or by pressing the open button.
    
    @signal sourceFile(str) emitted to open a file in the editor
    @signal designerFile(str) emitted to open a Qt-Designer file
    @signal linguistFile(str) emitted to open a Qt-Linguist (*.ts) file
    @signal trpreview([str]) emitted to preview Qt-Linguist (*.qm) files
    @signal pixmapFile(str) emitted to open a pixmap file
    @signal svgFile(str) emitted to open a SVG file
    @signal umlFile(str) emitted to open an eric UML file
    """
    sourceFile = pyqtSignal(str)
    designerFile = pyqtSignal(str)
    linguistFile = pyqtSignal(str)
    trpreview = pyqtSignal(list)
    pixmapFile = pyqtSignal(str)
    svgFile = pyqtSignal(str)
    umlFile = pyqtSignal(str)
    
    def __init__(self, project, parent=None):
        """
        Constructor
        
        @param project reference to the project object
        @type Project
        @param parent parent widget of this dialog
        @type QWidget
        """
        super().__init__(parent)
        self.setupUi(self)
        
        self.layout().setContentsMargins(0, 3, 0, 0)
        
        self.searchDirPicker.setMode(EricPathPickerModes.DIRECTORY_MODE)
        
        self.fileList.headerItem().setText(self.fileList.columnCount(), "")
        
        self.stopButton.setEnabled(False)
        self.stopButton.clicked.connect(self.__stopSearch)
        self.stopButton.setIcon(UI.PixmapCache.getIcon("stopLoading"))
        
        self.findButton.setEnabled(False)
        self.findButton.clicked.connect(self.__searchFile)
        self.findButton.setIcon(UI.PixmapCache.getIcon("find"))
        
        self.openButton.setIcon(UI.PixmapCache.getIcon("open"))
        self.openButton.clicked.connect(self.__openFile)
        
        self.__project = project
        self.__project.projectOpened.connect(self.__projectOpened)
        self.__project.projectClosed.connect(self.__projectClosed)
        self.extsepLabel.setText(os.extsep)
        
        self.__shouldStop = False
        
        self.fileNameEdit.returnPressed.connect(self.__searchFile)
        self.fileExtEdit.returnPressed.connect(self.__searchFile)
        
        self.__projectClosed()
    
    @pyqtSlot()
    def __stopSearch(self):
        """
        Private slot to handle the stop button being pressed.
        """
        self.__shouldStop = True
    
    @pyqtSlot()
    def __openFile(self, itm=None):
        """
        Private slot to open a file.
        
        It emits a signal depending on the file extension.
        
        @param itm item to be opened
        @type QTreeWidgetItem
        """
        if itm is None:
            itm = self.fileList.currentItem()
        if itm is not None:
            fileName = itm.text(0)
            filePath = itm.text(1)
            fileExt = os.path.splitext(fileName)[1]
            fullName = os.path.join(filePath, fileName)
            
            if fileExt == ".ui":
                self.designerFile.emit(fullName)
            elif fileExt == ".ts":
                self.linguistFile.emit(fullName)
            elif fileExt == ".qm":
                self.trpreview.emit([fullName])
            elif fileExt in (".egj", ".e5g"):
                self.umlFile.emit(fullName)
            elif fileExt == ".svg":
                self.svgFile.emit(fullName)
            elif fileExt[1:] in QImageReader.supportedImageFormats():
                self.pixmapFile.emit(fullName)
            else:
                if Utilities.MimeTypes.isTextFile(fullName):
                    self.sourceFile.emit(fullName)
                else:
                    QDesktopServices.openUrl(QUrl(fullName))
    
    @pyqtSlot()
    def __searchFile(self):
        """
        Private slot to handle the search.
        """
        fileName = self.fileNameEdit.text()
        if not fileName:
            self.fileList.clear()
            return
        
        fileExt = self.fileExtEdit.text()
        if not fileExt and Utilities.isWindowsPlatform():
            self.fileList.clear()
            return
        
        self.findStatusLabel.clear()
        
        patternFormat = fileExt and "{0}{1}{2}" or "{0}*{1}{2}"
        fileNamePattern = patternFormat.format(
            fileName, os.extsep, fileExt and fileExt or '*')
        
        searchPaths = []
        if (
            self.searchDirCheckBox.isChecked() and
            self.searchDirPicker.text() != ""
        ):
            searchPaths.append(self.searchDirPicker.text())
        if self.projectCheckBox.isChecked():
            searchPaths.append(self.__project.getProjectPath())
        if self.syspathCheckBox.isChecked():
            searchPaths.extend(sys.path)
        
        self.fileList.clear()
        locations = {}
        self.__shouldStop = False
        self.stopButton.setEnabled(True)
        QApplication.processEvents()
        
        for path in searchPaths:
            if os.path.isdir(path):
                files = direntries(path, True, fileNamePattern,
                                   False, self.checkStop)
                if files:
                    for file in files:
                        fp, fn = os.path.split(file)
                        if fn in locations:
                            if fp in locations[fn]:
                                continue
                            else:
                                locations[fn].append(fp)
                        else:
                            locations[fn] = [fp]
                        QTreeWidgetItem(self.fileList, [fn, fp])
                    QApplication.processEvents()
        
        del locations
        self.stopButton.setEnabled(False)
        self.fileList.sortItems(self.fileList.sortColumn(),
                                Qt.SortOrder.AscendingOrder)
        self.fileList.header().resizeSections(
            QHeaderView.ResizeMode.ResizeToContents)
        self.fileList.header().resizeSection(0, self.width() // 2)
        self.fileList.header().setStretchLastSection(True)
        
        self.findStatusLabel.setText(self.tr(
            "%n file(s) found", "", self.fileList.topLevelItemCount()))

    def checkStop(self):
        """
        Public method to check, if the search should be stopped.
        
        @return flag indicating the search should be stopped
        @rtype bool
        """
        QApplication.processEvents()
        return self.__shouldStop
    
    @pyqtSlot(str)
    def on_fileNameEdit_textChanged(self, text):
        """
        Private slot to handle the textChanged signal of the file name edit.
        
        @param text (ignored)
        @type str
        """
        self.findButton.setEnabled(bool(text))
    
    @pyqtSlot(str)
    def on_searchDirPicker_textChanged(self, text):
        """
        Private slot to handle the textChanged signal of the search directory
        edit.
        
        @param text text of the search dir edit
        @type str
        """
        self.searchDirCheckBox.setEnabled(text != "")
    
    @pyqtSlot(QTreeWidgetItem, int)
    def on_fileList_itemActivated(self, itm, column):
        """
        Private slot to handle the double click on a file item.
        
        It emits the signal sourceFile or designerFile depending on the
        file extension.
        
        @param itm the double clicked listview item
        @type QTreeWidgetItem
        @param column column that was double clicked (ignored)
        @type int
        """
        self.__openFile(itm)
    
    @pyqtSlot(QTreeWidgetItem, QTreeWidgetItem)
    def on_fileList_currentItemChanged(self, current, previous):
        """
        Private slot handling a change of the current item.
        
        @param current current item
        @type QTreeWidgetItem
        @param previous prevoius current item
        @type QTreeWidgetItem
        """
        self.openButton.setEnabled(current is not None)
    
    @pyqtSlot()
    def __projectOpened(self):
        """
        Private slot to handle a project being opened.
        """
        self.projectCheckBox.setEnabled(True)
        self.projectCheckBox.setChecked(True)
    
    @pyqtSlot()
    def __projectClosed(self):
        """
        Private slot to handle a project being closed.
        """
        self.projectCheckBox.setEnabled(False)
        self.projectCheckBox.setChecked(False)
    
    @pyqtSlot()
    def activate(self):
        """
        Public slot to enable/disable the project checkbox.
        """
        self.fileNameEdit.selectAll()
        self.fileNameEdit.setFocus()
