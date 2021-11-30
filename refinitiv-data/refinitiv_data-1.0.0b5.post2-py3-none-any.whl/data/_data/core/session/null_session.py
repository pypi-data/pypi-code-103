from typing import TYPE_CHECKING

from . import SessionType
from ._session import Session
from ._session_cxn_type import SessionCxnType

if TYPE_CHECKING:
    from refinitiv.data import OpenState


class NullSession(Session):
    type = SessionType.NONE

    def __init__(self):
        Session.__init__(self, app_key="")

    def _get_session_cxn_type(self) -> SessionCxnType:
        return SessionCxnType.NONE

    def get_omm_login_message_key_data(self):
        return {}

    def get_rdp_login_message(self, stream_id):
        return {}

    async def open_async(self) -> "OpenState":
        # do nothing
        pass
