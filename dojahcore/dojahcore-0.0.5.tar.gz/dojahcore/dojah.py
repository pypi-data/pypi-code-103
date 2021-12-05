"""Entry point defined here"""

from dojahcore.core import DojahBase


from dojahcore.financial import Financial
from dojahcore.general import General
from dojahcore.identification import Identification
from dojahcore.messaging import Messaging
from dojahcore.server_error import ServerError
from dojahcore.verification import Verification
from dojahcore.wallet import Wallet

class Dojah(DojahBase):
    """Base class defined for Dojah Instance Method """

    def __init__(self, api_key=None,app_id=None) -> None:
        """ """
        DojahBase.__init__(self,api_key=api_key,app_id=app_id)
        self.financial  =  Financial
        self.general = General
        self.identification =  Identification
        self.messaging  =  Messaging
        self.verification  =  Verification
        self.wallet  =  Wallet