import requests
import threading
from urllib.parse import urlparse
import paho.mqtt.client as mqtt
import json

def uploadImage(url, token, payload):
    '''
    url : IoT.own Server Address
    token : IoT.own API Token
    payload : Image + Annotation Json Data (check format in README.md)
    '''
    apiaddr = url + "/api/v1.0/nn/image"
    header = {'Content-Type': 'application/json', 'Token': token}
    try:
        r = requests.post(apiaddr, data=payload, headers=header, verify=False, timeout=10)
        if r.status_code == 200:
            return True
        else:
            print(r)
            return False
    except Exception as e:
        print(e)
        return False
def data(url, token, nid, data):
    '''
    url : IoT.own Server Address
    token : IoT.own API Token
    type: Message Type
    nid: Node ID
    data: data to send (JSON object)
    '''
    typenum = "2" # 2 static 
    apiaddr = url + "/api/v1.0/data"
    header = {'Accept':'application/json', 'token':token} 
    payload = { "type" : typenum, "nid" : nid, "data": data }
    try:
        r = requests.post(apiaddr, json=payload, headers=header, verify=False, timeout=10)
        if r.status_code == 200:
            return True
        else:
            print(r)
            return False
    except Exception as e:
        print(e)
        return False

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connect OK! Subscribe Start")
    else:
        print("Bad connection Reason",rc)
def on_message(client, userdata, msg):
    data = json.loads((msg.payload).decode('utf-8'))
    result = json.dumps(userdata(data)).encode('utf-8')
    print("post process done. publish result")
    client.publish('iotown/proc-done', result, 1)
def updateExpire(url, token, name):
    apiaddr = url + "/api/v1.0/pp/proc"
    header = {'Accept':'application/json', 'token':token}
    payload = { 'name' : name}
    try:
        r = requests.post(apiaddr, json=payload, headers=header, verify=False, timeout=10)
        if r.status_code == 200 or r.status_code == 403:
            print("update Expire Success")
        else:
            print("update Expire Fail! reason:",r)
    except Exception as e:
        print("update Expire Fail! reason:", e)
    timer = threading.Timer(60, updateExpire,[url,token,name])
    timer.start()
def getTopic(url, token, name):
    apiaddr = url + "/api/v1.0/pp/proc"
    header = {'Accept':'application/json', 'token':token}
    payload = {'name':name}    
    try:
        r = requests.post(apiaddr, json=payload, headers=header, verify=False, timeout=10)
        if r.status_code == 200:
            print("Get Topic From IoT.own Success")
            return json.loads((r.content).decode('utf-8'))['topic']
        elif r.status_code == 403:
            print("process already in use. please restart after 1 minute later.")
            return json.loads((r.content).decode('utf-8'))['topic']
        else:
            print(r)
            return None
    except Exception as e:
        print(e)
        return None
def postprocess(url, token, name, func, username, pw):
    # get Topic From IoTown
    topic = getTopic(url,token,name)
    print("topic:",topic)
    if topic == None:
        raise Exception("Fatal Error")
    else:
        updateExpire(url, token, name)
    # if return typical topic, then updateExpire 60 seconds
    # if return 403 error, that means postprocess already in use at the other 
    #2  func등록 및 ID, PASSWORD 등록하기
    client = mqtt.Client() #client config
    client.on_connect = on_connect # callback function config (on_connect)
    client.on_message = on_message # callback function config (on_message)
    client.username_pw_set(username,pw)
    client.user_data_set(func)
    #3 토픽정보를 가지고 subscribe를 시작한다.
    mqtt_server = urlparse(url).netloc
    print("connect to",mqtt_server)
    client.connect(mqtt_server) # server address
    client.subscribe(topic,1) # subscribe all 'topic#'
    client.loop_forever() # loop forever

def postprocess_common(url, topic, func, username, pw):
    client = mqtt.Client() #client config
    client.on_connect = on_connect # callback function config (on_connect)
    client.on_message = on_message # callback function config (on_message)
    client.username_pw_set(username,pw)
    client.user_data_set(func)
    #3 토픽정보를 가지고 subscribe를 시작한다.
    mqtt_server = urlparse(url).netloc
    print("connect to",mqtt_server)
    client.connect(mqtt_server) # server address
    # topic = 'iotown/proc/common/yolox-x'
    client.subscribe(topic,1) # subscribe all 'topic#'
    client.loop_forever() # loop forever
