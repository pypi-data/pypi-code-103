# -*- coding: utf-8 -*-
import logging
import sys
from os import makedirs
from os.path import dirname, exists

__all__ = [
    'get_logger'
]


def get_logger(name=None, log_path="", log_level="INFO", log_format='%(asctime)s - %(levelname)s - %(process)d - %(filename)s - %(name)s - %(lineno)d - %(module)s - %(message)s', log_enabled=True, log_to_console=True, log_to_file=True):
    """"""
    if not name: name = __name__

    logger = logging.getLogger(name)
    logger.handlers.clear()
    log_level = getattr(logging, log_level) if isinstance(log_level, str) else log_level
    logger.setLevel(log_level)

    # 输出到控制台
    if log_enabled and log_to_console:
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setLevel(level=log_level)
        formatter = logging.Formatter(log_format)
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)

    # 输出到文件
    if log_enabled and log_to_file:
        # 如果路径不存在，创建日志文件文件夹
        log_dir = dirname(log_path)
        if not exists(log_dir): makedirs(log_dir)
        # 添加 FileHandler
        file_handler = logging.FileHandler(log_path, encoding='utf-8')
        file_handler.setLevel(level=log_level)
        formatter = logging.Formatter(log_format)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger
