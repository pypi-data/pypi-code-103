# -*- coding: utf-8 -*-
import pytest

from zwutils.config import Config

def test_config():
    cfg = Config('data/test_config.json', default={'fld0':123})
    assert cfg.fld0==123 and cfg.fld1=='a'