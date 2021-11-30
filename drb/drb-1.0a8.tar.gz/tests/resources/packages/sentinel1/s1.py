import re
import uuid
from drb import DrbNode
from drb.factory import DrbFactory, DrbSignatureType

from safe import SafeSignature


class Sentinel1Factory(DrbFactory):
    def _create(self, node: DrbNode) -> DrbNode:
        return node


class Sentinel1Signature(SafeSignature):
    def __init__(self):
        self._factory = Sentinel1Factory()

    @property
    def uuid(self) -> uuid.UUID:
        return uuid.UUID('84a54dea-2800-11ec-9621-0242ac130002')

    @property
    def label(self) -> str:
        return 'Sentinel-1'

    @property
    def category(self) -> DrbSignatureType:
        return DrbSignatureType.CONTAINER

    @property
    def factory(self) -> DrbFactory:
        return self._factory

    def match(self, node: DrbNode) -> bool:
        return re.match(r'S1[AB]_.{63}.SAFE', node.name) is not None
