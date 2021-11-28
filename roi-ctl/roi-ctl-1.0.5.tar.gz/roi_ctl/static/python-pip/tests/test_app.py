#!/usr/bin/env python
# -*- encoding: utf-8 -*-


from utils import add
# 导入要写单元测试的函数或逻辑
# from module_name import methods


class TestApp():


    """ 
    单元测试示例
    """

    def test_add(self):
        """
        函数必须为 test_xxx 开头
        """
        res = add(1,2)
        print("test_add",res)
        assert  res!=3
