from dg_sdk.module.request_tools import request_post
from dg_sdk.module.pay.pay_api_urls import scan_payment_create, scan_payment_close, \
    scan_payment_query, scan_payment_refund, scan_payment_refund_query, offline_payment_scan, \
    scan_payment_close_query


class ScanPayment(object):
    """
    聚合正扫，聚合反扫，交易查询，交易退款，退款查询，关单
    """

    @classmethod
    def create(cls, trade_type, trans_amt, goods_desc, **kwargs):
        """
        创建聚合正扫订单
        :param trade_type: 微信公众号-T_JSAPI 小程序-T_MINIAPP 支付宝JS-A_JSAPI 支付宝正扫-A_NATIVE 银联正扫-U_NATIVE
        银联JS-U_JSAPI 数字货币二维码支付-D_NATIVE
        :param trans_amt: 交易金额，单位为元，（例如：100.00）
        :param goods_desc: 商品描述
        :param kwargs:  非必填额外参数
        :return: 支付对象
        """

        required_params = {
            "trade_type": trade_type,
            "trans_amt": trans_amt,
            "goods_desc": goods_desc,
        }

        required_params.update(kwargs)
        return request_post(scan_payment_create, required_params)

    @classmethod
    def micro_create(cls, trans_amt, goods_desc, auth_code, **kwargs):
        """
        聚合反扫
        :param trans_amt: 交易金额
        :param goods_desc: 商品描述
        :param auth_code: 支付授权码
        :param kwargs: 非必填额外参数
        :return: 支付结果
        """
        required_params = {
            "auth_code": auth_code,
            "trans_amt": trans_amt,
            "goods_desc": goods_desc,
        }

        required_params.update(kwargs)
        return request_post(offline_payment_scan, required_params)

    @classmethod
    def query(cls, org_req_date, *, org_req_seq_id="", org_hf_seq_id="", party_order_id="", out_trans_id="", **kwargs):
        """
        支付查询
        :param org_req_date: 原始订单请求时间
        :param party_order_id: 微信支付宝的商户单号
        :param org_hf_seq_id: 交易返回的全局流水号
        :param out_trans_id: 微信支付宝的订单号
        :param org_req_seq_id: 原始请求流水号
        :param kwargs: 非必填额外参数
        :return: 支付对象
        """

        required_params = {
            "org_req_date": org_req_date,
            "org_req_seq_id": org_req_seq_id,
            "org_hf_seq_id": org_hf_seq_id,
            "party_order_id": party_order_id,
            "out_trans_id": out_trans_id,
        }

        required_params.update(kwargs)
        return request_post(scan_payment_query, required_params, need_seq_id=False)

    @classmethod
    def refund(cls, ord_amt, org_req_date, *, org_req_seq_id="", org_hf_seq_id="", org_party_order_id="", **kwargs):
        """
        发起退款
        :param ord_amt: 退款金额
        :param org_req_seq_id: 原始请求流水号
        :param org_req_date: 原始订单请求时间
        :param org_party_order_id: 微信支付宝的商户单号
        :param org_hf_seq_id: 交易返回的全局流水号
        :param kwargs: 非必填额外参数
        :return: 返回报文
        """

        required_params = {
            "ord_amt": ord_amt,
            "org_req_date": org_req_date,
            "org_req_seq_id": org_req_seq_id,
            "org_hf_seq_id": org_hf_seq_id,
            "org_party_order_id": org_party_order_id,
        }

        required_params.update(kwargs)

        return request_post(scan_payment_refund, required_params)

    @classmethod
    def refund_query(cls, org_req_date, *, org_req_seq_id="", org_hf_seq_id="", **kwargs):
        """
        退款查询
        :param org_req_seq_id: 原始请求流水号
        :param org_req_date: 原始退款请求时间
        :param org_hf_seq_id: 交易返回的全局流水号
        :param kwargs: 非必填额外参数
        :return: 退款对象
        """
        required_params = {
            "org_req_date": org_req_date,
            "org_req_seq_id": org_req_seq_id,
            "org_hf_seq_id": org_hf_seq_id,
        }
        required_params.update(kwargs)
        return request_post(scan_payment_refund_query, required_params, need_seq_id=False)

    @classmethod
    def close(cls, org_req_date, *, org_req_seq_id="", org_hf_seq_id="", **kwargs):
        """
        关单请求
        :param org_req_seq_id: 原始订单请求流水号
        :param org_req_date: 原始订单请求日期
        :param org_hf_seq_id: 交易返回的全局流水号
        :param kwargs: 非必填额外参数
        :return: 关单对象
        """
        required_params = {
            "org_hf_seq_id": org_hf_seq_id,
            "org_req_date": org_req_date,
            "org_req_seq_id": org_req_seq_id
        }

        required_params.update(kwargs)
        return request_post(scan_payment_close, required_params)

    @classmethod
    def close_query(cls, org_req_date, *, org_req_seq_id="", org_hf_seq_id="", **kwargs):
        """
        关单查询请求
        :param org_req_seq_id: 原始订单请求流水号
        :param org_req_date: 原始订单请求日期
        :param org_hf_seq_id: 交易返回的全局流水号
        :param kwargs: 非必填额外参数
        :return: 关单对象
        """
        required_params = {
            "org_hf_seq_id": org_hf_seq_id,
            "org_req_date": org_req_date,
            "org_req_seq_id": org_req_seq_id
        }

        required_params.update(kwargs)
        return request_post(scan_payment_close_query, required_params)
