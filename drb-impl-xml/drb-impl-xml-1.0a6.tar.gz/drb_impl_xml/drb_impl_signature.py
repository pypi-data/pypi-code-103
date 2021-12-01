import os
import uuid

from drb.factory import DrbSignature, DrbSignatureType, DrbFactory

from drb import DrbNode
from .xml_node_factory import XmlNodeFactory


class DrbXmlSignature(DrbSignature):
    def __init__(self):
        self._factory = XmlNodeFactory()

    @property
    def uuid(self) -> uuid.UUID:
        return uuid.UUID('40123218-2b5e-11ec-8d3d-0242ac130003')

    @property
    def label(self) -> str:
        return 'xml'

    @property
    def category(self) -> DrbSignatureType:
        return DrbSignatureType.FORMATTING

    @property
    def factory(self) -> DrbFactory:
        return self._factory

    def match(self, node: DrbNode) -> bool:
        supported_ext = {
            '.xml'
        }

        filename, file_extension = os.path.splitext(node.path.filename)
        return file_extension and file_extension.lower() in supported_ext
