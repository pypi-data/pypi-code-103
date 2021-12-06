# Copyright (C), 2021, 爱德数智
"""
文件名称: Logger.py
作者: 王震
版本: 1.0
Date: 2021-09-17
Description: 日志记录模块
    级别	何时使用
    DEBUG	详细信息，一般只在调试问题时使用。
    INFO	证明事情按预期工作。
    WARNING	某些没有预料到的事件的提示，或者在将来可能会出现的问题提示。例如：磁盘空间不足。但是软件还是会照常运行。
    ERROR	由于更严重的问题，软件已不能执行一些功能了。
    CRITICAL	严重错误，表明软件已不能继续运行了。
History: /* 历史修改记录 */
<Author>   <Date>   <Version>   <Desc>
 王震     2021-09-17   1.0        创建
"""
import logging
import os
import datetime
import time
import boto3
import threading
import traceback
import socket
logger_out_path = None
logger_out_name = None
logger_obj = None
timer = None
lock = threading.RLock()
run_uuid = socket.gethostname()


def transmission(bucket, out_path, read_path, s3_client):
    s3_client.put_object(Bucket=bucket, Key=out_path,
                         Body=open(read_path, "rb").read())


class Logger(object):
    """日志记录模块.
    可以对日志打印并且记录在文件内
    Raises:
        无.
    """

    CRITICAL = 50
    FATAL = CRITICAL
    ERROR = 40
    WARNING = 30
    WARN = WARNING
    INFO = 20
    DEBUG = 10
    NOTSET = 0  # 日志级别关系映射
    overall_is_try = True  # 全局异常捕获
    overall_level = DEBUG  # 全局记录等级

    def __init__(self, func=None, path=None, file_name=None,file_path = None,
                 clevel=DEBUG, flevel=DEBUG, is_try=None,
                 sav_result=False):
        """初始化日志模块.
        主要对日志的路径和显示等级进行配置.
        Args:
            func：装饰器使用，无需赋值.
            paht：日志生成路径
        Returns:
            返回结果描述.
        Raises:
            无.
        """
        global logger_out_path
        self.func = func
        self.sav_result = sav_result
        self.clevel = clevel
        self.flevel = flevel
        self.is_try = is_try
        if file_path != None:
            self.set_global_file(file_path)
        elif logger_out_path == None:
            if path == "" or path == None:
                default_file_name = os.path.abspath(os.curdir)
                now_time = datetime.datetime.now().strftime('%Y-%m-%d')
                path = str(os.path.abspath(os.curdir)).replace(
                    default_file_name, "")
                path += "logs/" + str(now_time) + "/"
                logger_out_path = path
            if file_name == None:
                file_name = "logs.log"
            self.set_file_name(file_name)

    def set_s3(self, s3_out_path, bucket, endpoint_url,
               aws_access_key_id, aws_secret_access_key, flush_time=10):
        session = boto3.Session(
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
        )
        s3_client = session.client(
            's3', endpoint_url=endpoint_url, use_ssl=True, verify=False)
        self.bucket = bucket
        self.s3_out_path = s3_out_path
        self.flush_time = flush_time
        self.s3_client = s3_client
        global timer
        timer = threading.Timer(
            0, thread_task, [self])
        timer.setDaemon(True)
        timer.start()

    def set_global_configuration(self,out_path, file_name):
        global logger_out_path
        global logger_obj
        global logger_out_name
        logger_out_path = out_path
        logger_out_name = file_name
        out_path = logger_out_path + file_name
        logger_obj = logging.getLogger(out_path)
        if not os.path.exists(out_path):
            os.makedirs(os.path.dirname(out_path), exist_ok=True)
        logger_obj.setLevel(logging.DEBUG)
        fmt = logging.Formatter(
            '[%(asctime)s] - %(levelname)s - %(message)s', '%Y-%m-%d %H:%M:%S')
        #设置CMD日志
        sh = logging.StreamHandler()
        sh.setFormatter(fmt)
        sh.setLevel(self.clevel)
        #设置文件日志
        fh = logging.FileHandler(out_path)
        fh.setFormatter(fmt)
        fh.setLevel(self.flevel)
        logger_obj.addHandler(sh)
        logger_obj.addHandler(fh)
        logger_obj.debug("【日志系统】日志储存目录：" + out_path)
    
    def set_global_file(self,file_path, file_name=None):
        default_file_name = os.path.basename(file_path)
        now_time = datetime.datetime.now().strftime('%Y-%m-%d')
        path = str(file_path).replace(default_file_name, "")
        path += "logs/" + str(now_time) + "/"
        if file_name == None:
            file_name = "logs.log"
        self.set_global_configuration(path, file_name)

    def __call__(self, *args, **kwargs):  # 接受函数
        def inner(*args, **kwargs):
            self.log("[" + self.func.__name__ + "] - " + "开始执行", self.clevel)
            self.log("[" + self.func.__name__ + "] - " + "输入参数：" +
                     str(args) + str(kwargs), self.clevel)
            starttime = time.time()
            result = None
            if self.is_try == None:
                is_try = self.overall_is_try
            else:
                is_try = self.is_try
            if is_try:
                try:
                    result = self.func(*args, **kwargs)
                except Exception as e:
                    self.log("[" + self.func.__name__ + "] - " +
                             "执行过程中发生异常", self.ERROR)
                    self.log("[" + self.func.__name__ +
                             "] - 异常原因：" + traceback.format_exc(), self.ERROR)
                    raise e
            else:
                result = self.func(*args, **kwargs)
            endtime = time.time()
            millisecond = endtime - starttime
            self.log("[" + self.func.__name__ + "] - " +
                     "执行完毕 - 执行时间：" + str(millisecond) + " 秒", self.clevel)
            if self.sav_result:
                self.log("[" + self.func.__name__ + "] - " +
                         "执行结果：" + str(result), self.clevel)
            return result
        if self.func == None:
            self.func = args[0]  # 带参数的装饰器
            return inner
        else:
            return inner(*args, **kwargs)  # 不带参数的装饰器

    def set_file_name(self, file_name=None):
        global logger_out_name
        global logger_out_path
        global logger_obj
        if file_name != None:
            if logger_obj != None:
                logger_obj.debug("设定任务：" + file_name)
            global timer
            if timer != None:
                lock.acquire()
                try:
                    timer.cancel()
                    timer = None
                finally:
                    lock.release()
                timer = threading.Timer(
                    self.flush_time, thread_task, [self])
                timer.setDaemon(True)
                timer.start()
            logger_out_name = file_name
        out_path = logger_out_path + logger_out_name
        logger_obj = logging.getLogger(out_path)
        if logger_obj.handlers == []:
            self.set_global_configuration(logger_out_path, logger_out_name)

    def get_path(self):
        """获取日志记录路径.
        获取当前类记录日志所在位置.
        Args:
            无
        Returns:
            日志路径.
        Raises:
            无.
        """
        global logger_out_name
        global logger_out_path
        global logger_obj
        out_path = logger_out_path + logger_out_name
        return out_path

    def debug(self, message, *args, **kwargs):
        """debug.
        记录严重性为 "调试" 的 "消息".
        Args:
            message：异常信息.
        Returns:
            无.
        Raises:
            无.
        """
        logger_obj.debug(message, *args, **kwargs)

    def info(self, message):
        """info.
        记录严重性为 "信息" 的 "消息".
        Args:
            message：异常信息.
        Returns:
            无.
        Raises:
            无.
        """
        logger_obj.info(message)

    def warn(self, message):
        """warn.
        记录严重性为 "警告" 的 "消息".
        Args:
            message：异常信息.
        Returns:
            无.
        Raises:
            无.
        """
        logger_obj.warn(message)

    def error(self, message):
        """error.
        记录严重性为 "错误" 的 "消息".
        Args:
            message：异常信息.
        Returns:
            无.
        Raises:
            无.
        """
        logger_obj.error(message)

    def critical(self, message):
        """critical.
        记录严重性为 "奔溃" 的 "消息".
        Args:
            message：异常信息.
        Returns:
            无.
        Raises:
            无.
        """
        logger_obj.critical(message)

    def log(self, message, level=None):
        """log.
        记录严重性为指定信息，根据level进行自动分配等级.
        如果没有给level分配消息等级，则会使用overall_level全局消息等级
        Args:
            message：异常信息.
            level：消息等级
        Returns:
            无.
        Raises:
            无.
        """
        if level == None:
            level = self.overall_level
        if level == self.DEBUG:
            self.debug(message)
        elif level == self.INFO:
            self.info(message)
        elif level == self.WARN:
            self.warn(message)
        elif level == self.ERROR:
            self.error(message)
        elif level == self.CRITICAL:
            self.critical(message)
        else:
            self.info(message)
    def get_S3_Path(self):
        now_time = datetime.datetime.now().strftime('%Y-%m-%d')
        return self.s3_out_path + \
            str(now_time) + "/" + str(run_uuid) + "/" + logger_out_name

def thread_task(logger: Logger, is_stop=False):
    lock.acquire()
    try:
        if logger_out_name == None:
            return
        out_path = logger.get_S3_Path()
        read_path = logger_out_path + logger_out_name
        transmission(logger.bucket, out_path, read_path, logger.s3_client)
    finally:
        global timer
        if timer != None and not is_stop:
            timer = threading.Timer(
                logger.flush_time, thread_task, [logger])
            timer.setDaemon(True)
            timer.start()
        lock.release()
