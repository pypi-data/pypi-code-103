from enum import Enum, unique


@unique
class URL(Enum):
    # 主站地址
    DOMAIN = "https://v1.api.juliangip.com"
    # DOMAIN = "http://192.168.10.52:8087"
    # 获取账户余额
    USERS_GETBALANCE = DOMAIN + "/users/getbalance"
    # 获取账户下对应类型的所有正常状态订单
    USERS_GETALLORDERS = DOMAIN + "/users/getAllOrders"
    # 动态代理 - - 提取动态代理
    DYNAMIC_GETIPS = DOMAIN + "/dynamic/getips"
    # 动态代理 - - 校验IP可用性
    DYNAMIC_CHECK = DOMAIN + "/dynamic/check"
    # 动态代理 - - 设置代理IP白名单
    DYNAMIC_SETWHITEIP = DOMAIN + "/dynamic/setwhiteip"
    # 动态代理 - - 替换IP白名单
    DYNAMIC_REPLACEWHITEIP = DOMAIN + "/dynamic/replaceWhiteIp"
    # 动态代理 - - 获取IP白名单
    DYNAMIC_GETWHITEIP = DOMAIN + "/dynamic/getwhiteip"
    # 动态代理 - - 获取代理剩余可用时长
    DYNAMIC_REMAIN = DOMAIN + "/dynamic/remain"
    # 动态代理 - - 获取剩余可用时长
    DYNAMIC_BALANCE = DOMAIN + "/dynamic/balance"
    # 独享代理 - - 获取代理详情
    ALONE_GETIPS = DOMAIN + "/alone/getips"
    # 独享代理 - - 设置代理IP白名单
    ALONE_SETWHITEIP = DOMAIN + "/alone/setwhiteip"
    # 独享代理 - - 获取代理IP白名单
    ALONE_GETWHITEIP = DOMAIN + "/alone/getwhiteip"
    # 独享代理 -- 替换IP白名单
    ALONE_REPLACEWHITEIP = DOMAIN + "/alone/replaceWhiteIp"
