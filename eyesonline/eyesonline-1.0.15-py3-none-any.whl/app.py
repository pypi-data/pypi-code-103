from PyQt5 import QtGui,QtCore,QtWidgets
from PyQt5.QtWebChannel import QWebChannel

import os,string,time,sys,base64,hashlib,re,zipfile
from .templates import ui_layout3 as layout
from . import utilities
from .socketcontroller import socketController
from scipy.interpolate import interp1d
from flask import json

import pyqtgraph as pg
import numpy as np


from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage
from PyQt5 import QtWebEngineWidgets

import importlib,requests,os

class webPage(QWebEnginePage):
	def __init__(self, *args, **kwargs):
		super(webPage, self).__init__()
		self.featurePermissionRequested.connect(self.onFeaturePermissionRequested)
	def javaScriptConsoleMessage(self,level, msg, line, source):
		print (' \033[4;33m line %d: %s !! %s , %s \033[0m' % ( line, msg, source,level))

	def onFeaturePermissionRequested(self, url, feature):
		print('feature requested',feature)
		if feature in (QWebEnginePage.MediaAudioCapture, 
			QWebEnginePage.MediaVideoCapture, 
			QWebEnginePage.MediaAudioVideoCapture,
			QWebEnginePage.DesktopVideoCapture,
			QWebEnginePage.DesktopAudioVideoCapture):
			self.setFeaturePermission(url, feature, QWebEnginePage.PermissionGrantedByUser)
		else:
			self.setFeaturePermission(url, feature, QWebEnginePage.PermissionDeniedByUser)


	def certificateError(self, certificateError):
		certificateError.isOverridable()
		certificateError.ignoreCertificateError()
		return True

class helpWin(QWebEngineView):
	def __init__(self, parent):
		super(helpWin, self).__init__()
		self.parent=parent
		self.mypage = webPage(self)
		self.setPage(self.mypage)

	def loadPage(self,url):
		print('loading page...',url)
		self.setUrl(QtCore.QUrl(url))
		self.show()




class AppWindow(QtWidgets.QMainWindow, layout.Ui_MainWindow):
	initSocket = QtCore.pyqtSignal(object,object)
	getScreenshot = QtCore.pyqtSignal(object)
	remoteAccessSignal = QtCore.pyqtSignal(object)
	roomStatusSignal = QtCore.pyqtSignal(object,object)


	def __init__(self, app,**kwargs):
		super(AppWindow, self).__init__(None)
		self.setupUi(self)
		self.remote = kwargs.get('remote',False)

		self.p = None
		self.roomStatusSignal.connect(self.join_room_callback)
		

		self.statusBar = self.statusBar()
		self.chatbox = QtWidgets.QLineEdit(self)
		self.chatbox.setStyleSheet('max-width:200px')
		self.chatbox.setPlaceholderText('chat with admin...')
		self.chatbox.returnPressed.connect(self.sendChatMessage)
		self.statusBar.addPermanentWidget(self.chatbox)

		self.lastTransmittedData = {}
		self.autotransmit = True
		self.autographtransmit = False #Linked to the graph onchange event
		
		## Local Scripts directory for remotely downloaded content
		localstorage = '.expeyesapps'
		homedir = os.path.expanduser('~')
		self.appdir = os.path.join(homedir,localstorage)
		if not os.path.isdir(self.appdir):
			os.makedirs(self.appdir)
		self.newcode =None #New experiment widget. loaded remotely
		self.availableScripts = {}
		self.availableExperiments = {}
		self.loggedIn = False
		self.pname = None

		try:
			with open(os.path.join(self.appdir,'scripts.json'), 'r', encoding='utf-8') as f:
				scripts = json.load(f)
				self.refreshScriptList(scripts)
		except Exception as e:
			print('no scripts found',e)

		if 'remote' in sys.argv or self.remote:
			self.url = 'https://expeyes.scischool.in'
		else:
			self.url = 'https://mypc.in'

		if 'autologin' in sys.argv: QtCore.QTimer.singleShot(0, self.loginScreen ) #Launch the login screen

		self.socklib = socketController(self)

		self.setTheme('aqua')
		self.setupBrowser()

	def showLoginScreen(self):
		QtCore.QTimer.singleShot(0, self.loginScreen ) #Launch the login screen

	def showJoinRoom(self):
		QtCore.QTimer.singleShot(0, self.joinRoomScreen ) #Launch the room joining dialog
	def showLeaveRoom(self):
		QtCore.QTimer.singleShot(0, self.leaveRoomScreen ) #Launch the room leaving dialog

	def refreshScriptList(self,scripts):
		self.availableScripts.update(scripts)
		for a in self.availableExperiments:
			self.availableExperiments[a].setParent(None)
		self.availableExperiments = {}
		#import json
		with open(os.path.join(self.appdir,'scripts.json'), 'w', encoding='utf-8') as f:
			json.dump(scripts, f, ensure_ascii=False, indent=4)
		
		for packagename in scripts:
			pkg = scripts[packagename]
			modname = re.split(r'[\\,/]',pkg['path'])[-1]
			e = utilities.exptEntryHeader(modname,os.path.join(self.appdir,modname),pkg.get('filetype',''))
			self.availableExperiments[modname] = e
			self.experimentListLayout.addWidget(e)

			for expt in pkg['data']:
				e = utilities.exptEntry(expt['Filename'],expt['Intro'],pkg['path'],self.appdir,pkg['hash'],self.downloadAndExecuteExperiment, filetype = pkg.get('filetype',None))
				self.experimentListLayout.addWidget(e)
				self.availableExperiments[expt['Filename']] = e
		

	def loginScreen(self):
		self.room = 'd'
		if len(sys.argv)>1:
			testname = sys.argv[1];	self.name = testname; self.pwd = testname
		else:
			self.name = ''; self.pwd = ''

		self.loginDialog = utilities.loginDialog(self,username = self.name, password = self.pwd,classroom = self.room,url = self.url)

		if 'skip' not in sys.argv: #Command line skipping of the login screen . auto-login. for testing
			retval = self.loginDialog.exec_()
			if not retval:
				return

		try:	# 167.71.230.181 expeyes.scischool.in
			self.name = self.loginDialog.getUsername()
			self.pwd = self.loginDialog.getPassword()
			self.room = self.loginDialog.getClassroom()
			self.url = self.loginDialog.getUrl()
			
			if not self.loggedIn:
				self.socklib.connect(self.url,{'name':self.name,'password':self.pwd,'remember':'true'},remote = (self.remote or 'remote' in sys.argv))
				'''
				if 'remote' in sys.argv or self.remote:
					self.socklib.connect(self.url,{'name':self.name,'password':self.pwd,'remember':'true'})
				else:
					self.socklib.connect(self.url+':8080',{'name':self.name,'password':self.pwd,'remember':'true'}) #HTTPS doesn't work with self signed cert in local dev env
				'''
			scripts = self.socklib.getScriptList(self.url)
			self.refreshScriptList(scripts)
			print('scripts refreshed')

			self.socklib.joinRoom(self.room,self.roomStatusSignal.emit)
			self.loggedIn = True

			##HANDLERS for remote events
			self.socklib.addHandler('get screenshot',self.getScreenshot.emit)
			self.socklib.addHandler('message',self.interpretMessage)
			self.socklib.addHandler('iot',self.setWidgetValue)
			self.remoteAccessSignal.connect(self.socklib.executeRemoteCallback)#self.remoteAccessCallbacks)
			self.getScreenshot.connect(self.screenshot)
			if self.pname:
				self.socklib.transmitWidgets(layoutname=self.pname)			

		except Exception as e:
			self.loggedIn = False
			print('Login Error',e)
			self.statusBar.showMessage('connect failed:'+str(e),3000)

	def joinRoomScreen(self):
		self.room = 'd'
		self.joinRoomDialog = utilities.joinDialog(self,classroom = self.room)
		
		retval = self.joinRoomDialog.exec_()
		if not retval:
			return
		self.room = self.joinRoomDialog.getClassroom()
		self.socklib.joinRoom(self.room,self.roomStatusSignal.emit)


	def join_room_callback(self,room,args):
		print(args)
		if 'status' in  args:
			if args['status'] == 'false':
				QtWidgets.QMessageBox.warning(self,'Connection error!', args['message'])
				self.statusBar.showMessage(args['message'],3000)
			elif args['status'] == 'true':
				QtWidgets.QMessageBox.information(self, 'Success', args['message'])
				self.statusBar.showMessage(args['message'],3000)
				self.socklib.activeroom = room
				self.room=room
				self.setWindowTitle('CSpark Remote Labs: %s | %s'%(self.name,self.room))
		else:
			QtWidgets.QMessageBox.warning(self, 'Server Error','Failed to join/leave classroom. Is https://expeyes.scischool.in active?')
			self.statusBar.showMessage('Failed to join/leave classroom',3000)

	def leaveRoomScreen(self):
		self.socklib.leaveRoom(self.room,self.roomStatusSignal.emit)



	def setupBrowser(self):
		## HELP
		self.hwin = helpWin(self)
		self.webLayout.addWidget(self.hwin)
		
		try:
			from PyQt5.QtWebChannel import QWebChannel
			self.channel = QWebChannel()
			self.webhandler = self.rtcHandler(self.socklib,self.url,self.appdir)
			self.channel.registerObject('handler', self.webhandler)
			self.hwin.page().setWebChannel(self.channel)

			self.webhandler.importLibrarySignal.connect(self._downloadAndExecuteExperiment)
			self.webhandler.iotSignal.connect(self.setWidgetValue)
			
			print('main thread is: ',int(QtCore.QThread.currentThreadId()) )
			print('web channel established')
		except Exception as e:
			print('what!',e)
		self.hwin.loadPage(self.url+"/scripts")

		self.statustimer = QtCore.QTimer()
		self.statustimer.timeout.connect(self.sendStatus)
		self.statustimer.start(30)


	##############################
	def setTheme(self,theme):
		self.setStyleSheet("")
		self.setStyleSheet(open(os.path.join(os.path.dirname(os.path.realpath(__file__)),'themes',theme+".qss"), "r").read())

	def setAutoGraph(self,state):
		self.autographtransmit = state

	def _downloadAndExecuteExperiment(self,path,fname,packagehash,filetype):
		self.downloadAndExecuteExperiment(path,fname,packagehash,filetype = filetype)

	def downloadAndExecuteExperiment(self,path,fname,packagehash,**kwargs):
		self.autotransmit = False
		modname = re.split(r'[\\,/]',path)[-1]
		modzip = modname+'.zip'
		modpath = os.path.join(self.appdir,modzip)
		self.statusBar.showMessage('Checking if lastest package exists: '+modpath,200)
		try:
			ziphash = hashlib.md5(open(modpath,"rb").read()).hexdigest()
			if (packagehash == ziphash):
				self.statusBar.showMessage('Module found:'+ ' Launch : '+fname,2000)
				self.loadExperiment(fname,os.path.join(self.appdir,modname),**kwargs)
				return packagehash
			else:
				self.statusBar.showMessage('Module has changed. Downloading... ' + packagehash)

		except IOError:
			self.statusBar.showMessage('module not found. Download... '+modname)

		#This is a good place to check if we already have the file or not. add versioning.
		r = requests.get(self.url+'/'+path+'.zip',verify=False) 
		if r.status_code == 200:
			with open(modpath, 'wb') as f:
				f.write(r.content)
			with zipfile.ZipFile(modpath, 'r') as zip_ref:
				zip_ref.extractall(self.appdir)
			
			self.loadExperiment(fname,os.path.join(self.appdir,modname) , **kwargs )
			self.statusBar.showMessage('Launched experiment : '+fname,2000)
		else:
			self.statusBar.showMessage('file not found: '+	self.url+'/'+path+'/'+fname )

		return hashlib.md5(open(modpath,"rb").read()).hexdigest()

	def _loadExperiment(self,fname,path,filetype):
		self.loadExperiment(fname,path, filetype = filetype)

	def loadExperiment(self,fname,path,**kwargs):
		if self.loggedIn:
			try:
				self.socklib.disconnectGraphConnections()
			except:
				pass

		import sys,importlib
		sys.path.append(path)
		with open(os.path.join(path,fname)) as f:
			self.codeBrowser.document().setPlainText(f.read())
		f.close()


		if self.newcode:
			self.newcode.setParent(None)
			self.newcode.deleteLater()
			time.sleep(0.5)
			self.newcode = None
		
		filetype = kwargs.get('filetype',None)
		
		if filetype == 'eyes17':
			if not self.p:
				## Connect to device
				try:
					import eyes17.eyes
					self.p = eyes17.eyes.open()
				except Exception as e:
					print('getting device failed. not connected?',e)
					self.p = utilities.eyes17dummy()

			self.pname = fname.split('.')[0] #Get rid of the .py extension
			mylib = importlib.import_module(self.pname)
			self.newcode = mylib.Expt(self.p)

			self.exptLayout.addWidget(self.newcode)
			self.myTabs.setCurrentWidget(self.remoteExptTab)
			self.prepareRemoteMonitorWidgetList(self.remoteExptTab)
			if self.loggedIn:
				self.socklib.set_device_id(self.p.version)
				self.socklib.transmitWidgets(layoutname=self.pname)
				self.statustimer.stop()				
				self.statustimer.start(300) 
			
			self.autotransmit = True

		elif filetype == 'kuttypy':
			if self.p:
				try:
					self.p.close()()
				except Exception as e:
					print('Failed to close',e)

			self.pname = fname.split('.')[0] #Get rid of the .py extension
			mylib = importlib.import_module(self.pname)
			self.newcode = mylib.runWindowed()

			self.exptLayout.addWidget(self.newcode)
			self.myTabs.setCurrentWidget(self.remoteExptTab)
			self.prepareRemoteMonitorWidgetList(self.remoteExptTab)
			if self.loggedIn:
				self.socklib.set_device_id(self.newcode.VERSION)
				#print(self.pname,self.socklib.monitorWidgets)
				self.socklib.transmitWidgets(layoutname=self.pname)

				self.statustimer.stop()				
				self.statustimer.start(300) 
			self.autotransmit = True



		elif filetype == 'editor':
			self.pname = fname.split('.')[0] #Get rid of the .py extension
			mylib = importlib.import_module(self.pname)
			self.newcode = mylib.AppWindow()
			self.exptLayout.addWidget(self.newcode)
			self.myTabs.setCurrentWidget(self.remoteExptTab)
			self.prepareRemoteMonitorWidgetList(self.remoteExptTab)
			self.socklib.addMonitor(self.newcode.ipyConsole.kernel_client.iopub_channel)
			if self.loggedIn:
				print ('sending',self.pname)
				self.socklib.transmitWidgets(layoutname = self.pname)
				self.statustimer.stop()				
				self.statustimer.start(1000) #Slow timer for text editor mode. Until such a time as diff can be implemented.
			
			self.autotransmit = True

		elif filetype == 'runscript':
			self.pname = fname.split('.')[0] #Get rid of the .py extension
			mylib = importlib.import_module(self.pname)
			self.myTabs.setCurrentWidget(self.codeTab)
			self.prepareRemoteMonitorWidgetList(self.codeTab)
			if self.loggedIn:
				self.socklib.transmitWidgets(layoutname='runscript')#self.pname)
				self.statustimer.stop()				
				self.statustimer.start(1000) #Slow timer for text editor mode. Until such a time as diff can be implemented.
			
			self.autotransmit = True


		else:
			self.statusBar.showMessage('Script type unsupported',1000)
			return


	def prepareRemoteMonitorWidgetList(self,location):
		self.socklib.clearMonitors()
		self.socklib.addMonitors(location.findChildren((QtWidgets.QCheckBox,QtWidgets.QPushButton,QtWidgets.QSlider,QtWidgets.QLabel,pg.PlotWidget,QtWidgets.QStackedWidget,QtWidgets.QComboBox,QtWidgets.QTextBrowser,QtWidgets.QPlainTextEdit)),remote=True)
		#self.socklib.addMonitorSpacer('spacer1')

	class rtcHandler(QtCore.QObject):
		peer_id = None
		iceCandidate = QtCore.pyqtSignal(int,str)
		sessionDescription = QtCore.pyqtSignal(str,str)
		makeVideoCall = QtCore.pyqtSignal(bool,bool)
		getInfo = QtCore.pyqtSignal()
		importLibrarySignal = QtCore.pyqtSignal(str,str,str,str)
		sendDataSignal = QtCore.pyqtSignal(str)
		iotSignal = QtCore.pyqtSignal(object)
		def __init__(self,socklib,url,localdir):
			super(AppWindow.rtcHandler,self).__init__()
			print('rtc thread is: ',int(QtCore.QThread.currentThreadId()) )
			self.socklib = socklib
			self.socklib.addHandler('sessionDescription',self.gotSessionDescription)
			self.socklib.addHandler('iceCandidate',self.gotIceCandidate)
			self.socklib.addHandler('init video exchange',self.beginCall)

			self.url = url
			self.appdir = localdir
			self.dataChannel = False
			self.dataChannelFull = False

		@QtCore.pyqtSlot(str,str,str,str)
		def fetchFile(self,path,fname,packagehash,filetype):
				self.importLibrarySignal.emit(path,fname,packagehash,filetype )


		@QtCore.pyqtSlot(str)
		def printInfo(self,info):
			print('INFO: ',info)

		@QtCore.pyqtSlot(str)
		def gotRemoteData(self,info):
			self.iotSignal.emit(json.loads(info))

		@QtCore.pyqtSlot(int,str)
		def relayICECandidate(self,sdpMLineIndex,candidate):
			print('ICE',sdpMLineIndex,candidate)
			self.socklib.sio.emit('relayICECandidate',{'peer_id':self.peer_id,'ice_candidate':{'sdpMLineIndex':sdpMLineIndex,'candidate':candidate} },namespace='/classroom')

		@QtCore.pyqtSlot(str,str)
		def relaySessionDescription(self,tp,sdp):
			print('relaying session description...',tp,sdp[:10])
			self.socklib.sio.emit('relaySessionDescription',{'peer_id':self.peer_id,'session_description':{'type':tp,'sdp':sdp} },namespace='/classroom')

		@QtCore.pyqtSlot()
		def callTeacher(self):
			print('Calling the teacher')
			self.socklib.sio.emit('call the teacher',{ },namespace='/classroom')

		def beginCall(self,config):
			print('begin video call', config)
			self.peer_id = config['peer_id']
			self.makeVideoCall.emit(config['should_create_offer'],config.get('p2pdata',False))
		
		def gotSessionDescription(self,config):
			print('got session description from',config['peer_id'])
			self.sessionDescription.emit(config['session_description']['type'],config['session_description']['sdp'])

		def gotIceCandidate(self,config):
			print('got ice candidate from',config['peer_id'])
			self.iceCandidate.emit(config['ice_candidate']['sdpMLineIndex'],config['ice_candidate']['candidate'])

		#Data Channel
		@QtCore.pyqtSlot(bool)
		def configureDataChannel(self,state):
			self.dataChannel = state
			print('Data channel update..: ',state)

		@QtCore.pyqtSlot(bool)
		def dataChannelBufferFull(self,state):
			self.dataChannelFull = state
			#print('Data channel buffer full state..: ',state)

		def sendData(self,data):
			if self.dataChannel:
				if not self.dataChannelFull:
					self.sendDataSignal.emit(data)
					return True
				elif 'iot' in data: #IOT data is simply streaming the latest state. can be skipped if data buffer is running full
					return True
			return False

	def setWidgetValue(self,data):
		if('closeapp' in data): #TODO remove
			self.connected = False
			self.loggedIn = False
			self.closeEvent(None)#QtWidgets.qApp.quit()
			return
		self.remoteAccessSignal.emit(data)

	'''
	def remoteAccessCallbacks(self,data):
		self.socklib.executeRemoteCallback(data)
	'''
	def closeEvent(self, evnt):
		global app
		try:
			evnt.ignore()
		except:
			pass

		try:
			self.socklib.sio.emit('leave',{'room':self.room},namespace='/classroom')
			time.sleep(0.5)
			self.socklib.sio.disconnect()
		except Exception as e:
			print(e)
		print('goodbye')
		app.exit()

	def interpretMessage(self,data):
		if 'chatmsg' in data:
			self.statusBar.showMessage('Admin: ' + data.get('chatmsg'))			
		elif 'autotransmit' in data:
			self.autotransmit = data.get('autotransmit')
		elif 'autographtransmit' in data:
			self.autographtransmit = data.get('autographtransmit')
		elif 'fetchall' in data:
			self.sendStatus()
		elif 'modify widget list' in data:
			remoteList = data['modify widget list']
			self.loggedIn = False ; time.sleep(0.5)
			for widget in self.socklib.monitorWidgets.keys():
				if widget in remoteList:
					self.socklib.monitorWidgets[widget].active = True
				else:
					self.socklib.monitorWidgets[widget].active = False

			print('Got modified widget list from Remote',remoteList, ' PREVIOUS:',self.socklib.monitorWidgets.keys(), ' Now:',self.socklib.prepareWidgetList(True).keys())
			self.loggedIn = True
		elif 'set monitor state' in data:
			if data['widget'] in self.socklib.monitorWidgets:
				self.socklib.monitorWidgets[data['widget']].active = data['set monitor state']
				print('Widget state changed :',data['widget'],data['set monitor state'])

	def sendChatMessage(self):
		text = self.chatbox.displayText()
		self.socklib.sendInformation({'chatmsg':text})
		self.chatbox.setText('')

	def sendStatus(self):
		if (not self.loggedIn) or (not self.autotransmit):
			return
		v = self.socklib.getWidgetValues()
		data = {}
		if v!= self.lastTransmittedData:
			for a in v: #Iterate through new dataset
				if a in self.lastTransmittedData: #This widget is in the old dataset
					if self.lastTransmittedData[a] == v[a]: #This widget has not changed
						continue
				data[a] = v[a] #Copy the key value pair. It either did not exist, or is unchanged.	
				self.lastTransmittedData[a] = v[a] #Update the last transmitted information

		if not self.webhandler.sendData(json.dumps(data)): 
			self.socklib.transmitWidgetValues(data)   ##Failed to send data via datachannel (Channel closed) , so use regular channel
			self.statustimer.stop()				
			self.statustimer.start(300) #Slow timer for relay through server mode
		else: #Data sent successfully
			self.statustimer.stop()				
			self.statustimer.start(300) #Speed up data rate for P2P

	
	def screenshot(self,args):
		path='tmp.png'#, _filter  = QtWidgets.QFileDialog.getSaveFileName(self, 'Save File', '~/')
		t= time.time()
		#screen = QtWidgets.QApplication.primaryScreen()
		#screenshot = screen.grabWindow( self.winId() )
		#screenshot.save(path)

		pix = QtGui.QPixmap(self.remoteExptTab.size())
		self.remoteExptTab.render(pix)
		pixs = pix.scaledToWidth(int(args.get('width',800)), mode=QtCore.Qt.FastTransformation)
		pixs.save(path)

		#pix=widget.grab()
		#pix.save("save.png")


		with open(path, "rb") as img_file:
		    imgstr = base64.b64encode(img_file.read())
		print('transmitting screenshot')
		self.socklib.sendInformation({'screenshot':"data:image/png;base64,"+imgstr.decode('utf-8')})

	def rawscreenshot(self,args):
		path='tmp.png'#, _filter  = QtWidgets.QFileDialog.getSaveFileName(self, 'Save File', '~/')
		t= time.time()
		screen = QtWidgets.QApplication.primaryScreen()
		screenshot = screen.grabWindow( self.winId() )
		screenshot.save(path)

		with open(path, "rb") as img_file:
		    imgstr = base64.b64encode(img_file.read())
		print('transmitting screenshot')
		self.socklib.sendInformation({'screenshot':"data:image/png;base64,"+imgstr.decode('utf-8')})




def run():
	global app
	print('QT Version',QtCore.__file__)
	app = QtWidgets.QApplication(sys.argv)
	myapp = AppWindow(app)
	myapp.show()
	sys.exit(app.exec_())

def runonline():
	global app
	print('QT Version',QtCore.__file__)
	app = QtWidgets.QApplication(sys.argv)
	myapp = AppWindow(app,remote=True)
	myapp.show()
	sys.exit(app.exec_())


if __name__ == "__main__":
	run()
