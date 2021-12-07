""" 
@project: gruntest
@file: parse 
@time: 2021/11/18
@software: PyCharm
@author: zy7y
"""
from json import dumps
from string import Template
from typing import Union, Any, Optional
from ast import literal_eval
from jsonpath import jsonpath


def parse_int(var: str) -> Any:
    """
    字符串转原有类型
    :param var:
    :return:
    """
    try:
        return literal_eval(var)
    except (ValueError, SyntaxError):
        return var


def parse_gql(var: str) -> dict:
    """
    获取query语句的optionName
    :param var:
    :return: {"query":"query", "optionName": "..."}
    """
    var = var.strip()
    first = var.index(' ')
    try:
        end = var.index('(')
    except ValueError:
        end = var.index('{')
    return {'optionName': var[first + 1: end].strip(), 'query': var}


class Parse:

    def __init__(self, data_pool: dict = None, func_pool: dict = None, last_resp=None):
        """
        Parse 解析类 处理变量、方法等
        :param data_pool: 字典变量池
        """
        self.data_pool = data_pool or {}    # data_pool 不是 None 就 赋值 {}
        self.func_pool = func_pool or {}
        self.resp = last_resp

    def print_maps(self):
        datas = dumps(self.data_pool, sort_keys=True, indent=4, separators=(',', ':'), ensure_ascii=False)
        funcs = dumps({k: [arg for arg in v.__annotations__] for k, v in self.func_pool.items()}, sort_keys=True, indent=4, separators=(',', ':'), ensure_ascii=False)
        print(datas, funcs)

    def _parse_str(self, var: str) -> str:
        """
        替换字符串的方法, 用于替换本身就是字符串的数据如 url
        :param var: ${变量} or $变量
        :return:
        """
        return Template(var).safe_substitute(self.data_pool)

    def _parse_json_str(self, var: str) -> Any:
        """
        处理 json/dict/ list 中的 变量名称
        :param var: $变量
        :return:
        """
        if var.startswith('$'):
            return self.data_pool.get(var[1:])

    def _parse_func_obj(self, var: str) -> Any:
        """
        使用方法对象的方式调用函数 功能等同于 _parse_func
        :param var:
        :return:
        todo: 如果方法的参数是 url 将会出现错误
        """
        if var.startswith('${') and var.endswith('}'):
            var = self._parse_str(var)
            func_str = var[2:-1]
            func_name = func_str[: func_str.index('(')]
            func_vars = func_str[func_str.index('(') + 1: func_str.rindex(')')].strip()

            args = []
            kwargs = {}

            if not func_vars:
                return self.func_pool.get(func_name)()

            for arg in func_vars.split(','):
                if '=' in arg.strip():
                    kwarg = arg.split('=')
                    kwargs[kwarg[0].strip()] = parse_int(kwarg[1].strip())
                else:
                    args.append(parse_int(arg.strip()))
            try:
                return self.func_pool.get(func_name)(*args, **kwargs)
            except TypeError:
                return var
        return self._parse_json_str(var)

    def parse_url(self, url: str) -> str:
        """
        解析 url 中的 $xx ${func()}, ${func($a, $b)}
        :param url: $url
        :return:
        >>> p = Parse({"url": "https://www.baidu.com"})
        >>> p.parse_url('$url')
        'https://www.baidu.com'
        >>> p.parse_url('$url/${sum1(1,2)}/${sum1(1,3)}')
        'https://www.baidu.com/3/4'
        """
        url = self._parse_str(url)
        for i in url.split('/'):
            if i.startswith('${') and i.endswith('}'):
                url = url.replace(f'{i}', str(self._parse_func_obj(i)))
        return url

    def parse_json(self, data: Union[dict, list]):
        """
        解析json/dict/list 中的 $xx, ${func()}, ${func($xx)} 动态加载模块中的方法对象并执行
        :param data: 初始数据类型为dict
        :return:

        >>> from gruntest import loader
        >>> module = loader.loader_module('examples.gruntest')
        >>> funcs = loader.loader_funcs(module)
        >>> form = {"age": 18, "name": "奥利", "info": "g", "phone": 18716356843}
        >>> p = Parse(data_pool=form, func_pool=funcs)
        >>> form = {"name": "${sum3( a=3,b = 4 )}", "info": {"phone": "$phone", "loves": \
        ["$age", "${sum2(3)}", {"info": "$phone"}]}, "ages": "${sum4('$age', $phone)}"}
        >>> p.parse_json(form)
        {'name': 7, 'info': {'phone': 18716356843, 'loves': [18, 3, {'info': 18716356843}]}, 'ages': {'18': 18716356843}}
        """
        if isinstance(data, dict):
            for k, v in data.items():
                if isinstance(v, str):
                    data[k] = self._parse_func_obj(v)
                elif isinstance(v, (dict, list)):
                    self.parse_json(v)

        elif isinstance(data, list):
            for i, v in enumerate(data):
                if isinstance(v, str):
                    data[i] = self._parse_func_obj(v)
                elif isinstance(v, (dict, list)):
                    self.parse_json(v)

        return data

    def parse_gql_body(self, query: str, variables: Optional[dict] = None) -> dict:
        """
        构造graphql的请求数据, 并处理其中的变量 和 方法
        :param query: query语句
        :param variables:
        :return:
        """
        body = parse_gql(query)
        if variables is None:
            variables = {}
        else:
            variables = self.parse_json(variables)
        body.update({"variables": variables})
        return body

    def _extra(self, repx):
        if result := jsonpath(self.resp, repx):
            return result[0]
        else:
            return repx

    def extra_vars(self, extra_map: dict):
        """
        提取参数
        :param extra_map:
        :return:
        """
        for k, v in extra_map.items():
            self.data_pool[k] = self._extra(v)

    def expect_vars(self, expect_map):
        """
        断言
        :param expect_map:
        :return:
        """
        if expect_map is None:
            return
        for k, v in expect_map.items():
            # k 实际, v 期望
            assert self._extra(k) == v

