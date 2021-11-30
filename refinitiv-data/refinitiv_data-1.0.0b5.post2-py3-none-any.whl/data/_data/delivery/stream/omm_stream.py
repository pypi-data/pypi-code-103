# coding: utf8


from typing import Callable, Optional, TYPE_CHECKING

from ._omm_stream import _OMMStream
from ._stream_factory import create_omm_stream
from .base_stream import StreamOpenStateMixin
from ...content._content_type import ContentType
from ...content._types import ExtendedParams, Strings, OptStr
from ...core.session import get_valid_session
from ...tools import cached_property, create_repr

if TYPE_CHECKING:
    from . import OpenState
    from ...core.session import Session


class OMMStream(StreamOpenStateMixin):
    """
    Open an OMM stream.

    Parameters
    ----------
    name: string
        RIC to retrieve item stream.

    domain: string
        Specify item stream domain (MarketPrice, MarketByPrice, ...)
        Default : "MarketPrice"

    api: string, optional
        specific name of RDP streaming defined in config file.
        i.e. 'streaming/trading-analytics/redi'
        Default: 'streaming/pricing/main'

    service: string, optional
        Specify the service to subscribe on.
        Default: None

    fields: string or list, optional
        Specify the fields to retrieve.
        Default: None

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
    >>> APP_KEY = "app_key"
    >>> session = rd.session.desktop.Definition(app_key=APP_KEY).get_session()
    >>> session.open()
    >>>
    >>> euro = rd.delivery.omm_stream.Definition("EUR=").get_stream(session)
    >>> euro.open()
    >>>
    >>> def on_update(stream, msg):
    ...     print(msg)
    >>>
    >>> definition = rd.delivery.omm_stream.Definition("THB=")
    >>> thb = definition.get_stream(session)
    >>> thb.on_update(on_update)
    >>> thb.open()
    """

    def __init__(
        self,
        session: "Session",
        name: str,
        api: OptStr = None,
        domain: str = "MarketPrice",
        service: OptStr = None,
        fields: Optional[Strings] = None,
        extended_params: ExtendedParams = None,
    ) -> None:
        session = get_valid_session(session)
        self._session = session
        self._name = name
        self._api = api
        self._domain = domain
        self._service = service
        self._fields = fields
        self._extended_params = extended_params

    @cached_property
    def _stream(self) -> _OMMStream:
        return create_omm_stream(
            ContentType.NONE,
            api=self._api,
            session=self._session,
            name=self._name,
            domain=self._domain,
            service=self._service,
            fields=self._fields,
            extended_params=self._extended_params,
        )

    @property
    def status(self):
        status = {
            "status": self._stream.state,
            "code": self._stream.code,
            "message": self._stream.message,
        }
        return status

    def open(self, with_updates: bool = True) -> "OpenState":
        """
        Opens the OMMStream to start to stream.
        Once it's opened, it can be used in order to retrieve data.

        Parameters
        ----------
        with_updates : bool, optional
            actions:
                True - the streaming will work as usual
                        and the data will be received continuously.
                False - only one data snapshot will be received
                        (single Refresh 'NonStreaming') and
                        stream will be closed automatically.

            Defaults to True

        Returns
        -------
        OpenState
            current state of this OMM stream object.

        Examples
        --------
        >>> from refinitiv.data.delivery import omm_stream
        >>> definition = omm_stream.Definition("EUR")
        >>> stream = definition.get_stream()
        >>> stream.open()
        """
        state = self._stream.open(with_updates=with_updates)
        return self._convert_state(state)

    async def open_async(self, with_updates: bool = True) -> "OpenState":
        """
        Opens asynchronously the OMMStream to start to stream

        Parameters
        ----------
        with_updates : bool, optional
            actions:
                True - the streaming will work as usual
                        and the data will be received continuously.
                False - only one data snapshot will be received
                        (single Refresh 'NonStreaming') and
                        stream will be closed automatically.

        Returns
        -------
        OpenState
            current state of this OMM stream object.

        Examples
        --------
        >>> from refinitiv.data.delivery import omm_stream
        >>> definition = omm_stream.Definition("EUR")
        >>> stream = definition.get_stream()
        >>> await stream.open_async()
        """
        state = await self._stream.open_async(with_updates=with_updates)
        return self._convert_state(state)

    def close(self) -> "OpenState":
        """
        Closes the OMMStream connection, releases resources

        Returns
        -------
        OpenState
            current state of this OMM stream object.

        Examples
        --------
        >>> from refinitiv.data.delivery import omm_stream
        >>> definition = omm_stream.Definition("EUR")
        >>> stream = definition.get_stream()
        >>> stream.open()
        >>> stream.close()
        """
        state = self._stream.close()
        return self._convert_state(state)

    def on_refresh(self, func: Callable) -> "OMMStream":
        """
        This function called when the stream is opened or
        when the record is refreshed with a new image.
        This callback receives a full image.

        Parameters
        ----------
        func : Callable, optional
             Callable object to process retrieved refresh data

        Returns
        -------
        OMMStream
            current instance it is a OMM stream object.

        Examples
        --------
        Prerequisite: The default session must be opened.
        >>> from datetime import datetime
        >>> from refinitiv.data.delivery import omm_stream
        >>>
        >>> def display_response(response, event_type, event):
        ...      print(f'{response} - {event_type} received at {datetime.now}')
        ...      print(event)
        >>>
        >>> definition = omm_stream.Definition("EUR")
        >>> stream = definition.get_stream()
        >>> stream.on_refresh(
        ...     lambda stream, event: display_response(stream, 'refresh', event)
        ... )
        >>>
        >>> stream.open()
        """
        self._stream.on_refresh(func)
        return self

    def on_update(self, func: Callable) -> "OMMStream":
        """
        This function called when an update is received.

        Parameters
        ----------
        func : Callable, optional
            Callable object to process retrieved update data

        Returns
        -------
        OMMStream
            current instance it is a OMM stream object.

        Examples
        --------
        Prerequisite: The default session must be opened.
        >>> from datetime import datetime
        >>> from refinitiv.data.delivery import omm_stream
        >>>
        >>> def display_response(response, event_type, event):
        ...     print(f'{response} - {event_type} received at {datetime.now}')
        ...     print(event)
        >>>
        >>> definition = omm_stream.Definition("EUR")
        >>> stream = definition.get_stream()
        >>> stream.on_update(
        ...     lambda stream, event: display_response(stream, 'update', event)
        ... )
        >>>
        >>> stream.open()
        """
        self._stream.on_update(func)
        return self

    def on_status(self, func: Callable) -> "OMMStream":
        """
        This function these notifications are emitted when
        the status of one of the requested instruments changes

        Parameters
        ----------
        func : Callable, optional
            Callable object to process retrieved status data

        Returns
        -------
        OMMStream
            current instance it is a OMM stream object.

        Examples
        --------
        Prerequisite: The default session must be opened.
        >>> from datetime import datetime
        >>> from refinitiv.data.delivery import omm_stream
        >>>
        >>> def display_response(response, event_type, event):
        ...     print(f'{response} - {event_type} received at {datetime.now}')
        ...     print(event)
        >>>
        >>> definition = omm_stream.Definition("EUR")
        >>> stream = definition.get_stream()
        >>> stream.on_status(
        ...     lambda stream, event: display_response(stream, 'status', event)
        ... )
        >>>
        >>> stream.open()
        """
        self._stream.on_status(func)
        return self

    def on_complete(self, func: Callable) -> "OMMStream":
        """
        This function called on complete event

        Parameters
        ----------
        func : Callable, optional
            Callable object to process when retrieved on complete data.

        Returns
        -------
        OMMStream
            current instance it is a OMM stream object.

        Examples
        --------
        Prerequisite: The default session must be opened.
        >>> from datetime import datetime
        >>> from refinitiv.data.delivery import omm_stream
        >>>
        >>> def display_response(response, event_type, event):
        ...     print(f'{response} - {event_type} received at {datetime.now}')
        ...     print(event)
        >>>
        >>> definition = omm_stream.Definition("EUR")
        >>> stream = definition.get_stream()
        >>> stream.on_complete(
        ...     lambda stream, event: display_response(stream, 'complete', event)
        ... )
        >>>
        >>> stream.open()
        """
        self._stream.on_complete(func)
        return self

    def on_error(self, func: Callable) -> "OMMStream":
        """
        This function called when an error occurs

        Parameters
        ----------
        func : Callable, optional
            Callable object to process when retrieved error data.

        Returns
        -------
        OMMStream
            current instance it is a OMM stream object.

        Examples
        --------
        Prerequisite: The default session must be opened.
        >>> from datetime import datetime
        >>> from refinitiv.data.delivery import omm_stream
        >>>
        >>> def display_response(response, event_type, event):
        ...     print(f'{response} - {event_type} received at {datetime.now}')
        ...     print(event)
        >>>
        >>> definition = omm_stream.Definition("EUR")
        >>> stream = definition.get_stream()
        >>> stream.on_error(
        ...     lambda stream, event: display_response(stream, 'error', event)
        ... )
        >>>
        >>> stream.open()
        """
        self._stream.on_error(func)
        return self

    def __repr__(self):
        return create_repr(
            self,
            middle_path="delivery.omm_stream",
            class_name=self.__class__.__name__,
        )
