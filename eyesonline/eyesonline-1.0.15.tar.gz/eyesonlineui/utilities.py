from PyQt5 import QtGui,QtCore,QtWidgets
from .templates import ui_loginDialog , ui_joinDialog , ui_exptEntry, ui_exptEntryHeader
import numpy as np
import time, hashlib, requests, re, os, zipfile

class loginDialog(QtWidgets.QDialog, ui_loginDialog.Ui_Dialog):
	def __init__(self, parent,**kwargs):
		super(loginDialog, self).__init__(parent, QtCore.Qt.WindowStaysOnTopHint)
		self.setupUi(self)
		self.usernameBox.setText(kwargs.get('username',''))
		self.passwordBox.setText(kwargs.get('password',''))
		self.classroomBox.setText(kwargs.get('classroom',''))
		self.urlBox.setText(kwargs.get('url',''))
	def getUsername(self):
		return self.usernameBox.text()
	def getPassword(self):
		return self.passwordBox.text()
	def getClassroom(self):
		return self.classroomBox.text()
	def getUrl(self):
		return self.urlBox.text()

class joinDialog(QtWidgets.QDialog, ui_joinDialog.Ui_Dialog):
	def __init__(self, parent,**kwargs):
		super(joinDialog, self).__init__(parent, QtCore.Qt.WindowStaysOnTopHint)
		self.setupUi(self)
		self.classroomBox.setText(kwargs.get('classroom',''))
	def getClassroom(self):
		return self.classroomBox.text()


class exptEntry(QtWidgets.QWidget,ui_exptEntry.Ui_Form):
	def __init__(self,fname,intro, path, appdir,packagehash,callback, **kwargs):
		super(exptEntry, self).__init__()
		self.setupUi(self)
		self.fname  = fname
		self.appdir = appdir
		self.intro = intro
		self.path = path
		self.callback = callback
		self.packagehash = packagehash
		self.exptName.setText(fname)
		self.exptIntro.setText(intro)
		self.filetype = kwargs.get('filetype',None)
		
	def play(self):
		self.packagehash = self.callback(self.path,self.fname,self.packagehash,filetype = self.filetype)

class exptEntryHeader(QtWidgets.QWidget,ui_exptEntryHeader.Ui_Form):
	def __init__(self,pkgname, path, device):
		super(exptEntryHeader, self).__init__()
		self.setupUi(self)
		self.pkgname  = pkgname
		self.path = path
		self.device  = device
		self.exptName.setText(pkgname)
		self.exptPath.setText(path)
		self.exptDev.setText(device)


class eyes17dummy():
	version = 'dummy eyes17 time:date'
	connected = True
	def get_voltage(self,chan):
		return (np.random.random() - .5)*5
	def set_sqr1(self,val):
		return val
	def get_voltage_time(self,chan):
		return time.time(),(np.random.random() - .5)*5
	def set_state(self,**kwargs):
		pass
	def save(self,data,fname):
		print('dump to ',fname,data)
		
