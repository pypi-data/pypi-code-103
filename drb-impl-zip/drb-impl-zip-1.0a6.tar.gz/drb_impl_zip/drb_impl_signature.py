import os
import uuid

from drb.factory import DrbSignature, DrbSignatureType, DrbFactory

from drb import DrbNode
from .file_zip_node import DrbZipFactory


class DrbZipSignature(DrbSignature):
    def __init__(self):
        self._factory = DrbZipFactory()

    @property
    def uuid(self) -> uuid.UUID:
        return uuid.UUID('da61a26a-2b34-11ec-8d3d-0242ac130003')

    @property
    def label(self) -> str:
        return 'zip'

    @property
    def category(self) -> DrbSignatureType:
        return DrbSignatureType.CONTAINER

    @property
    def factory(self) -> DrbFactory:
        return self._factory

    def match(self, node: DrbNode) -> bool:
        supported_ext = {
            '.zip'
        }

        filename, file_extension = os.path.splitext(node.path.filename)
        return file_extension and file_extension.lower() in supported_ext
