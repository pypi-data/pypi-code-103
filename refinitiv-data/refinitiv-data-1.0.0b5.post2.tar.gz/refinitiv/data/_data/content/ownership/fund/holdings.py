from typing import Iterable, Union, TYPE_CHECKING
from typing import Optional

from ..._content_provider import ContentProviderLayer
from ..._content_type import ContentType
from ....tools import validate_types

if TYPE_CHECKING:
    from ....content._types import ExtendedParams


class Definition(ContentProviderLayer):
    """
    This class describe parameters to retrieve the holdings information for each fund investor companies.

    Parameters
    ----------
    universe: str, list of str
        The Universe parameter allows the user to define the companies for which the content is returned.
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
    limit: int, optional
        The limit parameter is used for paging. It allows users to select the number of records to be returned.
        Default page size is 100 or 20 (depending on the operation).
    extended_params : ExtendedParams, optional
        If necessary other parameters.

    Examples
    --------
    >>> from refinitiv.data.content import ownership
    >>> definition = ownership.fund.holdings.Definition("LP40189339")
    >>> response = definition.get_data()
    """

    def __init__(
        self,
        universe: Union[str, Iterable[str]],
        limit: Optional[int] = None,
        extended_params: "ExtendedParams" = None,
    ):
        validate_types(limit, [int, type(None)], "limit")

        super().__init__(
            content_type=ContentType.OWNERSHIP_FUND_HOLDINGS,
            universe=universe,
            limit=limit,
            extended_params=extended_params,
        )
