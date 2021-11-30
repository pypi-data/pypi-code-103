from typing import Iterable, Union, TYPE_CHECKING

from ..._content_provider import ContentProviderLayer
from ..._content_type import ContentType

if TYPE_CHECKING:
    from .._enums import SortOrder
    from ....content._types import ExtendedParams


class Definition(ContentProviderLayer):
    """
    This class describe parameters to retrieve the latest 5 buy or sell activites for the requested company.

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
    sort_order: str, SortOrder
        The sortOrder parameter specifies ascending (asc) or descending (desc) Sort Order.
    extended_params : ExtendedParams, optional
        If necessary other parameters.

    Examples
    --------
    >>> from refinitiv.data.content import ownership
    >>> definition = ownership.fund.recent_activity.Definition("TRI.N", ownership.SortOrder.ASCENDING)
    >>> response = definition..get_data()
    """

    def __init__(
        self,
        universe: Union[str, Iterable[str]],
        sort_order: Union[str, "SortOrder"],
        extended_params: "ExtendedParams" = None,
    ):
        super().__init__(
            content_type=ContentType.OWNERSHIP_FUND_RECENT_ACTIVITY,
            universe=universe,
            sort_order=sort_order,
            extended_params=extended_params,
        )
