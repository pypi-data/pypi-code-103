#!/usr/bin/env python3

"""
** Server TCP. **
-----------------

It is a tcp server listening to several clients. Unlike the client,
there must be only one instance per machine. The server must be executed
in a totally different process than the client.
It is the pillar that allows the processes to communicate with each other.
That it is via the internal sockets within the same machine
or via sockets tcp through the Internet network.
"""


import queue
import socket
import threading

from raisin.communication.abstraction import SocketAbstractConn
from raisin.communication.handler import Handler


__pdoc__ = {
    'Server.__del__': True,
    'Server.__enter__': True,
    'Server.__exit__': True,
    'Server.__repr__': True,
    'Server.__str__': True}


class BaseServer(threading.Thread):
    """
    ** TCP server. **

    This server is both able to listen in ipv4 and ipv6.

    Attributes
    ----------
    port : int
        The listening port number.
    clients : list
        It is in this attribute that all clients that are
        communicating with the server are stored.
    tcp_socket : socket.socket
        The socket object on which the server will listen for incoming requests.
    """

    def __init__(self, port):
        """
        Parameters
        ----------
        port : int
            The port to listen on.
        """
        threading.Thread.__init__(self)
        self.port = port
        self.clients = []
        self.tcp_socket = BaseServer._init_tcp_socket(self.port)
        self.tcp_socket.listen()

        self._shutdown = False  # The flag becomes True if you have to die.
        self._request_queue = queue.Queue()  # Contains new clients.

    @staticmethod
    def _init_tcp_socket(port):
        """
        ** Help for the ``BaseServer.__init__``. **

        Paremeters
        ----------
        port : int
            The port to listen on.

        Returns
        -------
        tcp_socket : socket.socket
            The TCP socket ready to listen.

        Examples
        --------
        >>> from raisin.communication.server import BaseServer
        >>> tcp_socket = BaseServer._init_tcp_socket(9999)
        >>> type(tcp_socket)
        <class 'socket.socket'>
        >>> tcp_socket.close()
        >>>
        """
        if hasattr(socket, 'has_dualstack_ipv6'):  # only supported for python >= 3.8
            if socket.has_dualstack_ipv6():
                return socket.create_server(
                    ('', port), family=socket.AF_INET6, dualstack_ipv6=True, reuse_port=True
                )
            return socket.create_server(('', port), reuse_port=True)
        tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        tcp_socket.bind(('', port))
        return tcp_socket

    def _get(self, request):
        """
        ** Prepare the client to pass the verification stape. **

        Parameters
        ----------
        request : tuple
            The tuple (conn, address) returned by the *socket.accept()* method.
        """
        conn, _ = request
        self._request_queue.put(
            {'stape': 'verify', 'abstract_conn': SocketAbstractConn(conn=conn)}
        )

    def _verify(self, abstract_conn):
        """
        ** Ensures the caller is welcome. **

        Parameters
        ----------
        abstract_conn : AbstractConn
            The connection to be checked.

        Notes
        -----
        For the moment, accept directly without making any verification.
        """
        self._request_queue.put({'stape': 'process', 'abstract_conn': abstract_conn})

    def _process(self, abstract_conn):
        """
        ** Definitely adds the client to the server. **

        Parameters
        ----------
        abstract_conn : AbstractConn
            The connection to be checked.
        """
        client_handler = Handler(abstract_conn)
        client_handler.start()
        self.clients.append(client_handler)

    def handle_request(self, request):
        """
        ** Process a single request. **

        This method creates a thread or a process in order to return immediately.
        In fact this method is called by the ``BaseServer.serve_forever`` method.

        Parameters
        ----------
        request : dict
            A client request that can be at different stages:

            - *get* : This is the client's first attempt to connect.
            - *verify* : Verification the client is welcome.
            - *process* : Creates an environment that allows dialogue with the client.
        """
        if request['stape'] == 'get':
            return self._get(request['request'])
        if request['stape'] == 'verify':
            return self._verify(request['abstract_conn'])
        if request['stape'] == 'process':
            return self._process(request['abstract_conn'])
        raise NameError(f"this step has nothing to do here: {request['stape']}")

    def run(self):
        """
        ** Start the server asynchronously. **

        Should not be called as is. It is the call of the
        *start* method that executes run.
        It is an alias to ``BaseServer.serve_forever``.
        """
        self.serve_forever()

    def serve_forever(self, poll_interval=0.5):
        """
        ** Handle requests until an explicit ``BaseServer.shutdown`` request. **

        Poll for shutdown every poll_interval seconds.
        """
        def listen(self):
            self.tcp_socket.settimeout(poll_interval) # avoids creation of zombies
            while not self._shutdown:
                try:
                    self._request_queue.put({'stape': 'get', 'request': self.tcp_socket.accept()})
                except socket.timeout:
                    continue
                except OSError:
                    break

        thread = threading.Thread(target=listen, args=(self,))
        thread.start()
        while not self._shutdown:
            try:
                self.handle_request(self._request_queue.get(timeout=poll_interval))
            except queue.Empty:
                continue
        thread.join()

    def shutdown(self):
        """
        Tell the ``BaseServer.serve_forever`` loop to stop and wait until it does.
        ``BaseServer.shutdown`` must be called while ``BaseServer.serve_forever``
        is running in a different thread otherwise it will deadlock.
        """
        self.server_close()
        while self.is_alive():
            continue
        for client in self.clients:
            client.join()

    def server_close(self):
        """
        ** Clean up the server. **

        Should not be called if the server is encapsulated
        in a context manager (*with* statement).
        Can be called several times.
        """
        self._shutdown = True
        try:
            self.tcp_socket.shutdown(socket.SHUT_RDWR)
        except OSError:
            pass
        self.tcp_socket.close()
        for client in self.clients:
            client.handler_close()


class Server(BaseServer):
    """
    ** Enables you to enrich the ``raisin.communication.server.BaseServer``. **

    Examples
    --------
    >>> import time
    >>> from raisin.communication.server import Server
    >>> with Server(9999) as server:
    ...     server.start() # the server is listening
    ...     time.sleep(1) # wait until the server is ready
    ...     server.shutdown() # stops the server
    ...
    >>>
    """

    def __del__(self):
        """
        ** Help for the garbage-collector. **
        """
        self.server_close()

    def __enter__(self):
        """
        ** Prepared for easy closing. **

        Allows you to use the *with* statement which allows
        you to set up a context manager.
        """
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """
        ** Stop the server. **

        Goes together with ``Server.__enter__``.
        """
        self.shutdown()

    def __repr__(self):
        """
        ** Gives a simple representation of the server. **
        """
        return f'Server({self.port})'

    def __str__(self):
        r"""
        ** Provides a complete representation of the server. **
        """
        return (
            f'TCP Server:\n'
            f'    port={self.port}\n'
            f'    tcp_socket={self.tcp_socket}\n'
            f'    clients={self.clients}')


if __name__ == '__main__':
    # Launches a server without returning the hand.
    with Server(20001) as server:
        server.serve_forever()
