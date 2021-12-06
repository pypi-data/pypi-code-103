class YAMLEmptyError(Exception):
    """The yaml configs file is empty, nothing to read from there."""


class BadInputs(Exception):
    """Bad inputs"""


class PeaFailToStart(SystemError):
    """When pea is failed to started"""


class GRPCServerError(Exception):
    """Can not connect to the grpc gateway"""


class BadClient(Exception):
    """A wrongly defined grpc client, can not communicate with bert2tf server correctly """


class NoExplicitMessage(Exception):
    """Waiting until all partial messages are received"""


class UnknownRequestError(Exception):
    """Unknown request type"""


class DriverError(Exception):
    """Base driver error"""


class UnattachedDriver(DriverError):
    """Driver is not attached to any BasePea or executor"""


class NoDriverForRequest(DriverError):
    """No matched driver for this request """


class UnknownControlCommand(RuntimeError):
    """The control command received can not be recognized"""


class RequestLoopEnd(KeyboardInterrupt):
    """The event loop of BasePea ends"""


class FlowTopologyError(Exception):
    """Flow exception when the topology is ambiguous."""


class FlowMissingPodError(Exception):
    """Flow exception when a pod can not be found in the flow."""


class FlowEmptyError(Exception):
    """Flow exception when flow was not built and to call flow external function, such as `predict()` """


