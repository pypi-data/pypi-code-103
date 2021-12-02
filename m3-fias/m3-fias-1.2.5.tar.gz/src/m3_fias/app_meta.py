# coding: utf-8
from __future__ import absolute_import
from __future__ import unicode_literals

import m3_fias
import warnings


def register_actions():
    if m3_fias.config:
        m3_fias.config.backend.register_packs()
    else:
        warnings.warn("Не указана конфигурация m3-fias, паки пакета не будут инициализированы")
