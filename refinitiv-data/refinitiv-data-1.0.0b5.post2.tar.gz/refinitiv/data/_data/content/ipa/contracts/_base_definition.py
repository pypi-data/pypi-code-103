from typing import Optional, TYPE_CHECKING

from .stream import Stream
from .._ipa_content_provider import IPAContentProviderLayer
from ..._content_type import ContentType

if TYPE_CHECKING:
    from ....core.session import Session


class BaseDefinition(IPAContentProviderLayer):
    def __init__(self, **kwargs) -> None:
        super().__init__(ContentType.CONTRACTS, **kwargs)

    def get_stream(
        self,
        session: Optional["Session"] = None,
    ) -> Stream:
        """
        Returns a streaming quantitative analytic service subscription

        Parameters
        ----------
        session : Session, optional
            Means the default session will be used

        Returns
        -------
        Stream

        Raises
        ------
        AttributeError
            If user didn't set default session.
        """
        definition = self._kwargs.get("definition")
        instrument_type = definition.get_instrument_type()
        json = definition.get_json()

        pricing_parameters = self._kwargs.get("pricing_parameters")

        definition = {
            "instrumentType": instrument_type,
            "instrumentDefinition": json,
        }

        if pricing_parameters:
            definition["pricingParameters"] = pricing_parameters.get_json()

        stream = Stream(
            session=session,
            fields=self._kwargs.get("fields"),
            universe=definition,
            extended_params=self._kwargs.get("extended_params"),
        )
        return stream

    def __eq__(self, other):
        definition = self._kwargs.get("definition")
        return definition == other

    def __repr__(self):
        repr_str = super().__repr__()
        new_str = f" {{name='{self._kwargs.get('definition')}'}}>"
        repr_str = repr_str.replace(">", new_str)
        return repr_str
