from __future__ import annotations

from media_platform.lang.serialization import Deserializable


class Protocol:
    tus = 'tus'

    @classmethod
    def has_value(cls, value):
        return value in [cls.tus]


class UploadConfiguration(Deserializable):
    def __init__(self, upload_url: str):
        self.upload_url = upload_url

    @classmethod
    def deserialize(cls, data: dict) -> UploadConfiguration:
        return UploadConfiguration(data['uploadUrl'])
