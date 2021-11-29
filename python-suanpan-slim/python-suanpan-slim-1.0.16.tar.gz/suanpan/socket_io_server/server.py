# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function

import urllib
import json
import gevent
import socketio
import geventwebsocket.handler
from suanpan.log import logger
from suanpan.g import g
from suanpan.utils import port, config


class WebSocketHandler(geventwebsocket.handler.WebSocketHandler):

    def get_environ(self):
        env = super(WebSocketHandler, self).get_environ()
        urlpath = self.path.split("?", 1)[0] if "?" in self.path else self.path
        env["PATH_INFO"] = urllib.parse.unquote(urlpath)
        return env


class SioServer:

    def __init__(self):
        self.sio = socketio.Server(async_mode="gevent",
                                   cors_allowed_origins="*",
                                   json=json)

    def on(self, name, func):
        self.sio.on(name, handler=func)

    def emit(self, name, message):
        self.sio.emit(name, message)

    def _init_win_server(self):
        p = None
        for _ in range(20):
            try:
                p = port.get_free_port()
                self.server.set_listener(("0.0.0.0", p))
                self.server.start()
                logger.info("Stream SIO Loop listen port {}".format(p))
                port.register_server(g.pstreamPort, p)
                return
            except OSError as e:
                if e.errno in [10013, 10048]:
                    logger.warn(
                        "Stream SIO Loop listen port conflict {}".format(p))
                    continue

                raise
            except Exception:
                raise

        raise Exception(
            "port conflicts repeatedly failed, please try again later")

    def _start_server(self):
        if port.need_free_port():
            self._init_win_server()
        else:
            self.server.start()

    def close(self):
        if self.server:
            self.server.stop()

    def start(self):
        self.sioApp = socketio.WSGIApp(
            self.sio,
            static_files={"/": config.resourcepath(g.staticFilesFolder)},
            socketio_path=g.sioPath)
        self.server = gevent.pywsgi.WSGIServer(("", g.pstreamPort),
                                               self.sioApp,
                                               handler_class=WebSocketHandler)
        self._start_server()
        self.server.serve_forever()
