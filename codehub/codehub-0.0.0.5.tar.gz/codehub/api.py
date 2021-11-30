import os
import shutil

import freehub as fh
from codehub import pkg_info
from codehub import utils
import logging
logging.basicConfig(level=logging.INFO)


def fetch_if_not_exists(address:str,target=None):
    return fetch_(address,target=target,ignore_if_exists=True)
def fetch_(address:str,target=None,ignore_if_exists=False):
    c_address=fh.get_complete_address(address)
    dst_path=utils.join_path(pkg_info.code_dir,target or os.path.basename(address))
    if not os.path.exists(dst_path):
        fh.freehub_download(c_address,dst_path=dst_path)
    else:
        if ignore_if_exists:
            logging.info('Ignore %s'%(address))
        else:
            raise FileExistsError(dst_path)

def clean(path='/'):
    dir=utils.join_path(pkg_info.code_dir,path)
    for item in os.listdir(dir):
        if item=='__init__.py':
            continue
        child=os.path.join(dir,item)
        if os.path.isdir(child):
            shutil.rmtree(child)
        else:
            os.remove(child)

def demo():
    # fetch_if_not_exists('pytest/hi.py')
    clean('/')

if __name__ == '__main__':
    demo()