import os
import uuid

from drb.factory import DrbSignature, DrbSignatureType, DrbFactory

from drb import DrbNode
from .netcdf_node_factory import DrbNetcdfFactory


class DrbNetcdfSignature(DrbSignature):
    def __init__(self):
        self._factory = DrbNetcdfFactory()

    @property
    def uuid(self) -> uuid.UUID:
        return uuid.UUID('83720abe-2c0e-11ec-8d3d-0242ac130003')

    @property
    def label(self) -> str:
        return 'netcdf'

    @property
    def category(self) -> DrbSignatureType:
        return DrbSignatureType.FORMATTING

    @property
    def factory(self) -> DrbFactory:
        return self._factory

    def match(self, node: DrbNode) -> bool:
        supported_ext = {
            '.nc'
        }

        filename, file_extension = os.path.splitext(node.path.filename)
        return file_extension and file_extension.lower() in supported_ext
