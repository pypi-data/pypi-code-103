import time
from threading import Thread
from typing import List

class Dionysos:
    def __init__(self, success: str="✔", error: str="✖", success_color: str="\033[32m", error_color: str="\033[31m", loader_color: str="\033[94m", loader: List[str]=["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"], success_message: str="", error_message: str="") -> None:
        self.__status = 0
        self.loader = loader
        self.loader_color = loader_color
        self.success = success
        self.success_color = success_color
        self.error = error
        self.error_color = error_color
        self.success_message = success_message
        self.error_message = error_message

    def apply(self, success: str=None, error: str=None, success_color: str=None, error_color: str=None, loader_color: str=None, loader: List[str]=None, success_message: str=None, error_message: str=None):
        def deco(func):
            def inner(*args, **kwargs):
                self.__status = 0
                self._loader = loader if loader else self.loader
                self._loader_color = loader_color if loader_color else self.loader_color
                self._success = success if success else self.success
                self._success_color = success_color if success_color else self.success_color
                self._error = error if error else self.error
                self._error_color = error_color if error_color else self.error_color
                self._success_message = success_message if success_message else self.success_message

                thread = Thread(target=self.__print_test)
                thread.start()
                try:
                    func(*args, **kwargs)
                    self.__status = 1
                    thread.join()
                    self.__status = 0
                except Exception as err:
                    self._error_message = error_message if error_message else str(err)
                    self.__status = 2
                    thread.join()
                    self.__status = 0
                    raise err
            return inner
        return deco

    def __print_test(self):
        i = 0
        while self.__status == 0:
            print(self._loader_color + self._loader[i], end="\r")
            i = (i+1 if i + 1 < len(self._loader) else 0)
            time.sleep(0.085)

        print(self._success_color + self._success, self._success_message + "\033[0m") if self.__status == 1 else print(self._error_color + self._error, self._error_message + "\033[0m")