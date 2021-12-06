#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SocketMessageClient.py inherits SocketMessage and is used by the client
to communicate with socket server via SocketMessageServer

Created on Mon Jun 7 23:47:19 2021

@author: D. Jackson
"""

import re
import logging
import time

from .SocketMessage import Message
from .QdCommandParser import QdCommandParser
from .project_vars import CLIENT_NAME


class ClientMessage(Message):
    def __init__(self,
                 selector,
                 sock,
                 qdCommandParser: QdCommandParser = None,
                 verbose=False):
        super().__init__(selector,
                         sock,
                         qdCommandParser,
                         verbose)
        time.sleep(0.3)
        self.addr = sock.getsockname()
        self.logger = logging.getLogger(CLIENT_NAME)

    #########################################
    #
    # Private Methods
    #
    #########################################

    def _process_response_json_content(self):
        content = self.response
        if content['action'] == 'START':
            self.verbose = (content['query'] == 'v')
            resp = content.get('result')
            search = r'Connected to ([\w]*) MultiVuServer'
            self.mvu_flavor = re.findall(search, resp)[0]
        self._log_received_result(content.get('result'))

    def _process_response_binary_content(self):
        content = self.response
        self._log_received_result(repr(content))

    def _reset_read_state(self):
        self._jsonheader_len = None
        self.jsonheader = None
        self.request = None
        self._request_is_text = False

    #########################################
    #
    # Public Methods
    #
    #########################################

    def read(self):
        # read sockets
        try:
            self._read()
        except ConnectionError:
            # This is thrown if the server or the client shut down. If
            # the server shuts down, the client needs to also shut down
            if self.request['content']['action'] == 'START':
                err_msg = 'No connection to the sever upon start.  Is the '
                err_msg += 'server running?'
                self.logger.info(err_msg)
            self.shutdown()
            raise ConnectionError

        if self._jsonheader_len is None:
            self.process_protoheader()

        if self._jsonheader_len is not None:
            if self.jsonheader is None:
                self.process_jsonheader()

        if self.jsonheader:
            self.process_response()

        self._set_selector_events_mask('w')
        self._check_close()
        self._check_exit()
        self._reset_read_state()

    def write(self):
        if not self._request_queued:
            self.queue_request()

        self._write()

        # This tells selector.select() to stop monitoring for write events
        # and reset the _request_queued flag
        if self._request_queued:
            if not self._send_buffer:
                # Set selector to listen for read events; we're done writing.
                # Keep this socket a read socket until we are ready
                # to write anything.
                self._set_selector_events_mask('r')
                self._request_queued = False

    def queue_request(self):
        content = self.request['content']
        content_type = self.request['type']
        content_encoding = self.request['encoding']
        if content_type == 'text/json':
            content_binary = self._json_encode(content, content_encoding)
        else:
            content_binary = self._binary_encode(content, content_encoding)

        req = {
            'content_bytes': content_binary,
            'content_type': content_type,
            'content_encoding': content_encoding,
            }
        message = self._create_message(**req)
        self._send_buffer += message
        self._request_queued = True

    def process_response(self):
        content_len = self.jsonheader["content-length"]
        if len(self._recv_buffer) < content_len:
            return

        if self._request_is_text:
            self.response = self._text_decode(self._recv_buffer, 'utf-8')
            self._recv_buffer = b''
            self._log_received_result(repr(self.response))
        else:
            data = self._recv_buffer[:content_len]
            self._recv_buffer = self._recv_buffer[content_len:]
            encoding = self.jsonheader["content-encoding"]
            if self.jsonheader["content-type"] == "text/json":
                self.response = self._json_decode(data, encoding)
                self._log_received_result(repr(self.response))
                self._process_response_json_content()
            else:
                # Binary or unknown content-type
                self.response = self._binary_decode(data, encoding)
                self._log_received_result(self.jsonheader["content-type"])
                self._process_response_binary_content()
