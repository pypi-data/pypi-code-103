import json
from datetime import datetime
from django.db import transaction
from wcd_geo_db.const import DivisionLevel
from wcd_geo_db_sources.modules.process import stage
from wcd_geo_db.modules.code_seeker import ISO3166_SEEKER, registry as seeker_registry
from wcd_geo_db_sources.modules.merger.divisions import (
    merge_divisions, merge_division_translations
)
from wcd_geo_db_sources.modules.merger.dtos import DivisionItem, DivisionTranslationItem

from .._base import BaseImportRunner
from .parsers import registry
from .const import SOURCE, ImportStage
from .code_seeker import KATOTTG_SEEKER


UPLOAD_URL = (
    'https://www.minregion.gov.ua/wp-content/uploads/2021/04/kodyfikator-2.xlsx'
)
PARSER_VERSION = 'v1'
UKRAINIAN_LANGUAGE = 'uk'

UKRAINE = DivisionItem(
    name='Україна',
    code=(ISO3166_SEEKER.name, 'UA'),
    path=[],
    level=DivisionLevel.COUNTRY,
    types=['country'],
)


class KATOTTGImportRunner(BaseImportRunner):
    CHUNK_SIZE: int = 500
    source: str = SOURCE
    Stage: ImportStage = ImportStage
    default_config: dict = {
        'url': UPLOAD_URL,
        'version': PARSER_VERSION,
    }
    parser_registry: dict = registry

    @stage(Stage.MERGE)
    def run_merge(self):
        state = self.state.state

        if KATOTTG_SEEKER.name not in seeker_registry:
            seeker_registry.register(KATOTTG_SEEKER)

        with transaction.atomic():
            if 'country' not in state:
                merge_divisions([UKRAINE])
                self.update_state(partial_state={'country': True})
                return

        offset = state.get('merge_offset', 0)
        chunk = []
        count = self.CHUNK_SIZE
        nest = None

        with open(state['parsed_file'], 'r') as file:
            items = json.loads(file.read())
            l = len(items)

            while count >= 0 and offset < l:
                item = items[offset]

                if nest == None:
                    nest = len(item['path'])

                if len(item['path']) != nest:
                    break

                item['path'] = [UKRAINE['code']] + item['path']
                chunk.append(item)

                offset += 1
                count -= 1

            with transaction.atomic():
                merge_divisions(chunk)
                self.update_state(partial_state={'merge_offset': offset})

            if l > offset:
                return

        self.update_state(stage=self.Stage.MERGE_TRANSLATIONS)

    @stage(Stage.MERGE_TRANSLATIONS)
    def run_merge_translations(self):
        state = self.state.state

        if KATOTTG_SEEKER.name not in seeker_registry:
            seeker_registry.register(KATOTTG_SEEKER)

        offset = state.get('merge_translations_offset', 0)
        chunk = []
        count = self.CHUNK_SIZE

        with open(state['parsed_file'], 'r') as file:
            items = json.loads(file.read())
            next_offset = offset + count
            chunk = [
                DivisionTranslationItem(name=item['name'], code=item['code'])
                for item in items[offset:next_offset]
            ]

            with transaction.atomic():
                merge_division_translations(UKRAINIAN_LANGUAGE, chunk)
                self.update_state(partial_state={'merge_translations_offset': next_offset})

            if len(items) > next_offset:
                return

        self.update_state(stage=self.Stage.CLEANUP)
