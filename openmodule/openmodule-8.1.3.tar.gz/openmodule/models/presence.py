from datetime import datetime
from typing import Optional, List, Union

from pydantic import Field

from openmodule.models.base import ZMQMessage, OpenModuleModel, Gateway, timezone_validator
from openmodule.models.vehicle import Medium, LPRMedium, MakeModel, PresenceAllIds


class PresenceMedia(OpenModuleModel):
    lpr: Optional[LPRMedium]
    qr: Optional[Medium]
    nfc: Optional[Medium]
    pin: Optional[Medium]


class PresenceBaseMessage(ZMQMessage):
    vehicle_id: int
    source: str
    present_area_name: str = Field(..., alias="present-area-name")
    last_update: datetime
    gateway: Gateway
    medium: PresenceMedia
    make_model: Optional[MakeModel]
    all_ids: PresenceAllIds

    _tz_last_update = timezone_validator("last_update")


class PresenceBackwardMessage(PresenceBaseMessage):
    type: str = "backward"
    unsure: bool = False
    leave_time: datetime = Field(..., alias="leave-time")
    bidirectional_inverse: bool = False

    _tz_leave_time = timezone_validator("leave_time")


class PresenceForwardMessage(PresenceBaseMessage):
    type: str = "forward"
    unsure: bool = False
    leave_time: datetime = Field(..., alias="leave-time")
    bidirectional_inverse: bool = False

    _tz_leave_time = timezone_validator("leave_time")


class PresenceLeaveMessage(PresenceBaseMessage):
    type: str = "leave"
    num_presents: int = Field(0, alias="num-presents")


class PresenceEnterMessage(PresenceBaseMessage):
    type: str = "enter"


class PresenceChangeMessage(PresenceBaseMessage):
    type: str = "change"
    change_vehicle_id: Optional[bool]
