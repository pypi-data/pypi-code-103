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

from typing import Dict, List

from madam.domains.entities.events import (
    ApplicationEvent,
    JobEvent,
    TimerEvent,
    WatchfolderEvent,
    WorkflowEvent,
    WorkflowInstanceEvent,
)
from madam.domains.events import EventDispatcher
from madam.domains.interfaces.events import EventInterface


class GraphQLAPI:

    subscriptions: Dict[str, List[EventInterface]] = {}

    def __init__(self, event_dispatcher: EventDispatcher):
        """
        Init GraphQLAPI instance with event_dispatcher

        :param event_dispatcher: EventDispatcher instance
        """
        self.event_dispatcher = event_dispatcher
        # subscribe to events
        self.event_dispatcher.add_event_listener(
            WorkflowEvent.EVENT_TYPE_CREATE, self.on_event
        )
        self.event_dispatcher.add_event_listener(
            WorkflowEvent.EVENT_TYPE_DELETE, self.on_event
        )
        self.event_dispatcher.add_event_listener(
            WorkflowInstanceEvent.EVENT_TYPE_CREATE, self.on_event
        )
        self.event_dispatcher.add_event_listener(
            WorkflowInstanceEvent.EVENT_TYPE_UPDATE, self.on_event
        )
        self.event_dispatcher.add_event_listener(
            WorkflowInstanceEvent.EVENT_TYPE_DELETE, self.on_event
        )
        self.event_dispatcher.add_event_listener(
            TimerEvent.EVENT_TYPE_CREATE, self.on_event
        )
        self.event_dispatcher.add_event_listener(
            TimerEvent.EVENT_TYPE_UPDATE, self.on_event
        )
        self.event_dispatcher.add_event_listener(
            TimerEvent.EVENT_TYPE_DELETE, self.on_event
        )
        self.event_dispatcher.add_event_listener(
            JobEvent.EVENT_TYPE_CREATE, self.on_event
        )
        self.event_dispatcher.add_event_listener(
            JobEvent.EVENT_TYPE_UPDATE, self.on_event
        )
        self.event_dispatcher.add_event_listener(
            JobEvent.EVENT_TYPE_DELETE, self.on_event
        )
        self.event_dispatcher.add_event_listener(
            ApplicationEvent.EVENT_TYPE_CREATE, self.on_event
        )
        self.event_dispatcher.add_event_listener(
            ApplicationEvent.EVENT_TYPE_UPDATE, self.on_event
        )
        self.event_dispatcher.add_event_listener(
            ApplicationEvent.EVENT_TYPE_DELETE, self.on_event
        )
        self.event_dispatcher.add_event_listener(
            WatchfolderEvent.EVENT_TYPE_CREATE, self.on_event
        )
        self.event_dispatcher.add_event_listener(
            WatchfolderEvent.EVENT_TYPE_UPDATE, self.on_event
        )
        self.event_dispatcher.add_event_listener(
            WatchfolderEvent.EVENT_TYPE_DELETE, self.on_event
        )

    def on_event(self, event: EventInterface):
        """
        Event listener to add events to subscription response queues

        :param event: Event instance
        :return:
        """
        for list_ in self.subscriptions.values():
            list_.append(event)
