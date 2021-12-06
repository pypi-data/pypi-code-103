#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 7 23:47:19 2021

MultiVuServer.py is a module for use on a computer running MultiVu.  It can
be used with MultiVuClient.py to control a Quantum Desing cryostat.

@author: D. Jackson
"""

import sys
from typing import Tuple, Dict, List
import socket
import selectors
import traceback
import threading


from .SocketMessageServer import ServerMessage
from .ParseInputs import Inputs
from .QdCommandParser import QdCommandParser
from .instrument import Instrument, MultiVuExeException
from .create_logger import log
from .project_vars import (TIMEOUT_LENGTH,
                           SERVER_NAME,
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


class MultiVuServer():
    def __init__(self,
                 flags: List[str] = [],
                 host: str = HOST,
                 port: int = PORT,
                 socket_io_timeout: int = TIMEOUT_LENGTH,
                 keep_server_open=False
                 ):
        '''
        This class is used to start and maintain a socket server.  A client
        can be set up using MultiVuClient.py.

        Parameters
        ----------
        flags : [str], optional
            For a list of flags, use the help flag, '--help'.  The default
            is [].
        host : str, optional
            The host IP address.  The default is 'localhost'.
        port : int, optional
            The desired port number.  The default is 5000.
        socket_io_timeout : int, optional
            Time in seconds before the program gives up with a connection.
            The default is None.
        keep_server_open : bool, optional
            This flag can be set to true when running the server in its own
            script.  When True, the script will stay in the .open() method
            as long as the server is running.
            Default is False.

        '''

        # The normal behavior of MultiVuServer runs the server in a separate
        # thread. In order to keep the server open when running the server  
        # alone, one does not want to use threading.
        run_with_threading = not keep_server_open

        self.socket_io_timeout = socket_io_timeout
        self.sel = selectors.DefaultSelector()
        self.lsock = None
        self.message = None
        self._client_connected = False
        # Set the flags used with threading
        self._thread_running = False
        self._stop_event = None  # this is a threading.Event() object
        # Parsing the flags looks for user
        try:
            flag_info = self._parse_input_flags(flags)
        except UserWarning as e:
            # This happens if it is displaying the help text
            self.log_event = log()
            self.logger = self.log_event.create(SERVER_NAME, False)
            self.logger.info(e)
            sys.exit(0)
        self.verbose = flag_info['verbose']
        # Update the host member variable if the user flags selectted one
        self.host = flag_info['host'] if flag_info['host'] != '' else host
        p = flag_info['port']
        self.port = p if p is not None else port
        self._addr = (self.host, self.port)

        # Configure logging
        self.log_event = log()
        self.logger = self.log_event.create(SERVER_NAME,
                                            run_with_threading,
                                            )

        # Instantiate the Instrument class
        try:
            self.instr = Instrument(flag_info['instrument_str'],
                                    flag_info['scaffolding_mode'],
                                    run_with_threading,
                                    self.verbose)
        except MultiVuExeException as e:
            self.logger.info(e)
            good_exit = self.close()
            if not good_exit:
                sys.exit(0)
        # Create a threading event
        if run_with_threading:
            self._stop_event = threading.Event()

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        if self.message is not None:
            self.message.shutdown()
        if self.lsock is not None:
            if self.lsock.fileno() > 0:
                self.sel.unregister(self.lsock)
                try:
                    self.lsock.close()
                except OSError as e:
                    msg = 'error: socket.close() exception for '
                    msg += f'{self.addr}: {repr(e)}'
                    self.logger.info(msg)
                finally:
                    # Delete reference to socket object for garbage collection
                    self.lsock = None
        self._thread_active = False
        if self._stop_event is not None:
            self._stop_event.set()
        self.log_event.remove()

        # Error handling
        safe_exit = True
        if isinstance(exc_value, KeyboardInterrupt):
            self._update_connection_status(False)
            self.logger.info('')
            self.logger.info('Caught keyboard interrupt, exiting')
            safe_exit = True
        elif isinstance(exc_value, MultiVuExeException):
            self.logger.info(exc_value)
            # self.logger.error(exc_traceback.print_exc())
            safe_exit = False
        elif isinstance(exc_value, UserWarning):
            # Display the help and quit.
            self.logger.info(exc_value)
            safe_exit = True
        elif isinstance(exc_value, ConnectionError):
            safe_exit = True
        elif isinstance(exc_value, Exception):
            msg = 'MultiVuServer: error: exception for '
            msg += f'{self.message.addr}:\n'
            msg += f'{traceback.format_exc()}'
            self.logger.info(msg)
            safe_exit = False
        else:
            safe_exit = True
        self.log_event.remove()
        return safe_exit

    def _update_connection_status(self, connected):
        with threading.Lock():
            self._client_connected = connected
            self._addr = None if not connected else self._addr
        if not connected:
            self.close()

    @property
    def _thread_active(self):
        with threading.Lock():
            return self._thread_running

    @_thread_active.setter
    def _thread_active(self, active):
        with threading.Lock():
            if self._thread_running and not active:
                self._stop_event.set()
            self._thread_running = active

    def _parse_input_flags(self, flags: List[str]) -> Dict[str, str]:
        '''
        This routine will determine what the list of flags mean. If either
        the flag (--t) or the threading input-parameter are true, the server
        will be run in its own thread

        Parameters
        ----------
        flags : [str]
            Input flags such as -h or -s and PPMS flavor.  Note that any
            options specified by the command line arguments (these flags)
            will overwrite any parameters passed when instantiating the class.

        Returns
        -------
        dict()
            Dictionary with keys: 'instrument_str',
                                  'run_with_threading',
                                  'scaffolding_mode',
                                  'host',
                                  'verbose'.

        '''
        user_input = Inputs()
        return_flags = user_input.parse_input(flags)

        return return_flags

    def _accept_wrapper(self, sel, sock):
        '''
        This method accepts a new client.

        Parameters
        ----------
        sel : selectors.KqueueSelector
            This managges the socket connections.
        sock : socket.socket
            This contains the socket information.

        Returns
        -------
        sel : selectors.KqueueSelector
            Returns the selector with updated information.

        '''
        accepted_sock, self._addr = sock.accept()  # Should be ready to read
        self.logger.info(f'Accepted connection from {self._addr}')
        accepted_sock.setblocking(False)

        # Connect to MultiVu in order to enable a new thread
        self.instr.get_multivu_win32com_instance()

        self.qd_command = QdCommandParser(self.instr)
        self.message = ServerMessage(sel,
                                     accepted_sock,
                                     self.qd_command,
                                     self.verbose,
                                     )
        # Start with a read socket
        sel.register(accepted_sock, selectors.EVENT_READ, data=self.message)

        self._update_connection_status(True)
        return sel

    def _monitor_socket_connection(self, selectors):
        '''
        This monitors traffic and looks for new clients and new requests.  For
        new clients, it calls ._accept_wrapper.  After that, it takes the
        socket and asks the SocketMessageServer for help in figuring out what
        to do.

        Parameters
        ----------
        selectors : selectors.KqueueSelector
            This managges the socket connections.

        Raises
        ------
        KeyboardInterrupt
            Keyboard interrupts are how the user closes the server.

        Returns
        -------
        None.

        '''

        if self._stop_event is not None:
            self._stop_event.wait(1)

        while True:
            if self._stop_event is not None:
                if self._stop_event.isSet():
                    return
            try:
                events = selectors.select(timeout=self.socket_io_timeout)
            except OSError:
                # This error happens if the selectors is unavailble.
                pass
            for key, mask in events:
                if key.data is None:
                    selectors = self._accept_wrapper(selectors, key.fileobj)
                else:
                    self.message = key.data
                    try:
                        self.message.process_events(mask)
                    except ConnectionAbortedError:
                        self.logger.info('Exiting Server')
                        self._update_connection_status(False)
                        return
                    except ConnectionError as e:
                        self.logger.info(e)
                    else:
                        # Windows looks for the ESC key to quit.
                        if sys.platform == 'win32':
                            if (msvcrt.kbhit()
                                    and msvcrt.getch().decode() == chr(27)):
                                raise KeyboardInterrupt
                if self.instr.run_with_threading:
                    if not self._thread_active:
                        return

    def open(self):
        '''
        This method is the entry point to the MultiVuServer class.  It starts
        the connection and passes off control to the rest of the class to
        monitor traffic in order to  receive commands from a client and
        respond appropriately.

        Returns
        -------
        None.

        '''
        # Set up the sockets
        self.lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Avoid bind() exception: OSError: [Errno 48] Address already in use
        self.lsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            self.lsock.bind(self._addr)
        except OSError as e:
            # connection already open?
            self.logger.info(e)
            return
        self.lsock.listen()
        self.logger.info(f'listening on {self._addr}')
        if sys.platform == 'win32':
            quit_keys = "ESC"
        else:
            quit_keys = "ctrl-c"
        self.logger.info(f'Press {quit_keys} to exit.')
        self.lsock.setblocking(False)
        self.sel.register(self.lsock, selectors.EVENT_READ, data=None)

        # Call ._monitor_socket_connection()
        if self._stop_event is not None:

            self.server_thread = threading.Thread(
                name=SERVER_NAME,
                target=self._monitor_socket_connection,
                args=[self.sel]
                )
            # The Server thread is now doing most of the work
            self._thread_active = True
            self.server_thread.start()
        else:
            self._monitor_socket_connection(self.sel)

    def close(self):
        '''
        This closes the server

        Returns
        -------
        None.

        '''
        err_info = sys.exc_info()
        return self.__exit__(err_info[0],
                             err_info[1],
                             err_info[2])

    def is_client_connected(self):
        with threading.Lock():
            status = False
            if self.message is not None:
                # status = self.message.sock is not None
                status = self.message.connected
            return status

    def client_address(self):
        with threading.Lock():
            # return self._addr
            if self.is_client_connected():
                address = self.message.addr
            else:
                address = ('', 0)
            return address


def server(flags: str = ''):
    '''
    This method is called when MultiVuServer.py is run from a command line.
    It deciphers the command line text, and the instantiates the
    MultiVuServer.

    Parameters
    ----------
    flags : str, optional
        The default is ''.

    Returns
    -------
    None.

    '''

    user_flags = []
    if flags == '':
        user_flags = sys.argv[1:]
    else:
        user_flags = flags.split(' ')

    s = MultiVuServer(user_flags, run_with_threading=False)
    s.open()


if __name__ == '__main__':
    server()
