# coding: utf8

__all__ = ["Definition"]

from typing import TYPE_CHECKING

from ._data_grid_provider_layer import DataGridContentProviderLayer
from .data_grid_type import (
    DataGridType,
    data_grid_types_arg_parser,
    data_grid_type_value_by_content_type,
)
from ...tools import create_repr

if TYPE_CHECKING:
    from .._types import ExtendedParams, OptBool, OptDict


class Definition(DataGridContentProviderLayer):
    """
    This class describe the universe (list of instruments), the fields (a.k.a. data items) and
    parameters that will be requested to the data platform

    Parameters:
    ----------
    universe : list
        The list of RICs
    fields : list
        List of fundamental field names
    parameters : dict, optional
        Global parameters for fields
    use_field_names_in_headers : bool, optional
        If value is True we add field names in headers.
    extended_params : dict, optional
        Other parameters can be provided if necessary

    Examples
    --------
     >>> from refinitiv.data.content import fundamental_and_reference
     >>> definition = fundamental_and_reference.Definition(["IBM"], ["TR.Volume"])
     >>> definition.get_data()

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
        universe: list,
        fields: list,
        parameters: "OptDict" = None,
        use_field_names_in_headers: "OptBool" = False,
        extended_params: "ExtendedParams" = None,
    ):
        from .. import ContentType
        from ...delivery.data._data_provider_factory import get_api_config
        from refinitiv.data import get_config

        self.universe = universe
        self.fields = fields
        self.parameters = parameters
        self.use_field_names_in_headers = use_field_names_in_headers
        self.extended_params = extended_params

        config = get_api_config(ContentType.DATA_GRID_RDP, get_config())
        name_platform = config.setdefault("underlying-platform", DataGridType.RDP.value)
        name_platform = data_grid_types_arg_parser.get_str(name_platform)

        content_type = data_grid_type_value_by_content_type().get(name_platform)
        output = config.setdefault("output", None)
        super().__init__(
            content_type=content_type,
            universe=self.universe,
            fields=self.fields,
            parameters=self.parameters,
            use_field_names_in_headers=self.use_field_names_in_headers,
            extended_params=self.extended_params,
            output=output,
        )

    def __repr__(self):
        return create_repr(
            self,
            middle_path="content.fundamental_and_reference",
            content=f"{{name='{self.universe}'}}",
        )
