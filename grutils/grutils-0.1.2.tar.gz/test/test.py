#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from grutils import utils
from grutils import error

err = error.Error()
print(utils.int_value_of("101.12", err, 0))
