# !/usr/bin/env python
# coding:utf-8

"""
Copyright (c) 2021. quinn.7@foxmail.com All rights reserved.
Based on the Apache License 2.0 open source protocol.

作者 cat7
邮箱 quinn.7@foxmail.com

"""


from rains.common.const import ConstTaskType
from rains.common.const import ConstTaskOrderSignNaming


CASE_SPECIFICATION_NAME = 'CASE'


class TaskInstruction(object):
    """
    [ 任务指令集 ]
    * rains 允许通过多种方式编写自动化测试用例。
    * 为了使这些方式具备一定的兼容性，TaskInstruction类将进行中间指令集的转换。

    """

    task_name: str
    """ 任务名称 """

    task_type: str
    """ 任务类型 """

    task_class = None
    """ 任务类的类名 """

    _is_packaging: bool = False
    """ 是否完成组装 """

    _instruction_map_flow: dict
    """ 流程指令集 """

    _instruction_map_step: dict
    """ 步骤指令集 """

    def __init__(self):
        """
        [ 初始化 ]
        * 无

        [ 必要参数 ]
        * 无

        [ 可选参数 ]
        * 无

        [ 返回内容 ]
        * 无

        """

        # 初始化 流程指令集
        self._instruction_map_flow = {
            ConstTaskOrderSignNaming.CLASS_STARTING: None,
            ConstTaskOrderSignNaming.CLASS_ENDING: None,
            ConstTaskOrderSignNaming.FUNCTION_STARTING: None,
            ConstTaskOrderSignNaming.FUNCTION_ENDING: None,
        }

        # 初始化 步骤指令集
        self._instruction_map_step = {}

    @property
    def instruction_map_flow(self):
        return self._instruction_map_flow

    @property
    def instruction_map_step(self):
        return self._instruction_map_step

    def convert_from_code(self, task_class):
        """
        [ 从 Task 类中转换 ]
        * 无

        [ 必要参数 ]
        * task_class (Object): 继承 ITask 接口的任务类

        [ 可选参数 ]
        * 无

        [ 返回内容 ]
        * 无

        """

        try:

            if not self._is_packaging:

                # 确认 指令集类型
                self.task_type = ConstTaskType.CODE
                # 获取 任务类的类名
                self.task_class = task_class
                # 读取 任务类的信息
                self.task_name = task_class.__name__

                # 捕获指令集
                for k, v in self.task_class.__dict__.items():

                    # 捕获 流程指令集
                    # 遍历任务类中是否存在与 流程指令命名 一致的函数
                    # 如果存在则将其储存到 流程指令集 中
                    if k in self._instruction_map_flow.keys() and callable(v):
                        self._instruction_map_flow[k] = v

                    # 捕获 步骤指令集
                    # 遍历任务类中函数命名是否以符合规范
                    # 如果存在则将其储存到 步骤指令集 中
                    if str(k[:4:]).upper() == CASE_SPECIFICATION_NAME and callable(v):
                        self._instruction_map_step[k] = v

                # 完成封装
                self._is_packaging = True

            return self

        except BaseException as e:
            raise Exception(f'从 Task类 中转换指令集时发生了异常:: { e }')
