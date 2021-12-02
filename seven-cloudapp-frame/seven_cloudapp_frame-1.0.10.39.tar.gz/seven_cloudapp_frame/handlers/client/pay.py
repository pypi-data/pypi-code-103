# -*- coding: utf-8 -*-
"""
@Author: HuangJianYi
@Date: 2021-09-13 16:49:46
@LastEditTime: 2021-11-17 15:13:36
@LastEditors: HuangJianYi
@Description: 
"""
from seven_cloudapp_frame.libs.customize.seven_helper import SevenHelper
from seven_cloudapp_frame.libs.customize.wechat_helper import WeChatPayRequest, WeChatPayReponse, WeChatRefundReponse
from seven_cloudapp_frame.libs.customize.tiktok_helper import TikTokPayRequest, TikTokReponse
from seven_cloudapp_frame.handlers.frame_base import *
from seven_cloudapp_frame.models.db_models.pay.pay_order_model import *
from seven_cloudapp_frame.models.db_models.refund.refund_order_model import *


class WechatVoucherOrderHandler(ClientBaseHandler):
    """
    :description: 创建微信预订单
    """
    @filter_check_params("user_id,pay_order_no")
    def get_async(self):
        """
        :description: 创建微信预订单
        :param pay_order_no:支付单号
        :param user_id:用户标识
        :return: 请求接口获取客户端需要的支付密钥数据
        :last_editors: HuangJianYi
        """
        user_id = self.get_user_id()
        pay_order_no = self.get_param("pay_order_no")
        invoke_result_data = InvokeResultData()

        if SevenHelper.is_continue_request(f"WechatVoucherOrderHandler_{str(user_id)}") == True:
            return self.response_json_error("error", "对不起,请求太频繁")
        pay_order_model = PayOrderModel(context=self)
        pay_order = pay_order_model.get_entity("pay_order_no=%s", params=[pay_order_no])
        if not pay_order or pay_order.order_status != 0:
            return self.response_json_error("error", "抱歉!未查询到订单信息,请联系客服")
        pay_config = config.get_value("wechat_pay")
        pay_notify_url = pay_config["pay_notify_url"]

        # 商品说明
        body = pay_order.order_name
        # 金额
        total_fee = pay_order.pay_amount
        # ip
        ip = SevenHelper.get_first_ip(self.get_remote_ip())

        try:
            invoke_result_data = self.business_process_executing()
            if invoke_result_data.success == True:
                pay_notify_url = invoke_result_data.data["pay_notify_url"] if invoke_result_data.data.__contains__("pay_notify_url") else pay_notify_url
                time_expire = invoke_result_data.data["time_expire"] if invoke_result_data.data.__contains__("time_expire") else str(SevenHelper.get_now_int(1))  #交易结束时间,设置1小时
            invoke_result_data = WeChatPayRequest().create_order(pay_order_no, body, total_fee, ip, pay_notify_url, pay_order.open_id, time_expire)
            if invoke_result_data.success == False:
                return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)

            # self.logging_link_info('小程序支付返回前端参数:' + str(invoke_result_data.data))
            ref_params = {}
            invoke_result_data = self.business_process_executed(invoke_result_data, ref_params)
            return self.response_json_success(invoke_result_data.data)
        except Exception as ex:
            self.logging_link_error("【创建微信预订单异常】" + traceback.format_exc())
            return self.response_json_error("fail", "请重新支付")


class WechatPayNotifyHandler(FrameBaseHandler):
    """
    :description: 微信支付异步通知
    """
    @filter_check_params()
    def post_async(self):
        """
        :description:支付异步通知
        :return: 
        :last_editors: HuangJianYi
        """
        invoke_result_data = InvokeResultData()
        xml_params = self.request.body.decode('utf-8')
        wechat_pay_reponse = None
        try:
            wechat_pay_reponse = WeChatPayReponse(xml_params)  # 创建对象
            response_result = wechat_pay_reponse.get_data()
            return_code = response_result["return_code"]
            result_code = response_result["result_code"]
            if return_code == "FAIL":
                return self.write(wechat_pay_reponse.convert_response_xml(response_result["return_msg"], False))
            if result_code == "FAIL":
                return self.write(wechat_pay_reponse.convert_response_xml(response_result["err_code_des"], False))
            if wechat_pay_reponse.check_sign() != True:  # 校验签名,成功则继续后续操作
                return self.write(wechat_pay_reponse.convert_response_xml("签名验证失败", False))
            total_fee = response_result["total_fee"]
            pay_order_no = response_result["out_trade_no"]

            pay_order_model = PayOrderModel(context=self)
            pay_order = pay_order_model.get_entity("pay_order_no=%s", params=[pay_order_no])
            if not pay_order:
                return self.write(wechat_pay_reponse.convert_response_xml("未查询到订单信息", False))
            # 判断金额是否匹配
            if int(decimal.Decimal(str(pay_order.pay_amount)) * 100) != int(total_fee):
                self.logging_link_error(f"微信支付订单[{pay_order_no}] 金额不匹配疑似刷单.数据库金额:{str(pay_order.pay_amount)} 平台回调金额:{str(total_fee)}")
                return self.write(wechat_pay_reponse.convert_response_xml("金额异常", False))

            invoke_result_data = self.business_process_executing()
            if invoke_result_data.success == False:
                return self.write(wechat_pay_reponse.convert_response_xml(invoke_result_data.error_message, False))
            ref_params = {}
            ref_params["pay_order"] = pay_order
            ref_params["response_result"] = response_result
            self.business_process_executed(invoke_result_data, ref_params)

            return self.write(wechat_pay_reponse.convert_response_xml("SUCCESS", True))

        except Exception as ex:
            self.logging_link_error("【微信支付异步通知】" + traceback.format_exc() + ":" + str(xml_params))
            return self.write(wechat_pay_reponse.convert_response_xml("数据异常", False))


    def business_process_executed(self, result_data, ref_params):
        """
        :description: 执行后事件
        :param result_data: result_data
        :param ref_params: 关联参数
        :return:
        :last_editors: HuangJianYi
        """
        response_result = ref_params["response_result"]
        pay_order = ref_params["pay_order"]
        pay_order_model = PayOrderModel(context=self)
        transaction_id = response_result["transaction_id"]
        time_string = response_result["time_end"]
        if pay_order.order_status == 0 or pay_order.order_status == 2:
            pay_order.out_order_no = transaction_id
            pay_order.order_status = 1
            pay_order.pay_date = time.strftime("%Y-%m-%d %H:%M:%S", time.strptime(time_string, "%Y%m%d%H%M%S"))
            pay_order_model.update_entity(pay_order, "out_order_no,order_status,pay_date")

        return result_data


class WechatRefundNotifyHandler(FrameBaseHandler):
    """
    :description: 微信退款异步通知
    """
    @filter_check_params()
    def post_async(self):
        invoke_result_data = InvokeResultData()
        xml_params = self.request.body.decode('utf-8')
        wechat_refund_reponse = None
        try:
            wechat_refund_reponse = WeChatRefundReponse(xml_params)  # 创建对象
            response_result = wechat_refund_reponse.get_data()
            return_code = response_result["return_code"]
            if return_code == "FAIL":
                return self.write(wechat_refund_reponse.convert_response_xml(response_result["return_msg"], False))
            invoke_result_data = self.business_process_executing()
            if invoke_result_data.success == False:
                return self.write(wechat_refund_reponse.convert_response_xml(invoke_result_data.error_message, False))
            # 解密
            req_info_dict = wechat_refund_reponse.decode_req_info(response_result["req_info"])
            req_info_dict = req_info_dict["root"]
            ref_params = {}
            ref_params["req_info_dict"] = req_info_dict
            self.business_process_executed(invoke_result_data, ref_params)
            return self.write(wechat_refund_reponse.convert_response_xml("SUCCESS", True))
        except Exception as ex:
            self.logging_link_error("【微信退款异步通知】" + traceback.format_exc() + ":" + str(xml_params))
            return self.write(wechat_refund_reponse.convert_response_xml("数据异常", False))


    def business_process_executed(self, result_data, ref_params):
        """
        :description: 执行后事件
        :param result_data: result_data
        :param ref_params: 关联参数
        :return:
        :last_editors: HuangJianYi
        """
        req_info_dict = ref_params["req_info_dict"]
        db_transaction = DbTransaction(db_config_dict=config.get_value("db_cloudapp"))
        pay_order_model = PayOrderModel(db_transaction=db_transaction, context=self)
        refund_order_model = RefundOrderModel(db_transaction=db_transaction, context=self)
        try:
            db_transaction.begin_transaction()
            if req_info_dict["refund_status"] == "SUCCESS":
                self.logging_link_info(f'pay_order_no:{str(req_info_dict["out_trade_no"])},微信退款异步通知:' + str(req_info_dict))
                # 退款成功(相关表处理)
                refund_order_model.update_table("refund_status=3,out_refund_no=%s,refund_date=%s", where="refund_no=%s", params=[req_info_dict["refund_id"], req_info_dict["success_time"], req_info_dict["out_refund_no"]])
                pay_order_model.update_table("order_status=20,refund_amount=%s", where="pay_order_no=%s", params=[int(req_info_dict["settlement_refund_fee"]) / 100, req_info_dict["out_trade_no"]])
                db_transaction.commit_transaction()
            else:
                # 退款失败(只更新退款表)
                refund_order_model.update_table("refund_status=4", where="out_refund_no=%s", params=req_info_dict["refund_id"])
        except Exception as ex:
            db_transaction.rollback_transaction()
            self.logging_link_error("【微信退款异步通知数据处理异常】" + traceback.format_exc())

        return result_data


class TiktokVoucherOrderHandler(ClientBaseHandler):
    """
    :description: 创建抖音预订单
    """
    @filter_check_params("user_id,pay_order_no")
    def get_async(self):
        """
        :description: 创建抖音预订单
        :param pay_order_no:支付单号
        :param user_id:用户标识
        :return: 请求接口获取客户端需要的支付密钥数据
        :last_editors: HuangJianYi
        """
        user_id = self.get_user_id()
        pay_order_no = self.get_param("pay_order_no")
        invoke_result_data = InvokeResultData()

        if SevenHelper.is_continue_request(f"TiktokVoucherOrderHandler_{str(user_id)}") == True:
            return self.response_json_error("error", "对不起,请求太频繁")
        pay_order_model = PayOrderModel(context=self)
        pay_order = pay_order_model.get_entity("pay_order_no=%s", params=[pay_order_no])
        if not pay_order or pay_order.order_status != 0:
            return self.response_json_error("error", "抱歉!未查询到订单信息,请联系客服")
        pay_config = config.get_value("tiktok_pay")
        pay_notify_url = pay_config["pay_notify_url"]
        # 商品描述
        subject = pay_order.order_name
        # 商品详情
        body = pay_order.order_desc
        # 金额
        total_amount = pay_order.pay_amount

        try:
            invoke_result_data = self.business_process_executing()
            if invoke_result_data.success == True:
                pay_notify_url = invoke_result_data.data["pay_notify_url"] if invoke_result_data.data.__contains__("pay_notify_url") else pay_notify_url
                time_expire = invoke_result_data.data["time_expire"] if invoke_result_data.data.__contains__("time_expire") else 3600  #交易结束时间,设置1小时,单位秒
            invoke_result_data = TikTokPayRequest().create_order(pay_order_no=pay_order_no, notify_url=pay_notify_url, total_amount=total_amount, subject=subject, body=body, valid_time=time_expire)
            if invoke_result_data.success == False:
                return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
            # self.logging_link_info('小程序支付返回前端参数:' + str(invoke_result_data.data))
            pay_order_model.update_table("out_order_no=%s", "pay_order_no=%s", params=[invoke_result_data.data["order_id"], pay_order_no])
            ref_params = {}
            invoke_result_data = self.business_process_executed(invoke_result_data, ref_params)
            return self.response_json_success(invoke_result_data.data)
        except Exception as ex:
            self.logging_link_error("【创建抖音预订单异常】" + traceback.format_exc())
            return self.response_json_error("fail", "请重新支付")


class TiktokPayNotifyHandler(FrameBaseHandler):
    """
    :description: 抖音支付异步通知
    """
    @filter_check_params()
    def post_async(self):
        """
        :description:抖音支付异步通知
        :return: 
        :last_editors: HuangJianYi
        """
        invoke_result_data = InvokeResultData()
        json_params = self.request.body.decode('utf-8')
        tiktok_reponse = None
        try:
            tiktok_reponse = TikTokReponse(json_params)
            response_result = tiktok_reponse.get_data()
            if tiktok_reponse.check_sign() != True:  # 校验签名,成功则继续后续操作
                return self.write(tiktok_reponse.convert_response_json(-1, "签名验证失败"))
            if response_result["type"] != "payment":
                return self.write(tiktok_reponse.convert_response_json(-1, "回调类型标记错误"))
            response_data = SevenHelper.json_loads(response_result["msg"])
            total_fee = response_data["total_amount"] if response_data.__contains__("total_amount") else 0
            pay_order_no = response_data["cp_orderno"]
            pay_order_model = PayOrderModel(context=self)
            pay_order = pay_order_model.get_entity("pay_order_no=%s", params=[pay_order_no])
            if not pay_order:
                return self.write(tiktok_reponse.convert_response_json(-1, "未查询到支付订单信息"))
            # 判断金额是否匹配
            if int(decimal.Decimal(str(pay_order.pay_amount)) * 100) != int(total_fee):
                self.logging_link_error(f"抖音支付订单[{pay_order_no}] 金额不匹配疑似刷单.数据库金额:{str(pay_order.pay_amount)} 平台回调金额:{str(total_fee)}")
                return self.write(tiktok_reponse.convert_response_json(-1, "金额异常"))

            invoke_result_data = self.business_process_executing()
            if invoke_result_data.success == False:
                return self.write(tiktok_reponse.convert_response_json(-1, invoke_result_data.error_message))

            ref_params = {}
            ref_params["pay_order"] = pay_order
            ref_params["response_data"] = response_data
            self.business_process_executed(invoke_result_data, ref_params)

            return self.write(tiktok_reponse.convert_response_json())

        except Exception as ex:
            self.logging_link_error("【抖音支付异步通知】" + traceback.format_exc() + ":" + str(json_params))
            return self.write(tiktok_reponse.convert_response_json(-1, "数据异常"))


    def business_process_executed(self, result_data, ref_params):
        """
        :description: 执行后事件
        :param result_data: result_data
        :param ref_params: 关联参数
        :return:
        :last_editors: HuangJianYi
        """
        pay_order = ref_params["pay_order"]
        pay_order_model = PayOrderModel(context=self)
        if pay_order.order_status == 0 or pay_order.order_status == 2:
            pay_time = SevenHelper.get_now_datetime()
            order_id = ""
            tiktok_pay_request = TikTokPayRequest()
            query_invoke_result_data = tiktok_pay_request.query_order(pay_order.pay_order_no)
            if query_invoke_result_data.success == True:
                pay_time = query_invoke_result_data.data["payment_info"]["pay_time"]
                order_id = query_invoke_result_data.data["order_id"]
            pay_order.order_status = 1
            pay_order.pay_date = pay_time
            pay_order.out_order_no = order_id if order_id else pay_order.out_order_no
            pay_order_model.update_entity(pay_order, "out_order_no,order_status,pay_date")

        return result_data


class TiktokRefundNotifyHandler(FrameBaseHandler):
    """
    :description: 抖音退款异步通知
    """
    @filter_check_params()
    def post_async(self):
        invoke_result_data = InvokeResultData()
        json_params = self.request.body.decode('utf-8')
        tiktok_reponse = None
        try:
            tiktok_reponse = TikTokReponse(json_params)
            response_result = tiktok_reponse.get_data()
            if tiktok_reponse.check_sign() != True:  # 校验签名,成功则继续后续操作
                return self.write(tiktok_reponse.convert_response_json(-1, "签名验证失败"))
            if response_result["type"] != "refund":
                return self.write(tiktok_reponse.convert_response_json(-1, "回调类型标记错误"))
            response_data = SevenHelper.json_loads(response_result["msg"])
            cp_refundno = response_data["cp_refundno"]
            refund_order_model = RefundOrderModel(context=self)
            refund_order = refund_order_model.get_entity("refund_no=%s", params=[cp_refundno])
            if not refund_order:
                return self.write(tiktok_reponse.convert_response_json(-1, "未查询到退款订单信息"))
            invoke_result_data = self.business_process_executing()
            if invoke_result_data.success == False:
                return self.write(tiktok_reponse.convert_response_json(-1, invoke_result_data.error_message))
            ref_params = {}
            ref_params["refund_order"] = refund_order
            ref_params["response_data"] = response_data
            self.business_process_executed(invoke_result_data, ref_params)

            return self.write(tiktok_reponse.convert_response_json())

        except Exception as ex:
            self.logging_link_error("【抖音退款异步通知】" + traceback.format_exc() + ":" + str(json_params))
            return self.write(tiktok_reponse.convert_response_json(-1, "数据异常"))


    def business_process_executed(self, result_data, ref_params):
        """
        :description: 执行后事件
        :param result_data: result_data
        :param ref_params: 关联参数
        :return:
        :last_editors: HuangJianYi
        """
        refund_order = ref_params["refund_order"]
        response_data = ref_params["response_data"]
        db_transaction = DbTransaction(db_config_dict=config.get_value("db_cloudapp"))
        pay_order_model = PayOrderModel(db_transaction=db_transaction, context=self)
        refund_order_model = RefundOrderModel(db_transaction=db_transaction, context=self)
        try:
            db_transaction.begin_transaction()
            if response_data["status"] == "SUCCESS":
                self.logging_link_info(f'refund_no:{str(response_data["cp_refundno"])},抖音退款异步通知:' + str(response_data))
                # 退款成功(相关表处理)
                refund_order_model.update_table("refund_status=3,refund_date=%s", where="refund_no=%s", params=[SevenHelper.get_now_datetime(), response_data["cp_refundno"]])
                pay_order_model.update_table("order_status=20,refund_amount=%s", where="pay_order_no=%s", params=[int(response_data["refund_amount"]) / 100, refund_order.pay_order_no])
                db_transaction.commit_transaction()
            else:
                # 退款失败(只更新退款表)
                refund_order_model.update_table("refund_status=4", where="refund_no=%s", params=[response_data["cp_refundno"]])
        except Exception as ex:
            db_transaction.rollback_transaction()
            self.logging_link_error("【抖音退款异步通知数据处理异常】" + traceback.format_exc())
        return result_data