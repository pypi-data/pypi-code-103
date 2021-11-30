
from .clients import hw_eip_client, hw_bss_client


class HuaweiEip:
    STATE_UNBIND = 'DOWN'
    STATE_BIND = 'ACTIVE'

    def __init__(self, object):
        self.object = object

    @property
    def id(self):
        return self.object.id

    @property
    def status(self):
        return self.object.status

    @property
    def name(self):
        return self.object.bandwidth_name

    @property
    def ip(self):
        return self.object.public_ip_address

    @property
    def type(self):
        return self.object.type

    @property
    def private_ip(self):
        return self.object.private_ip_address

    @property
    def port_id(self):
        return self.object.port_id

    @classmethod
    def get(cls, publicip_id=None):
        public_ip = hw_eip_client.describe_eip(publicip_id)
        if not public_ip:
            return
        return cls(public_ip)

    @classmethod
    def list(cls):
        public_ips = hw_eip_client.list_eip()
        if not public_ips:
            return
        return [cls(public_ip) for public_ip in public_ips]

    @classmethod
    def create(cls, params=None):
        create_response = hw_eip_client.create_eip(body_params=params)
        if not create_response:
            return
        if create_response.publicip:
            return create_response.publicip.id
        order_id = create_response.order_id
        return hw_bss_client.list_resources_by_order(order_id)

    def delete(self):
        return hw_eip_client.delete_eip(publicip_id=self.id)

    def associate(self, port_id=None):
        params = {
            "publicip": {
                "port_id": port_id
            }
        }
        return hw_eip_client.update_eip(self.id, body_params=params)

    def disassociate(self):
        params = {
            "publicip": {
                "port_id": ""
            }
        }
        return hw_eip_client.update_eip(self.id, body_params=params)

    def prepaid_resource(self):
        return hw_bss_client.query_resource(self.id)

    def cancel_resource(self):
        return hw_bss_client.cancel_resource(self.id)

