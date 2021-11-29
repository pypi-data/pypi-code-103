# -*- coding: utf-8 -*-
# @File    : permission.py
# @Time    : 2021/11/26 5:27 下午

from typing import List
from authority import Definition


class Template(object):
    def __init__(
        self, project: str, name: str, policies: List[Definition], namespace: str = None
    ):
        self.project = project
        self.name = name
        self.policies = policies
        self.namespace = namespace


class Permission(object):
    def __init__(
        self,
        group: str,
        name: str,
        identifier: str,
        description: str,
        templates: List[Template],
        permission_type: str = "",
        serial_no: int = 0,
    ):
        self.group = group
        self.name = name
        self.identifier = identifier
        self.description = description
        self.permission_type = permission_type
        self.serial_no = serial_no
        self.templates = templates
