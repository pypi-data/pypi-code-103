from configparser import ConfigParser
from pathlib import Path

try:
    from PySide6 import QtCore
except ImportError:
    from PySide2 import QtCore

from fime.exceptions import FimeException


def dequotify(string):
    if string.startswith(('"', "'")) and string.endswith(('"', "'")):
        return string[1:-1]
    else:
        return string


class Config:
    def __init__(self):
        self._configparser = ConfigParser()
        config_dir_path = Path(QtCore.QStandardPaths.writableLocation(QtCore.QStandardPaths.AppConfigLocation))
        config_path = config_dir_path / "fime.conf"
        if config_path.exists():
            print(f'Reading config file "{config_path}"')
            with open(config_path) as f:
                config_text = f.read()
            config_text = "[DEFAULT]\n" + config_text
            self._configparser.read_string(config_text)
        if (not self._configparser.has_option("DEFAULT", "jira_url") or
                not self._configparser.has_option("DEFAULT", "jira_token")):
            raise FimeException(f'Please add config file {config_path} '
                                        f'with config keys "jira_url" and "jira_token" in INI style')

    @property
    def jira_url(self):
        return dequotify(self._configparser["DEFAULT"]["jira_url"])

    @property
    def jira_token(self):
        return dequotify(self._configparser["DEFAULT"]["jira_token"])

    @property
    def tray_theme(self):
        val = dequotify(self._configparser.get("DEFAULT", "tray_theme", fallback="dark"))
        return val if val in ["light", "dark"] else "dark"
