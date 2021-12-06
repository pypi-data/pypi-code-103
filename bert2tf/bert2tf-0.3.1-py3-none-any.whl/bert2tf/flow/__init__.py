from collections import OrderedDict
from contextlib import ExitStack
from typing import Union, List, Tuple, Set, Iterator

import numpy as np

from .. import __stop_msg__
from ..baml import BAMLCompatible
from ..enums import SocketType
from ..excepts import FlowTopologyError, FlowMissingPodError, FlowEmptyError
from ..helper import colored
from ..logging.base import get_logger
from ..peapods.helper import get_internal_ip, get_public_ip
from ..peapods.pod import GatewayPod, Pod


class FlowType(type(ExitStack), type(BAMLCompatible)):
    """Type of Flow, metaclass of :class:`BaseFlow`"""


class Flow(BAMLCompatible, ExitStack, metaclass=FlowType):
    """Flow for models serving"""

    def __init__(self, **kwargs):
        super(Flow, self).__init__()

        self.logger = get_logger(self.__class__.__name__)

        self._pod_nodes = OrderedDict()
        self._pod_name_counter = 0

        self._last_changed_pod = ['gateway']

        self.built = False

        self._gateway_kwargs = kwargs

    def add_gateway(self, **kwargs):
        kwargs['name'] = 'gateway'
        kwargs.update(self._gateway_kwargs)
        self._pod_nodes['gateway'] = GatewayPod(kwargs=kwargs, needs={self._last_changed_pod[-1]})

    def add(self, needs: Union[str, Tuple[str], List[str]] = None, **kwargs):
        pod_name = kwargs.get('name', None)

        if pod_name in self._pod_nodes:
            raise FlowTopologyError('name: %s is used in this Flow already!' % pod_name)

        if not pod_name:
            pod_name = f'pod{self._pod_name_counter}'
            self._pod_name_counter += 1

        needs = self._parse_endpoints(self, pod_name, needs, connect_to_last_pod=True)
        kwargs['name'] = pod_name
        kwargs['num_part'] = len(needs)

        self._pod_nodes[pod_name] = Pod(kwargs=kwargs, needs=needs)
        self.set_last_pod(pod_name)

        return self

    def build(self) -> 'Flow':
        if self.built:
            self.logger.warning('flow was built!')
            return self

        _pod_edges = set()

        if 'gateway' not in self._pod_nodes:
            self.add_gateway()

        # direct all income peas' output to the current service
        for k, p in self._pod_nodes.items():
            for s in p.needs:
                if s not in self._pod_nodes:
                    raise FlowMissingPodError(f'{s} is not in this flow, misspelled name?')
                _pod_edges.add(f'{s}-{k}')

        for k in _pod_edges:
            s_name, e_name = k.split('-')
            edges_with_same_start = [ed for ed in _pod_edges if ed.startswith(s_name)]
            edges_with_same_end = [ed for ed in _pod_edges if ed.endswith(e_name)]

            s_pod = self._pod_nodes[s_name]
            e_pod = self._pod_nodes[e_name]

            # Rule
            # if a node has multiple income/outgoing peas,
            # then its socket_in/out must be PULL_BIND or PUB_BIND
            # otherwise it should be different than its income
            # i.e. income=BIND => this=CONNECT, income=CONNECT => this = BIND
            #
            # when a socket is BIND, then host must NOT be set, aka default host 0.0.0.0
            # host_in and host_out is only set when corresponding socket is CONNECT
            if len(edges_with_same_start) > 1 and len(edges_with_same_end) == 1:
                Pod.connect(s_pod, e_pod, first_socket_type=SocketType.PUB_BIND)

            elif len(edges_with_same_start) == 1 and len(edges_with_same_end) > 1:
                Pod.connect(s_pod, e_pod, first_socket_type=SocketType.PUSH_CONNECT)

            elif len(edges_with_same_start) == 1 and len(edges_with_same_end) == 1:
                # in this case, either side can be BIND
                # we prefer gateway to be always CONNECT so that multiple clients can connect to it
                # check if either node is gateway
                # this is the only place where gateway appears
                Pod.connect(s_pod, e_pod,
                            first_socket_type=SocketType.PUSH_BIND if e_name == 'gateway' else SocketType.PUSH_CONNECT)
            else:
                raise FlowTopologyError('found %d edges start with %s and %d edges end with %s, '
                                        'this type of topology is ambiguous and should not exist, '
                                        'i can not determine the socket type' % (
                                            len(edges_with_same_start), s_name, len(edges_with_same_end), e_name))

        for pod in self._pod_nodes.values():
            self.enter_context(pod)

        self.built = True
        self._show_success_message()

        # there doing a loop iteration?
        # just for unblock the loop, can let close event loop become easy.
        self.dummy_run()

        return self

    def set_last_pod(self, name: str) -> 'Flow':
        """
        Set a pod as the last pod in the flow, useful when modifying the flow.

        :param name: the name of the existing pod
        :return: a (new) flow object with modification
        """
        if name not in self._pod_nodes:
            raise FlowMissingPodError('%s can not be found in this Flow' % name)

        if self._last_changed_pod and name == self._last_changed_pod[-1]:
            pass
        else:
            self._last_changed_pod.append(name)

        return self

    @staticmethod
    def _parse_endpoints(op_flow, pod_name, endpoint, connect_to_last_pod=False) -> Set:
        # parsing needs
        if isinstance(endpoint, str):
            endpoint = [endpoint]
        elif not endpoint:
            if op_flow._last_changed_pod and connect_to_last_pod:
                endpoint = [op_flow._last_changed_pod[-1]]
            else:
                endpoint = []

        if isinstance(endpoint, list) or isinstance(endpoint, tuple):
            for idx, s in enumerate(endpoint):
                if s == pod_name:
                    raise FlowTopologyError('the income/output of a pod can not be itself')
        else:
            raise ValueError('endpoint=%s is not parsable' % endpoint)
        return set(endpoint)

    def predict(self, inputs: Union[List[List[str]], List[List[List[int]]]], timeout: int = 10000) -> Union[
        np.ndarray, Iterator[np.ndarray]]:
        from ..client.python import PyClient
        if not self.built:
            raise FlowEmptyError('before you call `predict()`, make sure the flow was built.')

        with PyClient(host=self.gateway.host, grpc_port=self.gateway.grpc_port, timeout=timeout) as client:
            return client.predict(inputs)

    def dummy_run(self):
        if self.gateway.rest_api:
            import requests
            requests.post(f'http://{self.gateway.host}:{self.gateway.rest_port}/{self.gateway.rest_url}')

    def _show_success_message(self):
        message = f'\t\t\tProtocol: \t{colored(self.protocol, attrs="bold")}'
        message = message + '\n\t\t💻 Local grpc access:\t' + colored(f'{self.gateway.host}:{self.gateway.grpc_port}',
                                                                      'cyan', attrs='underline')
        if self.gateway.rest_api:
            message = message + '\n\t\t💻 Local rest access:\t' + colored(
                f'http://{self.gateway.host}:{self.gateway.rest_port}/{self.gateway.rest_url}', 'cyan',
                attrs='underline')
        message = message + f'\n\t\t🔒 Private network:\t' + colored(f'{self.address_private}', 'cyan',
                                                                     attrs='underline')
        message = message + f'\n\t\t🌏 Public network:\t' + colored(f'{self.address_public}', 'cyan',
                                                                    attrs='underline')

        self.logger.success(f'Flow is ready to use!\n{message}')

    def __enter__(self):
        return self.build()

    def __exit__(self, exc_type, exc_val, exc_tb):
        super().__exit__(exc_type, exc_val, exc_tb)
        self.built = False
        self.logger.success(__stop_msg__)

    @property
    def gateway(self) -> GatewayPod:
        return self._pod_nodes['gateway']

    @property
    def protocol(self) -> str:
        if self.gateway.rest_api:
            return 'GRPC+REST'

        return 'GRPC'

    @property
    def address_private(self) -> str:
        return get_internal_ip()

    @property
    def address_public(self) -> str:
        return get_public_ip()
