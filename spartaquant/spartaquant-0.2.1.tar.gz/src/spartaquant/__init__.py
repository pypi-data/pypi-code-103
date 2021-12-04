import importlib
import sys
import os
import getpass

import requests
import inspect
import json
import base64
import cloudpickle
import sqlite3


class spartaquant():

    def __init__(self):
        self.URL_BASE = None
        self.USER_ID = None
        self.authenticate()

    def authenticate(self):
        # **************************************************************************************************************
        bInternalJupyterDesktop = False
        try:
            self.URL_BASE, self.USER_ID = self.getDBAuthFunc()
            bInternalJupyterDesktop = True
        except Exception as e:
            pass
        
        def printError():
            print("Authentication failed. Make sure you have entered the correct accessKey")

        if not bInternalJupyterDesktop:
            accessKey = getpass.getpass(prompt="Enter your access key")
            try:
                mainUrl = self.decodeMainUrl(accessKey)
            except:
                printError()
                return
                
            validateUrl = mainUrl+'validateMainUrlExternalApi'
            newJson = dict()
            json_data = dict()
            json_data['accessKey'] = accessKey
            newJson['jsonData'] = json.dumps(json_data)
            newJsonB = json.dumps(newJson)
            try:
                res = requests.post(validateUrl, data=newJsonB, verify=False)
                statusCode = res.status_code
                if int(statusCode) == 200:
                    resJson = json.loads(res.text)
                    res = resJson['res']
                    if res == 1:
                        self.URL_BASE = mainUrl
                        self.USER_ID = self.decodeb64(self.decodeb64(resJson['userId']))
                        print("You are logged "+str(chr(0x2713)))
                    else:
                        printError()
                else:
                    printError()
            except:
                printError()

        # **************************************************************************************************************

    def decodeMainUrl(self, accessKey):
        return self.decodeFunc(self.decodeFunc(accessKey).split('__sq__')[0])

    def decodeb64(self, thisStr):
        return base64.b64decode(thisStr).decode('utf-8')
        
    def decodeFunc(self, thisStr):
        return self.decodeb64(self.decodeb64(self.decodeb64(thisStr)))

    def getDBAuthFunc(self):
        try:
            currentDirPath = os.path.dirname(os.path.abspath(__file__))
            currentDirPath = os.path.dirname(currentDirPath)
            currentDirPath = os.path.dirname(currentDirPath)
            currentDirPath = os.path.dirname(currentDirPath)
            currentDirPath = os.path.dirname(currentDirPath)
            dbPath = currentDirPath+'\desktop.sqlite3'
            conn = sqlite3.connect(dbPath)  
            data  = conn.execute("SELECT * FROM config").fetchall()
            nbRow = len(data)
            conn.close()
            if nbRow > 0:
                return self.decodeMainUrl(data[-1][0]), base64.b64decode(data[-1][1]).decode('utf-8')
            else:
                return None
        except:
            return None

    # def getDBAuth(self):
    #     global bInternalJupyterDesktop
    #     if bInternalJupyterDesktop:
    #         return getDBAuthFunc()
    #     else:
    #         global urlExternalApi
    #         global userIdExternalApi
    #         return urlExternalApi, userIdExternalApi

    def sendRequests(self, funcName, *args):
        # try:
        #     URL_BASE, USER_ID = self.getDBAuth()
        # except:
        #     print("Authentication failed. You may need to restart the kernel")
        #     return 
        if self.URL_BASE is None or self.USER_ID is None:
            print("Authentication failed. You may need to reload the SpartaQuant module")

        thisUrl = self.URL_BASE+"jupyterAPI"
        newJson = dict()
        json_data = dict()
        argsSerialized = []
        for thisArg in args:
            data_bin = cloudpickle.dumps(thisArg)
            serializedObj = str(base64.b64encode(data_bin), "utf-8")
            argsSerialized.append(serializedObj)
        
        json_data['userId'] = 'EXT_API'+str(base64.b64encode(str(self.USER_ID).encode()), 'utf-8')
        json_data['funcName'] = funcName
        json_data['args'] = argsSerialized
        newJson['jsonData'] = json.dumps(json_data)
        newJsonB = json.dumps(newJson)
        res = requests.post(thisUrl, data=newJsonB, verify=False)
        resJson = json.loads(res.text)
        if int(resJson['res']) == 1:
            return cloudpickle.loads(base64.b64decode(resJson['serializedObj']))
        else:
            print("Could not proceed the request")
            return {'res': -1}

    def getDataDB(self):
        funcName = str(inspect.stack()[0][0].f_code.co_name)
        return self.sendRequests(funcName)

    def getData(self, thisData):
        funcName = str(inspect.stack()[0][0].f_code.co_name)
        return self.sendRequests(funcName, thisData)

    def getDataDates(self, thisDates, formula, bBusiness=True, formatDate='%Y%m%d'):
        funcName = str(inspect.stack()[0][0].f_code.co_name)
        return self.sendRequests(funcName, thisDates, formula, bBusiness, formatDate)

    def getDates(self, startDate, endDate, freq='b', bBusiness=True, orderBased='desc', formatDate='%Y%m%d'):
        funcName = str(inspect.stack()[0][0].f_code.co_name)
        return self.sendRequests(funcName, startDate, endDate, freq, bBusiness, orderBased, formatDate)

    def getFunctionsDB(self):
        funcName = str(inspect.stack()[0][0].f_code.co_name)
        return self.sendRequests(funcName)

    def getMTD(self):
        funcName = str(inspect.stack()[0][0].f_code.co_name)
        return self.sendRequests(funcName)

    def getQTD(self):
        funcName = str(inspect.stack()[0][0].f_code.co_name)
        return self.sendRequests(funcName)

    def getYTD(self):
        funcName = str(inspect.stack()[0][0].f_code.co_name)
        return self.sendRequests(funcName)

    def putExec(self, str2Eval, name):
        funcName = str(inspect.stack()[0][0].f_code.co_name)
        return self.sendRequests(funcName, str2Eval, name)

    def runFunction(self, functionName, *args):
        funcName = str(inspect.stack()[0][0].f_code.co_name)
        return self.sendRequests(funcName, functionName, *args)

    def createFunction(self, functionObj):
        functionSource = inspect.getsource(functionObj)
        funcName = str(inspect.stack()[0][0].f_code.co_name)
        return self.sendRequests(funcName, functionSource)

    def updateFunction(self, functionName2Create, functionObj):
        functionSource = inspect.getsource(functionObj)
        funcName = str(inspect.stack()[0][0].f_code.co_name)
        return self.sendRequests(funcName, functionName2Create, functionSource)

    def testFunction(self, functionObj, *args):
        print("test function")
        print("args")
        print(len(args))
        print(args)
        try:
            functionObj.__call__(args)
        except Exception as e:
            print("Error")
            print(e)
        # functionSource = inspect.getsource(functionObj)
        # funcName = str(inspect.stack()[0][0].f_code.co_name)
        return "Function tested"

    