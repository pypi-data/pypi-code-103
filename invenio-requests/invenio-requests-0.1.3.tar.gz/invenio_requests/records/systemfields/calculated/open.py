# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 TU Wien.
#
# Invenio-Requests is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Systemfield for calculating the ``is_open`` property of a request."""


from .base import CalculatedField


class OpenStateCalculatedField(CalculatedField):
    """Systemfield for calculating whether or not the request is open."""

    def __init__(self, key=None):
        """Constructor."""
        super().__init__(key=key, use_cache=False)

    def calculate(self, record):
        """Calculate the ``is_open`` property of the request."""
        status = getattr(record, self.key)
        return record.type.available_statuses.get(status, False)
