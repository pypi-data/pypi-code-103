import abc
import logging
from enum import Enum
from typing import List, Optional, Dict, Any, Iterable
from typing import TypeVar
from typing import Union
from uuid import UUID
from datetime import datetime, timezone

from pydantic import BaseModel, Field, HttpUrl, ValidationError, validator, UUID4, Json


class Location(BaseModel):
    longitude: float = Field(..., ge=-180.0, le=360.0, title="Longitude in decimal degrees")
    latitude: float = Field(..., ge=-90.0, le=90.0, title="Latitude in decimal degrees")


class Event(BaseModel):
    id: Optional[UUID4] = Field(None, title='Event ID', description='The unique ID for the event')
    serial_number: Optional[int] = Field(None, title='Serial Number')
    message: Optional[Any] = Field(None, title='Event Message')
    comment: Optional[str] = Field(None, description='Additional message text')
    title: Optional[str] = Field(None, title='Event Title')
    time: datetime = Field(..., title='Event Time', description='Timestamp for the data, preferrably in ISO format.',
                           example='2021-03-21 12:01:02-0700')
    end_time: Optional[datetime]
    provenance: Optional[str]
    priority: Optional[int]
    state: Optional[str]
    event_type: str
    location: Location
    attributes: Optional[Json]
    created_at: Optional[datetime]
    # reported_by: Optional[dict]
    event_details: Optional[Dict[str, Any]]

    class Config:
        title = 'Event'


class Observation(BaseModel):
    id: Optional[UUID4]
    manufacturer_id: str
    source_type: Optional[str]
    recorded_at: datetime
    location: Location
    additional: Optional[Dict[str, Any]]