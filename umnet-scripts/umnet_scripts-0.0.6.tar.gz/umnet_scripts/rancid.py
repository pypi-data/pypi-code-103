import os
import logging
from dns import resolver
from .utils import resolve_name_or_ip
from .constants import CORE_IPS, VALID_PORT, RANCID_CONFIG_DIRS

logger = logging.getLogger(__name__)

class Device:

    valid_attrs = {
        'hostname':'',
        'ip':'',
        'rancid_type':'',
        'model':'',
        'cfg_file':'',
        'status':'',
        'neighbors':{},
        }

    def __init__(self, **kwargs):

        for attr in self.valid_attrs:
            if attr in kwargs:
                setattr(self, k, kwargs[k])
            else:
                setattr(self, k, self.valid_attrs[k])

    def __setattr__(self, attr, value):
        if attr not in valid_attrs:
            raise ValueError(f'Invalid attr {attr}: valid attrs are {valid_attrs}')
        self.__dict__[attr] = value

    @property
    def rancid_name(self):
        '''
        The 'rancid name' of the device is the name
        the device is known as - either dns name (core/dl/dc/etc)
        or ip address (al). We're deriving it from the config
        file
        '''
        return os.path.basename(self.cfg_file)

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
                active_only:bool=False):
        
        # first we're going to populate an internal device
        # list with Device objects from every router.db
        # in every rancid directory
        self.rancid_dir = rancid_dir
        self.cfg_dirs = cfg_dirs

        self._devices = []
        for d in cfg_dirs:
            routerdb = f'{rancid_dir}/{d}/router.db'
            self._devices.extend(self._parse_rdb(d))

        # Now we're going to parse topologywalker and build connections
        # between the devices
        for d in self._devices:
            iftable_file = f'{self.rancid_dir}/Topology/{d.rancid_name}.ifTable'
            neighs = self._parse_iftable(iftable_file)

            # parse_iftable returns a dict of 
            # tuples neighs[port] = (neigh_ip, neigh_port)
            for port, neigh in neighs.items():
                n_device = [d for d in self._devices if d.ip == neigh[0]]
                if n_device:
                    d.neighbors[port] = n_device[0]


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

        with open(db_file) as fh:
            rdb = fh.read.splitlines()

        devices = []

        for l in rdb:

            #rdb fields are name:rancid_type:status:platform
            fields = l.split(":")
            if fields[2] == 'up' or not(active_only):
                
                device = Device()
                name_and_ip = resolve_name_or_ip(fields[1])
                device.hostname = name_and_ip['dns']
                device.ip = name_and_ip['ip']

                device.rancid_type = fields[1]
                device.status = fields[2]
                device.model = fields[3]
                device.cfg_file = db_file.replace('router.db',f'configs/{fields[0]}')
            
                devices.append(device)

    def _parse_iftable(self, file):
        '''
        Given a path to a ".ifTable" file on the local
        filesystem, parses the file into a dict of
        on interface name.

        Also shortens/cleans up port names to match their
        well-known abbreviations
        '''

        if not(os.path.exists(file)):
            self.log.error(f'{file} not found!')
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
        returns a device based on name or ip
        '''
        name_or_ip = resolve_name_or_ip(fields[1])
        device = [d for d in self._devices 
                    if d.hostname == name_or_ip['name']
                    or d.ip == name_or_ip['ip']
                ]
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
 

