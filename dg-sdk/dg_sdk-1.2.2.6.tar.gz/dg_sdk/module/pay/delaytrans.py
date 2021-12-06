from dg_sdk.module.request_tools import request_post
from dg_sdk.module.pay.pay_api_urls import payment_confirm, payment_confirm_query, \
    payment_confirm_refund, payment_confirm_list


class Delaytrans(object):
    """
    延时交易，交易确认，交易确认查询，交易退款
    """

    @classmethod
    def confirm(cls, org_req_date="", org_req_seq_id="", org_hf_seq_id="", **kwargs):
        """
        交易确认 (org_req_seq_id,org_req_date)、org_hf_seq_id 两者必填其一
        :param org_req_date: 原交易请求日期
        :param org_req_seq_id: 原交易请求流水号
        :param org_hf_seq_id: 原交易汇付全局流水号
        :param kwargs: 非必填额外参数
        :return: 交易确认返回报文
        """
        required_params = {
            "org_hf_seq_id": org_hf_seq_id,
            "org_req_date": org_req_date,
            "org_req_seq_id": org_req_seq_id
        }

        required_params.update(kwargs)
        return request_post(payment_confirm, required_params)

    @classmethod
    def confirm_query(cls, org_req_date, org_req_seq_id, **kwargs):
        """
        交易确认查询 (org_req_seq_id,org_req_date)、org_hf_seq_id 两者必填其一
        :param org_req_date: 原交易请求日期
        :param org_req_seq_id: 原交易请求流水号
        :param kwargs: 非必填额外参数
        :return: 交易确认返回报文
        """
        required_params = {
            "org_req_date": org_req_date,
            "org_req_seq_id": org_req_seq_id
        }

        required_params.update(kwargs)
        return request_post(payment_confirm_query, required_params)

    @classmethod
    def query_confirm_list(cls, org_req_date, org_req_seq_id, **kwargs):
        """
        交易确认列表查询 (org_req_seq_id,org_req_date)、org_hf_seq_id 两者必填其一
        :param org_req_date: 原交易请求日期
        :param org_req_seq_id: 原交易请求流水号
        :param kwargs: 非必填额外参数
        :return: 交易确认返回报文
        """
        required_params = {
            "trans_req_date": org_req_date,
            "trans_req_seq_id": org_req_seq_id
        }

        required_params.update(kwargs)
        return request_post(payment_confirm_list, required_params)

    @classmethod
    def confirm_refund(cls, org_req_date, org_req_seq_id, **kwargs):
        """
        交易确认退款
        :param org_req_date: 原交易请求日期
        :param org_req_seq_id: 原交易请求流水号
        :param kwargs: 非必填额外参数
        :return: 交易确认退款返回报文
        """
        required_params = {
            "org_req_date": org_req_date,
            "org_req_seq_id": org_req_seq_id
        }

        required_params.update(kwargs)
        return request_post(payment_confirm_refund, required_params)
