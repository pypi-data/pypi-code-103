from crikit.cr.types import Space


class DirectSum(Space):
    """This space represents a concatenation of separate spaces."""

    def __init__(self, *spaces):
        if len(spaces) == 1 and isinstance(spaces[0], (tuple, list)):
            spaces = tuple(spaces[0])
        self._spaces = spaces
        if all((space == self._spaces[0]) for space in self._spaces):
            self._shape = (len(self._spaces),) + self._spaces[0].shape()
        else:
            self._shape = tuple(space.shape() for space in self._spaces)
        self._enlisted = False

    def __repr__(self):
        return "DirectSum" + str(self._spaces)

    def __eq__(self, other):
        return (
            isinstance(other, DirectSum)
            and self._shape == other._shape
            and all(mine == theirs for mine, theirs in zip(self._spaces, other._spaces))
        )

    def delist(self, y=None):
        y = self if y is None else y
        if self._enlisted:
            return y[0]
        else:
            return y

    def __getitem__(self, idx):
        """Can be used to iterate through the spaces."""
        return self._spaces[idx]

    def __len__(self):
        """Returns the number of component spaces"""
        return len(self._spaces)

    def point(self, **kwargs):
        subargs = kwargs.get("subargs", tuple(() for space in self._spaces))
        subkwargs = kwargs.get("subkwargs", tuple(dict() for space in self._spaces))
        if "near" in kwargs:
            near_point = kwargs["near"]
            for p, kw in zip(near_point, subkwargs):
                kw["near"] = p
        if "zero" in kwargs:
            zero = kwargs["zero"]
            for kw in subkwargs:
                kw["zero"] = zero
        return tuple(
            space.point(*sargs, **skwargs)
            for (space, sargs, skwargs) in zip(self._spaces, subargs, subkwargs)
        )

    def is_point(self, tup):
        if not isinstance(tup, (list, tuple)) or len(tup) != len(self._spaces):
            return False
        return all(space.is_point(point) for space, point in zip(self._spaces, tup))

    def shape(self):
        return self._shape


def enlist(spaces):
    """Given a space or a tuple of spaces, this returns a DirectSum representing
    those spaces. If the given space is already a DirectSum, it returns that
    space. Otherwise, it creates a DirectSum of the space(s) and marks it as
    enlisted so that it can delisted later.

    Args:
        spaces (Space, tuple[Space], or list[Space]): the space(s) to enlist

    Returns:
        DirectSum: a single space containing the given space(s)
    """
    if isinstance(spaces, DirectSum):
        return spaces
    else:
        dspace = DirectSum(spaces)
        dspace._enlisted = True
        return dspace


class Multiset(Space):
    """This space represents a single space repeated multiple times."""

    def __init__(self, space, n):
        self._space = space
        self._n = n
        self._shape = (n,) + space.shape()

    @property
    def space(self):
        """the base space for the Multiset"""
        return self._space

    def __repr__(self):
        return "Multiset(" + repr(self._space) + "," + repr(self._n) + ")"

    def __getitem__(self, idx):
        """Can be used to iterate through the spaces."""
        if 0 <= idx and idx < self._n:
            return self._space
        raise IndexError("index out of range")

    def __eq__(self, other):
        if (
            isinstance(other, Multiset)
            and self._space == other._space
            and self._shape == other._shape
        ):
            return True
        return False

    def __len__(self):
        """Returns the number of component spaces"""
        return self._n

    def is_point(self, tup):
        if not isinstance(tup, tuple) or len(tup) != len(self._spaces):
            return False
        return all(self._space.is_point(point) for point in tup)

    def shape(self):
        return self._shape
