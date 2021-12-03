"""
提供兼容 s3 的常用 file system 操作 
"""
import os
import uuid
import megfile
import pathlib
import builtins
import functools
import skimage.io
import glob as glob_std
from functools import wraps
from boxx import FuncArgs, removeimp
from megfile import (
    is_s3,
    smart_glob,
    smart_listdir,
    smart_open,
    smart_remove,
    smart_isdir,
)


os_abspath = os.path.abspath


def abspath_for_s3(self):
    """
    To support 

    >>> smart_abspath('s3://a/b/../c')
    's3://a/c'
    """
    return str(self.root) + os_abspath("/" + self.path_without_protocol)[1:]


megfile.pathlike.URIPath.abspath = abspath_for_s3


class ramfs:
    mode = "r"
    PATH_TYPES = (str, bytes, pathlib.Path)

    def __init__(self, func, arg=None, mode=None):
        """
        装饰器, 装饰某个函数后, 使其兼容 s3 path::
            img = ramfs(imread)(s3_path)
            ramfsw(imsave)(s3_path, img)
        
        原理: 会将对应的 oss 文件拷贝到内存文件 (/dev/shm 下), 对应函数在内存文件上操作完成后再同步回 oss
        arg:
            None: 自动找到第一个是 (str, bytes, pathlib.Path) 的变量作为 path
            int: 第几个参数
            str: 参数名
        """
        self.func = func
        functools.update_wrapper(self, func)
        if mode is None:
            mode = self.mode
        self.mode = mode
        assert mode in "rw"
        self.arg = arg

    class ThreadingSafeWith:
        def __init__(self, father, args, kwargs):
            self.father = father
            self.args = args
            self.kwargs = kwargs
            self.func_args = FuncArgs(father.func, *args, **kwargs)
            if not hasattr(self.father, "argname"):
                self.father.argname = self.func_args.find_argname(
                    father.arg or father.PATH_TYPES
                )
            self.path = self.func_args.get_arg(self.father.argname)
            self.not_local = (
                self.path.startswith("s3://")
                or self.path.startswith("http://")
                or self.path.startswith("https://")
            )

        def __enter__(self):
            if self.not_local:
                self.tmp_dir = os.path.join("/dev/shm", "ramfs_tmp", str(uuid.uuid1()))
                os.makedirs(self.tmp_dir)
                self.tmp_path = os.path.join(self.tmp_dir, os.path.basename(self.path))
                if self.father.mode == "r":
                    megfile.smart_copy(self.path, self.tmp_path)
                self.func_args.set_arg(self.father.argname, self.tmp_path)
            return self.func_args

        def __exit__(self, exc_type, exc_value, exc_traceback):
            if self.not_local:
                try:
                    if exc_type is None and self.father.mode == "w":
                        megfile.smart_copy(self.tmp_path, self.path)
                finally:
                    if os.path.isfile(self.tmp_path):
                        os.remove(self.tmp_path)
                    os.rmdir(self.tmp_dir)

    def __call__(self, *args, **kwargs):
        with self.ThreadingSafeWith(self, args, kwargs) as func_args:
            re = func_args.apply(self.func)
        return re

    @staticmethod
    def test():
        from skimage import data
        from boxx import imsave, imread, show, mg

        img = data.coffee()
        path = "s3://yl-share/tmp/a.jpg"
        ramfsw(imsave)(path, img)
        show - ramfs(imread)(path)
        url = path.replace("s3://", "https://oss.iap.hh-b.brainpp.cn/")
        print(" S3:", path)
        print("URL:", url)
        mg()


class ramfsw(ramfs):
    mode = "w"


std_funcs = {}


def def_new_path_func(module, name, megfile_name=None):
    if name in std_funcs:
        return std_funcs[name]["compat_func"]
    if megfile_name is None:
        megfile_name = name
    smart_name = "smart_" + (megfile_name or name)
    std_func = getattr(module, name)
    smart_func = getattr(megfile.smart, smart_name)
    globals()[smart_name] = smart_func

    @wraps(std_func)
    def compat_func(*args, **kwargs):
        # print(__import__('boxx').prettyFrameStack())
        path = args[0] if len(args) else kwargs["path"]
        if is_s3(path):
            return smart_func(*args, **kwargs)
        return std_func(*args, **kwargs)

    std_funcs[name] = dict(
        name=name,
        module=module,
        std_func=std_func,
        smart_name=smart_name,
        smart_func=smart_func,
        compat_func=compat_func,
    )
    return compat_func


def compat_mode():
    """
    通过侵入式地替换标准库中的 path 操作, 在几乎不改动代码的情况下, 让 Python 程序兼容 oss. 即让 boxx, os.path, skimage.io 兼容 s3.
    用法: 需要文件最开始导入::
        from brainpp_yl.fs import compat_mode, open, isdir, ramfs, ramfsw
        compat_mode()

        import boxx
    
    - 被侵入式替换的函数记录在 brainpp_yl.fs.std_funcs, 不支持 isdir (有神奇BUG)
    """
    skimage.io.imread = imread
    skimage.io.imsave = imsave

    # 在 IPython 中第二次 run 的时候会导致 len not found 错误
    # os.path.isdir = isdir
    for k, d in std_funcs.items():
        setattr(d["module"], k, d["compat_func"])
    removeimp("boxx")
    # import boxx
    # boxx.loadjson = ramfs(boxx.loadjson)
    # boxx.savejson = ramfsw(boxx.savejson)
    # boxx.loadCoco = ramfs(boxx.loadCoco)
    # boxx.saveCoco = ramfsw(boxx.saveCoco)

    builtins.open = open


listdir = def_new_path_func(os, "listdir")
makedirs = def_new_path_func(os, "makedirs")
remove = def_new_path_func(os, "remove")
abspath = def_new_path_func(os.path, "abspath")
relpath = def_new_path_func(os.path, "relpath")
realpath = def_new_path_func(os.path, "realpath")
isfile = def_new_path_func(os.path, "isfile")
isabs = def_new_path_func(os.path, "isabs")
glob = def_new_path_func(glob_std, "glob")

# 在 IPython 中第二次 run 的时候会导致 len not found 错误
# isdir = def_new_path_func(os.path, "isdir")
isdir_std = os.path.isdir


def isdir(s):
    if is_s3(s):
        return smart_isdir(s)
    return isdir_std(s)


imread = ramfs(skimage.io.imread, 0)
imsave = ramfsw(skimage.io.imsave, 0)

builtins_open = builtins.open


@wraps(builtins_open)
def open(file, *args, **argkv):
    if isinstance(file, int):
        # support os.pipe()
        return builtins_open(file, *args, **argkv)
    else:
        return smart_open(file, *args, **argkv)


if __name__ == "__main__":
    compat_mode()
    ramfs.test()
