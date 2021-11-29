# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function

import json
import gevent
from suanpan.log import logger
from suanpan.g import g
from suanpan.utils import port


class HttpServer:

    def __init__(self, mainThread):
        self.mainThread = mainThread

    def application(self, env, start_response):
        if env['REQUEST_METHOD'] == 'POST' and env[
                'PATH_INFO'] == '/internal/trap':
            start_response('200 OK', [('Content-Type', 'text/json')])
            yield json.dumps({
                "success": "true"
            }, ensure_ascii=False).encode('utf8')
            yield from self.mainThread.kill(code=98)
            return

        start_response('404 Not Found', [('Content-Type', 'text/json')])
        return [b'{"success": "false", "msg": "invalid request"}']

    def _init_win_server(self):
        p = None
        for _ in range(20):
            try:
                p = port.get_free_port()
                self.server.set_listener(("0.0.0.0", p))
                self.server.start()
                logger.info("Stream HTTP Loop listen port {}".format(p))
                port.register_server(g.termPort, p)
                return
            except OSError as e:
                if e.errno in [10013, 10048]:
                    logger.warn(
                        "Stream HTTP Loop listen port conflict {}".format(p))
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
        self.server = gevent.pywsgi.WSGIServer(("", g.termPort),
                                               self.application)
        self._start_server()
        self.server.serve_forever()
