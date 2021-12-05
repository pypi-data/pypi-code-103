class TradeType:
    M = 'M'
    D = 'D'
    W = 'W'
    One = '1'
    Five = '5'
    Fifteen = '15'
    Thirty = '30'
    Sixty = '60'

FrequencyDic = {
    'M': 24*60*60*31,
    'W': 24*60*60*7,
    'D': 24*60*60,
    '60': 60*60,
    '30': 30*60,
    '15': 15*60,
    '5': 5*60,
    '1': 60
}

FrequencyMinDic = {
    '60': 60,
    '30': 30,
    '15': 15,
    '5': 5,
    '1': 1
}

FrequencyDescDic = {
    'M': '月线级别',
    'W': '周线级别',
    'D': '日线级别',
    '60': '60分钟级别',
    '30': '30分钟级别',
    '15': '15分钟级别',
    '5': '5分钟级别',
    '1': '1分钟级别'
}

SubFreqDic = {
    'M': 'W',
    'W': 'D',
    'D': '30',
    '60': '5',
    '30': '5',
    '15': '5',
    '5': '1',
    '1': None
}

SuperFreqDic = {
    'M': None,
    'W': 'M',
    'D': 'W',
    '60': 'D',
    '30': 'D',
    '15':'60',
    '5' : '30',
    '1':'5'
}

def getFrequencyFromTradeType(ktype):
    return FrequencyDic[ktype]

def getFrequencyList():
    return FrequencyDic.keys()


def getMinsDiffFromFreq(freq):
    return FrequencyMinDic[freq]

def getSubFreq(freq):
    if SubFreqDic.__contains__(freq):
        return SubFreqDic[freq]
    return None

def getFreqDesc(freq):
    return FrequencyDescDic[freq]

def getDayFreqList():
    return ['D','W','M']

def getMinFreqList():
    return ['1','5','15','30','60']

def getStorageFreqList():
    return ['D','1','5','15','30','60']

def getSuperFreq(freq):
    return SuperFreqDic[freq]
