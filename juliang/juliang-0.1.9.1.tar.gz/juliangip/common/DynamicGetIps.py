class DynamicGetIps(object):
    def __init__(self, key, trade_no, num):
        self.key = key
        self.trade_no = trade_no
        self.num = num


    # 业务秘钥
    key = ""
    # 业务编号
    trade_no = ""
    # 提取数量
    num = ""
    # 代理类型
    pt = ""
    # 返回类型
    result_type = ""
    # 结果分隔符
    split = ""
    # 地区名称
    city_name = ""
    # 邮政编码
    city_code = ""
    # 剩余可用时长
    ip_remain = ""
    # 筛选地区
    area = ""
    # 排除地区
    no_area = ""
    # 筛选ip段
    ip_seg = ""
    # 排除IP段
    no_ip_seg = ""
    # 运营商筛选
    isp = ""
    # IP去重
    filter = ""
