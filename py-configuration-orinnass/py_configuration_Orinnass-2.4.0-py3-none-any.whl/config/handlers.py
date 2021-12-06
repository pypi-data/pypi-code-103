# from pymysql import Connection as pymySQLConnection
# from logging import Handler, LogRecord
#
#
# class DBHandler(Handler):
#     """
#     Обработчик логирования в БД
#     """
#     # TODO: Дописать обработчик
#     def __init__(self, connection: pymySQLConnection, table: str):
#         super().__init__()
#         self.__connection = connection
#         self.__cursor = connection.cursor()
#         self.__table = table
#
#     def emit(self, record: LogRecord) -> None:
#         self.__cursor.execute(f"insert into `{self.__table}` (`logger`, `level_log`, `message`, `time`) "
#                               f"values (%s, %s, %s, %s)", [record.name, record.levelname, record.message, record.asctime])
#         self.__connection.commit()
from logging.handlers import RotatingFileHandler as RotatingFileHandlerWithOutZip, \
    TimedRotatingFileHandler as TimedRotatingFileHandlerWithOutZip
from os import rename, remove
from os.path import exists as path_exists
import gzip
import time


class RotatingFileHandler(RotatingFileHandlerWithOutZip):
    """
    Класс ротации логов по размеру, с возможностью сжатия файлов
    """
    @staticmethod
    def __rotator__(source, dest):
        with gzip.open(f"{dest}.gz", mode='w') as compression_file:
            with open(source, mode='rb') as source_file:
                compression_file.write(source_file.read())
        remove(source)

    rotator = __rotator__

    def __init__(self, filename, mode='a', max_bytes=0, backup_count=0,
                 encoding=None, delay=False, errors=None, compression: bool = False):
        super().__init__(filename, mode, max_bytes, backup_count, encoding, delay, errors)
        if not compression:
            self.rotator = None
            self.doRollover = super(RotatingFileHandler, self).doRollover

    def doRollover(self):
        """
        Do a rollover, as described in __init__().
        """
        if self.stream:
            self.stream.close()
            self.stream = None
        if self.backupCount > 0:
            for i in range(self.backupCount - 1, 0, -1):
                sfn = self.rotation_filename(f"{self.baseFilename}.{i}.gz")
                dfn = self.rotation_filename(f"{self.baseFilename}.{i + 1}.gz")

                if path_exists(sfn):
                    if path_exists(dfn):
                        remove(dfn)
                    rename(sfn, dfn)
            dfn = self.rotation_filename(self.baseFilename + ".1")
            if path_exists(dfn):
                remove(dfn)
            self.rotate(self.baseFilename, dfn)
        if not self.delay:
            self.stream = self._open()


class TimedRotatingFileHandler(TimedRotatingFileHandlerWithOutZip):
    # TODO: доделать класс
    def __init__(self, filename, when='h', interval=1, backup_count=0, encoding=None, delay=False,
                 utc=False, at_time=None, errors=None, compression: bool = False):
        super().__init__(filename, when, interval, backup_count, encoding, delay,
                         utc, at_time, errors)
        if not compression:
            self.rotator = None
            self.doRollover = super(TimedRotatingFileHandler, self).doRollover

    def doRollover(self):
        """
        do a rollover; in this case, a date/time stamp is appended to the filename
        when the rollover happens.  However, you want the file to be named for the
        start of the interval, not the current time.  If there is a backup count,
        then we have to get a list of matching filenames, sort them and remove
        the one with the oldest suffix.
        """
        if self.stream:
            self.stream.close()
            self.stream = None
        # get the time that this sequence started at and make it a TimeTuple
        currentTime = int(time.time())
        dstNow = time.localtime(currentTime)[-1]
        t = self.rolloverAt - self.interval
        if self.utc:
            timeTuple = time.gmtime(t)
        else:
            timeTuple = time.localtime(t)
            dstThen = timeTuple[-1]
            if dstNow != dstThen:
                if dstNow:
                    addend = 3600
                else:
                    addend = -3600
                timeTuple = time.localtime(t + addend)
        dfn = self.rotation_filename(self.baseFilename + "." +
                                     time.strftime(self.suffix, timeTuple))
        if path_exists(dfn):
            remove(dfn)
        self.rotate(self.baseFilename, dfn)
        if self.backupCount > 0:
            for s in self.getFilesToDelete():
                remove(s)
        if not self.delay:
            self.stream = self._open()
        newRolloverAt = self.computeRollover(currentTime)
        while newRolloverAt <= currentTime:
            newRolloverAt = newRolloverAt + self.interval
        #If DST changes and midnight or weekly rollover, adjust for this.
        if (self.when == 'MIDNIGHT' or self.when.startswith('W')) and not self.utc:
            dstAtRollover = time.localtime(newRolloverAt)[-1]
            if dstNow != dstAtRollover:
                if not dstNow:  # DST kicks in before next rollover, so we need to deduct an hour
                    addend = -3600
                else:           # DST bows out before next rollover, so we need to add an hour
                    addend = 3600
                newRolloverAt += addend
        self.rolloverAt = newRolloverAt

    @staticmethod
    def __rotator__(source, dest):
        with gzip.open(f"{dest}.gz", mode='w') as compression_file:
            with open(source, mode='rb') as source_file:
                compression_file.write(source_file.read())
        remove(source)

    rotator = __rotator__
