import uuid
from drb import DrbNode
from drb.factory import DrbFactory, DrbSignature, DrbSignatureType
from drb.exceptions import DrbException


class SafeFactory(DrbFactory):
    def _create(self, node: DrbNode) -> DrbNode:
        return node


class SafeSignature(DrbSignature):
    def __init__(self):
        self._factory = SafeFactory()

    @property
    def uuid(self) -> uuid.UUID:
        return uuid.UUID('c44c2f36-2779-11ec-9621-0242ac130002')

    @property
    def label(self) -> str:
        return 'safe-product'

    @property
    def category(self) -> DrbSignatureType:
        return DrbSignatureType.CONTAINER

    @property
    def factory(self) -> DrbFactory:
        return self._factory

    def match(self, node: DrbNode) -> bool:
        try:
            return node.name.endswith('.SAFE') and \
                   node[('manifest.safe', None, 1)] is not None
        except KeyError:
            return False
