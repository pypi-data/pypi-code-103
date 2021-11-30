import os
import yaml
import copy
from pathlib import Path
from shutil import copyfile
from abc import ABC, abstractmethod


class Config:

    def __init__(self, conf_config):
        self._installfolder = Path(conf_config['execpath']).parent
        self.homevar = "{}/var/{}".format(str(Path.home()), conf_config['modulename'])

        if not os.path.exists(self.homevar):
            os.makedirs(self.homevar)

        self.refresh()

    @classmethod
    @abstractmethod
    def getClassName(cls):
        pass

    def getAll(self):
        return copy.deepcopy(self.config)

    def __getitem__(self, key):
        return self.config[key]

    def getDict(self):
        return self.config

    def _readConfig(self):
        # First get default values from template config file
        config_template_yml_path = os.path.join(self._installfolder, 'config-template.yml')
        try:
            # First try to get the template
            with open(config_template_yml_path, 'r') as config_template_file:
                template_config = yaml.load(config_template_file, Loader=yaml.FullLoader)
        except OSError as error:
            # No template
            template_config = None

        # Try to get the config
        try:
            config_yml_path = os.path.join(self.homevar, 'config.yml')
            with open(config_yml_path, 'r') as config_file:
                config = yaml.load(config_file, Loader=yaml.FullLoader)
        except OSError as error:
            config = None

        if config:
            if template_config:
                self._mergeConfig(config, template_config)
                return template_config
            else:
                return config
        else:
            if template_config:
                return template_config
            else:
                return None

    def refresh(self):
        self.config = self._readConfig()

    def _mergeConfig(self, source_config, dest_config):
        #Update keys
        for key, value in source_config.items():
            dest_config[key] = value

    def update(self, config_update):
        #Read fresh config file to be updated
        new_config = self._readConfig()

        #Update keys
        self._mergeConfig(config_update, new_config)

        config_yml_path = os.path.join(self.homevar, 'config.yml')
        try:
            with open(config_yml_path, 'w') as config_file:
                yaml.dump(new_config, config_file)
                self.config = new_config

        except OSError as error:
            pass

