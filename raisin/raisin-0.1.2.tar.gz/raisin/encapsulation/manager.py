#!/usr/bin/env python3

"""
** Forms the packages. **
-------------------------

Allows to generate packages.
"""

import queue
import threading

from raisin.encapsulation.packaging import Argument, Function, Task
from raisin.communication.client import Client


__pdoc__ = {'TasksSharer.__enter__': True, 'TasksSharer.__exit__': True}


def make_tasks(functions, arguments):
    """
    ** Generates the tasks to be performed. **

    Parameters
    ----------
    functions : iterable
        Generator that assigns each function associated with each task.
        In the case of map, this iterator must yield the same function at each iteration.
    arguments : iterable
        Generator that assigns the set of arguments for each task. At each iteration
        the arguments must be provided via a tuple of size *n*, with *n* the number
        of arguments that the function associated with this task takes.

    Yields
    ------
    new_packages : list
        The list of packets to send for the proper functioning of the task.
        This list contains packets of type ``raisin.encapsulation.packaging.Function``
        or ``raisin.encapsulation.packaging.Argument``.
        This list does not contain packages that have already been assigned
        to a previous task, even if they are also needed for the current task.
    task : ``raisin.encapsulation.packaging.Task``
        The task to execute, which contains the address of the function and its arguments.

    Notes
    -----
    - There is no verification on the inputs, they must be verified by higher level functions.
    - For functions, the detection of redundancy is done from the address of the memory pointer.

    Examples
    --------
    >>> from itertools import cycle
    >>> from raisin.encapsulation.manager import make_tasks
    >>>
    >>> def f(x, y):
    ...     return x**2 + y**2
    ...
    >>> def pprint(job):
    ...    for new_packages, task in job:
    ...        print(f'new: {new_packages}, task: {task}')
    ...
    >>> pprint(make_tasks(cycle((f,)), [(1, 2), (2, 3)]))
    new: [Argument(1), Argument(2), Function(f)], task: Task()
    new: [Argument(3)], task: Task()
    >>>
    """

    def check_and_add(set_, element):
        if element in set_:
            return False
        set_.add(element)
        return True

    pointers2hashes = {}  # To each object address, associates its hash.
    args_hashes = set()  # The hash value of each argument.
    for func, args in zip(functions, arguments):
        new_args = [(a, Argument(a)) for a in args if id(a) not in pointers2hashes]
        pointers2hashes.update({id(p): hash(a) for p, a in new_args})
        new_args = [a for _, a in new_args if check_and_add(args_hashes, hash(a))]

        new_func = Function(func) if id(func) not in pointers2hashes else None
        if new_func is not None:
            pointers2hashes[id(func)] = hash(new_func)

        new_packages = new_args if new_func is None else new_args + [new_func]
        task = Task(
            func_hash=pointers2hashes[id(func)], arg_hashes=[pointers2hashes[id(a)] for a in args]
        )
        yield new_packages, task


class TasksSharer(threading.Thread):
    """
    ** Communicate packets with the local server. **

    Attributes
    ----------
    res_queue : Queue
        The FIFO queue which contains the result packets of type
        ``raisin.encapsulation.packaging.Result` in the order they arrive.

    Examples
    --------
    >>> from raisin.encapsulation.manager import make_tasks, TasksSharer
    >>>
    >>> def f(x): return x**2
    ...
    >>> tasks_generator = make_tasks((f,), ([2],))
    >>> with TasksSharer(tasks_generator) as tasks_sharer:
    ...     tasks_sharer.start()
    ...     tasks_sharer.join()
    ...
    >>>
    """

    def __init__(self, tasks_iterator):
        """
        Parameters
        ----------
        tasks_iterator : iterator
            Gives for each task, the list of packages of type
            ``raisin.encapsulation.packaging.Function``
            or ``raisin.encapsulation.packaging.Argument`` and also the task to execute
            (of type ``raisin.encapsulation.packaging.Task``). For example, the generator
            ``raisin.encapsulation.manager.make_tasks`` can do the job.

        Notes
        -----
        - There is no verification on the inputs, they must be verified by higher level functions.
        - You have to start the thread with the *start()* method to establish
            asynchronous communication with the server.
        """
        threading.Thread.__init__(self)
        self._tasks_iterator = tasks_iterator
        self.res_queue = queue.Queue()

    def __enter__(self):
        """
        ** Allows to cut the connection in case of error. **

        Instead of quitting the server without warning, this context
        manager allows you to quit the dialog cleanly.
        """
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """
        ** Stops and closes the dialog with the local server. **

        Goes together with ``TasksSharer.__enter__``.
        This is where you break the connection with the server.
        """
        return None

    def run(self):
        """
        ** Represents the thread activity. **

        This method is the first method that will be executed when the thread is launched.
        It must not be called directly. It is the call of the 'start' method which
        takes care in the background to launch this method.
        """
        # try:
        #     with Client(None, 20001) as client:
        #         client.start()
        #         for new_packages, task in self._tasks_iterator:
        #             # for new_package in new_packages:
        #             #     client.send_obj(new_package)
        #             # client.send_obj(task)
        #             pass
        # except ConnectionError as err:
        #     raise ConnectionError('please launch a listening server on port 20001') from err
