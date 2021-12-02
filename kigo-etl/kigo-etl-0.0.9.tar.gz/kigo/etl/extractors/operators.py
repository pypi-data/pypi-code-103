from operator import add
from operator import and_
from operator import contains
from operator import eq
from operator import ge
from operator import getitem
from operator import gt
from operator import inv
from operator import le
from operator import lshift
from operator import lt
from operator import mod
from operator import mul
from operator import ne
from operator import neg
from operator import or_
from operator import rshift
from operator import sub
from operator import truediv
div = truediv


class ExtractorOperator:

    def __lt__(self, other):
        """Implement the ``<`` operator."""
        return self.operate(lt, other)

    def __le__(self, other):
        """Implement the ``<=`` operator."""
        return self.operate(le, other)

    def __eq__(self, other):
        """Implement the ``==`` operator."""
        return self.operate(eq, other)

    def __ne__(self, other):
        """Implement the ``!=`` operator."""
        return self.operate(ne, other)

    def __gt__(self, other):
        """Implement the ``>`` operator."""
        return self.operate(gt, other)

    def __ge__(self, other):
        """Implement the ``>=`` operator."""
        return self.operate(ge, other)

    def __neg__(self):
        """Implement the ``-`` operator."""
        return self.operate(neg)

    def __contains__(self, other):
        return self.operate(contains, other)

    def __getitem__(self, index):
        """Implement the [] operator."""
        return self.operate(getitem, index)

    def __lshift__(self, other):
        """implement the << operator."""
        return lshift, self, other

    def __rshift__(self, other):
        """implement the >> operator."""
        return rshift, self, other

    def __radd__(self, other):
        """Implement the ``+`` operator in reverse."""
        return add, other, self

    def __rsub__(self, other):
        """Implement the ``-`` operator in reverse."""
        return sub, other, self

    def __rmul__(self, other):
        """Implement the ``*`` operator in reverse."""
        return mul, other, self

    def __rdiv__(self, other):
        """Implement the ``/`` operator in reverse."""
        return div, other, self

    def __rmod__(self, other):
        """Implement the ``%`` operator in reverse."""
        return mod, other, self

    def __add__(self, other):
        """Implement the ``+`` operator."""
        return add, self, other

    def __sub__(self, other):
        """Implement the ``-`` operator."""
        return sub, self, other

    def __mul__(self, other):
        """Implement the ``*`` operator."""
        return mul, self, other

    def __div__(self, other):
        """Implement the ``/`` operator."""
        return div, self, other

    def __mod__(self, other):
        """Implement the ``%`` operator."""
        return mod, self, other

    def __truediv__(self, other):
        """Implement the ``//`` operator."""
        return truediv, self, other

    def __rtruediv__(self, other):
        """Implement the ``//`` operator in reverse."""
        return truediv, other, self

    def operate(self, op, *other, **kwargs):
        r"""Operate on an argument."""
        print(str(op), other, kwargs)

    def reverse_operate(self, op, other, **kwargs):
        """Reverse operate on an argument."""
        print(str(op), other, kwargs)
