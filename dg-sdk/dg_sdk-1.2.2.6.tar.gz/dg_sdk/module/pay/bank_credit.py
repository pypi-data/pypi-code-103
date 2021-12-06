from dg_sdk.module.request_tools import request_post
from dg_sdk.module.pay.pay_api_urls import bank_credit_payment, bank_credit_payment_apply, \
    bank_credit_payment_confirm, bank_credit_query, bank_credit_refund, bank_credit_sign

from dg_sdk.core.rsa_utils import rsa_long_encrypt
from dg_sdk.dg_client import DGClient
from dg_sdk.module.pay.credit_card_info import CreditCardInfo


class BankCredit(object):
    """
    银行卡分期支付相关接口
    银行卡分期支付签约，
    一段式分期支付
    二段式分期支付申请
    二段式分期支付确认
    银行卡分期退款
    银行卡分期查询
    """

    @classmethod
    def sign(cls, trans_amt, business_url, credit_card: CreditCardInfo, request_type, **kwargs):
        """
        银行卡分期支付签约
        :param trans_amt: 交易金额
        :param business_url: 页面跳转地址
        :param credit_card: 卡片信息
        :param request_type: 请求类型，0:pc 1:安卓 2：ios
        :param kwargs: 非必填额外参数
        :return: 返回报文
        """

        required_params = {
            "trans_amt": trans_amt,
            "bank_card_mobile_no": credit_card.bank_card_mobile_no,
            "bank_card_no": credit_card.bank_card_no,
            "card_name": credit_card.card_name,
            "certificate_no": credit_card.certificate_no,
            "certificate_type": credit_card.certificate_type,
            "bank_no": credit_card.bank_no,
            "card_act_type": credit_card.card_act_type,
            "card_type": credit_card.card_type,
            "cvv2": credit_card.cvv2,
            "valid_date": credit_card.valid_date,
            "request_type": request_type,
            "business_url": business_url
        }

        required_params.update(kwargs)

        return request_post(bank_credit_sign, required_params)

    @classmethod
    def payment_apply(cls, trans_amt, credit_card: CreditCardInfo, goods_desc, instalments_num, **kwargs):
        """
        二段式分期支付申请
        :param trans_amt: 交易金额
        :param credit_card: 卡片信息
        :param goods_desc: 商品描述
        :param instalments_num: 银行卡分期期数
        :param kwargs: 非必填额外参数
        """
        required_params = {
            "trans_amt": trans_amt,
            "goods_desc": goods_desc,
            "instalments_num": instalments_num,
            "mobile_no": credit_card.bank_card_mobile_no,
            "bank_card_no": credit_card.bank_card_no,
            "certificate_name": credit_card.card_name,
            "certificate_no": credit_card.certificate_no,
            "certificate_type": credit_card.certificate_type,
            "bank_no": credit_card.bank_no,
            "card_act_type": credit_card.card_act_type,
            "card_type": credit_card.card_type,
            "cvv2": credit_card.cvv2,
            "valid_date": credit_card.valid_date,
        }

        required_params.update(kwargs)

        return request_post(bank_credit_payment_apply, required_params)

    @classmethod
    def payment_confirm(cls, goods_desc, cvv2, org_req_date, org_req_seq_id, valid_date, verify_code, **kwargs):
        """
        二段式分期支付确认
        :param goods_desc: 商品描述
        :param cvv2: 信用卡cvv2
        :param org_req_date: 原请求时间
        :param org_req_seq_id: 原请求流水号
        :param valid_date: 信用卡有效期
        :param verify_code: 手机验证码
        :param kwargs: 非必填额外参数
        :return: 返回报文
        """

        required_params = {
            "goods_desc": goods_desc,
            "cvv2": rsa_long_encrypt(cvv2, DGClient.mer_config.public_key),
            "org_req_date": org_req_date,
            "org_req_seq_id": org_req_seq_id,
            "valid_date": rsa_long_encrypt(valid_date, DGClient.mer_config.public_key),
            "verify_code": verify_code
        }
        required_params.update(kwargs)
        return request_post(bank_credit_payment_confirm, required_params)

    @classmethod
    def payment(cls, trans_amt, credit_card: CreditCardInfo, instalments_num, **kwargs):
        """
        二段式分期支付确认
        :param credit_card: 卡片信息
        :param trans_amt: 交易金额
        :param instalments_num: 分期期数
        :param kwargs: 非必填额外参数
        :return: 返回报文
        """

        required_params = {
            "trans_amt": trans_amt,
            "instalments_num": instalments_num,
            "bank_card_mobile_no": credit_card.bank_card_mobile_no,
            "bank_card_no": credit_card.bank_card_no,
            "card_name": credit_card.card_name,
            "certificate_no": credit_card.certificate_no,
            "certificate_type": credit_card.certificate_type,
            "bank_no": credit_card.bank_no,
            "card_act_type": credit_card.card_act_type,
            "card_type": credit_card.card_type,
            "cvv2": credit_card.cvv2,
            "valid_date": credit_card.valid_date,
        }
        required_params.update(kwargs)
        return request_post(bank_credit_payment, required_params)

    @classmethod
    def query(cls, org_req_date, org_req_seq_id, org_hf_seq_id="", **kwargs):
        """
        分期支付查询
        :param org_req_seq_id: 原始请求流水号
        :param org_req_date: 原始订单请求时间
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
        return request_post(bank_credit_query, required_params, need_seq_id=False)

    @classmethod
    def refund(cls, ord_amt, org_req_date, org_req_seq_id, org_hf_seq_id="", **kwargs):
        """
        分期支付查询
        :param ord_amt: 金额
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
        return request_post(bank_credit_refund, required_params)
