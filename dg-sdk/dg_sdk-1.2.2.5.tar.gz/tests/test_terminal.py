import unittest
import dg_sdk
from tests.conftest import *


class TestTerminal(unittest.TestCase):

    def setUp(self):

        dg_sdk.DGClient.mer_config = dg_sdk.MerConfig(private_key, public_key, sys_id, product_id, huifu_id)

        print("setup")

    def tearDown(self):
        print("tearDown")

    def test_terminal_create(self):
        result = dg_sdk.Terminal.create(order_status="10")
        assert result["resp_code"] == "00000000"

    def test_terminal_query(self):

        result = dg_sdk.Terminal.query_detail(order_id="12123123123123")

        assert result["resp_code"] == "00000000"

    def test_terminal_list(self):
        result = dg_sdk.Terminal.query_list(page_num="1")

        assert result["resp_code"] == "00000000"

    def test_terminal_sale_plan(self):
        result = dg_sdk.Terminal.query_sale_plan()

        assert result["resp_code"] == "00000000"
