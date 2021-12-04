import codecs
import os
from pathlib import Path

from ruamel.yaml import YAML


class Config:
    __instance = None

    @staticmethod
    def get_instance():
        """ Static access method. """
        if not Config.__instance:
            Config()
        return Config.__instance

    def __init__(self):
        if Config.__instance:
            raise Exception("This class is a singleton!")
        else:
            Config.__instance = self

    def load(self):
        config_folder = os.path.join(Path.home(), ".ucode")
        config_file = os.path.join(config_folder, f"config.yaml")

        res = {}
        if os.path.isfile(config_file):
            with open(config_file, encoding="utf-8") as f:
                yaml = YAML(typ="safe")
                res = yaml.load(f)

        return res or {}

    def save(self, config):
        config_folder = os.path.join(Path.home(), ".ucode")
        os.makedirs(config_folder, exist_ok=True)
        config_file = os.path.join(config_folder, f"config.yaml")

        with codecs.open(config_file, "w", encoding="utf-8") as f:
            yaml = YAML()
            yaml.indent(offset=2)
            yaml.dump(config, f)

        return None


if __name__ == "__main__":
    config = Config.load_config()
    print(config)
    Config.save_config({"token": "asdfsa"})
