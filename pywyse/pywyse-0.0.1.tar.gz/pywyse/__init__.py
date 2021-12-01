from base64 import b64encode
from pathlib import Path 
import configparser

BASE_DIR = Path.home()

config = configparser.ConfigParser()

def auth(conf, auth='auth', platform='CW'): 
    if platform == 'CW': 
        user = conf['cw_company'] + "+" + conf['cw_public'] + ":" + conf['cw_private']
    else: 
        user = conf['sell_key'] + "+" + conf['sell_user'] + ":" + conf['sell_pw']
    password = b64encode(user.encode('ascii'))  
    conf[auth] = "Basic %s" % password.decode()
    return conf 
       

try: 
    config.read(BASE_DIR / '.cw_conf')
    __conf = {}
    for k in config["DEFAULT"]: 
        __conf[k] = config['DEFAULT'][k]
    for s in config["SELL"]: 
        __conf[s] = config['SELL'][s]

    __conf = auth(conf=__conf)
    __conf = auth(conf=__conf, auth='sell_auth', platform='SELL')
    
except: 
    print('No .cw_conf file found.\n\nPlease update the config file in your home directory.')

    config['CW'] = {
        'CW_SERVER': '',
        'CW_COMPANY': '',
        'CW_PUBLIC': '',
        'CW_PRIVATE': '',
        'CW_CLIENTID': '',
        'CW_CODEBASE': '',
        'CW_APIVERSION': ''
    }
    with open(BASE_DIR / '.cw_conf', 'w') as configfile:
        config.write(configfile)


# from . import auth
from .client import Client 
from . import basemodel
from . import exceptions
from . import utils
from pywyse.agreement import agreement
from pywyse.company import company
from pywyse.expense import expense
from pywyse.finance import finance
from pywyse.invoicing import invoicing
from pywyse.procurement import procurement
from pywyse.project import project
from pywyse.sales import sales
from pywyse.service import service 
from pywyse.system import system 
from pywyse.time import time 

