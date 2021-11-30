from typing import Iterable, Union

from ._base_definition import BaseDefinition
from .._content_type import ContentType
from ...tools import validate_types


class Definition(BaseDefinition):
    """
    This class describe parameters to retrieve ESG standart measures data.

    Parameters
    ----------
    universe : str, list of str
        The Universe parameter allows the user to define the company they
        want content returned for, ESG content is delivered at the Company Level.

    start : int, optional
        Start & End parameter allows the user to request
         the number of Financial Years they would like returned.

    end : int, optional
        Start & End parameter allows the user to request
        the number of Financial Years they would like returned.

    closure : str, optional
        Specifies the parameter that will be merged with the request

    Examples
    --------
    >>> from refinitiv.data.content import esg
    >>> definition = esg.standard_measures.Definition("BNPP.PA")
    """

    def __init__(
        self,
        universe: Union[str, Iterable[str]],
        start: int = None,
        end: int = None,
        closure: str = None,
    ):
        validate_types(start, [int, type(None)], "start")
        validate_types(end, [int, type(None)], "end")

        super().__init__(
            content_type=ContentType.ESG_STANDARD_MEASURES,
            universe=universe,
            start=start,
            end=end,
            closure=closure,
        )

    def __repr__(self):
        get_repr = super().__repr__()
        return get_repr.replace("esg", "esg.standard_measures")
