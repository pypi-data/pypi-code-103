from flask import json
from PyQt5 import QtWidgets
from collections import OrderedDict
import socketio,requests,functools

class remoteWidget():
	def __init__(self,name, params, setValue = None, callback = None):
		self.objectName = name
		self.widgetType = params['widget']
		self.params = params
		self.callback = callback
		self.setValue = setValue
		self.active = True
		self.params.update({'active':self.active})

	def updateParams(self,params):
		self.params = params
		self.params.update({'active':self.active})

class socketController():
	sio = socketio.Client()
	monitorWidgets=OrderedDict()
	parent = None
	activeroom = None
	autotransmit = False
	graphWidgetValues = {}
	graphConnections = [] #Signals to autoupdate graphs
	
	def __init__(self, parent):
		self.url = ''
		self.socketurl = ''
		self.parent  = parent
	
	def prepareWidgetList(self, cleanup = False):
		if cleanup:
			return {a:self.monitorWidgets[a].params for a in self.monitorWidgets if self.monitorWidgets[a].active }
		else:
			return {a:self.monitorWidgets[a].params for a in self.monitorWidgets }

	def connect(self,homeurl, creds,**kwargs):
		self.url = homeurl
		if kwargs.get('remote'): self.socketurl = self.url.replace('https','https')
		else: self.socketurl = self.url.replace('https','http')+':8000'
		print('connecting to %s and sockets at %s'%(self.url, self.socketurl))
		session = requests.session()
		#creds.update({'myname':'j'})
		r = session.post(homeurl+'/login', creds, verify=False) #,headers={'User-Agent': 'Chrome'}
		if r.status_code == 200:
			token = 'remember_token='
			token += session.cookies['remember_token']
			token += '; session='
			token += session.cookies.get('session',domain = self.url.replace('https://',''))
			self.sio.connect(self.socketurl,headers={'Cookie': token}, namespaces=['/classroom'])
			print('connected to socket',self.socketurl)
			return self.sio
		else:
			print('invalid status code returned on login',r.status_code)

		return None

	def addHandler(self,event,function):
		self.sio.on(event, function, namespace='/classroom')

	def joinRoom(self,room,callback,**kwargs):
		data = {'room':room}
		data['widgets'] = self.prepareWidgetList()
		data.update(kwargs)
		self.sio.emit('join',data,namespace='/classroom',callback = functools.partial(callback,room) )

	def leaveRoom(self,room,callback,**kwargs):
		data = {'room':room}
		data['widgets'] = self.prepareWidgetList()
		data.update(kwargs)
		self.sio.emit('leave',data,namespace='/classroom',callback = functools.partial(callback,None) )


	def transmitWidgets(self,**kwargs):
		if not self.activeroom:return

		data = {'room':self.activeroom}
		data['widgets'] = self.prepareWidgetList() # add boolean True to enable cleanup. Only send active widgets.
		data.update(kwargs)
		self.sio.emit('widget list',data,namespace='/classroom')


	def set_device_id(self,devID):
		'''
		this will set the device ID(versio) in the database
		'''
		self.sio.emit('set device id',{'id':devID},namespace='/classroom')

	def sendInformation(self,info):
		'''
		this will be relayed to the owners of all the rooms this user is in
		'''
		self.sio.emit('chatter',info,namespace='/classroom')


	def addMonitors(self,widgets,**kwargs):
		'''
		Widgets which the teacher can monitor in real time
		'''
		for a in widgets:
			self.addMonitor(a,**kwargs)

	def setLabelText(self,label,data):
		label.setText(data['value'])
	def setCbxState(self,cbx,data):
		cbx.setChecked(data['value'])
	def setSliderValue(self,sldr,data):
		sldr.setValue(int(data['value']))
	def setComboState(self,combo,data):
		combo.setCurrentIndex(int(data['value']))
	def animateButtonClick(self,btn,data): #data param ignored for consistency
		btn.animateClick()
	def setDioState(self,dio,data):
		dio.setState(data['value'])

	def addMonitor(self,a,**kwargs):
		'''
		Widgets which the teacher can monitor in real time
		'''
		if (len(a.objectName())==0 ):
			return
		
		if isinstance(a,QtWidgets.QLabel):
			self.monitorWidgets[a.objectName()]=remoteWidget(a.objectName(), {'widget':'label','text':a.text()}, functools.partial(self.setLabelText,a))

		elif isinstance(a,QtWidgets.QCheckBox):
			self.monitorWidgets[a.objectName()]=remoteWidget(a.objectName(), {'widget':'checkbox','text':a.text()}, functools.partial(self.setCbxState,a) )

		elif isinstance(a,QtWidgets.QSlider):
			self.monitorWidgets[a.objectName()]=remoteWidget(a.objectName(), {'widget':'slider','value':a.value(),'min':a.minimum(),'max':a.maximum()} , functools.partial(self.setSliderValue,a) )

		elif isinstance(a,QtWidgets.QComboBox):
			self.monitorWidgets[a.objectName()]=remoteWidget(a.objectName(),{'widget':'combobox','value':[a.itemText(i) for i in range(a.count())]} , functools.partial(self.setComboState,a) )


		elif isinstance(a,QtWidgets.QPushButton):
			self.monitorWidgets[a.objectName()]=remoteWidget(a.objectName(),{'widget':'button','text':str(a.text())} , functools.partial(self.animateButtonClick,a) )

		elif isinstance(a,QtWidgets.QTextBrowser):
			self.monitorWidgets[a.objectName()]=remoteWidget(a.objectName(),{'widget':'textbrowser','text':str(a.toPlainText())} )

		elif isinstance(a,QtWidgets.QPlainTextEdit):
			self.monitorWidgets[a.objectName()]=remoteWidget(a.objectName(),{'widget':'textedit','text':str(a.toPlainText())} )

		elif 'PlotWidget' in str(a.__class__):
			self.monitorWidgets[a.objectName()]=remoteWidget(a.objectName(),{'widget':'graph','xlabel':a.plotItem.getAxis('bottom').labelText,'ylabel':a.plotItem.getAxis('left').labelText} )
			for b in a.plotItem.listDataItems():
				b.sigPlotChanged.connect(functools.partial(self.updatePlot,a.objectName(),b))
				self.graphConnections.append(b)
		elif 'QtInProcessChannel' in str(a.__class__): #iPython interactive console output IOBUF monitor socket.
			self.monitorWidgets[a.objectName()]=remoteWidget(a.objectName(),{'widget':'ipywidget'} )
			a.message_received.connect(functools.partial(self.updateShellOutput,a.objectName()))

		elif ".DIO'" in str(a.__class__):			#DIO widget from KuttyPy
			self.monitorWidgets[a.objectName()] = remoteWidget(a.objectName(),{'widget':'dio','value':a.getState()}, functools.partial(self.setDioState,a) )
		elif ".DIOADC'" in str(a.__class__):			#DIO widget from KuttyPy
			self.monitorWidgets[a.objectName()]=remoteWidget(a.objectName(),{'widget':'dioadc','value':a.getState()}, functools.partial(self.setDioState,a) )
		elif ".DIOPWM'" in str(a.__class__):			#PWM widget from KuttyPy
			self.monitorWidgets[a.objectName()]=remoteWidget(a.objectName(),{'widget':'diopwm','value':a.getState()}, functools.partial(self.setDioState,a) )
		else:
			print(' UNKNOWN WIDGET: ',str(a.__class__))
			return False


		if a.property("remote"):
			self.monitorWidgets[a.objectName()].updateParams({'remote':a.property("remote")})

		self.monitorWidgets[a.objectName()].params.update(kwargs) #Override with any keyword arguments

	def executeRemoteCallback(self,data):
		self.monitorWidgets[data['widget']].setValue(data)

	def disconnectGraphConnections(self):
		for a in self.graphConnections:
			print('disconnecting',a)
			a.sigPlotChanged.disconnect()
		self.graphConnections = []
		self.graphWidgetValues = {}


	def graphChanged(self,graph): #This function is called when the graph is altered (range) . It disconnects all signals, and new data items to signals.
		self.disconnectGraphConnections()
		for b in graph.plotItem.listDataItems():
			b.sigPlotChanged.connect(functools.partial(self.updatePlot,graph.objectName(),b, ))
			self.graphConnections.append(b)
		#print('something changed with the graph',self.graphConnections)

	def truncateFloats(self,obj,decimals=2):
		return json.loads(json.dumps(obj), parse_float=lambda x: round(float(x), decimals) )

	def updateShellOutput(self,name, data): 
		self.transmitWidgetValues({name:{'widget':'ipywidget','value':{'type':data['msg_type'],'content':data['content']} }})

	def updatePlot(self,name,plotDataItem):
		if not self.parent.autographtransmit: return
		if 'PlotDataItem' in str(plotDataItem.__class__):
			if(len(plotDataItem.curve.xData)<=2): return
			self.graphWidgetValues = [self.truncateFloats(plotDataItem.curve.xData.tolist()),self.truncateFloats(plotDataItem.curve.yData.tolist())]
		elif 'PlotCurveItem' in str(plotDataItem.__class__):
			if(len(plotDataItem.xData)<=2): return
			self.graphWidgetValues = [self.truncateFloats(plotDataItem.xData.tolist()),self.truncateFloats(plotDataItem.yData.tolist())]
		self.parent.webhandler.sendData(json.dumps({name:{'widget':'graph','value':self.graphWidgetValues}}))

	def addMonitorSpacer(self,unique_name,classattr=''):
		self.monitorWidgets[unique_name] = remoteWidget('unique_name',{'widget':'spacer','value':classattr}	)

	def addMonitorVariable(self,unique_name,target,getDataFunction,**kwargs):
		self.monitorWidgets[unique_name]=remoteWidget('unique_name',{'widget':target},None,getDataFunction )
		self.monitorWidgets[unique_name].params.update(kwargs)

	def getWidgetValues(self, cleanup = True):
		self.widgetValues = {}
		for a in self.monitorWidgets:
			if not self.monitorWidgets[a].active and cleanup: continue
			widgetType = self.monitorWidgets[a].widgetType 
			widget = self.parent.findChild(QtWidgets.QWidget, a)
			if widgetType == 'label':
				self.widgetValues[a] = {'widget':widgetType,'text':widget.text()}
			elif widgetType == 'checkbox':
				self.widgetValues[a] = {'widget':widgetType,'value':widget.isChecked(),'text':widget.text()}
			elif widgetType == 'combobox':
				self.widgetValues[a] = {'widget':widgetType,'value':widget.currentIndex(),'text':str(widget.currentText())}
			elif widgetType == 'slider':
				self.widgetValues[a] = {'widget':widgetType,'value':widget.value()}
			elif widgetType == 'button':
				self.widgetValues[a] = {'widget':widgetType,'text':widget.text()}
			elif widgetType == 'textbrowser':
				self.widgetValues[a] = {'widget':widgetType,'text':widget.toPlainText()}
			elif widgetType == 'textedit':
				self.widgetValues[a] = {'widget':widgetType,'text':widget.toPlainText()} #https://conclave-team.github.io/conclave-site/ . implement CRDT at some point.
			elif widgetType == 'combobox':
				self.widgetValues[a] = {'widget':widgetType,'value':widget.currentIndex()}
			elif widgetType in ['dio','dioadc','diopwm']:			#DIO / DIOADC / DIOPWM widget from KuttyPy
				self.widgetValues[a] = {'widget':widgetType,'value':widget.getState()}
			elif widgetType == 'graph':
				graphvals = [] #dummy
				xlen = 0
				for b in widget.plotItem.listDataItems():
					if 'PlotDataItem' in str(b.__class__):
						if(len(b.curve.xData)<=2):
							continue #Invalid xdata. minimum 2 points required.
						if(not len(graphvals)):
							graphvals.append(self.truncateFloats(b.curve.xData.tolist()))
							xlen = len(graphvals[-1])
						graphvals.append(self.truncateFloats(b.curve.yData.tolist()))
						#tval = {"x":b.curve.xData.tolist(),"y":b.curve.yData.tolist()}
					elif 'PlotCurveItem' in str(b.__class__): #also check whether histogram or line plot
						if b.xData is not None and b.yData is not None:
							if(len(b.xData)<=2):
								continue
							if(not len(graphvals)):
								if len(b.xData) == len(b.yData): #Regular plot
									graphvals.append(self.truncateFloats(b.xData.tolist()))
								else: #Histogram probably. 
									graphvals.append(self.truncateFloats(b.xData[:-1].tolist())) #Knock off one element
								xlen = len(graphvals[-1])
							graphvals.append(self.truncateFloats(b.yData.tolist()))

						#tval = {"x":b.xData.tolist(),"y":b.yData.tolist()}
				if (len(graphvals)):
					self.widgetValues[a] = {'widget':widgetType,'value':graphvals} # graphvals ...[x1,y1,y2,y3...]
			elif widgetType in ['spacer']:
				pass #widgetValues[a] = [widgetType,parent.findChild(QtWidgets.QSlider, a).value()]
			elif self.monitorWidgets[a].callback:
				self.widgetValues[a] = {'widget':widgetType,'value':self.monitorWidgets[a].callback()} 
		return self.widgetValues

	def transmitWidgetValues(self,widgetValues,**kwargs):
		if not self.activeroom:return
		if not len(widgetValues) : #Empty list. return
			return

		data = {'room':self.activeroom}
		data.update(kwargs)

		data['widget values'] = widgetValues
		#print(widgetValues.keys())
		self.sio.emit('widget values',data,namespace='/classroom')

	def clearMonitors(self):
		self.monitorWidgets = OrderedDict()

	def getScriptList(self,url):
		#self.sio.emit('script list',{},setScriptList,namespace='/classroom')
		r = requests.get(url+'/getStaticData',{'data':'scripts'} ,verify=False)
		if r.status_code == 200:
			return r.json()
		else:
			print('invalid status code returned on login',r.status_code)
			return {}

