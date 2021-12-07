import numpy as np


class Dualnumber:
    """
        Implements the DualNumber class.
        Args:
             set_dual(int): Sets dual number value.
             add(int or float): Adds two dual numbers.
    """

    def __init__(self, a, der=1):
        self.val = a
        self.der = der

    def set_dual(self, dual):
        self.der = dual

    def __add__(self, other):
        """
            Overloads the add operation.
            Args:
                 other(Dualnumber or number): Adds number to other.
        """
        try:
            addition = Dualnumber(self.val + other.val)
            addition.der = self.der + other.der
            return addition
        except AttributeError as e:
            other = Dualnumber(other)
            addition = Dualnumber(self.val + other.val)
            addition.set_dual(self.der)
            return addition

    def __radd__(self, other):
        return self + other

    def __mul__(self, other):
        """
            Overloads the mul operation.
            Args:
                 other(Dualnumber or number): multliplies number to other.
        """
        try:
            multi = Dualnumber(self.val * other.val)
            multi.der = self.val * other.der + self.der * other.val
            return multi
        except AttributeError as e:
            multi = Dualnumber(self.val * other)
            multi.set_dual(self.der * other)
            return multi

    def __rmul__(self, other):
        return self * other

    def __sub__(self, other):
        """
            Overloads the sub operation.
            Args:
                 other(Dualnumber or number): Subtracts other from number.
        """
        try:
            subtraction = Dualnumber(self.val - other.val)
            subtraction.der = self.der - other.der
            return subtraction
        except AttributeError as e:
            other = Dualnumber(other)
            subtraction = Dualnumber(self.val - other.val)
            subtraction.set_dual(self.der)
            return subtraction

    def __rsub__(self, other):
        return (self - other) * (-1)

    def __truediv__(self, other):
        try:
            div = Dualnumber(self.val / other.val)
            div.der = (self.der * other.val - self.val * other.der) / (other.val ** 2)
            return div
        except AttributeError as e:
            div = Dualnumber(self.val / other)
            div.set_dual(self.der / other)
            return div

    def __rtruediv__(self, other):
        self.der = -self.der
        return self * (other / (self.val * self.val))

    def __pow__(self, other):
        try:
            power = Dualnumber(self.val ** other.val)
            power.der = power.val * (other.der * (np.log(self.val)) + (self.der * other.val / self.val))
            return power
        except AttributeError as e:
            # dual number raised to real number d^r
            power = Dualnumber(self.val ** other)
            power.der = power.val * (self.der * other / self.val)
            return power

    def __rpow__(self, other):
        rpower = Dualnumber(other ** self.val)
        rpower.der = rpower.val * (np.log(other) * self.der)
        return rpower

    def __neg__(self):
        return Dualnumber(-self.val, -self.der)

    def __pos__(self):
        return self

    def __eq__(self, other):
        try:
            return self.val == other.val and self.der == other.der
        except AttributeError as e:
            return self.val == other


if __name__ == '__main__':
    # test passing 2 dual numbers to add
    x = Dualnumber(1)
    y = Dualnumber(2)
    z = x + y
    assert z.val == 3
    assert z.der == 2

    # test passing 1 dual and 1 non dual number to add
    x = Dualnumber(4)
    y = 5
    z = x + y
    z_rev = y + x
    assert z.val == 9
    assert z.der == 1
    assert z_rev.val == 9
    assert z_rev.der == 1

    # test passing two real numbers to add
    x = 2
    y = 3
    z = x + y
    assert z == 5

    # test passing 2 dual numbers to subtract
    x = Dualnumber(1)
    y = Dualnumber(2)
    z = x - y
    assert z.val == -1
    assert z.der == 0

    # test passing 1 dual and 1 non dual number to subtract
    x = Dualnumber(2)
    x.set_dual(4)
    y = 5
    z = x - y
    z_inv = y - x
    assert z.val == -3
    assert z.der == 4
    assert z_inv.val == 3
    assert z_inv.der == -4

    # test 2 real nos subtraction
    x = 2
    y = 3
    assert x - y == -1

    # test passing two dual numbers to multiply
    x = Dualnumber(3)
    x.set_dual(4)
    y = Dualnumber(2)
    y.set_dual(5)
    z = x * y
    assert z.val == 6
    assert z.der == 23

    # test passing one dual number and one real number to multiply
    x = Dualnumber(3)
    x.set_dual(4)
    y = 5
    z = x * y
    z_inv = y * x
    assert z.val == 15
    assert z.der == 20
    assert z_inv.val == 15
    assert z_inv.der == 20

    # test passing two real numbers to multiply

    x = 3
    y = 2
    assert x * y == 6

    # test passing two dual numbers to divide

    x = Dualnumber(3)
    x.set_dual(4)
    y = Dualnumber(5)
    y.set_dual(3)
    z = x / y
    assert z.val == .6
    assert z.der == .44

    # test passing one dual and one real number to divide

    x = Dualnumber(5)
    x.set_dual(4)
    y = 5
    z = x / y
    z_inv = y / x
    assert z.val == 1
    assert z.der == .8
    assert z_inv.val == 1
    assert z_inv.der == -.8

    # test two real numbers to divide

    x = 3
    y = 5
    assert x / y == .6

    # test passing 2 dual numbers through power:
    x = Dualnumber(2)
    x.set_dual(3)
    y = Dualnumber(4, der=5)

    z = x ** y
    assert z.val == 16
    assert np.isclose(z.der, 151.45177444479563)

    # test passing 1 dual number and 1 int through power:
    x = Dualnumber(2, der=4)
    y = 3
    z = x ** y
    z_inv = y**x
    assert z.val == 8
    assert z.der == 48
    assert z_inv.val == 9
    assert np.isclose(z_inv.der, 4*np.log(3)*9)

    # test passing 2 dual numbers through division:
    x = Dualnumber(4)
    y = Dualnumber(2)
    z = x / y
    assert z.val == 2
    assert z.der == -0.5

    # test passing 1 dual number and 1 int through division:
    x = Dualnumber(4)
    y = 2
    z = x / y
    assert z.val == 2
    assert z.der == 0.5
