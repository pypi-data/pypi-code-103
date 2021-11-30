from dg_sdk.module.request_tools import request_post
from dg_sdk.module.pay.pay_api_urls import online_payment_query, online_payment_refund, \
    online_payment_refund_query, union_app_pay, wap_pay,web_page
from dg_sdk.dg_client import DGClient
import json


class OnlinePayment(object):
    """
    线上交易相关接口，银联APP支付，网银支付，手机网页支付，线上交易退款，线上交易退款查询，线上交易交易查询
    """

    @classmethod
    def web_page(cls, trans_amt, goods_desc, goods_short_name, gw_chnnl_tp, biz_tp, notify_url,**kwargs):
        """
        网银支付
        :param trans_amt: 订单金额
        :param goods_desc: 商品描述
        :param extend_pay_data: 银行扩展数据
        :param kwargs:
        :return:
        """

        required_params = {
            "trans_amt": trans_amt,
            "goods_desc": goods_desc,
            "extend_pay_data": json.dumps({
                "goods_short_name": goods_short_name,
                "gw_chnnl_tp": gw_chnnl_tp,
                "biz_tp": biz_tp
            }),
            "risk_check_data":json.dumps({"ip_addr":"127.0.0.1"}),
            "terminal_device_data":json.dumps({"device_type":"4","device_ip":"127.0.0.1"}),
            "product_id": DGClient.mer_config.product_id,
            "notify_url":notify_url
        }

        required_params.update(kwargs)
        return request_post(web_page, required_params)

    @classmethod
    def union_app_create(cls, trans_amt, **kwargs):
        """
        银联APP支付
        :param trans_amt: 交易金额，单位为元，（例如：100.00）
        :param kwargs:  非必填额外参数
        :return: 支付对象
        """

        required_params = {
            "trans_amt": trans_amt,
        }

        required_params.update(kwargs)
        return request_post(union_app_pay, required_params)

    @classmethod
    def wap_page(cls, bank_card_no, front_url, trans_amt, **kwargs):
        """
        手机网页支付
        :param bank_card_no:
        :param front_url:
        :param trans_amt:
        :param kwargs:
        :return:
        """

        required_params = {
            "trans_amt": trans_amt,
            "bank_card_no": bank_card_no,
            "front_url": front_url,
        }

        required_params.update(kwargs)
        return request_post(wap_pay, required_params)

    @classmethod
    def query(cls, org_req_date, *, org_req_seq_id="", org_hf_seq_id="", pay_type="", **kwargs):
        """
        线上交易查询接口
        :param org_req_seq_id: 原始请求流水号
        :param org_req_date: 原始订单请求时间
        :param pay_type: 原交易支付类型, 快捷支付传quick_pay
        :param org_hf_seq_id: 交易返回的全局流水号
        :param kwargs: 非必填额外参数
        :return: 返回报文
        """
        required_params = {
            "org_req_date": org_req_date,
            "org_req_seq_id": org_req_seq_id,
            "org_hf_seq_id": org_hf_seq_id,
            "pay_type": pay_type
        }

        required_params.update(kwargs)

        return request_post(online_payment_query, required_params)

    @classmethod
    def refund(cls, ord_amt, org_req_date, *, org_req_seq_id="", org_hf_seq_id="", **kwargs):
        """
        线上退款接口
        :param ord_amt: 退款金额
        :param org_req_seq_id: 原始请求流水号
        :param org_req_date: 原始订单请求时间
        :param org_hf_seq_id: 交易返回的全局流水号
        :param kwargs: 非必填额外参数
        :return: 返回报文
        """

        required_params = {
            "ord_amt": ord_amt,
            "org_req_date": org_req_date,
            "org_req_seq_id": org_req_seq_id,
            "org_hf_seq_id": org_hf_seq_id,
        }

        required_params.update(kwargs)

        return request_post(online_payment_refund, required_params)

    @classmethod
    def refund_query(cls, org_req_date, *, org_req_seq_id="", org_hf_seq_id="", **kwargs):
        """
        线上退款查询接口
        :param org_req_seq_id: 原始请求流水号
        :param org_req_date: 原始退款请求时间
        :param org_hf_seq_id: 交易返回的全局流水号
        :param kwargs: 非必填额外参数
        :return: 返回报文
        """
        required_params = {
            "org_req_date": org_req_date,
            "org_req_seq_id": org_req_seq_id,
            "org_hf_seq_id": org_hf_seq_id,
        }
        required_params.update(kwargs)
        return request_post(online_payment_refund_query, required_params)
