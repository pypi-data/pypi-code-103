from sqlalchemy import create_engine
from .utils import get_env_vars
from .umnetdb import UMnetdb
import logging
import ipaddress

logger = logging.getLogger(__name__)

class UMnetinfo(UMnetdb):
    '''
    This class wraps helpful netinfo db queries in python.
    '''
    def __init__(self, host='kannada.web.itd.umich.edu', port=1521):

        eqdb_creds = get_env_vars(['NETINFO_USERNAME','NETINFO_PASSWORD'])
        self._url = f"oracle://{eqdb_creds['NETINFO_USERNAME']}:{eqdb_creds['NETINFO_PASSWORD']}@(DESCRIPTION=(ADDRESS=(PROTOCOL=TCP)(HOST={host})(PORT={port}))(CONNECT_DATA=(SID=KANNADA)))"
        self._e = create_engine(self._url)
        
        logger.debug(f"Created DB engine {self._url}")


    def get_network_by_ip(self, ip, active_only=False):
        '''
        Looks up a network based on an IPv4 or IPv6 address. Returns the netname,
        vlan id, as well as *all active subnets* (IPv4 and IPv6) tied to the netname.
        '''

        ip = ipaddress.ip_address(ip)

        # to make our lives simpler we're breaking this up into two steps.
        # first let's find the network entry in the 'item' table
        if ip.version == 4:
            select = ["p.itemidnum"]
            table = 'UMNET_ONLINE.IP_SUBNET ip'
            joins = [
                'join UMNET_ONLINE.ITEM i on ip.itemidnum = i.itemidnum',
                'join UMNET_ONLINE.ITEM p on i.parentitemidnum = p.itemidnum',
                ]
            where = [
                    f"{int(ip)} >= ip.ADDRESS32BIT",
                    f"{int(ip)} <= ip.ENDADDRESS32BIT",
                    ]

        # IPv6 table is related to the 'item' table via the RELATED_ITEM table
        elif ip.version == 6:
            select = ["p.itemidnum"]
            table = 'UMNET_ONLINE.IP6NET ip'
            joins = [
                'join UMNET_ONLINE.RELATED_iTEM r on r.itemidnum = ip.itemidnum',
                'join UMNET_ONLINE.ITEM p on p.itemidnum = r.relitemidnum',
                    ]
            # and the start/end addresses are stored as hex strings
            addr_str = ip.exploded.replace(":","")
            where = [
                    f"'{addr_str}' >= ip.ADDRESS128BIT",
                    f"'{addr_str}' <= ip.ENDADDRESS128BIT",
                    ]

        # add status check if user wants it    
        if active_only:
            where.append("p.statuscd='A'")

        sql = self._build_select(select, table, joins=joins, where=where)
        network = self._execute(sql)

        if not(network):
            return False
        net_id = network[0][0]

        # Now let's use the network itemidnum to find all associated subnets
        # with that network, as well as the netname and VLAN ID
        select = [
                "p.itemname as netname",
                "i.itemname as ipv4_subnet",
                "six_i.itemname as ipv6_subnet",
                "NVL(n.vlanid,n.local_vlanid) AS vlan_id",
                ]
        table = "UMNET_ONLINE.ITEM p"
        joins = [
                "join UMNET_ONLINE.NETWORK n on p.itemidnum = n.itemidnum",
                "join UMNET_ONLINE.ITEM i on i.parentitemidnum = p.itemidnum",
                "join UMNET_ONLINE.IP_SUBNET ip on i.itemidnum = ip.itemidnum",
                "join UMNET_ONLINE.RELATED_ITEM r on p.itemidnum = r.relitemidnum",
                "join UMNET_ONLINE.IP6NET six on r.itemidnum = six.itemidnum",
                "join UMNET_ONLINE.ITEM six_i on six.itemidnum = six_i.itemidnum",
                ]
        where = [f"p.itemidnum = {net_id}"]

        sql = self._build_select(select, table, joins=joins, where=where)
        results = self._execute(sql)
        return results



