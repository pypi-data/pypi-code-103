from radicl.api import *
from . import MockRADPort
import pytest


class Test_RAD_API():
    @pytest.fixture()
    def api(self, payload):
        p = MockRADPort(payload=payload)
        return RAD_API(port=p)

    @pytest.mark.parametrize('payload, expected', [
        ([0x00, 0x00, 0x00, 0x00, 0x00], 10)
    ])
    def test_getHWID(self, api, expected):
        a = api.getHWID()
        print(a)
