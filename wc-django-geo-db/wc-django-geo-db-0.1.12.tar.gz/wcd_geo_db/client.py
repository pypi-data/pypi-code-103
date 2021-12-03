from px_client_builder import Client

from .modules.addresses import AddressesClient
from .modules.bank import BankClient
from .modules.names import NamesClient
from .conf import Settings


__all__ = 'GeoClient',


class GeoClient(Client):
    settings: Settings

    bank: BankClient = BankClient.as_property()
    names: NamesClient = NamesClient.as_property()
    addresses: AddressesClient = AddressesClient.as_property()

    def __init__(self, *_, settings: Settings, **kw):
        self.settings = settings

        super().__init__(**kw)
