from .._content_provider import ContentProviderLayer
from .._content_type import ContentType
from ...tools import create_repr


class Definition(ContentProviderLayer):
    """
    This class describe parameters to retrieve data for ESG universe.

    Parameters
    ----------
    closure : str, optional
        Specifies the parameter that will be merged with the request

    Examples
    --------
    >>> from refinitiv.data.content import esg
    >>> definition = esg.universe.Definition()
    >>> response = definition.get_data()

    >>> response = await definition.get_data_async()
    """

    def __init__(
        self,
        closure: str = None,
    ):
        super().__init__(
            content_type=ContentType.ESG_UNIVERSE,
            closure=closure,
        )

    def __repr__(self):
        return create_repr(
            self,
            middle_path="content.esg.universe",
            content=f"{{closure='{self._kwargs.get('closure')}'}}",
        )
