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

import asyncio
import uuid
from asyncio import sleep
from typing import AsyncGenerator

from ariadne import SubscriptionType, UnionType
from graphql.type.definition import GraphQLResolveInfo

from madam.domains.application import MainApplication
from madam.domains.entities.events import (
    ApplicationEvent,
    JobEvent,
    TimerEvent,
    WatchfolderEvent,
    WorkflowEvent,
    WorkflowInstanceEvent,
)
from madam.domains.interfaces.events import EventInterface

subscription = SubscriptionType()


@subscription.source("events")
async def events_generator(
    _, info: GraphQLResolveInfo
) -> AsyncGenerator[EventInterface, None]:
    """
    Push instance event object

    :param _: Parent
    :param info: Context
    :return:
    """
    application = info.context["application"]  # type: MainApplication
    subscription_id = str(uuid.uuid4())
    application.graphql_api.subscriptions[subscription_id] = []
    try:
        while True:
            if len(application.graphql_api.subscriptions[subscription_id]) > 0:
                event = application.graphql_api.subscriptions[subscription_id].pop(0)
                yield event
            await sleep(1)
    except asyncio.CancelledError:
        del application.graphql_api.subscriptions[subscription_id]
        raise


@subscription.field("events")
async def events_resolver(event: EventInterface, _) -> EventInterface:
    """
    Subscription events field resolver

    :param event: Event instance
    :param _:
    :return:
    """
    return event


subscription_event_union_type = UnionType("SubscriptionEvent")


@subscription_event_union_type.type_resolver
def resolve_subscription_event_union_type(obj, *_):
    """
    Return type of object as string for this interface

    :param obj: Instance to resolve
    :param _: Unused
    :return:
    """
    type_ = None
    if isinstance(obj, WatchfolderEvent):
        type_ = "WatchfolderEvent"

    if isinstance(obj, WorkflowEvent):
        type_ = "WorkflowEvent"

    if isinstance(obj, WorkflowInstanceEvent):
        type_ = "WorkflowInstanceEvent"

    if isinstance(obj, TimerEvent):
        type_ = "TimerEvent"

    if isinstance(obj, JobEvent):
        type_ = "JobEvent"

    if isinstance(obj, ApplicationEvent):
        type_ = "ApplicationEvent"

    return type_
