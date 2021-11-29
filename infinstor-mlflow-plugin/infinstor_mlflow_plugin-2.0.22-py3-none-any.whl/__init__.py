import os
import logging
import json
import builtins
import logging

def read_infinstor_config_json_key(jsonkey:str):
    keyval = None
    config_json_path = os.path.join(os.path.expanduser('~'),'.infinstor','config.json')
    if os.path.exists(config_json_path): 
        with open(config_json_path, 'r') as fh:
            config_json:dict = json.load(fh)
            keyval = config_json.get(jsonkey, None)
    return keyval

def get_log_level_from_config_json(module_name:str) -> int:
    """
    Get the loglevel (integer) that correpsonds to the specified module_name, by looking into ~/.infinstor/config.json
    """
    
    loglevel_str:str = read_infinstor_config_json_key('loglevel.' + module_name)
    
    loglevel_int = None
    # if config.json has loglevel defined for the specified module    
    if loglevel_str:
        loglevel_int:int = getattr(logging, loglevel_str.upper(), None)
    
    return loglevel_int

logging.basicConfig(level=get_log_level_from_config_json("root"), format="%(asctime)s - %(process)d - %(name)s - %(levelname)s - %(message)s")

def set_builtins_with_serverside_config(server_config:dict):
    builtins.clientid = server_config.get('clientid', "default_unknown")
    builtins.appclientid = server_config.get('appclientid', "default_unknown")
    builtins.mlflowserver = server_config.get('mlflowserver', "default_unknown")
    builtins.mlflowuiserver = server_config.get('mlflowuiserver', "default_unknown")
    builtins.mlflowstaticserver = server_config.get('mlflowstaticserver', "default_unknown")
    builtins.apiserver = server_config.get('apiserver', "default_unknown")
    builtins.serviceserver = server_config.get('serviceserver', "default_unknown")
    builtins.service = server_config.get('service', "default_unknown")
    builtins.region = server_config.get('region', "default_unknown")

