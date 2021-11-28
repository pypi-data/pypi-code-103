import os
os.environ['ANSI_COLORS_DISABLED']="1"
import shutil
import fire
from wkmake.make import make_from_files,WKMAKE_FILENAME
from wkmake.pkg_info import pkg_templates_dir,PkgData,TemplatePaths
from wkmake.utils import export
class CLI:
    def hi(cls):
        print('Hi, I am codetmpl.'.center(50, '*'))

def main():
    fire.Fire(CLI())

if __name__ == '__main__':
    main()