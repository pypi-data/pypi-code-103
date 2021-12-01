from enum import Enum
from ncclient import manager
import logging
import json
from lxml import etree
from .constants import NETBOX_NSO_NEDS
from datetime import datetime
from pprint import pprint

NCS_NAMESPACE = 'http://tail-f.com/ns/ncs'
NAMESPACES = {'ncs':NCS_NAMESPACE}

logger = logging.getLogger()


class UMnetnso:

    def __init__(self, host='localhost', port=2022, 
            user='admin', password='admin'):

        self.m = manager.connect_ssh(
                host,
                username=user,
                password=password,
                port=port,
                look_for_keys=False,
                hostkey_verify=False
                )

        self._device_groups = None

    def _get_xpath(self, get_type, xpath, filter_on=[], source='running', with_defaults=None):
        '''
        Builds an xpath get or get_config query based on a provided absolute path
        and an optional list of things to filter on at that path. Then calls the ncclient get or get_config
        method and returns a result.

        The 'filtered on' input is for filtering out the child nodes retrieved at that path and
        will get 'ored' together.

        Eg: filter_on = ['address','port'] will get translated to '*[self::address|self::port]'

        xpath :str: a string representing an absolute path
        get_type :str: either 'get' or 'get_config'
        filter_on :list: a list of nodes to further filter for
            at the provided path - they will get ORed together.
        source :string: The source datastore (eg "running" or "candidate"), only
            applicable for get_config
        with_defaults :string: see RFC6243, tells NSO whether to return default
            config values or not
        Result is returned as :class: xml.etree.ElementTree.Element
        '''

        if filter_on:
            filter_str = "|".join([f"self::{f}" for f in filter_on])
            filtered_xpath = f'{xpath}*[{filter_str}]'
        else:
            filtered_xpath = xpath

        logger.debug(f"_get_xpath: generated xpath {filtered_xpath}")

        if get_type == 'get':
            result = self.m.get(filter=('xpath', filtered_xpath), with_defaults=with_defaults)

        elif get_type == 'get_config':
            result = self.m.get_config(source=source, filter=('xpath', filtered_xpath), with_defaults=with_defaults)

        else:
            raise ValueError(f"Invalid netconf get type {get_type}")

        return result.data_ele

    def get_device_groups(self, device_name=None, force_query=False):
        '''
        Returns a list of nso group names. If you provide a device name
        it will return the groups tied only to that device.

        The function sets an internal object called _device_group when
        first queried. If you don't set force_query to "true", it will
        use that cached object for subsequent calls.

        device_name :str: name of device
        force_query :bool: Force a new call to nso 
        '''

        if self._device_groups == None or force_query:
            self._device_groups = self._get_xpath('get_config', '/devices/device-group')
        
        if device_name:
            query = f"//ncs:device-group[ncs:device-name='{device_name}']/ncs:name/text()"
        else:
            query = "//ncs:device-group/ncs:name/text()"
       
        return self._device_groups.xpath(query, namespaces=NAMESPACES)



    def get_nso_devices(self):
        '''
        Gets a subset of basic config info for all devices in NSO. Returns results
        as a list of dicts with the following format:
            [{'name':name, 'address':address, 'ned-id', ned-id, 'admin-state':admin-state,
               'groups':[list of groups] } ]
        '''

        # Get device addresses, type (NED), and admin state. We'll also get the device
        # name since it's the key for the devices/device leaflist.
        xpath='/devices/device/'
        filter_on = ['device-type','address','state']
        result = self._get_xpath('get_config', xpath, filter_on=filter_on, with_defaults='report-all')

        # extract values from leafs
        leafs = ['name','address','admin-state','ned-id']
        output_lists = [result.xpath(f'//ncs:{l}/text()',namespaces=NAMESPACES) for l in leafs]

        
        # this transforms a list of lists [ [name1, name2,...], [ip1, ip2, ...] ...]
        # into a list of dicts
        #  [{'name':name1,'address':ip1,...}, {'name':name2,'address':ip2,...}... ]
        output = [ dict(zip(leafs,device)) for device in list(zip(*output_lists)) ]
       
        # Add group membership to device entries
        for d in output:
            d['groups'] = set(self.get_device_groups(device_name=d['name']))

        return output

    def update_nb_devices(self, nb_devices, operation='merge'):
        '''
        This takes a list of pynetbox device objects and updates the NSO device
        and device group leaflists
        :devices: list of pynetbox device objects
        :operation: the netconf operation for the devices (default: merge)
        '''
        # First we need a current list of the device group assignments from NSO.
        xpath='/devices/device-group'
        nso_groups = self._get_xpath('get_config', xpath)

        # Now let's start building our tree
        config = etree.Element("{urn:ietf:params:xml:ns:netconf:base:1.0}config")
        devices = etree.SubElement(config, "devices", nsmap={None:NCS_NAMESPACE})

        # add elements
        for d in nb_devices:

            e_device = etree.SubElement(devices, "device",operation=operation)
            etree.SubElement(e_device, "name").text = d.name
            etree.SubElement(e_device, "address").text = d.primary_ip4.address.split("/")[0]
            etree.SubElement(e_device, "port").text = "22"
            etree.SubElement(e_device, "authgroup").text = "local"
            
            try:
                ned = NETBOX_NSO_NEDS[d.platform.name]
            except KeyError:
                logger.error("ERROR: no NED for {d.platform.name}, skipping")
                continue

            d_type = etree.SubElement(e_device, "device-type")
            ned_type = etree.SubElement(d_type, ned["device-type"])
            etree.SubElement(ned_type, "ned-id").text = ned["ned-id"]

            source = etree.SubElement(e_device, "source")
            etree.SubElement(source, "when").text = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
            etree.SubElement(source, "source").text = "Netbox audit script"

            # current device groups are based on site and device role
            nb_groups = [ d.device_role.slug, d.site.slug ]

            # pull existing groups for this device
            curr_groups = self.get_device_groups(d.name)

            # if a device is in a group it shouldn't be, remove that.
            for g in [g for g in curr_groups if g not in nb_groups]:
                e_group = etree.SubElement(devices, "device-group")
                etree.SubElement(e_group, "name").text = g
                etree.SubElement(e_group, "device-name",operation='delete').text = d.name

            # if a device needs to be added to a group, add it
            for g in [g for g in nb_groups if g not in curr_groups]:
                e_group = etree.SubElement(devices, "device-group")
                etree.SubElement(e_group, "name").text = g
                etree.SubElement(e_group, "device-name").text = d.name

        result = self.m.edit_config(config, target="running")



        return result

    def remove_devices(self, device_names):
        '''
        This takes a list of device names and removes them from NSO.
        :device_names: list of device names
        '''

        config = etree.Element("{urn:ietf:params:xml:ns:netconf:base:1.0}config")
        devices = etree.SubElement(config, "devices", nsmap={None:'http://tail-f.com/ns/ncs'})

        # reset device group internal element
        self._device_groups = None

        for d in device_names:
            e_device = etree.SubElement(devices, "device", operation="delete")
            etree.SubElement(e_device, "name").text = d

            groups = self.get_device_groups(d)
            for g in groups:
                e_group = etree.SubElement(devices,"device-group")
                etree.SubElement(e_group,"name").text = g
                etree.SubElement(e_group,"device-name",operation='delete').text = d

        result = self.m.edit_config(config, target="running")

        return result
