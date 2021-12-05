#!/usr/bin/env python3

"""
** Processes requests. **
-------------------------

Whether it is a client or a server that asks for something, it doesn't change much.
In all cases it is TCP sockets that request and render services.
That's why once the communication is established,
clients and servers use the same function to communicate.
"""

import threading


class Handler(threading.Thread):
    """
    ** Helps a socket to communicate. **

    Attributes
    ----------
    abstract_conn : AbstractConn
        The abstract connection that allows communication.
    """

    def __init__(self, abstract_conn):
        """
        Parameters
        ----------
        abstract_conn : AbstractConn
            An entity able to communicate.
        """
        threading.Thread.__init__(self)
        self.abstract_conn = abstract_conn

    def run(self):
        """
        ** Wait for the requests to answer them. **

        This method must be launched asynchronously by invoking the *start* method.
        It listens for the arrival of a request through the 'abstract_conn' attribute.
        As soon as a request arrives, it is processed. Once the request is processed,
        this method starts listening for the next request.
        """
        while True:
            try:
                request = self.abstract_conn.recv_obj()
            except ConnectionError:
                break
            raise NotImplementedError(f'impossible de traiter {request}, c est pas code')

    def handler_close(self):
        """
        ** Clean up the connection. **
        """
        self.abstract_conn.close()
