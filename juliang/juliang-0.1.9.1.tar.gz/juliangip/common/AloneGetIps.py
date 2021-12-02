class AloneGetIps(object):
    def __init__(self, key, trade_no):
        self.key = key
        self.trade_no = trade_no

    # 密钥
    key = ""
    # 业务编号
    trade_no = ""
    # SOCK代理端口
    sock_port = ""
    # IP可用时间[动态型独有]
    ip_remain = ""
    # 地区名称
    city_name = ""
    # 邮政编码
    city_code = ""
    # 业务到期时间
    order_endtime = ""
