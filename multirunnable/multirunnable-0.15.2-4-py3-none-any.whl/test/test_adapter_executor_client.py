import os

DEVELOPMENT_MODE = os.getenv("DEVELOPMENT_MODE", True)

if DEVELOPMENT_MODE:
    # Import package multirunnable
    import pathlib
    import sys
    package_path = str(pathlib.Path(__file__).absolute().parent.parent.parent.parent)
    print("[CHECK] package_path: ", package_path)
    sys.path.append(package_path)

# multirunnable package
from multirunnable import RunningMode, sleep, set_mode
from multirunnable.executor import AdapterExecutor
from multirunnable.parallel import ProcessStrategy
from multirunnable.concurrent import ThreadStrategy
from multirunnable.coroutine import GreenThreadStrategy, AsynchronousStrategy
import multiprocessing



class ExampleTargetFunction:

    def target_function(self, *args, **kwargs) -> str:
        print("This is ExampleTargetFunction.target_function.")
        sleep(3)
        print("This is target function args: ", args)
        print("This is target function kwargs: ", kwargs)
        # raise Exception("Test for error")
        return "You are 87."



class ExampleAdapterExecutor:

    __Executor_Number = 0

    __example = ExampleTargetFunction()

    def __init__(self, executors: int):
        self.__Executor_Number = executors


    def main_run(self):
        # # # # Initial Executor object
        set_mode(RunningMode.Parallel)
        print("Open executor: ", self.__Executor_Number)
        strategy = ProcessStrategy(executors=self.__Executor_Number)
        args = ("index_1", "index_2.2")
        workers = strategy.generate_worker(self.__example.target_function, *args)
        strategy.activate_workers(workers)
        strategy.close(workers)



if __name__ == '__main__':

    print("This is executor client: ")
    __executor_number = 3
    o_executor = ExampleAdapterExecutor(executors=__executor_number)
    o_executor.main_run()

