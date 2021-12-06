import os
from typing import Dict, List, TypeVar

from .metas import get_default_metas
from .requests import get_default_reqs
from ..baml import BAMLCompatible, BAMLCompatibleType
from ..excepts import UnattachedDriver, NoDriverForRequest
from ..logging.base import get_logger
from ..logging.profile import TimeContext

if False:
    from ..peapods.pea import BasePea

AnyExecutor = TypeVar('AnyExecutor', bound='BaseExecutor')


class ExecutorType(BAMLCompatibleType, type):
    def __call__(cls, *args, **kwargs):
        r = kwargs.pop('requests') if 'requests' in kwargs else {}
        m = kwargs.pop('metas') if 'metas' in kwargs else {}

        _to_device(m.get('device_id') if 'device_id' in m else -1)

        obj = type.__call__(cls, *args, **kwargs)
        getattr(obj, '_post_init_wrapper', lambda *x: None)(m, r)

        return obj


class BaseExecutor(BAMLCompatible, metaclass=ExecutorType):
    def __init__(self):
        self.logger = get_logger(os.environ.get('BERT2TF_PEA_NAME') or self.__class__.__name__.lower())

        self._drivers = {}  # type: Dict[str, List['BaseDriver']]

    def _post_init_wrapper(self, _metas: Dict = None, _requests: Dict = None):
        with TimeContext('post initiating, this may take some time', self.logger):
            self._fill_metas(_metas)
            self._fill_requests(_requests)
            self.post_init()

    def _fill_metas(self, _metas):
        _default_metas = get_default_metas()
        if _metas:
            _default_metas.update(_metas)

        for key, value in _default_metas.items():
            setattr(self, key, value)

    def _fill_requests(self, _requests):
        if not _requests:
            _requests = get_default_reqs(type.mro(self.__class__))

        # maybe default requests is None
        if _requests:
            # reset requests
            _requests_tmp = {}
            for key in _requests.keys():
                if isinstance(key, (list, tuple)):
                    for k in key:
                        _requests_tmp[(k,)] = _requests[key]
                else:
                    _requests_tmp[(key,)] = _requests[key]
            _requests = _requests_tmp

            # if control request is forget in YAML, then fill it
            if ('ControlRequest',) not in _requests:
                from ..drivers.control import ControlReqDriver
                _requests[('ControlRequest',)] = [ControlReqDriver()]

            for req_type, drivers in _requests.items():
                for r in req_type:
                    if r not in self._drivers:
                        self._drivers[r] = []
                    if self._drivers[r] != drivers:
                        self._drivers[r].extend(drivers)

    def post_init(self):
        """Post init, like model load pre train weights"""

    def attach(self, pea: 'BasePea', *args, **kwargs):
        for v in self._drivers.values():
            for driver in v:
                driver.attach(executor=self, pea=pea, *args, **kwargs)

        if pea:
            # replacing logger
            self.logger = getattr(pea, 'logger', self.logger)

    def deal(self, req_type, *args, **kwargs):
        if req_type in self._drivers:
            for d in self._drivers[req_type]:
                if d.attached:
                    d()
                else:
                    raise UnattachedDriver(d)
        else:
            raise NoDriverForRequest(req_type)


def _to_device(device_id: int):
    import os
    if device_id >= 0:
        os.environ['CUDA_VISIBLE_DEVICES'] = str(device_id)
