import sys
from PyQt6.QtWidgets import (QLabel, QLineEdit, QPushButton, QApplication, QMainWindow, QVBoxLayout, QDialog, QWidget)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import (QRect, QCoreApplication, QMetaObject)

class HomeWindow(object):
	def __init__(self, bd, parent=None):
		super(HomeWindow, self).__init__(parent)
		# header
		self.setWindowTitle('BReATH')
		
	def setupUi(self, Form):
		Form.setObjectName("Form")
		Form.resize(541, 566)
		self.verticalLayoutWidget = QWidget(Form)
		self.verticalLayoutWidget.setGeometry(QRect(70, 40, 391, 441))
		self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
		self.verticalLayout = QVBoxLayout(self.verticalLayoutWidget)
		self.verticalLayout.setContentsMargins(0, 0, 0, 0)
		self.verticalLayout.setObjectName("verticalLayout")
		self.title = QLabel(self.verticalLayoutWidget)
		font = QFont()
		font.setPointSize(20)
		self.title.setFont(font)
		self.title.setObjectName("title")
		self.verticalLayout.addWidget(self.title)

		self.reg_text = self.createLabel(self.verticalLayout, self.verticalLayoutWidget, "lgn_text")
		self.lgn_btn = self.createPushBotton(self.verticalLayout, self.verticalLayoutWidget, "lgn_btn")
		self.reg_text = self.createLabel(self.verticalLayout, self.verticalLayoutWidget, "reg_text")
		self.reg_btn = self.createPushBotton(self.verticalLayout, self.verticalLayoutWidget, "reg_btn")

		self.retranslateUi(Form)
		QMetaObject.connectSlotsByName(Form)

	def createLabel(verticalLayout:QVBoxLayout, verticalLayoutWidget:QWidget, label:str) -> QLabel:
		label:QLabel = QLabel(verticalLayoutWidget)
		label.setObjectName(label)
		verticalLayout.addWidget(label)
		return label

	def createPushBotton(verticalLayout:QVBoxLayout, verticalLayoutWidget:QWidget, label:str) -> QPushButton:
		btn = QPushButton(verticalLayoutWidget)
		btn.setObjectName(label)
		verticalLayout.addWidget(btn)
		return btn

	def retranslateUi(self, Form):
		_translate = QCoreApplication.translate
		Form.setWindowTitle(_translate("Form", "Form"))
		self.title.setText(_translate("Form", "  Bem vindo ao Sistema Breath"))
		self.lgn_text.setText(_translate("Form", "    Por favor faça seu login para que possamos continuar"))
		self.lgn_btn.setText(_translate("Form", "Login"))
		self.reg_text.setText(_translate("Form", "       Ou faça seu registro caso seja seu primeiro acesso"))
		self.reg_btn.setText(_translate("Form", "Registro"))


class UIToolTab(QWidget):
	def __init__(self, parent=None):
		super(UIToolTab, self).__init__(parent)
		self.CPSBTN = QPushButton("text2", self)
		self.CPSBTN.move(100, 350)
