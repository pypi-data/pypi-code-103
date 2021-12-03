import os
import requests
import tempfile

from wcd_geo_db_sources.modules.process import (
    ProcessRunner, stage, ProcessFinished, ProcessCantProceed
)
from wcd_geo_db_sources.modules.merger.dtos import DivisionItem

from .const import BaseImportStage


PARSER_VERSION = 'v1'


class BaseImportRunner(ProcessRunner):
    Stage: BaseImportStage = BaseImportStage
    default_config: dict = {
        'url': None,
        'version': PARSER_VERSION,
    }
    parser_registry: dict

    @stage(Stage.INITIAL)
    def run_initial(self):
        self.update_state(stage=self.Stage.UPLOADING, partial_state={
            'url': self.config['url'],
            'version': self.config['version'],
        })

    @stage(Stage.UPLOADING)
    def run_uploading(self):
        state = self.state.state
        r = requests.get(state['url'], allow_redirects=True)

        if r.status_code // 100 != 2:
            raise ProcessCantProceed(r.reason)

        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(r.content)
            self.update_state(stage=self.Stage.PARSING, partial_state={
                'source_file': tmp.name
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
        raise NotImplementedError('Implement merge stage.')

    @stage(Stage.MERGE_TRANSLATIONS)
    def run_merge_translations(self):
        raise NotImplementedError('Implement merge translations stage.')

    @stage(Stage.CLEANUP)
    def run_cleanup(self):
        state = self.state.state

        for key in ('source_file', 'parsed_file'):
            if state.get(key):
                os.unlink(state[key])

        raise ProcessFinished()
