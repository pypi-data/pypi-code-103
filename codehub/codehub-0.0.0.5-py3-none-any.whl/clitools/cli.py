import os
os.environ['ANSI_COLORS_DISABLED']="1"
import shutil
import fire
from codehub import api
class CLI:
    @classmethod
    def hi(cls):
        print('Hi, welcome to use codehub !'.center(50, '*'))
    @classmethod
    def fetch(cls,address:str):
        api.fetch(address)
    @classmethod
    def clean(cls,path='/'):
        api.clean(path)
def main():
    fire.Fire(CLI())

if __name__ == '__main__':
    main()