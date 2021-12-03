from .clients import cbs_client


class TencentCbs:
    def __init__(self, object):
        self.object = object

    @property
    def id(self):
        return self.object.get('DiskId')

    @property
    def name(self):
        return self.object.get('DiskName')

    @property
    def disk_type(self):
        return self.object.get('DiskType')

    @property
    def host_id(self):
        return self.object.get('InstanceId')

    @property
    def state(self):
        return self.object.get('DiskState')

    @property
    def size(self):
        return self.object.get('DiskSize')

    @property
    def charge_type(self):
        return self.object.get('DiskChargeType')

    @classmethod
    def list(cls, **kwargs):
        volumes = cbs_client.describe_volume(**kwargs).get('DiskSet')
        if not volumes:
            return
        return [cls(volume) for volume in volumes]

