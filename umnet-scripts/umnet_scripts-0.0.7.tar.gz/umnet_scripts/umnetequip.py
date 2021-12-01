from sqlalchemy import create_engine
from .utils import get_env_vars
from .umnetdb import UMnetdb
import logging

logger = logging.getLogger(__name__)

class UMnetequip(UMnetdb):
    '''
    This class wraps helpful equip db queries in python.
    The API is lame.
    '''
    def __init__(self, host='mallard.dsc.umich.edu', port=1521):

        eqdb_creds = get_env_vars(['EQUIP_DB_USERNAME','EQUIP_DB_PASSWORD'])
        self._url = f"oracle://{eqdb_creds['EQUIP_DB_USERNAME']}:{eqdb_creds['EQUIP_DB_PASSWORD']}@(DESCRIPTION=(ADDRESS=(PROTOCOL=TCP)(HOST={host})(PORT={port}))(CONNECT_DATA=(SID=PC13)))"
        self._e = create_engine(self._url)
        
        logger.debug(f"Created DB engine {self._url}")


    def get_devices_by_category(self, category, active_only=False):
        '''
        Queries equip db for devices by category. You can also
        specify if you only want active devices.
        '''

        select = [ 'eq.monitored_device', 
                   'eq.rancid',
                   'eq.off_line',
                   'eq.dns_name',
                   'eq.ip_address',
                 ]
        table = 'ARADMIN1.MAC_SLA_EQUIPMENT eq'

        where = [f"eq.category = '{category}'"]

        # Equipshim status numbers (see ARADMIN1.UMNET_EQUIPMENT_STATUS)
        # 1: RESERVE, 2:ACTIVE, 3:RETIRED
        if active_only:
            where.append("eq.status = 2")
        
        sql = self._build_select(select, table, where=where, distinct=True)
        return self._execute(sql)
