import os
import uuid

from drb.factory import DrbSignature, DrbSignatureType, DrbFactory
from drb import DrbNode
from .file_tar_node import DrbTarFactory


class DrbTarSignature(DrbSignature):
    def __init__(self):

        self._factory = DrbTarFactory()

    @property
    def uuid(self) -> uuid.UUID:
        return uuid.UUID('60e58ee2-2b5c-11ec-8d3d-0242ac130003')

    @property
    def label(self) -> str:
        return 'tar'

    @property
    def category(self) -> DrbSignatureType:
        return DrbSignatureType.CONTAINER

    @property
    def factory(self) -> DrbFactory:
        return self._factory

    def match(self, node: DrbNode) -> bool:
        supported_ext = {
            '.tar'
        }

        filename, file_extension = os.path.splitext(node.path.filename)
        return file_extension and file_extension.lower() in supported_ext
