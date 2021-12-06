import os
import zmq
import sys
import time
import nidaqmx
import logging
import zmq_tools
import multiprocessing as mp
from pyglui import ui
from time import sleep
from ctypes import c_bool
from plugin import Plugin
from background_helper import Task_Proxy, EarlyCancellationError

# Pupil integration not yet done, requires calling class from their own codebase

class Pupil(Glasses):

    """A child class of Glasses, which will contain functions just for calling
    the Pupil API.

    Arguments:
        Glasses {[type]} -- [description]
    """
    def __init__(self):
        super().__init__()


class BackgroundTick(Task_Proxy):
    def __init__(self, name, args=[], kwargs={}):
        
            # super().logger.info('Starting PyTick background thread')
            self._should_terminate_flag = mp.Value(c_bool, 0)
            
            pipe_parent, pipe_child = mp.Pipe(True)
            wrapper_args = super()._prepare_wrapper_args(
                pipe_child, self._should_terminate_flag
            )
            # wrapper_args.extend(args)
            self.process = mp.Process(
                target=self._wrapper, name=name, args=wrapper_args, kwargs=kwargs
            )
            self.process.daemon = True
            self.process.start()
            self.pipe = pipe_parent

        

        def _wrapper(self, pipe, _should_terminate_flag, *args, **kwargs):

            niTask = nidaqmx.Task()
            niTask.ao_channels.add_ao_voltage_chan('Dev1/ao1')

            def trigger(skipFirst=0, skipFactor=1):
                for _ in range(skipFirst + skipFactor + 1):
                    niTask.write([3.3], auto_start=True)
                    sleep(0.002)
                    niTask.write([0.0], auto_start=True)
                    sleep(0.001)

            while True:
                if pipe.poll(0):
                    recvStr = pipe.recv()
                    if recvStr == 'trigger':
                        try:
                            trigger(**kwargs)
                        except Exception as e:
                            pipe.send(e)
                            if not isinstance(e, EarlyCancellationError):
                                import traceback
                                # super().logger.info(traceback.format_exc())
                                pass
                            break
                    
                    elif recvStr == 'stopped':
                        break
                    else:
                        # super().logger.info('Invalid trigger received')
                        pass
            
            pipe.close()
            niTask.stop()
            print('NI Task Stopped')
            # super().logger.debug("Exiting _wrapper")

        def fetch(self):
            print('Fetched')

    

        def finish(self, timeout=1):
            if self.process is not None:
                self.process.join(timeout)
                self.process = None


class PyTick(Plugin):
    icon_chr = "'"
    icon_font="roboto"

    def __init__(self, g_pool, skipFactor=1, skipFirst=0):
        super().__init__(g_pool)

        self.uniqueness = "by_class"
        self.order = 1

        self.state = 'stopped'
        self.proxy = BackgroundTick(
        'BackgroundTick', kwargs={'skipFactor': skipFactor, 'skipFirst':skipFirst})
        self.skipFactor = skipFactor
        self.skipFirst = skipFirst

    def init_ui(self):
        self.add_menu()
        self.menu.label = 'PyTick'
        help_str = "PyTick"
        self.menu.append(ui.Info_Text(help_str))
        # self.menu.append(ui.Text_Input('skipFactor'), self, label='Skip Factor')
        # self.menu.append(ui.Text_Input('skipFirst'), self, label='Skip First')

    def deinit_ui(self):
        self.remove_menu()


    def get_init_dict(self):
        return {'skipFactor': self.skipFactor, 'skipFirst': self.skipFirst}
    
    def on_char(self, character):
        if character is 's':
            if self.state == 'stopped':
                self.state = 'started'
                self.proxy.pipe.send('trigger')
            else:
                self.state = 'stopped'
                self.proxy.pipe.send('trigger')

    def on_notify(self, notification):
        # print(notification['subject'])
        if (notification['subject'] == 'recording.should_start') and self.state == 'stopped':
            self.state = 'started'
            self.proxy.pipe.send('trigger')
        elif notification['subject'] == 'recording.should_stop' and self.state == 'started':
            self.state = 'stopped'
            self.proxy.pipe.send('trigger')
        else:
            print(notification['subject'])

    def fetch(self):
        print('Fetched')

    def finish(self, timeout=1):
        self.niTask.stop()
        if self.process is not None:
            self.process.join(timeout)
            self.process = None