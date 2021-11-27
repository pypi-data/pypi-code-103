import jax.numpy as jnp
import numpy as np
import jax
from jax.ops import index_update
from jax.tree_util import (
    register_pytree_node,
    register_pytree_node_class,
    tree_flatten,
    tree_unflatten,
)
from jax.tree_util import Partial as partial
from pyadjoint.overloaded_function import overload_function
from pyadjoint.overloaded_type import (
    OverloadedType,
    register_overloaded_type,
    create_overloaded_object,
)
from pyadjoint.tape import get_working_tape, stop_annotating, annotate_tape
from pyadjoint_utils.block import Block
from pyadjoint_utils.convert import make_convert_block
from pyadjoint_utils.adjfloat import AdjFloat
from pyadjoint import AdjFloat, Control
from typing import Any, Iterable, Sequence, Union, Optional, Tuple
from .blocks import AddBlock, SubBlock, PowBlock, MulBlock, DivBlock, NegBlock

Array = Any
Shape = Sequence[int]

_default_dtype = jnp.float64


def set_default_dtype(dtype: jnp.dtype) -> None:
    """Sets the default data type for jax arrays used inside crikit. Default jax.numpy.float64.

    :param dtype: the default data type to set
    :type dtype: Union[jnp.dtype,str,Tuple[Union[jnp.dtype,str]]]
    :returns: None

    """
    global _default_dtype
    dtype = jnp.dtype(dtype)
    _default_dtype = dtype


def get_default_dtype() -> jnp.dtype:
    """Returns the default CRIKit JAX dtype

    :returns: CRIKit default JAX dtyle
    :rtype: jnp.dtype

    """
    return _default_dtype


# similar to what pyadjoint defines in adjfloat.py
def annotate_operator(orig_operator, nojit=False):
    """Decorates an operator like __add__, __sub__, etc.
    with JAX JIT compilation.
    """

    def reverse(block):
        def _reversed_block(operator, args, output):
            return block(operator, (args[1], args[0]), output)

        return _reversed_block

    op_map = {
        "__neg__": (lambda x: -x, NegBlock),
        "__add__": (lambda x, y: x + y, AddBlock),
        "__mul__": (lambda x, y: x * y, MulBlock),
        "__truediv__": (lambda x, y: x / y, DivBlock),
        "__rtruediv__": (lambda x, y: y / x, reverse(DivBlock)),
        "__sub__": (lambda x, y: x - y, SubBlock),
        "__pow__": (lambda x, y: x ** y, PowBlock),
        "__radd__": (lambda x, y: y + x, reverse(AddBlock)),
        "__rmul__": (lambda x, y: y * x, reverse(MulBlock)),
        "__rsub__": (lambda x, y: y - x, reverse(SubBlock)),
        "__rpow__": (lambda x, y: y ** x, reverse(PowBlock)),
    }

    def is_unitary(op):
        # only one unary operator right now
        return op.__name__ == "__neg__"

    op, block_ctor = op_map[orig_operator.__name__]
    if not nojit:
        op = jax.jit(op)

    def annotated_operator(*args):
        # args[0] is always self
        output = args[0].__class__(op(*(convert_arg(x) for x in args)))
        args = [
            arg if isinstance(arg, OverloadedType) else create_overloaded_object(arg)
            for arg in args
        ]
        if annotate_tape():
            block = block_ctor(op, args, output)
            tape = get_working_tape()
            tape.add_block(block)
            block.add_output(output.block_variable)

        return output

    annotated_operator.__name__ = orig_operator.__name__
    return annotated_operator


@register_pytree_node_class
class ndarray(OverloadedType):
    def __repr__(self):
        return f"ndarray({self.arr.__repr__()})"

    def __array__(self, dtype=None):
        if dtype:
            if hasattr(self.arr, "__array__"):
                return self.arr.__array__(dtype=dtype)
            else:
                return np.array(self.arr).__array__(dtype=dtype)
        else:
            if hasattr(self.arr, "__array__"):
                return self.arr.__array__()
            else:
                return np.array(self.arr).__array__()

    def __float__(self):
        return float(self.unwrap(True))

    def __iter__(self):
        return self.arr.__iter__()

    def __init__(self, obj: Array, *args, **kwargs):
        """Note: you should not typically use this constructor directly in your code. Instead, you should call
        :func:`array` or :func:`asarray`, which will call the constructor of this class when appropriate.


        :param obj: the object to wrap; should be either a JAX ndarray or something
            that can be converted to one (such as a list or tuple of floats or ints,
            or a float or int, or a numpy ndarray)
        :type obj: jax.interpreters.xla.DeviceArray
        :return: a class that wraps a JAX array (such that it can be added to the JAX Pytree
            and thus used as an argument to a differentiable function) to be passed to a
            function wrapped with `overload_jax()`, while also inheriting from
            pyadjoint.OverloadedType
            (since you can't inherit from a JAX array;
            see https://github.com/google/jax/issues/4269).
        :rtype: ndarray

        """
        dtype = kwargs.get("dtype", np.float64)
        self.arr = obj
        self.extras = args
        super().__init__()

    @property
    def value(self):
        return self.arr

    @value.setter
    def value(self, new_jax_array):
        self.arr = new_jax_array

    @property
    def dtype(self):
        return self.arr.dtype

    @property
    def ndim(self):
        return self.arr.ndim

    def unwrap(self, to_jax: bool = True) -> jnp.ndarray:
        """
        If this ndarray holds recursively nested ndarrays (e.g. its __repr__() is ndarray(ndarray(...))), unwrap until it holds the array data contained in the deepest-nested ndarray.

        This is mostly a utility for use in jacfwd and jacrev in pyadjoint_utils/numpy_adjoint/jax.py

        :param to_jax: go one level further and return the raw JAX array (instead of ndarray, the OverloadedType wrapper)?, defaults to False
        :type to_jax: bool, optional
        :return: unwrapped version of self
        :rtype: jax.interpreters.xla.DeviceArray
        """
        newarr = self.arr
        while isinstance(newarr, ndarray):
            newarr = newarr.arr

        if isinstance(newarr, (list, tuple)):
            tna = type(newarr)
            arr = list(newarr)
            for i, val in enumerate(newarr):
                if isinstance(val, ndarray):
                    val = val.unwrap(to_jax=to_jax)
                arr[i] = val
            return tna(arr)

        if to_jax:
            return newarr
        else:
            # we went one level too far!
            # whatever, it's relatively cheap to construct a new ndarray
            return ndarray(newarr)

    def tree_flatten(self) -> Tuple[Tuple[jnp.ndarray, ...], None]:
        """
        Flattens an ndarray in the JAX Pytree structure

        :return:  tuple containing any arrays (or other children) this ndarray holds, and an empty metadata field
        :rtype: tuple

        """
        if self.extras:
            return ((self.arr, *self.extras), None)
        return ((self.arr,), None)

    @classmethod
    def tree_unflatten(cls, aux_data, children):
        """
        Constructs an ndarray from its flattened components

        :param cls: ndarray
        :type cls: type
        :param aux_data: ignore this parameter
        :type aux_data: None
        :param children: any children that belonged to this ndarray before it was flattened
        :type children: Union[jax.interpreters.xla.DeviceArray,Iterable[jax.interpreters.xla.DeviceArray]]
        :return: an ndarray holding the children
        :rtype: ndarray

        """
        return cls(*children)

    def flatten(self) -> jnp.ndarray:
        """Returns a flattened 1-d array (NOT an ndarray, but rather the array type it contains)"""
        try:
            return self.arr.flatten()
        except Exception:
            return self.arr

    @classmethod
    def _ad_init_object(cls, obj: Array):
        obj = jnp.array(obj) if not isinstance(obj, (int, float)) else obj
        return cls(obj)

    @property
    def size(self):
        """How many elements does the array contain?"""
        try:
            return self.arr.size
        except Exception:
            return 0

    @property
    def shape(self):
        """The shape of the array"""
        try:
            return self.arr.shape
        except Exception:
            return ()

    @property
    def T(self):
        """Returns the transpose of this ndarray"""
        return ndarray(self.arr.T)

    def __len__(self):
        return self.arr.__len__()

    def __eq__(self, other):
        return self.arr.__eq__(other)

    # annotated operators are implemented in the table
    # mapping their name to a tuple of the implementation and
    # the corresponding Block contained in annotate_operator()
    @annotate_operator
    def __add__(self, other):
        pass

    @annotate_operator
    def __neg__(self):
        pass

    @annotate_operator
    def __truediv__(self, other):
        pass

    @annotate_operator
    def __rtruediv__(self, other):
        pass

    @annotate_operator
    def __radd__(self, other):
        return self.__add__(other)

    @annotate_operator
    def __rmul__(self, other):
        pass

    def __iadd__(self, other):
        return NotImplemented

    def __imul__(self, other):
        return NotImplemented

    def __isub__(self, other):
        return NotImplemented

    @annotate_operator
    def __sub__(self, other):
        pass

    @annotate_operator
    def __rsub__(self, other):
        pass

    @annotate_operator
    def __mul__(self, other):
        pass

    @annotate_operator
    def __pow__(self, other):
        pass

    @annotate_operator
    def __rpow__(self, other):
        pass

    def __abs__(self):
        return ndarray(jnp.abs(self.arr))

    def _ad_create_checkpoint(self) -> jnp.ndarray:
        return self.arr

    def _ad_restore_at_checkpoint(self, checkpoint):
        return ndarray(checkpoint)

    def _ad_dim(self) -> int:
        return self.arr.size

    def _ad_dot(self, other) -> float:
        sflat = self.flat()
        oflat = flatten(other)
        if sflat.size == 1 or oflat.size == 1:
            return float(jnp.sum(sflat * oflat))
        return float(jnp.dot(sflat, oflat))

    def _ad_mul(self, other):
        return ndarray(self.arr * other)

    def _ad_add(self, other):
        return ndarray(self.arr + other)

    def _ad_copy(self):
        if isinstance(self.arr, tuple):
            try:
                return ndarray(tuple(map(lambda x: x.copy(), self.arr)))
            except Exception:
                return self.arr
        return (
            ndarray(self.arr.copy())
            if not isinstance(self.arr, (int, float))
            else ndarray(self.arr)
        )

    def _ad_convert_type(self, value, options={}):
        return array(value, **options)

    def copy(self, *args, **kwargs):
        return ndarray(self.arr.copy(*args, **kwargs))

    def copy_data(self):
        return ndarray(self.arr.copy())

    def flat(self) -> jnp.ndarray:
        return jnp.ravel(self.unwrap(to_jax=True))

    @staticmethod
    def _ad_assign_numpy(dst, src, offset):
        if isinstance(src, ndarray):
            src = src.unwrap(to_jax=True)
        if isinstance(src, (list, tuple)):
            src = list(src)
            while isinstance(src, list) and len(src) == 1:
                src = src[0]
            else:
                for i, s in enumerate(src):
                    if isinstance(s, ndarray):
                        src[i] = s.unwrap(to_jax=True)
                src_val = src[offset]
                if isinstance(src_val, (int, float)):
                    dst = src_val
                else:
                    dst = jnp.reshape(jnp.array(src_val), dst.shape)
                offset += 1
                return array(dst), offset

        if hasattr(src, "__len__") and len(src) == 1:
            src = src[0]
        if isinstance(src, (int, float)):
            return array(src), offset + 1
        dst = jnp.reshape(jnp.array(src[offset : offset + dst.size]), dst.shape)
        offset += dst.size
        return array(dst), offset

    @staticmethod
    def _ad_to_list(m) -> list:
        if isinstance(m, ndarray):
            return np.array(m.arr).flatten().tolist()
        try:
            return list(np.array(m).tolist())
        except TypeError:
            return [m]

    def __getitem__(self, item):
        annotate = annotate_tape()
        if annotate:
            block = JAXArraySliceBlock(self, item)
            tape = get_working_tape()
            tape.add_block(block)

        with stop_annotating():
            out = self.arr.__getitem__(item)

        if annotate:
            out = ndarray(out) if not isinstance(out, ndarray) else out
            block.add_output(out.create_block_variable())
        return out


def array(obj: Array, **kwargs) -> ndarray:
    """Converts the input to an :class:`ndarray`. This function is NOT
        overloaded (does not add any :class:`Block` to the :class:`Tape`).
        If you want to convert an :class:`AdjFloat` to an :class:`ndarray`
        or vice-versa, use the functions :func:`to_jax` or :func:`to_adjfloat`
        respectively.

    :param obj: the object to wrap; should be either a JAX ndarray or something
        that can be converted to one (such as a list or tuple of floats or ints,
        or a float or int, or a numpy ndarray)
    :type obj: Union[jax.interpreters.xla.DeviceArray,Iterable[Union[int,float,jax.interpreters.xla.DeviceArray]]]
    :returns: a class that wraps a JAX array (such that it can be added to the JAX Pytree
        and thus used as an argument to a differentiable function) to be passed to a
        function wrapped with `overload_jax()`, while also inheriting from
        pyadjoint.OverloadedType
        (since you can't inherit from a JAX array;
        see https://github.com/google/jax/issues/4269).
    :rtype: ndarray

    """
    return _backend_array(obj, **kwargs)


def _backend_array(obj, **kwargs):
    directly_convertible_types = (
        float,
        int,
        jax.interpreters.xla.DeviceArray,
        jnp.ndarray,
        np.ndarray,
        ndarray,
    )
    if isinstance(obj, ndarray):
        return obj
    elif isinstance(obj, directly_convertible_types):
        return ndarray(obj)

    dtype = kwargs.get("dtype", _default_dtype)

    dtype = kwargs.get("dtype", _default_dtype)
    if isinstance(obj, (list, tuple)):
        if len(obj) == 0:
            return ndarray(obj)
        while isinstance(obj, (list, tuple)) and not isinstance(
            obj[0], directly_convertible_types
        ):
            if len(obj) == 1:
                obj = obj[0]
            else:
                obj = list(obj)
                for i, val in enumerate(obj):
                    obj[i] = array(val)

        if isinstance(obj[0], ndarray):
            return ndarray(obj)

    elif isinstance(obj, AdjFloat):
        obj = float(obj)
    elif isinstance(obj, Control):
        obj = obj.data()

    # jax.numpy.array(numpy.array(x)) is typically faster than
    # jax.numpy.array(x), especially if x is a list or tuple, because
    # numpy.array() is written in C, whereas jax.numpy.array() is written in
    # Python. This is recommended by the JAX developers.
    try:
        return ndarray(jnp.array(np.array(obj), dtype=dtype), **kwargs)
    except Exception:
        return ndarray(obj)


def asarray(obj: Array, **kwargs) -> ndarray:
    return array(obj, **kwargs)


ConvertJAXToAdjFloat = make_convert_block(
    AdjFloat,
    _backend_array,
    "ConvertJAXToFloat",
)

ConvertAdjFloatToJAX = make_convert_block(
    _backend_array,
    AdjFloat,
    "ConvertAdjFloatToJAX",
)


to_adjfloat = overload_function(AdjFloat, ConvertJAXToAdjFloat)

to_jax = overload_function(_backend_array, ConvertAdjFloatToJAX)


def flatten(x):
    if isinstance(x, ndarray):
        return x.flat()
    elif isinstance(x, (np.ndarray, jax.interpreters.xla.DeviceArray)):
        return jnp.ravel(x)
    else:
        return x


class JAXArraySliceBlock(Block):
    def __init__(self, arr, item):
        super().__init__()
        self.add_dependency(arr)
        self.item = item

    def evaluate_adj_component(
        self, inputs, adj_inputs, block_variable, idx, prepared=None
    ):
        adj_output = jnp.zeros(inputs[0].shape)
        return index_update(adj_output, self.item, adj_inputs[0])

    def recompute_component(self, inputs, block_variable, idx, prepared):
        return inputs[0][self.item]

    def evaluate_tlm_component(
        self, inputs, tlm_inputs, block_variable, idx, prepared=None
    ):
        return tlm_inputs[0][self.item]


def convert_arg(
    x: Union[ndarray, list, tuple, int, float, jnp.ndarray]
) -> Union[list, tuple, int, float, jnp.ndarray]:
    if isinstance(x, (jnp.ndarray, jax.interpreters.xla.DeviceArray, int, float)):
        return x
    elif isinstance(x, ndarray):
        return x.unwrap(to_jax=True)

    elif isinstance(x, (list, tuple)):
        tx = type(x)
        return tx([convert_arg(v) for v in x])
    elif isinstance(x, Control):
        return convert_arg(x.data())
    try:
        return jnp.array(x)
    except Exception:
        return x


register_overloaded_type(ndarray, jnp.ndarray)
register_overloaded_type(ndarray, jax.interpreters.xla.DeviceArray)
try:
    register_overloaded_type(ndarray, jax.interpreters.xla._DeviceArray)
except:
    pass

try:
    import jaxlib

    register_overloaded_type(ndarray, jaxlib.xla_extension.Buffer)
except:
    pass
