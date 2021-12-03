from px_client_builder import NestedClient
from .divisions import DivisionsClient


__all__ = 'BankClient',


class BankClient(NestedClient):
    divisions: DivisionsClient = DivisionsClient.as_property()
