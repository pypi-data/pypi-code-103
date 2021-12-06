import argparse
import multiprocessing
import os
import threading
import traceback

import zmq

from .helper import get_event, ConditionalEvent, routes2str
from ..zmq import Zmqlet, send_ctrl_message, ZmqStreamlet
from ...enums import PeaRoleType, RuntimeBackendType
from ...excepts import PeaFailToStart, NoExplicitMessage
from ...executors import BaseExecutor
from ...logging.base import get_logger
from ...proto import bert2tf_pb2
from ...proto.helper import add_route, get_request_type


class BasePea:
    """The basic unit in Pod"""

    def __init__(self, args: 'argparse.Namespace'):
        self.args = args

        # add events
        test_worker = {
            RuntimeBackendType.THREAD: threading.Thread,
            RuntimeBackendType.PROCESS: multiprocessing.Process,
        }.get(getattr(args, 'runtime_backend', RuntimeBackendType.THREAD))()
        self.is_ready = get_event(test_worker)
        self.is_shutdown = get_event(test_worker)
        self.unset_shutdown()
        self.ready_or_shutdown = ConditionalEvent(events_list=[self.is_ready, self.is_shutdown],
                                                  runtime_backend=getattr(args, 'runtime_backend',
                                                                          RuntimeBackendType.THREAD)).event

        # add worker
        self.worker = {
            RuntimeBackendType.THREAD: threading.Thread,
            RuntimeBackendType.PROCESS: multiprocessing.Process,
        }.get(getattr(args, 'runtime_backend', RuntimeBackendType.THREAD))(
            target=self.run
        )
        self.name = args.name or self.__class__.__name__.lower()

        if self.args.role == PeaRoleType.REPLICA:
            self.name = f'{self.name}-{args.replicas_id}'

        self.args.name = self.name

        self.logger = get_logger(self.name)

        self._message = None
        self._request = None

        self.ctrl_addr = Zmqlet.get_ctrl_address(self.args)

    def run(self):
        try:
            self.loop_body()

        except KeyboardInterrupt:
            self.logger.info('Loop interrupted by user')
        except SystemError as ex:
            self.logger.error(f'SystemError interrupted pea loop {repr(ex)}')
        except zmq.error.ZMQError:
            self.logger.critical('zmqlet can\'t be initiated')
        except Exception as ex:
            self.logger.critical(f'met unknown exception {repr(ex)}', exc_info=True)
        finally:
            self.loop_teardown()
            self.unset_ready()
            self.set_shutdown()

    def start(self):
        self.worker.start()

        _timeout = getattr(self.args, 'timeout_ready', -1)
        if _timeout <= 0:
            _timeout = None
        else:
            _timeout /= 1e3

        if self.ready_or_shutdown.wait(_timeout):
            if self.is_shutdown.is_set():
                # return too early and the shutdown is set, means something fails!!
                self.logger.critical(f'fail to start {self.__class__} with name {self.name}, '
                                     f'this often means the pea used in the pod is not valid')
                raise PeaFailToStart
            return self
        else:
            raise TimeoutError(
                f'{self.__class__} with name {self.name} can not be initialized after {_timeout * 1e3}ms')

    def loop_body(self):
        self.load_executor()
        # avoid process bug, need create logger again
        self.logger = get_logger(self.name)
        self.zmqlet = ZmqStreamlet(self.args)

        self.set_ready()
        self.zmqlet.start(self.msg_callback)

    def pre_hook(self, msg: bert2tf_pb2.Message) -> 'BasePea':
        self._message = msg
        self._request = getattr(msg.request, msg.request.WhichOneof('body'))

        self.logger.info(
            f'received "{get_request_type(self.request)}" from {routes2str(msg, flag_current=True)} client {msg.envelope.client_id}')

        add_route(self.message.envelope, self.name, self.args.identity)

        return self

    def handle(self, msg: bert2tf_pb2.Message) -> 'BasePea':
        if msg.envelope.status.code != bert2tf_pb2.Status.ERROR:
            self.executor.deal(self.request_type)
        return self

    def post_hook(self, msg: bert2tf_pb2.Message) -> 'BasePea':
        msg.envelope.routes[-1].end_time.GetCurrentTime()
        return self

    def _callback(self, msg: bert2tf_pb2.Message) -> bert2tf_pb2.Message:
        if msg.envelope.status.code != bert2tf_pb2.Status.ERROR:
            self.pre_hook(msg).handle(msg).post_hook(msg)

        return msg

    def msg_callback(self, msg: bert2tf_pb2.Message) -> bert2tf_pb2.Message:
        try:
            self.zmqlet.send_message(self._callback(msg))
        except (SystemError, zmq.error.ZMQError, KeyboardInterrupt) as ex:
            self.logger.info(f'{repr(ex)} causes the breaking from the event loop')
            # serious error happen in callback, we need to break the event loop
            self.zmqlet.send_message(msg)
            # note, the logger can only be put on the second last line before `close`, as when
            # `close` is called, the callback is unregistered and everything after `close` can not be reached
            # some black magic in eventloop i guess?

            self.loop_teardown()
            self.set_shutdown()

        except NoExplicitMessage:
            # silent and do not propagate message anymore
            # 1. wait partial message to be finished
            # 2. dealer send a control message and no need to go on
            pass
        except (RuntimeError, Exception) as ex:
            msg.envelope.status.code = bert2tf_pb2.Status.ERROR
            if not msg.envelope.status.description:
                msg.envelope.status.description = f'{self} throws {repr(ex)}'
            d = msg.envelope.status.details.add()
            d.pod = self.name
            d.pod_id = self.args.identity
            d.exception = repr(ex)
            d.traceback = traceback.format_exc()
            d.time.GetCurrentTime()
            self.logger.error(ex, exc_info=True)

            self.zmqlet.send_message(msg)

    def load_executor(self):
        # set envs
        os.environ['BERT2TF_PEA_NAME'] = self.args.name

        self.executor = BaseExecutor.load_config(self.args.use, self.args.use_with, self.args.metas)
        self.executor.attach(pea=self)

    def set_ready(self, *args, **kwargs):
        """Set the status of the pea to ready """
        from ... import __ready_msg__
        if not self.is_ready.is_set():
            self.is_ready.set()
            self.logger.success(__ready_msg__)

    def unset_ready(self, *args, **kwargs):
        """Set the status of the pea to shutdown """
        if self.is_ready.is_set():
            from ... import __stop_msg__
            self.is_ready.clear()
            self.logger.success(__stop_msg__)

    def set_shutdown(self, *args, **kwargs):
        """Set the status of the pea to shutdown"""
        if not self.is_shutdown.is_set():
            self.is_shutdown.set()

    def unset_shutdown(self, *args, **kwargs):
        """Set the status of the peat to ready"""
        if self.is_shutdown.is_set():
            self.is_shutdown.clear()

    def loop_teardown(self):
        """Stop the request loop """
        if hasattr(self, 'zmqlet'):
            self.zmqlet.close()

    def close(self):
        self.send_terminate_signal()
        self.is_shutdown.wait()

    def join(self, *args, **kwargs):
        self.worker.join(*args, **kwargs)

    def send_terminate_signal(self):
        if self.is_ready.is_set() and hasattr(self, 'ctrl_addr'):
            send_ctrl_message(self.ctrl_addr,
                              bert2tf_pb2.Request.ControlRequest.TERMINATE,
                              self.args.timeout_ctrl)

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    @property
    def message(self):
        return self._message

    @property
    def request(self) -> bert2tf_pb2.Request:
        return self._request

    @property
    def request_type(self) -> str:
        return self._request.__class__.__name__
