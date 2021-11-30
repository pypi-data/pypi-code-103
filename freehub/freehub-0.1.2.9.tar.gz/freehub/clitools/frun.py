

from freehub import apis
import os
os.environ['ANSI_COLORS_DISABLED']="1"
import shutil
import fire
from freehub.clitools.cli import Cli

def frun(address:str,*args,**kwargs):
    return Cli.run(address,*args,**kwargs)

def main():
    fire.Fire(frun)
if __name__ == '__main__':
    main()