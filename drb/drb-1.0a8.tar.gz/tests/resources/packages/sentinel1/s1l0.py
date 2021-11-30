import re
import uuid
from drb import DrbNode
from drb.factory import DrbFactory, DrbSignatureType

from .s1 import Sentinel1Signature


class Sentinel1l0Signature(Sentinel1Signature):
    @property
    def uuid(self) -> uuid.UUID:
        return uuid.UUID('4d28758a-2806-11ec-9621-0242ac130002')

    @property
    def label(self) -> str:
        return 'Sentinel-1 Level 0'

    @property
    def category(self) -> DrbSignatureType:
        return DrbSignatureType.CONTAINER

    @property
    def factory(self) -> DrbFactory:
        return super().factory

    def match(self, node: DrbNode) -> bool:
        regex = r'.*((EW|IW|WV|RF|S[1-6])_RAW__0(C|N|S|A)' \
                r'(SH|SV|HH|VV|HV|VH|DH|DV)|(GP|HK)_RAW__0___).*'
        return re.match(regex, node.name) is not None
