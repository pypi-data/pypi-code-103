from . import BaseDriver
from ..excepts import UnknownControlCommand, RequestLoopEnd
from ..proto import bert2tf_pb2


class ControlReqDriver(BaseDriver):
    """Handling the control request, by default it is installed for all :class:`bert2tf.peapods.pea.BasePea`"""

    def __call__(self, *args, **kwargs):
        if self.request.command == bert2tf_pb2.Request.ControlRequest.TERMINATE:
            self.envelope.status.code = bert2tf_pb2.Status.SUCCESS
            raise RequestLoopEnd
        else:
            raise UnknownControlCommand(f'don\'t know how to handle {self.request}')
