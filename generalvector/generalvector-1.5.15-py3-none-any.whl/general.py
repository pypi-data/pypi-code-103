
from generallibrary import typeChecker, confineTo


class _GeneralVector:
    """ GeneralVector class that Vec2 and Vec inherits for shared functions.
        Todo: Move most methods to _GeneralVector. """
    def __init__(self, *axis, length):
        axis = tuple([float(n) if typeChecker(n, str, error=False) else n for n in axis if n is not None])

        axisLen = len(axis)
        if axisLen == 0:
            self.axis = tuple([0] * length)

        elif axisLen == 1:

            if typeChecker(axis[0], _GeneralVector, error=False):
                vector = axis[0]
                if len(vector.axis) != length:
                    raise AttributeError(f"{vector} was supplied as first argument but it's axis length is not {length}")

                self.axis = vector.axis + tuple()

            else:
                typeChecker(axis[0], float)
                self.axis = tuple([axis[0]] * length)

        elif axisLen == length:
            self.axis = axis

        else:
            raise AttributeError(f"Could not handle supplied axis {axis} for {self.__class__.__name__}")

        for n in self.axis:
            typeChecker(n, float)

    def __getitem__(self, item):
        return self.axis[item]

    def sanitize(self, ints=False, positive=False, positiveOrZero=False, negative=False, negativeOrZero=False, minimum=None, maximum=None):
        """
        Sanitize this vector with a bunch of optional flags.

        :param generalvector.Vec or generalvector.Vec2 self:
        :param ints:
        :param positive:
        :param positiveOrZero:
        :param negative:
        :param negativeOrZero:
        :param generalvector.Vec or generalvector.Vec2 minimum:
        :param generalvector.Vec or generalvector.Vec2 maximum:
        :return: self
        """
        if ints and self != self.round():
            raise ValueError(f"{self} failed 'ints' sanitizing")

        if positive and not self > 0:
            raise ValueError(f"{self} failed 'positive' sanitizing")
        if positiveOrZero and not self >= 0:
            raise ValueError(f"{self} failed 'positiveOrZero' sanitizing")

        if negative and not self < 0:
            raise ValueError(f"{self} failed 'negative' sanitizing")
        if negativeOrZero and not self <= 0:
            raise ValueError(f"{self} failed 'negativeOrZero' sanitizing")

        if minimum and not self >= minimum:
            raise ValueError(f"{self} failed 'minimum' sanitizing")
        if maximum and not self <= maximum:
            raise ValueError(f"{self} failed 'maximum' sanitizing")

        if ints:
            return self.round()
        else:
            return self

    def confineTo(self, pos, size, margin=0):
        """
        Confine this vector to an area, but unlike clamp it subtracts axis * n to create an 'infinite' area effect.

        :param generalvector.Vec or generalvector.Vec2 self:
        :param generalvector.Vec or generalvector.Vec2 pos: Lowest point of area
        :param generalvector.Vec or generalvector.Vec2 size: Size of area, has to be positive or zero
        :param float margin: Margin of confinement
        """
        pos = self.__class__(pos)
        size = self.__class__(size).sanitize(positiveOrZero=True)
        maximum = pos + size

        return self.__class__(*[confineTo(axis, pos[i], maximum[i], margin) for i, axis in enumerate(self.axis)])

    def absolute(self):
        """
        Return this vector with absolute values.

        :param generalvector.Vec or generalvector.Vec2 self:
        """
        return self.__class__(*[abs(axis) for axis in self.axis])












