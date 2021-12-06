import copy
import logging
from argparse import Namespace
from contextlib import ExitStack
from typing import Dict, Optional, Union, List, Callable, Set

from ..helper import random_port, random_identity
from ..pea import BasePea
from ..pea.head_pea import HeadPea
from ..pea.tail_pea import TailPea
from ...enums import SocketType, PeaRoleType, RuntimeBackendType
from ...logging.base import get_logger
from ...parser import set_pod_parser, set_gateway_parser
from ...parser.helper import get_parsed_args


class BasePod(ExitStack):
    """
    Base Pod, the basic unit in Flow
    """

    def __init__(self, args: Namespace):
        super().__init__()
        self.peas = []
        self._args = args

        self.name = getattr(args, 'name', self.__class__.__name__)
        self.logger = get_logger(self.name)

        self.peas_args = self._parse_args(args)

        if hasattr(args, 'device_map') and args.on_gpu:
            self._set_peas_device_map()

    def _parse_args(self, args: Namespace) -> Dict[str, Optional[Union[List[Namespace], Namespace]]]:
        peas_args = {
            'head': None,
            'tail': None,
            'peas': []
        }

        if getattr(args, 'replicas', 1) > 1:
            peas_args['head'] = _copy_to_head_args(args)
            peas_args['tail'] = _copy_to_tail_args(args)
            peas_args['peas'] = _set_peas_args(args, peas_args['head'], peas_args['tail'])

        else:
            args.role = PeaRoleType.SINGLETON
            peas_args['peas'] = [args]

        return peas_args

    def _set_peas_device_map(self):
        self.head_args.metas['device_id'] = -1
        self.tail_args.metas['device_id'] = -1

        if 'device_id' not in self.peas_args['peas'][0].metas:
            device_map = _get_device_map(self._args.device_map, len(self.peas_args['peas']), self.logger)
            for idx, pea_args in enumerate(self.peas_args['peas']):
                pea_args.metas['device_id'] = device_map[idx]

    def start(self) -> 'BasePod':
        if self.peas_args['head']:
            pea = HeadPea(self.peas_args['head'])
            self.peas.append(pea)
            self.enter_context(pea)

        for idx, args in enumerate(self.peas_args['peas']):
            args.replicas_id = idx
            pea = BasePea(args)
            self.peas.append(pea)
            self.enter_context(pea)

        if self.peas_args['tail']:
            pea = TailPea(self.peas_args['tail'])
            self.peas.append(pea)
            self.enter_context(pea)

        return self

    def join(self):
        """Wait until all peas exit"""
        try:
            for p in self.peas:
                # p.join()
                pass
        except KeyboardInterrupt:
            pass
        finally:
            self.peas.clear()

    def __enter__(self):
        return self.start()

    def __exit__(self, exc_type, exc_val, exc_tb):
        super().__exit__(exc_type, exc_val, exc_tb)
        self.join()

    @property
    def head_args(self) -> Namespace:
        if self.peas_args['head']:
            return self.peas_args['head']
        else:
            return self.peas_args['peas'][0]

    @property
    def tail_args(self) -> Namespace:
        if self.peas_args['tail']:
            return self.peas_args['tail']
        else:
            return self.peas_args['peas'][0]

    @property
    def all_args(self) -> List[Namespace]:
        return self.peas_args['peas']


class Pod(BasePod):
    def __init__(self,
                 kwargs: Dict,
                 needs: Set[str] = None,
                 parser: Callable = set_pod_parser):
        self._args, _ = get_parsed_args(kwargs, parser(), 'Pod')
        self.needs = needs
        super().__init__(self._args)

    @staticmethod
    def connect(first: 'BasePod', second: 'BasePod', first_socket_type: 'SocketType'):
        """Connect two Pods

        :param first: the first BasePod
        :param second: the second BasePod
        :param first_socket_type: socket type of the first BasePod, availables are PUSH_BIND, PUSH_CONNECT, PUB_BIND
        """
        if first_socket_type == SocketType.PUSH_BIND:
            first.tail_args.socket_out = SocketType.PUSH_BIND
            second.head_args.socket_in = SocketType.PULL_CONNECT

            second.head_args.port_in = first.tail_args.port_out
        elif first_socket_type == SocketType.PUSH_CONNECT:
            first.tail_args.socket_out = SocketType.PUSH_CONNECT
            second.head_args.socket_in = SocketType.PULL_BIND

            first.tail_args.port_out = second.head_args.port_in
        elif first_socket_type == SocketType.PUB_BIND:
            first.tail_args.socket_out = SocketType.PUB_BIND
            second.head_args.socket_in = SocketType.SUB_CONNECT

            second.head_args.port_in = first.tail_args.port_out
        else:
            raise NotImplementedError('%r is not supported here' % first_socket_type)


class GatewayPod(Pod):
    def __init__(self, *args, **kwargs):
        super(GatewayPod, self).__init__(parser=set_gateway_parser, *args, **kwargs)

    def start(self):
        from ..pea.gateway import RESTGatewayPea, GatewayPea
        gateway_pea_args = self.all_args[0]

        gateway_pea_args.name = 'gateway'
        gateway = GatewayPea(gateway_pea_args)
        self.peas.append(gateway)
        self.enter_context(gateway)

        if gateway_pea_args.rest_api:
            rest_gateway_pea_args = copy.deepcopy(gateway_pea_args)
            rest_gateway_pea_args.runtime_backend = RuntimeBackendType.from_string('thread')
            rest_gateway_pea_args.name = 'rest_gateway'
            rest_gateway_pea_args.use = '_rest_gateway'
            rest_gateway_pea_args.port_ctrl = random_port()
            rest_gateway = RESTGatewayPea(rest_gateway_pea_args)
            self.peas.append(rest_gateway)
            self.enter_context(rest_gateway)

        return self

    @property
    def grpc_port(self) -> int:
        return self.all_args[0].grpc_port

    @property
    def host(self) -> str:
        return self.all_args[0].host

    @property
    def rest_api(self) -> bool:
        return self.all_args[0].rest_api

    @property
    def rest_port(self) -> Optional[int]:
        if self.rest_api:
            return self.all_args[0].rest_port

        return None

    @property
    def rest_url(self) -> Optional[str]:
        if self.rest_api:
            return self.all_args[0].rest_url

        return None


def _copy_to_head_args(args: Namespace) -> Namespace:
    _args = copy.deepcopy(args)
    _args.port_out = random_port()
    _args.port_ctrl = random_port()
    _args.socket_out = SocketType.ROUTER_BIND
    _args.role = PeaRoleType.HEAD
    _args.use = '_route'
    _args.use_with = None
    _args.runtime_backend = RuntimeBackendType.from_string('thread')

    return _args


def _copy_to_tail_args(args: Namespace) -> Namespace:
    _args = copy.deepcopy(args)
    _args.port_in = random_port()
    _args.port_ctrl = random_port()
    _args.role = PeaRoleType.TAIL
    _args.socket_in = SocketType.PULL_BIND
    _args.use = '_forward'
    _args.use_with = None
    _args.runtime_backend = RuntimeBackendType.from_string('thread')

    return _args


def _set_peas_args(args: Namespace, head_args: Namespace, tail_args: Namespace) -> List[Namespace]:
    pea_args = []
    for idx in range(args.replicas):
        _args = copy.deepcopy(args)
        _args.identity = random_identity()
        _args.port_in = head_args.port_out
        _args.port_out = tail_args.port_in
        _args.port_ctrl = random_port()
        _args.socket_in = SocketType.DEALER_CONNECT
        _args.socket_out = SocketType.PUSH_CONNECT
        _args.role = PeaRoleType.REPLICA
        _args.replicas_id = idx
        pea_args.append(_args)

    return pea_args


def _get_device_map(device_map: List[int], num_worker: int, logger: logging.Logger) -> List[int]:
    import GPUtil
    cur_device_map = [-1] * num_worker
    try:
        avail_gpus = GPUtil.getAvailable(order='memory', limit=len(GPUtil.getGPUs()))

        if avail_gpus:
            cur_device_map = avail_gpus
            if device_map:
                device_map = list(set(device_map))
                not_matched_gpus = [idx for idx in device_map if idx not in avail_gpus]
                if not not_matched_gpus:
                    cur_device_map = device_map
                else:
                    cur_device_map = [idx for idx in device_map if idx in avail_gpus]
                    logger.warning(
                        f'device(s):{not_matched_gpus} not in available device(s):{avail_gpus}, '
                        f'use matched available device(s): {cur_device_map}')

            cur_device_map = (cur_device_map * num_worker)[:num_worker]

        else:
            logger.info('no GPU(s) available, fall back to CPU')

    except FileNotFoundError:
        logger.warning('nvidia-smi is missing, often means no gpu on this machine. fall back to cpu!')
    return cur_device_map
