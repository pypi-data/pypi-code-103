from loguru import logger


class Logger(object):
    """
    Desc: Encapsulation of requests library
    Date: 20191127
    Author: Linty Liu (Tingli)
    Email: liu.tingli@outlook.com
    """
    _logger = None
    _file_name = None
    _format = "{time} - {name} - {level} - {message}"

    def __init__(self, log_path):
        """
        构造方法
        :param log_path:
        """
        # log_path：日志存放路径
        # 文件命名

        self._file_name = log_path

        self._logger = logger
        self._logger.add(
            log_path,
            level="DEBUG",
            format=self._format,
            rotation="10:00",
            retention="15 days",
            encoding="UTF8",
            enqueue=True)

    def info(self, message):
        """
        添加信息日志
        :param message:
        :return:
        """
        self._logger.info(message)

    def warning(self, message):
        """
        添加警告日志
        :param message:
        :return:
        """
        self._logger.warning(message)

    def error(self, message):
        """
        添加错误日志
        :param message:
        :return:
        """
        self._logger.error(message)


def info(msg, log: Logger):
    """
    记录日志
    :param log:
    :param msg:
    :return:
    """
    if log is not None and isinstance(log, Logger):
        log.info(msg)


def error(msg, log: Logger):
    """
    记录错误
    :param log:
    :param msg:
    :return:
    """
    if log is not None and isinstance(log, Logger):
        log.error(msg)


def build_logger(log_path):
    """
    build logger
    :param log_path:
    :return:
    """
    return Logger(
        log_path=log_path
    )
