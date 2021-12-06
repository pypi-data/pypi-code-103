import argparse
from typing import Tuple, Callable, Optional, List

import zmq
import zmq.asyncio
from zmq.eventloop.zmqstream import ZMQStream

from .. import __default_host__
from ..enums import SocketType
from ..helper import colored, get_or_reuse_loop
from ..logging import default_logger
from ..logging.base import get_logger
from ..proto import bert2tf_pb2
from ..proto.helper import add_envelope, is_data_request


class Zmqlet:
    def __init__(self, args: 'argparse.Namespace'):
        self.args = args

        self.name = args.name or self.__class__.__name__
        self.identity = args.identity
        self.msg_sent = 0
        self.msg_recv = 0

        self.logger = get_logger(self.name)

        self.ctrl_addr = self.get_ctrl_address(args)

        self.is_polling_pause = False  # flag to identity whether the in sock was paused
        self.ctx, self.in_sock, self.out_sock, self.ctrl_sock = self.init_socket()
        self.opened_socks = []
        self.register_pollin()

        self.opened_socks.extend([self.in_sock, self.out_sock, self.ctrl_sock])

        if self.in_sock_type == zmq.DEALER:
            self.send_idle()

        self.is_closed = False

    def send_idle(self):
        """Use `in_sock` to send idle signal to head pea, used for Router-Dealer"""
        req = bert2tf_pb2.Request()
        req.control.command = bert2tf_pb2.Request.ControlRequest.IDLE
        msg = add_envelope(req, self.name, self.identity)

        send_message(self.in_sock, msg)

    def pause_pollin(self):
        """Remove :attr:`in_sock` from the poller """
        self.poller.unregister(self.in_sock)
        self.logger.info(f'{self.name} stop receiving message')

    def resume_pollin(self):
        """Put :attr:`in_sock` back to the poller """
        self.poller.register(self.in_sock)
        self.logger.info(f'{self.name} restart receiving message')

    def send_message(self, msg: bert2tf_pb2.Message):
        """Main entry for send message"""
        if self.out_sock_type == zmq.PUB:
            msg.envelope.receiver_id = msg.envelope.client_id

        _req = getattr(msg.request, msg.request.WhichOneof('body'))

        if is_data_request(_req):
            o_sock = self.out_sock
        else:
            o_sock = self.ctrl_sock

        send_message(o_sock, msg)
        self.msg_sent += 1
        if o_sock == self.out_sock and self.in_sock_type == zmq.DEALER:
            self.send_idle()

    def recv_message(self, callback: Callable = None):
        """Main entry for receive message"""
        i_sock = self._pull()
        if i_sock is not None:
            msg = recv_message(i_sock)
            self.msg_recv += 1
            if callback:
                return callback(msg)

    def _pull(self, interval: int = 1):
        socks = dict(self.poller.poll(interval))
        if socks.get(self.in_sock) == zmq.POLLIN:
            return self.in_sock  # for dealer return idle status to router
        elif socks.get(self.out_sock) == zmq.POLLIN:
            return self.out_sock

    def register_pollin(self):
        """Register `in_sock` and `ctrl_sock` to zmq Poller, if the `out_sock` is Router type, it should be register"""
        self.poller = zmq.Poller()
        self.poller.register(self.in_sock, zmq.POLLIN)
        self.poller.register(self.ctrl_sock, zmq.POLLIN)
        if self.out_sock_type == zmq.ROUTER:
            self.poller.register(self.out_sock, zmq.POLLIN)

    def init_socket(self) -> Tuple[zmq.Context, zmq.Socket, zmq.Socket, zmq.Socket]:
        """Initial socket"""
        ctx = self._get_zmq_ctx()
        ctx.setsockopt(zmq.LINGER, 0)

        self.logger.info('setting up sockets...')
        in_sock, in_addr = _init_socket(ctx, self.args.socket_in, self.identity, port=self.args.port_in)
        out_sock, out_addr = _init_socket(ctx, self.args.socket_out, self.identity, port=self.args.port_out)
        ctrl_sock, ctrl_addr = _init_socket(ctx, SocketType.PAIR_BIND, None, port=self.args.port_ctrl)

        self.logger.info(
            'input %s (%s) \t output %s (%s) \t control %s (%s)' %
            (colored(in_addr, 'yellow'), self.args.socket_in,
             colored(out_addr, 'yellow'), self.args.socket_out,
             colored(ctrl_addr, 'yellow'), SocketType.PAIR_BIND))

        self.in_sock_type = in_sock.type
        self.out_sock_type = out_sock.type
        self.ctrl_sock_type = ctrl_sock.type

        return ctx, in_sock, out_sock, ctrl_sock

    def _get_zmq_ctx(self) -> zmq.Context:
        return zmq.Context()

    @staticmethod
    def get_ctrl_address(args: argparse.Namespace) -> str:
        """Get control socket address"""
        return f'tcp://{__default_host__}:{args.port_ctrl}'

    def print_status(self):
        self.logger.info(f'#sent: {self.msg_sent} '
                         f'#recv: {self.msg_recv} ')

    def close(self):
        """Close open socket"""
        if not self.is_closed:
            self.is_closed = True
            for sock in self.opened_socks:
                sock.close()
            self.ctx.term()
            self.print_status()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


class ZmqStreamlet(Zmqlet):
    """A :class:`ZmqStreamlet` object can send/receive data to/from ZeroMQ stream and invoke callback function. It
    has three sockets for input, output and control.

    .. warning::
        It requires :mod:`tornado` and :mod:`uvloop` to be installed.
    """

    def register_pollin(self):
        import tornado.ioloop
        get_or_reuse_loop()

        self.io_loop = tornado.ioloop.IOLoop.current()

        self.in_sock = ZMQStream(self.in_sock, self.io_loop)
        self.out_sock = ZMQStream(self.out_sock, self.io_loop)
        self.ctrl_sock = ZMQStream(self.ctrl_sock, self.io_loop)
        self.in_sock.stop_on_recv()

    def pause_pollin(self):
        """Remove :attr:`in_sock` from the poller """
        self.in_sock.stop_on_recv()

    def resume_pollin(self):
        """Put :attr:`in_sock` back to the poller """
        self.in_sock.on_recv(self._on_recv_callback)

    def start(self, callback):
        def _callback(msg):
            msg = _prepare_recv_msg(msg[-1])
            self.msg_recv += 1

            msg = callback(msg)

            if msg:
                self.send_message(msg)

        self._on_recv_callback = lambda x: _callback(x)
        self.in_sock.on_recv(self._on_recv_callback)

        self.ctrl_sock.on_recv(self._on_recv_callback)

        if self.out_sock_type == zmq.ROUTER:
            self.out_sock.on_recv(self._on_recv_callback)

        self.io_loop.start()
        self.io_loop.clear_current()
        self.io_loop.close(all_fds=True)

    def close(self):
        """Close all sockets and shutdown the ZMQ context associated to this `Zmqlet`. """
        if not self.is_closed:
            import time
            # wait until the close signal is received
            time.sleep(.01)
            for sock in self.opened_socks:
                sock.flush()

            super().close()
            try:
                self.io_loop.stop()
                # Replace handle events function, to skip
                # None event after sockets are closed.
                if hasattr(self.in_sock, '_handle_events'):
                    self.in_sock._handle_events = lambda *args, **kwargs: None
                if hasattr(self.out_sock, '_handle_events'):
                    self.out_sock._handle_events = lambda *args, **kwargs: None
                if hasattr(self.ctrl_sock, '_handle_events'):
                    self.ctrl_sock._handle_events = lambda *args, **kwargs: None
            except AttributeError as e:
                self.logger.error(f'failed to stop. {e}')


class AsyncZmqlet(Zmqlet):
    def _get_zmq_ctx(self) -> zmq.asyncio.Context:
        return zmq.asyncio.Context()

    async def send_message(self, msg: bert2tf_pb2.Message):
        _msg = _prepare_send_msg(msg)
        await self.out_sock.send_multipart(_msg)
        self.msg_sent += 1

    async def recv_message(self, callback: Callable = None):
        self.in_sock.setsockopt(zmq.RCVTIMEO, -1)
        identity, msg = await self.in_sock.recv_multipart()
        self.msg_recv += 1
        msg = _prepare_recv_msg(msg)
        if callback:
            return callback(msg)


def send_message(sock: zmq.Socket, msg: bert2tf_pb2.Message, timeout: int = -1):
    try:
        if timeout > 0:
            sock.setsockopt(zmq.SNDTIMEO, timeout)
        else:
            sock.setsockopt(zmq.SNDTIMEO, -1)

        _msg = _prepare_send_msg(msg)
        sock.send_multipart(_msg)

    except zmq.error.Again:
        raise TimeoutError(
            'cannot send message to sock %s after timeout=%dms, please check the following:'
            'is the server still online? is the network broken? are "port" correct? ' % (
                sock, timeout))
    except zmq.error.ZMQError as ex:
        default_logger.critical(ex)
    finally:
        try:
            sock.setsockopt(zmq.SNDTIMEO, -1)
        except zmq.error.ZMQError:
            pass


def _prepare_send_msg(msg: bert2tf_pb2.Message) -> List[bytes]:
    _msg = [msg.envelope.receiver_id.encode(), msg.SerializeToString()]
    return _msg


def recv_message(sock: zmq.Socket, timeout: int = -1) -> bert2tf_pb2.Message:
    try:
        if timeout > 0:
            sock.setsockopt(zmq.RCVTIMEO, timeout)
        else:
            sock.setsockopt(zmq.RCVTIMEO, -1)
        msg = sock.recv_multipart()
        msg = _prepare_recv_msg(msg[-1])
        return msg
    except zmq.error.Again:
        raise TimeoutError(
            'no response from sock %s after timeout=%dms, please check the following:'
            'is the server still online? is the network broken? are "port" correct? ' % (
                sock, timeout))
    except Exception as ex:
        raise ex
    finally:
        sock.setsockopt(zmq.RCVTIMEO, -1)


def _prepare_recv_msg(msg: str) -> bert2tf_pb2.Message:
    _msg = bert2tf_pb2.Message()
    _msg.ParseFromString(msg)

    return _msg


def _init_socket(ctx: 'zmq.Context', socket_type: SocketType, identity: str, host: str = __default_host__,
                 port: int = None) -> Tuple[zmq.Socket, zmq.Socket]:
    sock = {
        SocketType.PULL_BIND: lambda: ctx.socket(zmq.PULL),
        SocketType.PULL_CONNECT: lambda: ctx.socket(zmq.PULL),
        SocketType.SUB_BIND: lambda: ctx.socket(zmq.SUB),
        SocketType.SUB_CONNECT: lambda: ctx.socket(zmq.SUB),
        SocketType.PUB_BIND: lambda: ctx.socket(zmq.PUB),
        SocketType.PUB_CONNECT: lambda: ctx.socket(zmq.PUB),
        SocketType.PUSH_BIND: lambda: ctx.socket(zmq.PUSH),
        SocketType.PUSH_CONNECT: lambda: ctx.socket(zmq.PUSH),
        SocketType.PAIR_BIND: lambda: ctx.socket(zmq.PAIR),
        SocketType.PAIR_CONNECT: lambda: ctx.socket(zmq.PAIR),
        SocketType.ROUTER_BIND: lambda: ctx.socket(zmq.ROUTER),
        SocketType.DEALER_CONNECT: lambda: ctx.socket(zmq.DEALER),
    }[socket_type]()
    sock.setsockopt(zmq.LINGER, 0)

    if socket_type == SocketType.DEALER_CONNECT:
        sock.set_string(zmq.IDENTITY, identity)

    if socket_type.is_bind:
        if not port:
            sock.bind(host)
        else:
            try:
                sock.bind(f'tcp://{host}:{port}')
            except zmq.error.ZMQError as ex:
                default_logger.error(f'error when binding port {port} to {host}')
                raise ex

    else:
        if not port:
            sock.connect(host)
        else:
            sock.connect(f'tcp://{host}:{port}')

    if socket_type in (SocketType.SUB_CONNECT, SocketType.SUB_BIND):
        sock.subscribe(identity)

    return sock, sock.getsockopt_string(zmq.LAST_ENDPOINT)


def send_ctrl_message(address: str, cmd: 'bert2tf_pb2.Request.ControlRequest', timeout: int) -> Optional[
    bert2tf_pb2.Message]:
    """Send a control message to a specific address and wait for the response

    :param address: the socket address to send
    :param cmd: the control command to send
    :param timeout: the waiting time (in ms) for the response
    """
    # control message is short, set a timeout and ask for quick response
    with zmq.Context() as ctx:
        ctx.setsockopt(zmq.LINGER, 0)
        sock, _ = _init_socket(ctx, SocketType.PAIR_CONNECT, None, host=address)
        req = bert2tf_pb2.Request()
        req.control.command = cmd
        msg = add_envelope(req, 'ctl', '')
        send_message(sock, msg, timeout)
        r = None
        try:
            r = recv_message(sock, timeout)
        except TimeoutError:
            pass
        finally:
            sock.close()
        return r
