#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 7 23:47:19 2021

MultiVuClient.py is a module for use on a network that has access to a
computer running MultiVuServer.py.  By running this client, a python script
can be used to control a Quantum Desing cryostat.

@author: D. Jackson
"""

import sys
from typing import Tuple, Dict
import socket
import selectors
from enum import IntEnum
import traceback
import time
from threading import Thread, Lock


from .SocketMessageClient import ClientMessage
from .instrument import MultiVuExeException, InstrumentList
from .CommandTemperature import CommandTemperature
from .CommandField import CommandField
from .CommandChamber import CommandChamber
from .create_logger import log
from .project_vars import (TIMEOUT_LENGTH,
                           CLIENT_NAME,
                           HOST,
                           PORT,
                           )

if sys.platform == 'win32':
    try:
        import msvcrt    # Used to help detect the esc-key
    except ImportError:
        print("Must import the pywin32 module.  Use:  ")
        print("\tconda install -c conda-forge pywin32")
        print("   or")
        print("\tpip install pywin32")
        sys.exit(0)


class MultiVuClient():
    def __init__(self,
                 host: str = HOST,
                 port: int = PORT,
                 socket_io_timeout: int = TIMEOUT_LENGTH
                 ):
        '''
        This class is used for a client to connect to a computer with
        MutliVu running MultiVuServer.py

        Parameters
        ----------
        socket_io_timeout : float, optional
            Time in seconds before the client will give up in communicating
            with the server. The default is None.

        '''
        self._addr = (host, port)
        self._sel = selectors.DefaultSelector()
        self._socketIoTimeout = socket_io_timeout
        self._message = None     # ClientMessage object
        self.sock = None
        self.response = None
        self.temperature = CommandTemperature(None)
        self.field = CommandField(None)
        self.chamber = CommandChamber(None)
        self._thread_running = False

        class Subsystem(IntEnum):
            no_subsystem = 0
            temperature = 1
            field = 2
            chamber = 4
        self.subsystem = Subsystem

        # variables to hold the set points and status info
        self._set_pointT = 300
        self._set_pointH = 0
        self._set_chamb = 0

        # Configure logging
        # TODO - Determine from querying the server if using
        # threading or not.  That would require moving
        # this into the __enter__() method.
        self.log_event = log()
        self.logger = self.log_event.create(CLIENT_NAME,
                                            display_logger_name=True,
                                            )

    def __enter__(self):
        self.logger.info(f'Starting connection to {self._addr}')
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setblocking(False)
        self.sock.connect_ex(self._addr)

        self._message = ClientMessage(self._sel,
                                      self.sock,
                                      )
        # send a request to the sever to confirm a connection
        max_tries = 3
        action = 'START'
        for attempt in range(max_tries):
            try:
                self.response = self._send_and_receive(action)
            except OSError as e:
                msg = f'Attempt {attempt + 1} of {max_tries} failed:  {e}'
                self.logger.info(msg)
                time.sleep(1)
                if attempt == max_tries - 1:
                    err_msg = 'Failed to make a connection to the '
                    err_msg += 'server.  Check if the MultiVuServer '
                    err_msg += 'is running.'
                    self.logger.info(err_msg)
                    sys.exit(0)
            else:
                self.logger.info(self.response['result'])
                break

        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        exit_without_error = False
        # Error handling
        if isinstance(exc_value, SystemExit):
            exit_without_error = True
        if isinstance(exc_value, KeyboardInterrupt):
            self.logger.info('')
            self.logger.info('Caught keyboard interrupt, exiting')
            exit_without_error = True
        elif isinstance(exc_value, ConnectionAbortedError):
            msg = 'Shutting down the server.'
            self.logger.info(msg)
            exit_without_error = True
        elif isinstance(exc_value, ConnectionError):
            # Note that ConnectionAbortedError and ConnectionRefusedError
            # are subclasses of ConnectionError
            exit_without_error = True
        elif isinstance(exc_value, MultiVuExeException):
            # Connection closed by the server
            self.logger.info(traceback.format_exc())
            exit_without_error = False
        elif isinstance(exc_value, Exception):
            msg = 'MultiVuClient: error: exception for '
            msg += f'{self._message.addr}:\n'
            msg += f'{traceback.format_exc()}'
            self.logger.info(msg)
            exit_without_error = False
        else:
            try:
                self.response = self._send_and_receive('CLOSE')
            except ConnectionError:
                exit_without_error = True

        # Close things up for all cases
        self._thread_running = False
        if self._message is not None:
            self._message.shutdown()
        self.sock.close()
        time.sleep(1)
        self.log_event.remove()
        return exit_without_error

    ###########################
    #  Private Methods
    ###########################

    def _send_and_receive(self, action: str, query: str = '') -> Dict[str, str]:
        '''
        This takes an action and a query, and sends it to
        ._monitor_and_get_response() to let that method figure out what
        to do with the information.

        Parameters
        ----------
        action : str
            The general command going to MultiVu:  TEMP(?), FIELD(?), and
            CHAMBER(?).  If one wants to know the value of the action, then
            it ends with a question mark.  If one wants to set the action in
            order for it to do something, then it does not end with a question
            mark.
        query : str, optional
            The query gives the specifics of the command going to MultiVu.  For
            queries. The default is '', which is what is used when the action
            parameter ends with a question mark.

        Returns
        -------
        self.response : dict()
            The response dictionary from the ClientMessage class.

        '''
        self._message.create_request(action, query)
        self.response = self._monitor_and_get_response()
        if self.response is None:
            msg = 'MultiVuError:  No return value, which could mean that '
            msg += 'MultiVu is not running or that the connection has '
            msg += 'been closed.'
            self.logger.info(msg)
            raise MultiVuExeException(msg)
        return self.response

    def _monitor_and_get_response(self) -> Dict[str, str]:
        '''
        This monitors the traffic going on.  It asks the SocketMessageClient
        class for help in understanding the data.  This is also used to handle
        the possible errors that SocketMessageClient could generate.

        Raises
        ------
        ConnectionRefusedError
            Could be raised if the server is not running.
        ConnectionError
            Could be raised if there are connection issues with the server.
        KeyboardInterrupt
            This is used by the user to close the connection.
        MultiVuExeException
            Raised if there are issues with the request for MultiVu commands.

        Returns
        -------
        TYPE
            The information retrived from the socket and interpreted by
            SocketMessageClient class.

        '''
        while True:
            events = self._sel.select(timeout=self._socketIoTimeout)
            if events:
                for key, mask in events:
                    message = key.data
                    try:
                        message.process_events(mask)
                    except ConnectionAbortedError as e:
                        # Client closed the server
                        raise ConnectionAbortedError from e
                    except ConnectionError as e:
                        # Client closed the client
                        raise ConnectionError from e
                    except Exception:
                        self._close_and_exit()
                    else:
                        # Windows looks for the ESC key to quit.
                        if sys.platform == 'win32':
                            escKey = chr(27)
                            if (msvcrt.kbhit()
                                    and msvcrt.getch().decode() == escKey):
                                self._thread_running = False
                                raise KeyboardInterrupt
                        # return the response
                        self.response = message.response
                        if (self.response is not None
                                and message.request is None):
                            rslt = self.response['result']
                            if rslt.startswith('MultiVuError:'):
                                self.logger.info(self.response['result'])
                                message.close()
                                raise MultiVuExeException(rslt)
                            else:
                                return self.response
            else:
                # An empty list means the selector timed out
                msg = 'Socket timed out after '
                msg += f'{self._socketIoTimeout} seconds.'
                raise TimeoutError(msg)
            # Check for a socket being monitored to continue.
            if not self._sel.get_map():
                break

    def _monitor_temp_stability(self, timeout_sec, mutex):
        '''
        This private method is used to monitor the temperature. It waits for
        the status to become not 'stable,' and then waits again for the status
        to become 'stable.'

        Parameters
        ----------
        timeout_sec : float
            This is the timeout set by the user for when the temperature
            monitoring will quit, even if the temperature is not stable.
        mutex : threading.Lock
            The mutex lock.

        Returns
        -------
        None.

        '''
        start = time.time()
        mutex.acquire()
        t, status = self.get_temperature()
        mutex.release()
        max_time_to_start = 5.0
        while status == 'Stable':
            time.sleep(0.3)
            mutex.acquire()
            t, status = self.get_temperature()
            mutex.release()
            measure_time = time.time()
            if measure_time - start > max_time_to_start:
                break
            if timeout_sec > 0:
                if measure_time - start > timeout_sec:
                    return
            # check if the main thread has killed this process
            if not self._thread_running:
                return

        while status != 'Stable':
            time.sleep(0.3)
            mutex.acquire()
            t, status = self.get_temperature()
            mutex.release()
            if timeout_sec > 0:
                if time.time() - start > timeout_sec:
                    return
            # check if the main thread has killed this process
            if not self._thread_running:
                return

    def _monitor_field_stability(self, timeout_sec, mutex):
        '''
        This private method is used to monitor the magnetic field. It waits for
        the status to start with 'Holding,' and then waits again for the status
        to not start with 'Holding.'

        Parameters
        ----------
        timeout_sec : float
            This is the timeout set by the user for when the field
            monitoring will quit, even if the field is not stable.
        mutex : threading.Lock
            The mutex lock.

        Returns
        -------
        None.

        '''
        start = time.time()
        mutex.acquire()
        f, status = self.get_field()
        mutex.release()
        max_time_to_start = 5.0
        while status.startswith('Holding'):
            time.sleep(0.3)
            mutex.acquire()
            f, status = self.get_field()
            mutex.release()
            measure_time = time.time()
            if measure_time - start > max_time_to_start:
                return
            if timeout_sec > 0:
                if measure_time - start > timeout_sec:
                    return
            # check if the main thread has killed this process
            if not self._thread_running:
                return

        while not status.startswith('Holding'):
            time.sleep(0.3)
            mutex.acquire()
            f, status = self.get_field()
            mutex.release()
            if timeout_sec > 0:
                if time.time() - start > timeout_sec:
                    return
            # check if the main thread has killed this process
            if not self._thread_running:
                return

    def _monitor_chamber_stability(self, timeout_sec, mutex):
        start = time.time()
        mutex.acquire()
        mode = self.get_chamber()
        mutex.release()

        while not self.chamber.mode_setting_correct(self._set_chamb, mode):
            time.sleep(0.3)
            mutex.acquire()
            mode = self.get_chamber()
            mutex.release()
            if timeout_sec > 0:
                if time.time() - start > timeout_sec:
                    return
            # check if the main thread has killed this process
            if not self._thread_running:
                return

    def _close_and_exit(self):
        err_info = sys.exc_info()
        dont_show_traceback = self.__exit__(err_info[0],
                                            err_info[1],
                                            err_info[2])
        if not dont_show_traceback:
            self.logger.info(traceback.format_exc())

    ###########################
    #  Public Methods
    ###########################

    def open(self):
        '''
        This is the entry point into the MultiVuClient.  It connects to
        a running MultiVuServer

        Parameters
        ----------
        host : str
            The host IP address.  If the server is running on the same
            computer, it is should be 'localhost.'  The host must match
            the IP address of the server.
        port : int
            The port must match the port number for the Server, which is 5000.

        Raises
        ------
        ConnectionRefusedError
            This is raised if there is a problem connecting to the server. The
            most common issue is that the server is not running.

        Returns
        -------
        None.

        '''
        self.__enter__()

    def close_client(self):
        '''
        This command closes the client, but keeps the server running
        '''
        self._close_and_exit()

    def close_server(self):
        '''
        This command closes the server
        '''
        try:
            self.response = self._send_and_receive('EXIT')
        except ConnectionAbortedError:
            self._close_and_exit()
        except ConnectionError:
            print('Error:')
            err_info = sys.exc_info()
            traceback.print_tb(err_info[2], limit=1)
            msg = 'No connection to the server.  Is the client connected?'
            print(msg)
            self._close_and_exit()

    def get_temperature(self) -> Tuple[float, str]:
        '''
        This gets the current temperature, in Kelvin, from MultiVu.

        Returns
        -------
        A tuple of (temperature, status).

        '''
        self.response = self._send_and_receive('TEMP?', '')
        temperature, status = self.temperature.convert_result(self.response)
        return temperature, status

    def set_temperature(self,
                        set_point: float,
                        rate_per_min: float,
                        approach_mode: IntEnum
                        ):
        '''
        This sets the temperature.

        Parameters
        ----------
        set_point : float
            The desired temperature, in Kelvin.
        rate_per_min : float
            The rate of change of the temperature in K/min
        approach_mode : IntEnum
            This uses the MultiVuClient.temperature.approach_mode enum.
            Options are:
                .temperature.approach_mode.fast_settle
                .temperature.approach_mode.no_overshoot

        Returns
        -------
        None.

        '''
        try:
            query = self.temperature.prepare_query(set_point,
                                                   rate_per_min,
                                                   approach_mode,
                                                   )
            self._set_pointT = set_point
        except ValueError as e:
            self.logger.info(e.message)
            raise ValueError
        else:
            self._send_and_receive('TEMP', query)

    def get_field(self) -> Tuple[float, str]:
        '''
        This gets the current field, in Oe, from MultiVu.

        Returns
        -------
        A tuple of (field, status)

        '''
        self.response = self._send_and_receive('FIELD?', '')
        field, status = self.field.convert_result(self.response)
        return field, status

    def set_field(self,
                  set_point: float,
                  rate_per_sec: float,
                  approach_mode: IntEnum,
                  driven_mode=None,
                  ):
        '''
        This sets the magnetic field.

        Parameters
        ----------
        set_point : float
            The desired magnetic field, in Oe.
        rate_per_sec : float
            The ramp rate, in Oe/sec.
        approach_mode : IntEnum
            This uses the MultiVuClient.field.approach_mode enum.  Options are:
                MultiVuClient.field.approach_mode.linear
                MultiVuClient.field.approach_mode.no_overshoot
                MultiVuClient.field.approach_mode.oscillate
        driven_mode : IntEnum, Only used for PPMS
            This uses the MultiVuClient.field.DrivenMode, and is only used
            by the PPMS, for which the options are:
                MultiVuClient.field.DrivenMode.Persistent
                MultiVuClient.field.DrivenMode.Driven

        Raises
        ------
        ValueError
            Thrown if the set_point and rate_per_sec are not numbers.

        Returns
        -------
        None.

        '''
        try:
            query = self.field.prepare_query(set_point,
                                             rate_per_sec,
                                             approach_mode,
                                             driven_mode)
            self._set_pointH = set_point
        except ValueError as e:
            self.logger.info(e.message)
            raise ValueError
        else:
            self._send_and_receive('FIELD', query)

    def get_chamber(self) -> str:
        '''
        This gets the current chamber setting.

        Returns
        -------
        str
            The chamber status.

        '''
        self.response = self._send_and_receive('CHAMBER?', '')
        status = self.chamber.convert_result(self.response)
        return status

    def set_chamber(self, mode: IntEnum):
        '''
        This sets the chamber status.

        Parameters
        ----------
        mode : IntEnum
            The chamber is set using the MultiVuClient.chamber.Mode enum.
            Options are:
            MultiVuClient.chamber.mode.seal
            MultiVuClient.chamber.mode.purge_seal
            MultiVuClient.chamber.mode.vent_seal
            MultiVuClient.chamber.mode.pump_continuous
            MultiVuClient.chamber.mode.vent_continuous
            MultiVuClient.chamber.mode.high_vacuum

        Raises
        ------
        MultiVuExeException

        Returns
        -------
        None.

        '''
        if self._message.mvu_flavor == InstrumentList.OPTICOOL.name:
            err_msg = 'set_chamber is not available for the OptiCool'
            raise MultiVuExeException(err_msg)
        try:
            query = self.chamber.prepare_query(mode)
        except ValueError as e:
            self.logger.info(e.message)
            raise ValueError
        else:
            self._set_chamb = mode
            self._send_and_receive('CHAMBER', query)

    def wait_for(self, delay_sec, timeout_sec=0, bitmask=0):
        '''
        This command pauses the code until the specified criteria are met.

        Parameters
        ----------
        delay_sec : float
            Time in seconds to wait after stability is reached.
        timeout_sec : float, optional
            If stability is not reached within timeout (in seconds), the
            wait is abandoned. The default timeout is 0, whih indicates this
            feature is turned off (i.e., to wait forever for stability).
        bitmask : int, optional
            This tells wait_for which parameters to wait on.  The best way
            to set this parameter is to use the MultiVuClient.subsystem enum,
            using bitewise or to wait for multiple paramets.  For example,
            to wait for the temperature and field to stabalize, one would set
            bitmask = (MultiVuClient.subsystem.temperature
                       | MultiVuClient.subsystem.field).
            The default is MultiVuClient.no_subsystem (which is 0).

        '''
        max_mask = self.subsystem.temperature | self.subsystem.field
        if self._message.mvu_flavor != InstrumentList.OPTICOOL:
            max_mask = max_mask | self.subsystem.chamber
        if bitmask > max_mask:
            err_msg = f'The mask, {bitmask}, is out of bounds.  Must be '
            err_msg += 'one of the following'
            for s in self.subsystem:
                if (self._message.mvu_flavor != InstrumentList.OPTICOOL
                        and s is not self.subsystem.chamber):
                    err_msg += f'\n\t{s.name}: {s.value}'
            raise MultiVuExeException(err_msg)

        mutex = Lock()
        threads = list()
        # stop any other threads
        self._thread_running = False
        if (bitmask & self.subsystem.temperature
                == self.subsystem.temperature):
            t = Thread(target=self._monitor_temp_stability,
                       args=(timeout_sec, mutex))
            threads.append(t)
            self._thread_running = True
            t.start()
        if bitmask & self.subsystem.field == self.subsystem.field:
            f = Thread(target=self._monitor_field_stability,
                       args=(timeout_sec, mutex))
            threads.append(f)
            self._thread_running = True
            f.start()
        if bitmask & self.subsystem.chamber == self.subsystem.chamber:
            c = Thread(target=self._monitor_chamber_stability,
                       args=(timeout_sec, mutex))
            threads.append(c)
            self._thread_running = True
            c.start()

        for thread in threads:
            thread.join()
        time.sleep(delay_sec)
