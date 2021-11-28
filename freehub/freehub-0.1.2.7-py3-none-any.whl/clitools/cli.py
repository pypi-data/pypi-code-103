from freehub import apis
import os
os.environ['ANSI_COLORS_DISABLED']="1"
import shutil
import fire
from freehub import utils

class Cli:
    '''
    address: [[[{host}/]{username}/]{repo_name}:]{branch_name}[/{relative_path}]
    TODO:
        - run: when address point to a directory ,what to run, should it run a script with tht default name. e.g. start.bat.
        - or use a package.json to customize the behaviour.

        - how to run an app
    '''
    @classmethod
    def help(cls,address:str):
        '''
        Print information about given address, might be the content of README.md under the given address
        '''
        raise NotImplementedError(Cli.help)
    @classmethod
    def install(cls,address:str):
        raise NotImplementedError(cls.install)
    @classmethod
    def publish(cls,address,str):
        raise NotImplementedError(cls.publish)
    @classmethod
    def update(cls):
        apis.freehub_update()
    @classmethod
    def download(cls,address,path=None,overwrite=False):
        path=path or './'
        address=apis.get_complete_address(address)
        apis.freehub_download(address,path,overwrite=overwrite,quiet=False)
    @classmethod
    def upload(cls,path,address,overwrite=True):
        address = apis.get_complete_address(address)
        apis.freehub_upload(path,address,overwrite=overwrite,quiet=False)
    @classmethod
    def login(cls):
        apis.freehub_login()
    @classmethod
    def logout(cls):
        apis.freehub_logout()

    @classmethod
    def search(cls,pattern:str):
        '''
        - search branch under any repo
        - search files under any branch
        :param pattern:
        :return:
        '''
        pattern=apis.get_complete_address(pattern)
        apis.freehub_search(pattern)
    @classmethod
    def ls(cls, address:str=None):
        '''

        :param repo:
        :return:
        - list branches under any repo
        - list files under any branch
        '''
        if not address:
            return cls.branch.list()
        if address.endswith(':'):
            return cls.branch.list(address.rstrip(':'))
        address = apis.get_complete_address(address)
        pattern=address.rstrip('/')+'/*'
        return cls.search(pattern)
    @classmethod
    def cat(cls, address):
        '''
        output file content to stdout (that is : print content)
        :param address:
        :return:
        '''
        address = apis.get_complete_address(address)
        apis.freehub_cat(address)

    @classmethod
    def run(cls,address:str,*args,**kwargs):
        address = apis.get_complete_address(address)
        script_path = apis.fetch(address)
        args_string = ' '.join(args)
        kwargs_string = []
        for k, v in kwargs.items():
            kwargs_string.append('--%s=%s' % (k, v))
        kwargs_string = ' '.join(kwargs_string)
        os.system('%s %s %s'%(script_path,args_string,kwargs_string))

    @classmethod
    def shrun(cls, address: str, *args, **kwargs):
        address = apis.get_complete_address(address)
        script_path = apis.fetch(address)
        def try_file_path(pre, sufs=None):
            if sufs is None:
                sufs = []
            sufs=['']+sufs
            for suf in sufs:
                if os.path.exists(pre+suf):
                    return pre+suf
        script_path=try_file_path(script_path,['.sh'])
        args_string = ' '.join(args)
        kwargs_string = []
        for k, v in kwargs.items():
            kwargs_string.append('--%s=%s' % (k, v))
        kwargs_string = ' '.join(kwargs_string)
        os.system('bash %s %s %s' % (script_path, args_string, kwargs_string))
    @classmethod
    def test(cls,*args,**kwargs):
        print(*args)
        print(kwargs)
    @classmethod
    def version(cls):
        print('freehub-0.1.2.7')
    class branch:
        @classmethod
        def search(cls,pattern:str):
            pattern = apis.get_complete_address(pattern)
            apis.freehub_branch_search(pattern)
        @classmethod
        def list(cls,repo:str=None):
            pattern = repo + ':*' if repo else '*'
            return cls.search(pattern)
    @classmethod
    def pyrun(cls,address:str,*args,**kwargs):
        return cls.py.run(address,*args,**kwargs)
    class py:
        @classmethod
        def run(cls,address:str,*args,**kwargs):
            if not address.endswith('.py'):
                address+='.py'
            address = apis.get_complete_address(address)
            file_path = apis.fetch(address)
            args_string=' '.join(args)
            kwargs_string=[]
            for k,v in kwargs.items():
                kwargs_string.append('--%s=%s'%(k,v))
            kwargs_string=' '.join(kwargs_string)
            os.system('python %s %s %s'%(file_path,args_string,kwargs_string))
def main():
    fire.Fire(Cli)
if __name__ == '__main__':
    main()