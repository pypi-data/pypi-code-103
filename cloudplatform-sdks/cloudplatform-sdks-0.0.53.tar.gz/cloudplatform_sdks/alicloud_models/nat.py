from .clients import nat_client


class AliNatDomain:
    def __init__(self, obj):
        self.obj = obj

    @classmethod
    def create(cls, params):
        response = nat_client.create_nat(params)
        return response.get("NatGatewayId")

    @classmethod
    def update_attrs(cls, params):
        nat_client.modify_nat_attrs(params)

    @classmethod
    def update_spec(cls, params):
        nat_client.modify_nat_spec(params)

    @classmethod
    def get_nats(cls, params=None):
        response = nat_client.describe_nats(params)
        return response

    @classmethod
    def delete(cls, params):
        nat_client.delete_nat(params)

    @classmethod
    def bound(cls, params):
        nat_client.bound_eip(params)

    @classmethod
    def unbound(cls, params):
        nat_client.unbound_eip(params)

    @classmethod
    def get_vpc_info(cls, params):
        res = nat_client.describe_vpc(params)
        return res

    @classmethod
    def create_snat(cls, params):
        nat_client.create_snat(params)

    @classmethod
    def describe_snat(cls, params):
        res = nat_client.describe_snat(params)
        return res

    @classmethod
    def delete_snat(cls, params):
        nat_client.delete_snat(params)

    @classmethod
    def create_dnat(cls, params):
        nat_client.create_dnat(params)

    @classmethod
    def describe_dnat(cls, params):
        nat_client.describe_dnat(params)

    @classmethod
    def delete_dnat(cls, params):
        nat_client.delete_dnat(params)