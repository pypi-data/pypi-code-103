from crikit.cr.types import Space
from crikit.cr.space_builders import DirectSum
from crikit.cr.map_builders import Callable
from functools import update_wrapper


class Numbers(Space):
    def __init__(self, name, pointclass, compat_classes=()):
        self._name = name
        self._pointclass = pointclass
        self._compat_classes = frozenset(compat_classes + (pointclass,))

    def shape(self):
        return ()

    def __str__(self):
        return self._name

    def point(self, **kwargs):
        return self._pointclass(0)

    def is_point(self, point):
        if isinstance(point, self._compat_classes):
            return True
        return False


class Integers(Numbers):
    def __init__(self, name=None):
        _name = "ZZ(std)" if name is None else name
        super(Integers, self).__init__(_name, int)


ZZ = Integers()  #: Represents the space of integers


class Reals(Numbers):
    def __init__(self, name=None):
        _name = "RR(std)" if name is None else name
        super(Reals, self).__init__(_name, float, (int,))


RR = Reals()  #: Represents the space of real numbers


class Complexs(Numbers):
    def __init__(self, name=None):
        _name = "CC(std)" if name is None else name
        super(Complexs, self).__init__(_name, complex, (int, float))


CC = Complexs()  #: Represents the space of complex numbers


def type_tuple_to_space(tt):
    """Converts the given numeric type or tuple of types to a Space using the
    stdnumeric spaces and DirectSum.

    If ``tt`` is a tuple, :code:`type_tuple_to_space()` is recursively called on
    each element of the tuple, and the DirectSum of the result is returned.

    If ``tt`` is a numeric type, then the corresponding stdnumeric Space is
    returned. If ``tt`` is a subclass of a numeric type, the name of the
    returned space will contain the name of that class.

    Supported numeric types are :class:`int`, :class:`float`, :class:`complex`,
    or subclasses of those types.

    Args:
        tt: a numeric type or arbitrarily nested tuples of numeric types.

    Returns:
        Space: the stdnumeric Space corresponding to the given types.

    Todo:
        * Use numbers.Integral/Real/Complex to find the corresponding space,
    """
    if isinstance(tt, type):
        stdnumeric = (
            (int, ZZ, Integers, "ZZ"),
            (float, RR, Reals, "RR"),
            (complex, CC, Complexs, "CC"),
        )
        for numbers in stdnumeric:
            if issubclass(tt, numbers[0]):
                if tt == numbers[0]:
                    return numbers[1]
                else:
                    return numbers[2](f"{numbers[3]}({tt!s})")
        raise NotImplementedError
    elif isinstance(tt, tuple):
        return DirectSum(*tuple(map(type_tuple_to_space, tt)))
    else:
        raise NotImplementedError


def point_map(source_types, target_types, **kwargs):
    """Decorates a function to make it a point map (by constructing a Callable
    instance).

    Args:
        source_types: a type tuple representing the source space.
        target_types: a type tuple representing the target space.
        **kwargs: passed through to the :class:`~crikit.cr.map_builders.Callable` constructor.

    Here's example usage for calculating the p-norm of a two-dimensional vector:

    .. testcode::

        from crikit.cr.stdnumeric import point_map

        @point_map(((float, float), float), float, bare=True)
        def pnorm_2d(v, p):
            return (v[0]**p + v[1]**p) ** (1/p)
        assert pnorm_2d(((1, 2), 1)) == 3

        from crikit.cr.types import PointMap
        from crikit.cr.space_builders import DirectSum
        from crikit.cr.stdnumeric import RR

        assert isinstance(pnorm_2d, PointMap)
        assert pnorm_2d.source == DirectSum(DirectSum(RR, RR), RR)
        assert pnorm_2d.target == RR
    """

    source_space = type_tuple_to_space(source_types)
    target_space = type_tuple_to_space(target_types)

    def point_map_decorator(func):
        pm = Callable(source_space, target_space, func, **kwargs)
        return pm

    return point_map_decorator
