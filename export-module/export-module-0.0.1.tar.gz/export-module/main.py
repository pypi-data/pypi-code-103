'''
Author: 兄弟们Go
Date: 2021-11-07 17:01:31
LastEditTime: 2021-11-28 19:11:10
LastEditors: 兄弟们Go
Description: 
FilePath: \export-module\main.py

'''
import importlib
from inspect import getframeinfo,currentframe
from re import findall,sub
class Import_Manager(object):
    def __init__(self,name):
        self.__ImportData__ ={
            'obj':None,
            '_obj':None,
            'spec':None,
            'name':name,
            'at':None,
            'imported':False
        }
    def _can_require(self,name):
        """是否能够被导入"""
        self.__ImportData__["spec"] = importlib.util.find_spec(name)
        if self.__ImportData__["spec"] is None:
            return False
        else:
            return True
    def _check_imported(self):
        """检查是否引入，若没有则引入"""
        data = self.__ImportData__
        if data["imported"]==False:
            package=self._resolve_name()
            self._Import(package)
    def _Import(self,name):
        """导入操作"""
        data = self.__ImportData__
        if self._can_require(name)==False:
            raise ModuleNotFoundError(f'No module named {name!r}',name)
        module = importlib.util.module_from_spec(data["spec"])
        data["spec"].loader.exec_module(module)
        # 更新导入状态
        data["imported"] = True
        # 引入的是模块
        if data["at"] is None:
            data["obj"] = self._resolve_export(module)
        else:
            # 引入的是模块内容
            # data["_obj"] = module
            data["obj"] = self._resolve_export_at(module,data["name"])
    def _resolve_name(self):
        """
        处理名称，返回包名
        """
        data = self.__ImportData__
        if data["at"] is not None:
            return data["at"]
        return data["name"]
    def _resolve_export_at(self,obj,name):
        if(hasattr(obj, "Export")):
            if(name in obj.Export.data.keys()):
                return obj.Export.data[name]
            raise ModuleNotFoundError(f'No module named {name!r}',name)
        # 没有使用export
        return getattr(obj,name,None)
    def _resolve_export(self,obj):
        """处理导入"""
        if(hasattr(obj, "Export")):
            # 直接返回所有export内容
            if(len(obj.Export.data) == 1):
                return obj.Export.data[obj.Export.data.keys()[0]]
            return obj.Export.data
        # 没有使用export
        return obj
class Import(object):
    def __init__(self,name):
        self.__IM__ = Import_Manager(name)
    def From(self,name):
        self.__IM__.__ImportData__["at"] = name
        return self
    def As(self,name):
        # 暂时不能用
        self.__IM__._check_imported()
        globals().update({name:self.__IM__.__ImportData__["obj"]})
        return self.__IM__.__ImportData__["obj"]
    def __call__(self,*args,**kwargs):
        # print("call",args,kwargs)
        self.__IM__._check_imported()
        return self.__IM__.__ImportData__["obj"](*args,**kwargs)
    def __getattr__(self, name):
        # print("getattr",name)
        if(name == "__IM__"):
            return super().__getattr__(name)
        self.__IM__._check_imported()
        return getattr(self.__IM__.__ImportData__["obj"],name,None)
    def __setattr__(self,name,value):
        # print("setattr",name)
        if(name=="__IM__"):
            return super().__setattr__(name,value)
        self.__IM__._check_imported()
        return setattr(self.__IM__.__ImportData__["obj"],name,value)
    def __str__(self):
        """
        字符串表示
        """
        data = self.__IM__.__ImportData__
        self.__IM__._check_imported()
        if(data["imported"]):
            return str(data["obj"])
        return self.__repr__()
    def __repr__(self):
        data = self.__IM__.__ImportData__
        self.__IM__._check_imported()
        if(data["imported"]):
            return repr(data["obj"])
        return '<{0}.{1} object at {2}>'.format(
            self.__module__,type(self).__name__,hex(id(self)))
class Export(object):
    store_name = "_ExportData_"
    data = {}
    ignore_tokens=["_exportSTR_"]
    def __init__(self,*args,**kwargs):
        self.frame = currentframe()
        if(kwargs):
            self._store_dict(kwargs)
        if(args):
            names = self._get_names(args,self.frame)
            self._store_dict(names)
    def _get_names(self,args,frame):
        _,_,_,code_context,_=getframeinfo(frame.f_back)
        func_name = findall('Export\((.*)\)',code_context[0])
        func_name=sub(r"""(['|"].*['|"])""",'_exportSTR_',func_name[-1]).split(',')
        result = {}
        index = 0
        for i in func_name:
            if i not in self.ignore_tokens:
                result.setdefault(i,args[index])
            index += 1
        return result
    def _store_dict(self,dic):
        for i in dic.keys():
            self._store(i,dic[i])
        return True
    def _store(self,name,value):
        # global _ExportData_
        if(name in self.data.keys()):
            self.data[name] = value
            return True
        return self.data.setdefault(name,value)
if __name__ == '__main__':
    # a = require("tkinter").As('s')
    # print(s)
    pass