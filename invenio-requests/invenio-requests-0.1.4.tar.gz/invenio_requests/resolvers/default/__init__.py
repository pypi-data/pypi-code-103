# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 TU Wien.
#
# Invenio-Requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Default entity resolvers and proxies."""

from .records import RecordResolver
from .requests import RequestResolver
from .users import UserResolver

__all__ = (
    "RecordResolver",
    "RequestResolver",
    "UserResolver",
)
