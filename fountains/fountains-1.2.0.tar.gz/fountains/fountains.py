"""
Python library for generating and concisely specifying
reproducible pseudorandom binary data for unit testing.
"""
from __future__ import annotations
from typing import Optional, Union, Sequence, Callable
import doctest
import string
from itertools import islice # pylint: disable=W0611 # Used in doctests.
from math import log2
from hashlib import sha256
from bitlist import bitlist

class fountains: # pylint: disable=R0903
    """
    Class that can act as a pseudorandom test data generator and a testing
    harness for functions.

    :param length: Size in bytes of each pseudorandom bytes-like object.
    :param limit: Number of pseudorandom bytes-like objects to generate.
    :param seed: Seed to use for generating pseudorandom bytes-like objects.
    :param bits: Output specification to use for testing a function.
    :param function: Function to test against the supplied specification.

    An object of this class can be used to generate pseudorandom binary test data.

    >>> [bs.hex() for bs in fountains(2, limit=3)]
    ['e3b0', 'ce1b', '2ed5']
    >>> [int.from_bytes(bs, 'little') for bs in fountains(2, 3, seed=123)]
    [7938, 11702, 64114]
    >>> [int.from_bytes(bs, 'little') for bs in fountains(2, 3, seed='abc')]
    [30906, 57846, 34365]
    >>> fountains(2, seed=-1)
    Traceback (most recent call last):
      ...
    ValueError: integer seed must be non-negative
    >>> fountains(2, seed=0.1)
    Traceback (most recent call last):
      ...
    ValueError: seed must be of type int, str, bytes, or bytearray
    >>> [int.from_bytes(bs, 'little') for bs in fountains(1, 3)]
    [227, 206, 46]

    Supplying a function as a parameter makes it possible to generate a concise
    specification for that function's behavior across a sequence of pseudorandom
    inputs. The sequence of inputs corresponds exactly to the test data that is
    emitted (as in the above example) when the function parameter is not used.

    >>> fun = lambda bs: bytes(reversed(bs))
    >>> bitlist(list(fountains(8, limit=5 * 8, function=fun))).hex()
    '30a2657266'

    Supplying the specification generated in the manner above as an additional
    parameter makes it possible to test a function's behavior. In this case, an
    iterable of boolean values is returned, with each boolean value in the sequence
    indicating whether the function's behavior on the corresponding input (within
    the sequence of pseudorandom test inputs) is consistent with the specification.
    Note that *false negatives may occur*, but *false positive cannot occur*.

    >>> list(fountains(4, 4, function=fun, bits=bytes([123])))
    [True, True, True, True, False, True, True, True]
    >>> list(fountains(4, 4, function=fun, bits='7b'))
    [True, True, True, True, False, True, True, True]
    >>> list(fountains(4, 4, function=fun, bits=0.1)) # doctest: +ELLIPSIS
    Traceback (most recent call last):
      ...
    ValueError: target bits must be of type int, str of hexdigits, ... [0, 1]
    >>> list(fountains(4, 4, function=fun, bits=[0,1,0,1]))
    [True, True, False, True]
    >>> [f(bitlist(fun(bs))) for (bs, f) in list(fountains(4, 4, bits=[0,1,0,1]))]
    [True, True, False, True]
    >>> fun = lambda bs: bitlist([1])
    >>> list(fountains(4, 4, function=fun, bits=[0,1,0,1]))
    [False, True, False, True]
    >>> fun = lambda bs: ['this is a list']
    >>> list(fountains(1, 1, function=fun, bits=[1]))
    Traceback (most recent call last):
      ...
    ValueError: test output must be a bytes-like object or bitlist

    It is possible to limit the number of pseudorandom test values
    that are yielded (or, depending on the other parameters, the
    number of tests that are conducted) when iterating over an object.

    >>> len(list(fountains(32, limit=10)))
    10
    >>> len(list(fountains(32, limit=5)))
    5
    >>> len(list(islice(fountains(32, limit=10), 0, 5)))
    5
    >>> len(list(islice(fountains(32), 0, 5)))
    5
    """
    def __init__(
            self: fountains,
            length: int = 1,
            limit: Optional[int] = None,
            seed: Union[int, str, bytes, bytearray, None] = bytes(0),
            bits: Union[Sequence[int], str, bytes, bytearray, None] = None,
            function: Optional[Callable[[bytes], bytes]] = None
        ):
        self.length = length
        self.limit = limit
        self.count = 0
        self.bit_ = 0

        if isinstance(seed, int):
            if seed < 0:
                raise ValueError("integer seed must be non-negative")
            self.state = seed.to_bytes(1 + (int(log2(max(seed, 1))) // 8), 'little')
        elif isinstance(seed, str):
            self.state = str.encode(seed)
        elif isinstance(seed, (bytes, bytearray)):
            self.state = seed
        else:
            raise ValueError("seed must be of type int, str, bytes, or bytearray")

        if bits is None:
            self.bits = None
        elif isinstance(bits, (bytes, bytearray)):
            self.bits = bitlist(bits)
            self.limit = len(self.bits) # Only enough data for target bits.
        elif isinstance(bits, list) and all(isinstance(n, int) for n in bits):
            self.bits = bitlist(bits)
            self.limit = len(self.bits) # Only enough data for target bits.
        elif isinstance(bits, str) and all(c in string.hexdigits for c in bits):
            self.bits = bitlist.fromhex(bits)
            self.limit = len(self.bits) # Only enough data for target bits.
        else:
            raise ValueError(
                "target bits must be of type int, str of hexdigits, bytes, " +
                "bytearray, or list of integers in the interval [0, 1]"
            )

        self.function = function

    def _bit(self: fountains, bs: Union[bytes, bytearray, bitlist]): # pylint: disable=C0103
        """
        Obtain the next bit from the output.
        """
        if isinstance(bs, (bytes, bytearray)):
            bs = bitlist(bs)
        if not isinstance(bs, bitlist):
            raise ValueError("test output must be a bytes-like object or bitlist")

        # Reset the bit counter if the output is too short.
        self.bit_ = self.bit_ if self.bit_ < len(bs) else 0

        return bs[self.bit_]

    def __iter__(self: fountains):
        """
        Return a generator that yields values based on the parameters
        supplied at this object's instantiation.

        >>> [bs.hex() for bs in fountains(length=3, limit=4)]
        ['e3b0c4', 'ce1bc4', '2ed5b5', '781f5a']
        """
        while self.limit is None or self.count < self.limit:
            bs = bytearray()
            while len(bs) < self.length:
                bs_ = sha256(self.state).digest()
                bs.extend(bs_[:16])
                self.state = bs_[16:]

            if self.function is not None and self.bits is None:
                # Return the output bits of the function on the
                # generated test inputs, one at a time.
                yield self._bit(self.function(bs[:self.length]))
            elif self.function is not None and self.bits is not None:
                # Return whether the function has the correct bit
                # in its output for this generated input.
                yield\
                    self.bits[self.count] ==\
                        self._bit(self.function(bs[:self.length]))
            elif self.function is None and self.bits is not None:
                # If a target bit sequence has been supplied
                # but no function has been supplied, return a
                # function that checks an output for that bit.
                yield (
                    bs[:self.length],
                    eval( # pylint: disable=W0123
                        "lambda bs: bs[" + str(self.bit_) + "] == " +\
                        str(self.bits[self.count])
                    )
                )
            else:
                # Return the generated test input.
                yield bs[:self.length]

            self.count += 1
            self.bit_ += 1

if __name__ == "__main__":
    doctest.testmod() # pragma: no cover
