# coding: utf-8


from typing import Callable, TYPE_CHECKING

from ._rdp_stream import _RDPStream
from ._stream_factory import create_rdp_stream
from .base_stream import StreamOpenStateMixin
from ...content._content_type import ContentType
from ...core.session import get_valid_session
from ...tools import cached_property, create_repr

if TYPE_CHECKING:
    from ...content._types import ExtendedParams
    from . import OpenState
    from ...core.session import Session


class RDPStream(StreamOpenStateMixin):
    """
    Open an RDP stream.

    Parameters
    ----------

    service: string, optional
        name of RDP service

    universe: list
        RIC to retrieve item stream.

    view: list
        data fields to retrieve item stream

    parameters: dict
        extra parameters to retrieve item stream.

    api: string
        specific name of RDP streaming defined in config file. i.e.
        'streaming/trading-analytics/redi'

    extended_params: dict, optional
        Specify optional params
        Default: None

    Raises
    ------
    Exception
        If request fails or if Refinitiv Services return an error

    Examples
    --------
    >>> import refinitiv.data as rd
    >>> APP_KEY = "APP_KEY"
    >>> USERNAME = "USERNAME"
    >>> PASSWORD = "PASSWORD"
    >>> session = rd.session.platform.Definition(
    ...         app_key=APP_KEY,
    ...         grant=rd.session.platform.GrantPassword(
    ...             username=USERNAME,
    ...             password=PASSWORD,
    ...         )
    ... ).get_session()
    >>> session.open()
    >>>
    >>> tds = rd.delivery.rdp_stream.Definition(
    ...     service="",
    ...     universe=[],
    ...     view=[],
    ...     parameters={"universeType": "RIC"},
    ...     api='streaming/trading-analytics/redi'
    ... ).get_stream(session)
    >>> tds.open()
    """

    def __init__(
        self,
        session: "Session",
        service: str,
        universe: list,
        view: list,
        parameters: dict,
        api: str,
        extended_params: "ExtendedParams" = None,
    ) -> None:
        session = get_valid_session(session)
        self._session = session
        self._service = service
        self._universe = universe
        self._view = view
        self._parameters = parameters
        self._api = api
        self._extended_params = extended_params

    @cached_property
    def _stream(self) -> _RDPStream:
        return create_rdp_stream(
            ContentType.NONE,
            api=self._api,
            session=self._session,
            service=self._service,
            universe=self._universe,
            view=self._view,
            parameters=self._parameters,
            extended_params=self._extended_params,
        )

    def open(self) -> "OpenState":
        """
        Opens the RDPStream to start to stream. Once it's opened,
        it can be used in order to retrieve data.

        Parameters
        ----------

        Returns
        -------
        OpenState
            current state of this RDP stream object.

        Examples
        --------
        >>> from refinitiv.data.delivery import rdp_stream
        >>> definition = rdp_stream.Definition(
        ...                    service=None,
        ...                    universe=[],
        ...                    view=None,
        ...                    parameters={"universeType": "RIC"},
        ...                    api='streaming/trading-analytics/redi')
        >>> stream = definition.get_stream()
        >>> await stream.open_async()
        """
        state = self._stream.open()
        return self._convert_state(state)

    async def open_async(self) -> "OpenState":
        """
        Opens asynchronously the RDPStream to start to stream

        Parameters
        ----------

        Returns
        -------
        OpenState
            current state of this RDP stream object.

        Examples
        --------
        >>> from refinitiv.data.delivery import rdp_stream
        >>> definition = rdp_stream.Definition(
        ...                     service=None,
        ...                     universe=[],
        ...                     view=None,
        ...                     parameters={"universeType": "RIC"},
        ...                     api='streaming/trading-analytics/redi')
        >>> stream = definition.get_stream()
        >>> await stream.open_async()
        """
        state = await self._stream.open_async()
        return self._convert_state(state)

    def close(self) -> "OpenState":
        """
        Closes the RPDStream connection, releases resources

        Returns
        -------
        OpenState
            current state of this RDP stream object.

        Examples
        --------
        >>> from refinitiv.data.delivery import rdp_stream
        >>> definition = rdp_stream.Definition(
        ...                    service=None,
        ...                    universe=[],
        ...                    view=None,
        ...                    parameters={"universeType": "RIC"},
        ...                    api='streaming/trading-analytics/redi')
        >>> stream = definition.get_stream()
        >>> stream.open()
        >>> stream.close()
        """
        state = self._stream.close()
        return self._convert_state(state)

    def on_ack(self, on_ack: Callable) -> "RDPStream":
        """
        This function called when the stream received an ack message.

        Parameters
        ----------
        on_ack : Callable, optional
             Callable object to process retrieved ack data

        Returns
        -------
        RDPStream
            current instance it is a RDP stream object.

        Examples
        --------
        Prerequisite: The default session must be opened.
        >>> from datetime import datetime
        >>> from refinitiv.data.delivery import rdp_stream
        >>>
        >>> def display_response(response, event_type, event):
        ...     print(f'{response} - {event_type} received at {datetime.now}')
        ...     print(event)
        >>>
        >>> definition = rdp_stream.Definition(
        ...                     service=None,
        ...                     universe=[],
        ...                     view=None,
        ...                     parameters={"universeType": "RIC"},
        ...                     api='streaming/trading-analytics/redi')
        >>> stream = definition.get_stream()
        >>> stream.on_ack(lambda stream, event: display_response(stream, 'ack', event))
        >>>
        >>> stream.open()
        """
        self._stream.on_ack(on_ack)
        return self

    def on_response(self, on_response) -> "RDPStream":
        """
        This function called when the stream received an response message.

        Parameters
        ----------
        on_response : Callable, optional
             Callable object to process retrieved response data

        Returns
        -------
        RDPStream
            current instance it is a RDP stream object.

        Examples
        --------
        Prerequisite: The default session must be opened.
        >>> from datetime import datetime
        >>> from refinitiv.data.delivery import rdp_stream
        >>>
        >>> def display_response(response, event_type, event):
        ...     print(f'{response} - {event_type} received at {datetime.now}')
        ...     print(event)
        >>>
        >>> definition = rdp_stream.Definition(
        ...                    service=None,
        ...                    universe=[],
        ...                    view=None,
        ...                    parameters={"universeType": "RIC"},
        ...                    api='streaming/trading-analytics/redi')
        >>> stream = definition.get_stream()
        >>> stream.on_response(lambda stream, event: display_response(stream, 'response', event))
        >>>
        >>> stream.open()
        """
        self._stream.on_response(on_response)
        return self

    def on_update(self, on_update) -> "RDPStream":
        """
        This function called when the stream received an update message.

        Parameters
        ----------
        on_update : Callable, optional
             Callable object to process retrieved update data

        Returns
        -------
        RDPStream
            current instance it is a RDP stream object.

        Examples
        --------
        Prerequisite: The default session must be opened.
        >>> from datetime import datetime
        >>> from refinitiv.data.delivery import rdp_stream
        >>>
        >>> def display_response(response, event_type, event):
        ...     print(f'{response} - {event_type} received at {datetime.now}')
        ...     print(event)
        >>>
        >>> definition = rdp_stream.Definition(
        ...                    service=None,
        ...                    universe=[],
        ...                    view=None,
        ...                    parameters={"universeType": "RIC"},
        ...                    api='streaming/trading-analytics/redi')
        >>> stream = definition.get_stream()
        >>> stream.on_update(lambda stream, event: display_response(stream, 'update', event))
        >>>
        >>> stream.open()
        """
        self._stream.on_update(on_update)
        return self

    def on_alarm(self, on_alarm) -> "RDPStream":
        """
        This function called when the stream received an alarm message.

        Parameters
        ----------
        on_alarm : Callable, optional
             Callable object to process retrieved alarm data

        Returns
        -------
        RDPStream
            current instance it is a RDP stream object.

        Examples
        --------
        Prerequisite: The default session must be opened.
        >>> from datetime import datetime
        >>> from refinitiv.data.delivery import rdp_stream
        >>>
        >>> def display_response(response, event_type, event):
        ...     print(f'{response} - {event_type} received at {datetime.now}')
        ...     print(event)
        >>>
        >>> definition = rdp_stream.Definition(
        ...                    service=None,
        ...                    universe=[],
        ...                    view=None,
        ...                    parameters={"universeType": "RIC"},
        ...                    api='streaming/trading-analytics/redi')
        >>> stream = definition.get_stream()
        >>> stream.on_alarm(lambda stream, event: display_response(stream, 'alarm', event))
        >>>
        >>> stream.open()
        """
        self._stream.on_alarm(on_alarm)
        return self

    def __repr__(self):
        return create_repr(
            self,
            middle_path="delivery.rdp_stream",
            class_name=self.__class__.__name__,
        )
