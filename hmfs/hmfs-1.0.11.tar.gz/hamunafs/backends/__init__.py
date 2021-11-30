from .base import BackendBase
from .qiniu import Qiniu
from .yaocdn import YaoStorage

backend_factory = {
    'qiniu': Qiniu,
    'yaocdn': YaoStorage
}