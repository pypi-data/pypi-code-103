#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import os
import json
from .app_static import get_package

class AppProduct:
    """
    运行环境
    """

    def __init__(self):
        """
        环境变量
        """
        # 日志
        self.is_debug = True
        # 声明环境变量: product.json 保持一致

    def create():
        # 环境
        env_code = "debug"
        if "ENV" in os.environ:
            env_code = os.environ["ENV"]
        envs = {}
        config_file  =  get_package()
        with open(config_file, "r") as file:
            envs = json.loads(file.read())["envs"]
        env_runtime = envs[env_code]
        # 若需要外部环境变量加载，在此进行
        # 环境配置
        print(env_code, json.dumps(env_runtime, indent=4))
        # 初始化配置
        prod = AppProduct()
        prod.__dict__ = env_runtime
        return prod


# exports product
product = AppProduct.create()
