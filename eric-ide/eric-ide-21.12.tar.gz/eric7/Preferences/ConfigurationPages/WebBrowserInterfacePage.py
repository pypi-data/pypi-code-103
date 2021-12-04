# -*- coding: utf-8 -*-

# Copyright (c) 2006 - 2019 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing the Interface configuration page (variant for web browser).
"""

from PyQt6.QtWidgets import QStyleFactory

from EricWidgets.EricPathPicker import EricPathPickerModes

from .ConfigurationPageBase import ConfigurationPageBase
from .Ui_WebBrowserInterfacePage import Ui_WebBrowserInterfacePage

import Preferences


class WebBrowserInterfacePage(ConfigurationPageBase,
                              Ui_WebBrowserInterfacePage):
    """
    Class implementing the Interface configuration page (variant for web
    browser).
    """
    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        self.setupUi(self)
        self.setObjectName("InterfacePage")
        
        self.styleSheetPicker.setMode(EricPathPickerModes.OPEN_FILE_MODE)
        self.styleSheetPicker.setFilters(self.tr(
            "Qt Style Sheets (*.qss);;Cascading Style Sheets (*.css);;"
            "All files (*)"))
        
        # set initial values
        self.__populateStyleCombo()
        self.styleSheetPicker.setText(Preferences.getUI("StyleSheet"))
    
    def save(self):
        """
        Public slot to save the Interface configuration.
        """
        # save the style settings
        styleIndex = self.styleComboBox.currentIndex()
        style = self.styleComboBox.itemData(styleIndex)
        Preferences.setUI("Style", style)
        Preferences.setUI(
            "StyleSheet",
            self.styleSheetPicker.text())
    
    def __populateStyleCombo(self):
        """
        Private method to populate the style combo box.
        """
        curStyle = Preferences.getUI("Style")
        styles = sorted(QStyleFactory.keys())
        self.styleComboBox.addItem(self.tr('System'), "System")
        for style in styles:
            self.styleComboBox.addItem(style, style)
        currentIndex = self.styleComboBox.findData(curStyle)
        if currentIndex == -1:
            currentIndex = 0
        self.styleComboBox.setCurrentIndex(currentIndex)
    

def create(dlg):
    """
    Module function to create the configuration page.
    
    @param dlg reference to the configuration dialog
    @return reference to the instantiated page (ConfigurationPageBase)
    """
    page = WebBrowserInterfacePage()
    return page
