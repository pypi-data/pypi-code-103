import os
import shutil

import freehub as fh
from codehub import pkg_info
from codehub import utils
import logging
logging.basicConfig(level=logging.INFO)


def fetch_if_not_exists(address:str):
    return fetch_(address,ignore_if_exists=True)
def fetch_(address:str,ignore_if_exists=False):
    basename=os.path.basename(address)
    c_address=fh.get_complete_address(address)
    target=utils.join_path(pkg_info.code_dir,basename)
    if not os.path.exists(target):
        fh.freehub_download(c_address,dst_path=pkg_info.code_dir)
    else:
        if ignore_if_exists:
            logging.info('Ignore %s'%(address))
        else:
            raise FileExistsError(target)

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