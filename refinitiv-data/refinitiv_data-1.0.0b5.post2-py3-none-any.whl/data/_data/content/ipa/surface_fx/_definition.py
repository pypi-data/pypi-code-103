__all__ = ["Definition"]


from .._ipa_content_provider import IPAContentProviderLayer
from .._surfaces import FxSurfaceRequestItem
from .._surfaces._surface_types import SurfaceParameters, SurfaceLayout
from ..._content_type import ContentType
from ..._types import ExtendedParams, OptStr
from ....tools import create_repr


class Definition(IPAContentProviderLayer):
    """
    Create a Fx data Definition object.

    Parameters
    ----------
    surface_layout : SurfaceLayout
        See details in SurfaceLayout class
    surface_parameters : SurfaceParameters
        See details in SurfaceParameters class
    underlying_definition : dict
       Dict with instrument_code
       Example:
            {"fxCrossCode": "EURUSD"}
    surface_tag : str, optional
        A user defined string to describe the volatility surface
    extended_params : dict, optional
        If necessary other parameters

    Methods
    -------
    get_data(session=session, on_response=on_response, **kwargs)
        Returns a response to the data platform
    get_data_async(session=None, on_response=None, **kwargs)
        Returns a response asynchronously to the data platform

    Examples
    --------
    >>> from refinitiv.data.content.ipa.surfaces import surface_fx
    >>> definition = surface_fx.Definition(
    ...    underlying_definition={"fxCrossCode": "EURUSD"},
    ...    surface_tag="FxVol-EURUSD",
    ...    surface_layout=surface_fx.SurfaceLayout(
    ...    format=surface_fx.Format.MATRIX
    ...    ),
    ...    surface_parameters=surface_fx.FxCalculationParams(
    ...    x_axis=surface_fx.Axis.DATE,
    ...    y_axis=surface_fx.Axis.STRIKE,
    ...    calculation_date="2018-08-20T00:00:00Z"
    ...    )
    ...)
    >>>
    """

    def __init__(
        self,
        surface_layout: SurfaceLayout,
        surface_parameters: SurfaceParameters,
        underlying_definition: dict,
        surface_tag: OptStr = None,
        extended_params: ExtendedParams = None,
    ):
        request_item = FxSurfaceRequestItem(
            surface_layout=surface_layout,
            surface_parameters=surface_parameters,
            underlying_definition=underlying_definition,
            surface_tag=surface_tag,
        )
        super().__init__(
            content_type=ContentType.SURFACES,
            universe=request_item,
            extended_params=extended_params,
        )

    def __repr__(self):
        return create_repr(self, middle_path="content.ipa.surfaces.surface_fx")
