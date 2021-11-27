from crikit.cr.types import PointMap
from crikit.cr.space_builders import DirectSum, Multiset, enlist
from pyadjoint.enlisting import Enlist
from functools import update_wrapper
from itertools import chain
from typing import Union, Iterable, TypeVar, Optional, List

# these TypeVars represent generic points in the input, output,
# and parameter spaces of various PointMaps
InputPoint = TypeVar("InputPoint")
ParameterPoint = TypeVar("ParameterPoint")
OutputPoint = TypeVar("OutputPoint")


class Callable(PointMap):
    """This class wraps a Python callable into a PointMap.

    I.e., if you (1) have a function or a class/object with a ``__call__`` method,
    and you (2) know the input space and output space of the callable, then this
    will put the callable into the Space/PointMap structure.

    Set bare to true if the callable requires that the point be unpacked.

    A point map that accepts multiple inputs will receive those inputs as a
    single tuple, so if your callable expects to receive them as separate
    arguments, you must use ``bare=True``.

        >>> from crikit.cr.map_builders import Callable
        >>> source = ... # The source and target space don't really matter here.
        >>> target = ...
        >>> standard_callable = lambda x: x[0] + x[1] + x[2]
        >>> c = Callable(source, target, standard_callable)
        >>> c((1, 2, 3))
        6
        >>> bare_callable = lambda a, b, c: a + b + c
        >>> c_bare = Callable(source, target, bare_callable, bare=True)
        >>> c_bare((1, 2, 3))
        6
        >>> c_bad = Callable(source, target, bare_callable, bare=False)
        >>> c_bad((1, 2, 3))
        Traceback (most recent call last):
        ...
        TypeError: <lambda>() missing 2 required positional arguments: 'b' and 'c'
        >>> c_bad(1, 2, 3)
        Traceback (most recent call last):
        ...
        TypeError: __call__() takes 2 positional arguments but 4 were given

    TODO:
        * Define a function decorator to make it easier to use.
    """

    def __init__(self, source_space, target_space, callble, bare=False):
        assert callable(callble)
        super(Callable, self).__init__(source_space, target_space)
        self._callable = callble
        self._bare = bare
        update_wrapper(self, self._callable)

    @property
    def callable(self):
        """the callable that this point map was initialized with"""
        return self._callable

    def __call__(self, point, **kwargs):
        """Calls the callable with given point, unpacking the point first if
        initialized with ``bare=True``"""
        if self._bare:
            return self._callable(*point, **kwargs)
        else:
            return self._callable(point, **kwargs)


class AugmentPointMap(PointMap):
    """This class wraps a PointMap so that keyword arguments of its ``__call__``
    method are moved to the explicit input space of the map.

    In mathematical notation, this wraps a function :math:`f(u; p)` so that it must be called as :math:`f(u, p)`.

    If the original point map is called as :code:`point_map(point)`, then the augmented point map
    is called as :code:`aug_map((point, params))` (or :code:`aug_map((point, *params)` if :code:`bare=True`).

    Args:
        point_map (PointMap): The point map to wrap.
        param_names (str, tuple[str], or list[str]): The keywords that will be
            added to the input space of the point map.
        param_space (Space, tuple[Space], or list[Space]): The spaces
            corresponding to each keyword in the param_names list.
        bare (bool): If you set this to true, then the ``__call__`` method
            expects the params to be unpacked.

    TODO:
        * Rename the class to ``Augment`` to match Callable and Parametric?
            * Or rename the other ones to match CompositePointMap and ParallelPointMap?
        * Maybe rename bare to bare_params and add a new parameter called bare_point.
          If they're both true, then map can be called as ``aug_map((*point, *params))``.
    """

    def __init__(self, point_map, param_names, param_space, bare=False):
        param_names = Enlist(param_names)
        if bare:
            param_space = enlist(param_space)
            self._param_len = len(param_space)
            new_source = DirectSum(tuple(chain(enlist(point_map.source), param_space)))
        else:
            new_source = DirectSum(point_map.source, param_space)

        self._bare = bare
        self._point_map = point_map
        self._param_names = param_names
        self._param_space = param_space
        super().__init__(new_source, point_map.target)

    def __call__(self, point_params, **kwargs):
        """
        Args:
            point_params: the point at which to evaluate the point map and the
                params to pass as keyword args. It must be in the form ``(point,
                params)`` (or ``(point, *params)`` if ``bare=True`` was passed
                in the constructor).

        Returns:
            The output of the base point map.
        """
        point = point_params[0]
        if self._bare:
            params = point_params[-self._param_len :]
        else:
            if len(point_params) != 2:
                raise ValueError(
                    "Expected a tuple of length 2 in the form (point, params),"
                    " but got a tuple of length %d. (Did you mean to use bare=True?)"
                    % len(point_params)
                )
            params = point_params[1]
            if not isinstance(self._param_space, DirectSum):
                params = [params]

        if len(params) != len(self._param_names):
            raise ValueError("")
        for name, val in zip(self._param_names, params):
            if name in kwargs:
                raise ValueError(
                    "%s specified as both a positional argument and keyword argument"
                    % name
                )
            kwargs[name] = val
        return self._point_map(point, **kwargs)


class Parametric(PointMap):
    """This class wraps a PointMap so that some parameters do not need to be
    specified when the point map is called.

    In mathematical notation, this wraps a function :math:`f(u, p)` so that it can be called as
    :math:`f(u)` or as :math:`f(u; p)` with some default value of p if p is not specified.

    Args:
        orig_map (PointMap): The point map to wrap.
        param_indices (int, tuple[int], or list[int]): The position of the
            parameters in the input space of the point map.
        param_point: The default values to use for the parameters if they are
            not specified in the :meth:`__call__` method.
        bare (bool): If you set this to true, then the number of remaining args
            to the point map (after removing the param_indices) must be 1, in
            which case the resulting Parametric map can be called as pmap(val)
            instead of pmap((val,)).
        bare_map (bool): If true, then the args to the point map will be
            unpacked before calling the map.
            Note: We should probably get rid of this since we're now requiring
            that PointMaps not accept bare arguments (I.e., all PointMap
            __call__ functions must accept a single arg, which is either a
            single value or a tuple of values if necessary).
    """

    def __init__(
        self,
        orig_map: PointMap,
        param_indices: Union[int, Iterable[int]],
        param_point: InputPoint,
        bare: Optional[bool] = False,
        bare_map: Optional[bool] = False,
    ):
        orig_source = orig_map.source
        if isinstance(param_indices, int):
            bare_param = True
            param_indices = (param_indices,)
        else:
            bare_param = False
        comp_indices = tuple(
            sorted(frozenset(range(len(orig_source))) - frozenset(param_indices))
        )
        if isinstance(orig_source, DirectSum):
            new_source = DirectSum(*tuple(orig_source[i] for i in comp_indices))
            param_space = DirectSum(*tuple(orig_source[i] for i in param_indices))
        elif isinstance(orig_source, Multiset):
            new_source = Multiset(
                orig_source.space, len(orig_source) - len(param_indices)
            )
            param_space = Multiset(orig_source.space, len(param_indices))
        if bare:
            assert len(new_source) == 1
            new_source = new_source[0]
        if bare_param:
            param_space = param_space[0]
        super(Parametric, self).__init__(new_source, orig_map.target)
        self._orig_map = orig_map
        self._comp_indices = comp_indices
        self._param_space = param_space
        self._param_indices = param_indices
        self._param_point = param_point
        self._bare_point = bare
        self._bare_param = bare_param
        self._bare_map = bare_map

    def __repr__(self):
        if self._bare_param:
            return f"Parametric({self._orig_map!r},arg[{self._param_indices[0]}]={self._param_point})"
        else:
            return f"Parametric({self._orig_map!r},arg[{self._param_indices}]={self._param_point})"

    def __call__(
        self, point: InputPoint, params: Optional[ParameterPoint] = None, **kwargs
    ) -> OutputPoint:
        """
        Args:
            point: point at which to evaluate the point map
            params: parameter values to use for the point map. If None, then the
                default param_point will be used.
            **kwargs: keyword arguments are passed through to the base point map.

        Returns:
            The output of the base point map.
        """
        params = self._param_point if not params else params
        full = [None] * len(self._orig_map.source)
        if self._bare_point:
            point = (point,)
        if self._bare_param:
            params = (params,)
        for i, j in enumerate(self._param_indices):
            full[j] = params[i]
        for i, j in enumerate(self._comp_indices):
            full[j] = point[i]
        full = tuple(full)
        if self._bare_map:
            return self._orig_map(*full, **kwargs)
        else:
            return self._orig_map(full, **kwargs)

    def set_param_point(self, param_point: ParameterPoint) -> None:
        """Sets the default value to use for the parameters."""
        self._param_point = param_point


class CompositePointMap(PointMap):
    """This class is a point map that links a group of point maps.

    Given a list of point maps, the source space is the source space of the
    first point map, and the target space is the target space of the last point
    map.

    The __call__ function gives the inputs to the first map, and then
    successively feeds the outputs of one map to the next map.

    """

    def __init__(self, *point_maps):
        # This allows CompositePointMap(map_list) or CompositePointMap(*map_list).
        if len(point_maps) == 1 and isinstance(point_maps[0], (list, tuple)):
            point_maps = point_maps[0]
        self._point_maps = point_maps

        source = self._point_maps[0].source
        target = self._point_maps[-1].target
        super().__init__(source, target)

    def __repr__(self):
        return f"CompositePointMap{tuple(self._point_maps)}"

    def __call__(self, args: InputPoint) -> OutputPoint:
        for point_map in self._point_maps:
            args = point_map(args)
        return args

    def point_maps(self) -> List[PointMap]:
        """Returns a list of the point maps used to create this composite map."""
        return self._point_maps


class ParallelPointMap(PointMap):
    """This class is a point map that runs a group of point maps independently.

    Given a list of point maps, the source space is a DirectSum of the source
    space from each point map, and similarly for the target space.

    The __call__ function gives each argument to the corresponding point map,
    and concatenates the outputs into a single list.

    """

    def __init__(self, *point_maps):
        if len(point_maps) == 1 and isinstance(point_maps, (tuple, list)):
            point_maps = tuple(point_maps[0])
        self._point_maps = point_maps
        source = DirectSum(*tuple(point_map.source for point_map in self._point_maps))
        target = DirectSum(*tuple(point_map.target for point_map in self._point_maps))

        super().__init__(source, target)

    def __call__(self, arg):
        return tuple(p(a) for p, a in zip(self._point_maps, arg))


class IdentityPointMap(PointMap):
    """This class is a point map that simply returns its input."""

    def __call__(self, point: InputPoint, **kwargs) -> InputPoint:
        return point


class FunnelOut(PointMap):
    """Makes n copies of its input"""

    def __init__(self, source_space, n):
        self._n = n
        target_space = DirectSum((source_space,) * n)
        super().__init__(source_space, target_space)

    def __call__(self, arg: InputPoint) -> OutputPoint:
        return (arg,) * self._n
