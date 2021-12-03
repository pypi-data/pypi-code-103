from typing import Any, Optional, Sequence
from django.utils.translation import get_language
from wcd_geo_db.modules.addresses.dtos import FormattedAddressDTO
from wcd_geo_db.modules.bank.client import DivisionsClient
from wcd_geo_db.modules.addresses.client import FormatterClient


__all__ = (
    'Preparator',
    'DivisionsPreparator',
)


class Preparator:
    type = None

    def prepare(items: Sequence) -> Sequence:
        return items

    def get_value(value: Any) -> Any:
        return value

    def get_label(value: Any) -> Any:
        return value


class DivisionsPreparator(Preparator):
    client: DivisionsClient
    formatter_client: FormatterClient
    type = FormattedAddressDTO

    def __init__(
        self,
        client: DivisionsClient,
        formatter_client: FormatterClient,
    ):
        self.client = client
        self.formatter_client = formatter_client

    def prepare(self, ids: Sequence[int], language: Optional[str] = None) -> FormattedAddressDTO:
        language = language or get_language()
        # Converting to list here is important as it wouldn't
        # make a subquery here:
        # FIXME: Remove magic of id's resolving from here. It must
        # happened somewhere before method execution.
        ids = [x if isinstance(x, (int, str)) else x.id for x in ids]

        addresses = self.formatter_client.format_addresses(
            # FIXME:
            # This here makes a second query(because we're trying to get
            # an additional path parameter). And it's inefficient to
            # search twice.
            # May be there is some way not to execute query somwhere before.
            # [
            #     {'divisions_path': path, 'division': id}
            #     for [id, path] in ids.values_list('id', 'path')
            # ],
            [
                {'division': dto, 'divisions_path': dto.path}
                for dto in self.client.get(ids, keep_ordering=True)
            ],
            language=language
        )

        return addresses

    def get_value(self, value: FormattedAddressDTO):
        return value.id

    def get_label(self, value: FormattedAddressDTO):
        return value.formatted_address
