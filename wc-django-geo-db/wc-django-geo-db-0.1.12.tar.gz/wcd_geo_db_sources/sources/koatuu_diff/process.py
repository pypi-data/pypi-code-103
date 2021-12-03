import json
from typing import List, Tuple
import requests
import tempfile
from django.db import transaction
from wcd_geo_db.modules.bank.db import Division
from wcd_geo_db_sources.modules.merger.code_seeker import get_code_seeker_registry
from wcd_geo_db_sources.modules.merger.divisions import find_by_codes, make_merge_division_code
from wcd_geo_db_sources.sources.katottg import KATOTTG_SEEKER
from wcd_geo_db_sources.sources.koatuu import KOATUU_SEEKER
from wcd_geo_db_sources.modules.process import (
    ProcessRunner, stage, ProcessFinished, ProcessCantProceed
)
from wcd_geo_db.const import DivisionLevel
from wcd_geo_db.modules.code_seeker import ISO3166_SEEKER, registry as seeker_registry
from wcd_geo_db_sources.modules.merger.dtos import DivisionItem, DivisionTranslationItem
from wcd_geo_db_sources.modules.merger.divisions import (
    merge_divisions, merge_division_translations
)
from wcd_geo_db_sources.sources.koatuu.parsers.shared.geo import order_geos

# FIXME: Shouldn't import encoder from here
from ..koatuu.parsers.shared import json_encoder
from ..koatuu.parsers import raw_parsers
from .._base import BaseImportRunner
from .const import SOURCE, ImportStage
from .diff import find_diff, Diff, DiffItem, Geo


UPLOAD_URLS = (
    'https://data.gov.ua/dataset/d945de87-539c-45b4-932a-7dda57daf8d9/resource/296adb7a-476a-40c8-9de6-211327cb3aa1/revision/10441/download',
    'https://data.gov.ua/dataset/d945de87-539c-45b4-932a-7dda57daf8d9/resource/296adb7a-476a-40c8-9de6-211327cb3aa1/revision/10442/download',
    'https://data.gov.ua/dataset/d945de87-539c-45b4-932a-7dda57daf8d9/resource/296adb7a-476a-40c8-9de6-211327cb3aa1/revision/50850/download',
    'https://data.gov.ua/dataset/d945de87-539c-45b4-932a-7dda57daf8d9/resource/296adb7a-476a-40c8-9de6-211327cb3aa1/revision/148926/download',
    'https://data.gov.ua/dataset/d945de87-539c-45b4-932a-7dda57daf8d9/resource/296adb7a-476a-40c8-9de6-211327cb3aa1/revision/197517/download',
    'https://data.gov.ua/dataset/d945de87-539c-45b4-932a-7dda57daf8d9/resource/296adb7a-476a-40c8-9de6-211327cb3aa1/revision/203509/download',
    'https://data.gov.ua/dataset/d945de87-539c-45b4-932a-7dda57daf8d9/resource/296adb7a-476a-40c8-9de6-211327cb3aa1/revision/203510/download',
    'https://data.gov.ua/dataset/d945de87-539c-45b4-932a-7dda57daf8d9/resource/296adb7a-476a-40c8-9de6-211327cb3aa1/revision/215040/download',
    'https://data.gov.ua/dataset/d945de87-539c-45b4-932a-7dda57daf8d9/resource/296adb7a-476a-40c8-9de6-211327cb3aa1/revision/223784/download',
)
PARSER_VERSIONS = {
    'hierarchy': 'hierarchical_v1',
    'plain_list': 'v1',
}
UKRAINIAN_LANGUAGE = 'uk'

UKRAINE = DivisionItem(
    name='Україна',
    code=(ISO3166_SEEKER.name, 'UA'),
    path=[],
    level=DivisionLevel.COUNTRY,
    types=['country'],
)


def prepare_diff_item(item: DiffItem) -> Geo:
    main = item['items'][0]
    rest = item['items'][1:]

    for r in rest:
        main['codes'] = main.get('codes') or []
        main['codes'].append(r['code'])
        main['codes'] += r.get('codes') or []

        if 'name' in r and r['name']:
            main['name'] = ','.join((main['name'], r['name']))

    return main


class KOATUU_DIFFImportRunner(BaseImportRunner):
    CHUNK_SIZE: int = 10000
    source: str = SOURCE
    Stage: ImportStage = ImportStage
    default_config: dict = {
        'urls': UPLOAD_URLS,
        'parsers': PARSER_VERSIONS,
    }
    parser_registry: dict = raw_parsers

    def resolve_staging(
        self,
        key: str,
        source_key: str,
        stage_current: Stage,
        stage_further: Stage
    ) -> Tuple[List[str], int, str, Stage]:
        state = self.state.state
        items = state.get(key, [])
        index = len(items)
        sources = state[source_key]
        source = sources[index]
        to_stage = stage_further if index == (len(sources) - 1) else stage_current

        return items, index, source, to_stage, sources


    @stage(Stage.INITIAL)
    def run_initial(self):
        self.update_state(stage=self.Stage.UPLOADING, partial_state={
            'urls': self.config['urls'],
            'parsers': self.config['parsers'],
        })

    @stage(Stage.UPLOADING)
    def run_uploading(self):
        key = 'source_files'
        sources, index, url, to_stage, _ = self.resolve_staging(
            key, 'urls', self.Stage.UPLOADING, self.Stage.PARSING
        )

        r = requests.get(url, allow_redirects=True)

        if r.status_code // 100 != 2:
            raise ProcessCantProceed(r.reason)

        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(r.content)
            self.update_state(stage=to_stage, partial_state={
                key: sources + [tmp.name]
            })

    @stage(Stage.PARSING)
    def run_parsing(self):
        state = self.state.state
        key = 'parsed_files'
        parseds, index, path, to_stage, _ = self.resolve_staging(
            key, 'source_files', self.Stage.PARSING, self.Stage.DIFF
        )

        with open(path, 'r') as file:
            data = json.loads(file.read())

            if isinstance(data, dict) and 'level1' in data:
                parser_name = state['parsers']['hierarchy']
            elif isinstance(data, list):
                parser_name = state['parsers']['plain_list']
            else:
                raise ProcessCantProceed('Unknown file format.')

            parse = self.parser_registry[parser_name]
            parsed = parse(data)

        with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp:
            tmp.write(json.dumps(
                parsed,
                default=json_encoder
            ))

        self.update_state(stage=to_stage, partial_state={
            key: parseds + [tmp.name]
        })

    @stage(Stage.DIFF)
    def run_diff(self):
        state = self.state.state
        diff_file = 'diff_file'
        key = 'diffed_files'
        parseds, index, path, to_stage, sources = self.resolve_staging(
            key, 'parsed_files', self.Stage.DIFF, self.Stage.MERGE
        )

        if index == 0:
            with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp:
                tmp.write('{}')

            self.update_state(partial_state={diff_file: tmp.name})
        else:
            with open(sources[index - 1], 'r') as file:
                older = json.loads(file.read())

            with open(path, 'r') as file:
                newer = json.loads(file.read())

            with open(state[diff_file], 'r') as file:
                diff = json.loads(file.read())

            current_unmatched = len([0 for x in diff.get('items', {}).values() if len(x['items']) == 0])
            diff, missing_amount = find_diff(older, newer, diff)
            items = diff.get('items', {}).values()

            new_unmatched = len([0 for x in items if len(x['items']) == 0])

            print('nones', len([x for x in items if len(x['items']) == 0]))
            print('ones', len([x for x in items if len(x['items']) == 1]))
            print('twos', len([x for x in items if len(x['items']) == 2]))
            print('threes', len([x for x in items if len(x['items']) == 3]))
            print('mores', len([x for x in items if len(x['items']) > 3]))

            with open(state[diff_file], 'w') as file:
                file.write(json.dumps(diff, default=json_encoder))

            print(
                f'Difference between files [{index - 1}] and [{index}] is: {missing_amount}'
            )
            print(f'Unmatched items count in new set is: {new_unmatched-current_unmatched}')
            print(f'Overall unmatched items count is: {new_unmatched}')

        self.update_state(stage=to_stage, partial_state={
            key: parseds + [path]
        })

    @stage(Stage.PREPARE_DIFF)
    def run_prepare_diff(self):
        state = self.state.state

        prepared = []

        with open(state['diff_file'], 'r') as file:
            items: Diff = json.loads(file.read())
            prepared = order_geos([
                prepare_diff_item(item) for item in items['items'].values()
            ])

        with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp:
            tmp.write(json.dumps(prepared, default=json_encoder))

        self.update_state(stage=self.Stage.MERGE, partial_state={'prepared_file': tmp.name})

    @stage(Stage.MERGE)
    def run_merge(self):
        state = self.state.state

        if KOATUU_SEEKER.name not in seeker_registry:
            seeker_registry.register(KOATUU_SEEKER)

        with transaction.atomic():
            if 'country' not in state:
                merge_divisions([UKRAINE])
                self.update_state(partial_state={'country': True})
                return

        offset = state.get('merge_offset', 0)
        chunk = []
        count = self.CHUNK_SIZE
        nest = None

        with open(state['prepared_file'], 'r') as file:
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
                merge_divisions(chunk, change_path=False, change_level=False, change_types=False)
                self.update_state(partial_state={'merge_offset': offset})

            if l > offset:
                return

        self.update_state(stage=self.Stage.MERGE_TRANSLATIONS)

    @stage(Stage.MERGE_TRANSLATIONS)
    def run_merge_translations(self):
        state = self.state.state

        if KOATUU_SEEKER.name not in seeker_registry:
            seeker_registry.register(KOATUU_SEEKER)

        offset = state.get('merge_translations_offset', 0)
        chunk = []
        count = self.CHUNK_SIZE

        with open(state['prepared_file'], 'r') as file:
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

    @stage(Stage.CLEANUP)
    def run_cleanup(self):
        # FIXME: Merge cleanup

        raise ProcessFinished()
