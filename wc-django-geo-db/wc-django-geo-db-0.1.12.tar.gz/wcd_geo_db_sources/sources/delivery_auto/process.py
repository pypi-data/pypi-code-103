import json
import tempfile
from datetime import datetime
from itertools import groupby, chain
from django.conf import settings
from django.db import transaction, models
from wcd_geo_db.modules.bank.db.translations import DivisionTranslation
from wcd_geo_db_sources.modules.merger.merger import inject_synonyms
from wcd_geo_db_sources.modules.process import stage
from wcd_geo_db_sources.modules.merger.divisions import (
    merge_division_translations
)
from wc_delivery_auto.client import Client
from wc_delivery_auto.const import Culture
from wcd_geo_db_sources.modules.process import stage, ProcessFinished
from .._base import BaseImportRunner
from .parsers import registry
from .const import (
    GENERAL_LANGUAGE, SOURCE, ImportStage, UKRAINIAN_LANGUAGE, RUSSIAN_LANGUAGE, ENGLISH_LANGUAGE
)
from .code_seeker import DELIVERY_AUTO_SEEKER


PARSER_VERSION = 'v1'

CULTURE_ORDERING = {
    None: Culture.UA,
    Culture.UA: Culture.RU,
    Culture.RU: Culture.US,
    Culture.US: None
}
CULTURE_TO_LANGUAGE = {
    Culture.UA: UKRAINIAN_LANGUAGE,
    Culture.RU: RUSSIAN_LANGUAGE,
    Culture.US: ENGLISH_LANGUAGE,
}


def collect_translations(items: DivisionTranslation):
    collected = {}

    def to_key(item, key: str):
        collected[key] = collected.get(key) or {}
        collected[key][item.entity_id] = collected[key].get(item.entity_id) or {}
        collected[key][item.entity_id][item.language] = item

    for item in items:
        to_key(item, item.initial_name)
        to_key(item, item.name)

    return collected


class DELIVERY_AUTOImportRunner(BaseImportRunner):
    CHUNK_SIZE: int = 1500
    source: str = SOURCE
    Stage: ImportStage = ImportStage
    default_config: dict = {}
    parser_registry: dict = registry

    @stage(Stage.INITIAL)
    def run_initial(self):
        self.update_state(stage=self.Stage.UPLOADING, partial_state={
            'version': PARSER_VERSION,
        })

    def g(self, key, dflt=None):
        return self.state.state.get(key, dflt)

    def get_client(self):
        return Client()

    @stage(Stage.UPLOADING)
    def run_uploading(self):
        client = self.get_client()
        what = self.g('uploading_what', 'regions')
        culture = self.g('uploading_culture')
        filename = self.g('source_file')
        culture = CULTURE_ORDERING[culture]

        if filename is None:
            with tempfile.NamedTemporaryFile(delete=False) as tmp:
                tmp.write(b'{}')
            filename = tmp.name

        if what == 'regions' and culture is None:
            what = 'cities'
            culture = CULTURE_ORDERING[culture]

        if what == 'cities' and culture is None:
            return self.update_state(stage=self.Stage.PARSING, partial_state={
                'source_file': filename
            })

        response = (
            client.geo.cities.get_list(culture=culture, all=True)
            if what == 'cities' else
            client.geo.regions.get_list(culture=culture)
        )
        items = response['data']

        with open(filename, 'r+') as f:
            data = json.loads(f.read())
            f.seek(0)
            data[what] = data.get(what) or {}
            data[what][CULTURE_TO_LANGUAGE[culture]] = items
            f.write(json.dumps(data))
            f.truncate()

        self.update_state(stage=self.Stage.UPLOADING, partial_state={
            'uploading_what': what,
            'uploading_culture': culture,
            'source_file': filename,
        })

    @stage(Stage.MERGE)
    def run_merge(self):
        self.update_state(stage=self.Stage.MERGE_TRANSLATIONS)

    @stage(Stage.MERGE_TRANSLATIONS)
    def run_merge_translations(self):
        state = self.state.state

        offset = state.get('merge_translations_offset', 0)
        chunk = []
        count = self.CHUNK_SIZE

        with open(state['parsed_file'], 'r') as file:
            items = json.loads(file.read())
            next_offset = offset + count
            chunk = items[offset:next_offset]
            existing = collect_translations(
                DivisionTranslation.objects
                .annotate(initial_name=models.F('entity__name'))
                .filter(
                    # TODO: Also we should to same thing for reverse related
                    # language translations.
                    models.Q(initial_name__in=[x[0] for x in chunk]) |
                    models.Q(language=GENERAL_LANGUAGE, name__in=[x[0] for x in chunk])
                )
            )
            updateds = []
            createds = []

            with transaction.atomic():
                # Getting translatable name and dict of it's translations
                for name, group in chunk:
                    # If there is not such name - nothing to translate
                    if name not in existing:
                        continue

                    # For every entity id and a dict of translations
                    # for different languages it has:
                    for entity_id, existed in existing[name].items():
                        # For every language in grouped translation.
                        # Update entities translations to have all languages.
                        for lng, translateds in group.items():
                            translateds = [x for x in translateds if x]

                            if len(translateds) == 0:
                                continue

                            joined = ','.join(translateds)

                            if lng in existed:
                                item = existed[lng]
                                inject_synonyms(item, item.name, joined)
                                updateds.append(item)
                            else:
                                item = DivisionTranslation(
                                    entity_id=entity_id, language=lng,
                                    name=next(iter(translateds))
                                )
                                inject_synonyms(item, item.name, joined)
                                createds.append(item)

                DivisionTranslation.objects.bulk_create(createds, ignore_conflicts=True)
                DivisionTranslation.objects.bulk_update(updateds, fields=('synonyms',))

                self.update_state(partial_state={'merge_translations_offset': next_offset})

            if len(items) > next_offset:
                return

        self.update_state(stage=self.Stage.CLEANUP)

    @stage(Stage.CLEANUP)
    def run_cleanup(self):
        raise ProcessFinished()
