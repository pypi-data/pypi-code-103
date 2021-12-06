#!/usr/bin/env python
# coding=utf-8

import logging
import os
import stat


def checkLogFile(filename):
    if  os.path.exists(filename) is False:
        os.mknod(filename)
        os.chmod(filename, stat.S_IWUSR|stat.S_IRUSR|stat.S_IWGRP|stat.S_IRGRP|stat.S_IWOTH|stat.S_IROTH)


"""
功能描述: afwf模块debug信息打印
   参数: debugString, 提示信息
 返回值: 无
   说明:
"""


def AFWF_Debug(debugString):
    checkLogFile('/opt/afwf/logs/py_proc.log')
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(levelname)s: %(message)s',
                        datefmt='%a, %d %b %Y %H:%M:%S',
                        filename='/opt/afwf/logs/py_proc.log',
                        filemode='a')
    logging.debug(debugString)


"""
 功能描述: afwf模块error信息打印
    参数: errorString, 错误信息
  返回值: 无
    说明:
"""


def AFWF_Error(errorString):
    checkLogFile('/opt/afwf/logs/py_proc.log')
    logging.basicConfig(level=logging.ERROR,
                        format='%(asctime)s %(levelname)s: %(message)s',
                        datefmt='%a, %d %b %Y %H:%M:%S',
                        filename='/opt/afwf/logs/py_proc.log',
                        filemode='a')
    logging.error(errorString)


"""
 功能描述: afwf模块info信息打印
    参数: infoString, info信息
  返回值: 无
    说明:
"""


def AFWF_Info(infoString):
    checkLogFile('/opt/afwf/logs/py_proc.log')
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(levelname)s: %(message)s',
                        datefmt='%a, %d %b %Y %H:%M:%S',
                        filename='/opt/afwf/logs/py_proc.log',
                        filemode='a')
    logging.info(infoString)
