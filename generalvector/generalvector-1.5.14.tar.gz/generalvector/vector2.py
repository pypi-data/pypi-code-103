
from generallibrary import clamp, inrange, typeChecker
from generalvector.general import _GeneralVector

from math import sqrt
import random


class Vec2(_GeneralVector):
    """
    Immutable vector2.
    """
    def __init__(self, x=None, y=None):
        _GeneralVector.__init__(self, x, y, length=2)

        self.x = self.axis[0]
        self.y = self.axis[1]

    def __str__(self):
        return f"Vec2({self.x}, {self.y})"

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        if typeChecker(other, _GeneralVector, error=False):
            return self.x == other.x and self.y == other.y
        else:
            return self.x == other and self.y == other

    def __add__(self, other):
        other = Vec2(other)
        return Vec2(self.x + other.x, self.y + other.y)

    def __neg__(self):
        return Vec2(-self.x, -self.y)

    def __sub__(self, other):
        other = Vec2(other)
        return self + -other

    def __mul__(self, other):
        other = Vec2(other)
        return Vec2(self.x * other.x, self.y * other.y)

    def __truediv__(self, other):
        other = Vec2(other)
        """:param float or Vec2 other:"""
        return Vec2(self.x / other.x, self.y / other.y)

    def __lt__(self, other):
        other = Vec2(other)
        return self.x < other.x and self.y < other.y

    def __gt__(self, other):
        other = Vec2(other)
        return self.x > other.x and self.y > other.y

    def __le__(self, other):
        other = Vec2(other)
        return self.x <= other.x and self.y <= other.y

    def __ge__(self, other):
        other = Vec2(other)
        return self.x >= other.x and self.y >= other.y

    def length(self):
        """
        Get the length of this vector using pythagorean theorem.
        """
        return sqrt(self.x ** 2 + self.y ** 2)

    def normalized(self):
        """
        Get this vector2 normalized by dividing each value by it's length.
        """
        length = self.length()
        if length == 0:
            return Vec2(0)
        return self / length

    def round(self):
        """
        Get this vector2 with each value rounded.
        """
        return Vec2(round(self.x), round(self.y))

    @staticmethod
    def random(value1, value2=None):
        """
        Get a vector2 with random values.

        :param float or Vec2 value1: Minimum value if value2 is specified too. Otherwise it's the maximum value and minimum becomes 0
        :param float or Vec2 value2: Optional maximum value
        """
        if value2 is None:
            value2 = Vec2(value1)
            value1 = Vec2(0)
        else:
            value2 = Vec2(value2)
            value1 = Vec2(value1)
        return Vec2(random.uniform(value1.x, value2.x), random.uniform(value1.y, value2.y))

    def min(self, minimum):
        """
        Get a new vector2 containing the minimum value for each value in the two vectors2.

        :param float or Vec2 minimum: Minimum value, floats are converted to Vec2
        """
        minimum = Vec2(minimum)
        return Vec2(min(self.x, minimum.x), min(self.y, minimum.y))

    def max(self, maximum):
        """
        Get a new vector2 containing the maximum value for each value in the two vectors2.

        :param float or Vec2 maximum: Minimum value, floats are converted to Vec2
        """
        maximum = Vec2(maximum)
        return Vec2(max(self.x, maximum.x), max(self.y, maximum.y))

    def clamp(self, minimum, maximum):
        """
        Get this vector2 clamped between two values.
        :param float or Vec2 minimum: Minimum value, floats are converted to Vec2
        :param float or Vec2 maximum: Maximum value, floats are converted to Vec2
        """
        minimum = Vec2(minimum)
        maximum = Vec2(maximum)
        return Vec2(clamp(self.x, minimum.x, maximum.x), clamp(self.y, minimum.y, maximum.y))

    def inrange(self, minimum, maximum):
        """
        Return whether this vector2 is between two other vector2s.

        :param float or Vec2 minimum: Minimum value, floats are converted to Vec2
        :param float or Vec2 maximum: Maximum value, floats are converted to Vec2
        """
        minimum = Vec2(minimum)
        maximum = Vec2(maximum)
        return inrange(self.x, minimum.x, maximum.x) and inrange(self.y, minimum.y, maximum.y)

    def range(self, size):
        """
        Get a range from two vector2s.
        Self is upper left corner.
        A size of Vec2(1, 1) will return 1 Vec2.

        :param Vec2 size: Size of range.
        :rtype: list[Vec2]
        """
        self.sanitize(ints=True)
        size = Vec2(size).sanitize(ints=True, positiveOrZero=True)

        rangeList = []
        for y in range(size.y):
            for x in range(size.x):
                rangeList.append(self + Vec2(x, y))
        return rangeList

    def distance(self, other):
        """
        Return distance between two Vector2s.

        :param other: Another Vec2
        """
        return (self - other).length()

























