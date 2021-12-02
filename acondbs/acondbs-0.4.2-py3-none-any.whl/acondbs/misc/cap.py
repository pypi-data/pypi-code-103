"""Throttle function executions
"""
import threading
import functools
import queue
import time
from enum import Enum

##__________________________________________________________________||
class cap_exec_rate:
    """cap the execution rate of a function

    This class prevents a function from being executed too often. This
    class executes a function in another thread. Once it executes a
    function, it starts a timer. If the function is called again
    through this class while the timer is still running, this class
    does not execute the function immediately. Instead, this class
    executes the function after the timer goes off.

    The function might be called multiple times through this class
    while the timer is running. After the timer goes off, this class
    only executes the function once.

    Parameters
    ----------
    func : callable
        A function or any callable object to be executed not too often
    pause_time : float
        The length of time [second] to be waited after an execution of
        the `func` before the next execution. If the `func` is called
        through this class once or more times within this time length
        after an execution, it will be executed once after this time
        length passes.
    daemon : bool
        whether the thread which executes the function and sets the
        timer is daemonic. If `False`, the Python program doesn't exit
        until the thread ends; the method `end()` needs to be called;
        the function will be executed one last time if it has been
        called but not executed. If `True`, the thread can be abruptly
        stopped at the end of Python program; the function that has
        been called but not executed will not be executed.

    """
    def __init__(self, func, pause_time=1.0, daemon=False):
        self.func = func
        self.pause_time = pause_time
        self.daemon = daemon

        self.queue = queue.Queue()
        config = Config(func, self.queue, pause_time)
        self.machine = threading.Thread(
            target=state_machine, args=(config, ), daemon=daemon)
        self.machine.start()

    def __call__(self):
        """call the function

        The number of executions of the function is capped
        """
        self.queue.put(Message.FUNC_CALLED)

    def end(self):
        """end using this class

        The function will be executed immediately if it is waiting for
        the timer. This method returns after the function is executed
        and the thread joins.

        """
        self.queue.put(Message.EXIT)
        self.machine.join()

def state_machine(config):
    """the entry function to be executed in a thread
    """
    state = Active(config)
    while not state.end:
        state = state()

class Message(Enum):
    FUNC_CALLED = 1
    TIMER_GOES_OFF = 2
    EXIT = 3

class Config:
    """Configuration of the state
    """
    def __init__(self, func, queue, pause_time):
        self.func = func
        self.queue = queue
        self.pause_time = pause_time

##__________________________________________________________________||
class State:
    """The base class of the states
    """
    def __init__(self, config):
        self.config = config
    def __call__(self):
        message = self.config.queue.get()
        if message == Message.FUNC_CALLED:
            return self.func_called()
        elif message == Message.TIMER_GOES_OFF:
            return self.timer_goes_off()
        elif message == Message.EXIT:
            return self.exit_()
        else:
            raise ValueError('unknown message: {!r}'.format(message))

class Active(State):
    """Active state

    The timer is not running. The function can be executed immediately
    if it is called.
    """
    end = False
    def __init__(self, config):
        super().__init__(config)
    def func_called(self):
        self.config.func()
        return Pause(self.config)
    def exit_(self):
        return Exit(self.config)

def timer_end(queue):
    queue.put(Message.TIMER_GOES_OFF)

class Pause(State):
    """Pause state. The function has not been called

    The timer is running. The function has not been called. It won't
    be executed immediately when it is called.
    """
    end = False
    def __init__(self, config):
        super().__init__(config)
        self.timer = threading.Timer(
            self.config.pause_time,
            functools.partial(timer_end, self.config.queue))
        self.timer.start()
    def func_called(self):
        return PauseCalled(self.config, self.timer)
    def timer_goes_off(self):
        return Active(self.config)
    def exit_(self):
        self.timer.cancel()
        return Exit(self.config)

class PauseCalled(State):
    """Pause state. The function has been called

    The timer is running. The function has been called. The function
    won't be executed until the timer goes off.
    """
    end = False
    def __init__(self, config, timer):
        super().__init__(config)
        self.timer = timer
    def func_called(self):
        return self
    def timer_goes_off(self):
        self.config.func()
        return Pause(self.config)
    def exit_(self):
        self.timer.cancel()
        self.config.func()
        return Exit(self.config)

class Exit(State):
    """Exit state
    """
    end = True
    def __init__(self, config):
        super().__init__(config)

##__________________________________________________________________||
