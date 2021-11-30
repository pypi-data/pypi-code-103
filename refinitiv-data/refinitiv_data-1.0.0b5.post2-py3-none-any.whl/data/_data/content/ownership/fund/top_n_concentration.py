from typing import Iterable, Union, TYPE_CHECKING

from ..._content_provider import ContentProviderLayer
from ..._content_type import ContentType
from ....tools import validate_types

if TYPE_CHECKING:
    from ....content._types import ExtendedParams


class Definition(ContentProviderLayer):
    """
    This class describe parameters to retrieve the calculated concentration data
    by top 10, 20, 50, 100 fund investors.

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
    count: int
        Number of records
    extended_params : ExtendedParams, optional
        If necessary other parameters.

    Examples
    --------
    >>> from refinitiv.data.content import ownership
    >>> definition = ownership.fund.top_n_concentration.Definition("TRI.N", 30)
    >>> response = definition.get_data()
    """

    def __init__(
        self,
        universe: Union[str, Iterable[str]],
        count: int,
        extended_params: "ExtendedParams" = None,
    ):
        validate_types(count, [int], "count")

        super().__init__(
            content_type=ContentType.OWNERSHIP_FUND_TOP_N_CONCENTRATION,
            universe=universe,
            count=count,
            extended_params=extended_params,
        )
