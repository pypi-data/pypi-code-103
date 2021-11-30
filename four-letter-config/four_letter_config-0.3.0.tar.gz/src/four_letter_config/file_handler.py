# -*- coding: utf-8 -*-

"""

four_letter_config.file_handler

Handle JSON and YAML files, preferring YAML.

Copyright (C) 2021 Rainer Schwarzbach

This file is part of four_letter_config.

four_letter_config is free software: you can redistribute it and/or modify
it under the terms of the MIT License.

four_letter_config is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
See the LICENSE file for more details.

"""


import json
import os

import yaml


#
# Constants
#


MODE_READ = "rt"
MODE_WRITE = "wt"
ENCODING = "utf-8"

YAML_FILE = "YAML file"
JSON_FILE = "JSON file"

SUPPORTED_FILE_TYPES = {YAML_FILE: (".yaml", ".yml"), JSON_FILE: (".json",)}


#
# Exceptions
#


class FiletypeNotSupported(Exception):

    """Raised if an unsupported fie type was encountered"""

    ...


class InvalidFormatError(Exception):

    """Raised if file content is not loadable using the YAML or JSON parser"""

    ...


#
# Functions
#


def load_yaml(file_name):
    """Load a YAML file"""
    try:
        with open(file_name, mode=MODE_READ, encoding=ENCODING) as input_file:
            return yaml.safe_load(input_file)
        #
    except yaml.parser.ParserError as yaml_parser_error:
        raise InvalidFormatError(
            f"YAML parsing failed:\n{yaml_parser_error.problem}"
        ) from yaml_parser_error
    #


def dump_to_yaml(file_name, data):
    """Dump data to a YAML file"""
    with open(file_name, mode=MODE_WRITE, encoding=ENCODING) as output_file:
        yaml.dump(data, output_file, default_flow_style=False)
    #
    return True


def load_json(file_name):
    """Load a JSON file"""
    try:
        with open(file_name, mode=MODE_READ, encoding=ENCODING) as input_file:
            return json.load(input_file)
        #
    except json.decoder.JSONDecodeError as json_decode_error:
        raise InvalidFormatError(
            *json_decode_error.args
        ) from json_decode_error
    #


def dump_to_json(file_name, data):
    """Dump data to a JSON file"""
    with open(file_name, mode=MODE_WRITE, encoding=ENCODING) as output_file:
        json.dump(data, output_file, indent=2)
    #
    return True


#
# Generalized functions
#


LOADERS = {
    YAML_FILE: load_yaml,
    JSON_FILE: load_json,
}

DUMPERS = {
    YAML_FILE: dump_to_yaml,
    JSON_FILE: dump_to_json,
}


def __dispatch(registry, file_name, *data):
    """Read or write a YAML or JSON file,
    dispatch to the matching function depending on the file extension.
    """
    file_extension = os.path.splitext(file_name)[1]
    for file_type, applicable_function in registry.items():
        if file_extension in SUPPORTED_FILE_TYPES[file_type]:
            return applicable_function(file_name, *data)
        #
    #
    raise FiletypeNotSupported(
        f"File extension {file_extension!r} not supported"
    )


def read_file(file_name):
    """Read a YAML or JSON file and return the contained data
    (autodetect the file type via the extension)
    """
    return __dispatch(LOADERS, file_name)


def write_to_file(file_name, data):
    """Dump the data structure to a YAML or JSON file
    (autodetect the file type via the extension)
    """
    return __dispatch(DUMPERS, file_name, data)


def comparable_form(data):
    """Return a serialized form of data
    to enable comparing data structures.
    """
    return yaml.dump(data, default_flow_style=False, sort_keys=True)


# vim: fileencoding=utf-8 ts=4 sts=4 sw=4 autoindent expandtab syntax=python:
