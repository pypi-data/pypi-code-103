__all__ = ["Definition"]

from typing import List, TYPE_CHECKING

from numpy import iterable

from ..._content_provider import ContentProviderLayer
from ..._content_type import ContentType
from ..._types import ExtendedParams
from ....tools import create_repr


if TYPE_CHECKING:
    from refinitiv.data.content.ipa.curves import zc_curve_definition


class Definition(ContentProviderLayer):
    """

    Parameters
    ----------
    universe : list of zc_curve_definition.Definition
        See detail class zc_curve_definition.Definition.
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
    >>> from refinitiv.data.content.ipa.curves import zc_curve_definitions
    >>> definition1 = zc_curve_definition.Definition(source="Refinitiv")
    >>> definition2 = zc_curve_definition.Definition(source="Peugeot")
    >>> definitions = zc_curve_definitions.Definition(
    ...     universe=[definition1, definition2]
    ...)
    >>> response = definitions.get_data()

    Using get_data_async
     >>> import asyncio
     >>> task = asyncio.gather(
     ...    definitions.get_data_async(),
     ...)
     >>> asyncio.get_event_loop().run_until_complete(task)
     >>> response, *_ = task.result()
    """

    def __init__(
        self,
        universe: List["zc_curve_definition.Definition"],
        extended_params: ExtendedParams = None,
    ):

        if not iterable(universe):
            universe = [universe]

        super().__init__(
            content_type=ContentType.ZC_CURVE_DEFINITIONS,
            universe=universe,
            extended_params=extended_params,
        )

    def __repr__(self):
        return create_repr(self, middle_path="content.ipa.curves.zc_curve_definitions")
