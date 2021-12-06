import unittest
from tests.conftest import *


class TestQuickAndHoldPay(unittest.TestCase):

    def setUp(self):
        dg_sdk.DGClient.mer_config = dg_sdk.MerConfig(private_key, public_key, sys_id, product_id, huifu_id)

        print("setup")

    def tearDown(self):
        print("tearDown")

    # def test_quick_create(self):
    #
    #     result =
    #
    #     assert result["resp_code"] == "20000007"

    def test_drawcash_query(self):

        result = dg_sdk.Drawcash.query("20211123", org_req_seq_id="dsfasdfs")

        assert result["resp_code"] == "20000004"


