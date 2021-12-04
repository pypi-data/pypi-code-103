# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 TU Wien.
#
# Invenio-Requests is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Systemfields for calculated properties."""


from .base import CalculatedField
from .expired import ExpiredStateCalculatedField
from .state import StateCalculatedField

__all__ = (
    "CalculatedField",
    "ExpiredStateCalculatedField",
    "StateCalculatedField",
)
