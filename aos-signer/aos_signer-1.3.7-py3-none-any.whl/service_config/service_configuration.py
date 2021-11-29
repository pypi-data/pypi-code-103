import json
import os

import importlib_resources as pkg_resources
import jsonschema
import ruamel.yaml
from colorama import Fore, Style

from aos_signer.signer.errors import SignerConfigError
from .models.build import Build
from .models.configuration import Configuration
from .models.publish import Publish
from .models.publisher import Publisher

CONFIG_NOT_FOUND_HELP = [
    "if you have configured service, run aos-signer tool from the parent directory of 'meta' dir",
    "If you are configuring service for the first time, run 'aos-signer init' first"
]


class ServiceConfiguration(object):

    DEFAULT_META_FOLDER = 'meta'
    DEFAULT_CONFIG_FILE_NAME = 'config.yaml'

    def __init__(self, file_path=None):
        self._config_path = file_path

        if file_path is None:
            file_path = os.path.join(self.DEFAULT_META_FOLDER, self.DEFAULT_CONFIG_FILE_NAME)

        if not os.path.isfile(file_path):
            raise SignerConfigError("Config file {} not found. Exiting...".format(file_path), CONFIG_NOT_FOUND_HELP)

        yaml = ruamel.yaml.YAML()
        print("{}Starting CONFIG VALIDATION process...{}".format(Fore.LIGHTBLACK_EX, Style.RESET_ALL))
        print("Validating config...           ", end='')

        with open(file_path, 'r') as file:
            try:
                schema = pkg_resources.files('aos_signer') / 'files/root_schema.json'
                loaded = yaml.load(file)
                with pkg_resources.as_file(schema) as schema_path:
                    with open(schema_path, 'r') as f:
                        sc = json.loads(f.read())
                        jsonschema.validate(loaded, schema=sc)
                self._publisher = Publisher.from_yaml(loaded.get('publisher'))
                self._publish = Publish.from_yaml(loaded.get('publish'))
                self._build = Build.from_yaml(loaded.get('build'))
                self._configuration = Configuration.from_yaml(loaded.get('configuration'))
                print(f"{Fore.GREEN}VALID{Style.RESET_ALL}")
            except (ruamel.yaml.parser.ParserError,
                    ruamel.yaml.scanner.ScannerError,
                    jsonschema.exceptions.ValidationError) as exc:
                print(f"{Fore.RED}ERROR{Style.RESET_ALL}")
                raise SignerConfigError(str(exc))

    @property
    def publisher(self):
        return self._publisher

    @property
    def publish(self):
        return self._publish

    @property
    def build(self):
        return self._build

    @property
    def configuration(self):
        return self._configuration

    @property
    def config_path(self):
        return self._config_path
