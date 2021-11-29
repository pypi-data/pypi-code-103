# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function

import os
import re
import base64
from suanpan.utils import config


class GlobalVars(dict):

    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

    def __init__(self):
        self.pkgPath = os.path.dirname(os.path.dirname(__file__))
        defaultEnvYaml = os.path.join(self.pkgPath,
                                      "suanpan/configs/defaultEnvs.yaml")
        defaults = config.loadConfig(defaultEnvYaml)
        for k, v in self.getEnv(defaults).items():
            setattr(self, k, v)
        for k, v in self.getParam().items():
            setattr(self, k, v)
        self.tempStore = self.storageOssTempStore if self.storageType == "oss" else self.storageMinioTempStore

    def getEnv(self, defaults={}):
        suanpanEnvs = {}
        defaults.update(os.environ)
        for key, value in defaults.items():
            if key.startswith("SP_"):
                names = key.split("_")
                if len(names) > 1:
                    envName = "".join([
                        name.lower() if i == 0 else name.capitalize()
                        for i, name in enumerate(names[1:]) if name
                    ])
                    if envName:
                        suanpanEnvs[envName] = value
        return suanpanEnvs

    def getParam(self):
        if os.environ.get("SP_PARAM"):
            params = base64.b64decode(os.environ["SP_PARAM"]).decode()
            regex = r"(--[\w-]+)\s+(?:(?P<quote>[\"\'])(.*?)(?P=quote)|([^\'\"\s]+))"
            groups = re.findall(regex, params, flags=re.S)
            return {
                "".join([
                    key if i == 0 else key.capitalize()
                    for i, key in enumerate(group[0][2:].split("-"))
                ]): group[-2] or group[-1]
                for group in groups
            }
        return {}

    def get(self, key, default=None):
        return getattr(self, key, default) if getattr(self, key,
                                                      default) else default


g = GlobalVars()
