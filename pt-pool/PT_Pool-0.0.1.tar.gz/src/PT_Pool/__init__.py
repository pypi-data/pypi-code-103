from .PT_Pool import PT_Pool
import time

def f(x):
    time.sleep(1)
    return x*x

def on_result(res):
    print(res)

pt_pool = PT_Pool(threads_limit = 100)

pt_pool.apply_async(f, range(10), on_result=on_result)

time.sleep(2)
input('Press enter to exit...')
