import fnmatch
import logging
import os
import yaml


DEFAULT_ALLOWED_MIME_TYPES = [
    'text/plain',
    'inode/x-empty',
]
LOG_LEVELS = {
    'critical': logging.CRITICAL,
    'error': logging.ERROR,
    'warning': logging.WARNING,
    'info': logging.INFO,
    'debug': logging.DEBUG,
}
ROLLBAR_TOKEN = 'ac917447c181447cbd50e4c6f108e1d2'
ROLLBAR_ENV = 'production'


class Config():
    def __init__(self):
        # See the README for explanations of these configs
        self.watch_directory = '/var/log/'
        self.ingest_endpoint = 'https://ingest.log.fit/log'
        self.source = 'unknown'
        self.log_level = logging.WARNING
        self.log_file = 'logfit.log'
        self.allowed_mime_types = DEFAULT_ALLOWED_MIME_TYPES
        self.ignore_paths = []

    def read_config_file(self, path):
        try:
            with open(path, 'r') as handle:
                data = yaml.safe_load(handle)
        except IOError:
            return
        self.parse_config_data(data)

    def parse_config_data(self, data):
        self.watch_directory = data.get(
            'watch_directory',
            self.watch_directory,
        )
        self.ingest_endpoint = data.get(
            'ingest_endpoint',
            self.ingest_endpoint,
        )
        self.source = data.get(
            'source',
            self.source,
        )
        self.log_level = self.parse_log_level(data.get('log_level', ''))
        self.log_file = os.path.abspath(data.get('log_file', self.log_file))
        self.allowed_mime_types = data.get(
            'allowed_mime_types',
            self.allowed_mime_types,
        )
        self.ignore_paths = data.get(
            'ignore_paths',
            self.ignore_paths,
        )
        self.ignore_paths.append(self.log_file)

    def parse_log_level(self, log_level_string):
        """
        Converts a log level string into a python enum in
        https://docs.python.org/3/library/logging.html#logging-levels
        """
        log_level_string = log_level_string.lower()
        log_level = LOG_LEVELS.get(log_level_string, self.log_level)
        return log_level

    def is_ignored_path(self, file_name):
        """ Check whether a path is ignored or not """
        for ignore_path in self.ignore_paths:
            if fnmatch.fnmatch(file_name, ignore_path):
                return True
        return False
