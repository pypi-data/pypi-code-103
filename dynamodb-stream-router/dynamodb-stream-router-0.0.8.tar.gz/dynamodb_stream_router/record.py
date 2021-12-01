from __future__ import annotations

from base64 import b64decode
from copy import deepcopy
from typing import Any, TypedDict

from boto3.dynamodb.types import TypeDeserializer

AttributeValueMap = dict[str, dict[str, Any]]


class Identity(TypedDict, total=False):
    PrincipalId: str
    Type: str


class StreamRecord(TypedDict, total=False):
    ApproximateCreationDateTime: int
    Keys: AttributeValueMap
    NewImage: AttributeValueMap
    OldImage: AttributeValueMap
    SequenceNumber: str
    SizeBytes: int
    StreamViewType: str


class Record(TypedDict, total=False):
    awsRegion: str
    dynamodb: StreamRecord
    eventID: str
    eventName: str
    eventSource: str
    eventSourceARN: str
    eventVersion: str
    userIdentity: Identity


class StreamTypeDeserializer(TypeDeserializer):
    def _deserialize_b(self, value):
        if isinstance(value, str):
            value = b64decode(value)
        return super()._deserialize_b(value)


class RouteRecord:
    __DESERIALIZER = StreamTypeDeserializer()

    def __init__(self, record: Record) -> None:
        self.__keys: dict[str, Any] = None
        self.__new_image: dict[str, Any] = None
        self.__old_image: dict[str, Any] = None
        self.__record = record

    @property
    def keys(self) -> dict[str, Any]:
        if self.__keys is None and "Keys" in self.__record["dynamodb"]:
            self.__keys = self.__DESERIALIZER.deserialize(
                dict(M=self.__record["dynamodb"]["Keys"])
            )
        return deepcopy(self.__keys)

    @property
    def new_image(self) -> dict[str, Any]:
        if self.__new_image is None and "NewImage" in self.__record["dynamodb"]:
            self.__new_image = self.__DESERIALIZER.deserialize(
                dict(M=self.__record["dynamodb"]["NewImage"])
            )
        return deepcopy(self.__new_image)

    @property
    def old_image(self) -> dict[str, Any]:
        if self.__old_image is None and "OldImage" in self.__record["dynamodb"]:
            self.__old_image = self.__DESERIALIZER.deserialize(
                dict(M=self.__record["dynamodb"]["OldImage"])
            )
        return deepcopy(self.__old_image)

    @property
    def record(self) -> Record:
        return deepcopy(self.__record)
