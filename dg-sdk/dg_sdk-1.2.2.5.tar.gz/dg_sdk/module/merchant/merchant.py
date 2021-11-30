from dg_sdk.module.request_tools import request_post
from dg_sdk.module.merchant.merchant_api_urls import *
from dg_sdk.dg_client import DGClient
from dg_sdk.module.merchant.merchant_info import MerchantInfo
from dg_sdk.module.merchant.legal_info import LegalInfo
from dg_sdk.module.merchant.bussiness_lic_info import BussinessLicInfo
from dg_sdk.module.merchant.settle_config_info import SettleConfigInfo
from dg_sdk.module.merchant.cash_config_info import CashConfigInfo
from dg_sdk.module.merchant.mer_card_info import MerCardInfo
from dg_sdk.module.merchant.corp_info import CorpInfo
from typing import List
import os


class Merchant(object):
    """
    商户进件相关类，包含以下接口
    企业类型商户进件
    个体户类型商户进件
    基本信息修改
    详细信息查询
    新增总部
    修改总部
    总部商户绑定&解除
    查询账户信息
    商户业务开通
    商户业务开通修改
    申请单状态查询
    商户图片资料上传
    商户分账配置
    商户分账配置查询
    商户分期配置
    商户分期配置详情查询
    活动报名，支持微信
    """

    @classmethod
    def create_enterprise(cls, upper_huifu_id,
                          merchant_info: MerchantInfo,
                          card_info: MerCardInfo,
                          lic_info: BussinessLicInfo,
                          legal_info: LegalInfo,
                          settle_info: SettleConfigInfo = None,
                          cash_config: List[CashConfigInfo] = None,
                          settle_agree_pic="",
                          **kwargs):
        """
        企业类型商户进件
        :param upper_huifu_id: 渠道商汇付Id
        :param merchant_info: 商户经营信息
        :param lic_info: 营业执照信息
        :param legal_info: 法人信息
        :param card_info: 卡信息
        :param settle_info: 结算配置
        :param cash_config:取现配置列表
        :param settle_agree_pic: D1结算协议图片文件路径
        :param kwargs: 额外参数
        :return:
        """

        required_params = {
            "upper_huifu_id": upper_huifu_id,
            "product_id": DGClient.mer_config.product_id
        }
        if merchant_info:
            required_params.update(merchant_info.obj_to_dict())
        if lic_info:
            required_params.update(lic_info.obj_to_dict())
        if legal_info:
            required_params.update(legal_info.obj_to_dict())
        if card_info:
            required_params["card_info"] = card_info.obj_to_dict()
        if settle_info:
            required_params["settle_config"] = settle_info.obj_to_dict()
        if cash_config:
            configs = []
            for config in cash_config:
                configs.append(config.obj_to_dict())
            required_params["cash_config"] = configs

        file = None
        if not settle_agree_pic:
            settle_agree_pic = kwargs.get('settle_agree_pic')
            if settle_agree_pic:
                kwargs.pop('settle_agree_pic')

        if settle_agree_pic:
            file = {'settle_agree_pic': (
                os.path.basename(settle_agree_pic), open(settle_agree_pic, 'rb'), 'application/octet-stream')}

        required_params.update(kwargs)
        return request_post(ent_mer_reg, required_params, file)

    @classmethod
    def create_individual(cls, upper_huifu_id,
                          merchant_info: MerchantInfo,
                          card_info: MerCardInfo,
                          settle_info: SettleConfigInfo = None,
                          cash_config: List[CashConfigInfo] = None,
                          settle_agree_pic="",
                          short_name="",
                          **kwargs):
        """
        个人类型商户进件
        :param upper_huifu_id: 渠道商汇付Id
        :param merchant_info: 商户经营信息
        :param card_info: 卡信息
        :param settle_info: 结算配置
        :param cash_config:取现配置列表
        :param settle_agree_pic: D1结算协议图片文件路径
        :param short_name: 商户简称
        :param kwargs: 额外参数
        :return:
        """

        required_params = {
            "upper_huifu_id": upper_huifu_id,
            "product_id": DGClient.mer_config.product_id,
            "short_name": short_name,
        }
        if merchant_info:
            required_params.update(merchant_info.obj_to_dict())
        if card_info:
            required_params["card_info"] = card_info.obj_to_dict()
        if settle_info:
            required_params["settle_config"] = settle_info.obj_to_dict()
        if cash_config:
            configs = []
            for config in cash_config:
                configs.append(config.obj_to_dict())
            required_params["cash_config"] = configs

        file = None
        if not settle_agree_pic:
            settle_agree_pic = kwargs.get('settle_agree_pic')
            if settle_agree_pic:
                kwargs.pop('settle_agree_pic')

        if settle_agree_pic:
            file = {'settle_agree_pic': (
                os.path.basename(settle_agree_pic), open(settle_agree_pic, 'rb'), 'application/octet-stream')}

        required_params.update(kwargs)
        return request_post(indv_mer_reg, required_params, file)

    @classmethod
    def modify(cls, upper_huifu_id,
               merchant_info: MerchantInfo = None,
               lic_info: BussinessLicInfo = None,
               legal_info: LegalInfo = None,
               card_info: MerCardInfo = None,
               settle_info: SettleConfigInfo = None,
               cash_config: List[CashConfigInfo] = None,
               settle_agree_pic="",
               **kwargs):
        """
        修改商户基本信息
        :param upper_huifu_id: 渠道商汇付Id
        :param merchant_info: 商户经营信息
        :param lic_info: 营业执照信息
        :param legal_info: 法人信息
        :param card_info: 卡信息
        :param settle_info: 结算配置
        :param cash_config:取现配置列表
        :param settle_agree_pic: D1结算协议图片文件路径
        :param kwargs: 额外参数
        :return:
        """

        required_params = {
            "upper_huifu_id": upper_huifu_id,
            "product_id": DGClient.mer_config.product_id
        }
        if merchant_info:
            required_params.update(merchant_info.obj_to_dict())
        if lic_info:
            required_params.update(lic_info.obj_to_dict())
        if legal_info:
            required_params.update(legal_info.obj_to_dict())
        if card_info:
            required_params["card_info"] = card_info.obj_to_dict()
        if settle_info:
            required_params["settle_config"] = settle_info.obj_to_dict()
        if cash_config:
            configs = []
            for config in cash_config:
                configs.append(config.obj_to_dict())
            required_params["cash_config"] = configs

        file = None
        if not settle_agree_pic:
            settle_agree_pic = kwargs.get('settle_agree_pic')
            if settle_agree_pic:
                kwargs.pop('settle_agree_pic')

        if settle_agree_pic:
            file = {'settle_agree_pic': (
                os.path.basename(settle_agree_pic), open(settle_agree_pic, 'rb'), 'application/octet-stream')}

        required_params.update(kwargs)
        return request_post(mer_modify, required_params, files=file)

    @classmethod
    def query_merch_info(cls, **kwargs):
        """
        查询商户详细信息
        :return:
        """

        required_params = {
            "product_id": DGClient.mer_config.product_id
        }
        required_params.update(kwargs)
        return request_post(query_merch_info, required_params)

    @classmethod
    def add_headquarters(cls,
                         name,
                         contact_name,
                         contact_mobile_no,
                         contact_cert_no,
                         login_name="",
                         login_mobile_no="",
                         add_corp_info: CorpInfo = None,
                         bd_login_user_id="",
                         mer_huifu_id="",
                         **kwargs):
        """
        新增总部
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
        if add_corp_info:
            required_params["add_corp_info"] = add_corp_info.obj_to_dict()

        required_params.update(kwargs)
        return request_post(add_chains_corp_info, required_params)

    @classmethod
    def modify_headquarters(cls,
                            chains_id,
                            name="",
                            contact_name="",
                            contact_mobile_no="",
                            contact_cert_no="",
                            edit_corp_info: CorpInfo = None,
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
        if edit_corp_info:
            required_params["edit_corp_info"] = edit_corp_info.obj_to_dict()

        required_params.update(kwargs)
        return request_post(modify_chains_corp_info, required_params)

    @classmethod
    def bind_headquarters(cls, chains_id, state, mer_type, **kwargs):
        """
        总部商户绑定&解除
        :param chains_id: 连锁编号,每个总部下最多添加50个商户
        :param state: 状态，1绑定，0 解除
        :param mer_type: 商户类型，0 自营，1 加盟
        :return:
        """

        required_params = {
            "product_id": DGClient.mer_config.product_id,
            "chains_id": chains_id,
            "state": state,
            "mer_type": mer_type,
        }
        required_params.update(kwargs)
        return request_post(bind_chains_mer, required_params)

    @classmethod
    def query_acct_info(cls, **kwargs):
        """
        查询账户余额
        :param kwargs:
        :return:
        """
        required_params = {
            "product_id": DGClient.mer_config.product_id
        }
        required_params.update(kwargs)
        return request_post(query_acct_info_list, required_params)

    @classmethod
    def reg_busi_info(cls, upper_huifu_id, out_fee_flag, **kwargs):
        """
        商户业务开通
        :param upper_huifu_id: 渠道商汇付Id
        :param out_fee_flag: 是否交易手续费外扣1:外扣 2:内扣（默认2内扣）
        :param kwargs:
        :return:
        """

        required_params = {
            "upper_huifu_id": upper_huifu_id,
            "out_fee_flag": out_fee_flag
        }
        required_params.update(kwargs)
        return request_post(reg_mer_busi_info, required_params)

    @classmethod
    def modify_busi_info(cls, **kwargs):
        """
        商户业务开通修改
        :param kwargs:
        :return:
        """

        required_params = {
        }
        required_params.update(kwargs)
        return request_post(modify_mer_busi_info, required_params)

    @classmethod
    def query_apply_status(cls, apply_no, **kwargs):
        """
        申请单状态查询
        :param apply_no: 申请单号
        :param kwargs:
        :return:
        """

        required_params = {
            "apply_no": apply_no,
        }
        required_params.update(kwargs)
        return request_post(query_apply_status, required_params)

    @classmethod
    def upload(cls, file_type, picture_path, **kwargs):
        """
        商户图片上传
        :param file_type: 申请单号
        :param picture_path: 图片路径
        :param kwargs:
        :return:
        """

        file = {'picture': (
            os.path.basename(picture_path), open(picture_path, 'rb'), 'application/octet-stream')}

        required_params = {
            "file_type": file_type
        }
        required_params.update(kwargs)
        return request_post(mer_file_upload, required_params, file)

    @classmethod
    def add_split_config(cls, rule_origin, repeal_flag, refund_flag, div_flag, apply_ratio, start_type, **kwargs):
        """
        商户分账配置
        :param rule_origin:  分账规则来源01 接口发起 02 控台配置
        :param repeal_flag: 分账是否支持撤销交易,	（Y：支持，N：不支持）
        :param refund_flag: 分账是否支持退货交易（Y：支持，N：不支持
        :param div_flag: 分账开关, （Y：开，N：关）
        :param apply_ratio: 最大分账比例 0-100 的数值;
        :param start_type:  生效类型 0-审核通过即时生效
        :param kwargs:
        :return:
        """

        required_params = {
            "product_id": DGClient.mer_config.product_id,
            "rule_origin": rule_origin,
            "repeal_flag": repeal_flag,
            "refund_flag": refund_flag,
            "div_flag": div_flag,
            "apply_ratio": apply_ratio,
            "start_type": start_type
        }
        required_params.update(kwargs)
        return request_post(add_mer_split_config, required_params)

    @classmethod
    def query_split_config(cls, **kwargs):
        """
        查询商户分账配置信息
        :return:
        """

        required_params = {
            "product_id": DGClient.mer_config.product_id
        }
        required_params.update(kwargs)
        return request_post(query_mer_split_config, required_params)

    @classmethod
    def fenqi_config(cls, **kwargs):
        """
        商户分期配置
        :return:
        """

        required_params = {
            "product_id": DGClient.mer_config.product_id
        }
        required_params.update(kwargs)
        return request_post(config_fq_mer_free, required_params)

    @classmethod
    def query_fenqi_config(cls, **kwargs):
        """
        商户分期配置详情查询
        :return:
        """

        required_params = {
            "product_id": DGClient.mer_config.product_id
        }
        required_params.update(kwargs)
        return request_post(query_fq_mer_free_detail, required_params)

    @classmethod
    def reg_activities(cls, pay_way, fee_type, syt_photo, mm_photo, bl_photo, dh_photo, **kwargs):
        """
        活动报名，支持微信
        :param pay_way:  支付通道
        :param fee_type: 手续费类型
        :param syt_photo: 收银台照片
        :param mm_photo: 整体门面图片（门头照
        :param bl_photo: 营业执照图片
        :param dh_photo: 店内环境图片
        :param kwargs:
        :return:
        """

        required_params = {
            "product_id": DGClient.mer_config.product_id,
            "pay_way": pay_way,
            "fee_type": fee_type,
            "syt_photo": syt_photo,
            "mm_photo": mm_photo,
            "bl_photo": bl_photo,
            "dh_photo": dh_photo
        }
        required_params.update(kwargs)
        return request_post(reg_activities, required_params)

    @classmethod
    def download_bill(cls, check_order_type, file_date, **kwargs):

        required_params = {
            "check_order_type": check_order_type,
            "file_date": file_date
        }
        required_params.update(kwargs)
        return request_post(mer_file_download, required_params)
