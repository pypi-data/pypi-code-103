import argparse
import copy
import json
import os
import threading
from json import JSONDecodeError
from typing import Dict, Optional

import grpc
from tornado.web import RequestHandler

from .grpc_asyncio import AsyncioExecutor
from .. import BasePea
from ..helper import routes2str
from ...helper import random_identity, random_port
from ...zmq import AsyncZmqlet
from .... import __stop_msg__
from ....client.python import request
from ....helper import use_uvloop
from ....logging.base import get_logger
from ....proto import bert2tf_pb2, bert2tf_pb2_grpc
from ....proto.helper import pb2array, add_envelope, add_route

use_uvloop()


class GatewayPea:
    """A :class:`BasePea`-like class for holding a gRPC Gateway."""

    def __init__(self, args):
        if not args.proxy and os.name != 'nt':
            os.unsetenv('http_proxy')
            os.unsetenv('https_proxy')

        self.name = args.name or 'gateway'
        self.logger = get_logger(self.name)
        self._p_servicer = self._Pea(args)
        self._stop_event = threading.Event()
        self.is_ready = threading.Event()
        self.init_server(args)

        self.host = args.host
        self.grpc_port = args.grpc_port

    def init_server(self, args):
        self._ae = AsyncioExecutor()
        self._server = grpc.server(
            self._ae,
            options=[('grpc.max_send_message_length', args.max_message_size),
                     ('grpc.max_receive_message_length', args.max_message_size)])
        bert2tf_pb2_grpc.add_Bert2tfRPCServicer_to_server(self._p_servicer, self._server)
        self._bind_address = f'{args.host}:{args.grpc_port}'
        self._server.add_insecure_port(self._bind_address)

    class _Pea(bert2tf_pb2_grpc.Bert2tfRPCServicer):
        def __init__(self, args):
            super().__init__()
            self.args = args
            self.name = args.name or self.__class__.__name__
            self.logger = get_logger(self.name)

        def post_hook(self, msg: bert2tf_pb2.Message):
            msg_type = msg.request.WhichOneof('body')
            self.logger.info(
                f'received  "{msg_type}" from {routes2str(msg, flag_current=True)} client {msg.envelope.client_id}')
            msg.request.client_id = msg.envelope.client_id
            msg.request.status.CopyFrom(msg.envelope.status)

            add_route(msg.envelope, self.name, msg.envelope.client_id)

            return msg

        async def CallUnary(self, request: bert2tf_pb2.Request, context):
            with AsyncZmqlet(self.args) as zmqlet:
                await zmqlet.send_message(add_envelope(request, self.args.name, zmqlet.identity))
                msg = await zmqlet.recv_message(callback=self.post_hook)

                return msg.request

    def __enter__(self):
        return self.start()

    def start(self):
        self._server.start()
        self._stop_event.clear()
        self.is_ready.set()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        self._ae.shutdown()
        self._server.stop(None)
        self._stop_event.set()
        self.logger.success(__stop_msg__)

    def join(self):
        try:
            self._stop_event.wait()
        except KeyboardInterrupt:
            pass


class RESTGatewayPea(BasePea):
    def _create_http_server(self):
        from tornado.web import HTTPServer, Application
        app = Application([(f'/{self.args.rest_url}', PredictHandler, dict(args=self.args))])
        server = HTTPServer(app)
        server.bind(self.args.rest_port)
        return server

    def _create_io_loop(self):
        use_uvloop()
        import asyncio
        asyncio.set_event_loop(asyncio.new_event_loop())
        from tornado import ioloop
        io_loop = ioloop.IOLoop.current()
        return io_loop

    def loop_body(self):
        self.logger = get_logger(self.name)

        self.io_loop = self._create_io_loop()
        self.server = self._create_http_server()
        # do not use start(0), if that, uvloop will raise error,
        # the error can't be solve now, start() has same function with start(0) in my local machine
        self.server.start()
        self.set_ready()
        self.io_loop.start()

        # after call io_loop.stop(), it will run into this place
        self.io_loop.clear_current()
        self.io_loop.close(all_fds=True)

    def close(self):
        self.server.stop()
        self.io_loop.stop()

    @property
    def url(self):
        return f'http://{self.args.host}:{self.args.rest_port}/{self.args.rest_url}'


class PredictHandler(RequestHandler):
    """Tornado request handler for predict request"""

    def initialize(self, args: 'argparse.Namespace'):
        self.args = copy.deepcopy(args)
        self.args.port_ctrl = random_port()
        self.args.identity = random_identity()
        self.logger = get_logger(args.name)
        self._p_servicer = GatewayPea._Pea(self.args)

    async def prepare(self):
        try:
            self.set_status(200)
            self.logger.info(f'new request from {self.request.remote_ip}\t client {self.args.identity}')
            self.logger.debug(f'client {self.args.identity}\trequest body: {self.inputs}')
        except JSONDecodeError:
            self.set_status(400, reason='bad inputs')
            self.logger.debug(
                f'remote addr: {self.request.remote_ip}\trequest body: {self.request.body.decode("unicode_escape")} is a bad json')

    async def post(self):
        if self.get_status() == 200:
            if self.inputs:
                req = getattr(request, 'predict')(self.inputs)
                req = await self._p_servicer.CallUnary(req, None)
                if req.status.code == bert2tf_pb2.Status.SUCCESS:
                    self.write(
                        {'outputs': [[pb2array(blob).tolist() for blob in result.blobs] for result in
                                     req.predict.results]})
                else:
                    self.set_status(500, reason=f'internal server error: {req.status.description}')

            else:
                self.write('')
        elif self.get_status() == 400:
            pass
        else:
            raise ValueError(f'bad status code {self.get_status()}')

        self.flush()

    def on_finish(self):
        self.logger.success(f'remote addr {self.request.remote_ip} client {self.args.identity} send back result')

    @property
    def inputs(self) -> Optional[Dict]:
        body = self.request.body.decode('unicode_escape')
        if body:
            return json.loads(body)['inputs']
        else:
            return None
