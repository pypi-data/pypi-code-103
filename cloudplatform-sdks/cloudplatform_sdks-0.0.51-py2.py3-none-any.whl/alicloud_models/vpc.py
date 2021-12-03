from .clients import vpc_client
import math


class AliVpc:

    STATUS_MAPPER = {
        'Available': 'available',
        'InUse': 'inuse',
        'Deleted': 'deleted',
        'Pending': 'pending',
    }

    def __init__(self, vpc_info):
        self.vpc_info = vpc_info

    @classmethod
    def get_vpc_list(cls, params=None):
        vpcs, max_len = list(), 50
        if isinstance(params, dict):
            params['PageSize'] = params.get('PageSize', max_len)
        else:
            params = {'PageSize': max_len}
        params['PageNumber'] = 1
        response = vpc_client.describe_vpcs(params)
        if 'TotalCount' in response:
            vpcs = response['Vpcs']['Vpc']
            tolal = response['TotalCount']
            page_total = math.ceil(tolal / params['PageSize'])
            page_number = response['PageNumber']
            while page_number < page_total:
                params['PageNumber'] += 1
                page_number += 1
                response = vpc_client.describe_vpcs(params)
                vpcs += response['Vpcs']['Vpc']
        return {'Vpcs': {'Vpc': vpcs}}

    @classmethod
    def get_vpc_attribute(cls, params=None):
        return vpc_client.describe_vpc_attribute(params)

    @classmethod
    def get_vswitches_list(cls, params=None):
        vswitches, max_len = list(), 50
        if isinstance(params, dict):
            params['PageSize'] = params.get('PageSize', max_len)
        else:
            params = {'PageSize': max_len}
        params['PageNumber'] = 1
        response = vpc_client.describe_vswitches(params)
        if 'TotalCount' in response:
            vswitches = response['VSwitches']['VSwitch']
            tolal = response['TotalCount']
            page_total = math.ceil(tolal / params['PageSize'])
            page_number = response['PageNumber']
            while page_number < page_total:
                params['PageNumber'] += 1
                page_number += 1
                response = vpc_client.describe_vswitches(params)
                vswitches += response['VSwitches']['VSwitch']
        return {'VSwitches': {'VSwitch': vswitches}}

    @classmethod
    def get_vswitches_attribute(cls, params=None):
        return vpc_client.describe_vswitch_attributes(params)

    @classmethod
    def get_eip_address(cls, params=None):
        eipaddresses, max_len = list(), 50
        if isinstance(params, dict):
            params['PageSize'] = params.get('PageSize', max_len)
        else:
            params = {'PageSize': max_len}
        params['PageNumber'] = 1
        response = vpc_client.describe_eip_address(params)
        if 'TotalCount' in response:
            eipaddresses = response['EipAddresses']['EipAddress']
            tolal = response['TotalCount']
            page_total = math.ceil(tolal / params['PageSize'])
            page_number = response['PageNumber']
            while page_number < page_total:
                params['PageNumber'] += 1
                page_number += 1
                response = vpc_client.describe_eip_address(params)
                eipaddresses += response['EipAddresses']['EipAddress']
        return {'EipAddresses': {'EipAddress': eipaddresses}}

