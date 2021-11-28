import os
import freehub as fh
from codetmpl import pkg_info

def fetch(address:str):
    address=fh.get_complete_address(address)
    fh.freehub_download(address,dst_path=pkg_info.code_dir)
def demo():
    fetch('pytest/hi.py')

if __name__ == '__main__':
    demo()