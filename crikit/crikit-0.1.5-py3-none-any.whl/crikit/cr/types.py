from typing import Any, Tuple


Shape = Tuple[int, ...]


class Space:
    """Arguments / output spaces of CRs.

    A class of spaces is a representation.

    Spaces in a representation may look something like expression
    trees of operations that build new spaces recursively from
    base spaces.

    Abstract representations will have spaces that can't instantiate points as
    real data.  They have to be lowered into concrete representations.
    """

    def point(self, *args, **kwargs):
        """create a point in the space"""
        raise NotImplementedError

    def is_point(self, x: Any) -> bool:
        """test if a point is in the space"""
        raise NotImplementedError

    def shape(self) -> Shape:
        """Get the shape of the space (as in the shape of the arguments
        that you would make from a point in the space)"""
        raise NotImplementedError


class PointMap:
    """Takes points from one space and maps them into another"""

    def __init__(self, source_space, target_space):
        self._source = source_space
        self._target = target_space

    @property
    def source(self):
        """the input Space of the PointMap"""
        return self._source

    @property
    def target(self):
        """the output Space of the PointMap"""
        return self._target

    def __call__(self, point, **kwargs):
        """Apply the point map to the given point. I.e., map the given point in
        the source space to a point in the target space."""
        raise NotImplementedError

    def est_degree(self, *args, **kwargs) -> int:
        return None

    def adjoint(self, point, adj_input):
        raise NotImplementedError

    def tlm(self, point, tlm_input):
        raise NotImplementedError

    def hessian(self, arg, adj_input, tlm_input):
        raise NotImplementedError
