from .common.DynamicGetIps import DynamicGetIps
from .common.DynamicCheck import DynamicCheck
from .common.DynamicSetWhiteIp import DynamicSetWhiteIp
from .common.DynamicGetWhiteIp import DynamicGetWhiteIp
from .common.DynamicRemain import DynamicRemain
from .common.DynamicBalance import DynamicBalance
from .common.DynamicReplaceWhiteIp import DynamicReplaceWhiteIp
from .common.UsersGetBalance import UsersGetBalance
from .common.AloneGetIps import AloneGetIps
from .common.AloneSetWhiteIp import AloneSetWhiteIp
from .common.AloneGetWhiteIp import AloneGetWhiteIp
from .common.AloneReplaceWhiteIp import AloneReplaceWhiteIp
from .common.UsersGetAllOrders import UsersGetAllOrders
from .enums.URL import URL
from .ext.StrKit import get_params
import urllib.request
from urllib.parse import unquote


# 动态代理 --提取动态代理
def dynamic_get_ips(getips: DynamicGetIps) -> str:
    dic = getips.__dict__
    appkey = dic.get("key")
    params = get_params(dic, appkey)
    request = urllib.request.urlopen(URL.DYNAMIC_GETIPS.value + params)
    result = unquote(request.read(), "utf-8")
    return result


# 动态代理 -- 校验IP可用性
def dynamic_check(check: DynamicCheck) -> str:
    dic = check.__dict__
    appkey = dic.get("key")
    params = get_params(dic, appkey)
    request = urllib.request.urlopen(URL.DYNAMIC_CHECK.value + params)
    result = unquote(request.read(), "utf-8")
    return result


# 动态代理 -- 设置代理IP白名单
def dynamic_set_white_ip(ip: DynamicSetWhiteIp) -> str:
    dic = ip.__dict__
    appkey = dic.get("key")
    params = get_params(dic, appkey)
    request = urllib.request.urlopen(URL.DYNAMIC_SETWHITEIP.value + params)
    result = unquote(request.read(), "utf-8")
    return result

# 动态代理 -- 替换IP白名单
def dynamic_replace_white_ip(ip: DynamicReplaceWhiteIp) -> str:
    dic = ip.__dict__
    appkey = dic.get("key")
    params = get_params(dic, appkey)
    request = urllib.request.urlopen(URL.DYNAMIC_REPLACEWHITEIP.value + params)
    result = unquote(request.read(), "utf-8")
    return result


# 动态代理 -- 获取IP白名单
def dynamic_get_white_ip(ip: DynamicGetWhiteIp) -> str:
    dic = ip.__dict__
    appkey = dic.get("key")
    params = get_params(dic, appkey)
    request = urllib.request.urlopen(URL.DYNAMIC_GETWHITEIP.value + params)
    result = unquote(request.read(), "utf-8")
    return result


# 动态代理 -- 获取代理剩余可用时长
def dynamic_remain(remain: DynamicRemain) -> str:
    dic = remain.__dict__
    appkey = dic.get("key")
    params = get_params(dic, appkey)
    request = urllib.request.urlopen(URL.DYNAMIC_REMAIN.value + params)
    result = unquote(request.read(), "utf-8")
    return result


# 动态代理 -- 获取剩余可提取IP数量
def dynamic_balance(balance: DynamicBalance) -> str:
    dic = balance.__dict__
    appkey = dic.get("key")
    params = get_params(dic, appkey)
    request = urllib.request.urlopen(URL.DYNAMIC_BALANCE.value + params)
    result = unquote(request.read(), "utf-8")
    return result

def users_get_allOrders(allorders: UsersGetAllOrders) -> str:
    dic = allorders.__dict__
    appkey = dic.get("key")
    params = get_params(dic,appkey)
    request = urllib.request.urlopen(URL.USERS_GETALLORDERS.value + params)
    result = unquote(request.read(), "utf-8")
    return result

# 获取账户余额
def users_get_balance(balance: UsersGetBalance) -> str:
    dic = balance.__dict__
    appkey = dic.get("key")
    params = get_params(dic, appkey)
    request = urllib.request.urlopen(URL.USERS_GETBALANCE.value + params)
    result = unquote(request.read(), "utf-8")
    return result


# 独享代理 -- 获取代理详情
def alone_get_ips(ips: AloneGetIps) -> str:
    dic = ips.__dict__
    appkey = dic.get("key")
    params = get_params(dic, appkey)
    request = urllib.request.urlopen(URL.ALONE_GETIPS.value + params)
    result = unquote(request.read(), "utf-8")
    return result


# 独享代理 -- 设置代理IP白名单
def alone_set_white_ip(ip: AloneSetWhiteIp) -> str:
    dic = ip.__dict__
    appkey = dic.get("key")
    params = get_params(dic, appkey)
    request = urllib.request.urlopen(URL.ALONE_SETWHITEIP.value + params)
    result = unquote(request.read(), "utf-8")
    return result

# 独享代理 -- 替换IP白名单
def alone_replace_white_ip(ip: AloneReplaceWhiteIp) -> str:
    dic = ip.__dict__
    appkey = dic.get("key")
    params = get_params(dic, appkey)
    request = urllib.request.urlopen(URL.ALONE_REPLACEWHITEIP.value + params)
    result = unquote(request.read(), "utf-8")
    return result



# 独享代理 -- 获取代理IP白名单
def alone_get_white_ip(ip: AloneGetWhiteIp) -> str:
    dic = ip.__dict__
    appkey = dic.get("key")
    params = get_params(dic, appkey)
    request = urllib.request.urlopen(URL.ALONE_GETWHITEIP.value + params)
    result = unquote(request.read(), "utf-8")
    return result

