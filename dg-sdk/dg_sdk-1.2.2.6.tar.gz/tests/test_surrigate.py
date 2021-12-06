import unittest
from tests.conftest import *


class TestAcctPayment(unittest.TestCase):

    def setUp(self):
        dg_sdk.DGClient.mer_config = dg_sdk.MerConfig(private_key, public_key, sys_id, product_id, huifu_id)

        print("setup")

    def tearDown(self):
        print("tearDown")

    def test_drawcash_create(self):
        result = dg_sdk.Drawcash.create(cash_amt="0.01",
                                           token_no="121231312",
                                           into_acct_date_type="D1")

        assert result["resp_code"] == "20000007"

    def test_drawcash_query(self):

        result = dg_sdk.Drawcash.query("20211123", org_req_seq_id="dsfasdfs")

        assert result["resp_code"] == "20000004"


