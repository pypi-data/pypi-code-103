"""
A unittest for pyocean.worker module
"""
import pathlib
import sys

package_pyocean_path = str(pathlib.Path(__file__).parent.parent.absolute())
print(package_pyocean_path)
sys.path.append(package_pyocean_path)

# from pyocean.manager import (
#     OceanManager, OceanSimpleManager, OceanPersistenceManager,
#     OceanAsyncWorker, OceanPersistenceAsyncManager)
from abc import ABCMeta, abstractmethod
# from unittest import TestCase



class TestWorkerFramework(metaclass=ABCMeta):

    @abstractmethod
    def test_init(self):
        pass


    @abstractmethod
    def test_initial_running_strategy(self):
        pass


    @abstractmethod
    def test_running_timeout(self):
        pass


    @abstractmethod
    def test_start(self):
        pass


    @abstractmethod
    def test_pre_activate(self):
        pass


    @abstractmethod
    def test_activate(self):
        pass


    @abstractmethod
    def test_run_task(self):
        pass


    @abstractmethod
    def test_pre_stop(self):
        pass


    @abstractmethod
    def test_post_stop(self):
        pass


    @abstractmethod
    def test_post_done(self):
        pass


    @abstractmethod
    def test_get_result(self):
        pass



class TestOceanWorker(TestWorkerFramework):
    pass



class TestSimpleWorker(TestOceanWorker):
    pass



class TestPersistenceWorker(TestOceanWorker):
    pass



class TestAsyncSimpleWorker(TestOceanWorker):
    pass



class TestAsyncPersistenceWorker(TestOceanWorker):
    pass



class TestSystem:
    pass


def test_fun():
    print("This is testing function.")


if __name__ == '__main__':

    from multirunnable import RunningMode
    from multirunnable.manager import OceanMapManager

    __manager = OceanMapManager(mode=RunningMode.Parallel)
    __manager.__generate_worker(function=test_fun)

