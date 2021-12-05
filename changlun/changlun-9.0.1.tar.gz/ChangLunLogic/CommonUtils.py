__author__ = 'shenli'

def addIndex(objectList):
    if objectList is None or len(objectList) == 0:
        return None
    for i in range(0,len(objectList)):
        objectList[i]['index'] = i
    return objectList