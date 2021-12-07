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
Triggers module data exchange
"""

# Python base dependencies
from typing import Dict, Optional, Type

# Library dependencies
from exchange_plugin.dispatcher import EventDispatcher
from exchange_plugin.publisher import Publisher
from kink import inject
from modules_metadata.routing import RoutingKey
from modules_metadata.types import ModuleOrigin
from pony.orm import core as orm
from whistle import Event

# Library libs
from triggers_module.events import (
    ModelEntityCreatedEvent,
    ModelEntityDeletedEvent,
    ModelEntityUpdatedEvent,
)
from triggers_module.models import (
    AutomaticTriggerEntity,
    ChannelPropertyActionEntity,
    ChannelPropertyConditionEntity,
    DateConditionEntity,
    DevicePropertyActionEntity,
    DevicePropertyConditionEntity,
    EmailNotificationEntity,
    ManualTriggerEntity,
    SmsNotificationEntity,
    TimeConditionEntity,
    TriggerControlEntity,
)


@inject
class ModuleExchange:
    """
    Data exchanges utils

    @package        FastyBird:TriggersModule!
    @module         exchange

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    CREATED_ENTITIES_ROUTING_KEYS_MAPPING: Dict[Type[orm.Entity], RoutingKey] = {
        ManualTriggerEntity: RoutingKey.TRIGGERS_ENTITY_CREATED,
        AutomaticTriggerEntity: RoutingKey.TRIGGERS_ENTITY_CREATED,
        TriggerControlEntity: RoutingKey.TRIGGERS_CONTROL_ENTITY_CREATED,
        DevicePropertyActionEntity: RoutingKey.TRIGGERS_ACTIONS_ENTITY_CREATED,
        ChannelPropertyActionEntity: RoutingKey.TRIGGERS_ACTIONS_ENTITY_CREATED,
        DevicePropertyConditionEntity: RoutingKey.TRIGGERS_CONDITIONS_ENTITY_CREATED,
        ChannelPropertyConditionEntity: RoutingKey.TRIGGERS_CONDITIONS_ENTITY_CREATED,
        TimeConditionEntity: RoutingKey.TRIGGERS_CONDITIONS_ENTITY_CREATED,
        DateConditionEntity: RoutingKey.TRIGGERS_CONDITIONS_ENTITY_CREATED,
        SmsNotificationEntity: RoutingKey.TRIGGERS_NOTIFICATIONS_ENTITY_CREATED,
        EmailNotificationEntity: RoutingKey.TRIGGERS_NOTIFICATIONS_ENTITY_CREATED,
    }

    UPDATED_ENTITIES_ROUTING_KEYS_MAPPING: Dict[Type[orm.Entity], RoutingKey] = {
        ManualTriggerEntity: RoutingKey.TRIGGERS_ENTITY_UPDATED,
        AutomaticTriggerEntity: RoutingKey.TRIGGERS_ENTITY_UPDATED,
        TriggerControlEntity: RoutingKey.TRIGGERS_CONTROL_ENTITY_UPDATED,
        DevicePropertyActionEntity: RoutingKey.TRIGGERS_ACTIONS_ENTITY_UPDATED,
        ChannelPropertyActionEntity: RoutingKey.TRIGGERS_ACTIONS_ENTITY_UPDATED,
        DevicePropertyConditionEntity: RoutingKey.TRIGGERS_CONDITIONS_ENTITY_UPDATED,
        ChannelPropertyConditionEntity: RoutingKey.TRIGGERS_CONDITIONS_ENTITY_UPDATED,
        TimeConditionEntity: RoutingKey.TRIGGERS_CONDITIONS_ENTITY_UPDATED,
        DateConditionEntity: RoutingKey.TRIGGERS_CONDITIONS_ENTITY_UPDATED,
        SmsNotificationEntity: RoutingKey.TRIGGERS_NOTIFICATIONS_ENTITY_UPDATED,
        EmailNotificationEntity: RoutingKey.TRIGGERS_NOTIFICATIONS_ENTITY_UPDATED,
    }

    DELETED_ENTITIES_ROUTING_KEYS_MAPPING: Dict[Type[orm.Entity], RoutingKey] = {
        ManualTriggerEntity: RoutingKey.TRIGGERS_ENTITY_DELETED,
        AutomaticTriggerEntity: RoutingKey.TRIGGERS_ENTITY_DELETED,
        TriggerControlEntity: RoutingKey.TRIGGERS_CONTROL_ENTITY_DELETED,
        DevicePropertyActionEntity: RoutingKey.TRIGGERS_ACTIONS_ENTITY_DELETED,
        ChannelPropertyActionEntity: RoutingKey.TRIGGERS_ACTIONS_ENTITY_DELETED,
        DevicePropertyConditionEntity: RoutingKey.TRIGGERS_CONDITIONS_ENTITY_DELETED,
        ChannelPropertyConditionEntity: RoutingKey.TRIGGERS_CONDITIONS_ENTITY_DELETED,
        TimeConditionEntity: RoutingKey.TRIGGERS_CONDITIONS_ENTITY_DELETED,
        DateConditionEntity: RoutingKey.TRIGGERS_CONDITIONS_ENTITY_DELETED,
        SmsNotificationEntity: RoutingKey.TRIGGERS_NOTIFICATIONS_ENTITY_DELETED,
        EmailNotificationEntity: RoutingKey.TRIGGERS_NOTIFICATIONS_ENTITY_DELETED,
    }

    __publisher: Publisher
    __event_dispatcher: EventDispatcher

    # -----------------------------------------------------------------------------

    def __init__(
        self,
        publisher: Publisher,
        event_dispatcher: EventDispatcher,
    ) -> None:
        self.__publisher = publisher
        self.__event_dispatcher = event_dispatcher

        self.__event_dispatcher.add_listener(
            event_id=ModelEntityCreatedEvent.EVENT_NAME,
            listener=self.__entity_created,
        )

        self.__event_dispatcher.add_listener(
            event_id=ModelEntityUpdatedEvent.EVENT_NAME,
            listener=self.__entity_updated,
        )

        self.__event_dispatcher.add_listener(
            event_id=ModelEntityDeletedEvent.EVENT_NAME,
            listener=self.__entity_deleted,
        )

    # -----------------------------------------------------------------------------

    def __entity_created(self, event: Event) -> None:
        if not isinstance(event, ModelEntityCreatedEvent):
            return

        routing_key = self.__get_entity_created_routing_key(entity=type(event.entity))

        if routing_key is not None:
            self.__publisher.publish(
                origin=ModuleOrigin.TRIGGERS_MODULE,
                routing_key=routing_key,
                data=event.entity.to_dict(),
            )

    # -----------------------------------------------------------------------------

    def __entity_updated(self, event: Event) -> None:
        if not isinstance(event, ModelEntityUpdatedEvent):
            return

        routing_key = self.__get_entity_updated_routing_key(entity=type(event.entity))

        if routing_key is not None:
            self.__publisher.publish(
                origin=ModuleOrigin.TRIGGERS_MODULE,
                routing_key=routing_key,
                data=event.entity.to_dict(),
            )

    # -----------------------------------------------------------------------------

    def __entity_deleted(self, event: Event) -> None:
        if not isinstance(event, ModelEntityDeletedEvent):
            return

        routing_key = self.__get_entity_deleted_routing_key(entity=type(event.entity))

        if routing_key is not None:
            self.__publisher.publish(
                origin=ModuleOrigin.TRIGGERS_MODULE,
                routing_key=routing_key,
                data=event.entity.to_dict(),
            )

    # -----------------------------------------------------------------------------

    def __get_entity_created_routing_key(self, entity: Type[orm.Entity]) -> Optional[RoutingKey]:
        """Get routing key for created entity"""
        for classname, routing_key in self.CREATED_ENTITIES_ROUTING_KEYS_MAPPING.items():
            if issubclass(entity, classname):
                return routing_key

        return None

    # -----------------------------------------------------------------------------

    def __get_entity_updated_routing_key(self, entity: Type[orm.Entity]) -> Optional[RoutingKey]:
        """Get routing key for updated entity"""
        for classname, routing_key in self.UPDATED_ENTITIES_ROUTING_KEYS_MAPPING.items():
            if issubclass(entity, classname):
                return routing_key

        return None

    # -----------------------------------------------------------------------------

    def __get_entity_deleted_routing_key(self, entity: Type[orm.Entity]) -> Optional[RoutingKey]:
        """Get routing key for deleted entity"""
        for classname, routing_key in self.DELETED_ENTITIES_ROUTING_KEYS_MAPPING.items():
            if issubclass(entity, classname):
                return routing_key

        return None
