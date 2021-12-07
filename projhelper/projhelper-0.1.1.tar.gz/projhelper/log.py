#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import sys

file_info = '''
 @Time    : 18/1/7 13:34
 @Author  : oujianhua
 @mail  : ojhtyy@163.com
 引用时, 要把本第一个 import , 以免打印不出 , 如git 
 '''

import logging
from  logging import config

#如果日志目录不存在, 在当前工作目录下创建Log文件夹 ,之后如果程序使用 os.chdir 切换目录 , 也不影响


#通过调用时指定配置文件 调用时如： main.py dev|prod
try:
    env = sys.argv[1]
except BaseException as e:
    env='prod'

log_dir="logs"  #日志目录在运行路径下
work_dir=os.getcwd()
if not log_dir in os.listdir(work_dir):
     os.mkdir(os.path.join(work_dir,"logs"))
#获取配置文件
conf_file_full_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'conf','logging.cfg')
config.fileConfig(conf_file_full_path)

#除了开发时 ,其他情况的日志都输出到文件
if env=='dev':
    logger = logging.getLogger('console')
else:
    logger = logging.getLogger('file')
if __name__=='__main__':
    #log = logging.getLogger('root') #获取 配置文件中的 root节点 通过root节点来处理日志
    #errorlog=logging.getLogger("error")  #通过配置文件中的error 节点处理日志 ,处理的信息会交给 root 再次处理
    #errorlog.error("9898989889") #传给  error 这个 logger 处理 后, 又给到 root再次处理
    logger.error("444444444")
    logger.info("iiiiiiiiiiii")

