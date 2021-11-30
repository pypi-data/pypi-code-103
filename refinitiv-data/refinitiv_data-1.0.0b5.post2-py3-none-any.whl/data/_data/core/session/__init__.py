# coding: utf-8

from ._session_type import SessionType
from ._session_definition import Definition
from . import desktop_session
from . import platform_session

from ._session import Session, DacsParams
from .tools import is_open, is_closed
from ._desktop_session import DesktopSession
from ._platform_session import PlatformSession

from .grant_refresh import *
from .grant_password import *

from ._default_session_manager import (
    get_default,
    set_default,
    _eikon_default_session_manager,
    _rd_default_session_manager,
    get_valid_session,
    EikonDefaultSessionManager,
    RDDefaultSessionManager,
)

from .connection import *

from .authentication_token_handler_thread import (
    AuthenticationTokenHandlerThread as _AuthenticationTokenHandlerThread,
)

from .stream_service_discovery.stream_service_discovery_handler import (
    StreamServiceInformation as _StreamServiceInformation,
)
from .stream_service_discovery.stream_service_discovery_handler import (
    DesktopStreamServiceDiscoveryHandler as _DesktopStreamServiceDiscoveryHandler,
)
from .stream_service_discovery.stream_service_discovery_handler import (
    PlatformStreamServiceDiscoveryHandler as _PlatformStreamServiceDiscoveryHandler,
)

from .stream_service_discovery.stream_connection_configuration import (
    StreamConnectionConfiguration as _StreamConnectionConfiguration,
)
from .stream_service_discovery.stream_connection_configuration import (
    RealtimeDistributionSystemConnectionConfiguration as _RealtimeDistributionSystemConnectionConfiguration,
)
