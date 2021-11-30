import uuid
from drb import DrbNode
from drb.factory import DrbFactory, DrbSignature, DrbSignatureType
from drb.utils.logical_node import DrbLogicalNode


class TextNode(DrbLogicalNode):
    def __init__(self, node: DrbNode):
        super().__init__(node)


class TextFactory(DrbFactory):
    def _create(self, node: DrbNode) -> DrbNode:
        return TextNode(node)


class TextSignature(DrbSignature):
    def __init__(self):
        self._factory = TextFactory()

    @property
    def uuid(self) -> uuid.UUID:
        return uuid.UUID('3d797648-281a-11ec-9621-0242ac130002')

    @property
    def label(self) -> str:
        return 'Text'

    @property
    def category(self) -> DrbSignatureType:
        return DrbSignatureType.FORMATTING

    @property
    def factory(self) -> DrbFactory:
        return self._factory

    def match(self, node: DrbNode) -> bool:
        return node.name.endswith('.txt')
