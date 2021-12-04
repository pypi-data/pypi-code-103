import hashlib


# 计算签名
def get_params(kv: {}, appkey: str) -> str:
    # 清理参数
    cleanParams = clean_params(kv)
    value = format_url_map(cleanParams, 0, 0)
    value += "&key=" + appkey
    sign = hashlib.md5(value.encode(encoding='UTF-8')).hexdigest()
    cleanParams["sign"] = sign
    params = format_url_map(cleanParams, 0, 0)
    return "?" + params


# 在字典中清理不用的参数
def clean_params(kv: {}) -> {}:
    para_map = {}
    for i in kv:
        value = kv[i]
        if value == "":
            continue
        if i == "key":
            continue
        para_map[i] = value
    return para_map


# 方法用途: 对所有传入参数按照字段名的 ASCII 码从小到大排序（字典序），并且生成url参数串
def format_url_map(para_map: {}, url_encode: bool, key_toLower: bool) -> str:
    buff = ""
    for i in sorted(para_map):
        if i == "key":
            continue
        buff += "&" + i + "=" + para_map[i]
    buff = buff[1:]
    return buff

# def main():
#     paraMap = {}
#     paraMap["trade_no"] = "1135123858735679"
#     paraMap["num"] = "5"
#     paraMap["pt"] = "2"
#     paraMap["city_name"] = "1"
#     paraMap["result_type"] = "json"
#     paraMap["key"] = "0794d170bdc14b3f835a2202bb21cbcd"
#     params = get_params(paraMap, paraMap["key"])
#     print(params)
#
#
# if __name__ == "__main__":
#     main()
