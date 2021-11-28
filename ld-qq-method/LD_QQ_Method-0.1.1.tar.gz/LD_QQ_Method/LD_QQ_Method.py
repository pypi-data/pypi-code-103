# Insert your code here. 
from email import message
import requests
from urllib import parse
import base64
from requests import api
import threading
import json
import os
import console
import random

apiUrl = ''
TTSUrl = ''
TianXingKey = ''

messageType = {
    '1'     : '好友',
    '2'     : '群聊',
    '1000'  : '单向添加好友',
    '1001'  : '被请求添加好友',
    '80004' : '机器人发出消息'
}
color = ['\033[31m', '\033[32m', '\033[33m', '\033[34m', '\033[35m', '\033[36m', '\033[37m']

# 机器人基础属性
class myRobot():
    def __init__(self, myApiUrl, myTTSUrl, myTianXingKey):
        global apiUrl
        global TTSUrl
        global TianXingKey
        apiUrl = myApiUrl
        TTSUrl = myTTSUrl
        TianXingKey = myTianXingKey

# 创建线程
class myThread(threading.Thread):
    def __init__(self, name, raw_rev_data):
        threading.Thread.__init__(self)
        # self.myThread.name = myThread.name
        self.name = name
        self.raw_rev_data = raw_rev_data
        self.recRobot = ''
        self.recType = -1
        self.recID = ''
        self.recFromQQ = ''
        self.recMsg = ''
        self.colorFront = random.randint(31, 37)
        self.colorBack = random.randint(41, 47)
        while True:
            if (self.colorFront + 10) == self.colorBack:
                self.colorBack = random.randint(41, 47)
            else:
                break
    def run(self):
        msg = self.name + "：开始线程" 
        print (self.wordColor(msg))
        # 解析 raw_rev_data 文件
        raw_rev_data = json.loads(self.raw_rev_data)
        self.recRobot = raw_rev_data['MQ_robot']
        self.recType = raw_rev_data['MQ_type']
        self.recID = raw_rev_data['MQ_fromID']
        self.recFromQQ = raw_rev_data['MQ_fromQQ']
        self.recMsg = parse.unquote(raw_rev_data['MQ_msg'])
        # print(raw_rev_data)
        # 触发条件后根据实际情况处理调用情况
        if self.recType == 1 or (self.recType == 2 and not (self.recFromQQ == self.recRobot)):
            apiSendMsg(self)
        elif self.recType == 1000 or self.recType == 1001:
            agreeFriendEvent(self)
        msg = self.name + "：退出线程" 
        print (self.wordColor(msg))
    # 文字颜色
    def wordColor(self, recMsg):
        recMsg = '\033['+ str(self.colorFront) + ';' + str(self.colorBack) + 'm' + recMsg + '\033[0m'
        return recMsg

# api消息回应
def apiSendMsg(myThread):
    try:
        global result
        myThread.recMsg = strQ2B(myThread.recMsg)
        fromQQName = getFriendsRemark(myThread)
        if myThread.recType == 1:
            msg = myThread.name + '：[' + messageType[str(myThread.recType)] + '] ' + fromQQName + '(' + myThread.recID + ')：' + myThread.recMsg
            print(myThread.wordColor(msg))
            if myThread.recFromQQ == '3194775246' and myThread.recMsg[0] == '/':
                systemSetting(myThread)
            else:
                prepareVoice(myThread)
                sendVoice_friend(myThread)
        elif myThread.recType == 2 and judgeAt(myThread.recMsg):
            groupName = getGroupName(myThread)
            msg = myThread.name + '：[' + messageType[str(myThread.recType)] + '] [' + groupName + ']' + fromQQName + '(' + myThread.recID + ')：' + myThread.recMsg
            print(myThread.wordColor(msg))
            myThread.recMsg = deleteAt(myThread.recMsg)
            prepareVoice(myThread)
            sendVoice_group(myThread)
    except Exception as e:
        msg = 'error:', e
        print(myThread.wordColor(msg))

# 系统设置
def systemSetting(myThread):
    msgLen = len(myThread.recMsg)
    myThread.recMsg = myThread.recMsg[1:msgLen]
    if myThread.recMsg == '线程数目':
        sendMsg = '当前线程：' + str(len(threading.enumerate()))
        sendMsg_friend(myThread, myThread.recFromQQ, sendMsg)

# 发送消息
def sendMsg_friend(myThread, sendNum, sendMsg):
    sendMsgData = {
        'function'  : 'Api_SendMsg',
        'token'     : '666',
        'params'    : {
            'c1'        : myThread.recRobot,
            'c2'        : 1,
            'c3'        : '',
            'c4'        : sendNum,
            'c5'        : sendMsg
        }
    }
    requests.post(apiUrl, json=sendMsgData)
    msg = myThread.name + '：向' + getFriendsRemark(myThread) + '(' + sendNum + ')发送：' + sendMsg
    print(myThread.wordColor(msg))

# 字典类型数据None数据处理功能
def dict_clean(items):
    result = {}
    for key, value in items:
        if value is None:
            value = '没有找到'
        result[key] = value
    return result

# 全角 -> 半角转换功能
def strQ2B(ustring):
    ss = ''
    for s in ustring:
        restring = ''
        for uchar in s:
            inside_code = ord(uchar)
            if inside_code == 12288:                # 全角空格直接转换
                inside_code = 32
            elif 65281 <= inside_code <= 65374:     # 全角字符（除空格）根据关系转化
                inside_code -= 65248
            restring += chr(inside_code)
        ss += restring
    return ss

# 使用 VOCALTTS 获取mp3
def getTTStoMP3(myThread, TTSQuest):
    TTSDosynth = requests.get(TTSUrl + 'text=' + TTSQuest).json()
    code64 = TTSDosynth['data']
    code = base64.b64decode(code64)
    route = 'E:/MyQQ/MyQQ/Voice/' + myThread.name + '.mp3'
    tts = open(route, 'wb')
    tts.write(code)
    tts.close()
    msg = myThread.name + '：成功获取MP3'
    print(myThread.wordColor(msg))
    return

# 使用 天行机器人 获取回复内容
def getTianXing(myThread):
    TianXingData = {
            'key'       : TianXingKey,
            'question'  : '你好',
            'mode'      : 1
        }
    TianXingData['question'] = myThread.recMsg
    TianXingURL = 'http://api.tianapi.com/robot/index'
    TianXingPost = requests.post(TianXingURL, data=TianXingData).json()
    TianXingNewlist = TianXingPost['newslist']
    TianXingReply = TianXingNewlist[0]
    msg = myThread.name + '：AI(' + myThread.recRobot + ')：' + TianXingReply['reply']
    print(myThread.wordColor(msg))
    return TianXingReply['reply']

# Mp3 转 Amr
def getAmr(myThread):
    routeMp3 = 'E:/MyQQ/MyQQ/Voice/' + myThread.name + '.mp3'
    routeAmr = 'E:/MyQQ/MyQQ/Voice/' + myThread.name + '.amr'
    AMRData = {
            'function'  : 'Api_Mp3ToAmr',
            'token'     : '666',
            'params'    : {
                'c1'        : routeMp3,
                'c2'        : routeAmr
            }   
        }
    requests.post(apiUrl, json=AMRData)
    msg = myThread.name + '：成功获取AMR'
    print(myThread.wordColor(msg))
    os.remove(routeMp3)
    return

# 好友发送语音
def sendVoice_friend(myThread):
    routeAmr = 'E:/MyQQ/MyQQ/Voice/' + myThread.name + '.amr'
    SendVoiceData = {
        'function'  : 'Api_SendVoice',
        'token'     : '666',
        'params'    : {
            'c1'        : myThread.recRobot,
            'c2'        : myThread.recID,
            'c3'        : routeAmr
        }
    }
    requests.post(apiUrl, json=SendVoiceData)
    os.remove(routeAmr)
    msg = myThread.name + '：向' + myThread.recID + '发送音频'
    print(myThread.wordColor(msg))

# 上传语音
def upLoadVoice(myThread):
    routeAmr = 'E:/MyQQ/MyQQ/Voice/' + myThread.name + '.amr'
    upLoadVoiceData = {
        'function'  : 'Api_UpLoadVoice',
        'token'     : '666',
        'params'    : {
            'c1'        : myThread.recRobot,
            'c2'        : routeAmr
        }
    }
    GUIDData = requests.post(apiUrl, json=upLoadVoiceData).json()
    GUIDret = GUIDData['data']
    msg = myThread.name + '：语音上传成功'
    print(myThread.wordColor(msg))
    return GUIDret['ret']

# 群聊发送语音
def sendVoice_group(myThread):
    routeAmr = 'E:/MyQQ/MyQQ/Voice/' + myThread.name + '.amr'
    GUID = upLoadVoice(myThread)
    sendVoiceData = {
        'function'  : 'Api_SendMsg',
        'token'     : '666',
        'params'    : {
            'c1'        : myThread.recRobot,
            'c2'        : 2,
            'c3'        : myThread.recID,
            'c4'        : '',
            'c5'        : GUID
        }
    }
    requests.post(apiUrl, json=sendVoiceData)
    os.remove(routeAmr)
    msg = myThread.name + '：向' + myThread.recID + '发送音频'
    print(myThread.wordColor(msg))

# 音频准备
def prepareVoice(myThread):
    # 使用 天行机器人 获取回复内容
    reply = getTianXing(myThread)
    # 使用 VOCALTTS 获取mp3
    getTTStoMP3(myThread, reply)
    # Api_Mp3ToAmr
    getAmr(myThread)
    return

# 判断 @
def judgeAt(recMsg):
    if recMsg[0:13] == '[@2327541179]':
        return True
    else:
        return False

# 除去 @
def deleteAt(recMsg):
    msgLen = len(recMsg)
    recMsg = recMsg[14:msgLen]
    return recMsg

# 同意好友添加
def agreeFriendEvent(myThread):
    HandleFriendEventData = {
        'function'  : 'Api_HandleFriendEvent',
        'token'     : '666',
        'params'    : {
            'c1'        : myThread.recRobot,
            'c2'        : myThread.recFromQQ,
            'c3'        : 10,
            'c4'        : ''    
        }
    }
    requests.post(apiUrl, json=HandleFriendEventData)
    welcomSend(myThread)

# 好友添加发送语音
def welcomSend(myThread):
    routeAmr = 'E:/MyQQ/MyQQ/Voice/welcom.amr'
    SendVoiceData = {
        'function'  : 'Api_SendVoice',
        'token'     : '666',
        'params'    : {
            'c1'        : myThread.recRobot,
            'c2'        : myThread.recFromQQ,
            'c3'        : routeAmr
        }
    }
    requests.post(apiUrl, json=SendVoiceData)
    msg = myThread.name + '：向' + myThread.recFromQQ + '发送欢迎音频'
    print(myThread.wordColor(msg))

# 获取好友备注
def getFriendsRemark(myThread):
    GetFriendsRemarkData = {
        'function'  : 'Api_GetFriendsRemark',
        'token'     : '666',
        'params'    : {
            'c1'        : myThread.recRobot,
            'c2'        : myThread.recFromQQ
        }
    }
    recFromQQName = requests.post(apiUrl, json=GetFriendsRemarkData).json()
    fromQQNameData = recFromQQName['data']
    fromQQName = fromQQNameData['ret']
    return fromQQName

# 获取群名称
def getGroupName(myThread):
    getGroupNameData = {
        'function'  : 'Api_GetGroupName',
        'token'     : '666',
        'params'    : {
            'c1'        : myThread.recRobot,
            'c2'        : myThread.recID
        }
    }
    recGroupName = requests.post(apiUrl, json=getGroupNameData).json()
    groupNameData = recGroupName['data']
    groupName = groupNameData['ret']
    return groupName
