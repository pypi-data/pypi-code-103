#!/usr/bin/env python
# -*- coding: utf-8 -*-
from collections import defaultdict
from lxml import etree
import json5
import re
from w3lib import html

_isdefault = 0
_tag_sep=' '
_key_sep=' '
_defaultKeyL = None
_defaultValueL = None
#方法：table转换为json
#入参
# tableStr:table相关的html字符串 列表
# keyNumList:key的行号，合并的行号列表
# excludeKeyList:排除的行号列表
# hasLabel:是否包含标签：0：否，1：是 , 2：只保留值的标签
# isDefault:是否使用默认的： 0：否，1：是 （智能匹配默认key和value）
# tagSep:不用标签时，标签的占位字符串  ，默认空格
# keySep:key的分割字符串，默认空格
#出参
# 返回 dict的List,形式如[{'key1':'value1','key2':'value2'},{'key1','value12','key2':'value22'}]
def table2json(tableStr=['<table></table>'], keyNumList=[0], excludeKeyList=[], hasLabel = 0,isDefault = 0,tagSep=' ',keySep=' '):
    global _tag_sep
    global _key_sep
    global _isdefault
    _tag_sep = tagSep
    _key_sep = keySep
    _isdefault = isDefault
    ##合并tableStr
    ##保留第一个tableStr的table、tbody标签，其他的table、tbody标签去除
    table = []
    for tableItemStr in tableStr:
        doc = etree.HTML(tableItemStr, etree.HTMLParser())
        ###解析tableStr为dict列表
        for table_el in doc.xpath('//table'):
            table += __table_to_list(table_el,hasLabel)

    maxLen = 0
    for temp in table:
        if maxLen < len(temp):
            maxLen = len(temp)

    keyL = getKeyL(_key_sep, _tag_sep, hasLabel, keyNumList, maxLen, table)
    # value的列表 排除 下标为keyNumList、excludeKeyList的为value列表
    valueL = [element for i, element in enumerate(table) if i not in keyNumList+excludeKeyList]
    #如果用默认，直接返回
    if _isdefault == 1 and _defaultValueL is not None:
        valueL = _defaultValueL


    rightLength = 0
    for i,item in enumerate(table):
        if len(item)>rightLength:
            rightLength = len(item)
    ##把异常长度的全去掉
    valueL = [i for i in valueL if len(i)==rightLength]

    # 将key和value组装起来[{},{},{},...]
    if len(valueL) > 0:
        result = list()
        for value in valueL:
            jsons = {}
            for keyIndex, key in enumerate(keyL):
                if(keyIndex<=len(value)-1):
                    jsons[key] = value[keyIndex]
            result.append(jsons)

        return result

    return None

##获取keyL
def getKeyL(_key_sep, _tag_sep, hasLabel, keyNumList, maxLen, table):
    # key的列表
    keyL = ['' for n in range(maxLen)]
    for keyNum in keyNumList:
        try:
            if keyNum < len(table) - 1:  ##此处要做这个判断，否则会报错
                keyList = table[keyNum]
                keyL.append(keyList)
        except Exception as e:
            print("常规报错：" + e)
            None
    #如果用默认，直接返回
    if _isdefault == 1 and _defaultKeyL is not None:
        keyL = _defaultKeyL
    ##循环操作
    newkeyL = ['' for n in range(maxLen)]
    for keyList in keyL:
        for i, key in enumerate(keyList):
            if newkeyL[i].strip().strip(_key_sep) != keyList[i].strip():
                if i < len(keyList) - 1:
                    newkeyL[i] += keyList[i] + _key_sep
                else:
                    newkeyL[i] += keyList[i]

    newkeyL = [x.strip().strip(_key_sep) for x in newkeyL]
    # 只保留值的标签
    if hasLabel == 2:
        newkeyL = [re.compile(r'<[^>]+>', re.S).sub(_tag_sep, x).strip().strip(_key_sep) for x in newkeyL]
    return newkeyL


#方法：table转换为json字符串
def table2jsonStr(tableStr=['<table></table>'], keyNumList=[0], excludeKeyList=[],hasLabel = 0):
    return json5.dumps(table2json(tableStr,keyNumList,excludeKeyList,hasLabel), ensure_ascii=False)


def __table_to_list(table, hasLabel=0):
    dct = __table_to_2d_dict(table, hasLabel)
    return list(__iter_2d_dict(dct))

#, hasLabel是否包含标签 0否，1是
def __table_to_2d_dict(table, hasLabel=0):

    tables = table.xpath("./tbody|./thead")
    ##头部的列表
    headIndexList = set()
    bodyHeadIndexList = set()
    headResult = __table_label(table, hasLabel, './thead', './td|./th',headIndexList)
    bodyResult = __table_label(table,hasLabel,'./tbody','./td|./th',bodyHeadIndexList)
    if(len(bodyResult)==0):
        bodyResult = __table_label(table,hasLabel,'../table','./td|./th',bodyHeadIndexList)

      #"./tbody|./thead"
      #'./td|./th'
    ll = defaultdict(list)
    ##设置默认头、默认体
    defaultKeyL =  [headResult[i] for i , head in enumerate(headResult) if i in headIndexList] +[bodyResult[i] for i , head in enumerate(bodyResult) if i in bodyHeadIndexList]
    defaultValueL = [headResult[i] for i , head in enumerate(headResult) if i not in headIndexList] +[bodyResult[i] for i , head in enumerate(bodyResult) if i not in bodyHeadIndexList]
    global _defaultKeyL
    global _defaultValueL
    _defaultKeyL = defaultKeyL
    _defaultValueL = defaultValueL

    ##存在头和身体都一样的情况，这个说明头和身体都含有 th
    if headResult == bodyResult:
        for i,item in enumerate([headResult[i] for i in headResult]):
            ll[i] =item
        return ll
    for i,item in enumerate([headResult[i] for i in headResult]+[bodyResult[i] for i in bodyResult]):
        ll[i] =item

    return ll

def __table_label(table, hasLabel=0,tableXpath = './tbody',rowXpath = './td' , headIndexList = set()):
    result = defaultdict(lambda: defaultdict())
    tables = table.xpath(tableXpath)
    for table2 in tables:
        for row_i, row in enumerate(table2.xpath('//tr')):
            for col_i, col in enumerate(row.xpath(rowXpath)):
                col_data = ''
                colspan = int(col.get('colspan', 1))
                rowspan = int(col.get('rowspan', 1))
                if len(col) > 0:
                    lst = []
                    # for e in col:
                    item = html.remove_tags(etree.tostring(col, method='html',encoding='UTF-8'),which_ones = ('tr','td','th'),encoding='utf-8')
                    if hasLabel == 0:
                        # for e in col:
                        #     lst.append(e.xpath('string(.)'))
                        item = re.compile(r'<[^>]+>', re.S).sub(_tag_sep, item)
                    else:
                        None
                    lst.append(item)
                    col_data = ''.join(lst)
                else:
                    col_data = col.text
                if col_data is None:
                    col_data = ''
                while row_i in result and col_i in result[row_i]:
                    col_i += 1
                headIndex = None
                for i in range(row_i, row_i + rowspan):
                    ##保存头部位置
                    if 'th' in col.tag and headIndex is None:
                        #头部
                        headIndex = i
                        headIndexList.add(headIndex)
                    for j in range(col_i, col_i + colspan):
                        if (col_data != None):
                            result[i][j] = str(col_data).strip()
    return result
def __iter_2d_dict(dct):
    for i, row in sorted(dct.items()):
        cols = []
        for j, col in sorted(row.items()):
            cols.append(col)
        yield cols
