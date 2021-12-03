import json
import tempfile
from datetime import datetime
from itertools import groupby, chain
from django.conf import settings
from django.db import transaction
from wcd_geo_db.const import DivisionLevel
from wcd_geo_db_sources.modules.process import stage
from wcd_geo_db.modules.code_seeker import ISO3166_SEEKER, registry as seeker_registry
from wcd_geo_db_sources.modules.merger.divisions import (
    merge_divisions, merge_division_translations
)
from wcd_geo_db_sources.modules.merger.dtos import DivisionItem, DivisionTranslationItem
from wc_novaposhta.client import Client
from wcd_geo_db_sources.sources.koatuu.code_seeker import KOATUU_SEEKER
from wcd_geo_db_sources.modules.process import (
    ProcessRunner, stage, ProcessFinished, ProcessCantProceed
)
from .._base import BaseImportRunner
from .parsers import registry
from .const import SOURCE, ImportStage
from .code_seeker import NOVAPOSHTA_SEEKER


PARSER_VERSION = 'v1'
UKRAINIAN_LANGUAGE = 'uk'
RUSSIAN_LANGUAGE = 'ru'


class NOVAPOSHTAImportRunner(BaseImportRunner):
    CHUNK_SIZE: int = 1500
    source: str = SOURCE
    Stage: ImportStage = ImportStage
    default_config: dict = {}
    parser_registry: dict = registry

    @stage(Stage.INITIAL)
    def run_initial(self):
        self.update_state(stage=self.Stage.UPLOADING, partial_state={
            'version': PARSER_VERSION,
            'api_key': settings.WCD_GEO_SOURCES_NOVAPOSHTA_API_KEY,
        })

    def g(self, key, dflt=None):
        return self.state.state.get(key, dflt)

    def get_client(self):
        return Client(key=self.g('api_key'))

    @stage(Stage.UPLOADING)
    def run_uploading(self):
        client = self.get_client()
        page = self.g('uploading_page', 1)
        filename = self.g('source_file')

        if page == 1 or filename is None:
            with tempfile.NamedTemporaryFile(delete=False) as tmp:
                tmp.write(b'[]')
            filename = tmp.name

        response = client.geo.settlements.get_list(page=page)
        items = response['data']

        if len(items) == 0:
            # No more pages
            return self.update_state(stage=self.Stage.PARSING, partial_state={
                'source_file': filename
            })

        with open(filename, 'r+') as f:
            data = json.loads(f.read())
            f.seek(0)
            f.write(json.dumps(data + items))
            f.truncate()

        self.update_state(stage=self.Stage.UPLOADING, partial_state={
            'uploading_page': page + 1,
            'source_file': filename,
        })

    @stage(Stage.PARSING)
    def run_parsing(self):
        state = self.state.state
        parse = self.parser_registry[state['version']]

        with open(state['source_file'], 'r') as file:
            parsed_file = parse(self, file=file)

        self.update_state(stage=self.Stage.MERGE, partial_state={
            'parsed_file': parsed_file
        })

    @stage(Stage.MERGE)
    def run_merge(self):
        state = self.state.state

        if KOATUU_SEEKER.name not in seeker_registry:
            seeker_registry.register(KOATUU_SEEKER)

        if NOVAPOSHTA_SEEKER.name not in seeker_registry:
            seeker_registry.register(NOVAPOSHTA_SEEKER)

        offset = state.get('merge_offset', 0)
        chunk = []
        count = self.CHUNK_SIZE

        with open(state['parsed_file'], 'r') as file:
            items = json.loads(file.read())
            to = offset + count
            chunk = items[offset:to]

            with transaction.atomic():
                merge_divisions(
                    chunk,
                    change_path=False, change_level=False, change_types=False,
                    should_create=False, lookup_on_singular_name_equality=True,
                )
                self.update_state(partial_state={'merge_offset': to})

            if len(items) > to:
                return

        self.update_state(stage=self.Stage.MERGE_TRANSLATIONS)

    @stage(Stage.MERGE_TRANSLATIONS)
    def run_merge_translations(self):
        state = self.state.state

        if KOATUU_SEEKER.name not in seeker_registry:
            seeker_registry.register(KOATUU_SEEKER)

        if NOVAPOSHTA_SEEKER.name not in seeker_registry:
            seeker_registry.register(NOVAPOSHTA_SEEKER)

        offset = state.get('merge_translations_offset', 0)
        chunk = []
        count = self.CHUNK_SIZE

        with open(state['parsed_file'], 'r') as file:
            items = json.loads(file.read())
            next_offset = offset + count
            key = lambda x: x['language']
            chunk = groupby(sorted(chain(*(
                item['translations'] for item in items[offset:next_offset]
            )), key=key), key=key)

            with transaction.atomic():
                for language, group in chunk:
                    g = list(group)
                    merge_division_translations(language, g)
                self.update_state(partial_state={'merge_translations_offset': next_offset})

            if len(items) > next_offset:
                return

        self.update_state(stage=self.Stage.CLEANUP)

    @stage(Stage.CLEANUP)
    def run_cleanup(self):
        raise ProcessFinished()
