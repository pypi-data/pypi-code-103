from collections import namedtuple
from configparser import ConfigParser, SectionProxy
import json
from pathlib import Path
from typing import Union, Iterable, Dict, Optional


class LegionConfig:
    _Legion = namedtuple('_Legion', ['meta_queue', 'reporters_dir', 'package_overrides'])
    Reporter = namedtuple('Reporter', ['name', 'meta_queue', 'file_url', 'requirements',
                                       'config', 'delay', 'description', 'failure_threshold_error',
                                       'failure_threshold_critical'])

    def __init__(self, configuration: Union[str, Path]):
        self.config = ConfigParser(comment_prefixes=('#'), inline_comment_prefixes=('#'))
        self.config.read(configuration, encoding='utf-8-sig') if isinstance(configuration, Path) else self.config.read_string(configuration)

    @property
    def legion(self) -> '_Legion':
        return self._Legion(**self.config['legion'])

    def _reporter_of(self, config_section: SectionProxy) -> 'Reporter':
        return self.Reporter(name=config_section.name[len('reporter:'):],
                             meta_queue=self.legion.meta_queue,
                             file_url=config_section['file_url'],
                             requirements=json.loads(config_section.get('requirements', '[]')),
                             config=json.loads(config_section.get('config', '{}')),
                             delay=config_section.getfloat('delay', 0),
                             description=config_section.get('description', ''),
                             failure_threshold_error=config_section.getint('failure_threshold_error',5),
                             failure_threshold_critical=config_section.getint('failure_threshold_critical',10))

    def reporter(self, reporter: str) -> 'Reporter':
        return self.reporters_dict[reporter]

    @property
    def package_overrides(self) -> Optional[Dict[str, str]]:
        if self.config.has_option('legion', 'package_overrides'):
            return json.loads(self.legion.package_overrides)
        return None

    @property
    def reporters(self) -> Iterable[Reporter]:
        return [self._reporter_of(self.config[section]) for section in self.config.sections() if section.startswith('reporter:')]

    @property
    def reporters_dict(self) -> Dict[str, Reporter]:
        return {reporter.name: reporter for reporter in self.reporters}

    @property
    def dict(self):
        return self.config._sections

    @property
    def reporters_dir(self) -> Path:
        return Path(self.legion.reporters_dir)
