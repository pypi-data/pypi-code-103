# Copyright 2021, Jean-Benoist Leger <jb@leger.tf>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import re
import os
import sys

import xdg
import configobj

import flatlatex

from PyQt5.QtWidgets import (
    QApplication,
    QCheckBox,
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class ConfigAndConverter:
    def __init__(self):
        basedir = xdg.BaseDirectory.xdg_config_home + os.sep + "flatlatex-gui"
        if not os.path.isdir(basedir):
            os.mkdir(basedir)
        configfile = basedir + os.sep + "config.ini"
        self._configobj = configobj.ConfigObj(configfile)

        if "allow_zw" in self._configobj:
            self._allow_zw = self._configobj["allow_zw"] == "True"
        else:
            self._allow_zw = True
        if "allow_combinings" in self._configobj:
            self._allow_combinings = self._configobj["allow_combinings"] == "True"
        else:
            self._allow_combinings = True
        if "newcommands" in self._configobj:
            self._newcommands = tuple(self._configobj["newcommands"])
        else:
            self._newcommands = (r"% Insert \newcommand lines here.",)

        self._create_converter()

    @property
    def allow_zw(self):
        return self._allow_zw

    @property
    def allow_combinings(self):
        return self._allow_combinings

    @property
    def newcommands(self):
        return self._newcommands

    def _create_converter(self):
        newconverter = flatlatex.converter(
            allow_zw=self._allow_zw, allow_combinings=self._allow_combinings
        )
        for nc in self._newcommands:
            if not re.match(r"\s*%", nc):
                newconverter.add_newcommand(nc)
        self.converter = newconverter

    def update_newcommands(self, newcommands):
        old_newcommands = self._newcommands
        self._newcommands = newcommands
        try:
            self._create_converter()
        except flatlatex.conv.LatexSyntaxError:
            self._newcommands = old_newcommands
            return False
        self._configobj["newcommands"] = newcommands
        self._configobj.write()
        return True

    def update_params(self, allow_zw, allow_combinings):
        self._configobj["allow_zw"] = allow_zw
        self._configobj["allow_combinings"] = allow_combinings
        self._configobj.write()
        self._allow_zw = allow_zw
        self._allow_combinings = allow_combinings
        self.converter.allow_zw = allow_zw
        self.converter.allow_combinings = allow_combinings


class WidConfig(QWidget):
    def __init__(self, cc, reconvert, parent=None):
        super().__init__(parent)

        self._cc = cc
        self._reconvert = reconvert

        self._allowcombinings = QCheckBox("Allow combining chars")
        self._allowzw = QCheckBox("Allow zero width chars")
        self._newcommands = QTextEdit()
        self._newcommands.setMaximumHeight(105)
        self._btn_update = QPushButton("Update newcommands")
        self._btn_cancel = QPushButton("Cancel changes on newcommands")
        self._label_errornewcommand = QLabel("Syntax error, previous version restored")

        self._widbtn = QWidget()
        btnlayout = QHBoxLayout(self._widbtn)
        btnlayout.addWidget(self._btn_update)
        btnlayout.addWidget(self._btn_cancel)

        self._allowzw.setChecked(self._cc.allow_zw)
        self._allowcombinings.setChecked(self._cc.allow_combinings)
        self._newcommands.setText("\n".join(self._cc.newcommands))
        self._widbtn.setVisible(False)
        self._label_errornewcommand.setVisible(False)

        layout = QVBoxLayout(self)
        layout.addWidget(self._allowcombinings)
        layout.addWidget(self._allowzw)
        layout.addWidget(self._newcommands)
        layout.addWidget(self._widbtn)
        layout.addWidget(self._label_errornewcommand)

        self._allowcombinings.stateChanged.connect(self._params_update)
        self._allowzw.stateChanged.connect(self._params_update)
        self._newcommands.textChanged.connect(self._newcommands_changed)
        self._btn_update.clicked.connect(self._newcommands_update)
        self._btn_cancel.clicked.connect(self._newcommands_cancel)

    def _params_update(self):
        allow_zw = self._allowzw.isChecked()
        allow_combinings = self._allowcombinings.isChecked()
        self._cc.update_params(allow_zw, allow_combinings)
        self._reconvert()

    def _newcommands_changed(self):
        self._label_errornewcommand.setVisible(False)
        self._widbtn.setVisible(True)

    def _newcommands_cancel(self):
        self._newcommands.setText("\n".join(self._cc.newcommands))
        self._widbtn.setVisible(False)

    def _newcommands_update(self):
        newcommands = self._newcommands.toPlainText().split("\n")
        if not self._cc.update_newcommands(newcommands):
            self._newcommands.setText("\n".join(self._cc.newcommands))
            self._label_errornewcommand.setVisible(True)
        self._widbtn.setVisible(False)
        self._reconvert()


class WidMain(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self._cc = ConfigAndConverter()

        mainLayout = QVBoxLayout(self)
        mainLayout.setContentsMargins(5, 5, 5, 5)

        self._showconfig = QCheckBox("Show configuration")
        self._config = WidConfig(self._cc, self._reconvert)
        self._showconfig.setChecked(False)
        self._config.setVisible(False)
        self._showconfig.stateChanged.connect(self._show_config_toogle)

        labelLaTeX = QLabel("LaTeX: ")
        labelunicode = QLabel("Unicode: ")
        self._latexline = QLineEdit()
        self._unicodeline = QLineEdit()
        layoutlinelatex = QHBoxLayout()
        layoutlineunicode = QHBoxLayout()
        layoutlinelatex.addWidget(labelLaTeX)
        layoutlinelatex.addWidget(self._latexline)
        layoutlineunicode.addWidget(labelunicode)
        layoutlineunicode.addWidget(self._unicodeline)

        self._latexline.textChanged.connect(self._reconvert)
        self._unicodeline.setReadOnly(True)

        self._okbtn = QPushButton("Save unicode to clipboard and quit")
        self._okbtn.clicked.connect(self._clip_and_exit)
        self._okbtn.setAutoDefault(True)

        mainLayout.addWidget(self._showconfig)
        mainLayout.addWidget(self._config)
        mainLayout.addLayout(layoutlinelatex)
        mainLayout.addLayout(layoutlineunicode)
        mainLayout.addWidget(self._okbtn)
        self.setWindowTitle("FlatLatex GUI")
        self._set_initial_size()

        self._lastunicode = ""
        self._latexline.setFocus()

    def _reconvert(self):
        latex = self._latexline.text()
        try:
            output = self._cc.converter.convert(latex)
        except flatlatex.conv.LatexSyntaxError:
            self._unicodeline.setStyleSheet("background-color: rgb(255, 208, 208);")
            return
        self._lastunicode = output
        self._unicodeline.setText(output)
        self._unicodeline.setStyleSheet("")

    def _clipboard(self):
        if self._lastunicode:
            QApplication.clipboard().setText(self._lastunicode)

    def _clip_and_exit(self):
        self._clipboard()
        QApplication.quit()

    def _set_initial_size(self):
        self.setMinimumWidth(600)
        pass

    def _show_config_toogle(self):
        config = self._showconfig.isChecked()
        self._config.setVisible(config)
        if not config:
            self._set_initial_size()


def main():
    app = QApplication([])
    mwg = WidMain()
    mwg.show()
    app.exec_()

