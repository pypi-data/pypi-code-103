import unittest
import dg_sdk
from tests.conftest import *


class TestPayment(unittest.TestCase):

    def setUp(self):

        dg_sdk.DGClient.mer_config = dg_sdk.MerConfig(private_key, public_key, sys_id, product_id, huifu_id)

        print("setup")

    def tearDown(self):
        print("tearDown")

    def test_payment_create(self):
        result = dg_sdk.OnlinePayment.web_page(trans_amt="0.01", goods_desc="goods_desc",goods_short_name="商品",gw_chnnl_tp="01",biz_tp="100001",notify_url="https://notify_url")
        assert isinstance(result,str)

    def test_payment_query(self):
        result = dg_sdk.OnlinePayment.query(org_req_date="20211130",org_req_seq_id="16382554335827509", pay_type="")

        assert result["resp_code"] == "20000004"

    def test_payment_close(self):
        result = dg_sdk.ScanPayment.create(trade_type="A_NATIVE", trans_amt="1.00", goods_desc="test")

        result = dg_sdk.ScanPayment.close(org_req_date=result["req_date"], org_req_seq_id=result["req_seq_id"])

        assert result["resp_code"] == "10000015"

    def test_payment_close_query(self):
        result = dg_sdk.ScanPayment.create(trade_type="A_NATIVE", trans_amt="1.00", goods_desc="test")
        result = dg_sdk.ScanPayment.close(org_req_date=result["req_date"], org_req_seq_id=result["req_seq_id"])
        result = dg_sdk.ScanPayment.close_query(org_req_date=result["req_date"], org_req_seq_id=result["req_seq_id"])

        assert result["resp_code"] == "20000004"

    def test_payment_refund(self):
        result = dg_sdk.ScanPayment.create(trade_type="A_NATIVE", trans_amt="1.00", goods_desc="test")

        result = dg_sdk.ScanPayment.refund(ord_amt="0.01", org_req_date=result["req_date"],
                                           org_req_seq_id=result["req_seq_id"])

        assert result["resp_code"] == "10000001"

    def test_payment_refund_query(self):
        result = dg_sdk.ScanPayment.create(trade_type="A_NATIVE", trans_amt="1.00", goods_desc="test")

        result = dg_sdk.ScanPayment.refund(ord_amt="0.01", org_req_date=result["req_date"],
                                           org_req_seq_id=result["req_seq_id"])
        result = dg_sdk.ScanPayment.refund_query(org_req_date=result["req_date"],
                                                 org_req_seq_id=result["req_seq_id"])

        assert result["resp_code"] == "20000004"
