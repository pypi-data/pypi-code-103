"""
A unittest for pyocean.task module
"""

from multirunnable.mode import RunningMode
from multirunnable.tasks import OceanTask, QueueTask
from abc import ABCMeta, abstractmethod
import pytest



class OceanTaskTestCases(metaclass=ABCMeta):

    """
    Record and define which testing cases and scenario we need to do.
    """

    @abstractmethod
    def test_get_function(self, ocean_task):
        """
        Description:
            Getting target function which be used as running multi-work simultaneously.
        Sub-Test Item:
            The callable function could be run with fun_args or fun_kwargs.
        Success:
            Get a Callable object and could be run.
        :return:
        """
        pass


    @abstractmethod
    def test_set_function(self, ocean_task):
        """
        Description:
            Setting target function which be used as running multi-work simultaneously.
        Sub-Test Item:
            The callable function could be run with fun_args or fun_kwargs.
        Success:
            Get a Callable object and could be run.
        :return:
        """
        pass


    @abstractmethod
    def test_get_func_args(self, ocean_task):
        pass


    @abstractmethod
    def test_set_func_args(self, ocean_task):
        pass


    @abstractmethod
    def test_get_func_kwargs(self, ocean_task):
        pass


    @abstractmethod
    def test_set_func_kwargs(self, ocean_task):
        pass


    @abstractmethod
    def test_get_initialization(self, ocean_task):
        pass


    @abstractmethod
    def test_set_initialization(self, ocean_task):
        pass


    @abstractmethod
    def test_get_init_args(self, ocean_task):
        pass


    @abstractmethod
    def test_set_init_args(self, ocean_task):
        pass


    @abstractmethod
    def test_get_init_kwargs(self, ocean_task):
        pass


    @abstractmethod
    def test_set_init_kwargs(self, ocean_task):
        pass


    @abstractmethod
    def test_get_group(self, ocean_task):
        pass


    @abstractmethod
    def test_set_group(self, ocean_task):
        pass


    @abstractmethod
    def test_get_done_handler(self, ocean_task):
        pass


    @abstractmethod
    def test_set_done_handler(self, ocean_task):
        pass


    @abstractmethod
    def test_get_error_handler(self, ocean_task):
        pass


    @abstractmethod
    def test_set_error_handler(self, ocean_task):
        pass


    @abstractmethod
    def test_get_running_timeout(self, ocean_task):
        pass


    @abstractmethod
    def test_set_running_timeout(self, ocean_task):
        pass



class QueueTaskTestCases(metaclass=ABCMeta):

    @abstractmethod
    def test_get_name(self):
        pass


    @abstractmethod
    def test_set_name(self):
        pass


    @abstractmethod
    def test_get_queue_type(self):
        pass


    @abstractmethod
    def test_set_queue_type(self):
        pass


    @abstractmethod
    def test_get_value(self):
        pass


    @abstractmethod
    def test_set_value(self):
        pass



class TestingTargetFunction:

    def general_function(self, *args, **kwargs):
        print("This is testing general function.")
        print(f"Get the args: {args}")
        print(f"Get the kwargs: {kwargs}")


    def function_args(self):
        return "param1", "param2", 1, 2, ("t1", "t2"), ["l1", "l2"]


    def function_kwargs(self):
        return {"param1": "param1", "param2": "param2", "1": 1, "2": 2, "args": ("t1", "t2"), "kwargs": ["l1", "l2"]}


    def initial_function(self, *args, **kwargs):
        print("This is testing general function.")
        print(f"Get the args: {args}")
        print(f"Get the kwargs: {kwargs}")


    def init_func_args(self):
        return "param1", "param2", 1, 2, ("t1", "t2"), ["l1", "l2"]


    def init_func_kwargs(self):
        return {"param1": "param1", "param2": "param2", "1": 1, "2": 2, "args": ("t1", "t2"), "kwargs": ["l1", "l2"]}


    def done_function(self, result):
        print("This is testing done function.")
        print(f"Get the result: {result}")


    def error_function(self, e):
        print("This is testing exception function.")
        print(f"Get the e: {e}")



class TestOceanTask(OceanTaskTestCases):

    __Parallel_Task = OceanTask(mode=RunningMode.Parallel)
    __Concurrent_Task = OceanTask(mode=RunningMode.Concurrent)
    __Greenlet_Task = OceanTask(mode=RunningMode.GreenThread)
    __Async_Task = OceanTask(mode=RunningMode.Asynchronous)

    @pytest.fixture
    def ocean_task(self):
        return TestingTargetFunction()


    def test_get_function(self, ocean_task):
        pass


    def test_set_function(self, ocean_task):
        pass


    def test_get_func_args(self, ocean_task):
        pass


    def test_set_func_args(self, ocean_task):
        pass


    def test_get_func_kwargs(self, ocean_task):
        pass


    def test_set_func_kwargs(self, ocean_task):
        pass


    def test_get_initialization(self, ocean_task):
        pass


    def test_set_initialization(self, ocean_task):
        pass


    def test_get_init_args(self, ocean_task):
        pass


    def test_set_init_args(self, ocean_task):
        pass


    def test_get_init_kwargs(self, ocean_task):
        pass


    def test_set_init_kwargs(self, ocean_task):
        pass


    def test_get_group(self, ocean_task):
        pass


    def test_set_group(self, ocean_task):
        pass


    def test_get_done_handler(self, ocean_task):
        pass


    def test_set_done_handler(self, ocean_task):
        pass


    def test_get_error_handler(self, ocean_task):
        pass


    def test_set_error_handler(self, ocean_task):
        pass


    def test_get_running_timeout(self, ocean_task):
        pass


    def test_set_running_timeout(self, ocean_task):
        pass



class TestQueueTask(QueueTaskTestCases):

    def test_get_name(self):
        pass

    def test_set_name(self):
        pass

    def test_get_queue_type(self):
        pass

    def test_set_queue_type(self):
        pass

    def test_get_value(self):
        pass

    def test_set_value(self):
        pass


