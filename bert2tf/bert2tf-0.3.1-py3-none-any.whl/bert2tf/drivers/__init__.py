import logging

from ..baml import BAMLCompatible
from ..executors import AnyExecutor
from ..peapods.pea import BasePea
from ..proto import bert2tf_pb2


class DriverType(type(BAMLCompatible), type):
    pass


class BaseDriver(BAMLCompatible, metaclass=DriverType):
    """A :class:`BaseDriver` is a logic unit above the :class:`bert2tf.peapods.pea.BasePea`.
    It reads the protobuf message, extracts/modifies the required information and then return
    the message back to :class:`bert2f.peapods.pea.BasePea`.

    A :class:`BaseDriver` needs to be :attr:`attached` to a :class:`bert2tf.peapods.pea.BasePea` before using. This is done by
    :func:`attach`. Note that a deserialized :class:`BaseDriver` from file is always unattached.

    """

    def __init__(self, *args, **kwargs):
        super(BaseDriver, self).__init__()
        self.attached = False
        self.pea = None  # type: 'BasePea'

    def attach(self, pea: 'BasePea', *args, **kwargs) -> None:
        """Attach this driver to a :class:`bert2tf.peapods.pea.BasePea`

        :param pea: the pea to be attached.
        """
        self.pea = pea
        self.attached = True

    def __call__(self, *args, **kwargs):
        raise NotImplementedError

    @property
    def request(self) -> 'bert2tf_pb2.Request':
        """Get the current (typed) request, shortcut to ``self.pea.request``"""
        return self.pea.request

    @property
    def message(self) -> 'bert2tf_pb2.Message':
        """Get the current request, shortcut to ``self.pea.message``"""
        return self.pea.message

    @property
    def envelope(self) -> 'bert2tf_pb2.Envelope':
        """Get the current request, shortcut to ``self.pea.message``"""
        return self.message.envelope

    @property
    def logger(self) -> 'logging.Logger':
        """Shortcut to ``self.pea.logger``"""
        return self.pea.logger


class BaseExecutableDriver(BaseDriver):
    def __init__(self, method_name: str = None, *args, **kwargs):
        """ Initialize a :class:`BaseExecutableDriver`

        :param method: the function name of the executor that the driver feeds to
        """
        super().__init__(*args, **kwargs)
        self._executor = None

        self._method_name = method_name
        self._executor_fn = None

    def attach(self, executor: 'AnyExecutor', *args, **kwargs) -> None:
        super().attach(*args, **kwargs)
        self._executor = executor

        if self._method_name:
            self._executor_fn = getattr(self.executor, self._method_name, None)

    @property
    def executor(self) -> 'AnyExecutor':
        """the executor that attached """
        return self._executor

    @property
    def executor_fn(self):
        """the executor main function, can be customized, default `call`"""
        return self._executor_fn
