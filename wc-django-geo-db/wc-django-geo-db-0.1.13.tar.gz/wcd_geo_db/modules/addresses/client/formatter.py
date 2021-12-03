from typing import Any, Callable, Dict, Optional, Sequence, Tuple, TYPE_CHECKING
from functools import cached_property
from px_client_builder import NestedClient
from wcd_geo_db.modules.code_seeker.query import CodeSeekSeq

from ...bank.dtos import DivisionDTO, DivisionTranslationDTO
from ..dtos import AddressDefinitionDTO, FormattedAddressDTO

if TYPE_CHECKING:
    from ...bank import BankClient


__all__ = 'FormatterClient',


class FormatterClient(NestedClient):
    _bank_lookup: Callable

    def __init__(self, *_, bank_lookup: Callable = None, **kw):
        assert bank_lookup is not None, 'Bank lookuper is mandatory.'

        super().__init__(**kw)

        self._bank_lookup = bank_lookup

    bank: 'BankClient' = cached_property(lambda x: x._bank_lookup(x))

    def _make_formatted_address(
        self,
        definition: AddressDefinitionDTO,
        divisions_map: Dict[int, DivisionDTO] = {},
        translations_map: Dict[int, DivisionTranslationDTO] = {},
    ) -> Optional[FormattedAddressDTO]:
        path = definition.get('divisions_path')

        if not path:
            return None

        divisions = [
            translations_map.get(id, None) or divisions_map[id]
            for id in path
            if id in translations_map or id in divisions_map
        ]

        return FormattedAddressDTO(
            id=str(path[-1]),
            divisions=divisions,
            formatted_address=', '.join(d.name for d in reversed(divisions))
        )

    def _normalize_address_definitions(
        definitions: Sequence[AddressDefinitionDTO],
    ) -> Tuple[Sequence[AddressDefinitionDTO], dict]:
        return definitions

    def format_addresses(
        self,
        definitions: Sequence[AddressDefinitionDTO],
        language: str,
        fallback_languages: Sequence[str] = []
    ) -> Sequence[Optional[FormattedAddressDTO]]:
        """Formats addresses definitions.

        Result will be in the same order as passed in definitions.
        If address can't be formatted pastes None on it's place.
        """
        definitions: Sequence[AddressDefinitionDTO] = list(definitions)
        division_ids = set()
        divisions = []

        for definition in definitions:
            # FIXME: Made an adequate normalization that wouldn't
            # mutate initial structure.
            path = definition['divisions_path'] = list(definition.get('divisions_path') or ())

            for i, division in enumerate(path):
                if division is None:
                    continue

                if isinstance(division, int):
                    division_ids.add(division)
                elif isinstance(division, DivisionDTO):
                    divisions.append(division)
                    division_ids.add(division.id)
                    path[i] = division.id
                else:
                    raise TypeError(
                        f'Wrong division in path: {type(division)}, {repr(division)}.'
                    )

        # FIXME: A little bit inefficient.
        # There must be a way to fallback to division names if no translation
        # here in on query.
        translations = self.bank.divisions.get_translations(
            ids=division_ids,
            language=language, fallback_languages=fallback_languages
        )
        translations_map = {t.entity_id: t for t in translations}

        no_translated_ids = division_ids - translations_map.keys()

        if len(no_translated_ids) > 0:
            divisions += list(self.bank.divisions.get(ids=no_translated_ids))

        divisions_map = {d.id: d for d in divisions}

        return [
            self._make_formatted_address(
                definition,
                divisions_map=divisions_map,
                translations_map=translations_map
            )
            for definition in definitions
        ]
