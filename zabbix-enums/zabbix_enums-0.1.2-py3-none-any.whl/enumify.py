from copy import deepcopy
from common.host import *

def enumify_host(host: dict, deep_enumify: bool = False):
    host = deepcopy(host)
    field_mapping = {
        'available': None,
        'flags': HostFlag,
        'inventory_mode': HostInventoryMode,
        'ipmi_authtype': None,
        'ipmi_available': None,
        'ipmi_privilege': None,
        'jmx_available': None,
        'maintenance_status': HostMaintenanceStatus,
        'maintenance_type': None,
        'snmp_available': None,
        'status': HostStatus,
        'tls_connect': None,
        'tls_accept': None
    }
    for field, enumeration in field_mapping.items():
        if enumeration is None:
            continue
        if field in host:
            host[field] = enumeration(host[field])
    if deep_enumify:
        pass
    return host



host = {
            "maintenances": [],
            "hostid": "10160",
            "proxy_hostid": "0",
            "host": "Zabbix server",
            "status": "0",
            "disable_until": "0",
            "error": "",
            "available": "0",
            "errors_from": "0",
            "lastaccess": "0",
            "ipmi_authtype": "-1",
            "ipmi_privilege": "2",
            "ipmi_username": "",
            "ipmi_password": "",
            "ipmi_disable_until": "0",
            "ipmi_available": "0",
            "snmp_disable_until": "0",
            "snmp_available": "0",
            "maintenanceid": "0",
            "maintenance_status": "0",
            "maintenance_type": "0",
            "maintenance_from": "0",
            "ipmi_errors_from": "0",
            "snmp_errors_from": "0",
            "ipmi_error": "",
            "snmp_error": "",
            "jmx_disable_until": "0",
            "jmx_available": "0",
            "jmx_errors_from": "0",
            "jmx_error": "",
            "name": "Zabbix server",
            "description": "The Zabbix monitoring server.",
            "tls_connect": "1",
            "tls_accept": "1",
            "tls_issuer": "",
            "tls_subject": "",
            "tls_psk_identity": "",
            "tls_psk": ""
        }

a = enumify_host(host)
pass