import os
os.environ['ANSI_COLORS_DISABLED']="1"
import shutil
import fire
from wkmake.make import make_from_files,WKMAKE_FILENAME
from wkmake.pkg_info import pkg_templates_dir,PkgData,TemplatePaths
from wkmake.utils import export

class CLI:
    def hi(cls):
        print('Hi, I am wkmake.'.center(50, '*'))
    def makepkg(self,pkg_name):
        if os.path.exists(pkg_name):
            raise FileExistsError("File or directory already exists: %s"%(pkg_name))
        else:
            os.makedirs(pkg_name)
            shutil.copy(TemplatePaths.wkmake_file_path,os.path.join(pkg_name,WKMAKE_FILENAME))

    def make(self,dst='./wkmake-output',src='python_package',cfg=WKMAKE_FILENAME,overwrite=False):
        if not os.path.exists(src):
            src2=os.path.join(pkg_templates_dir,src)
            if not os.path.exists(src2):
                raise FileNotFoundError('Make source %s not found.'%(src))
            else:
                src=src2
        make_from_files(src,dst,config_files=[cfg],overwrite=overwrite)
    def export(self,demo=True,dst=None):
        dst=dst or './export-output'
        if demo:
            export(PkgData.Paths.example,dst)

def main():
    fire.Fire(CLI())

if __name__ == '__main__':
    main()