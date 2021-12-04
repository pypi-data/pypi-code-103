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

# pylint: disable=too-many-lines

"""
Triggers module repositories
"""

# Python base dependencies
import json
import uuid
from typing import Dict, List, Optional, Union

# Library dependencies
import modules_metadata.exceptions as metadata_exceptions
from exchange_plugin.dispatcher import EventDispatcher
from kink import inject
from modules_metadata.loader import load_schema
from modules_metadata.routing import RoutingKey
from modules_metadata.triggers_module import TriggerConditionOperator
from modules_metadata.types import ModuleOrigin
from modules_metadata.validator import validate
from pony.orm import core as orm
from whistle import Event

# Library libs
from triggers_module.events import (
    ModelEntityCreatedEvent,
    ModelEntityDeletedEvent,
    ModelEntityUpdatedEvent,
)
from triggers_module.exceptions import (
    HandleExchangeDataException,
    InvalidStateException,
)
from triggers_module.items import (
    AutomaticTriggerItem,
    ChannelPropertyActionItem,
    ChannelPropertyConditionItem,
    DateConditionItem,
    DevicePropertyActionItem,
    DevicePropertyConditionItem,
    ManualTriggerItem,
    TimeConditionItem,
    TriggerControlItem,
)
from triggers_module.models import (
    ActionEntity,
    AutomaticTriggerEntity,
    ChannelPropertyActionEntity,
    ChannelPropertyConditionEntity,
    ConditionEntity,
    DateConditionEntity,
    DevicePropertyActionEntity,
    DevicePropertyConditionEntity,
    ManualTriggerEntity,
    TimeConditionEntity,
    TriggerControlEntity,
    TriggerEntity,
)


@inject
class TriggersRepository:
    """
    Triggers repository

    @package        FastyBird:TriggersModule!
    @module         repositories

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __items: Optional[Dict[str, Union[AutomaticTriggerItem, ManualTriggerItem]]] = None

    __iterator_index = 0

    __event_dispatcher: EventDispatcher

    # -----------------------------------------------------------------------------

    def __init__(
        self,
        event_dispatcher: EventDispatcher,
    ) -> None:
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

    def get_by_id(self, trigger_id: uuid.UUID) -> Union[AutomaticTriggerItem, ManualTriggerItem, None]:
        """Find trigger in cache by provided identifier"""
        for record in self:
            if trigger_id.__eq__(record.trigger_id):
                return record

        return None

    # -----------------------------------------------------------------------------

    def clear(self) -> None:
        """Clear items cache"""
        self.__items = None

    # -----------------------------------------------------------------------------

    def create_from_exchange(self, routing_key: RoutingKey, data: Dict) -> bool:
        """Process received trigger message from exchange when entity was created"""
        if routing_key != RoutingKey.TRIGGERS_ENTITY_CREATED:
            return False

        result: bool = self.__handle_data_from_exchange(routing_key=routing_key, data=data)

        return result

    # -----------------------------------------------------------------------------

    def update_from_exchange(self, routing_key: RoutingKey, data: Dict) -> bool:
        """Process received trigger message from exchange when entity was updated"""
        if routing_key != RoutingKey.TRIGGERS_ENTITY_UPDATED:
            return False

        result: bool = self.__handle_data_from_exchange(routing_key=routing_key, data=data)

        return result

    # -----------------------------------------------------------------------------

    @orm.db_session
    def delete_from_exchange(self, routing_key: RoutingKey, data: Dict) -> bool:
        """Process received trigger message from exchange when entity was updated"""
        if routing_key != RoutingKey.TRIGGERS_ENTITY_DELETED:
            return False

        validated_data = validate_exchange_data(ModuleOrigin.TRIGGERS_MODULE, routing_key, data)

        if self.get_by_id(trigger_id=uuid.UUID(validated_data.get("id"), version=4)) is not None:
            del self[str(data.get("id"))]

            return True

        return False

    # -----------------------------------------------------------------------------

    @orm.db_session
    def __handle_data_from_exchange(self, routing_key: RoutingKey, data: Dict) -> bool:
        validated_data = validate_exchange_data(ModuleOrigin.TRIGGERS_MODULE, routing_key, data)

        trigger_item = self.get_by_id(trigger_id=uuid.UUID(validated_data.get("id"), version=4))

        if trigger_item is None:
            entity: Optional[TriggerEntity] = TriggerEntity.get(
                trigger_id=uuid.UUID(validated_data.get("id"), version=4)
            )

            if entity is not None:
                self[entity.trigger_id.__str__()] = self.__create_item(entity=entity)

                return True

            return False

        item = self.__update_item(item=trigger_item, data=validated_data)

        if item is not None:
            self[str(validated_data.get("id"))] = item

            return True

        return False

    # -----------------------------------------------------------------------------

    @orm.db_session
    def initialize(self) -> None:
        """Initialize repository by fetching entities from database"""
        items: Dict[str, Union[AutomaticTriggerItem, ManualTriggerItem]] = {}

        for trigger in TriggerEntity.select():
            items[trigger.trigger_id.__str__()] = self.__create_item(entity=trigger)

        self.__items = items

    # -----------------------------------------------------------------------------

    def __entity_created(self, event: Event) -> None:
        if not isinstance(event, ModelEntityCreatedEvent) or not isinstance(
            event.entity, (ManualTriggerEntity, AutomaticTriggerEntity)
        ):
            return

        self.initialize()

    # -----------------------------------------------------------------------------

    def __entity_updated(self, event: Event) -> None:
        if not isinstance(event, ModelEntityUpdatedEvent) or not isinstance(
            event.entity, (ManualTriggerEntity, AutomaticTriggerEntity)
        ):
            return

        self.initialize()

    # -----------------------------------------------------------------------------

    def __entity_deleted(self, event: Event) -> None:
        if not isinstance(event, ModelEntityDeletedEvent) or not isinstance(
            event.entity, (ManualTriggerEntity, AutomaticTriggerEntity)
        ):
            return

        self.initialize()

    # -----------------------------------------------------------------------------

    @staticmethod
    def __create_item(entity: TriggerEntity) -> Union[AutomaticTriggerItem, ManualTriggerItem]:
        if isinstance(entity, AutomaticTriggerEntity):
            return AutomaticTriggerItem(
                trigger_id=entity.trigger_id,
                name=entity.name,
                comment=entity.comment,
                enabled=entity.enabled,
            )

        if isinstance(entity, ManualTriggerEntity):
            return ManualTriggerItem(
                trigger_id=entity.trigger_id,
                name=entity.name,
                comment=entity.comment,
                enabled=entity.enabled,
            )

        raise InvalidStateException("Unsupported entity type provided")

    # -----------------------------------------------------------------------------

    @staticmethod
    def __update_item(
        item: Union[AutomaticTriggerItem, ManualTriggerItem],
        data: Dict,
    ) -> Union[AutomaticTriggerItem, ManualTriggerItem]:
        if isinstance(item, AutomaticTriggerItem):
            return AutomaticTriggerItem(
                trigger_id=item.trigger_id,
                name=data.get("name", item.name),
                comment=data.get("comment", item.comment),
                enabled=bool(data.get("enabled", item.enabled)),
            )

        if isinstance(item, ManualTriggerItem):
            return ManualTriggerItem(
                trigger_id=item.trigger_id,
                name=data.get("name", item.name),
                comment=data.get("comment", item.comment),
                enabled=bool(data.get("enabled", item.enabled)),
            )

        raise InvalidStateException("Unsupported entity type provided")

    # -----------------------------------------------------------------------------

    def __setitem__(self, key: str, value: Union[AutomaticTriggerItem, ManualTriggerItem]) -> None:
        if self.__items is None:
            self.initialize()

        if self.__items:
            self.__items[key] = value

    # -----------------------------------------------------------------------------

    def __getitem__(self, key: str) -> Union[AutomaticTriggerItem, ManualTriggerItem]:
        if self.__items is None:
            self.initialize()

        if self.__items and key in self.__items:
            return self.__items[key]

        raise IndexError

    # -----------------------------------------------------------------------------

    def __delitem__(self, key: str) -> None:
        if self.__items and key in self.__items:
            del self.__items[key]

    # -----------------------------------------------------------------------------

    def __iter__(self) -> "TriggersRepository":
        # Reset index for nex iteration
        self.__iterator_index = 0

        return self

    # -----------------------------------------------------------------------------

    def __len__(self) -> int:
        if self.__items is None:
            self.initialize()

        return len(self.__items.values()) if isinstance(self.__items, dict) else 0

    # -----------------------------------------------------------------------------

    def __next__(self) -> Union[AutomaticTriggerItem, ManualTriggerItem]:
        if self.__items is None:
            self.initialize()

        if self.__items and self.__iterator_index < len(self.__items.values()):
            items = list(self.__items.values()) if self.__items else []

            result = items[self.__iterator_index]

            self.__iterator_index += 1

            return result

        # Reset index for nex iteration
        self.__iterator_index = 0

        # End of iteration
        raise StopIteration


@inject
class ActionsRepository:
    """
    Triggers actions repository

    @package        FastyBird:TriggersModule!
    @module         repositories

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __items: Optional[Dict[str, Union[DevicePropertyActionItem, ChannelPropertyActionItem]]] = None

    __iterator_index = 0

    __event_dispatcher: EventDispatcher

    # -----------------------------------------------------------------------------

    def __init__(
        self,
        event_dispatcher: EventDispatcher,
    ) -> None:
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

    def get_by_id(self, action_id: uuid.UUID) -> Union[DevicePropertyActionItem, ChannelPropertyActionItem, None]:
        """Find action in cache by provided identifier"""
        for record in self:
            if action_id.__eq__(record.action_id):
                return record

        return None

    # -----------------------------------------------------------------------------

    def get_all_by_property_identifier(
        self,
        property_id: uuid.UUID,
    ) -> List[Union[DevicePropertyActionItem, ChannelPropertyActionItem]]:
        """Find actions in cache by provided property identifier"""
        items: List[Union[DevicePropertyActionItem, ChannelPropertyActionItem]] = []

        for record in self:
            if isinstance(record, DevicePropertyActionItem) and record.device_property.__eq__(property_id):
                items.append(record)

            if isinstance(record, ChannelPropertyActionItem) and record.channel_property.__eq__(property_id):
                items.append(record)

        return items

    # -----------------------------------------------------------------------------

    def get_all_for_trigger(
        self,
        trigger_id: uuid.UUID,
    ) -> List[Union[DevicePropertyActionItem, ChannelPropertyActionItem]]:
        """Find all actions in cache for provided trigger identifier"""
        items: List[Union[DevicePropertyActionItem, ChannelPropertyActionItem]] = []

        for record in self:
            if trigger_id.__eq__(record.trigger_id):
                items.append(record)

        return items

    # -----------------------------------------------------------------------------

    def clear(self) -> None:
        """Clear items cache"""
        self.__items = None

    # -----------------------------------------------------------------------------

    def create_from_exchange(self, routing_key: RoutingKey, data: Dict) -> bool:
        """Process received action message from exchange when entity was created"""
        if routing_key != RoutingKey.TRIGGERS_ACTIONS_ENTITY_CREATED:
            return False

        result: bool = self.__handle_data_from_exchange(routing_key=routing_key, data=data)

        return result

    # -----------------------------------------------------------------------------

    def update_from_exchange(self, routing_key: RoutingKey, data: Dict) -> bool:
        """Process received action message from exchange when entity was updated"""
        if routing_key != RoutingKey.TRIGGERS_ACTIONS_ENTITY_UPDATED:
            return False

        result: bool = self.__handle_data_from_exchange(routing_key=routing_key, data=data)

        return result

    # -----------------------------------------------------------------------------

    @orm.db_session
    def delete_from_exchange(self, routing_key: RoutingKey, data: Dict) -> bool:
        """Process received action message from exchange when entity was updated"""
        if routing_key != RoutingKey.TRIGGERS_ACTIONS_ENTITY_DELETED:
            return False

        validated_data = validate_exchange_data(ModuleOrigin.TRIGGERS_MODULE, routing_key, data)

        if self.get_by_id(action_id=uuid.UUID(validated_data.get("id"), version=4)) is not None:
            del self[str(data.get("id"))]

            return True

        return False

    # -----------------------------------------------------------------------------

    @orm.db_session
    def initialize(self) -> None:
        """Initialize repository by fetching entities from database"""
        items: Dict[str, Union[DevicePropertyActionItem, ChannelPropertyActionItem]] = {}

        for action in ActionEntity.select():
            items[action.action_id.__str__()] = self.__create_item(entity=action)

        self.__items = items

    # -----------------------------------------------------------------------------

    @orm.db_session
    def __handle_data_from_exchange(self, routing_key: RoutingKey, data: Dict) -> bool:
        validated_data = validate_exchange_data(ModuleOrigin.TRIGGERS_MODULE, routing_key, data)

        action_item = self.get_by_id(action_id=uuid.UUID(validated_data.get("id"), version=4))

        if action_item is None:
            entity: Optional[ActionEntity] = ActionEntity.get(action_id=uuid.UUID(validated_data.get("id"), version=4))

            if entity is not None:
                self[entity.action_id.__str__()] = self.__create_item(entity=entity)

                return True

            return False

        item = self.__update_item(item=action_item, data=validated_data)

        if item is not None:
            self[str(validated_data.get("id"))] = item

            return True

        return False

    # -----------------------------------------------------------------------------

    def __entity_created(self, event: Event) -> None:
        if not isinstance(event, ModelEntityCreatedEvent) or not isinstance(
            event.entity, (DevicePropertyActionEntity, ChannelPropertyActionEntity)
        ):
            return

        self.initialize()

    # -----------------------------------------------------------------------------

    def __entity_updated(self, event: Event) -> None:
        if not isinstance(event, ModelEntityUpdatedEvent) or not isinstance(
            event.entity, (DevicePropertyActionEntity, ChannelPropertyActionEntity)
        ):
            return

        self.initialize()

    # -----------------------------------------------------------------------------

    def __entity_deleted(self, event: Event) -> None:
        if not isinstance(event, ModelEntityDeletedEvent) or not isinstance(
            event.entity, (DevicePropertyActionEntity, ChannelPropertyActionEntity)
        ):
            return

        self.initialize()

    # -----------------------------------------------------------------------------

    @staticmethod
    def __create_item(entity: ActionEntity) -> Union[DevicePropertyActionItem, ChannelPropertyActionItem]:
        if isinstance(entity, DevicePropertyActionEntity):
            return DevicePropertyActionItem(
                action_id=entity.action_id,
                trigger_id=entity.trigger.trigger_id,
                enabled=entity.enabled,
                value=entity.value,
                device_property=entity.device_property,
                device=entity.device,
            )

        if isinstance(entity, ChannelPropertyActionEntity):
            return ChannelPropertyActionItem(
                action_id=entity.action_id,
                trigger_id=entity.trigger.trigger_id,
                enabled=entity.enabled,
                value=entity.value,
                channel_property=entity.channel_property,
                channel=entity.channel,
                device=entity.device,
            )

        raise InvalidStateException("Unsupported entity type provided")

    # -----------------------------------------------------------------------------

    @staticmethod
    def __update_item(
        item: Union[DevicePropertyActionItem, ChannelPropertyActionItem],
        data: Dict,
    ) -> Union[DevicePropertyActionItem, ChannelPropertyActionItem]:
        if isinstance(item, DevicePropertyActionItem):
            return DevicePropertyActionItem(
                action_id=item.action_id,
                trigger_id=item.trigger_id,
                enabled=data.get("enabled", item.enabled),
                value=data.get("value", item.value),
                device_property=item.device_property,
                device=item.device,
            )

        if isinstance(item, ChannelPropertyActionItem):
            return ChannelPropertyActionItem(
                action_id=item.action_id,
                trigger_id=item.trigger_id,
                enabled=data.get("enabled", item.enabled),
                value=data.get("value", item.value),
                channel_property=item.channel_property,
                channel=item.channel,
                device=item.device,
            )

        raise InvalidStateException("Unsupported entity type provided")

    # -----------------------------------------------------------------------------

    def __setitem__(self, key: str, value: Union[DevicePropertyActionItem, ChannelPropertyActionItem]) -> None:
        if self.__items is None:
            self.initialize()

        if self.__items:
            self.__items[key] = value

    # -----------------------------------------------------------------------------

    def __getitem__(self, key: str) -> Union[DevicePropertyActionItem, ChannelPropertyActionItem]:
        if self.__items is None:
            self.initialize()

        if self.__items and key in self.__items:
            return self.__items[key]

        raise IndexError

    # -----------------------------------------------------------------------------

    def __delitem__(self, key: str) -> None:
        if self.__items and key in self.__items:
            del self.__items[key]

    # -----------------------------------------------------------------------------

    def __iter__(self) -> "ActionsRepository":
        # Reset index for nex iteration
        self.__iterator_index = 0

        return self

    # -----------------------------------------------------------------------------

    def __len__(self) -> int:
        if self.__items is None:
            self.initialize()

        return len(self.__items.values()) if isinstance(self.__items, dict) else 0

    # -----------------------------------------------------------------------------

    def __next__(self) -> Union[DevicePropertyActionItem, ChannelPropertyActionItem]:
        if self.__items is None:
            self.initialize()

        if self.__items and self.__iterator_index < len(self.__items.values()):
            items = list(self.__items.values()) if self.__items else []

            result = items[self.__iterator_index]

            self.__iterator_index += 1

            return result

        # Reset index for nex iteration
        self.__iterator_index = 0

        # End of iteration
        raise StopIteration


@inject
class ConditionsRepository:
    """
    Triggers conditions repository

    @package        FastyBird:TriggersModule!
    @module         repositories

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __items: Optional[
        Dict[
            str, Union[DevicePropertyConditionItem, ChannelPropertyConditionItem, TimeConditionItem, DateConditionItem]
        ]
    ] = None

    __iterator_index = 0

    __event_dispatcher: EventDispatcher

    # -----------------------------------------------------------------------------

    def __init__(
        self,
        event_dispatcher: EventDispatcher,
    ) -> None:
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

    def get_by_id(
        self,
        condition_id: uuid.UUID,
    ) -> Union[DevicePropertyConditionItem, ChannelPropertyConditionItem, TimeConditionItem, DateConditionItem, None]:
        """Find condition in cache by provided identifier"""
        for record in self:
            if condition_id.__eq__(record.condition_id):
                return record

        return None

    # -----------------------------------------------------------------------------

    def get_all_by_property_identifier(
        self,
        property_id: uuid.UUID,
    ) -> List[Union[DevicePropertyConditionItem, ChannelPropertyConditionItem]]:
        """Find conditions in cache by provided property identifier"""
        items: List[Union[DevicePropertyConditionItem, ChannelPropertyConditionItem]] = []

        for record in self:
            if isinstance(record, DevicePropertyConditionItem) and property_id.__eq__(record.device_property):
                items.append(record)

            if isinstance(record, ChannelPropertyConditionItem) and property_id.__eq__(record.channel_property):
                items.append(record)

        return items

    # -----------------------------------------------------------------------------

    def get_all_for_trigger(
        self,
        trigger_id: uuid.UUID,
    ) -> List[Union[DevicePropertyConditionItem, ChannelPropertyConditionItem, TimeConditionItem, DateConditionItem]]:
        """Find all conditions in cache for provided trigger identifier"""
        items: List[
            Union[DevicePropertyConditionItem, ChannelPropertyConditionItem, TimeConditionItem, DateConditionItem]
        ] = []

        for record in self:
            if trigger_id.__eq__(record.trigger_id):
                items.append(record)

        return items

    # -----------------------------------------------------------------------------

    def clear(self) -> None:
        """Clear items cache"""
        self.__items = None

    # -----------------------------------------------------------------------------

    def create_from_exchange(self, routing_key: RoutingKey, data: Dict) -> bool:
        """Process received condition message from exchange when entity was created"""
        if routing_key != RoutingKey.TRIGGERS_CONDITIONS_ENTITY_CREATED:
            return False

        result: bool = self.__handle_data_from_exchange(routing_key=routing_key, data=data)

        return result

    # -----------------------------------------------------------------------------

    def update_from_exchange(self, routing_key: RoutingKey, data: Dict) -> bool:
        """Process received condition message from exchange when entity was updated"""
        if routing_key != RoutingKey.TRIGGERS_CONDITIONS_ENTITY_UPDATED:
            return False

        result: bool = self.__handle_data_from_exchange(routing_key=routing_key, data=data)

        return result

    # -----------------------------------------------------------------------------

    @orm.db_session
    def delete_from_exchange(self, routing_key: RoutingKey, data: Dict) -> bool:
        """Process received condition message from exchange when entity was updated"""
        if routing_key != RoutingKey.TRIGGERS_CONDITIONS_ENTITY_DELETED:
            return False

        validated_data = validate_exchange_data(ModuleOrigin.TRIGGERS_MODULE, routing_key, data)

        if self.get_by_id(condition_id=uuid.UUID(validated_data.get("id"), version=4)) is not None:
            del self[str(data.get("id"))]

            return True

        return False

    # -----------------------------------------------------------------------------

    @orm.db_session
    def initialize(self) -> None:
        """Initialize conditions repository by fetching entities from database"""
        items: Dict[
            str,
            Union[DevicePropertyConditionItem, ChannelPropertyConditionItem, TimeConditionItem, DateConditionItem],
        ] = {}

        for condition in ConditionEntity.select():
            items[condition.condition_id.__str__()] = self.__create_item(entity=condition)

        self.__items = items

    # -----------------------------------------------------------------------------

    @orm.db_session
    def __handle_data_from_exchange(self, routing_key: RoutingKey, data: Dict) -> bool:
        validated_data = validate_exchange_data(ModuleOrigin.TRIGGERS_MODULE, routing_key, data)

        condition_item = self.get_by_id(condition_id=uuid.UUID(validated_data.get("id"), version=4))

        if condition_item is None:
            entity: Optional[ConditionEntity] = ConditionEntity.get(
                condition_id=uuid.UUID(validated_data.get("id"), version=4)
            )

            if entity is not None:
                self[entity.condition_id.__str__()] = self.__create_item(entity=entity)

                return True

            return False

        item = self.__update_item(item=condition_item, data=validated_data)

        if item is not None:
            self[str(validated_data.get("id"))] = item

            return True

        return False

    # -----------------------------------------------------------------------------

    def __entity_created(self, event: Event) -> None:
        if not isinstance(event, ModelEntityCreatedEvent) or not isinstance(
            event.entity,
            (
                DevicePropertyConditionEntity,
                ChannelPropertyConditionEntity,
                DateConditionEntity,
                TimeConditionEntity,
            ),
        ):
            return

        self.initialize()

    # -----------------------------------------------------------------------------

    def __entity_updated(self, event: Event) -> None:
        if not isinstance(event, ModelEntityUpdatedEvent) or not isinstance(
            event.entity,
            (
                DevicePropertyConditionEntity,
                ChannelPropertyConditionEntity,
                DateConditionEntity,
                TimeConditionEntity,
            ),
        ):
            return

        self.initialize()

    # -----------------------------------------------------------------------------

    def __entity_deleted(self, event: Event) -> None:
        if not isinstance(event, ModelEntityDeletedEvent) or not isinstance(
            event.entity,
            (
                DevicePropertyConditionEntity,
                ChannelPropertyConditionEntity,
                DateConditionEntity,
                TimeConditionEntity,
            ),
        ):
            return

        self.initialize()

    # -----------------------------------------------------------------------------

    @staticmethod
    def __create_item(
        entity: ConditionEntity,
    ) -> Union[DevicePropertyConditionItem, ChannelPropertyConditionItem, TimeConditionItem, DateConditionItem]:
        if isinstance(entity, DevicePropertyConditionEntity):
            return DevicePropertyConditionItem(
                condition_id=entity.condition_id,
                trigger_id=entity.trigger.trigger_id,
                enabled=entity.enabled,
                operator=entity.operator_formatted,
                operand=entity.operand,
                device_property=entity.device_property,
                device=entity.device,
            )

        if isinstance(entity, ChannelPropertyConditionEntity):
            return ChannelPropertyConditionItem(
                condition_id=entity.condition_id,
                trigger_id=entity.trigger.trigger_id,
                enabled=entity.enabled,
                operator=entity.operator_formatted,
                operand=entity.operand,
                channel_property=entity.channel_property,
                channel=entity.channel,
                device=entity.device,
            )

        if isinstance(entity, TimeConditionEntity):
            return TimeConditionItem(
                condition_id=entity.condition_id,
                trigger_id=entity.trigger.trigger_id,
                enabled=entity.enabled,
                time=entity.time,
                days=entity.days,
            )

        if isinstance(entity, DateConditionEntity):
            return DateConditionItem(
                condition_id=entity.condition_id,
                trigger_id=entity.trigger.trigger_id,
                enabled=entity.enabled,
                date=entity.date,
            )

        raise InvalidStateException("Unsupported entity type provided")

    # -----------------------------------------------------------------------------

    @staticmethod
    def __update_item(
        item: Union[DevicePropertyConditionItem, ChannelPropertyConditionItem, TimeConditionItem, DateConditionItem],
        data: Dict,
    ) -> Union[DevicePropertyConditionItem, ChannelPropertyConditionItem, TimeConditionItem, DateConditionItem]:
        if isinstance(item, DevicePropertyConditionItem):
            return DevicePropertyConditionItem(
                condition_id=item.condition_id,
                trigger_id=item.trigger_id,
                enabled=data.get("enabled", item.enabled),
                operator=TriggerConditionOperator(data.get("operator", item.operator.value)),
                operand=data.get("operand", item.operand),
                device_property=item.device_property,
                device=item.device,
            )

        if isinstance(item, ChannelPropertyConditionItem):
            return ChannelPropertyConditionItem(
                condition_id=item.condition_id,
                trigger_id=item.trigger_id,
                enabled=data.get("enabled", item.enabled),
                operator=TriggerConditionOperator(data.get("operator", item.operator.value)),
                operand=data.get("operand", item.operand),
                channel_property=item.channel_property,
                channel=item.channel,
                device=item.device,
            )

        if isinstance(item, TimeConditionItem):
            return TimeConditionItem(
                condition_id=item.condition_id,
                trigger_id=item.trigger_id,
                enabled=data.get("enabled", item.enabled),
                time=data.get("time", item.time),
                days=data.get("days", item.days),
            )

        if isinstance(item, DateConditionItem):
            return DateConditionItem(
                condition_id=item.condition_id,
                trigger_id=item.trigger_id,
                enabled=data.get("enabled", item.enabled),
                date=data.get("time", item.date),
            )

        raise InvalidStateException("Unsupported entity type provided")

    # -----------------------------------------------------------------------------

    def __setitem__(
        self,
        key: str,
        value: Union[DevicePropertyConditionItem, ChannelPropertyConditionItem, TimeConditionItem, DateConditionItem],
    ) -> None:
        if self.__items is None:
            self.initialize()

        if self.__items:
            self.__items[key] = value

    # -----------------------------------------------------------------------------

    def __getitem__(
        self, key: str
    ) -> Union[DevicePropertyConditionItem, ChannelPropertyConditionItem, TimeConditionItem, DateConditionItem]:
        if self.__items is None:
            self.initialize()

        if self.__items and key in self.__items:
            return self.__items[key]

        raise IndexError

    # -----------------------------------------------------------------------------

    def __delitem__(self, key: str) -> None:
        if self.__items and key in self.__items:
            del self.__items[key]

    # -----------------------------------------------------------------------------

    def __iter__(self) -> "ConditionsRepository":
        # Reset index for nex iteration
        self.__iterator_index = 0

        return self

    # -----------------------------------------------------------------------------

    def __len__(self) -> int:
        if self.__items is None:
            self.initialize()

        return len(self.__items.values()) if isinstance(self.__items, dict) else 0

    # -----------------------------------------------------------------------------

    def __next__(
        self,
    ) -> Union[DevicePropertyConditionItem, ChannelPropertyConditionItem, TimeConditionItem, DateConditionItem]:
        if self.__items is None:
            self.initialize()

        if self.__items and self.__iterator_index < len(self.__items.values()):
            items = list(self.__items.values()) if self.__items else []

            result = items[self.__iterator_index]

            self.__iterator_index += 1

            return result

        # Reset index for nex iteration
        self.__iterator_index = 0

        # End of iteration
        raise StopIteration


@inject
class TriggersControlsRepository:
    """
    Triggers controls repository

    @package        FastyBird:TriggersModule!
    @module         repositories

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __items: Optional[Dict[str, Union[TriggerControlItem]]] = None

    __iterator_index = 0

    __event_dispatcher: EventDispatcher

    # -----------------------------------------------------------------------------

    def __init__(
        self,
        event_dispatcher: EventDispatcher,
    ) -> None:
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

    def get_by_id(
        self,
        control_id: uuid.UUID,
    ) -> Union[TriggerControlItem, None]:
        """Find control in cache by provided identifier"""
        for record in self:
            if control_id.__eq__(record.control_id):
                return record

        return None

    # -----------------------------------------------------------------------------

    def clear(self) -> None:
        """Clear items cache"""
        self.__items = None

    # -----------------------------------------------------------------------------

    def create_from_exchange(self, routing_key: RoutingKey, data: Dict) -> bool:
        """Process received control control message from exchange when entity was created"""
        if routing_key != RoutingKey.TRIGGERS_CONTROL_ENTITY_CREATED:
            return False

        result: bool = self.__handle_data_from_exchange(routing_key=routing_key, data=data)

        return result

    # -----------------------------------------------------------------------------

    def update_from_exchange(self, routing_key: RoutingKey, data: Dict) -> bool:
        """Process received control control message from exchange when entity was updated"""
        if routing_key != RoutingKey.TRIGGERS_CONTROL_ENTITY_UPDATED:
            return False

        result: bool = self.__handle_data_from_exchange(routing_key=routing_key, data=data)

        return result

    # -----------------------------------------------------------------------------

    @orm.db_session
    def delete_from_exchange(self, routing_key: RoutingKey, data: Dict) -> bool:
        """Process received control control message from exchange when entity was updated"""
        if routing_key != RoutingKey.TRIGGERS_CONTROL_ENTITY_DELETED:
            return False

        validated_data = validate_exchange_data(ModuleOrigin.TRIGGERS_MODULE, routing_key, data)

        if self.get_by_id(control_id=uuid.UUID(validated_data.get("id"), version=4)) is not None:
            del self[str(data.get("id"))]

            return True

        return False

    # -----------------------------------------------------------------------------

    @orm.db_session
    def initialize(self) -> None:
        """Initialize triggers controls repository by fetching entities from database"""
        items: Dict[str, Union[TriggerControlItem]] = {}

        for entity in TriggerControlEntity.select():
            items[entity.control_id.__str__()] = self.__create_item(entity=entity)

        self.__items = items

    # -----------------------------------------------------------------------------

    @orm.db_session
    def __handle_data_from_exchange(self, routing_key: RoutingKey, data: Dict) -> bool:
        validated_data = validate_exchange_data(ModuleOrigin.TRIGGERS_MODULE, routing_key, data)

        control_item = self.get_by_id(control_id=uuid.UUID(validated_data.get("id"), version=4))

        if control_item is None:
            entity: Optional[TriggerControlEntity] = TriggerControlEntity.get(
                control_id=uuid.UUID(validated_data.get("id"), version=4)
            )

            if entity is not None:
                self[entity.control_id.__str__()] = self.__create_item(entity=entity)

                return True

            return False

        item = self.__update_item(item=control_item)

        if item is not None:
            self[str(validated_data.get("id"))] = item

            return True

        return False

    # -----------------------------------------------------------------------------

    def __entity_created(self, event: Event) -> None:
        if not isinstance(event, ModelEntityCreatedEvent) or not isinstance(event.entity, TriggerControlEntity):
            return

        self.initialize()

    # -----------------------------------------------------------------------------

    def __entity_updated(self, event: Event) -> None:
        if not isinstance(event, ModelEntityUpdatedEvent) or not isinstance(event.entity, TriggerControlEntity):
            return

        self.initialize()

    # -----------------------------------------------------------------------------

    def __entity_deleted(self, event: Event) -> None:
        if not isinstance(event, ModelEntityDeletedEvent) or not isinstance(event.entity, TriggerControlEntity):
            return

        self.initialize()

    # -----------------------------------------------------------------------------

    @staticmethod
    def __create_item(entity: TriggerControlEntity) -> Union[TriggerControlItem]:
        if isinstance(entity, TriggerControlEntity):
            return TriggerControlItem(
                control_id=entity.control_id,
                control_name=entity.name,
                trigger_id=entity.trigger.trigger_id,
            )

        raise InvalidStateException("Unsupported entity type provided")

    # -----------------------------------------------------------------------------

    @staticmethod
    def __update_item(item: TriggerControlItem) -> Union[TriggerControlItem]:
        if isinstance(item, TriggerControlItem):
            return TriggerControlItem(
                control_id=item.control_id,
                control_name=item.name,
                trigger_id=item.trigger_id,
            )

        raise InvalidStateException("Unsupported entity type provided")

    # -----------------------------------------------------------------------------

    def __setitem__(self, key: str, value: Union[TriggerControlItem]) -> None:
        if self.__items is None:
            self.initialize()

        if self.__items:
            self.__items[key] = value

    # -----------------------------------------------------------------------------

    def __getitem__(self, key: str) -> Union[TriggerControlItem]:
        if self.__items is None:
            self.initialize()

        if self.__items and key in self.__items:
            return self.__items[key]

        raise IndexError

    # -----------------------------------------------------------------------------

    def __delitem__(self, key: str) -> None:
        if self.__items and key in self.__items:
            del self.__items[key]

    # -----------------------------------------------------------------------------

    def __iter__(self) -> "TriggersControlsRepository":
        # Reset index for nex iteration
        self.__iterator_index = 0

        return self

    # -----------------------------------------------------------------------------

    def __len__(self) -> int:
        if self.__items is None:
            self.initialize()

        return len(self.__items.values()) if isinstance(self.__items, dict) else 0

    # -----------------------------------------------------------------------------

    def __next__(self) -> Union[TriggerControlItem]:
        if self.__items is None:
            self.initialize()

        if self.__items and self.__iterator_index < len(self.__items.values()):
            items = list(self.__items.values()) if self.__items else []

            result = items[self.__iterator_index]

            self.__iterator_index += 1

            return result

        # Reset index for nex iteration
        self.__iterator_index = 0

        # End of iteration
        raise StopIteration


def validate_exchange_data(origin: ModuleOrigin, routing_key: RoutingKey, data: Dict) -> Dict:
    """
    Validate received RPC message against defined schema
    """
    try:
        schema: str = load_schema(origin, routing_key)

    except metadata_exceptions.FileNotFoundException as ex:
        raise HandleExchangeDataException("Provided data could not be validated") from ex

    except metadata_exceptions.InvalidArgumentException as ex:
        raise HandleExchangeDataException("Provided data could not be validated") from ex

    try:
        return validate(json.dumps(data), schema)

    except metadata_exceptions.MalformedInputException as ex:
        raise HandleExchangeDataException("Provided data are not in valid json format") from ex

    except metadata_exceptions.LogicException as ex:
        raise HandleExchangeDataException("Provided data could not be validated") from ex

    except metadata_exceptions.InvalidDataException as ex:
        raise HandleExchangeDataException("Provided data are not valid") from ex
