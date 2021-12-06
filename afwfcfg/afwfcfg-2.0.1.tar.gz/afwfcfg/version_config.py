#!/usr/bin/env python
# coding=utf-8

import os
from afwf_log import *


"""
 功能描述: 设置特性版本号
    参数: filepath, 版本文件路径,例如：/opt/afwf/
         feature,  特性名称,区分大小写，例如afwf
         verNum,   版本号
         buildEnv, 编译环境
         runEnv,   运行环境
  返回值: True， 设置成功
         False，设置失败
     说明: 文件路径不能携带文件名，统一由软件命名为version.cfg,输入路径时需要携带目录最后一个反斜杠。
          目前特性名称包含：afwf、afui、AFWarning、CommonSysMng、tx_api和APP，区分大小写。
"""


def setFeatureVersion(filepath, feature, verNum, buildEnv, runEnv):
    try:
        bias_add = False
        file_nm = '%s' % filepath + 'version.cfg'
        newline = feature + ': ' + 'version ' + verNum + ', ' + \
            buildEnv + ', ' + runEnv + '\n'
        if feature == 'APP':
            os.system('mv %s %s.bak' % (file_nm, file_nm))
            with open('%s.bak' % file_nm, "r") as fr:
                with open(file_nm, "w") as fw:
                    for line in fr:
                        if line.split(':')[0] == 'APP':
                            fw.write(newline)
                            bias_add = True
                        else:
                            fw.write(line)
                    if bias_add is False:
                        fw.write(newline)
            os.system('rm %s.bak' % file_nm)
        else:
            with open(file_nm, "w") as fp:
                fp.write(newline)
    except Exception as e:
        AFWF_Error("Failed to set the version. Reason: %s" % e)
        return False
    return True


"""
 功能描述: 设置依赖软件版本号
    参数: filepath, 版本文件路径,同特性版本号，例如：/opt/afwf/
         appName,  依赖软件名称,例如：DPDK
         verNum,   版本号，例如：17.05
  返回值: True， 设置成功
         False，设置失败
     说明: 设置依赖软件版本号需要在设置特性版本号以后完成，如果修改了特性版本号，依赖软件版本号需要重新设置。
          如果依赖多个软件版本号，则需要多次调用该接口。
"""


def setDependOnVersion(filepath, app_name, ver_num):
    try:
        file_nm = '%s' % filepath + 'version.cfg'
        os.system('mv %s %s.bak' % (file_nm, file_nm))
        with open('%s.bak' % file_nm, "r") as fr:
            for line in fr:
                if line is '':
                    os.system('rm %s.bak' % file_nm)
                    return False
                else:
                    with open(file_nm, "w") as fw:
                        newline = line.split('\n')[0] + ', ' + \
                                  app_name + ', ' + ver_num + '\n'
                        fw.write(newline)
        os.system('rm %s.bak' % file_nm)
    except Exception as e:
        AFWF_Error("Failed to set the APP version file. Reason: %s" % e)
        return False
    return True


"""
 功能描述: 设置设备ID
    参数: filepath,   版本文件路径,同特性版本号，例如：/opt/afwf/
         mechineID,  设备机器ID，例如：ZJ.HZ.China Mobile.005
  返回值: True， 设置成功
         False，设置失败
    说明: 机器ID格式: 省名.市名.企业名.编号，省名采用英文缩写(可参考国标)，市名为可区分的首字母缩写，企业名为企业英文名，编号为三位整数;
         对于直辖市或特别行政区的省名统一填写成CN。例如：CN.SH.China Mobile.007
"""


def setMechineID(filepath, mechine_id):
    try:
        bias_add = False
        file_nm = '%s' % filepath + 'version.cfg'
        os.system('sudo mv %s %s.bak' % (file_nm, file_nm))
        with open('%s' % file_nm + '.bak', 'r') as fr:
            with open('%s' % file_nm, "a") as fw:
                for line in fr:
                    if line.split()[0] == 'mechine_id:':
                        fw.write('mechine_id: ' + mechine_id + '\n')
                        bias_add = True
                    else:
                        fw.write(line)
                if bias_add is False:
                    fw.write('mechine_id: ' + mechine_id + '\n')
        os.system('sudo rm %s.bak' % file_nm)
    except Exception as e:
        AFWF_Error("Failed to set the Mechine ID. Reason: %s" % e)
        return False
    return True


"""
 功能描述: 获取版本信息
    参数: filepath,  版本文件路径,同特性版本号，例如：/opt/afwf/
         feature,   特性名称，区分大小写。
  返回值: 特性对应的版本信息
    说明: 机器ID格式: 省名.市名.企业名.编号，省名采用英文缩写(可参考国标)，市名为可区分的首字母缩写，企业名为企业英文名，编号为三位整数;
         对于直辖市或特别行政区的省名统一填写成CN。例如：CN.SH.China Mobile.007；
         输入特性名称区分大小写。
"""


def getVersion(filepath, feature):
    try:
        file_nm = '%s' % filepath + 'version.cfg'
        with open(file_nm, "r") as fp:
            for line in fp:
                if line.split(':')[0] == feature:
                    return line
    except Exception as e:
        AFWF_Error("Failed to get the version. Reason: %s" % e)
    return None


"""
 功能描述: 获取设备ID
    参数: 无
  返回值: 设备ID
   说明:
"""


def getMechineID():
    return getVersion('/opt/info/', 'mechine_id')


"""
 功能描述: 设置APP版本号
    参数: filepath, 版本文件路径,例如：/opt/afwf/
         feature,  特性名称,例如:afwf
  返回值: True， 设置成功
         False，设置失败
     说明: 文件路径不能携带文件名，统一由软件命名为version.cfg,输入路径时需要携带目录最后一个反斜杠。
          此接口用来汇总单个子软件版本信息到/opt/info/version.cfg中，用于安装盘制作时调用。
          设备ID和总软件版本号不需要再设置，当调用相关接口时，这些信息已经写入/opt/info/version.cfg中。
"""


def setSoftVersion(feature, filepath):
    try:
        bias_add = False
        os.system('mv /opt/info/version.cfg /opt/info/version.cfg.bak')
        with open('/opt/info/version.cfg.bak', "r") as fr:
            with open('/opt/info/version.cfg', "a") as fw:
                for line in fr:
                    if line.split(':')[0] == feature:
                        bias_add = True
                        line = getVersion(filepath, feature)
                    fw.write(line)
                if bias_add is False:
                    line = getVersion(filepath, feature)
                    fw.write(line)
        os.system('rm /opt/info/version.cfg.bak')
    except Exception as e:
        AFWF_Error("Failed to set the soft version. Reason: %s" % e)
        return False
    return True


if __name__ == "__main__":
    print(setMechineID('/opt/info/', 'CN.BJ.China Mobile.007'))
    print(getMechineID())
    print(setFeatureVersion('/opt/afwf/config/',
                            'afwf',
                            '1.1.1.1(base)',
                            'Built on Ubuntu',
                            'running on Ubuntu 14.04.5 (64 bit)'))
    print(setDependOnVersion('/opt/afwf/config/', 'DPDK', '18.18'))
    print(setSoftVersion('afwf', '/opt/afwf/config/'))
    print(setFeatureVersion('/opt/info/',
                            'APP',
                            '1.1.1.170726(release)',
                            'Built on Ubuntu',
                            'running on Ubuntu 14.04.5 (64 bit)'))
