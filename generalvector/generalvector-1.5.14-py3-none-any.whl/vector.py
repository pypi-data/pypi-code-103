
from math import sqrt

import random

from generallibrary import clamp, inrange, typeChecker
from generalvector.general import _GeneralVector


class Vec(_GeneralVector):
    """
    Immutable vector.
    """
    def __init__(self, x=None, y=None, z=None):
        _GeneralVector.__init__(self, x, y, z, length=3)

        self.x = self.axis[0]
        self.y = self.axis[1]
        self.z = self.axis[2]

    def __str__(self):
        return f"Vec({self.x}, {self.y}, {self.z})"

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        if typeChecker(other, _GeneralVector, error=False):
            return self.x == other.x and self.y == other.y and self.z == other.z
        else:
            return self.x == other and self.y == other and self.z == other

    def __add__(self, other):
        other = Vec(other)
        return Vec(self.x + other.x, self.y + other.y, self.z + other.z)

    def __neg__(self):
        return Vec(-self.x, -self.y, -self.z)

    def __sub__(self, other):
        return self + -other

    def __mul__(self, other):
        other = Vec(other)
        return Vec(self.x * other.x, self.y * other.y, self.z * other.z)

    def __truediv__(self, other):
        other = Vec(other)
        return Vec(self.x / other.x, self.y / other.y, self.z / other.z)

    def __lt__(self, other):
        other = Vec(other)
        return self.x < other.x and self.y < other.y and self.z < other.z

    def __gt__(self, other):
        other = Vec(other)
        return self.x > other.x and self.y > other.y and self.z > other.z

    def __le__(self, other):
        other = Vec(other)
        return self.x <= other.x and self.y <= other.y and self.z <= other.z

    def __ge__(self, other):
        other = Vec(other)
        return self.x >= other.x and self.y >= other.y and self.z >= other.z

    def length(self):
        """
        Get the length of this vector using pythagorean theorem.
        """
        return sqrt(self.x ** 2 + self.y ** 2 + self.z ** 2)

    def normalized(self):
        """
        Get this vector normalized by dividing each value by it's length.
        """
        length = self.length()
        if length == 0:
            return Vec(0)
        return self / length

    def round(self):
        """
        Get this vector with each value rounded.
        """
        return Vec(round(self.x), round(self.y), round(self.z))

    @staticmethod
    def random(value1, value2=None):
        """
        Get a vector with random values.

        :param float or Vec value1: Minimum value if value2 is specified too. Otherwise it's the maximum value and minimum becomes 0
        :param float or Vec value2: Optional maximum value
        """
        if value2 is None:
            value2 = Vec(value1)
            value1 = Vec(0)
        else:
            value2 = Vec(value2)
            value1 = Vec(value1)
        return Vec(random.uniform(value1.x, value2.x), random.uniform(value1.y, value2.y), random.uniform(value1.z, value2.z))

    def min(self, minimum):
        """
        Get a new vector containing the minimum value for each value in the two vectors.

        :param float or Vec minimum: Minimum value, floats are converted to Vec
        """
        minimum = Vec(minimum)
        return Vec(min(self.x, minimum.x), min(self.y, minimum.y), min(self.z, minimum.z))

    def max(self, maximum):
        """
        Get a new vector containing the maximum value for each value in the two vectors.

        :param float or Vec maximum: Minimum value, floats are converted to Vec
        """
        maximum = Vec(maximum)
        return Vec(max(self.x, maximum.x), max(self.y, maximum.y), max(self.z, maximum.z))

    def clamp(self, minimum, maximum):
        """
        Get this vector clamped between two values as a new vector.

        :param float or Vec minimum: Minimum value, floats are converted to Vec
        :param float or Vec maximum: Maximum value, floats are converted to Vec
        """
        minimum = Vec(minimum)
        maximum = Vec(maximum)
        return Vec(clamp(self.x, minimum.x, maximum.x), clamp(self.y, minimum.y, maximum.y), clamp(self.z, minimum.z, maximum.z))

    def inrange(self, minimum, maximum):
        """
        Return whether this vector is between two other vectors.

        :param float or Vec minimum: Minimum value, floats are converted to Vec
        :param float or Vec maximum: Maximum value, floats are converted to Vec
        """
        return inrange(self.x, minimum.x, maximum.x) and inrange(self.y, minimum.y, maximum.y) and inrange(self.z, minimum.z, maximum.z)

    def hex(self):
        """
        Get a hex based on each value. Rounded and clamped between 0 and 255.
        """
        rounded = self.round().clamp(0, 255)
        return f"#{'%02x' % rounded.x}{'%02x' % rounded.y}{'%02x' % rounded.z}"

    def range(self, size):
        """
        Get a range from two vectors.
        Self is upper left corner.
        A size of Vec(1, 1) will return 1 Vec.

        :param Vec size: Size of range.
        :rtype: list[Vec]
        """
        self.sanitize(ints=True)
        size = Vec(size).sanitize(ints=True, positiveOrZero=True)

        rangeList = []
        for z in range(size.z):
            for y in range(size.y):
                for x in range(size.x):
                    rangeList.append(self + Vec(x, y, z))
        return rangeList

    def distance(self, other):
        """
        Return distance between two Vectors.

        :param other: Another Vec
        """
        return (self - other).length()













