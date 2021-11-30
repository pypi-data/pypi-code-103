__all__ = ["Definition"]

from typing import Optional, TYPE_CHECKING

from .._curves._interest_rate_curve_get_definition import InterestRateCurveGetDefinition
from ..._content_provider import ContentProviderLayer
from ..._content_type import ContentType
from ..._types import OptStr, ExtendedParams
from ....tools import create_repr


if TYPE_CHECKING:
    from .._enums._risk_type import RiskType
    from .._enums._asset_class import AssetClass


class Definition(ContentProviderLayer):
    """

    Parameters
    ----------
    index_name : str, optional
        Example:
            "EURIBOR"
    main_constituent_asset_class : AssetClass, optional
        See detail class AssetClass.
    risk_type : RiskType, optional
        See detail RiskType class.
    currency : str, optional
        The currency code of the interest rate curve.
    curve_tag : str, optional
        User defined string to identify the curve. It can be used to link output results
        to the curve definition. Only alphabetic, numeric and '- _.#=@' characters
        are supported.
    id : str, optional
        Id of the curve definition
    name : str, optional
        The name of the interest rate curve.
    source : str, optional
        Example:
            "Refinitiv"
    valuation_date: str, optional
        Example:
            "2019-08-21"
    extended_params : dict, optional
        If necessary other parameters.

    Methods
    -------
    get_data(session=session, on_response=on_response, **kwargs)
        Returns a response to the data platform
    get_data_async(session=None, on_response=None, **kwargs)
        Returns a response asynchronously to the data platform

    Examples
    --------
    >>> from refinitiv.data.content.ipa.curves import zc_curve_definition
    >>> definition = zc_curve_definition.Definition(source="Refinitiv")
    >>> response = definition.get_data()

    Using get_data_async
     >>> import asyncio
     >>> task = asyncio.gather(
     ...    definition.get_data_async(),
     ...)
     >>> asyncio.get_event_loop().run_until_complete(task)
     >>> response, *_ = task.result()
    """

    def __init__(
        self,
        index_name: OptStr = None,
        main_constituent_asset_class: Optional["AssetClass"] = None,
        risk_type: Optional["RiskType"] = None,
        currency: OptStr = None,
        curve_tag: OptStr = None,
        id: OptStr = None,
        name: OptStr = None,
        source: OptStr = None,
        valuation_date: OptStr = None,
        extended_params: ExtendedParams = None,
    ) -> None:
        request_item = InterestRateCurveGetDefinition(
            index_name=index_name,
            main_constituent_asset_class=main_constituent_asset_class,
            risk_type=risk_type,
            currency=currency,
            curve_tag=curve_tag,
            id=id,
            name=name,
            source=source,
            valuation_date=valuation_date,
        )
        super().__init__(
            content_type=ContentType.ZC_CURVE_DEFINITIONS,
            universe=request_item,
            extended_params=extended_params,
        )

    def __repr__(self):
        return create_repr(self, middle_path="content.ipa.curves.zc_curve_definition")
