from px_client_builder import NestedClient

from .formatter import FormatterClient


__all__ = 'AddressesClient',


class AddressesClient(NestedClient):
    formatter: FormatterClient = FormatterClient.as_property(
        bank_lookup=lambda self: self.parent.parent.bank
    )
