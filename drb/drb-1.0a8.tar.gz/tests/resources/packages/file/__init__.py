import uuid
from drb import DrbNode
from drb.factory import DrbFactory, DrbSignature, DrbSignatureType


class FileFactory(DrbFactory):
    def _create(self, node: DrbNode) -> DrbNode:
        return node


class FileSignature(DrbSignature):
    def __init__(self):
        self._factory = FileFactory()

    @property
    def uuid(self) -> uuid.UUID:
        return uuid.UUID('99e6ce18-276f-11ec-9621-0242ac130002')

    @property
    def label(self) -> str:
        return 'file'

    @property
    def category(self) -> DrbSignatureType:
        return DrbSignatureType.PROTOCOL

    @property
    def factory(self) -> DrbFactory:
        return self._factory

    def match(self, node: DrbNode) -> bool:
        if node.path.is_local:
            scheme = node.path.scheme
            return scheme is None or '' == scheme or 'file' == scheme
        return False
