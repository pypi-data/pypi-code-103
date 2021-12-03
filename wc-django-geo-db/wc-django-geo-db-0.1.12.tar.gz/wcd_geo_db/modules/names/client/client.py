from px_client_builder import NestedClient
from .divisions import DivisionsClient


__all__ = 'NamesClient',


class NamesClient(NestedClient):
    divisions: DivisionsClient = DivisionsClient.as_property()
