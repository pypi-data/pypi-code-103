# !/usr/bin/env python
# coding:utf-8

"""
Copyright (c) 2021. quinn.7@foxmail.com All rights reserved.
Based on the Apache License 2.0 open source protocol.

作者 cat7
邮箱 quinn.7@foxmail.com

"""


__all__ = ['RunPool']


import gc
import psutil

from multiprocessing.dummy import Pool
from multiprocessing.dummy import Manager

from rains.common.log import Log


class RunPool(object):
    """
    [ 运行池 ]
    * 无

    """

    _log = Log()
    """ 日志服务 """

    _pool: Pool
    """ 进程池 """

    _core_queue: Manager().Queue
    """ 核心队列 """

    _task_queue: Manager().Queue
    """ 任务队列 """

    _pool_state: bool
    """ 进程池运作状态 """

    _sign_task_count: int
    """ 注册的任务数量 """

    _max_quantity_pool: int = 3
    """ 进程最大阈值 """

    _max_quantity_core: int = 5
    """ 核心最大阈值 """

    _max_quantity_task: int = 20
    """ 任务最大阈值 """

    _lock_from_core_queue: Manager().Lock
    """ 核心队列互斥锁 """

    _lock_from_task_queue: Manager().Lock
    """ 任务队列互斥锁 """

    _lock_from_pool_state: Manager().Lock
    """ 进程池运作状态互斥锁 """

    _lock_from_task_count: Manager().Lock
    """ 注册的任务数量互斥锁 """

    def __init__(self, cores: list, tasks: list):
        """
        [ 初始化 ]
        * 无

        [ 必要参数 ]
        * cores (list) : 核心列表
        * tasks (list) : 任务列表

        [ 可选参数 ]
        * 无

        [ 返回内容 ]
        * 无

        """

        # 初始化赋值
        self._initialization()

        # 遍历核心列表
        for core in cores:
            self._core_queue.put(core)

        # 遍历任务列表
        for task in tasks:
            self._task_queue.put(task)
            self._sign_task_count += 1

    def _initialization(self):
        """
        [ 初始化进程池 ]
        * 无

        [ 必要参数 ]
        * 无

        [ 可选参数 ]
        * 无

        [ 返回内容 ]
        * 无

        """

        mgr = Manager()
        self._sign_task_count = 0

        # 创建队列
        self._core_queue = mgr.Queue(maxsize=self._max_quantity_core)
        self._task_queue = mgr.Queue(maxsize=self._max_quantity_task)

        # 创建互斥锁
        self._lock_from_core_queue = mgr.Lock()
        self._lock_from_task_queue = mgr.Lock()
        self._lock_from_pool_state = mgr.Lock()
        self._lock_from_task_count = mgr.Lock()

        # 创建进程池
        self._pool = Pool(self._max_quantity_pool)

    def running(self):
        """
        [ 运行 ]
        * 无

        [ 必要参数 ]
        * 无

        [ 可选参数 ]
        * 无

        [ 返回内容 ]
        * 无

        """

        # 获取注册的任务数量
        with self._lock_from_task_count:
            count = self._sign_task_count

        # 存在任务则执行循环
        if count > 0:

            self._pool_state = True

            for i in range(count):
                # 强制 GC 回收垃圾避免内存溢出
                gc.collect()

                # 驱动冷启动时会占用大量的 CPU 资源，为避免因为 CPU 占用率过高导致进程启动异常
                # 每隔 2 秒检查 CPU 占用率，只有 CPU 占用率少于 50 时才会启动进程
                while True:
                    if psutil.cpu_percent(2) < 50:
                        self._pool.apply_async(func=self._emit)
                        break

            # 轮询进程执行情况，当所有进程都执行完毕后，退出程序
            while True:
                if self._pool_state and self._sign_task_count == 0:
                    self._pool_state = False
                    break

        gc.collect()

    def _emit(self):
        """
        [ 触发工作流 ]
        * 无

        [ 必要参数 ]
        * 无

        [ 可选参数 ]
        * 无

        [ 返回内容 ]
        * 无

        """

        # 取出队列中的核心与任务
        task = self._task_queue.get()
        core = self._core_queue.get()

        # 执行核心的 running 函数
        r = core.start_task(task)

        # 触发回调
        self._function_call_back()

        # 核心执行完任务后，放回核心队列等待
        with self._lock_from_core_queue:
            self._core_queue.put(core)

        return r

    def _function_call_back(self):
        """
        [ 触发回调 ]
        * 该回调将消耗任务数量。

        [ 必要参数 ]
        * 无

        [ 可选参数 ]
        * 无

        [ 返回内容 ]
        * 无

        """

        with self._lock_from_task_count:
            self._sign_task_count -= 1
