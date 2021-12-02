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


import uvicorn
from ariadne import load_schema_from_path, make_executable_schema
from ariadne.asgi import GraphQL

from madam.domains.application import MainApplication
from madam.domains.entities.constants import MADAM_GRAPHQL_SCHEMA_PATH
from madam.slots.graphql.mutation import mutation
from madam.slots.graphql.query import query, timer_interface
from madam.slots.graphql.scalar import datetime_scalar, timedelta_scalar
from madam.slots.graphql.subscription import subscription, subscription_event_union_type


class ASGI2Protocol(GraphQL):
    """
    ASGI2Protocol class type required by uvicorn.run()
    """


def run(application: MainApplication, log_level: str = "error"):
    """
    Run Madam GraphQL server

    :param application: Madam main application instance
    :param log_level: Level of logging (default="error")
    :return:
    """
    # construct schema from all *.graphql files in directory
    type_defs = load_schema_from_path(str(MADAM_GRAPHQL_SCHEMA_PATH))
    # create executable schema instance
    schema = make_executable_schema(
        type_defs,
        query,
        timer_interface,
        mutation,
        subscription,
        timedelta_scalar,
        subscription_event_union_type,
        datetime_scalar,
    )
    # create asgi graphql application
    graphql_asgi_application = ASGI2Protocol(
        schema,
        debug=(log_level.upper() == "DEBUG"),
        context_value={"application": application},
    )
    # get graphql server config
    server_config = application.config.get_root_key("server")
    # run graphql server
    uvicorn.run(
        graphql_asgi_application,
        host=server_config["host"],
        port=server_config["port"],
        log_level=log_level.lower(),
    )
