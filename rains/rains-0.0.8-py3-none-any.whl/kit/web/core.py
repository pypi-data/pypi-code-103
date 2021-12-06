# !/usr/bin/env python
# coding:utf-8

"""
Copyright (c) 2021. quinn.7@foxmail.com All rights reserved.
Based on the Apache License 2.0 open source protocol.

作者 cat7
邮箱 quinn.7@foxmail.com

"""


import time
import random

from rains.common.log import Log
from rains.common.db.sql_packaging import Sql
from rains.common.db.const import ConstDatabaseTaskNaming
from rains.common.db.const import ConstDatabaseCaseNaming
from rains.common.i.i_core import ICore
from rains.common.db.database import Database
from rains.common.const import ConstProjectType
from rains.common.const import ConstTaskAndCaseState
from rains.common.const import ConstTaskOrderSignNaming
from rains.common.task.case_recorder import CaseRecorder
from rains.common.task.task_instruction import TaskInstruction

from rains.kit.web.web_plant import WebPlant
from rains.kit.web.web_engine import WebEngine
from rains.kit.web.web_const import BrowserType


BROWSER_TYPE = BrowserType


_CORE_NUMBER_POOL = []
""" 核心编号池 """


class WebCore(ICore):
    """
    WEB核心

    * 运行核心相对于任务的消费者，它负责接收任务，并解析运行。
    * 另外，它代理着一个 WebEngine 引擎对象，并在工作流中管理其生命周期。

    """

    _log = Log()
    """ 日志服务 """

    _db = Database()
    """ 数据库服务 """

    _engine: WebEngine = None
    """ 引擎对象 """

    _plant: WebPlant = None
    """ 工厂对象 """

    _core_id: int
    """ 核心ID """

    _project_type: str = ConstProjectType.WEB
    """ 项目类型 """

    _case_recorder: CaseRecorder = CaseRecorder()
    """ 用例记录器 """

    def __init__(self):
        """
        初始化
        """
        # 生成随机核心ID并创建引擎对象
        while True:
            self._core_id = random.randint(10000, 99999)

            if self._core_id not in _CORE_NUMBER_POOL:
                _CORE_NUMBER_POOL.append(self._core_id)
                break
            else:
                continue

        self._engine = WebEngine(self._core_id)
        self._plant = WebPlant(self._engine)

    @property
    def engine(self):
        return self._engine

    @property
    def plant(self):
        return self._plant

    @property
    def core_id(self):
        return self._core_id

    @property
    def project_type(self):
        return self._project_type

    def set_browser_type(self, browser_type: str):
        """
        设置引擎的浏览器类型
        """
        self._engine.set_browser_type(browser_type)
        return self

    def start_task(self, task, log: bool = True):
        """
        开始执行 task

        * 接收一个 task，并执行该 task。

        Args:
            task (object): 任务对象，可以是实现 ITask 接口的任务类，或者是符合JSON译文标准的字典
            log (bool): 日志开关

        """
        # 执行任务类
        if not isinstance(task, dict):
            return self._running_task_code(TaskInstruction().convert_from_code(task), log)

        else:
            pass

    def end(self):
        """
        注销

        * 关闭数据库连接，并调用引擎对象的 end() 函数。

        """
        self._db.close()
        self._engine.end()
        return self

    def _running_task_code(self, task_instruction: TaskInstruction, log: bool):
        """
        执行 CODE 译文

        Args:
            task_instruction (Object): TaskInstruction 对象
            log (bool): 日志开关

        Return:
            TaskReport 任务报告

        """
        # 实例化任务类型
        task_class_living = task_instruction.task_class()
        task_class_living.engine = self._engine
        task_class_living.plant = self._plant

        if not task_class_living.engine.get_state():
            task_class_living.engine.run()

        # 初始化数据缓冲区
        db_task_id = 0
        execute_data = time.strftime("%Y-%m-%d")
        case_all_count = 0
        case_pass_count = 0
        case_fail_count = 0
        task_is_completed = True
        task_start_time = ''
        task_spend_time_s = 0

        # 解析步骤指令集数量
        all_case_count = len(task_instruction.instruction_map_step.keys())
        # 声明当前用例完成进度
        complete_count = 1

        try:
            # 获取任务注释内容
            remark = 'NULL'
            if type(task_class_living).__doc__:
                remark = type(task_class_living).__doc__.strip()

            # 创建数据库任务记录
            db_task_id = self._db.write(Sql.tasks_add({
                ConstDatabaseTaskNaming.NAME: task_instruction.task_name,
                ConstDatabaseTaskNaming.REMARK: remark,
                ConstDatabaseTaskNaming.EXECUTE_DATE: execute_data
            }))

            # 执行 类级起点 函数
            self._running_instruction_map_flow(
                task_instruction.instruction_map_flow[ConstTaskOrderSignNaming.CLASS_STARTING],
                task_class_living
            )

            # 记录任务开始时间
            task_start_time = time.strftime("%H:%M:%S")
            task_spend_time_s = int(time.time())

            # 执行步骤指令集
            for case_name, case_function in task_instruction.instruction_map_step.items():

                if log:
                    self._log.info(f'— case running ->>> [{all_case_count}/{complete_count}]')

                # 执行 函数级起点 函数
                self._running_instruction_map_flow(
                    task_instruction.instruction_map_flow[ConstTaskOrderSignNaming.FUNCTION_STARTING],
                    task_class_living
                )

                # 获取用例函数注释内容
                case_remark = 'NULL'
                if case_function.__doc__:
                    case_remark = case_function.__doc__.strip()

                # 数据库创建用例记录
                db_case_id = self._db.write(Sql.cases_add({
                    ConstDatabaseCaseNaming.TID: db_task_id,
                    ConstDatabaseCaseNaming.NAME: case_name,
                    ConstDatabaseCaseNaming.REMARK: case_remark,
                    ConstDatabaseCaseNaming.EXECUTE_DATE: execute_data
                }))

                # 用例计数器自增
                case_all_count += 1

                running_result = self._running_case(db_case_id, task_class_living, case_function)

                if running_result:
                    case_pass_count += 1
                    self._log_output(f'case[{ case_name }]::[{ConstTaskAndCaseState.SUCCESSFUL}]', log)
                else:
                    case_fail_count += 1
                    self._log_output(f'case[{ case_name }]::[{ConstTaskAndCaseState.UNSUCCESSFUL}]', log)
                    task_is_completed = False

                # 当前用例完成进度自增
                complete_count += 1

                # 执行 函数级终点 函数
                self._running_instruction_map_flow(
                    task_instruction.instruction_map_flow[ConstTaskOrderSignNaming.FUNCTION_ENDING],
                    task_class_living
                )
                self._engine.reset()

            # 执行 类级终点 函数
            self._running_instruction_map_flow(
                task_instruction.instruction_map_flow[ConstTaskOrderSignNaming.CLASS_ENDING],
                task_class_living
            )

            # 如果引擎仍在运行，则结束引擎
            if task_class_living.engine.get_state():
                task_class_living.engine.end()

        except BaseException as e:
            self._log_output(f'由于未知异常任务被迫中止:: { e }', log)
            task_class_living.engine.end()

        finally:
            # 更新数据库任务记录
            task_end_time = time.strftime("%H:%M:%S")
            self._db.write(Sql.tasks_update({
                ConstDatabaseTaskNaming.TID: db_task_id,
                ConstDatabaseTaskNaming.IS_COMPLETED: task_is_completed,
                ConstDatabaseTaskNaming.START_TIME: task_start_time,
                ConstDatabaseTaskNaming.END_TIME: task_end_time,
                ConstDatabaseTaskNaming.SPEND_TIME_S: (int(time.time()) - task_spend_time_s),
                ConstDatabaseTaskNaming.CASE_ALL: case_all_count,
                ConstDatabaseTaskNaming.CASE_PASS: case_pass_count,
                ConstDatabaseTaskNaming.CASE_FAIL: case_fail_count
            }))
            self._db.commit()

    def _running_case(self, case_id, task_class, case_function_object) -> bool:
        """
        执行用例

        Args:
            case_id (int): 用例数据库记录ID
            task_class (Object): 任务类型实例
            case_function_object (Object): 用例函数

        Return:
            Bool

        """
        case_db_dict = dict()
        case_db_dict[ConstDatabaseCaseNaming.CID] = case_id
        case_start_time = time.strftime("%H:%M:%S")
        case_spend_time_s = int(time.time())

        try:
            # 执行用例
            r = case_function_object(task_class)

            # 如果用例返回 True 或者未返回 False 都判断为用例通过
            if r is True or r is None:
                case_db_dict[ConstDatabaseCaseNaming.STATE] = ConstTaskAndCaseState.SUCCESSFUL
                return True

            # 如果用例返回 False 则判断用例失败
            else:
                case_db_dict[ConstDatabaseCaseNaming.STATE] = ConstTaskAndCaseState.UNSUCCESSFUL
                return False

        # 如果用例执行过程发生异常则判断用例失败
        except BaseException as e:
            case_db_dict[ConstDatabaseCaseNaming.STATE] = ConstTaskAndCaseState.ANOMALY
            self._log.debug(f'{ e }')
            return False

        finally:
            case_db_dict[ConstDatabaseCaseNaming.START_TIME] = case_start_time
            case_db_dict[ConstDatabaseCaseNaming.END_TIME] = time.strftime("%H:%M:%S")
            case_db_dict[ConstDatabaseCaseNaming.SPEND_TIME_S] = (int(time.time()) - case_spend_time_s)
            case_db_dict[ConstDatabaseCaseNaming.RUN_STEP] = self._case_recorder.read(self.core_id)

            self._db.write(Sql.cases_update(case_db_dict))

    @staticmethod
    def _running_instruction_map_flow(function, t):
        if function:
            function(t)

    def _log_output(self, message: str, log: bool):
        """
        日志输出

        Args:
            message (str): 输出信息

        """
        if log:
            self._log.info(f'RUN_CASE::[执行核心::{ self._core_id }]::{ message } ')
