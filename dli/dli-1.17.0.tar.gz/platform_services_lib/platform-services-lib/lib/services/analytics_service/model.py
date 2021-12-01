#
# Copyright (C) 2019 IHS Markit.
# All Rights Reserved
#
import dataclasses
from typing import Optional


@dataclasses.dataclass
class AnalyticsEvent:
    application_name: str
    application_version: str
    user_id: str
    entity: str
    action: Optional[str] = None
    organisation_id: Optional[str] = None
    result: Optional[int] = None
    properties: Optional[dict] = None
