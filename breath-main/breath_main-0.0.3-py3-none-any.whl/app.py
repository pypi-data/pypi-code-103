import sys,sqlite3
from ui import UIToolTab
from home import HomeWindow
from login import Login, Register
from PyQt6.QtWidgets import (QLineEdit, QPushButton, QApplication, QMainWindow, QVBoxLayout, QDialog, QWidget)
from PyQt6.QtGui import QIcon
from user.db import *

class MainWindow(QMainWindow):

	def __init__(self, bd, parent=None):
		super(MainWindow, self).__init__(parent)
		self.setGeometry(0, 0, 1000, 1000)
		self.bd = bd

		self.startHomeWindow()

	def startUIToolTab(self):
		self.ToolTab = UIToolTab(self)
		self.setWindowTitle("UIToolTab")
		self.setCentralWidget(self.ToolTab)
		self.ToolTab.CPSBTN.clicked.connect(self.startHomeWindow)
		self.show()

	def startHomeWindow(self):
		self.Window = HomeWindow()
		self.setWindowTitle("Home")
		self.setCentralWidget(self.Window)
		self.Window.lgn_btn.clicked.connect(self.startLogin)
		self.Window.reg_btn.clicked.connect(self.startRegister)
		self.show()
	
	def startLogin(self):
		self.Window = Login(self)
		self.setWindowTitle("Login")
		self.setCentralWidget(self.Window)
		self.Window.bd = self.bd
		self.Window.reg_btn.clicked.connect(self.startRegister)
		self.Window.return_btn.clicked.connect(self.startHomeWindow)
		self.show()

	def startRegister(self):
		self.Window = Register(self)
		self.setWindowTitle("Register")
		self.setCentralWidget(self.Window)
		self.Window.bd = self.bd
		self.Window.return_btn.clicked.connect(self.startHomeWindow)
		self.show()


if __name__ == '__main__':
	bank = sqlite3.connect('data.db')
	bd = BD(bank)

	app = QApplication(sys.argv)
	w = MainWindow(bd)
	sys.exit(app.exec())