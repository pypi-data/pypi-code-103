# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function

import datetime
import logging
import logging.handlers
import pytz
from urllib.parse import urljoin
from suanpan.g import g
from suanpan.api import api


class Formatter(logging.Formatter):
    def formatTime(self, record, datefmt=None):
        dt = datetime.datetime.fromtimestamp(record.created)
        try:
            tz = pytz.timezone(self.tzName)
        except Exception:  # pylint: disable=broad-except
            tz = pytz.utc
        converted = dt.astimezone(tz)
        return converted.strftime(
            datefmt) if datefmt else converted.isoformat()

    def __init__(
        self,
        fmt="%(asctime)s :: %(levelname)-10s :: %(message)s",
        datefmt=None,
        timezone="UTC",
    ):
        super().__init__(fmt=fmt, datefmt=datefmt)
        self.tzName = timezone


class Logger(logging.Logger):
    FORMATTER = Formatter(timezone=g.timezone)
    STREAM_LOG_LEVEL = logging.DEBUG
    LOGKIT_LOG_LEVEL = logging.DEBUG
    LOGKIT_URI = g.logkitUri
    LOGKIT_NAMESPACE = g.logkitNamespace
    LOGKIT_PATH = g.logkitPath
    LOGKIT_EVENTS_APPEND = g.logkitEventsAppend

    def __init__(self, name="suanpan"):
        super().__init__(name=name)
        logging.raiseExceptions = False
        self.addStreamHandler(
            level=logging.DEBUG if g.debug else logging.INFO)
        if self.LOGKIT_URI:
            self.addLogkitHandler(
                level=logging.getLevelName(g.logkitLogsLevel.upper()))

    def addStreamHandler(self, level=STREAM_LOG_LEVEL, formatter=FORMATTER):
        streamHandler = logging.StreamHandler()
        streamHandler.setLevel(level)
        streamHandler.setFormatter(formatter)
        self.addHandler(streamHandler)
        return streamHandler

    def addLogkitHandler(
        self,
        level=LOGKIT_LOG_LEVEL,
        formatter=FORMATTER,
        uri=LOGKIT_URI,
        namespace=LOGKIT_NAMESPACE,
        socketio_path=LOGKIT_PATH,
        event=LOGKIT_EVENTS_APPEND,
    ):
        url = urljoin(uri, namespace)
        logkitHandler = LoggerLogkitHandler(url, namespace, socketio_path,
                                            event)
        logkitHandler.setLevel(level)
        logkitHandler.setFormatter(formatter)
        self.addHandler(logkitHandler)
        return logkitHandler

    def makeRecord(
        self,
        name,
        level,
        fn,
        lno,
        msg,
        args,
        exc_info,
        func=None,
        extra=None,
        sinfo=None,
    ):
        extra = {
            "extra": {
                "app": g.appId,
                "node": g.nodeId,
                **(extra or {})
            }
        }
        return super().makeRecord(name, level, fn, lno, msg, args, exc_info,
                                  func, extra, sinfo)


class LoggerLogkitHandler(logging.Handler):
    def __init__(self, url, namespace, socketio_path, event):
        super().__init__()
        self.client = None
        self.url = url
        self.namespace = namespace
        self.socketio_path = socketio_path
        self.event = event

    def makeClient(self):
        return api.sioClient(self.url,
                             namespaces=self.namespace,
                             socketio_path=self.socketio_path,
                             wait_timeout=3)

    def send(self, msg):
        if not api.client:
            self.makeClient()
        elif not api.client:
            self.client.disconnect()
            self.client = self.makeClient()
        api.client.emit(self.event, data=msg, namespace=self.namespace)

    def makePickle(self, record):
        app = record.extra.pop("app")
        data = (app, {
            "level":
            record.levelname,
            "title":
            record.message,
            "data":
            record.extra,
            "time":
            datetime.datetime.now(datetime.timezone.utc).isoformat(),
        })
        return data

    def emit(self, record):
        try:
            msg = self.makePickle(record)
            self.send(msg)
        except Exception:  # pylint: disable=broad-except
            self.handleError(record)

    def close(self):
        """
        Closes the socket.
        """
        self.acquire()
        try:
            if api.client:
                api.client.disconnect()
                api.client = None
            super().close()
        finally:
            self.release()


logger = Logger("suanpan")
