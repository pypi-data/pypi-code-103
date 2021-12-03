import requests, socketio

url = "mypc.in" #"expeyes.scischool.in"
payload ={'name':'t4','password':'t4','remember':'true'}
print('connect to ','https://'+url+'/login')
session = requests.session()
r = session.post('https://'+url+'/login', payload, verify=False) #,headers={'User-Agent': 'Chrome'}
print('\n\n\n',session.cookies,'\n\n\n')
print('\n\n\n',session.cookies.get('session', domain=url),'\n\n\n')

if r.status_code == 200:
	token = 'remember_token='
	token += session.cookies.get('remember_token', domain=url)
	token += '; session='
	token += session.cookies.get('session', domain=url)

	sio = socketio.Client()

	sio.connect('ws://'+url+':8000',headers={'Cookie': token}, namespaces=['/classroom'])
	sio.emit('join',{'room':'d'}, namespace = '/classroom')

else:
	print('invalid status code returned on login',r.status_code)

