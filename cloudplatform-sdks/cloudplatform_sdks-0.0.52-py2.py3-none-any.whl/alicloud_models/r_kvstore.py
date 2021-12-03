from .clients import rkv_client


class AliRKvstore:

    def __init__(self, info=None):
        self.r_kvstore = info

    @classmethod
    def get_instances(cls, params=None):
        return rkv_client.describe_instances(params)

    @classmethod
    def get_instance_netinfo(cls, params=None):
        return rkv_client.describe_instance_netinfo(params)

    @classmethod
    def get_instance_attribute(cls, params=None):
        return rkv_client.describe_instance_attribute(params)

    @classmethod
    def get_security_ips(cls, params=None):
        return rkv_client.describe_security_ips(params)

    @classmethod
    def get_instance_auto_renewal_attribute(cls, params=None):
        return rkv_client.describe_instance_auto_renewal_attribute(params)


