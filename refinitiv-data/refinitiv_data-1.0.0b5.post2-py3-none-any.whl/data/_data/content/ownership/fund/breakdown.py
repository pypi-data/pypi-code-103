from typing import Iterable, Union, TYPE_CHECKING

from ..._content_provider import ContentProviderLayer
from ..._content_type import ContentType
from ....tools import validate_types
from .._enums import StatTypes

if TYPE_CHECKING:
    from ....content._types import ExtendedParams


class Definition(ContentProviderLayer):
    """
    This class describe parameters to retrieve holdings data breakdown by Investors Types,
    Styles, Region, Countries, Rotations and Turnovers.

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

    stat_type: int, StatTypes
        The statType parameter specifies which statistics type to be returned.
        The types available are:
            - Investor Type (1)
            - Investment Style (2)
            - Region (3)
            - Rotation (4)
            - Country (5)
            - Metro Area (6)
            - Investor Type Parent (7)
            - Invest Style Parent (8)
    extended_params : ExtendedParams, optional
        If necessary other parameters.

    Examples
    --------
    >>> from refinitiv.data.content import ownership
    >>> definition = ownership.fund.breakdown.Definition("TRI.N", ownership.StatTypes.INVESTOR_TYPE)
    >>> response = definition.get_data()
    """

    def __init__(
        self,
        universe: Union[str, Iterable[str]],
        stat_type: Union[int, StatTypes],
        extended_params: "ExtendedParams" = None,
    ):
        validate_types(stat_type, [int, StatTypes], "stat_type")

        super().__init__(
            content_type=ContentType.OWNERSHIP_FUND_BREAKDOWN,
            universe=universe,
            stat_type=stat_type,
            extended_params=extended_params,
        )
