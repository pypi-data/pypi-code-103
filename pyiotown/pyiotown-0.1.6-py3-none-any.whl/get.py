import requests

def downloadAnnotations(url, token, classname):
    ''' 
    url : IoT.own Server Address
    token : IoT.own API Token
    classname : Image Class ex) car, person, airplain
    '''
    apiaddr = url + "/api/v1.0/nn/images?labels=" + classname
    header = {'Accept':'application/json', 'token':token}
    try:
        r = requests.get(apiaddr, headers=header, verify=False, timeout=10)
        if r.status_code == 200:
            return r.json()
        else:
            print(r)
            return None
    except Exception as e:
        print(e)
        return None

def storage(url, token, nid, date_from , date_to, lastKey=""):
    '''
    url : IoT.own Server Address
    token : IoT.own API Token
    nid : Node ID
    date_from : UTC structure ex) "2018-11-02T13:00:00Z"
    '''
    header = {'Accept':'application/json','token':token}
    apiaddr = url + "/api/v1.0/storage?nid=" + nid + "&from=" + date_from + "&to=" + date_to
    if lastKey != "":
        apiaddr = url + "/api/v1.0/storage?nid=" + nid + "&from=" + date_from + "&to=" + date_to + "&lastKey=" + lastKey
    try:
        print(apiaddr)
        r = requests.get(apiaddr,headers=header, verify=False, timeout=10)
        if r.status_code == 200:
            return r.json()
        else:
            print(r.content)
            return None
    except Exception as e:
        print(e)
        return None
    

def downloadImage(url, token, imageID):
    ''' 
    url : IoT.own Server Address
    token : IoT.own API Token
    imageID : IoT.own imageID ( using annotation's 'id' not '_id' ) 
    '''
    apiaddr = url + "/nn/dataset/img/" + imageID
    header = {'Accept':'application/json', 'token':token}
    try:
        r = requests.get(apiaddr, headers=header, verify=False, timeout=10)
        if r.status_code == 200:
            return r.content
        else:
            print(r)
            return None
    except Exception as e:
        print(e)
        return None
