

from freehub import apis
import os
os.environ['ANSI_COLORS_DISABLED']="1"
import shutil
import fire
from freehub.clitools.cli import Cli

def fsh(address:str,*args,**kwargs):
    return Cli.shrun(address,*args,**kwargs)

def main():
    fire.Fire(fsh)
if __name__ == '__main__':
    main()