import sys, hashlib
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtWidgets import (QLineEdit, QPushButton, QVBoxLayout, QDialog)
import pandas as pd
from user.db import *

class Login(QtWidgets.QDialog):
	def __init__(self, parent=None):
		super(Login, self).__init__(parent)
		self.login_input = QtWidgets.QLineEdit()
		self.password_input = QtWidgets.QLineEdit()
		self.login_label = QtWidgets.QLabel('Login')
		self.password_label = QtWidgets.QLabel('Password')
		self.return_btn = QtWidgets.QPushButton('Return')
		self.lgn_btn = QtWidgets.QPushButton('Login')
		self.reg_btn = QtWidgets.QPushButton('Register')
		self.success_msg = QtWidgets.QLabel()

		layout = QVBoxLayout()
		layout.addWidget(self.success_msg)
		layout.addWidget(self.login_label)
		layout.addWidget(self.login_input)
		layout.addWidget(self.password_label)
		layout.addWidget(self.password_input)
		layout.addWidget(self.lgn_btn)
		layout.addWidget(self.reg_btn)
		layout.addWidget(self.return_btn)

		# Set dialog layout
		self.setLayout(layout)

		self.lgn_btn.clicked.connect(self.login)

	def login(self):
		hashed_pswd = make_hashes(self.password_input.text())
		result = self.bd.login_user(self.login_input.text(), check_hashes(self.password_input.text(),hashed_pswd))
		if result:
			self.success_msg.setText('Logado com sucesso!')
			self.success_msg.setStyleSheet("color:green")
		else:
			self.success_msg.setText('nao encontramos esta credencial')
			self.success_msg.setStyleSheet("color:red")
		print(self.bd.view_all_users())



class Register(QDialog):
	def __init__(self, parent=None):
		super(Register, self).__init__(parent)

		# Create widgets
		self.account = QLineEdit("Account")
		self.password_input = QLineEdit("Password")
		self.confirm = QLineEdit("Repeat Password")
		self.reg_btn = QPushButton("Register")
		self.return_btn = QPushButton("Return")
		# Create layout and add widgets
		layout = QVBoxLayout()
		layout.addWidget(self.account)
		layout.addWidget(self.password_input)
		layout.addWidget(self.confirm)
		layout.addWidget(self.reg_btn)
		layout.addWidget(self.return_btn)
		# Set dialog layout
		self.setLayout(layout)
		# Add button signal to register slot
		self.reg_btn.clicked.connect(self.register)

	# Greets the user
	def register(self):
		self.bd.add_userdata(self.account.text(),make_hashes(self.password_input.text()))
		print(self.bd.view_all_users())
		print("Você está logado")