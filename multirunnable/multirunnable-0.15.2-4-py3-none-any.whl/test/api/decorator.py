import pathlib
import inspect
import random
import sys

package_pyocean_path = str(pathlib.Path(__file__).parent.parent.parent.absolute())
sys.path.append(package_pyocean_path)

from multirunnable.api.decorator import ReTryMechanism, retry, Lock

from abc import ABCMeta, abstractmethod
import pytest
import re



class RetryTestCase(metaclass=ABCMeta):

    @abstractmethod
    def test_retry(self, function_collection):
        pass


    @abstractmethod
    def test_async_retry(self, function_collection):
        pass



class TargetFunctionComponent:

    @classmethod
    def initial_function(cls, *args, **kwargs):
        print(f"args: {args}")
        print(f"kwargs: {kwargs}")
        print("For testing initial process.")


    @classmethod
    def done_function(cls, result):
        print(f"result: {result}")
        print("For testing done-handling process.")
        return result


    @classmethod
    def error_function(cls, e: Exception):
        print(f"e: {e}")
        print("For testing error-handling process.")



class TargetFunction:

    Running_Timeout = 5

    def __init__(self):
        """
        Note:
            Think a mechanism which could help you to configure these
            functions and it has a interface which rule the signature.
        """
        ReTryMechanism._initialization = TargetFunctionComponent.initial_function
        ReTryMechanism._done_handling = TargetFunctionComponent.done_function
        ReTryMechanism._error_handling = TargetFunctionComponent.error_function


    @ReTryMechanism.function
    def raise_error(self):
        print("It will raise exception ...")
        __count = 1
        raise TestCounterException(count=__count)


    @ReTryMechanism.function
    def raise_error_with_param(self, *args, **kwargs):
        print(f"args: {args}")
        print(f"kwargs: {kwargs}")
        print("It will raise exception ...")
        __count = 1
        raise TestCounterException(count=__count)


    @classmethod
    def raise_error_cls_fun(cls):
        print("It will raise exception with classmethod ...")
        raise Exception("For testing retry mechanism with class method.")


    @staticmethod
    def raise_error_stat_fun():
        print("It will raise exception with staticmethod ...")
        raise Exception("For testing retry mechanism with static method.")



class RetryTargetFunction:

    # @Retry
    @retry(timeout=3)
    def target_run(self):
        """
        <class 'function'>
        :return:
        """
        print(f"self is: {self}")
        self.__test_fun()
        print("It will raise exception ...")
        __count = 1
        raise TestCounterException()


    @Lock.run_with_lock
    def __test_fun(self):
        print("This is testing function.")


    @classmethod
    @retry(timeout=3)
    def target_run_clsm(cls, index: int):
        print(f"self is: {cls}")
        print(f"index is: {index}")
        cls.__test_cls_fun()
        print("It will raise exception ...")
        __count = 1
        raise TestCounterException()


    @classmethod
    def __test_cls_fun(cls):
        print("This is testing function.")


    @staticmethod
    @retry(timeout=3)
    def target_run_stcm():
        print("It will raise exception ...")
        __count = 1
        raise TestCounterException()


    @target_run.initialization
    def initial_function(self, *args, **kwargs):
        print(f"args: {args}")
        print(f"kwargs: {kwargs}")
        print("For testing initial process.")


    @target_run.done_handling
    def done_function(self, result):
        print(f"result: {result}")
        print("For testing done-handling process.")
        return result


    @target_run.error_handling
    def error_function(self, e: Exception):
        print(f"e: {e}")
        print("For testing error-handling process.")



class TestCounterException(Exception):

    count = 0

    def __call__(self, *args, **kwargs):
        self.count += 1

    def __str__(self):
        return f"For testing retry mechanism and check the count is {self.count}"



class TestRetryMechanism(RetryTestCase):

    @pytest.fixture
    def function_collection(self):
        return TargetFunction()


    def test_retry(self, function_collection):
        function_collection.raise_error()


    def test_async_retry(self, function_collection):
        pass



if __name__ == '__main__':

    # # # # General function (In Python, it means bounded function)
    # tf = TargetFunction()
    # tf.raise_error()

    # t = RetryTargetFunction.target_run
    # print(t.__module__.__class__.__dict__["target_run"])

    rtf = RetryTargetFunction()
    result = rtf.target_run()
    print(f"[Final] {result}")
    print(f"[Final] type: {type(result)}")

    # result = ReTry(rtf.target_run)()
    # # result = ReTry(timeout=3)(rtf.target_run)()
    # print(f"[Final] {result}")
    # print(f"[Final] type: {type(result)}")

    result = rtf.target_run_clsm(index=random.randrange(1, 1000))
    print(f"[Final] {result}")
    print(f"[Final] type: {type(result)}")

    # result = rtf.target_run_stcm()
    # print(f"[Final] {result}")
    # print(f"[Final] type: {type(result)}")


    # # # # Class Method function
    # TargetFunction.raise_error_cls_fun()

    # # # # Static Method function
    # TargetFunction.raise_error_stat_fun()

