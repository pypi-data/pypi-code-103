import uuid

from drb.factory import DrbSignature, DrbSignatureType, DrbFactory

from drb import DrbNode
from drb_impl_file import DrbFileFactory


class DrbFileSignature(DrbSignature):
    def __init__(self):
        self._factory = DrbFileFactory()

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
