from pyadjoint.overloaded_type import register_overloaded_type
from pyadjoint.adjfloat import AdjFloat
import numpy
from .array import ndarray
from .autograd import overload_autograd

register_overloaded_type(AdjFloat, int)
register_overloaded_type(AdjFloat, numpy.float64)
register_overloaded_type(AdjFloat, numpy.float32)
register_overloaded_type(AdjFloat, numpy.int64)
register_overloaded_type(AdjFloat, numpy.int32)
