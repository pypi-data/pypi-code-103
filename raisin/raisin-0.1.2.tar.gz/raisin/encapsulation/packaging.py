#!/usr/bin/env python3

"""
** Unitary creation of packets. **
----------------------------------

This is where there are the basic classes that represent the fundamental
packets for transferring data across the network.
"""

from raisin.serialization import deserialize, serialize

__pdoc__ = {
    'Package.__repr__': True,
    'Package.__hash__': True,
    'Package.__eq__': True,
    'Argument.__repr__': True,
    'Argument.__getstate__': True,
    'Argument.__setstate__': True,
    'Function.__repr__': True,
}


class Package:
    """
    ** Base class to represent a package. **
    """

    def __repr__(self):
        """
        ** Improve representation. **

        Returns an evaluable representation in a particular context
        of the dynamic instance of an object inherited from this class.

        Examples
        --------
        >>> from raisin.encapsulation.packaging import Package
        >>> Package()
        Package()
        >>>
        """
        return f'{self.__class__.__name__}()'

    def __hash__(self):
        """
        ** Compute a real unique hash. **

        The hash calculation is based on the content of the object,
        not on the addresses in memory.

        Examples
        --------
        >>> from raisin.encapsulation.packaging import Package
        >>> {Package(), Package()}
        {Package()}
        >>>
        """
        ordered_items = sorted(self.__dict__.items(), key=lambda kv: kv[0])
        return hash(tuple(v for _, v in ordered_items))

    def __eq__(self, other):
        """
        ** Compare 2 objects based on the hash. **

        2 objects are equal if they are exactly
        the same type and have the same hash value.
        This function is essential to be able to apply
        hashable collections on ``Package`` instance.

        Examples
        --------
        >>> from raisin.encapsulation.packaging import Package
        >>> Package() == Package()
        True
        >>>
        """
        if self.__class__.__name__ != other.__class__.__name__:
            return False
        return hash(self) == hash(other)


class Argument(Package):
    """
    ** Represents an argument for a function. **
    """

    def __init__(self, arg):
        self._arg = arg

    def get_value(self):
        """
        ** Accessor to retrieve the value of the argument. **

        Example
        -------
        >>> from raisin.encapsulation.packaging import Argument
        >>> Argument(0)
        Argument(0)
        >>> _.get_value()
        0
        >>>
        """
        return self._arg

    def __repr__(self):
        """
        ** Improve representation. **

        Examples
        --------
        >>> from raisin.encapsulation.packaging import Argument
        >>> Argument(0)
        Argument(0)
        >>> a = 1
        >>> Argument(a)
        Argument(1)
        >>> Argument('toto')
        Argument('toto')
        >>> Argument(10**100)
        Argument(<arg>)
        >>>
        """
        arg_name = repr(self._arg)
        if len(arg_name) > 100:
            arg_name = '<arg>'
        return f'Argument({arg_name})'

    def __getstate__(self, as_iter=False, **kwds):
        """
        ** Help for the serialization. **

        Parameters
        ----------
        as_iter : boolean
            If True, returns a generator rather than binary.
            This can be useful to preserve RAM.
        **kwds : dict
            Arguments passed to the function ``raisin.serialization.serialize``.

        Returns
        -------
        state : bytes or iterable
            Sufficient information to reconstruct the object.

        Examples
        --------
        >>> from pickle import dumps
        >>> from raisin.encapsulation.packaging import Argument
        >>> Argument(0)
        Argument(0)
        >>> type(dumps(_))
        <class 'bytes'>
        >>>
        """
        if as_iter is False:
            return b''.join(self.__getstate__(as_iter=True, **kwds))
        return serialize(self.get_value(), **kwds)

    def __setstate__(self, state, **kwds):
        """
        ** Allows you to reconstruct the object. **

        This method replaces *__init__*. It is for example used by *pickle*.

        Parameters
        ----------
        state : bytes or iterable
            The state of the object is the value returned
            by the method ``Argument.__getstate__``.
        **kwds : dict
            Arguments passed to the function ``raisin.serialization.deserialize``.

        Examples
        --------
        >>> from pickle import dumps, loads
        >>> from raisin.encapsulation.packaging import Argument
        >>> Argument(0)
        Argument(0)
        >>> loads(dumps(_))
        Argument(0)
        >>>
        """
        self._arg = deserialize(state, **kwds)


class Function(Package):
    """
    ** Encapsulate a simple function. **
    """

    def __init__(self, func):
        self._func = func

    def __repr__(self):
        """
        ** Improve representation. **

        Examples
        --------
        >>> from raisin.encapsulation.packaging import Function
        >>> def f(): pass
        >>> Function(f)
        Function(f)
        >>> g = f
        >>> Function(g)
        Function(f)
        >>> Function(lambda x : None)
        Function(<lambda>)
        >>>
        """
        return f'Function({self._func.__name__})'


class Result(Package):
    """
    ** Represents the result of a job. **
    """

    def __init__(self):
        pass


class Task(Package):
    """
    ** Complete block to perform a calculation. **
    """

    def __init__(self, func_hash, arg_hashes):
        self.func_hash = func_hash
        self.arg_hashes = arg_hashes
