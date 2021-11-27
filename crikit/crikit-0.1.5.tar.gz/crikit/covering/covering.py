from crikit.cr.space_builders import DirectSum
from crikit.cr.map_builders import CompositePointMap, IdentityPointMap, ParallelPointMap
from crikit.cr.types import Space, PointMap
from typing import Optional


class Covering:
    """Base class for Covering types.

    To be compatible with the covering params structure, the constructor
    should accept all keywords arguments and just ignore the ones that it
    doesn't need.

    """

    def __init__(self, base_space, covering_space, **covering_params):
        self._base_space = base_space
        self._covering_space = covering_space

    def covering_map(self, **params) -> PointMap:
        """This method must be overridden.

        Should return a map from the covering space to the base space.

        Args:
            **params: any parameters that should be used for creating the map.

        Returns:
            PointMap: A map from the covering space to the base space.

        """
        raise NotImplementedError

    def section_map(self, **params) -> PointMap:
        """This method must be overridden.

        Should return a map from the base space to the covering space.

        Args:
            **params: any parameters that should be used for creating the map.

        Returns:
            PointMap: A map from the base space to the covering space.

        """
        raise NotImplementedError

    def bundle_map(self, covering_params=None, section_params=None) -> PointMap:
        raise NotImplementedError


_covering_registry = {}
_default_covering_params = {}


def get_default_covering_params() -> dict:
    """
    Returns:
        dict: a reference to the current covering params dictionary
    """
    return _default_covering_params


def set_default_covering_params(*args, **kwargs) -> None:
    """Update the covering params dictionary.

    Args:
        *args: dictionaries with key-value pairs to add to the covering params
            dictionary.
        **kwargs: key-value pairs to add to the covering params dictionary.
    """
    for a in args:
        _default_covering_params.update(a)
    _default_covering_params.update(kwargs)


def reset_default_covering_params() -> None:
    """Resets the default covering params to an empty dictionary."""
    global _default_covering_params
    _default_covering_params = {}


def register_covering(
    base_space: Space, covering_space: Space, covering_class: Optional[Covering] = None
) -> Covering:
    """Register a covering class for use in :func:`get_map`

    The ``covering_class`` should be defined with a ``covering_map`` method that
    returns a point map mapping from ``covering_space`` to ``base_space``, and a
    ``section_map`` method that returns a point map from ``base_space`` to
    ``covering_space``.

    This function can be used as a class decorator, in which case the
    ``covering_class`` doesn't need to be specified.

    Args:
        base_space (type): a Space subclass.
        covering_space (type): a Space subclass.
        covering_class (type): the Covering subclass to register as handling
            (base_space, covering_space) mappings.

    Returns:
        type: returns ``covering_class`` such that it can be used as a decorator.

    """
    if covering_class is None:
        # decorator mode.
        def decorator(covering_class):
            register_covering(base_space, covering_space, covering_class)
            return covering_class

        return decorator
    _covering_registry[(base_space, covering_space)] = covering_class
    return covering_class


def get_map(source: Space, target: Space, **covering_params) -> PointMap:
    """Creates a map from ``source`` to ``target`` using the Covering registry. If a
    mapping from source to target is not found in the registry, it raises an
    exception.

    If ``source`` and ``target`` are DirectSums of multiple spaces, they must each
    have the same number of spaces. In that case, the i-th subspace in the
    source is mapped individually to the i-th subspace in the target space.

    Any additional kwargs are passed to the covering constructor.

    Args:
        source (Space): The source space.
        target (Space): The target space.
        **covering_params: Parameters to pass to the covering class constructor.

    Returns:
        PointMap: A map from the source space to the target space.

    """
    if source == target:
        return IdentityPointMap(s, t)

    if (
        isinstance(source, DirectSum)
        and isinstance(target, DirectSum)
        and len(source) == len(target)
    ):
        return ParallelPointMap(
            *tuple(get_map(s, t, **covering_params) for s, t in zip(source, target))
        )

    params = get_default_covering_params().copy()
    params.update(covering_params)

    s_type = type(source)
    t_type = type(target)
    covering_class = _covering_registry.get((s_type, t_type), None)
    if covering_class is not None:
        covering = covering_class(source, target, **params)
        return covering.section_map()
    covering_class = _covering_registry.get((t_type, s_type), None)
    if covering_class is not None:
        covering = covering_class(target, source, **params)
        return covering.covering_map()
    msg = "Don't have a covering for %s and %s with shapes %s and %s" % (
        s_type,
        t_type,
        source.shape(),
        target.shape(),
    )
    msg = msg + "\n        source space: %s, target space: %s" % (source, target)
    raise NotImplementedError(msg)


def get_composite_cr(*args, **covering_params) -> PointMap:
    """Creates a map that composes the given PointMaps and/or Spaces by using
    covering maps to convert between Spaces.

    Any kwargs are passed to :func:`get_map`.

    For example, ``get_composite_cr(space1, cr1, cr2, space2)`` returns a
    :class:`~crikit.cr.map_builders.CompositePointMap` that does the following:

    - takes input in ``space1``,
    - converts it to input to ``cr1``,
    - applies ``cr1``
    - converts the output to the input space of ``cr2``
    - applies ``cr2``
    - and then converts the output to ``space2``.

    The conversion point maps are created using the :func:`get_map` function.

    Args:
        *args (Space or PointMap): the PointMaps that should be applied and any
            desired spaces to convert to.
        **covering_params: Parameters to pass to the covering class constructor.

    Returns:
        PointMap: A map from the source space to the target space.

    """

    if len(args) == 0:
        return

    if isinstance(args[0], PointMap):
        previous_space = args[0].source
    elif isinstance(args[0], Space):
        previous_space = args[0]
    else:
        raise ValueError(
            "Found input argument that is neither a Space nor a PointMap:"
            + str(args[0])
        )

    maps = []
    for a in args:
        if isinstance(a, PointMap):
            # Map from previous space to this point map's input space and then apply the point map.
            if previous_space != a.source:
                maps.append(get_map(previous_space, a.source, **covering_params))
            maps.append(a)
            previous_space = a.target
        elif isinstance(a, Space):
            # Map from previous space to current space.
            if previous_space != a:
                maps.append(get_map(previous_space, a, **covering_params))
            previous_space = a
        else:
            raise ValueError(
                "Found input argument that is neither a Space nor a PointMap:" + str(a)
            )
    return CompositePointMap(maps)
