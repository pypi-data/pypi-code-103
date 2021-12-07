
import multiprocessing as mp
from concurrent.futures import ThreadPoolExecutor
import math
from functools import partial
from threading import Thread
import time
import logging
# import psutil

class PT_Pool:
    def __init__(self, threads_limit=100):
        self.worker_thread = Thread(target=self.worker, daemon=True, args=[threads_limit])
        self.worker_thread.start()
        self.on_results = {}
        self.task_queues = []


    def worker(self, threads_limit):
        self.procs = []
        procs_count = mp.cpu_count()
        threads_pp = math.ceil( threads_limit / procs_count ) # threads per process
        self.task_queues = [mp.JoinableQueue() for _ in range(procs_count)] # multiple queues for the sake of even distribution
        self.result_queue = mp.Queue() # will allow calling "on_result" from the same process which is important
        for i in range(procs_count):
            p = mp.Process(target=self.process, args=[i, threads_pp, self.task_queues[i], self.result_queue]) 
            self.procs.append(p)

        for p in self.procs:
            p.start()

        while True:
            id_ , res = self.result_queue.get()
            on_result = self.on_results.get(id_, None)
            if not on_result:
                logging.error(f'{__class__.__name__} worker id={id_} wasn\'t found on self.on_results.')
                logging.debug(self.on_results)
                continue

            try:
                on_result(res)
            except Exception as e:
                logging.error(f'{__class__.__name__} worker on_result={on_result.__name__} res={res}  resulted in exception:')
                logging.error(e)


    def apply_async(self, f, *all_args, on_result=(lambda:None)):
        assert callable(on_result), 'supplied on_result is not callable'
        if not self.task_queues:
            logging.warning(f'{__class__.__name__} apply_async self.tasks_queues is empty, waiting for initialization...')
            while not self.task_queues:
                time.sleep(0.001)
            logging.warning(f'{__class__.__name__} apply_async self.tasks_queues got initialized.')

        task_queue = sorted( self.task_queues, key=lambda q: q.qsize() )[0]
        id_ = id(on_result)
        self.on_results[id_] = on_result
        task_queue.put((f, all_args, id_))

        # on_result can't be passed through task queue and back because 
        # lock objects are not serializable, on_result should be given 
        # unique id_ and once the result arrives the correct on_result 
        # should be identified and called 
        

    def process(self, proc_id, threads_count, task_queue, result_queue):
        futures = []
        def on_completed(future, id_):
            res = future.result()
            result_queue.put((id_, res))
        with ThreadPoolExecutor(max_workers=threads_count) as executor:
            while True:
                f, all_args, id_ = task_queue.get()
                task_queue.task_done()
                if f == None:
                    break
                for args in zip(*all_args):
                    future = executor.submit(f, *args)
                    future.add_done_callback(partial(on_completed, id_=id_))
        # print('end proc id', proc_id, ' cpu core=', psutil.Process().cpu_num())

    # def terminate(self):
    #     for p in self.procs:
    #         p.terminate()
    #     # procsss can use: start(), join(), is_alive(), terminate(), kill()

#if __name__ == '__main__':
#    import time
#
#    def f(x):
#        time.sleep(1)
#        return x*x
#
#    def on_result(res):
#        print(res)
#
#    pt_pool = PT_Pool(threads_limit = 100)
#    pt_pool.apply_async(f, range(10), on_result=on_result)
#    time.sleep(2)
#    input('Press enter to exit...')


