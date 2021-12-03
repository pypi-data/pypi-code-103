from enum import Enum
from typing import Dict

from pydantic import BaseModel


class CalibrationType(str, Enum):
    PINHOLE = "pinhole"
    FISHEYE = "fisheye"
    KANNALA = "kannala"
    LIDAR = "lidar"


class BaseSerializer(BaseModel):

    @classmethod
    def from_json(cls, js: Dict):
        return cls.parse_obj(js)

    def to_dict(self) -> Dict:
        return self.dict(exclude_none=True)


class RotationQuaternion(BaseSerializer):
    w: float
    x: float
    y: float
    z: float


class Position(BaseSerializer):
    x: float
    y: float
    z: float


class BaseCalibration(BaseSerializer):
    position: Position
    rotation_quaternion: RotationQuaternion
