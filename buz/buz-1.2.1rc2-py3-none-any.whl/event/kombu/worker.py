from buz.event.kombu.execution_strategy import ExecutionStrategy


class Worker:
    def __init__(
        self,
        execution_strategy: ExecutionStrategy,
    ):
        self.__execution_strategy = execution_strategy

    def start(self) -> None:
        self.__execution_strategy.start()

    def stop(self) -> None:
        self.__execution_strategy.stop()
