import json
from django.db import transaction
from wcd_geo_db.modules.bank.db import Division
from wcd_geo_db_sources.modules.process import stage
from wcd_geo_db_sources.modules.merger.code_seeker import get_code_seeker_registry
from wcd_geo_db_sources.modules.merger.divisions import find_by_codes, make_merge_division_code
from wcd_geo_db_sources.sources.katottg import KATOTTG_SEEKER
from wcd_geo_db_sources.sources.koatuu import KOATUU_SEEKER

from .._base import BaseImportRunner
from .parsers import registry
from .const import SOURCE, ImportStage


UPLOAD_URL = (
    'https://atu.decentralization.gov.ua/static/'
    '%D0%9F%D0%B5%D1%80%D0%B5%D1%85%D1%96%D0%B4%D0%BD%D0%B0%20%D1%82%D0'
    '%B0%D0%B1%D0%BB%D0%B8%D1%86%D1%8F%20%D0%B7%20%D0%9A%D0%9E%D0%90%D0'
    '%A2%D0%A3%D0%A3%20%D0%BD%D0%B0%20%D0%9A%D0%BE%D0%B4%D0%B8%D1%84%D1'
    '%96%D0%BA%D0%B0%D1%82%D0%BE%D1%80.xls'

)
PARSER_VERSION = 'v1'


def get_katottg(code: str):
    return {'code': make_merge_division_code(KATOTTG_SEEKER, code), 'path': []}


class KATOTTG_TO_KOATUUImportRunner(BaseImportRunner):
    CHUNK_SIZE: int = 10000
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
        seeker_registry = get_code_seeker_registry()

        if KATOTTG_SEEKER.name not in seeker_registry:
            seeker_registry.register(KATOTTG_SEEKER)

        if KOATUU_SEEKER.name not in seeker_registry:
            seeker_registry.register(KOATUU_SEEKER)

        with open(state['parsed_file'], 'r') as file:
            items = json.loads(file.read())

            offset = state.get('merge_offset', 0)
            chunk = items[offset:self.CHUNK_SIZE + offset]
            mapping = {katottg: koatuu for katottg, koatuu in chunk}
            existeds = find_by_codes(
                seeker_registry,
                [get_katottg(v) for v in mapping.keys()]
            )
            failures = []
            updateds = set()

            for katottg, koatuu in chunk:
                item = existeds.get_one([make_merge_division_code(KATOTTG_SEEKER, katottg)])

                if item is None:
                    failures.append((katottg, koatuu))
                    continue

                item.codes[KOATUU_SEEKER.name] = set(item.codes.get(KOATUU_SEEKER.name) or ())
                item.codes[KOATUU_SEEKER.name].add(koatuu)
                item.codes[KOATUU_SEEKER.name] = list(item.codes[KOATUU_SEEKER.name])
                updateds.add(item)

            offset += len(chunk)

            print(failures)

            with transaction.atomic():
                Division.objects.bulk_update(updateds, fields=('codes',))
                Division.objects.filter(pk__in=[x.pk for x in updateds]).update_relations_from_json()

                self.update_state(partial_state={'merge_offset': offset})

            if len(items) > offset:
                return

        self.update_state(stage=self.Stage.CLEANUP)
