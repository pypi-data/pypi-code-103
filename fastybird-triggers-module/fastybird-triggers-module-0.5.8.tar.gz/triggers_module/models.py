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
Triggers module models
"""

# Python base dependencies
import datetime
import uuid
from typing import Dict, List, Optional, Union

# Library dependencies
from exchange_plugin.dispatcher import EventDispatcher
from kink import di
from modules_metadata.triggers_module import TriggerConditionOperator
from modules_metadata.types import ButtonPayload, SwitchPayload
from pony.orm import PrimaryKey  # type: ignore[attr-defined]
from pony.orm import Set  # type: ignore[attr-defined]
from pony.orm import Database, Discriminator, Json  # type: ignore[attr-defined]
from pony.orm import Optional as OptionalField  # type: ignore[attr-defined]
from pony.orm import Required as RequiredField  # type: ignore[attr-defined]

# Library libs
from triggers_module.events import (
    ModelEntityCreatedEvent,
    ModelEntityDeletedEvent,
    ModelEntityUpdatedEvent,
)

# Create triggers module database accessor
db: Database = Database()  # type: ignore[no-any-unimported]


class TriggerEntity(db.Entity):  # type: ignore[no-any-unimported]
    """
    Base trigger entity

    @package        FastyBird:TriggersModule!
    @module         models

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    _table_: str = "fb_triggers"

    type = Discriminator(str, column="trigger_type")
    _discriminator_: str = "trigger"

    trigger_id: uuid.UUID = PrimaryKey(uuid.UUID, default=uuid.uuid4, column="trigger_id")
    name: str = RequiredField(str, column="trigger_name", max_len=100, nullable=False)
    comment: Optional[str] = OptionalField(str, column="trigger_comment", nullable=True, default=None)
    enabled: bool = OptionalField(bool, column="trigger_enabled", nullable=True, default=True)
    params: Optional[Dict] = OptionalField(Json, column="params", nullable=True)

    created_at: Optional[datetime.datetime] = OptionalField(datetime.datetime, column="created_at", nullable=True)
    updated_at: Optional[datetime.datetime] = OptionalField(datetime.datetime, column="updated_at", nullable=True)

    actions: List["ActionEntity"] = Set("ActionEntity", reverse="trigger")
    notifications: List["NotificationEntity"] = Set("NotificationEntity", reverse="trigger")
    controls: List["TriggerControlEntity"] = Set("TriggerControlEntity", reverse="trigger")

    # -----------------------------------------------------------------------------

    def to_dict(
        self,
        only: Union[List[str], str, None] = None,  # pylint: disable=unused-argument
        exclude: Union[List[str], str, None] = None,  # pylint: disable=unused-argument
        with_collections: bool = False,  # pylint: disable=unused-argument
        with_lazy: bool = False,  # pylint: disable=unused-argument
        related_objects: bool = False,  # pylint: disable=unused-argument
    ) -> Dict[str, Union[str, int, bool, Dict, None]]:
        """Transform entity to dictionary"""
        return {
            "id": self.trigger_id.__str__(),
            "type": self.type,
            "name": self.name,
            "comment": self.comment,
            "enabled": self.enabled,
            "params": self.params,
        }

    # -----------------------------------------------------------------------------

    def before_insert(self) -> None:
        """Before insert entity hook"""
        self.created_at = datetime.datetime.now()

    # -----------------------------------------------------------------------------

    def after_insert(self) -> None:
        """After insert entity hook"""
        di[EventDispatcher].dispatch(
            ModelEntityCreatedEvent.EVENT_NAME,
            ModelEntityCreatedEvent(self),
        )

    # -----------------------------------------------------------------------------

    def before_update(self) -> None:
        """Before update entity hook"""
        self.updated_at = datetime.datetime.now()

    # -----------------------------------------------------------------------------

    def after_update(self) -> None:
        """After update entity hook"""
        di[EventDispatcher].dispatch(
            ModelEntityUpdatedEvent.EVENT_NAME,
            ModelEntityUpdatedEvent(self),
        )

    # -----------------------------------------------------------------------------

    def after_delete(self) -> None:
        """After delete entity hook"""
        di[EventDispatcher].dispatch(
            ModelEntityDeletedEvent.EVENT_NAME,
            ModelEntityDeletedEvent(self),
        )


class ManualTriggerEntity(TriggerEntity):
    """
    Manual trigger entity

    @package        FastyBird:TriggersModule!
    @module         models

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    _discriminator_: str = "manual"


class AutomaticTriggerEntity(TriggerEntity):
    """
    Automatic trigger entity

    @package        FastyBird:TriggersModule!
    @module         models

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    _discriminator_: str = "automatic"

    conditions: List["ConditionEntity"] = Set("ConditionEntity", reverse="trigger")


class TriggerControlEntity(db.Entity):  # type: ignore[no-any-unimported]
    """
    Trigger control entity

    @package        FastyBird:TriggersModule!
    @module         models

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    _table_: str = "fb_triggers_controls"

    control_id: uuid.UUID = PrimaryKey(uuid.UUID, default=uuid.uuid4, column="control_id")
    name: str = OptionalField(str, column="control_name", nullable=False)

    created_at: Optional[datetime.datetime] = OptionalField(datetime.datetime, column="created_at", nullable=True)
    updated_at: Optional[datetime.datetime] = OptionalField(datetime.datetime, column="updated_at", nullable=True)

    trigger: TriggerEntity = RequiredField("TriggerEntity", reverse="controls", column="trigger_id", nullable=False)

    # -----------------------------------------------------------------------------

    def before_insert(self) -> None:
        """Before insert entity hook"""
        self.created_at = datetime.datetime.now()

    # -----------------------------------------------------------------------------

    def after_insert(self) -> None:
        """After insert entity hook"""
        di[EventDispatcher].dispatch(
            ModelEntityCreatedEvent.EVENT_NAME,
            ModelEntityCreatedEvent(self),
        )

    # -----------------------------------------------------------------------------

    def before_update(self) -> None:
        """Before update entity hook"""
        self.updated_at = datetime.datetime.now()

    # -----------------------------------------------------------------------------

    def after_update(self) -> None:
        """After update entity hook"""
        di[EventDispatcher].dispatch(
            ModelEntityUpdatedEvent.EVENT_NAME,
            ModelEntityUpdatedEvent(self),
        )

    # -----------------------------------------------------------------------------

    def after_delete(self) -> None:
        """After delete entity hook"""
        di[EventDispatcher].dispatch(
            ModelEntityDeletedEvent.EVENT_NAME,
            ModelEntityDeletedEvent(self),
        )


class ActionEntity(db.Entity):  # type: ignore[no-any-unimported]
    """
    Base action entity

    @package        FastyBird:TriggersModule!
    @module         models

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    _table_: str = "fb_actions"

    type = Discriminator(str, column="action_type")

    action_id: uuid.UUID = PrimaryKey(uuid.UUID, default=uuid.uuid4, column="action_id")
    enabled: bool = RequiredField(bool, column="action_enabled", nullable=False, default=True)

    created_at: Optional[datetime.datetime] = OptionalField(datetime.datetime, column="created_at", nullable=True)
    updated_at: Optional[datetime.datetime] = OptionalField(datetime.datetime, column="updated_at", nullable=True)

    trigger: TriggerEntity = RequiredField("TriggerEntity", reverse="actions", column="trigger_id", nullable=False)

    # -----------------------------------------------------------------------------

    def to_dict(
        self,
        only: Union[List[str], str, None] = None,  # pylint: disable=unused-argument
        exclude: Union[List[str], str, None] = None,  # pylint: disable=unused-argument
        with_collections: bool = False,  # pylint: disable=unused-argument
        with_lazy: bool = False,  # pylint: disable=unused-argument
        related_objects: bool = False,  # pylint: disable=unused-argument
    ) -> Dict[str, Union[str, int, bool, None]]:
        """Transform entity to dictionary"""
        return {
            "id": self.action_id.__str__(),
            "type": self.type,
            "enabled": self.enabled,
            "trigger": self.trigger.trigger_id.__str__(),
        }

    # -----------------------------------------------------------------------------

    def before_insert(self) -> None:
        """Before insert entity hook"""
        self.created_at = datetime.datetime.now()

    # -----------------------------------------------------------------------------

    def after_insert(self) -> None:
        """After insert entity hook"""
        di[EventDispatcher].dispatch(
            ModelEntityCreatedEvent.EVENT_NAME,
            ModelEntityCreatedEvent(self),
        )

    # -----------------------------------------------------------------------------

    def before_update(self) -> None:
        """Before update entity hook"""
        self.updated_at = datetime.datetime.now()

    # -----------------------------------------------------------------------------

    def after_update(self) -> None:
        """After update entity hook"""
        di[EventDispatcher].dispatch(
            ModelEntityUpdatedEvent.EVENT_NAME,
            ModelEntityUpdatedEvent(self),
        )

    # -----------------------------------------------------------------------------

    def after_delete(self) -> None:
        """After delete entity hook"""
        di[EventDispatcher].dispatch(
            ModelEntityDeletedEvent.EVENT_NAME,
            ModelEntityDeletedEvent(self),
        )


class PropertyActionEntity(ActionEntity):
    """
    Property action entity

    @package        FastyBird:TriggersModule!
    @module         models

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    device: uuid.UUID = RequiredField(uuid.UUID, column="action_device", nullable=True)

    value: str = RequiredField(str, column="action_value", max_len=100, nullable=True)

    # -----------------------------------------------------------------------------

    @property
    def value_formatted(self) -> Union[str, ButtonPayload, SwitchPayload]:
        """Transform value to enum value"""
        if ButtonPayload.has_value(self.value):
            return ButtonPayload(self.value)

        if SwitchPayload.has_value(self.value):
            return SwitchPayload(self.value)

        return self.value

    # -----------------------------------------------------------------------------

    def to_dict(
        self,
        only: Union[List[str], str, None] = None,
        exclude: Union[List[str], str, None] = None,
        with_collections: bool = False,
        with_lazy: bool = False,
        related_objects: bool = False,
    ) -> Dict[str, Union[str, int, bool, None]]:
        """Transform entity to dictionary"""
        return {
            **{
                "device": self.device.__str__(),
                "value": self.value,
            },
            **super().to_dict(only, exclude, with_collections, with_lazy, related_objects),
        }


class DevicePropertyActionEntity(PropertyActionEntity):
    """
    Device property action entity

    @package        FastyBird:TriggersModule!
    @module         models

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    _discriminator_: str = "device-property"

    device_property: uuid.UUID = RequiredField(uuid.UUID, column="action_device_property", nullable=True)

    # -----------------------------------------------------------------------------

    def to_dict(
        self,
        only: Union[List[str], str, None] = None,
        exclude: Union[List[str], str, None] = None,
        with_collections: bool = False,
        with_lazy: bool = False,
        related_objects: bool = False,
    ) -> Dict[str, Union[str, int, bool, None]]:
        """Transform entity to dictionary"""
        return {
            **{
                "property": self.device_property.__str__(),
            },
            **super().to_dict(only, exclude, with_collections, with_lazy, related_objects),
        }


class ChannelPropertyActionEntity(PropertyActionEntity):
    """
    Channel property action entity

    @package        FastyBird:TriggersModule!
    @module         models

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    _discriminator_: str = "channel-property"

    channel: uuid.UUID = RequiredField(uuid.UUID, column="action_channel", nullable=True)
    channel_property: uuid.UUID = RequiredField(uuid.UUID, column="action_channel_property", nullable=True)

    # -----------------------------------------------------------------------------

    def to_dict(
        self,
        only: Union[List[str], str, None] = None,
        exclude: Union[List[str], str, None] = None,
        with_collections: bool = False,
        with_lazy: bool = False,
        related_objects: bool = False,
    ) -> Dict[str, Union[str, int, bool, None]]:
        """Transform entity to dictionary"""
        return {
            **{
                "channel": self.channel.__str__(),
                "property": self.channel_property.__str__(),
            },
            **super().to_dict(only, exclude, with_collections, with_lazy, related_objects),
        }


class NotificationEntity(db.Entity):  # type: ignore[no-any-unimported]
    """
    Base notification entity

    @package        FastyBird:TriggersModule!
    @module         models

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    _table_: str = "fb_notifications"

    type = Discriminator(str, column="notification_type")

    notification_id: uuid.UUID = PrimaryKey(uuid.UUID, default=uuid.uuid4, column="notification_id")
    enabled: bool = RequiredField(bool, column="notification_enabled", nullable=False, default=True)

    created_at: Optional[datetime.datetime] = OptionalField(datetime.datetime, column="created_at", nullable=True)
    updated_at: Optional[datetime.datetime] = OptionalField(datetime.datetime, column="updated_at", nullable=True)

    trigger: TriggerEntity = RequiredField(
        "TriggerEntity",
        reverse="notifications",
        column="trigger_id",
        nullable=False,
    )

    # -----------------------------------------------------------------------------

    def to_dict(
        self,
        only: Union[List[str], str, None] = None,  # pylint: disable=unused-argument
        exclude: Union[List[str], str, None] = None,  # pylint: disable=unused-argument
        with_collections: bool = False,  # pylint: disable=unused-argument
        with_lazy: bool = False,  # pylint: disable=unused-argument
        related_objects: bool = False,  # pylint: disable=unused-argument
    ) -> Dict[str, Union[str, int, bool, None]]:
        """Transform entity to dictionary"""
        return {
            "id": self.notification_id.__str__(),
            "type": self.type,
            "enabled": self.enabled,
            "trigger": self.trigger.trigger_id.__str__(),
        }

    # -----------------------------------------------------------------------------

    def before_insert(self) -> None:
        """Before insert entity hook"""
        self.created_at = datetime.datetime.now()

    # -----------------------------------------------------------------------------

    def after_insert(self) -> None:
        """After insert entity hook"""
        di[EventDispatcher].dispatch(
            ModelEntityCreatedEvent.EVENT_NAME,
            ModelEntityCreatedEvent(self),
        )

    # -----------------------------------------------------------------------------

    def before_update(self) -> None:
        """Before update entity hook"""
        self.updated_at = datetime.datetime.now()

    # -----------------------------------------------------------------------------

    def after_update(self) -> None:
        """After update entity hook"""
        di[EventDispatcher].dispatch(
            ModelEntityUpdatedEvent.EVENT_NAME,
            ModelEntityUpdatedEvent(self),
        )

    # -----------------------------------------------------------------------------

    def after_delete(self) -> None:
        """After delete entity hook"""
        di[EventDispatcher].dispatch(
            ModelEntityDeletedEvent.EVENT_NAME,
            ModelEntityDeletedEvent(self),
        )


class EmailNotificationEntity(NotificationEntity):
    """
    Email notification entity

    @package        FastyBird:TriggersModule!
    @module         models

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    _discriminator_: str = "email"

    email: str = RequiredField(str, column="notification_email", max_len=150, nullable=True)

    # -----------------------------------------------------------------------------

    def to_dict(
        self,
        only: Union[List[str], str, None] = None,
        exclude: Union[List[str], str, None] = None,
        with_collections: bool = False,
        with_lazy: bool = False,
        related_objects: bool = False,
    ) -> Dict[str, Union[str, int, bool, None]]:
        """Transform entity to dictionary"""
        return {
            **{
                "email": self.email,
            },
            **super().to_dict(only, exclude, with_collections, with_lazy, related_objects),
        }


class SmsNotificationEntity(NotificationEntity):
    """
    SMS notification entity

    @package        FastyBird:TriggersModule!
    @module         models

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    _discriminator_: str = "sms"

    phone: str = RequiredField(str, column="notification_phone", max_len=150, nullable=True)

    # -----------------------------------------------------------------------------

    def to_dict(
        self,
        only: Union[List[str], str, None] = None,
        exclude: Union[List[str], str, None] = None,
        with_collections: bool = False,
        with_lazy: bool = False,
        related_objects: bool = False,
    ) -> Dict[str, Union[str, int, bool, None]]:
        """Transform entity to dictionary"""
        return {
            **{
                "phone": self.phone,
            },
            **super().to_dict(only, exclude, with_collections, with_lazy, related_objects),
        }


class ConditionEntity(db.Entity):  # type: ignore[no-any-unimported]
    """
    Base condition entity

    @package        FastyBird:TriggersModule!
    @module         models

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    _table_: str = "fb_conditions"

    type = Discriminator(str, column="condition_type")

    condition_id: uuid.UUID = PrimaryKey(uuid.UUID, default=uuid.uuid4, column="condition_id")
    enabled: bool = RequiredField(bool, column="condition_enabled", nullable=False, default=True)

    created_at: Optional[datetime.datetime] = OptionalField(datetime.datetime, column="created_at", nullable=True)
    updated_at: Optional[datetime.datetime] = OptionalField(datetime.datetime, column="updated_at", nullable=True)

    trigger: AutomaticTriggerEntity = RequiredField(
        "AutomaticTriggerEntity",
        reverse="conditions",
        column="trigger_id",
        nullable=False,
    )

    # -----------------------------------------------------------------------------

    def to_dict(
        self,
        only: Union[List[str], str, None] = None,  # pylint: disable=unused-argument
        exclude: Union[List[str], str, None] = None,  # pylint: disable=unused-argument
        with_collections: bool = False,  # pylint: disable=unused-argument
        with_lazy: bool = False,  # pylint: disable=unused-argument
        related_objects: bool = False,  # pylint: disable=unused-argument
    ) -> Dict[str, Union[str, int, bool, datetime.timedelta, datetime.datetime, None]]:
        """Transform entity to dictionary"""
        return {
            "id": self.condition_id.__str__(),
            "type": self.type,
            "enabled": self.enabled,
            "trigger": self.trigger.trigger_id.__str__(),
        }

    # -----------------------------------------------------------------------------

    def before_insert(self) -> None:
        """Before insert entity hook"""
        self.created_at = datetime.datetime.now()

    # -----------------------------------------------------------------------------

    def after_insert(self) -> None:
        """After insert entity hook"""
        di[EventDispatcher].dispatch(
            ModelEntityCreatedEvent.EVENT_NAME,
            ModelEntityCreatedEvent(self),
        )

    # -----------------------------------------------------------------------------

    def before_update(self) -> None:
        """Before update entity hook"""
        self.updated_at = datetime.datetime.now()

    # -----------------------------------------------------------------------------

    def after_update(self) -> None:
        """After update entity hook"""
        di[EventDispatcher].dispatch(
            ModelEntityUpdatedEvent.EVENT_NAME,
            ModelEntityUpdatedEvent(self),
        )

    # -----------------------------------------------------------------------------

    def after_delete(self) -> None:
        """After delete entity hook"""
        di[EventDispatcher].dispatch(
            ModelEntityDeletedEvent.EVENT_NAME,
            ModelEntityDeletedEvent(self),
        )


class PropertyConditionEntity(ConditionEntity):
    """
    Property condition entity

    @package        FastyBird:TriggersModule!
    @module         models

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    operator: str = RequiredField(str, column="condition_operator", nullable=True)
    operand: str = RequiredField(str, column="condition_operand", max_len=100, nullable=True)

    device: uuid.UUID = RequiredField(uuid.UUID, column="condition_device", nullable=True)

    # -----------------------------------------------------------------------------

    @property
    def operator_formatted(self) -> TriggerConditionOperator:
        """Transform operator to enum value"""
        return TriggerConditionOperator(self.operator)

    # -----------------------------------------------------------------------------

    @property
    def operand_formatted(self) -> Union[str, ButtonPayload, SwitchPayload]:
        """Transform operand to enum value"""
        if ButtonPayload.has_value(self.operand):
            return ButtonPayload(self.operand)

        if SwitchPayload.has_value(self.operand):
            return SwitchPayload(self.operand)

        return self.operand

    # -----------------------------------------------------------------------------

    def to_dict(
        self,
        only: Union[List[str], str, None] = None,
        exclude: Union[List[str], str, None] = None,
        with_collections: bool = False,
        with_lazy: bool = False,
        related_objects: bool = False,
    ) -> Dict[str, Union[str, int, bool, datetime.timedelta, datetime.datetime, None]]:
        """Transform entity to dictionary"""
        return {
            **{
                "operator": self.operator_formatted.value,
                "operand": self.operand,
                "device": self.device.__str__(),
            },
            **super().to_dict(only, exclude, with_collections, with_lazy, related_objects),
        }


class DevicePropertyConditionEntity(PropertyConditionEntity):
    """
    Device property condition entity

    @package        FastyBird:TriggersModule!
    @module         models

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    _discriminator_: str = "device-property"

    device_property: uuid.UUID = RequiredField(uuid.UUID, column="condition_device_property", nullable=True)

    # -----------------------------------------------------------------------------

    def to_dict(
        self,
        only: Union[List[str], str, None] = None,
        exclude: Union[List[str], str, None] = None,
        with_collections: bool = False,
        with_lazy: bool = False,
        related_objects: bool = False,
    ) -> Dict[str, Union[str, int, bool, datetime.timedelta, datetime.datetime, None]]:
        """Transform entity to dictionary"""
        return {
            **{
                "property": self.device_property.__str__(),
            },
            **super().to_dict(only, exclude, with_collections, with_lazy, related_objects),
        }


class ChannelPropertyConditionEntity(PropertyConditionEntity):
    """
    Channel property condition entity

    @package        FastyBird:TriggersModule!
    @module         models

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    _discriminator_: str = "channel-property"

    channel: uuid.UUID = RequiredField(uuid.UUID, column="condition_channel", nullable=True)
    channel_property: uuid.UUID = RequiredField(uuid.UUID, column="condition_channel_property", nullable=True)

    # -----------------------------------------------------------------------------

    def to_dict(
        self,
        only: Union[List[str], str, None] = None,
        exclude: Union[List[str], str, None] = None,
        with_collections: bool = False,
        with_lazy: bool = False,
        related_objects: bool = False,
    ) -> Dict[str, Union[str, int, bool, datetime.timedelta, datetime.datetime, None]]:
        """Transform entity to dictionary"""
        return {
            **{
                "channel": self.channel.__str__(),
                "property": self.channel_property.__str__(),
            },
            **super().to_dict(only, exclude, with_collections, with_lazy, related_objects),
        }


class TimeConditionEntity(ConditionEntity):
    """
    Time property condition entity

    @package        FastyBird:TriggersModule!
    @module         models

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    _discriminator_: str = "time"

    time: datetime.timedelta = RequiredField(datetime.timedelta, column="condition_time", nullable=True)
    days: str = RequiredField(str, column="condition_days", max_len=100, nullable=True)

    # -----------------------------------------------------------------------------

    def to_dict(
        self,
        only: Union[List[str], str, None] = None,
        exclude: Union[List[str], str, None] = None,
        with_collections: bool = False,
        with_lazy: bool = False,
        related_objects: bool = False,
    ) -> Dict[str, Union[str, int, bool, datetime.timedelta, datetime.datetime, None]]:
        """Transform entity to dictionary"""
        return {
            **{
                "time": self.time,
                "days": self.days,
            },
            **super().to_dict(only, exclude, with_collections, with_lazy, related_objects),
        }


class DateConditionEntity(ConditionEntity):
    """
    Date property condition entity

    @package        FastyBird:TriggersModule!
    @module         models

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    _discriminator_: str = "date"

    date: datetime.datetime = RequiredField(datetime.datetime, column="condition_date", nullable=True)

    # -----------------------------------------------------------------------------

    def to_dict(
        self,
        only: Union[List[str], str, None] = None,
        exclude: Union[List[str], str, None] = None,
        with_collections: bool = False,
        with_lazy: bool = False,
        related_objects: bool = False,
    ) -> Dict[str, Union[str, int, bool, datetime.timedelta, datetime.datetime, None]]:
        """Transform entity to dictionary"""
        return {
            **{
                "date": self.date,
            },
            **super().to_dict(only, exclude, with_collections, with_lazy, related_objects),
        }
