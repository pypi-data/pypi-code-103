from typing import Union, Optional, Iterable, TYPE_CHECKING

from ..._content_provider import ContentProviderLayer
from ..._content_type import ContentType
from ....tools import validate_types

if TYPE_CHECKING:
    from ....content._types import ExtendedParams

optional_date = Optional[Union[str, "datetime.datetime"]]


class Definition(ContentProviderLayer):
    """
    This class describe parameters to retrieve details on stakeholders and strategic entities
    transactions that purchased the requested instruments. Further details of insider stakeholder
    can be requested along with their holding details. The operation supports pagination, however,
    it is dependent on user entitlements. Maximum 'count' value per page is 100. The default date
    range is 20 transactions, unless the 'start date' and 'end date' define a smaller range. The
    count value is checked by the service to determine if it does not exceed a specific number. If
    it does, the service will overwrite the client value to service default value.

    Parameters
    ----------
    universe: str, list of str
        The Universe parameter allows the user to define the single company for which the content is returned.
        Ownership content is delivered at the Company Level. The user can use the following identifier types,
        there is no need to define what identifier type is being used:
            - Organization PermID
            - Instrument PermID
            - QuotePermID
            - RIC Code
            - ISIN
            - CUSIP
            - SEDOL
            - Valoren
            - Wert
    start: str, datetime, optional
        The start parameter allows users to define the start date of a time series.
        Dates are to be defined either by absolute or relative syntax.
        Example, 20190529, -1Q, 1D, -3MA.
    end: str, datetime, optional
        The end parameter allows users to define the start date of a time series.
        Dates are to be defined either by absolute or relative syntax.
        Example, 20190529, -1Q, 1D, -3MA.
    limit: int, optional
        The limit parameter is used for paging. It allows users to select the number of records to be returned.
    extended_params : ExtendedParams, optional
        If necessary other parameters.

    Examples
    --------
    >>> from refinitiv.data.content import ownership
    >>> definition = ownership.insider.transaction_report.Definition("TRI.N", start="-1Q")
    >>> response = definition.get_data()
    """

    def __init__(
        self,
        universe: Union[str, Iterable[str]],
        start: optional_date = None,
        end: optional_date = None,
        limit: Optional[int] = None,
        extended_params: "ExtendedParams" = None,
    ):
        validate_types(limit, [int, type(None)], "limit")

        super().__init__(
            content_type=ContentType.OWNERSHIP_INSIDER_TRANSACTION_REPORT,
            universe=universe,
            start=start,
            end=end,
            limit=limit,
            extended_params=extended_params,
        )
