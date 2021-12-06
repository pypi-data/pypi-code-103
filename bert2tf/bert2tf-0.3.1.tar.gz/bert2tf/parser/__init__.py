import argparse

from .helper import set_base_parser, add_arg_group, KVAppendAction
from .. import __default_host__
from ..enums import SocketType, PeaRoleType, RuntimeBackendType


def set_executor_parser(parser: argparse.ArgumentParser = None) -> argparse.ArgumentParser:
    """
    :param parser: set executor parser
    :return:
    """
    if not parser:
        parser = set_base_parser()

    gp0 = add_arg_group(parser, 'executor basic arguments')
    gp0.add_argument('--use', type=str, help='which executor should be used in this pea')
    gp0.add_argument('--use-with', action=KVAppendAction, help='parameters for initializing executor')
    gp0.add_argument('--metas', action=KVAppendAction, default=dict(), help='meta parameters for executor')

    return parser


def set_pea_parser(parser: argparse.ArgumentParser = None) -> argparse.ArgumentParser:
    """
    :param parser: set pea parser
    :return:
    """
    from ..peapods.helper import random_identity
    if not parser:
        parser = set_base_parser()

    parser = set_zmqlet_parser(parser)
    parser = set_executor_parser(parser)

    gp0 = add_arg_group(parser, 'pea basic arguments')
    gp0.add_argument('--name', type=str, help='the name of this pea')
    gp0.add_argument('--identity', type=str, default=random_identity(),
                     help='the identity of the sockets, default a random string')
    gp0.add_argument('--replicas-id', type=int, default=0, help='the id of pea')
    gp0.add_argument('--timeout-ready', type=int, default=10000,
                     help='timeout (ms) of a pea is ready for request, -1 for waiting forever')
    gp0.add_argument('--role', type=PeaRoleType.from_string, choices=list(PeaRoleType),
                     help='the role of this pea in a pod')
    gp0.add_argument('--runtime-backend', type=RuntimeBackendType.from_string, choices=list(RuntimeBackendType),
                     default=RuntimeBackendType.PROCESS,
                     help='whether pea run in thread or process, default process')

    gp1 = add_arg_group(parser, 'pea messaging arguments')
    gp1.add_argument('--num-part', type=int, default=1,
                     help='wait until the number of parts of message are all received')
    gp1.add_argument('--requests', action=KVAppendAction, help='parameters for requests action')

    return parser


def set_gateway_parser(parser: argparse.ArgumentParser = None) -> argparse.ArgumentParser:
    """
    :param parser: set gateway parser
    :return:
    """
    if not parser:
        parser = set_base_parser()

    parser = set_pea_parser(parser)
    parser = _set_grpc_parser(parser)
    gp0 = add_arg_group(parser, 'gateway basic arguments')
    gp0.add_argument('--rest-url', type=str, default='webapi', help='url for http request')
    gp0.add_argument('--rest-port', type=int, default=5000, help='port for http request')
    gp0.add_argument('--rest-api', action='store_true', default=False,
                     help='use REST-API as the interface instead of gRPC with port number '
                          'set to the value of "http-port"')
    return parser


def set_pod_parser(parser: argparse.ArgumentParser = None) -> argparse.ArgumentParser:
    """
    :param parser: set pod parser
    :return:
    """
    if not parser:
        parser = set_base_parser()

    parser = set_pea_parser(parser)
    gp0 = add_arg_group(parser, 'pod basic arguments')
    gp0.add_argument('--replicas', type=int, default=1, help='how many peas in pod, default 1')
    gp0.add_argument('--device-map', type=int, nargs='+', default=[], help='device map in pod, '
                                                                           'it always use in executor when on_gpu=True,'
                                                                           'warning: if device_id in namespace, '
                                                                           'if always use device_id instead of device_map')
    gp0.add_argument('--on-gpu', action='store_true', default=False, help='whether deploy executor in peas on GPU')
    return parser


def set_zmqlet_parser(parser: argparse.ArgumentParser = None) -> argparse.ArgumentParser:
    """
    :param parser: set zmqlet parser
    :return:
    """
    from ..peapods.helper import random_port
    if not parser:
        parser = set_base_parser()

    gp1 = add_arg_group(parser, 'pea network arguments')
    gp1.add_argument('--port-in', type=int, default=random_port(),
                     help='port for input data, default a random port between [49152, 65535]')
    gp1.add_argument('--port-out', type=int, default=random_port(),
                     help='port for output data, default a random port between [49152, 65535]')
    gp1.add_argument('--port-ctrl', type=int, default=random_port(),
                     help='port for controlling the pod, default a random port between [49152, 65535]')
    gp1.add_argument('--host-in', type=str, default=__default_host__,
                     help=f'host address for input, by default it is {__default_host__}')
    gp1.add_argument('--host-out', type=str, default=__default_host__,
                     help=f'host address for output, by default it is {__default_host__}')
    gp1.add_argument('--socket-in', type=SocketType.from_string, choices=list(SocketType),
                     default=SocketType.PULL_BIND,
                     help='socket type for input port')
    gp1.add_argument('--socket-out', type=SocketType.from_string, choices=list(SocketType),
                     default=SocketType.PUSH_BIND,
                     help='socket type for output port')
    gp1.add_argument('--timeout', type=int, default=-1,
                     help='timeout (ms) of all requests, -1 for waiting forever')
    gp1.add_argument('--timeout-ctrl', type=int, default=5000,
                     help='timeout (ms) of the control request, -1 for waiting forever')
    return parser


def _set_grpc_parser(parser: argparse.ArgumentParser = None) -> argparse.ArgumentParser:
    """
    :param parser: set grpc parser
    :return:
    """
    if not parser:
        parser = set_base_parser()
    gp1 = add_arg_group(parser, 'grpc and remote arguments')
    gp1.add_argument('--max-message-size', type=int, default=-1,
                     help='maximum send and receive size for grpc server in bytes, -1 means unlimited')
    gp1.add_argument('--proxy', action='store_true', default=False,
                     help='respect the http_proxy and https_proxy environment variables. '
                          'otherwise, it will unset these proxy variables before start. '
                          'gRPC seems to prefer --no-proxy')
    gp1.add_argument('--grpc-port', type=int, default=5555, help='port for GRPC gateway')
    gp1.add_argument('--host', type=str, default=__default_host__,
                     help=f'host address of the gateway, by default it is {__default_host__}.')
    return parser
