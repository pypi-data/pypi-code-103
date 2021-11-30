#!/usr/bin/env python3


# SAT: a jabber client
# Copyright (C) 2009-2021 Jérôme Poisson (goffi@goffi.org)
# Copyright (C) 2013-2016 Adrien Cossa (souliane@mailoo.org)

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

""" Configuration related useful methods """

import os
import csv
import json
from typing import Any
from configparser import ConfigParser, DEFAULTSECT, NoOptionError, NoSectionError
from xdg import BaseDirectory
from sat.core.log import getLogger
from sat.core.constants import Const as C
from sat.core.i18n import _
from sat.core import exceptions

log = getLogger(__name__)


def fixConfigOption(section, option, value, silent=True):
    """Force a configuration option value

    the option will be written in the first found user config file, a new user
    config will be created if none is found.

    @param section (str): the config section
    @param option (str): the config option
    @param value (str): the new value
    @param silent (boolean): toggle logging output (must be True when called from sat.sh)
    """
    config = ConfigParser()
    target_file = None
    for file_ in C.CONFIG_FILES[::-1]:
        # we will eventually update the existing file with the highest priority,
        # if it's a user personal file...
        if not silent:
            log.debug(_("Testing file %s") % file_)
        if os.path.isfile(file_):
            if file_.startswith(os.path.expanduser("~")):
                config.read([file_])
                target_file = file_
            break
    if not target_file:
        # ... otherwise we create a new config file for that user
        target_file = (
            f"{BaseDirectory.save_config_path(C.APP_NAME_FILE)}/{C.APP_NAME_FILE}.conf"
        )
    if section and section.upper() != DEFAULTSECT and not config.has_section(section):
        config.add_section(section)
    config.set(section, option, value)
    with open(target_file, "wb") as configfile:
        config.write(configfile)  # for the next time that user launches sat
    if not silent:
        if option in ("passphrase",):  # list here the options storing a password
            value = "******"
        log.warning(_("Config auto-update: {option} set to {value} in the file "
                      "{config_file}.").format(option=option, value=value,
                                                config_file=target_file))


def parseMainConf(log_filenames=False):
    """Look for main .ini configuration file, and parse it

    @param log_filenames(bool): if True, log filenames of read config files
    """
    config = ConfigParser(defaults=C.DEFAULT_CONFIG)
    try:
        filenames = config.read(C.CONFIG_FILES)
    except Exception as e:
        log.error(_("Can't read main config: {msg}").format(msg=e), exc_info=True)
    else:
        if log_filenames:
            if filenames:
                log.info(
                    _("Configuration was read from: {filenames}").format(
                        filenames=', '.join(filenames)))
            else:
                log.warning(
                    _("No configuration file found, using default settings")
                )

    return config


def getConfig(config, section, name, default=None):
    """Get a configuration option

    @param config (ConfigParser): the configuration instance
    @param section (str): section of the config file (None or '' for DEFAULT)
    @param name (str): name of the option
    @param default: value to use if not found, or Exception to raise an exception
    @return (unicode, list, dict): parsed value
    @raise: NoOptionError if option is not present and default is Exception
            NoSectionError if section doesn't exists and default is Exception
            exceptions.ParsingError error while parsing value
    """
    if not section:
        section = DEFAULTSECT

    try:
        value = config.get(section, name)
    except (NoOptionError, NoSectionError) as e:
        if default is Exception:
            raise e
        return default

    if name.endswith("_path") or name.endswith("_dir"):
        value = os.path.expanduser(value)
    # thx to Brian (http://stackoverflow.com/questions/186857/splitting-a-semicolon-separated-string-to-a-dictionary-in-python/186873#186873)
    elif name.endswith("_list"):
        value = next(csv.reader(
            [value], delimiter=",", quotechar='"', skipinitialspace=True
        ))
    elif name.endswith("_dict"):
        try:
            value = json.loads(value)
        except ValueError as e:
            raise exceptions.ParsingError("Error while parsing data: {}".format(e))
        if not isinstance(value, dict):
            raise exceptions.ParsingError(
                "{name} value is not a dict: {value}".format(name=name, value=value)
            )
    elif name.endswith("_json"):
        try:
            value = json.loads(value)
        except ValueError as e:
            raise exceptions.ParsingError("Error while parsing data: {}".format(e))
    return value


def getConf(
    conf: ConfigParser,
    prefix: str,
    section: str,
    name: str,
    default: Any
) -> Any:
    """Get configuration value from environment or config file

    @param str: prefix to use for the varilable name (see `name` below)
    @param section: config section to use
    @param name: unsuffixed name.
        For environment variable, `LIBERVIA_<prefix>_` will be prefixed (and name
        will be set to uppercase).
        For config file, `<prefix>_` will be prefixed (and DEFAULT section will be
        used).
        Environment variable has priority over config values. If Environment variable
        is set but empty string, config value will be used.
    @param default: default value to use if varilable is set neither in environment,
    nor in config
    """
    # XXX: This is a temporary method until parameters are refactored
    value = os.getenv(f"LIBERVIA_{prefix}_{name}".upper())
    return value or getConfig(conf, section, f"{prefix}_{name}", default)
