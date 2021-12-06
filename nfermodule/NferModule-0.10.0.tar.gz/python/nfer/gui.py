from multiprocessing import Process, Queue, Lock
from queue import Empty
from nfer.nfer import globcallbacks
from signal import signal, SIGTERM
import atexit
from aiohttp import web
import asyncio
import socketio
import logging
import os
import webbrowser


MIN_DURATION = 0
UPDATE_PERIOD_MS = 200
log = logging.getLogger('nfer')

# IPC queue for handling interval output
gui_queue = Queue(0)
connected = Lock()
gui_proc = None

# initial parameters for the gui
display_intervals = []
display_tooltips = []

############# set up AIOHTTP webserver #############
sio = socketio.AsyncServer(async_mode='aiohttp')
app = web.Application()
sio.attach(app)

# get the directories for serving files
current_directory = os.path.dirname(os.path.abspath(__file__))
static_directory = os.path.join(current_directory, 'static')
www_directory = os.path.join(current_directory, 'www')

# configure static files
app.add_routes([web.static('/static', static_directory), 
                web.static('/', www_directory, show_index=True)])

##################################################

@sio.on("init")
def handle_connection(sid, data):
    #print("received json: " + str(data))
    # set the connected variable so the gui method will return
    global connected
    connected.release()
    # return configuration
    return {'intervals':display_intervals, 'tooltips':display_tooltips}

def subscriber(interval):
    # try only outputting intervals with long enough duration
    if interval.end - interval.begin > MIN_DURATION:
        gui_queue.put({'name':interval.name, 'start':interval.begin, 'end':interval.end, 'data':interval.data})

async def emit_queue():
    period = UPDATE_PERIOD_MS / 1000
    batch = []
    # wait for a cancel signal from asyncio
    try:
        # loop forever (until cancelled)
        while True:
            # get all the current items in the queue (this could be problematic if they are coming very quickly...)
            while True:
                try:
                    interval = gui_queue.get_nowait()
                except Empty:
                    break
                else:
                    batch.append(interval)
                    # if this was the standard threading queue, we'd need to call task_done()

            # emit the batch
            await sio.emit('batch', batch)
            batch.clear()
            # enqueue the next round
            await asyncio.sleep(period)
    except asyncio.CancelledError:
        pass
    # finally:
        # consider adding a finally here to shut anything down we need


async def start_background_tasks(app):
    app['queue_emitter'] = asyncio.create_task(emit_queue())

async def cleanup_background_tasks(app):
    app['queue_emitter'].cancel()
    await app['queue_emitter']

def run_nfer_gui(intervals, tooltips, port=5000):
    # lots of globals in this - consider wrapping in an object
    global display_intervals, display_tooltips
    # , srv, loop

    # set the initial arguments
    display_intervals = intervals
    display_tooltips = tooltips


    # AIOHTTP has a clean way to add other asyncio tasks to the event loop
    # You just need to register the task with AIOHTTP to start and stop alongside it
    app.on_startup.append(start_background_tasks)
    app.on_cleanup.append(cleanup_background_tasks)
    web.run_app(app, port=port)


def shutdown_nfer_gui():
    global gui_proc
    log.debug('nfer gui process: called shutdown!')
    gui_proc.terminate()
    gui_proc.join()
    log.debug('nfer guid process: joined!')

def gui(intervals, tooltips=['args'], port=5000, wait=True, browser=True):
    global gui_proc
    # add callbacks for all the intervals to monitor
    # for name in intervals:
    #     if name not in callbacks:
    #         callbacks[name] = []
    #     callbacks[name].append(subscriber)
    globcallbacks.append(subscriber)
    # get the lock so we can wait in this process for the client to connect to the web server
    connected.acquire()

    # add a handler so we can tell when the main process exits
    atexit.register(shutdown_nfer_gui)

    # start the web server in a subprocess
    gui_proc = Process(name='nfer.gui', target=run_nfer_gui, kwargs={'intervals':intervals,'tooltips':tooltips,'port':port})
    gui_proc.start()

    # if we are to open a web browser window, do so
    webbrowser.open('http://localhost:%d/index.html' % port)

    # if we are to wait, pause execution until the client connects
    if wait:
        log.info('nfer console is waiting for a connection on http://localhost:%d' % port)
        connected.acquire()
