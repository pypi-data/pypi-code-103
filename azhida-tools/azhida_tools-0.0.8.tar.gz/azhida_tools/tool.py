# -*- coding: utf-8 -*-

import time
import logging
import inspect
import os


def test(str='abcd'):
    print(str)
    print(__file__)
    return str


def datetime():
    # 时间日期格式 2000-01-01 00:00:00
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())


# 返回 调用者的方法名
def get_function_name():
    curframe = inspect.currentframe()
    calframe = inspect.getouterframes(curframe, 2)
    caller_name = calframe[1][3]
    # print('caller name:', caller_name)
    return caller_name


# 返回 调用者的文件目录
def get_caller_path():
    caller_path = os.path.abspath(inspect.getframeinfo(inspect.stack()[-1][0])[0])
    print('current_path : ', caller_path)
    caller_path = os.path.split(caller_path)
    return caller_path


# 自定义日志
def log(message, **params):
    # 拿到调用者的文件目录
    caller_path = os.path.abspath(inspect.getframeinfo(inspect.stack()[-1][0])[0])
    caller_path = os.path.split(caller_path)[0]

    log_file_name = 'demo.log'
    if 'log_file_name' in params:
        log_file_name = params['log_file_name']

    # 日志文件名： demo-2020-01-01.log
    rq = time.strftime('%Y-%m-%d', time.localtime(time.time()))
    log_file_name = log_file_name.replace('.log', '')
    log_file_name = caller_path + f'/logs/{log_file_name}-{rq}.log'
    # 创建日志文件
    touch_file(log_file_name)

    logger = logging.getLogger(__name__)
    handler = logging.FileHandler(log_file_name, encoding='utf-8', mode='a')
    formatter = logging.Formatter('%(asctime)s - %(name)s-%(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    class_name = ''
    if 'class_name' in params:
        class_name = params['class_name']

    if 'caller_name' in params:
        caller_name = params['caller_name']
    else:
        # 获取调用者的方法名
        curframe = inspect.currentframe()
        calframe = inspect.getouterframes(curframe, 2)
        caller_name = calframe[1][3]
        if caller_name == '<module>':
            caller_name = ''

    logger.error(f'{datetime()} , {class_name}::{caller_name}() => {message}')
    # 如果不删除，将会把日志同时打印到所有添加过的日志文件里
    logger.removeHandler(handler)


# 创建文件，file_name 为 绝对路径
def touch_file(file_name):
    # 判断文件是否存在
    if not os.path.isfile(file_name):
        res = os.path.split(file_name)
        if not os.path.exists(res[0]):
            # 目录不存在，先创建目录
            os.makedirs(res[0])

        # 调用系统命令行来创建文件
        os.system(r"touch {}".format(file_name))

    return True
