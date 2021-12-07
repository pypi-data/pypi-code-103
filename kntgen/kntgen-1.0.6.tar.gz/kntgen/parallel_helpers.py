import math
from multiprocessing import Process, Queue

from kntgen.printer import error_printer

MAX_PROCESS = 50


def run_parallel_tasks(task_executor, tasks: list, *args, **kwargs):
    if not tasks:
        error_printer('Not found any task!')
        return

    def _split_to_section_tasks():
        total_section_task = max(MAX_PROCESS, len(tasks))
        task_per_section = math.ceil(len(tasks) / total_section_task)
        results = []
        for i in range(total_section_task):
            start = i * task_per_section
            end = (i + 1) * task_per_section
            if end >= len(tasks):
                end = None
            results.append(tasks[start:end])
            if end is None:
                break
        return results

    result_tasks = []
    mp = Multiprocessor()
    section_tasks = _split_to_section_tasks()
    for section_task in section_tasks:
        mp.run(_run_section_task, task_executor, section_task, *args, **kwargs)
    # Wait for all processes to finish
    result_section_tasks = mp.wait()
    for result_section_task in result_section_tasks:
        result_tasks.extend(result_section_task)
    return result_tasks


def _run_section_task(task_executor, section, *args, **kwargs):
    results = []
    for task in section:
        results.append(task_executor(task, *args, **kwargs))
    return results


class Multiprocessor:
    def __init__(self):
        self.processes = []
        self.queue = Queue()

    def run(self, func, *args, **kwargs):
        args2 = [func, self.queue, args, kwargs]
        p = Process(target=self._wrapper, args=args2)
        self.processes.append(p)
        p.start()

    def wait(self):
        rets = []
        for _ in self.processes:
            ret = self.queue.get()
            rets.append(ret)
        for p in self.processes:
            p.join()
        return rets

    @staticmethod
    def _wrapper(func, queue, args, kwargs):
        ret = func(*args, **kwargs)
        queue.put(ret)
