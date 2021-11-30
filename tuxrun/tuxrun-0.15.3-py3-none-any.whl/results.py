# -*- coding: utf-8 -*-
# vim: set ts=4
#
# Copyright 2021-present Linaro Limited
#
# SPDX-License-Identifier: MIT

import logging
import yaml

from tuxrun.yaml import yaml_load


LOG = logging.getLogger("tuxrun")


class Results:
    def __init__(self):
        self.__data__ = {}
        self.__ret__ = 0

    def parse(self, line):
        try:
            data = yaml_load(line)
        except yaml.YAMLError:
            LOG.debug(line)
            return
        if not data or not isinstance(data, dict):
            LOG.debug(line)
            return
        if data.get("lvl") != "results":
            return

        test = data.get("msg")
        if not set(["case", "definition"]).issubset(test.keys()):
            LOG.debug(line)
            return

        definition = test.pop("definition")
        case = test.pop("case")
        self.__data__.setdefault(definition, {})[case] = test
        if test["result"] == "fail":
            self.__ret__ = 1

    @property
    def data(self):
        return self.__data__

    def ret(self):
        return self.__ret__
