""" 
@project: grun
@file: loader 
@time: 2021/11/18
@software: PyCharm
@author: zy7y
"""
from importlib import reload, import_module
from types import ModuleType, FunctionType


def loader_module(module_name: str) -> ModuleType:
    """
    根据模块名，加载模块
    :param module_name: 模块名
    :return: 模块对象
    """
    module = import_module(module_name)
    reload(module)
    return module


def loader_funcs(module: ModuleType) -> dict[str, FunctionType]:
    """
    得到模块中的方法字典
    :param module: 模块
    :return: 方法字典
    """
    # func_pool = {}
    # for k, v in vars(module).items():
    #     if isinstance(v, FunctionType):
    #         func_pool[k] = v
    # return func_pool
    return {k: v for k, v in vars(module).items() if isinstance(v, FunctionType)}


def loader_local(path='hooks'):
    try:
        module = loader_module(path)
    except ModuleNotFoundError:
        raise ModuleNotFoundError('请在根目录下新建 hooks.py文件')
    return loader_funcs(module)
