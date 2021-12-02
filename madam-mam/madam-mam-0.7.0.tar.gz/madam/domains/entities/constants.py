# Copyright 2021 Vincent Texier
#
# This file is part of MADAM.
#
# MADAM is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# MADAM is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with MADAM.  If not, see <https://www.gnu.org/licenses/>.

"""
Madam constants data module
"""
from pathlib import Path

PROJECT_PATH = Path(__file__).parents[3].expanduser()
PACKAGE_PATH = PROJECT_PATH.joinpath("madam")
BPMN_XSD_PATH = PACKAGE_PATH.joinpath("adapters/bpmn/assets/BPMN20.xsd")
DATABASE_MIGRATIONS_PATH = PACKAGE_PATH.joinpath(
    "adapters/repository/assets/migrations"
)
MADAM_CONFIG_PATH = PROJECT_PATH.joinpath("madam.yaml")
MADAM_GRAPHQL_SCHEMA_PATH = PACKAGE_PATH.joinpath("slots/graphql/assets/schema.graphql")
MADAM_LOG_LEVEL = "ERROR"
