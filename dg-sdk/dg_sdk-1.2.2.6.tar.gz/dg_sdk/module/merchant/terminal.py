from dg_sdk.module.request_tools import request_post
from dg_sdk.module.merchant.terminal_api_urls import *
from dg_sdk.dg_client import DGClient


class Terminal(object):
    """
    终端自助申请对象，包含以下接口
    终端自助申请单创建
    终端申请列表查询
    终端申请订单详情
    终端申请订单取消
    查询商户/渠道商销售策略
    """

    @classmethod
    def create(cls, order_status, **kwargs):
        """
        终端自助申请单创建
        :param order_status: 订单状态
        :param kwargs: 额外参数
        :return:
        """

        required_params = {
            "order_status": order_status,
        }
        required_params.update(kwargs)
        return request_post(create, required_params)

    @classmethod
    def query_list(cls, page_num, page_size="10", **kwargs):
        """
        终端申请列表查询
        :param page_size: 每页条数
        :param page_num: 当前页码
        :param kwargs: 额外参数
        :return:
        """
        required_params = {
            "product_id": DGClient.mer_config.product_id,
            "page_size": page_size,
            "page_num": page_num
        }
        required_params.update(kwargs)
        return request_post(query_list, required_params)

    @classmethod
    def query_detail(cls, order_id, **kwargs):
        """
        终端申请订单详情
        :param order_id: 订单号
        :param kwargs: 额外参数
        :return:
        """

        required_params = {
            "order_id": order_id,
            "product_id": DGClient.mer_config.product_id
        }
        required_params.update(kwargs)
        return request_post(query_detail, required_params)

    @classmethod
    def cancle(cls, order_id, **kwargs):
        """
        终端申请订单取消
        :param order_id: 订单号
        :param kwargs: 额外参数
        :return:
        """

        required_params = {
            "order_id": order_id,
            "product_id": DGClient.mer_config.product_id
        }
        required_params.update(kwargs)
        return request_post(cancel_apply, required_params)

    @classmethod
    def query_sale_plan(cls, **kwargs):
        """
        查询商户/渠道商销售策略
        :param kwargs:
        :return:
        """

        required_params = {
            "product_id": DGClient.mer_config.product_id
        }

        required_params.update(kwargs)
        return request_post(query_sale_plan, required_params)
