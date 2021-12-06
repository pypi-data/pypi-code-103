#!/usr/bin/env python
# coding=utf-8

import os
import fileinput
from afwfcfg.afwf_log import *

"""
 功能描述: 修改恶意类型动作
    参数: evilType, 腾讯提供的EvilTypes.xls文件中eviltype列的值
         action,   动作类型，取值为1,2。对应动作如下：
                      1--查询到URL为恶意时做监控处理;
                      2--查询到URL为恶意时做重定向处理。
   返回值: True，  设置成功；
          False,  设置失败
     说明: 入参需要传入正确，否则会设置失败。
"""


def AFWF_ModifyEvilTypeAction(evilType, action):
    try:
        if action not in [1, 2]:
            return False
        os.system('mv /opt/afwf/config/afwfEvilType.cfg /opt/afwf/config/afwfEvilType.cfg.bak')
        with open('/opt/afwf/config/afwfEvilType.cfg', 'a+') as fw:
            with open('/opt/afwf/config/afwfEvilType.cfg.bak', 'r+') as fr:
                firstline = 0
                for line in fr:
                    if firstline is 0:
                        firstline = 1
                        fw.write(line)
                        continue
                    elif line is '\n':
                        continue
                    else:
                        eTypeInFile = int(line.split('\t')[1])
                        if eTypeInFile == evilType:
                            newline = '%s' % action + '\t' + line.split('\t')[1] + '\t' + line.split('\t')[2]
                            fw.write(newline)
                        else:
                            fw.write(line)
    except Exception as e:
        print('Failed to set the action for evil type. Reason:%s' % e)
        return False
    return True


"""
 功能描述: 获取恶意类型动作
    参数: evilType, 腾讯提供的EvilTypes.xls文件中eviltype列的值
   返回值: 获取成功返回当前恶意类型的操作类型列表
   　　　　获取失败或不存在该恶意类型时，返回:(0, 0, 0)
     说明:
"""


def AFWF_GetEvilTypeAction(evilType):
    try:
        with open('/opt/afwf/config/afwfEvilType.cfg', 'r') as fr:
            firstline = 0
            for line in fr:
                if firstline is 0:
                    firstline = 1
                    continue
                elif line is '\n':
                    continue
                else:
                    eTypeInFile = int(line.split('\t')[1])
                    if (eTypeInFile == evilType):
                        return (int(line.split('\t')[0]), int(line.split('\t')[1]), int(line.split('\t')[2]),)
    except Exception as e:
        print('Failed to get the action for evil type. Reason:%s' % e)
    return 0, 0, 0


"""
 功能描述: 添加恶意类型及动作
    参数: evilType, 腾讯提供的EvilTypes.xls文件中eviltype列的值
         action, 动作,1表示监控模式，２表示重定向模式
         classification, 类别（八大类中的一类）,取值为１～８
   返回值: True, 添加成功
   　　　　False, 添加失败
     说明:
"""


def AFWF_AddEvilTypeAction(evilType, action, classification):
    try:
        bIsAdd = False
        if action not in [1, 2]:
            return False
        os.system('mv /opt/afwf/config/afwfEvilType.cfg /opt/afwf/config/afwfEvilType.cfg.bak')
        with open('/opt/afwf/config/afwfEvilType.cfg', 'a') as fw:
            with open('/opt/afwf/config/afwfEvilType.cfg.bak', 'r') as fr:
                firstline = 0
                for line in fr:
                    if firstline is 0:
                        firstline = 1
                        fw.write(line)
                        continue
                    elif line is '\n':
                        continue
                    else:
                        eTypeInFile = int(line.split('\t')[1])
                        if (eTypeInFile >= evilType) and (bIsAdd is False):
                            if eTypeInFile == evilType:
                                fw.write(line)
                                bIsAdd = True
                            else:
                                newline = '%s' % action + '\t' + '%s' % evilType + '\t' + '%s' % classification + '\n'
                                fw.write(newline)
                                fw.write(line)
                                bIsAdd = True
                        else:
                            fw.write(line)
    except Exception as e:
        print('Failed to add the action for evil type. Reason:%s' % e)
        return False
    return True


"""
 功能描述: 删除恶意类型及动作
    参数: evilType, 腾讯提供的EvilTypes.xls文件中eviltype列的值
   返回值: True, 删除成功
   　　　　False, 删除失败
     说明:
"""


def AFWF_DelEvilTypeAction(evilType):
    try:
        os.system('mv /opt/afwf/config/afwfEvilType.cfg /opt/afwf/config/afwfEvilType.cfg.bak')
        with open('/opt/afwf/config/afwfEvilType.cfg', 'a') as fw:
            with open('/opt/afwf/config/afwfEvilType.cfg.bak', 'r') as fr:
                firstline = 0
                for line in fr:
                    if firstline is 0:
                        firstline = 1
                        fw.write(line)
                        continue
                    elif line is '\n':
                        continue
                    else:
                        eTypeInFile = int(line.split('\t')[1])
                        if eTypeInFile != evilType:
                            fw.write(line)
    except Exception as e:
        print('Failed to delete the action for evil type. Reason:%s' % e)
        return False
    return True


if __name__ == '__main__':
    for evilType in range(1, 2049):
        # AFWF_ModifyEvilTypeAction(evilType, 2)
        # AFWF_GetEvilTypeAction(evilType)
        # AFWF_AddEvilTypeAction(evilType, 2, 8)
        AFWF_DelEvilTypeAction(evilType)
