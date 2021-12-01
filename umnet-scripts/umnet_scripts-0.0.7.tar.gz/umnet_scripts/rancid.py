import os
import logging
from dns import resolver
from .utils import is_ip_address, forward_resolve, reverse_resolve
from .constants import CORE_IPS, VALID_PORT, RANCID_CONFIG_DIRS, I_ABBR
import re

logger = logging.getLogger(__name__)

logger.setLevel('DEBUG')

class Device:

    valid_attrs = {
        'rancid_name':'',
        'rancid_type':'',
        'model':'',
        'cfg_file':'',
        'status':'',
        'neighbors':{},
        }

    def __init__(self, **kwargs):

        for attr in self.valid_attrs:
            if attr in kwargs:
                setattr(self, attr, kwargs[attr])
            else:
                setattr(self, attr, self.valid_attrs[attr])

    def __setattr__(self, attr, value):

        if attr not in self.valid_attrs:
            raise ValueError(f'Invalid attr {attr}: valid attrs are {valid_attrs}')
        self.__dict__[attr] = value

    def __iter__(self):
        '''
        Defined so you can use dict() on a device object and get back
        A dict. Because neighbors reference other objects in a reflexive
        way, we just want to return a tuple for each neighbor (neigh_name, neigh_port). 
        '''
        for k,v in self.__dict__.items():
            
            if k in self.valid_attrs:
                yield (k, v)


    @property
    def hostname(self):
        '''
        The hostname of the device. A reverse DNS lookup is done if the
        device's rancid name is an IP address.
        If the reverse lookup fails for any reason, None is returned.
        '''

        # if the rancid name isn't set for the device return none
        if not(self.rancid_name):
            return None

        if is_ip_address(self.rancid_name):
            return reverse_resolve(self.rancid_name)

        return self.rancid_name

    @property
    def ip(self):
        '''
        The IP address of the device. A DNS lookup is done if the
        device's rancid name is a DNS name. If the lookup fails then
        'None' is returned.
        '''

        # if the rancid name isn't set for the device return none
        if not(self.rancid_name):
            return None

        if is_ip_address(self.rancid_name):
            return self.rancid_name
        
        return forward_resolve(self.rancid_name)


class Rancid:
    '''
    A class that provides easy access to rancid data
    stored on the local filesystem. This class is meant to
    be used on wallace/gromit. To use this succesfully
    on a different system you'll have to manually
    re-create '/home/rancid/' on your local system.
    '''

    def __init__(self, 
                rancid_dir:str="/home/rancid", 
                cfg_dirs:list=RANCID_CONFIG_DIRS,
                active_only:bool=False,
                get_neighbors:bool=True,
                ):
        
        # first we're going to populate an internal device
        # list with Device objects from every router.db
        # in every rancid directory
        self.rancid_dir = rancid_dir
        self.cfg_dirs = cfg_dirs

        self._devices = []
        for d in cfg_dirs:
            routerdb = f'{rancid_dir}/{d}/router.db'
            new_devices = self._parse_rdb(routerdb)
            if new_devices:
                self._devices.extend(new_devices)
            else:
                logger.error(f'No devices found in {routerdb}')

        # Now we're going to parse topologywalker and build connections
        # between the devices
        for d in self._devices:
            neigh_dict = {}

            iftable_file = f'{self.rancid_dir}/Topology/{d.ip}.ifTable'
            neigh_dict = self._parse_iftable(iftable_file)
            d.neighbors = neigh_dict                


    def _munge_port(self, port):
        '''
        Converts port reported by ifTable to the 'short'
        names we use in NSO
        '''

        # I_ABBR maps cisco short names to long ones
        for short, long in I_ABBR.items():
            if port.startswith(long):
                port.replace(long, short)
        
        # also need to remove ".0" from junos ports
        port = re.sub(r'\.0$','', port)

        return port

    def _parse_rdb(self, db_file:str, active_only:bool=False) -> list:
        '''
        Parses a router db file
        '''
        devices = []
        with open(db_file) as fh:
            lines = fh.read().splitlines()

        for l in lines:

            #rdb fields are name:rancid_type:status:platform
            fields = l.split(":")
            if fields[2] == 'up' or not(active_only):
                device = Device()

                device.rancid_name = fields[0]
                device.rancid_type = fields[1]
                device.status = fields[2]
                device.model = fields[3]
                device.cfg_file = db_file.replace('router.db',f'configs/{fields[0]}')
            
                devices.append(device)

        return devices

    def _parse_iftable(self, file):
        '''
        Given a path to a ".ifTable" file on the local
        filesystem, parses the file into a dict of
        on interface name.

        Also shortens/cleans up port names to match their
        well-known abbreviations
        '''
        if not(os.path.exists(file)):
            logging.error(f'{file} not found!')
            return {}

        with open(file) as fh:
            lines = fh.read().splitlines()

        ports = {}
        for l in lines:
            l = l.strip()
            m = re.match(r'^\d+\s+(\S+)\s+(\d+\.\d+\.\d+\.\d+)\s+(\S+)$',l)
            if m:
                port = self._munge_port(m.group(1))
                neigh_ip = m.group(2)
                neigh_port = self._munge_port(m.group(3))
                if neigh_ip not in CORE_IPS \
                    and VALID_PORT.match(port) \
                    and VALID_PORT.match(neigh_port):
                    ports[port] = (neigh_ip, neigh_port)

        return ports

    def get_device(self, name_or_ip:str) -> Device:
        '''
        returns a device based on its rancid name
        '''

        if is_ip_address(name_or_ip):
            ip = name_or_ip
            hostname = forward_resolve(name_or_ip)
        else:
            ip = reverse_resolve(name_or_ip)
            hostname = name_or_ip


        device = [d for d in self._devices if d.rancid_name in [ip, hostname] ]
        if len(device) == 0:
            return False
        if len(device) == 1:
            return device[0]
        raise LookupError(f'More than one device found for {name_or_ip}')


    def get_devices(self, **kwargs) -> list:
        '''
        Look up a set of devices based on any set of device attributes.
        If no arguments are provided, the full device list is returned.
        '''
        results = self._devices.copy()

        for k,v in kwargs.items():
            results = [ r for r in results if getattr(r,k) == v ]

        return results
 
    
    def get_dlzone(self, zone:str) -> list:
        '''
        Returns a list of devices in the same DL zone
        based on neighbors.
        '''
        devices = []
        dl1 = self.get_device(f'd-{zone.lower()}-1.umnet.umich.edu')
        if not(dl1):
            return []
       
        devices.append(dl1)

        dl2 = self.get_device(f'd-{zone.lower()}-1.umnet.umich.edu')
        if dl2:
            devices.append(dl2)

        to_do = devices.copy()

        while(len(to_do)):
            d = to_do.pop()
            if not(d.neighbors):
                continue
            for port, neigh in d.neighbors.items():

                if neigh[0] in CORE_IPS:
                    continue

                n_device = self.get_device(neigh[0])
                if n_device and n_device not in devices:
                    devices.append(n_device)
                    to_do.append(n_device)
                
        return devices

