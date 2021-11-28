

import logging
import sys, os
import toml
from . import *





logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')



sh = logging.StreamHandler(sys.stdout)
sh.setFormatter(formatter)
logger.addHandler(sh)

logger.debug('Welcome to project repo: https://github.com/kannab98/seawavepy')



        
        
name = 'config.toml'

cwd = os.getcwd()

cfg = os.path.join(cwd, name)
if os.path.isfile(cfg):
    configfile = cfg
else:
    configfile = os.path.join(os.path.dirname(__file__), name)

config = toml.load(configfile)
logger.info('Load config from %s' % configfile)

fh = logging.FileHandler('retracking.log')
fh.setFormatter(formatter)
logger.addHandler(fh)

import logging
import re, os
logger = logging.getLogger(__name__)

# def get_files(file, **kwargs):
#     """
#     Рекурсивный поиск данных по регулярному выражению 
#     """
#     # file = file.replace('\\', os.path.sep)
#     # file = file.replace('/', os.path.sep)
#     path, file = os.path.split(file)

#     path = os.path.abspath(path)

#     # file = os.path.join(path, file)
#     rx = re.compile(file)


#     _files_ = []
#     for root, dirs, files in os.walk(path, **kwargs):
#         for file in files:
#             tmpfile = os.path.join(root, file)
#             _files_ += rx.findall(tmpfile)
    
#     for file in _files_:
#         logger.info("Found file: %s" % file)

#     return _files_

# from . import retracking_new

# from . import retracking
# retracking = retracking.__retracking__()