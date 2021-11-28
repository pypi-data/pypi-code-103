#!/usr/bin/env python
# -*- encoding: utf-8 -*-


"""
测试主函数
"""

import pytest


if __name__=="__main__":
    # 全部用例文件
    pytest.main(["tests","-s"])
    # 单个用例文件
    pytest.main(["tests/test_app.py","-s"])

