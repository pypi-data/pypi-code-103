#!/usr/bin/python3
from datetime import datetime
import logging
import shutil
import sys

try:
    from ..backend.constants import ConfigDirs, ConfigFiles
except (ValueError, ImportError):
    from backend.constants import ConfigDirs, ConfigFiles

logging.addLevelName(60, "QUIET")


class ConsoleHandler(logging.StreamHandler):
    VERBOSE = logging.INFO

    def __init__(self):
        super().__init__()
        formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s : %(message)s",
                                      datefmt="%H:%M:%S")
        self.setFormatter(formatter)
        self.setLevel(self.VERBOSE)


class FileHandler(logging.FileHandler):
    def __init__(self):
        super().__init__(filename=ConfigFiles.LOG)
        formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s, %(funcName)s() : %(message)s",
                                      datefmt="%d/%m/%Y %H:%M:%S")
        self.setFormatter(formatter)
        self.setLevel(logging.DEBUG)


def new(name: str) -> logging.Logger:
    """ Returns a per-module logger instance"""
    ConfigDirs.LOGS.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger(name)
    logger.addHandler(ConsoleHandler())
    logger.addHandler(FileHandler())
    logger.setLevel("DEBUG")
    logger.propagate = False
    logger.disable_existing_loggers = False
    return logger


def _exception(type_, value, tb):
    """ Global exception handler. Saves crash logs with traceback """
    try:
        log = new(__name__)
        while "tb_next" in dir(tb):  # Log traceback stack
            frame = tb.tb_frame
            code = frame.f_code
            log.critical(f"file '{code.co_filename}' in {code.co_name} (line {frame.f_lineno})")
            tb = tb.tb_next
        log.critical(f"{type_} {value}".rstrip())  # Log exception

        # Save crash log
        now = datetime.now()
        date = f"{now.year:02d}-{now.month:02d}-{now.day:02d}"
        time = f"{now.hour:02d};{now.minute:02d};{now.second:02d}"
        logfile = ConfigDirs.LOGS / f"crash {date} {time}.log"
        shutil.copy(ConfigFiles.LOG, logfile)
        print(f"\n    //  \\\\\n   _\\\\()//_   \"{logfile}\"\n  / //  \\\\ \\\n   | \\__/ |\n")
    except Exception:
        pass
    finally:  # Ensures default hook is called
        sys.__excepthook__(type_, value, tb)
        sys.exit(1)


sys.excepthook = _exception
