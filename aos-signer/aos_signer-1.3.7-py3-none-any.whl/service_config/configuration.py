#
#  Copyright (c) 2018-2019 Renesas Inc.
#  Copyright (c) 2018-2019 EPAM Systems Inc.
#

import os
from enum import Enum

import ruamel.yaml

from aos_signer.service_config.service_configuration import ServiceConfiguration
from aos_signer.service_config.singleton import Singleton
from aos_signer.signer.errors import SignerConfigError
from aos_signer.signer.user_credentials import UserCredentials


class ConfigurationKeys(Enum):
    _CONFIGURATION = "configuration"
    META = "meta"
    QUOTAS = "quotas"

    # Configuration
    PRIVATE_KEY = "private_key"
    CERTIFICATE = "certificate"
    REMOVE_NON_REGULAR_FILES = "remove_non_regular_files"
    DEFAULT_STATE = "default_state"


class Configuration(metaclass=Singleton):
    META_FOLDER = os.path.join('.', "meta")

    def __init__(self, config_file_name='config.yaml'):
        if config_file_name is None:
            raise SignerConfigError("Configuration file is not defined.")
        self._conf_file_path = os.path.join('meta', config_file_name)
        with open(self._conf_file_path, "r") as fp:
            yaml = ruamel.yaml.YAML()
            self._data = yaml.load(fp)
        config = ServiceConfiguration('meta/config.yaml')
        self._user_credentials = UserCredentials(config)
        self._user_credentials.find_sign_key_and_cert()

    def __getitem__(self, item: ConfigurationKeys):
        src = self._data
        if item in (
                ConfigurationKeys.PRIVATE_KEY,
                ConfigurationKeys.CERTIFICATE,
                ConfigurationKeys.REMOVE_NON_REGULAR_FILES,
                ConfigurationKeys.DEFAULT_STATE,
        ):
            src = self._data.get(ConfigurationKeys._CONFIGURATION.value, {})
        return src.get(item.value)

    def get_sign_key(self):
        return self._data.get('build').get('sign_key')

    def get_quotas(self):
        return self._data.get('configuration', {}).get('quotas')

    def get_alerts(self):
        return self._data.get('configuration', {}).get('alerts')

    def get_conf_path(self):
        return self._conf_file_path

    def get_sign_certificate(self):
        return self._data.get('build').get('sign_certificate')

    def get_symlinks(self):
        return self._data.get('build').get('symlinks', 'raise')

    @property
    def user_credentials(self):
        return self._user_credentials

    @property
    def meta_folder(self):
        return self.META_FOLDER
