# -*- coding: utf-8 -*-
"""
为正在跟踪的跟踪实现全局缓存
"""

import sys
import threading
import weakref
import traceback
import logging

try:
    import thread
except ImportError:
    import _thread as thread

from fast_tracker.core.config import global_settings

_logger = logging.getLogger(__name__)


def current_task(asyncio):
    # asyncio是 asyncio包，这里没有在文件头显示导入该包，但是在用的时候用了模块缓存隐式导入
    # 返回当前正在执行的任务，这里涉及到异步框架
    if not asyncio:
        return

    current_task = getattr(asyncio, 'current_task', None)
    if current_task is None:
        current_task = getattr(asyncio.Task, 'current_task', None)

    try:
        return current_task()
    except:
        pass


def get_event_loop(task):
    """

    :param asyncio.Task task:
    :return:
    """
    #  获取循环事件
    get_loop = getattr(task, 'get_loop', None)
    if get_loop:
        return get_loop()
    else:
        return getattr(task, '_loop', None)


class cached_module(object):
    """
    缓存的模块
    """

    def __init__(self, module_path, name=None):
        self.module_path = module_path
        self.name = name or module_path

    def __get__(self, instance, owner=None):
        if instance is None:
            return self
        #  sys.modules是一个全局字典，该字典是python启动后就加载在内存中。每当程序员导入新的模块，sys.modules都将记录这些模块。
        #  字典sys.modules对于加载模块起到了缓冲的作用。当某个模块第一次导入，字典sys.modules将自动记录该模块。当第二次再导入该模块时，
        #  python会直接到字典中查找，从而加快了程序运行的速度
        module = sys.modules.get(self.module_path)  # 获取模块后就可以直接用了，不用在import
        if module:
            instance.__dict__[self.name] = module
            return module


class TraceCache(object):
    asyncio = cached_module("asyncio")
    greenlet = cached_module("greenlet")

    def __init__(self):
        self._cache = weakref.WeakValueDictionary()

    def current_thread_id(self):
        """
         获取当前线程ID
        """
        if self.greenlet:
            # greenlet框架
            current = self.greenlet.getcurrent()
            if current is not None and current.parent:
                return id(current)

        if self.asyncio:
            #  asyncio框架
            task = current_task(self.asyncio)
            if task is not None:
                return id(task)
        return thread.get_ident()

    def current_transaction(self):
        """
        如果该线程缓存了事物对象，返回事物对象
        """

        trace = self._cache.get(self.current_thread_id())
        return trace and trace.transaction

    def current_trace(self):
        return self._cache.get(self.current_thread_id())

    def active_threads(self):
        """
        返回活跃线程信息
        :return:
        """
        #  返回一个字典，将每个线程的标识符映射到调用该函数时该线程中当前活动的最顶层堆栈帧
        for thread_id, frame in sys._current_frames().items():
            trace = self._cache.get(thread_id)
            transaction = trace and trace.transaction
            if transaction is not None:
                if transaction.background_task:  # 如果是后台队列任务，非Web事物
                    yield transaction, thread_id, 'BACKGROUND', frame
                else:
                    yield transaction, thread_id, 'REQUEST', frame  # Web事物
            else:

                # 代理线程对象不一定总是存在
                thread = threading._active.get(thread_id)
                if thread is not None and thread.getName().startswith('NR-'):
                    yield None, thread_id, 'AGENT', frame
                else:
                    yield None, thread_id, 'OTHER', frame

        debug = global_settings().debug

        #  启用协程分析
        if debug.enable_coroutine_profiling:
            for thread_id, trace in self._cache.items():
                transaction = trace.transaction
                if transaction and transaction._greenlet is not None:
                    gr = transaction._greenlet()
                    if gr and gr.gr_frame is not None:
                        if transaction.background_task:
                            yield (transaction, thread_id, 'BACKGROUND', gr.gr_frame)
                        else:
                            yield (transaction, thread_id, 'REQUEST', gr.gr_frame)

    def save_trace(self, trace):
        """
            将追踪信息保存在当前运行的线程ID下
        """

        thread_id = trace.thread_id

        if (thread_id in self._cache and
                self._cache[thread_id].root is not trace.root):
            _logger.error('运行时检测到错误.尝试来保存非活跃事物的追踪.可将此问题报告给天眼团队以获得支持.\n%s',
                          ''.join(traceback.format_stack()[:-1]))

            raise RuntimeError('事物已经激活')

        self._cache[thread_id] = trace

        trace._greenlet = None

        if hasattr(sys, '_current_frames'):
            if thread_id not in sys._current_frames():
                if self.greenlet:
                    trace._greenlet = weakref.ref(self.greenlet.getcurrent())

                if self.asyncio and not hasattr(trace, '_task'):
                    task = current_task(self.asyncio)
                    trace._task = task

    def pop_current(self, trace):
        """在当前的线程ID下还原跟踪的父级执行线程."""

        if hasattr(trace, '_task'):
            delattr(trace, '_task')

        thread_id = trace.thread_id
        parent = trace.parent
        self._cache[thread_id] = parent

    def drop_trace(self, trace):
        """删除指定的跟踪，确认它是实际保存在当前执行线程下.
        """

        if hasattr(trace, '_task'):
            trace._task = None

        thread_id = trace.thread_id

        if thread_id not in self._cache:
            _logger.error('运行时检测错误.尝试删除跟踪,但没有任何跟踪.可将此问题报告给天眼团队以获得支持.\n%s',
                          ''.join(traceback.format_stack()[:-1]))

            raise RuntimeError('没有活跃的追踪')

        current = self._cache.get(thread_id)

        if trace is not current:
            _logger.error('运行时检测错误.尝试删除跟踪,但不是当前线程的追踪.可将此问题报告给天眼团队以获得支持.\n%s',
                          ''.join(traceback.format_stack()[:-1]))

            raise RuntimeError('不是当前线程的追踪')

        del self._cache[thread_id]
        trace._greenlet = None



_trace_cache = TraceCache()


def trace_cache():
    return _trace_cache


def greenlet_loaded(module):
    _trace_cache.greenlet = module


def asyncio_loaded(module):
    _trace_cache.asyncio = module
