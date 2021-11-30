import uuid
from drb import DrbNode
from drb.factory import DrbFactory, DrbSignature, DrbSignatureType


class XmlFactory(DrbFactory):
    def _create(self, node: DrbNode) -> DrbNode:
        return node


class XmlSignature(DrbSignature):
    def __init__(self):
        self._factory = XmlFactory()

    @property
    def uuid(self) -> uuid.UUID:
        return uuid.UUID('aced0812-2830-11ec-9621-0242ac130002')

    @property
    def label(self) -> str:
        return 'Extensible Markup Language'

    @property
    def category(self) -> DrbSignatureType:
        return DrbSignatureType.FORMATTING

    @property
    def factory(self) -> DrbFactory:
        return self._factory

    def match(self, node: DrbNode) -> bool:
        return node.name.endswith('.xml')
