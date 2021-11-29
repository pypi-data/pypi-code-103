#
#  Copyright (c) 2018-2019 Renesas Inc.
#  Copyright (c) 2018-2019 EPAM Systems Inc.
#

import logging

from aos_signer.service_config.singleton import Singleton

logger = logging.getLogger(__name__)


class KeyManagerException(Exception):
    pass


class KeyLoadException(KeyManagerException):
    pass


class KeysManager(metaclass=Singleton):
    def __init__(self):
        self._keys = {}

    def __getitem__(self, item):
        if item not in self._keys:
            try:
                with open(item, "rb") as fp:
                    self._keys[item] = fp.read()
            except Exception:
                raise KeyLoadException("Unable to read file '{}'.".format(item))
        return self._keys[item]
