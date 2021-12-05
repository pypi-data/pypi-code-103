import threading
import time
from . import Logger

max_threads = 0
current_threads = 0


def target_wrapper(target, args=()):
    global current_threads, max_threads

    Logger.info(f'stats: {current_threads}/{max_threads} threads...')
    try:
        current_threads += 1
        Logger.info(f'Starting Thread #{current_threads}...')
        target(*args)
    except Exception as ex:
        Logger.info(f'Thread #{current_threads}: {ex}')
    finally:
        Logger.info(f'Thread #{current_threads} Finished...')
        current_threads -= 1


def start_thread(target, args=(), _daemon=False):
    global current_threads, max_threads

    t = threading.Thread(target=target_wrapper, args=(target, args), daemon=_daemon)

    if 0 < max_threads <= current_threads:
        Logger.info('Max Threads Limit Exceed, Waiting...')
        while 0 < max_threads <= current_threads:
            time.sleep(.1)

    Logger.info('Starting Thread...')
    t.start()
    return t


def start_daemon(target, args=()):
    Logger.info('Starting Daemon...')
    return start_thread(target=target, args=args, _daemon=True)


def target_persistent(target, args=()):
    Logger.info('Starting Persistent Thread...')
    while True:
        try:
            target(*args)
        except Exception as ex:
            Logger.info(f'Persistent Thread Exception: {ex}')
        finally:
            Logger.info('Restarting Persistent Thread...')


def start_persistent_daemon(target, args=()):
    Logger.info('Starting Persistent Daemon...')
    return start_daemon(target=target_persistent, args=(target, args))


def is_all_threads_done():
    return current_threads <= 0


def join():
    while not is_all_threads_done():
        time.sleep(.1)
