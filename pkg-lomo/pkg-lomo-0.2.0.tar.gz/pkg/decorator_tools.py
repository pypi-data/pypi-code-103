# -*- coding: utf-8 -*-

# @File  : decorator_tools.py
# @Author: Lomo
# @Site  : lomo.space
# @Date  : 2021-12-04
# @Desc  : 常用工具函数(装饰器方式调用)

import os
import datetime
import time
import logging
from functools import wraps

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# root_path = os.path.abspath(os.path.join(os.getcwd(), '..'))  # 当前 py 在 pkg_lomo/pkg/ 目录下, 项目根目录 pkg_lomo


class LogTools(object):
    def __init__(self, root_path=None, file_name=None):
        if root_path:
            self.path_prefix = root_path + '/logs/'
        else:
            self.path_prefix = 'logs/'
        if not file_name:
            self.file_name = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S') + '.log'
        else:
            self.file_name = file_name + '.log'
        logging.info("日志文件名: {0}".format(self.file_name))
        self.log_name = self.path_prefix + self.file_name
        if not os.path.exists(self.path_prefix):
            os.mkdir(self.path_prefix)
        os.system('cd {0} && touch {1}'.format(self.path_prefix, self.file_name))

    def __call__(self, func):
        @wraps(func)
        def wrapper_function(*args, **kwargs):
            called_msg = LogTools.format_msg(func.__name__ + ' was called.')
            logging.info(called_msg)
            func_res = func(*args, **kwargs)
            func_res_msg = LogTools.format_msg(func.__name__ + '方法执行返回结果: ' + str(func_res))
            logging.info(func_res_msg)
            with open(self.log_name, mode='a', encoding='utf-8') as opened_file:
                opened_file.write(called_msg + '\n')
                opened_file.write(func_res_msg + '\n')
            return func_res
        return wrapper_function

    @staticmethod
    def format_msg(msg):
        c_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        return c_time + ' ' + str(msg)


class FuncTimer(object):
    def __init__(self):
        pass

    def __call__(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            res = func(*args, **kwargs)
            end_time = time.time()
            logging.info('花费时间：{0}秒'.format(end_time - start_time))
            return res
        return wrapper


class LoopExecute(object):
    def __init__(self, loop=1, sleep=0):
        self.loop_count = loop
        self.sleep = sleep

    def __call__(self, func):
        @wraps(func)
        def wrapper_function(*args, **kwargs):
            logging.info(func.__name__ + ' was called.')
            res = list()

            for n in range(self.loop_count):
                func_res = func(*args, **kwargs)
                time.sleep(self.sleep)
                logging.info('{0} 方法第 {1} 次执行返回结果: {2}'.format(func.__name__, n + 1, func_res))
                res.append(func_res)
            return res
        return wrapper_function


class DelayExecute(object):
    def __init__(self, duration=0):
        self.delay_time = duration

