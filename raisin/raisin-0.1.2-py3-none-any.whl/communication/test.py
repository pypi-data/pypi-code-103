#!/usr/bin/env python3

"""
** Allows for extensive testing around communication. **
--------------------------------------------------------
"""

import socket

from raisin.communication.abstraction import SocketAbstractConn

def test_socket_abstraction_conn():
    """
    ** Tests all fonctions of the abstraction. **
    """
    socket1, socket2 = socket.socketpair()
    abstraction1, abstraction2 = SocketAbstractConn(socket1), SocketAbstractConn(socket2)

    abstraction1.send((b'mes', b'sage1',))
    abstraction2.send((b'hello',))
    abstraction2.send((b'',))
    abstraction1.send((b'message2',))
    assert b''.join(abstraction2.recv()) == b'message1'
    assert b''.join(abstraction2.recv()) == b'message2'
    assert b''.join(abstraction1.recv()) == b'hello'
    assert b''.join(abstraction1.recv()) == b''

    socket1.shutdown(socket.SHUT_RDWR)
    socket2.shutdown(socket.SHUT_RDWR)
    socket1.close()
    socket2.close()
