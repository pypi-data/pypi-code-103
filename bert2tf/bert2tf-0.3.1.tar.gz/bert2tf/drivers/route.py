from . import BaseDriver
from .control import ControlReqDriver
from ..excepts import NoExplicitMessage
from ..proto import bert2tf_pb2
from ..proto.helper import is_data_request


class ForwardDriver(BaseDriver):
    """Forward the message to next pod"""

    def __call__(self, *args, **kwargs):
        pass


class RouteDriver(ControlReqDriver):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.idle_dealers = set()
        self.is_pollin_paused = False

    def __call__(self, *args, **kwargs):
        if is_data_request(self.request):
            self.logger.debug(self.idle_dealers)
            if self.idle_dealers:
                dealer_id = self.idle_dealers.pop()
                self.envelope.receiver_id = dealer_id
                if not self.idle_dealers:
                    self.pea.zmqlet.pause_pollin()
                    self.is_pollin_paused = True

            else:
                raise RuntimeError('if this router connects more than one dealer, '
                                   'then this error should never be raised. often when it '
                                   'is raised, some Pods must fail to start, so please go '
                                   'up and check the first error message in the log')

        elif self.request.command == bert2tf_pb2.Request.ControlRequest.IDLE:
            self.idle_dealers.add(self.envelope.client_id)
            self.logger.debug(f'{self.envelope.client_id} is idle')
            if self.is_pollin_paused:
                self.pea.zmqlet.resume_pollin()
                self.is_pollin_paused = False
            # need raise this exception, otherwise the idle message will propagate
            raise NoExplicitMessage
        else:
            super().__call__(*args, **kwargs)
