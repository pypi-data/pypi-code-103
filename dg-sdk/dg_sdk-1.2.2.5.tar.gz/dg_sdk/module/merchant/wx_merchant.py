from dg_sdk.module.request_tools import request_post
from dg_sdk.module.merchant.wxmerchant_api_urls import *
from dg_sdk.dg_client import DGClient
from typing import List
import os


class WXMerchant(object):
    """
    微信商户配置类，包含以下接口
    微信商户配置
    微信商户配置查询
    微信实名认证
    微信实名认证状态查询
    证书登记
    微信特约商户进件申请
    查询微信申请状态
    修改微信结算帐号
    查询微信结算账户
    微信关注配置
    微信关注配置查询
    """

    @classmethod
    def config(cls, fee_type, **kwargs):
        """
        微信商户配置
        :param fee_type: 业务开通类型
        :param kwargs: 额外参数
        :return:
        """

        required_params = {
            "fee_type": fee_type,
            "product_id": DGClient.mer_config.product_id
        }
        required_params.update(kwargs)
        return request_post(config, required_params)

    @classmethod
    def query_config(cls, **kwargs):
        """
        微信商户配置查询
        :param kwargs: 额外参数
        :return:
        """

        required_params = {
            "product_id": DGClient.mer_config.product_id,
        }

        required_params.update(kwargs)
        return request_post(query_config, required_params)

    @classmethod
    def real_name(cls, name,   mobile,  id_card_number, **kwargs):
        """
        微信实名认证
        :param name: 联系人姓名
        :param mobile: 联系人手机号
        :param id_card_number: 联系人身份证号码
        :param kwargs: 额外参数
        :return:
        """

        required_params = {
            "name": name,
            "mobile": mobile,
            "id_card_number":id_card_number
        }
        required_params.update(kwargs)
        return request_post(apply_wx_real_name, required_params)

    @classmethod
    def query_real_name_stat(cls, **kwargs):
        """
        查询微信实名认证
        :return:
        """

        required_params = {
        }
        required_params.update(kwargs)
        return request_post(query_apply_wx_real_name, required_params)

    @classmethod
    def add_cert_info(cls,
                         name,
                         contact_name,
                         contact_mobile_no,
                         contact_cert_no,
                         login_name="",
                         login_mobile_no="",
                         bd_login_user_id="",
                         mer_huifu_id="",
                         **kwargs):
        """
        证书登记
        :param name: 总部名称
        :param contact_name: 联系人姓名
        :param contact_mobile_no: 联系人手机号
        :param contact_cert_no:  联系人身份证号码
        :param login_name: 管理员账号，有值，必须全网唯一；为空，不生成管理员账号
        :param login_mobile_no: 管理员手机号
        :param add_corp_info: 企业信息
        :param bd_login_user_id: 业务经理userId
        :param mer_huifu_id: 商户汇付Id
        :param kwargs:
        :return:
        """
        # TODO

        required_params = {
            "product_id": DGClient.mer_config.product_id,
            "name": name,
            "contact_name": contact_name,
            "contact_mobile_no": contact_mobile_no,
            "contact_cert_no": contact_cert_no,
            "login_name": login_name,
            "login_mobile_no": login_mobile_no,
            "bd_login_user_id": bd_login_user_id,
            "mer_huifu_id": mer_huifu_id,
        }

        required_params.update(kwargs)
        return request_post(add_cert_info, required_params)


    @classmethod
    def apply_register_mer(cls,
                            chains_id,
                            name="",
                            contact_name="",
                            contact_mobile_no="",
                            contact_cert_no="",
                            mer_huifu_id="",
                            **kwargs):
        """
        修改总部
        :param chains_id: 连锁编号
        :param name: 总部名称
        :param contact_name: 联系人姓名
        :param contact_mobile_no: 联系人手机号
        :param contact_cert_no:  联系人身份证号码
        :param edit_corp_info: 企业信息
        :param mer_huifu_id: 商户汇付Id
        :param kwargs:
        :return:
        """

        required_params = {
            "product_id": DGClient.mer_config.product_id,
            "name": name,
            "chains_id": chains_id,
            "contact_name": contact_name,
            "contact_mobile_no": contact_mobile_no,
            "contact_cert_no": contact_cert_no,
            "mer_huifu_id": mer_huifu_id,
        }

        required_params.update(kwargs)
        return request_post(apply_wx_special_mer_sign, required_params)
