# -*- coding: utf-8 -*-

# @File  : test.py
# @Author: Lomo
# @Site  : lomo.space
# @Date  : 2021-12-04
# @Desc  : 单测

import os
import sys
import unittest
import random

# 命令行运行时必须在改目录下执行该脚本否则会导致日志文件到其它层级或找不到目录, 所以在项目根目录下添加运行脚本统一调用入口
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pkg import decorator_tools


@decorator_tools.LogTools(file_name='sum')
def sum_two(a=1, b=2):
    sum_ = a + b
    return sum_


class TestDecoratorTools(unittest.TestCase):
    def test_demo(self):
        self.assertEqual('Lomo'.upper(), 'LOMO')

    def test_log_tools_by_name(self):
        @decorator_tools.LogTools()
        def log_demo():
            print('test log tools decorator...')
        log_demo()

    def test_log_tools(self):
        @decorator_tools.LogTools(file_name='log_test_2021')
        def log_demo():
            return 'test log tools decorator...with user define log_file_name'

        log_demo()

    def test_sum_two(self):
        self.assertEqual(sum_two(10, 10), 20)

    def test_timer(self):
        @decorator_tools.FuncTimer()
        def demo():
            import time
            time.sleep(1)
        demo()

    def test_loop_run(self):
        @decorator_tools.FuncTimer()
        @decorator_tools.LogTools(file_name='loop_test')
        @decorator_tools.LoopExecute(loop=5, sleep=0)
        def run_demo():
            return random.randint(1, 30) + random.randint(30, 50)
        run_demo()


if __name__ == '__main__':
    unittest.main()
