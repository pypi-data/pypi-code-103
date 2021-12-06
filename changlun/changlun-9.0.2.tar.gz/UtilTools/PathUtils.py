import os
import traceback

backTestDirTemplate = 'D:\\xampp\\htdocs\\backtest\\%s'
backTestPathTemplate = 'D:\\xampp\\htdocs\\backtest\\%s\\%s.html'
baseDirTemplate = 'D:\\xampp\\htdocs\\model\\%s'

def createDir(todayStr):
    basePath = baseDirTemplate % (todayStr)
    if os.path.exists(basePath):
        return
    try:
        os.mkdir(basePath)
    except Exception as e:
        print(e)
        traceback.print_exc()

def createBackTestDir(modelName):
    basePath = backTestDirTemplate % (modelName)
    if os.path.exists(basePath):
        return
    try:
        os.mkdir(basePath)
    except Exception as e:
        print(e)
        traceback.print_exc()

def getBackTestPath(modelName,stockId):
    return backTestPathTemplate % (modelName,stockId)

