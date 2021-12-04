# -*- coding: utf-8 -*-

# Copyright (c) 2012 - 2021 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a main window class with styling support.
"""

from PyQt6.QtCore import QCoreApplication
from PyQt6.QtWidgets import QMainWindow, QStyleFactory, QApplication

from .EricApplication import ericApp
from . import EricMessageBox


class EricMainWindow(QMainWindow):
    """
    Class implementing a main window with styling support.
    """
    def __init__(self, parent=None):
        """
        Constructor
        
        @param parent reference to the parent widget (QWidget)
        """
        super().__init__(parent)
        
        self.defaultStyleName = QApplication.style().objectName()
    
    def setStyle(self, styleName, styleSheetFile):
        """
        Public method to set the style of the interface.
        
        @param styleName name of the style to set (string)
        @param styleSheetFile name of a style sheet file to read to overwrite
            defaults of the given style (string)
        """
        # step 1: set the style
        style = None
        if styleName != "System" and styleName in QStyleFactory.keys():
            # __IGNORE_WARNING_Y118__
            style = QStyleFactory.create(styleName)
        if style is None:
            style = QStyleFactory.create(self.defaultStyleName)
        if style is not None:
            QApplication.setStyle(style)
        
        # step 2: set a style sheet
        if styleSheetFile:
            try:
                with open(styleSheetFile, "r", encoding="utf-8") as f:
                    styleSheet = f.read()
            except OSError as msg:
                EricMessageBox.warning(
                    self,
                    QCoreApplication.translate(
                        "EricMainWindow", "Loading Style Sheet"),
                    QCoreApplication.translate(
                        "EricMainWindow",
                        """<p>The Qt Style Sheet file <b>{0}</b> could"""
                        """ not be read.<br>Reason: {1}</p>""")
                    .format(styleSheetFile, str(msg)))
                return
        else:
            styleSheet = ""
        
        ericApp().setStyleSheet(styleSheet)
