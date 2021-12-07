#!/usr/bin/python3

#     Copyright 2021. FastyBird s.r.o.
#
#     Licensed under the Apache License, Version 2.0 (the "License");
#     you may not use this file except in compliance with the License.
#     You may obtain a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#     Unless required by applicable law or agreed to in writing, software
#     distributed under the License is distributed on an "AS IS" BASIS,
#     WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#     See the License for the specific language governing permissions and
#     limitations under the License.

"""
Triggers module DI container
"""

# pylint: disable=no-value-for-parameter

# Python base dependencies
from typing import Dict, Union

# Library dependencies
from kink import di

# Library libs
from triggers_module.exchange import ModuleExchange
from triggers_module.models import db
from triggers_module.repositories import (
    ActionsRepository,
    ConditionsRepository,
    TriggersControlsRepository,
    TriggersRepository,
)

default_settings: Dict[str, Dict[str, Union[str, int, bool, None]]] = {
    "database": {
        "provider": "mysql",
        "host": "127.0.0.1",
        "port": 3306,
        "username": None,
        "password": None,
        "database": "fb_triggers_module",
        "create_tables": False,
    },
}


def create_container(settings: Dict[str, Dict[str, Union[str, int, bool, None]]]) -> None:
    """Register triggers module services"""
    module_settings: Dict[str, Dict[str, Union[str, int, bool, None]]] = {**default_settings, **settings}

    di["fb-triggers-module_database"] = db

    di[TriggersRepository] = TriggersRepository()  # type: ignore[call-arg]
    di["fb-triggers-module_trigger-repository"] = di[TriggersRepository]
    di[TriggersControlsRepository] = TriggersControlsRepository()  # type: ignore[call-arg]
    di["fb-triggers-module_trigger-control-repository"] = di[TriggersControlsRepository]
    di[ActionsRepository] = ActionsRepository()  # type: ignore[call-arg]
    di["fb-triggers-module_action-repository"] = di[ActionsRepository]
    di[ConditionsRepository] = ConditionsRepository()  # type: ignore[call-arg]
    di["fb-triggers-module_condition-repository"] = di[ConditionsRepository]

    di[ModuleExchange] = ModuleExchange()  # type: ignore[call-arg]
    di["fb-triggers-module_exchange"] = di[ModuleExchange]

    db.bind(
        provider="mysql",
        host=module_settings.get("database", {}).get("host", "127.0.0.1"),
        user=module_settings.get("database", {}).get("username", None),
        passwd=module_settings.get("database", {}).get("password", None),
        db=module_settings.get("database", {}).get("database", None),
        port=int(str(module_settings.get("database", {}).get("port", 3306))),
    )
    db.generate_mapping(create_tables=settings.get("database", {}).get("create_tables", False))
