# coding: utf-8
from typing import TYPE_CHECKING

from .rdp_stream import RDPStream
from ...content._types import ExtendedParams

if TYPE_CHECKING:
    from ...core.session import Session


class Definition:
    """
    This class to subscribe to streaming items of RDP streaming protocol
    that exposed by the underlying of the Refinitiv Data

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
        specific name of RDP streaming defined
        in config file. i.e. 'streaming/trading-analytics/redi'
    extended_params: dict, optional
        Specify optional params
        Default: None

    Examples
    --------
    >>> import refinitiv.data as rd
    >>> from refinitiv.data.delivery import rdp_stream
    >>> definition = rd.delivery.rdp_stream.Definition(
    ...     service=None,
    ...     universe=[],
    ...     view=None,
    ...     parameters={"universeType": "RIC"},
    ...     api='streaming/trading-analytics/redi'
    ... )
    """

    def __init__(
        self,
        service: str,
        universe: list,
        view: list,
        parameters: dict,
        api: str,
        extended_params: ExtendedParams = None,
    ) -> None:
        self._service = service
        self._universe = universe
        self._view = view
        self._parameters = parameters
        self._api = api
        self._extended_params = extended_params

    def get_stream(self, session: "Session" = None) -> RDPStream:
        stream = RDPStream(
            session=session,
            service=self._service,
            universe=self._universe,
            view=self._view,
            parameters=self._parameters,
            api=self._api,
            extended_params=self._extended_params,
        )
        return stream
