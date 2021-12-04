from . import tmp


class NewDict(dict):

    def __init__(self, *args, **kwargs):
        super(NewDict, self).__init__(*args, **kwargs)

    def get(self, *args):
        if len(args) <= 1:
            return super().get(args[0])
        else:
            result = []
            for i in args:
                result.append(super().get(i))
            return tuple(result)

    def merge(self, _dict: dict):
        self.replace_dict(self, _dict)

    def append_tmp(self, dpTmp):
        _id = self.get('id')
        tmp.tmp.append(_id, dpTmp)

    def replace_dict(self, _json1: dict, _json2: dict):
        for k in list(_json2.keys()):
            v = _json2[k]
            if k not in list(_json1.keys()) or type(v) != dict:
                _json1[k] = v
            elif type(v) == dict:
                _json1[k] = self.replace_dict(_json1[k], _json2[k])
        return _json1



def singleton(cls):
    """
    单例模式，使用方式： 在类上添加装饰器 @singleton
    @param cls:
    @return:
    """
    _instance = {}

    def _singleton(*args, **kwargs):
        # 先判断这个类有没有对象
        if cls not in _instance:
            _instance[cls] = cls(*args, **kwargs)  # 创建一个对象,并保存到字典当中
        # 将实例对象返回
        return _instance[cls]

    return _singleton

