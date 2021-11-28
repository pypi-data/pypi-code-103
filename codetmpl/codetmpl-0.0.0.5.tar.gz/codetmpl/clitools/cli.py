import os
os.environ['ANSI_COLORS_DISABLED']="1"
import shutil
import fire
from freehub.clitools.cli import Cli as fhcli
class CLI:
    def hi(cls):
        print('Hi, I am codetmpl.'.center(50, '*'))
    def export(self,tmpl:str,target='.'):
        tmpl=tmpl.replace('\\','/')
        if not '/' in tmpl:
            address='tmpl/'+tmpl
        else:
            address=tmpl
        fhcli.download(address,target)
def main():
    fire.Fire(CLI())

if __name__ == '__main__':
    main()