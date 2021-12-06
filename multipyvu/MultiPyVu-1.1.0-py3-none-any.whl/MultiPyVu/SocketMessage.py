#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SocketMessage.py is the base class for sending information across sockets.  It
has two inherited classes, SocketMessageServer.py and SocketMessageClient.py

Created on Mon Jun 7 23:47:19 2021

@author: D. Jackson
"""

import sys
import selectors
import json
import io
import logging
import struct
import time

from .QdCommandParser import QdCommandParser
from .project_vars import SERVER_NAME, CLIENT_NAME


class Message:
    def __init__(self,
                 selector,
                 sock,
                 qdCommandParser: QdCommandParser = None,
                 verbose=False):
        '''
        This is the base class for holding data when sending or receiving
        sockets.  The class is instantiated by MultiVuServer() and
        MultiVuClient().

        The data is sent (.request['content']) and received (.response) as
        a dictionary of the form:
                action (ie, 'TEMP?', 'EXIT', 'FIELD',...)
                query
                result

        The information goes between sockets using the following format:
            Header length in bytes
            JSON header (.jsonheader) dictionary with keys:
                byteorder
                content-type
                content-encoding
                content-length
            Content dictionary with key:
                action
                query
                result

        The entry method into the class is process_events(mask), where
        (key, mask) = selectors.select(), and indicates if the socket should
        be reading or writing.

        The class also has methods for read(), write(), and close().

        Parameters
        ----------
        selector : KqueueSelector
            selector = selectors.DefaultSelector()
        sock : socket
            The socket object.
        qdCommandParser : QdCommandParser object, optional
            This is what is used to connect the Socket Message to making
            real calls to MultiVu.
        verbose : bool, optional
            With this turned on, a notice will be printed showing everything
            sent and received across a socket.

        '''
        self.verbose = verbose
        self.selector = selector
        self.sock = sock
        self.addr = ('ip address', 0000)    # defined in the subclasses
        self.connected = True    # connection made when instantiated.
        self.request = None
        self._recv_buffer = b''
        self._send_buffer = b''
        self._request_queued = False    # only used by the client
        self._jsonheader_len = None
        self.jsonheader = None
        self.response_created = False   # only used by the server
        self._sent_success = False       # only used by the server
        self.response = None            # only used by the client
        self._request_is_text = False
        self.qd_command = qdCommandParser
        self.mvu_flavor = None

    #########################################
    #
    # Private Methods
    #
    #########################################

    def _set_selector_events_mask(self, mode):
        """Set selector to listen for events: mode is 'r', 'w', or 'rw'."""
        if mode == "r":
            events = selectors.EVENT_READ
        elif mode == "w":
            events = selectors.EVENT_WRITE
        elif mode == "rw":
            events = selectors.EVENT_READ | selectors.EVENT_WRITE
        else:
            raise ValueError(f"Invalid events mask mode {repr(mode)}.")
        self.selector.modify(self.sock, events, data=self)

    def _read(self):
        try:
            # Should be ready to read
            data = self.sock.recv(4096)
        except BlockingIOError:
            # Resource temporarily unavailable (errno EWOULDBLOCK)
            pass
        else:
            if data:
                self._recv_buffer += data
            else:
                raise ConnectionError

    def _write(self):
        # until the sock is sent, this flag should be False
        self._sent_success = False

        if self._send_buffer:
            self._log_send()
            try:
                # Should be ready to write
                sent = self.sock.send(self._send_buffer)
                self._sent_success = True
            except BlockingIOError:
                # Resource temporarily unavailable (errno EWOULDBLOCK)
                self._sent_success = False
            except BrokenPipeError:
                # Resource temporarily unavailable
                self._sent_success = False
            # Note that OSError is a base class with the folloiwng subclasses:
            # ConnectionError
            # ConnectionAbortedError
            # ConnectionRefusedError
            except OSError:
                # No socket connection
                self._sent_success = False
                err_msg = 'No socket connection.  Please make sure '
                err_msg += 'MultiVuServer is running and that '
                err_msg += 'MultiVuClient is using the same IP address.'
                raise ConnectionError(err_msg)
            else:
                self._send_buffer = self._send_buffer[sent:]

    def _log_received_result(self, message: str):
        msg = f';from {self.addr}; Received request {message}'
        if self.verbose:
            self.logger.info(msg)
        else:
            self.logger.debug(msg)

    def _log_send(self):
        msg = f';to {self.addr}; Sending {repr(self._send_buffer)}'
        if self.verbose:
            self.logger.info(msg)
        else:
            self.logger.debug(msg)

    def _check_close(self):
        '''
        Checks to see if the client has requested to close the connection
        to the server.

        Raises
        ------
        ConnectionError
            This error is used to let the program know the client
            is closing, but the server will remain open.

        Returns
        -------
        None.

        '''
        close_sent = self.response['action'] == 'CLOSE'
        closing_received = self.response['query'] = 'CLOSE'
        try:
            if close_sent and closing_received:
                self.close()
                # Client has requested to close the connection
                raise ConnectionError
        except KeyError:
            # connection closed by the other end
            pass

    def _check_exit(self):
        '''
        Checks to see if the client has requested to exit the program, meaning
        the client closes the connection and the server exits

        Raises
        ------
        ConnectionAbortedError
            This error is used to let the program know the server
            is getting shut down (EXIT received)

        Returns
        -------
        None.

        '''
        exit_sent = self.response['action'] == 'EXIT'
        exit_received = self.response['query'] = 'EXIT'
        try:
            if exit_sent and exit_received:
                self.shutdown()
                raise ConnectionAbortedError
        except KeyError:
            # connection closed by the other end
            pass

    def _json_encode(self, obj, encoding):
        return json.dumps(obj, ensure_ascii=False).encode(encoding)

    def _json_decode(self, json_bytes, encoding):
        tiow = io.TextIOWrapper(
            io.BytesIO(json_bytes), encoding=encoding, newline=""
        )
        obj = json.load(tiow)
        tiow.close()
        return obj

    def _binary_encode(self, obj, encoding):
        # first convert the dict to a string
        content_str = str(obj)
        # Then str to binary
        return content_str.encode(encoding=encoding)

    def _binary_decode(self, string_bytes, encoding):
        content_str = string_bytes.decode(encoding=encoding)

        decoded_dict = dict()
        # look for the string to be a dictionary
        if content_str[0] == '{' and content_str[-1] == '}':
            items = content_str[1:-1].split(',')
            for i in items:
                # each key and value have quotes around
                # them which need to be removed
                i = i.replace("'", "")
                key, value = i.split(':')
                key = key.strip()
                value = value.strip()
                if key == 'content-length':
                    value = int(value)
                decoded_dict[key] = value
        return decoded_dict

    def _text_encode(self, content_str, encoding):
        return content_str.encode(encoding=encoding)

    def _text_decode(self, string_bytes, encoding):
        command = string_bytes.decode(encoding=encoding)

        # TODO - the code below follows the original routine
        # cmd_buffer = ''
        # found_putty = False
        # for char in self._recv_buffer:
        #     if (char == b'\r') or (char == 'b\n'):
        #         command = cmd_buffer.upper().strip(' ')

        #     # discard escape characters from Putty
        #     elif (char == chr(0xff)):
        #         found_putty = True
        #         continue
        #     elif found_putty:
        #         found_putty = False
        #         continue

        #     # keep printable characters
        #     elif (ord(char) > 25) and (ord(char) < 125):
        #         cmd_buffer += (char.decode(encoding))

        return command

    def _create_message(self,
                        *,
                        content_bytes,
                        content_type,
                        content_encoding):
        header = {
            'byteorder': sys.byteorder,
            'content-type': content_type,
            'content-encoding': content_encoding,
            'content-length': len(content_bytes),
        }
        if content_type == 'text/json':
            header_bytes = self._json_encode(header, 'utf-8')
        else:
            header_bytes = self._binary_encode(header, 'utf-8')
        message_hdr = struct.pack('>H', len(header_bytes))
        message = message_hdr + header_bytes + content_bytes
        return message

    #########################################
    #
    # Public Methods
    #
    #########################################

    def process_events(self, mask):
        '''
        This is the entry-point for the Message base class.

        Parameters
        ----------
        mask : int
            The events mask returned via key, mask = sel.select().

        Returns
        -------
        None.

        '''
        if mask & selectors.EVENT_READ:
            self.read()
        if mask & selectors.EVENT_WRITE:
            max_tries = 3
            for attempt in range(max_tries):
                try:
                    self.write()
                except ConnectionAbortedError as e:
                    # Server closed, but don't want to show the message
                    # from the ConnectionError.  This is needed since
                    # ConnectionAbortedError is a subclass of ConnectionError
                    raise ConnectionAbortedError(e)
                except ConnectionError as e:
                    time.sleep(1)
                    if attempt == max_tries - 1:
                        err_msg = 'Socket connection failed after '
                        err_msg += f'{max_tries} attempts.'
                        self.logger.info(err_msg)
                        raise ConnectionError(e)
                else:
                    break

    def read(self):
        # this method needs to be overriden
        raise NotImplementedError()

    def write(self):
        # this method needs to be overriden
        raise NotImplementedError()

    def close(self):
        try:
            # Check for a socket being monitored to continue.
            sel_key = self.selector.get_key(self.sock)
        except ValueError:
            pass
        except KeyError:
            # no selector is registered
            pass
        else:
            if sel_key is not None:
                self.logger.info(f'Closing connection to {self.addr}')
                self.selector.unregister(self.sock)
                self.connected = False

    def shutdown(self):
        self.close()
        if self.sock is not None:
            try:
                self.sock.close()
            except OSError as e:
                msg = 'error: socket.close() exception for '
                msg += f'{self.addr}: {repr(e)}'
                self.logger.info(msg)
            finally:
                # Delete reference to socket object for garbage collection
                self.sock = None
                self.connected = False

    def process_protoheader(self):
        hdrlen = 2
        if len(self._recv_buffer) >= hdrlen:
            # format = >H, which means:
            #   > = big-endian
            #   H = unsigned short, length = 2 bytes
            # This returns a tuple, but only the first item has a value,
            # which is why the line ends with [0]
            self._jsonheader_len = struct.unpack(
                '>H',
                self._recv_buffer[:hdrlen])[0]
            if len(self._recv_buffer) > self._jsonheader_len:
                # Now that we know how big the header is, we can trim
                # the buffer and remove the header length info
                self._recv_buffer = self._recv_buffer[hdrlen:]
            else:
                # This indicates that the buffer could be straight binary
                # and was not encoded in json format.  See if the next
                # character is not a bracket ('{' or '['), which would
                # confirm that the buffer is not json.
                # Set the flag to show the input is text and set flags to
                # not look for a json header
                first_char = self._recv_buffer[hdrlen:hdrlen + 1]
                if first_char != b'{' or first_char != b'[':
                    self._request_is_text = True
                    self._jsonheader_len = 0
                    hdrlen = 0
                    self.jsonheader = ''

    def process_jsonheader(self):
        hdrlen = self._jsonheader_len

        # The buffer holds the header and the data.  This makes sure
        # that the buffer is at least as long as we expect.  It will
        # be longer if there is data.
        if len(self._recv_buffer) >= hdrlen:
            # parse the buffer to save the header
            try:
                self.jsonheader = self._json_decode(
                    self._recv_buffer[:hdrlen],
                    'utf-8')
            except json.decoder.JSONDecodeError:
                self.jsonheader = self._binary_decode(
                    self._recv_buffer[:hdrlen],
                    'utf-8')

            # This ensures that the header has all of the required fields
            for reqhdr in (
                    'byteorder',
                    'content-length',
                    'content-type',
                    'content-encoding',
                    ):
                if reqhdr not in self.jsonheader:
                    raise ValueError(f'Missing required header "{reqhdr}".')

            # Then cut the buffer down to remove the header so that
            # now the buffer only has the data.
            self._recv_buffer = self._recv_buffer[hdrlen:]

    def create_request(self, action, query):
        self.request = {
            'type': 'text/json',
            'encoding': 'utf-8',
            'content': dict(action=action.upper(), query=query, result=''),
            }
        events = selectors.EVENT_READ | selectors.EVENT_WRITE
        try:
            self.selector.modify(self.sock, events, data=self)
        except KeyError:
            self.selector.register(self.sock, events, data=self)
        except ValueError as e:
            self.logger.info('Warning:  No server/client connection')
            raise ConnectionError() from e
        return self.request
