#
# DISCo Python interface library
# Copyright (c) 2021 Greg Van Aken
#
"""io.py: I/O Classes interfacing with DISCo devices directly.

Contains the base class DiscoIO which must be re-implemented using user-specific read() and write() functions,
dependent on the interface (USB, Serial, Network, etc.).
"""

import struct
from discolib.protocol import Const

class Validate:
    """Validation decorators for IO operations."""
    def read(func):
        """Validate input to DiscoIO read"""
        def wrap(*args, **kwargs):           
            length = args[-1]
            if length < 0:
                # TODO: DiscoException (https://gavansystems.atlassian.net/browse/DIS-6)
                raise RuntimeError(f'Invalid length: {length}.')
            data = func(*args, **kwargs)
            if len(data) != length:
                # TODO: DiscoException (https://gavansystems.atlassian.net/browse/DIS-6)
                raise RuntimeError(f'Unexpected data length. Expected: {length}. Received: {len(data)}.')
            return data
        return wrap
    
    def write(func):
        """Validate input to DiscoIO write"""
        def wrap(*args, **kwargs):
            data = args[-1]
            if type(data) is not bytes:
                # TODO: DiscoException (https://gavansystems.atlassian.net/browse/DIS-6)
                raise RuntimeError(f'Cannot write binary data of invalid type: {type(data)}.')
            if len(data) == 0:
                # TODO: DiscoException (https://gavansystems.atlassian.net/browse/DIS-6)
                raise RuntimeError(f'Cannot write empty bytes.')
            return func(*args, **kwargs)
        return wrap
    


class DiscoIO:

    def read(self, length: int, *args, **kwargs) -> bytes:
        """Read bytes from the component(s). To be implemented (by you!)."""
        raise NotImplementedError('Define your own DiscoIO class that implements read(length)!')
    
    def write(self, data: bytes, *args, **kwargs) -> None:
        """Send bytes to the component(s). To be implemented (by you!)."""
        raise NotImplementedError('Define your own DiscoIO class that implements write(data)!')

    def read_response(self):
        """Read and validate a response's header, length, and checksum, extracting and returning the remaining bytes."""
        response = bytes()
        h1, h2, len = struct.unpack('BBB', self.read(3))
        if (h1 == Const.HEADER_1 and h2 == Const.HEADER_2):
            response = self.read(len-1) # TODO: CS
        return response
