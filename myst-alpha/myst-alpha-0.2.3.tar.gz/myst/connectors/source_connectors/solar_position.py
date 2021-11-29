import enum
from typing import List
from uuid import UUID

from myst.connectors.source_connector import SourceConnector


@enum.unique
class Field(str, enum.Enum):
    AZIMUTH = "azimuth"
    ELEVATION = "elevation"
    ZENITH = "zenith"


class SolarPosition(SourceConnector):
    def __init__(self, latitude: float, longitude: float, fields: List[Field]) -> None:
        super().__init__(
            uuid=UUID("9bf1b9dd-fd14-4b1e-bd47-a238dbcfc551"),
            parameters=dict(latitude=latitude, longitude=longitude, fields=fields),
        )
