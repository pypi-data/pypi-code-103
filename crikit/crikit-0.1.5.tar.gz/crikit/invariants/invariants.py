import jax
from jax import jit
from jax.tree_util import Partial as partial
import jax.numpy as jnp
import numpy as np
from typing import NamedTuple, List, Tuple, Optional, Union, Iterable
from crikit.logging import logger
from .utils import (
    symm,
    antisymm,
    commutator_action,
    anticommutator_action,
    scalar_triple_prod,
    powerset,
    eps_ij,
    eps_ijk,
    _eps_vec_action,
    axial_vector,
    _tprod,
    symm_q4,
    symm_q3,
    tA,
    tv,
    Tv,
    TinnerS,
    TcontrS,
    TW,
    tbrace,
    _3d_rotation_matrix,
    near,
    is_symm,
    is_antisymm,
)
from pyadjoint_utils.jax_adjoint import ndarray
import inspect
from operator import itemgetter
import itertools


class TensorType(NamedTuple):
    order: int = 0
    shape: tuple = ()
    symmetric: bool = False
    antisymmetric: bool = False
    name: str = ""

    @staticmethod
    def make_scalar(name: str = ""):
        """Returns a TensorType representing a scalar

        :param name: The name of the scalar, defaults to ''
        :type name: str, optional
        :return: A TensorType representing a scalar
        :rtype: TensorType
        """
        return TensorType(0, (), False, False, name)

    @staticmethod
    def make_vector(spatial_dims: int, name: str = ""):
        """Returns a TensorType representing a vector

        :param spatial_dims: The number of spatial dimensions
        :type spatial_dims: int
        :param name: The name of the vector, defaults to ''
        :type name: str, optional
        :return: A TensorType representing a vector
        :rtype: TensorType
        """
        return TensorType(1, (spatial_dims,), False, False, name)

    @staticmethod
    def make_symmetric(order: int, spatial_dims: int, name: str = ""):
        """Returns a TensorType representing a symmetric tensor

        :param order: The order of the tensor
        :type order: int
        :param spatial_dims: How many spatial dimensions?
        :type spatial_dims: int
        :param name: The name of the tensor, defaults to ''
        :type name: str, optional
        :return: A TensorType representing a symmetric order-``order`` tensor in
             `spatial_dims` spatial dimensions.
        :rtype: TensorType
        """
        return TensorType(order, order * (spatial_dims,), True, False, name)

    @staticmethod
    def make_antisymmetric(order: int, spatial_dims: int, name: str = ""):
        """Returns a :class:`TensorType` representing an antisymmetric tensor

        :param order: The order of the tensor
        :type order: int
        :param spatial_dims: How many spatial dimensions?
        :type spatial_dims: int
        :param name: The name of the tensor, defaults to ''
        :type name: str, optional
        :return: A TensorType representing an antisymmetric order-``order`` tensor in
             `spatial_dims` spatial dimensions.
        :rtype: TensorType
        """
        return TensorType(order, order * (spatial_dims,), False, True, name)

    @staticmethod
    def from_array(X, symmetric=False, antisymmetric=False, name: str = ""):
        """Creates a :class:`TensorType` representing a particular array

        :param X: The array
        :type x: Union[jnp.ndarray,np.ndarray,pyadjoint_utils.jax_adjoint.ndarray]
        :param symmetric: Is the array symmetric? defaults to False
        :type symmetric: bool, optional
        :param antisymmetric: Is the array antisymmetric? defaults to False
        :type antisymmetric: bool, optional
        :param name: The name of the tensor, defaults to ''
        :type name: str, optional
        :returns: A :class:`TensorType` representing ``X``
        :rtype: TensorType

        """
        shp = X.shape
        if symmetric and antisymmetric:
            raise RuntimeError(
                "Cannot create a TensorType from an array that is both symmetric and antisymmetric! (That's a contradiction; pass True to only ONE of symmetric or antisymmetric in TensorType.from_array)"
            )
        return TensorType(len(shp), shp, symmetric, antisymmetric, name)

    def get_symmetrizer(self):
        """Returns a function that takes in a tensor of order ``self.order`` and
        makes it symmetric.

        :return: The symmetrizer for a tensor of order ``self.order``
        :rtype: function

        """
        if self.order <= 1:
            return lambda x: x
        elif self.order == 2:
            return symm
        elif order == 3:
            return symm_q3
        elif order == 4:
            return symm_q4

    def zeros_like(self) -> jnp.ndarray:
        """Returns an array of zeros of the shape ``self.shape``.

        :returns: jnp.zeros(self.shape)
        :rtype: jnp.ndarray

        """
        return jnp.zeros(shape=self.shape)

    def tensor_space_dimension(self) -> int:
        """Returns the dimension (as a vector space) of the tensor space containing
        tensors of this shape.

        :returns: dimension of the tensor space containing this TensorType
        :rtype: int

        """
        N = max(self.shape)
        q = self.order

        if self.symmetric:
            if q == 2:
                return (N * (N + 1)) // 2
            raise NotImplementedError
        if self.antisymmetric:
            if q == 2:
                return (N * (N - 1)) // 2
            raise NotImplementedError

        return np.prod(self.shape)

    def __hash__(self):
        return hash(tuple((self.order, self.shape, self.symmetric, self.antisymmetric)))

    def __ge__(self, other):
        if isinstance(other, TensorType):
            return self._selfge(other)
        elif isinstance(other, tuple):
            return True
        elif isinstance(other, int):
            return True
        else:
            return False

    def __lt__(self, other):
        return not self.__ge__(other)

    def _selfge(self, other):
        if self.order > other.order:
            return True
        elif self.order == other.order:
            if self.symmetric:
                if other.antisymmetric:
                    return True
                elif other.symmetric:
                    return True
                else:
                    return False

            elif self.antisymmetric:
                if other.symmetric:
                    return False
                elif other.antisymmetric:
                    return True
                else:
                    return False
            else:
                return False
        else:
            return False

    def get_array_like(self) -> jnp.ndarray:
        """
        Constructs an example array with the right shape and symmetry

        :return: a tensor with the right shape and symmetry
        :rtype: jnp.ndarray

        """
        if self.symmetric and self.order == 2:
            return jnp.eye(max(self.shape))
        elif self.order == 1:
            return jnp.zeros(self.shape)

        arr = jnp.zeros(self.shape, dtype=jnp.float32)
        upper_right_corner = tuple(max(0, s - 1) for s in self.shape)
        arr = jax.ops.index_update(arr, upper_right_corner, 1.0)
        if self.symmetric:
            return symm(arr)
        elif self.antisymmetric:
            return antisymm(arr)
        else:
            return arr


class LeviCivitaType(TensorType):
    """A class that represents the Levi-Civita tensor"""

    def __new__(cls, order):
        if order == 2:
            order = 2
            shape = eps_ij.shape
            symmetric = False
            antisymmetric = True
            return super(LeviCivitaType, cls).__new__(
                cls, order, shape, symmetric, antisymmetric
            )
        elif order == 3:
            order = 3
            shape = eps_ijk.shape
            symmetric = False
            antisymmetric = True
            return super(LeviCivitaType, cls).__new__(
                cls, order, shape, symmetric, antisymmetric
            )
        else:
            raise NotImplementedError


def type_from_array(X, rtol: float = 1.0e-5, name: str = "") -> TensorType:
    """
    Like :meth:`TensorType.from_array`, but tries to detect if the matrix is symmetric
    or asymmetric.

    :param X: An array (JAX or numpy)
    :type X: Union[jnp.ndarray]
    :param rtol: The relative tolerance to use when determining if X is symmetric,
        antisymmetric, or both, defaults to 1.0e-5
    :type rtol: float
    :param name: The name of the tensor, defaults to ''
    :type name: str, optional
    :return: An appropriate TensorType instance
    :rtype: TensorType
    """
    if isinstance(X, ndarray):
        X = X.unwrap(to_jax=True)
    if jnp.isscalar(X) or X.size == 1:
        return TensorType.make_scalar(name)
    shp = X.shape
    order = len(shp)
    if order == 1:
        return TensorType(order, shp, False, False, name)
    elif order == 2:
        if shp == eps_ij.shape:
            if near(X, eps_ij, rtol):
                return LeviCivitaType(order)

        return TensorType(order, shp, is_symm(X, rtol), is_antisymm(X, rtol), name)
    elif order == 3:
        # NOTE: do we ever care whether or not a 3rd order tensor is totally antisymmetric? I don't think so, other than for comparison with the Levi-Civita tensor
        if shp == eps_ijk.shape:
            if near(X, eps_ijk, rtol):
                return LeviCivitaType(order)

        return TensorType(order, shp, near(X, symm_q3(X), rtol), False, name)
    else:
        raise NotImplementedError


def evaluate_invariant_function(
    phi_i, scalar_invariant_func, form_invariant_func, *input_tensors
):
    scalar_invariants = scalar_invariant_func(*input_tensors)
    if len(phi_i) != scalar_invariants.size:
        raise ValueError(
            f"Must pass {scalar_invariants.size} scalar functions, not {len(phi_i)}"
        )
    form_invariants = form_invariant_func(*input_tensors)
    return _evaluate_invariant(form_invariant, scalar_invariants, phi_i)


@partial(jit, static_argnums=(2,))
def _evaluate_invariant(form_invariants, scalar_invariants, phi_i):
    output_vec = jnp.array([phi(scalar_invariants) for phi in phi_i])
    return output_vec.T @ form_invariants


class InvariantInfo(NamedTuple):
    """A class that contains relevant information for computing invariants.
    For example, for a hemitropic CR in 3 spatial dimensions taking a symmetric
    and an antisymmetric tensor as inputs and outputs a symmetric second order
    tensor:
    ::

        info = InvariantInfo(3,
                             (TensorType.make_symmetric(2,3),
                              TensorType.make_antisymmetric(2,3),
                              LeviCivitaType(3)
                             ),
                             TensorType.make_symmetric(2,3)
                            )

    """

    spatial_dims: int
    input_types: Tuple[TensorType, ...]
    output_type: TensorType

    def get_group_symbol(self, sanitize_input_types: bool = False):
        """
        Returns a symbol representing the group this instance represents.

        :param sanitize_input_types: if True, this function will also return
                the input types without the Levi-Civita symbol, if it exists, default False
        :type sanitize_input_types: bool, optional

        :return: a string whose value is either :math:`O(2)`,:math:`SO(2)`,:math:`O(3)`, or :math:`SO(3)`
        :rtype: str
        """
        if self.spatial_dims <= 1:
            raise ValueError(
                f"Cannot get an orthogonal group symbol for {self.spatial_dims} spatial dimensions!"
            )
        contains_eps = False
        eps_id = None
        for i, tp in enumerate(self.input_types):
            if isinstance(tp, LeviCivitaType):
                contains_eps = True
                eps_id = i
                break

        grp = None
        if self.spatial_dims == 2:
            grp = "SO(2)" if contains_eps else "O(2)"
        elif self.spatial_dims == 3:
            grp = "SO(3)" if contains_eps else "O(3)"
        # NOTE: will not detect multiple instances of a LeviCivitaType. TODO: implement that.

        if sanitize_input_types:
            input_types = self.input_types
            if contains_eps:
                try:
                    if eps_id == len(self.input_types) - 1:
                        input_types = tuple(self.input_types[:-1])
                    elif eps_id == 0:
                        input_types = tuple(self.input_types[1:])
                    else:
                        input_types = tuple(
                            self.input_types[:i] + self.input_types[i + 1 :]
                        )
                except IndexError:
                    pass

            return grp, tuple(input_types)
        else:
            return grp

    @staticmethod
    def from_arrays(output_example, *args, **kwargs):
        """Constructs an :class:`InvariantInfo` from arrays representing the output and inputs

        :param output_example: an array of the correct shape and symmetry/antisymmetry of the desired output
        :type output_example: Union[jnp.ndarray]
        :param args: an example of each of the input tensors
        :type args: Iterable[Union[jnp.ndarray]]
        :param rtol: the relative tolerance for detecting symmetry/antisymmetry and the Levi-Civita symbol, defaults to 1.0e-5
        :type rtol: float
        :return: an InvariantInfo with the correct spatial dims (inferred from the first argument)
           and correct input_types for your inputs and output
        :rtype: InvariantInfo
        """
        rtol = kwargs.get("rtol", 1.0e-5)
        types = [type_from_array(x, rtol=rtol) for x in args]
        spatial_dims = max(types[0].shape)
        for t in types:
            if len(t.shape) > 0 and max(t.shape) != spatial_dims:
                raise ValueError(
                    f"Input type {t} has {max(t.shape)} spatial dimensions, but the first input type has {spatial_dims} spatial dimensions"
                )

        output_type = type_from_array(output_example, rtol=rtol)
        return InvariantInfo(spatial_dims, types, output_type)


# needed for static_argnums parameter of jax.jit
class HashableDict(dict):
    def _key(self):
        return tuple(sorted(self.items()))

    def __hash__(self):
        return hash(self._key())

    def __setitem__(self, key, value):
        raise TypeError(f"{type(self)} does not support assignment!")


def get_invariant_functions(
    info: InvariantInfo,
    suppress_warning_print: Optional[bool] = False,
    fail_on_warning: Optional[bool] = False,
):
    """
    This function builds two functions, one to compute the scalar invariants,
    and one to compute the form invariants.

    :param info: an InvariantInfo instance
    :type info: InvariantInfo
    :param suppress_warning_print: if True, don't print out warnings
       (this typically would be used if you get a warning about scalar or
       form-invariants not being available for a specific subset of the input types,
       and you know that this isn't a problem, e.g. because no such invariants
       exist for that subset), defaults to False
    :type suppress_warning_print: bool, optional
    :param fail_on_warning: if True, warnings become exceptions. Useful if you
        know that you should not get a warning for your inputs, and want to make
        sure that nothing changes in a way that breaks that assumption., defaults
        to False
    :type fail_on_warning: bool, optional
    :return: a tuple of two functions,  the first of which generates the
        input scalar invariants (and places them into a jax.numpy.ndarray),
        and the second of which generates the output form-invariant basis.
    :rtype: tuple

    """
    if not (isinstance(info, InvariantInfo)):
        raise TypeError(
            f"First parameter of get_scalar_invariant_function ({info}) is of type {type(info)}, not InvariantInfo!"
        )

    dims = info.spatial_dims
    group, input_types = info.get_group_symbol(sanitize_input_types=True)
    output_type = info.output_type
    include_identity = output_type.order == 2 and output_type.symmetric
    include_eps = dims == 2 and output_type.order == 2 and output_type.antisymmetric

    old_input_types = input_types
    # sort inputs
    input_sort_idxs, input_types = _get_sorted_and_indices(input_types, reverse=True)
    input_types = _tag_value_chains(tuple(input_types))
    input_sort_map = {itype: i for (itype, i) in zip(input_types, input_sort_idxs)}
    scalar_invts = []
    form_invts = []
    output_type = _nameless(output_type)
    for sub_types in powerset(input_types, exclude_empty_set=True):
        try:
            new_sub_types = tuple(sorted(_untagged_tuple(sub_types), reverse=True))
            si_func, fi_func = _get_invariant_functions(
                dims, group, _untagged_tuple(new_sub_types, nameless=True), output_type
            )
            scalar_invts.append((si_func, sub_types))
            if fi_func:
                form_invts.append((fi_func, sub_types))
            else:
                if not suppress_warning_print:
                    logger.warning(
                        f"""we don't have functions to compute form-invariants for all subsets of your input basis!
Specifically, we do not have invariants for the input TensorType subset      
{_untagged_tuple(sub_types)}. 
Proceed with caution, as your basis may be incomplete! This may not be a problem--invariants don't
always exist for any arbitrary subset of every set of input types--but if you expect invariants to
exist for this input subset (and you have checked that that assumption is justified), we may be missing those functions.
                   """
                    )
        except ValueError as v:
            if not suppress_warning_print:
                logger.warning(
                    f"""we don't have functions to compute scalar invariants for all subsets of your input basis!
Specifically, we do not have invariants for the input TensorType subset      
{_untagged_tuple(sub_types)}. 
Proceed with caution, as your basis may be incomplete! This may not be a problem--invariants don't
always exist for any arbitrary subset of every set of input types--but if you expect invariants to
exist for this input subset (and you have checked that that assumption is justified), we may be missing those functions.
                   """
                )

            if fail_on_warning:
                raise v

    # doing this because JAX doesn't support normal kwarg usage;
    # if https://github.com/google/jax/pull/3532 is merged, we can
    # just use one function that takes imap and sinvts as kwargs
    @partial(
        jit,
        static_argnums=(
            0,
            1,
        ),
    )
    def unified_scalar_invariant_func(imap, sinvts, *args):
        invts = []
        N = len(sinvts)
        for i in range(N):
            si_func, sub_types = sinvts[i]
            idx = [imap[sub_t] for sub_t in sub_types]
            inputs = [args[i] for i in idx]
            invts.append(_1darr(si_func(*inputs)))

        return jnp.concatenate(invts)

    scalar_invts = tuple(scalar_invts)
    input_sort_map = HashableDict(input_sort_map)

    def scalar_invariant_func(*args):
        imap = input_sort_map
        sinvts = scalar_invts
        if len(args) != len(input_types):
            raise ValueError(
                f"Wrong number of arguments passed to scalar_invariant_func! Expected {len(input_types)}, but got {len(args)}!"
            )
        return unified_scalar_invariant_func(imap, sinvts, *args)

    @partial(
        jit,
        static_argnums=(
            0,
            1,
        ),
    )
    def unified_form_invariant_func(imap, frminvts, *args):
        finvts = []
        N = len(frminvts)
        for i in range(N):
            fi_func, sub_types = frminvts[i]
            idx = [imap[sub_t] for sub_t in sub_types]
            inputs = [args[i] for i in idx]
            finvts += fi_func(*inputs)
            """
            NOTE: the above (making a list of indices then a list of inputs) works with jax.jit, but directly doing
            
            fi_func(args[imap[sub_t]] for sub_t in sub_types))

            doesn't work (JAX complains and throws an exception)

            ALSO NOTE: putting the jnp.stack in Python mode for now to deal with possibly appending the identity
            """
        return finvts

    form_invts = tuple(form_invts)

    def form_invariant_func(*args):
        imap = input_sort_map
        frminvts = form_invts
        has_identity = include_identity
        has_eps = include_eps
        if len(args) != len(input_types):
            raise ValueError(
                f"Wrong number of arguments passed to form_invariant_func! Expected {len(input_types)}, but got {len(args)}!"
            )

        extra_form_invts = []
        if has_identity:
            extra_form_invts.append(jnp.eye(dims))
        # elif has_eps:
        #    extra_form_invts.append(eps_ij)

        if extra_form_invts:
            return jnp.stack(
                extra_form_invts + unified_form_invariant_func(imap, frminvts, *args)
            )

        return jnp.stack(unified_form_invariant_func(imap, frminvts, *args))

    return scalar_invariant_func, form_invariant_func


def get_invariant_descriptions(
    info: InvariantInfo,
    suppress_warning_print: Optional[bool] = False,
    fail_on_warning: Optional[bool] = False,
    html: Optional[bool] = None,
    ipython: Optional[bool] = None,
):
    """
    This function builds a string description of the scalar and form invariants that you would get from
    :func:`get_invariant_functions` with the same arguments you pass in here.

    :param info: an InvariantInfo instance
    :type info: InvariantInfo
    :param suppress_warning_print: if True, don't print out warnings
       (this typically would be used if you get a warning about scalar or
       form-invariants not being available for a specific subset of the input types,
       and you know that this isn't a problem, e.g. because no such invariants
       exist for that subset), defaults to False
    :type suppress_warning_print: bool, optional
    :param fail_on_warning: if True, warnings become exceptions. Useful if you
        know that you should not get a warning for your inputs, and want to make
        sure that nothing changes in a way that breaks that assumption., defaults
        to False
    :type fail_on_warning: bool, optional
    :param html: Return HTML instead of a plain string description? Useful for use inside Jupyter notebooks.
        Defaults to False
    :type html: bool, optional
    :param ipython: Is this being used in ipython mode? (e.g. in a Jupyter notebook) By default,
        tries to guess whether or not you are. If the default behavior is undesirable, set this parameter manually.
    :type ipython: bool, optional
    :return: a string describing the invariants
    :rtype: str

    """
    if not (isinstance(info, InvariantInfo)):
        raise TypeError(
            f"First parameter of get_scalar_invariant_function ({info}) is of type {type(info)}, not InvariantInfo!"
        )

    class function_state:
        n_rank_0 = 0
        n_rank_1 = 0
        n_rank_2_s = 0
        n_rank_2_a = 0
        n_rank_3 = 0
        n_rank_0_n = (
            0  # _n params count the number of this type that has a name already
        )
        n_rank_1_n = 0
        n_rank_2_s_n = 0
        n_rank_2_a_n = 0
        n_rank_3_n = 0

    if _executing_in_ipython():
        ipython = True if ipython is None else ipython
        # if we're in IPython mode, we definitely need HTML unless the parameter says otherwise
        html = ipython if html is None else html

    dims = info.spatial_dims
    group, input_types = info.get_group_symbol(sanitize_input_types=True)
    output_type = info.output_type
    include_identity = output_type.order == 2 and output_type.symmetric
    include_eps = dims == 2 and output_type.order == 2 and output_type.antisymmetric
    input_state = function_state()
    HEADER = (
        _get_header_html(dims, input_types, input_state)
        if html
        else _get_header_plaintext(dims, input_types, input_state)
    )

    # sort inputs
    input_sort_idxs, input_types = _get_sorted_and_indices(input_types, reverse=True)
    input_types = _tag_value_chains(tuple(input_types))
    input_sort_map = {itype: i for (itype, i) in zip(input_types, input_sort_idxs)}
    scalar_invts = []
    form_invts = []
    output_type = _nameless(output_type)
    for sub_types in powerset(input_types, exclude_empty_set=True):
        try:
            new_sub_types = tuple(sorted(sub_types, reverse=True))
            si_func, fi_func = _get_invariant_functions(
                dims, group, _untagged_tuple(new_sub_types, nameless=True), output_type
            )
            sub_types = tuple(sorted(sub_types, reverse=True))
            scalar_invts.append((si_func, sub_types))
            if fi_func:
                form_invts.append((fi_func, sub_types))
            else:
                if not suppress_warning_print:
                    logger.warning(
                        f"""we don't have functions to compute form-invariants for all subsets of your input basis!
Specifically, we do not have invariants for the input TensorType subset      
{_untagged_tuple(sub_types)}. 
Proceed with caution, as your basis may be incomplete! This may not be a problem--invariants don't
always exist for any arbitrary subset of every set of input types--but if you expect invariants to
exist for this input subset (and you have checked that that assumption is justified), we may be missing those functions.
                   """
                    )
        except ValueError as v:
            if not suppress_warning_print:
                logger.warning(
                    f"""we don't have functions to compute scalar invariants for all subsets of your input basis!
Specifically, we do not have invariants for the input TensorType subset      
{_untagged_tuple(sub_types)}. 
Proceed with caution, as your basis may be incomplete! This may not be a problem--invariants don't
always exist for any arbitrary subset of every set of input types--but if you expect invariants to
exist for this input subset (and you have checked that that assumption is justified), we may be missing those functions.
                   """
                )

            if fail_on_warning:
                raise v

    scalar_symbols = ["x", "y", "z"][input_state.n_rank_0_n :]
    vector_symbols = ["v", "u"][input_state.n_rank_1_n :]
    symm_symbols = ["A", "B", "C"][input_state.n_rank_2_s_n :]
    antisymm_symbols = ["W", "V"][input_state.n_rank_2_a_n :]
    r3_symbols = ["T", "S"][input_state.n_rank_3_n :]
    # if you change this, also change _get_symbol_id() below
    symbol_map = [
        scalar_symbols,
        vector_symbols,
        symm_symbols,
        antisymm_symbols,
        r3_symbols,
    ]

    # build scalar invariant description
    scalar_invt_descrs = []
    N = len(scalar_invts)
    range_start = 0
    inputs = []
    for i in range(N):
        si_func, sub_types = scalar_invts[i]
        stride = _get_num_retvals(si_func, sub_types)
        if stride == 1:
            prepend = f"{range_start} : "
        else:
            prepend = f"({range_start}:{range_start + stride - 1}) : "

        if html:
            prepend = "<code>" + prepend + "</code>"
        range_start += stride
        param_names = _infer_param_names(si_func, sub_types, symbol_map)

        scalar_invt_descrs.append(
            prepend + _format_invt_function(si_func, sub_types, symbol_map, html)
        )

    si_descr = _apply_final_formatting("\n\n".join(scalar_invt_descrs), html)

    form_invt_descrs = []
    range_start = 0
    if include_identity:
        form_invt_descrs.append(
            f"<code>0 : [] -> I_{dims}</code>" if html else f"0 : [] -> I_{dims}"
        )
        range_start = 1

    for i in range(len(form_invts)):
        fi_func, sub_types = form_invts[i]
        stride = _get_num_retvals_form_invt(fi_func, sub_types)
        if stride == 1:
            prepend = f"{range_start} : "
        else:
            prepend = f"({range_start}:{range_start + stride - 1}) : "

        if html:
            prepend = "<code>" + prepend + "</code>"
        range_start += stride
        form_invt_descrs.append(
            prepend + _format_invt_function(fi_func, sub_types, symbol_map, html)
        )

    fi_line = (
        '<br><br><hr style="border: 1px dashed black"><br>'
        if html
        else "\n\n------------------------------------------------\n"
    )
    fi_line += "Form Invariants:\n\n"
    fi_descr = _apply_final_formatting(fi_line + "\n\n".join(form_invt_descrs), html)
    if html:
        string = HEADER + si_descr + fi_descr + "</html>"
        if ipython:
            from IPython.core.display import HTML, display

            if html:
                string = HTML(string)
            return display(string)
    return HEADER + si_descr + fi_descr


def _executing_in_ipython():
    try:
        sh = get_ipython().__class__.__name__
        return True
    except NameError:
        # get_ipython() doesn't exist, so we proabably aren't in an IPython environment
        return False


def _apply_final_formatting(string, html):
    if html:
        return string.replace("\n", "<br>")
    return string


def _get_header_html(dims, input_types, input_state):
    style = """
<html>
<head>
<style>
table, th, td {
    border: 1px solid black;
}

ul {
    margin: 0;
}
ul.dashed {
    list-style-type: none;
}
ul.dashed > li {
    text-indent: -5px;
}
ul.dashed > li:before {
    content: "-";
    text-indent: -5px;
}
</style>
</head>
<body>
<p>Legend</p>
    """
    string = f"""
<table style="width:100%">
    <tr>
      <th>Symbol(s)</th>
      <th>Tensor Rank</th>
      <th>Symmetric</th>
      <th>Antisymmetric</th>
    </tr>
    <tr>
      <td>x, y, z</td>
      <td>0</td>
      <td>N/A</td>
      <td>N/A</td>
    </tr>
    <tr>
      <td>v, u</td>
      <td>1</td>
      <td>N/A</td>
      <td>N/A</td>
    </tr>
    <tr>
      <td>A, B, C</td>
      <td>2</td>
      <td>Yes</td>
      <td>No</td>
    </tr>
    <tr>
      <td>W, V</td>
      <td>2</td>
      <td>No</td>
      <td>Yes</td>
    </tr>
    <tr>
      <td>T, S</td>
      <td>3</td>
      <td>Any</td>
      <td>Any</td>
    </tr>
</table>
<br><br>
Special symbols:<br>
    <ul class="dashed">
        <li> <code>I_{dims}</code> (rank-two identify tensor, A.K.A. identity matrix)</li>
    </ul>
<br>

Operations:<br>
    <ul class="dashed">
        <li> <code>_tprod(x, y) = jnp.tensordot(x, y, axes=0) (tensor product)</code></li> <br>
        <li> <code>symm(x) = x + x.T</code></li><br>
        <li> <code>antisymm(x) = x - x.T</code></li>
    </ul>

<br>
<hr style="border: 1px dashed black">

<br>
Input tensors: <br>
<code>{_get_type_symbols(input_types, input_state)}</code>
<br>
<hr style="border: 1px dashed black">
<br>
Scalar invariants:<br><br>
    """
    return style + string


def _get_header_plaintext(dims, input_types, input_state):
    return f"""
Legend:
------------------------------------------------
Symbol(s) | Tensor Rank | Symmetric | Antisymmetric
------------------------------------------------
x, y, z   |      0      |    N/A    |    N/A
------------------------------------------------
v, u      |      1      |    N/A    |    N/A
------------------------------------------------
A, B, C   |      2      |    Yes    |    No
------------------------------------------------
W, V      |      2      |    No     |    Yes
------------------------------------------------
T, S      |      3      |    Any    |    Any
------------------------------------------------


Special symbols:
    - I_{dims} (rank-two identify tensor, A.K.A. identity matrix)


Operations: 
    - _tprod(x, y) = jnp.tensordot(x, y, axes=0) (tensor product)
    
    - symm(x) = x + x.T

    - antisymm(x) = x - x.T

------------------------------------------------

Input tensors: 

{_get_type_symbols(input_types, input_state)}

------------------------------------------------
Scalar invariants:

"""


def _get_symbol_replacements(
    names: Union[List[str], Tuple[str]],
    types: Iterable[Union[TensorType, Tuple[TensorType, int]]],
    symbol_map: List[List[str]],
) -> List[Tuple[str, str]]:
    # names are returned by _infer_param_names() and are the same length as types
    replacements = set()
    for i, ttype in enumerate(types):
        if not isinstance(ttype, TensorType):
            ttype, j = ttype
            tid = _get_symbol_id(ttype)
            map_to = symbol_map[tid][j]
        else:
            tid = _get_symbol_id(ttype)
            map_to = names[i]

        candidate = symbol_map[tid][0]
        if candidate != map_to:
            replacements.add((candidate, map_to))

    return replacements


def _replace_symbols(
    names: Union[List[str], Tuple[str]],
    types: Iterable[Union[TensorType, Tuple[TensorType, int]]],
    symbol_map: List[List[str]],
    line: str,
) -> str:
    replacements = _get_symbol_replacements(names, types, symbol_map)
    for replacement in replacements:
        line = line.replace(*replacement).replace(
            replacement[0].lower(), replacement[1].lower()
        )
    return line


def _format_invt_function(f, types, symbol_map, html):
    param_names = _infer_param_names(f, types, symbol_map)
    lines = _strip_function_header(inspect.getsourcelines(f)[0])
    if len(lines) == 0:
        return (
            f"<code>{param_names} -> {param_names}</code>"
            if html
            else f"{param_names} -> {param_names}"
        )
    elif len(lines) == 1:
        body = []
        retline = lines[0]
    else:
        retline = -1
        for i, line in enumerate(lines):
            if "return" in line:
                retline = i
                break
        retline, body = lines[retline:], lines[:retline]
        retline = "\n".join(retline)
        body = _format_body(body)
    # retline = _replace_symbols(param_names, types, symbol_map,
    #                           _format_return_line(retline.lstrip(' ')))

    body = ",\n".join(body).rstrip(",\n")

    func_descr = f"{param_names} -> "
    replacement_str = "["
    for r in inspect.signature(f).parameters:
        replacement_str += "'" + r + "', "

    replacement_str = replacement_str.rstrip(", ") + "]"
    func_descr += replacement_str + " -> "

    func_descr += _format_return_line(retline.lstrip(" "))

    if len(lines) > 1:
        func_descr += "where\n" + body

    if html:
        return "<code>" + func_descr + "</code>"
    return func_descr


def _format_body(body):
    return [x.lstrip(" ").rstrip("\n") for x in body]


def _get_num_retvals(f, input_types):
    inputs = [_untagged_value(t).get_array_like() for t in input_types]
    return f(*inputs).size


def _get_num_retvals_form_invt(f, input_types):
    inputs = [_untagged_value(t).get_array_like() for t in input_types]
    return len(f(*inputs))


def _format_return_line(line):
    if "array(" in line:
        idx = line.find("array(") + len("array(")
        line = line.rstrip("\n").rstrip(")")[idx:] + "\n"
    elif line.startswith("return "):
        return line[len("return ") :]
    return line


def _strip_function_header(f_lines):
    return f_lines[2:]


def _get_symbol_id(ttype):
    if ttype.order < 2:
        return ttype.order

    if ttype.order == 2:
        return 2 if ttype.symmetric else 3

    return 4


def _infer_param_names(f, input_types, symbol_map):
    names = []
    for ttype in input_types:
        if isinstance(ttype, TensorType):
            # if it's a pure TensorType, it must be the first of its type, so get the first symbol
            name = (
                symbol_map[_get_symbol_id(ttype)][0] if ttype.name == "" else ttype.name
            )
            names.append(name)
        else:
            ttype, i = ttype
            name = (
                symbol_map[_get_symbol_id(ttype)][i] if ttype.name == "" else ttype.name
            )
            names.append(name)
    return names


def _get_type_symbols(ts, state):
    def _handle_rank_0(t):
        state.n_rank_0 += 1
        if state.n_rank_0 == 1:
            if t.name == "":
                return "x"
            else:
                state.n_rank_0_n += 1
                return t.name
        elif state.n_rank_0 == 2:
            if t.name == "":
                return "y"
            else:
                state.n_rank_0_n += 1
                return t.name
        elif state.n_rank_0 == 3:
            if t.name == "":
                return "z"
            else:
                state.n_rank_0_n += 1
                return t.name
        else:
            raise ValueError(
                "Currently can only represent 3 scalars in the input types!"
            )

    def _handle_rank_1(t):
        # global n_rank_1
        if state.n_rank_1 == 0:
            state.n_rank_1 = 1
            if t.name == "":
                return "v"
            else:
                state.n_rank_1_n += 1
                return t.name
        elif state.n_rank_1 == 1:
            state.n_rank_1 = 2
            if t.name == "":
                return "u"
            else:
                state.n_rank_1_n += 1
                return t.name
        else:
            raise ValueError(
                "Currently can only represent 2 vectors in the input types!"
            )

    def _handle_rank_2(t):
        # global n_rank_2_s
        if t.symmetric:
            state.n_rank_2_s += 1
            if state.n_rank_2_s == 1:
                if t.name == "":
                    return "A"
                else:
                    state.n_rank_2_s_n += 1
                    return t.name
            elif state.n_rank_2_s == 2:
                if t.name == "":
                    return "B"
                else:
                    state.n_rank_2_s_n += 1
                    return t.name
            elif state.n_rank_2_s == 3:
                if t.name == "":
                    return "C"
                else:
                    state.n_rank_2_s_n += 1
                    return t.name
            else:
                raise ValueError(
                    "Currently can only represent 3 symmetric rank-two tensors in the input types!"
                )
        else:
            state.n_rank_2_a += 1
            if state.n_rank_2_a == 1:
                if t.name == "":
                    return "W"
                else:
                    state.n_rank_2_a_n += 1
                    return t.name
            elif state.n_rank_2_a == 2:
                if t.name == "":
                    return "V"
                else:
                    state.n_rank_2_a_n += 1
                    return t.name
            else:
                raise ValueError(
                    "Currently can only represent 2 antisymmetric rank-two tensors in the input types!"
                )

    def _handle_rank_3(t):
        state.n_rank_3 += 1
        if state.n_rank_3 == 1:
            if t.name == "":
                return "T"
            else:
                state.n_rank_3_n += 1
                return t.name
        elif state.n_rank_3 == 2:
            if t.name == "":
                return "S"
            else:
                state.n_rank_3_n += 1
                return t.name
        else:
            raise ValueError(
                "Currently can only represent 2 rank-three tensors in the input types!"
            )

    handler_map = {
        0: lambda x: _handle_rank_0(x),
        1: lambda x: _handle_rank_1(x),
        2: lambda x: _handle_rank_2(x),
        3: lambda x: _handle_rank_3(x),
    }

    dispatcher = lambda t: handler_map[t.order](t)

    return [dispatcher(_untagged_value(t)) for t in ts]


# tags chains of the same value T (e.g. T,T,T,T,... becomes T,(T,1),(T,2),...)
def _tag_value_chains(indexable):
    val = list(indexable)
    N = len(indexable)
    i = 1
    while i < N:
        if val[i - 1] == val[i]:
            # chain starts here
            T = val[i]
            n = 1
            while val[i] == T:
                val[i] = (T, n)
                n += 1
                i += 1
                if i >= N:
                    break
        else:
            i += 1

    return tuple(val)


def _get_sorted_and_indices(l, reverse=True):
    if len(l) == 0:
        return (), ()
    srtd = sorted(enumerate(l), key=itemgetter(1), reverse=reverse)
    return tuple(x[0] for x in srtd), tuple(x[1] for x in srtd)


def _nameless(x):
    return TensorType(x.order, x.shape, x.symmetric, x.antisymmetric)


def _untagged_value(val, nameless=False):
    if isinstance(val, TensorType):
        return _nameless(val) if nameless else val
    return _nameless(val[0]) if nameless else val[0]


def _untagged_tuple(tpl, nameless=False):
    return tuple(_untagged_value(x, nameless) for x in tpl)


def _1darr(x):
    return (
        x
        if x.ndim > 0
        else jnp.array(
            [
                x,
            ]
        )
    )


def _get_invariant_functions(dims, group, input_types, output_type):
    missing_dims_err_str = f"The number of dimensions you passed to get_scalar_invariant_function through the info parameter ({dims}) is not supported. Supported numbers of dimensions are currently: (2,3)"
    missing_group_err_str = f"The symmetry group you passed in (of type {type(group)}) is not among the currently supported set of symmetry groups (O(2),SO(2),O(3),SO(3))"
    missing_num_inputs_err_str = f"The number of inputs you passed ({len(input_types)}) is not among the currently-supported set of input sizes (1,2,3,4)."
    missing_inputs_err_str = f"The input types you passed ({input_types}) are not among the currently-supported set of input types in {dims} dimensions under the symmetry group {group}."
    missing_outputs_err_str = f"The output type you passed ({output_type}) along with the combination of input types you passed ({input_types}) does not have a form-invariant function implemented at the time, or it does not exist."
    try:
        group_table = _get_item(
            _scalar_invariant_function_table, dims, missing_dims_err_str
        )
        inputs_table = _get_item(group_table, group, missing_group_err_str)
        inputs_table = _get_item(
            inputs_table, len(input_types), missing_num_inputs_err_str
        )
        scalar_func, outputs_table = _get_item(
            inputs_table, input_types, missing_inputs_err_str
        )
    except ValueError as v:
        raise v

    try:
        # get form-invariants
        output_basis_func = _get_item(
            outputs_table, output_type, missing_outputs_err_str
        )
        return scalar_func, output_basis_func
    except ValueError as v:
        return scalar_func, None


def _get_item(table, key, err_msg):
    val = None
    try:
        val = table[key]
    except KeyError:
        raise ValueError(err_msg)
    return val


def register_invariant_functions(
    info: InvariantInfo,
    scalar_invariant_func,
    form_invariant_func,
    overwrite_existing=False,
    nojit=False,
):
    """Register a scalar and form-invariant computing function for a given
    InvariantInfo.

    :param info: an InvariantInfo containing the relevant information about the
        inputs and outputs of functions with this symmetry.
    :type info: InvariantInfo
    :param scalar_invariant_func: a function that returns a single jax.numpy.ndarray
        contaning the scalar invariants for the inputs.
    :type scalar_invariant_func: Callable
    :param form_invariant_func: a function that returns a Python list of jax.numpy.ndarray
        instances representing the form-invariants for the inputs
    :type form_invariant_func: Callable
    :param overwrite_existing: if True, and the InvariantInfo you pass describes an
       existing set of invariants, replace those with your function. You should
       NEVER set this to True unless you really know what you're doing. If you want to
       overwrite one function but not the other (e.g. insert a form-invariant for a scenario
       where the scalar invariant already exists), you can also pass a pair of bools, one for
       the scalar invariant function and one for the form invariant function. defaults to False
    :type overwrite_existing: Union[bool, Tuple[bool, bool]], optional
    :param nojit: if True, do NOT call jax.jit() on scalar_invariant_func() or form_invariant_func(), defaults to False
    :type nojit: bool, optional
    :return: None, makes your functions available to get_invariant_functions()

    """
    if not nojit:
        scalar_invariant_func = jax.jit(scalar_invariant_func)
        form_invariant_func = jax.jit(form_invariant_func)
    dims = info.spatial_dims
    group, input_types = info.get_group_symbol(sanitize_input_types=True)
    output_type = info.output_type
    input_types = tuple(sorted(input_types, reverse=True))
    global _scalar_invariant_function_table
    if dims in _scalar_invariant_function_table:
        group_table = _scalar_invariant_function_table[dims]
    else:
        group_table = {group: {}}
        _scalar_invariant_function_table[dims] = group_table

    if group in group_table:
        n_input_table = group_table[group]
    else:
        n_input_table = {N: {}}
        group_table[group] = n_input_table

    N = len(input_types)
    if N in n_input_table:
        inputs_table = n_input_table[N]
    else:
        inputs_table = {tuple(input_types): [scalar_invariant_func, {}]}
        n_input_table[N] = inputs_table

    if isinstance(overwrite_existing, (int, bool)):
        overwrite_existing_scalar = overwrite_existing_form = overwrite_existing
    else:
        # if it's not a single bool/int, it must be a pair of them (or else we need to
        # throw an exception anyway, might as well let it be the default one from unpacking
        # a non-iterable object
        overwrite_existing_scalar, overwrite_existing_form = overwrite_existing

    if input_types in inputs_table:
        if not overwrite_existing_scalar:
            logger.warning(
                f"Scalar invariants for the inputs combination {input_types} already exists! Skipping this replacement for now. To overwrite this function, pass overwrite_existing=True to register_invariant_functions(). ONLY do this if you know what you are doing!"
            )
        else:
            extant, outputs_table = inputs_table[input_types]
            inputs_table[input_types] = (scalar_invariant_func, outputs_table)

    else:
        outputs_table = {}
        inputs_table[input_types] = (scalar_invariant_func, outputs_table)

    if output_type in outputs_table:
        if not overwrite_existing_form:
            logger.warning(
                f"Form-invariant functions for this inputs and outputs combination (inputs {input_types}, output {output_type}) already exist! Skipping this replacement for now. To overwrite this function, pass overwrite_existing=True to register_invariant_functions(). ONLY do this if you know what you're doing!"
            )
        else:
            outputs_table[output_type] = form_invariant_func
    else:
        outputs_table[output_type] = form_invariant_func


"""
Because Python's parsing rules are kinda weird when dictionaries are involved, all of the invariant-
calculating functions have to be first. If you're reading this for the first time, skip down to the
tables below first.
"""


@jit
def _2d_hmt_1_r3_o_r3(T):
    return [T, T @ eps_ij]


@jit
def _2d_hmt_1sr2_o_s2(A):
    return [A, A @ eps_ij - eps_ij @ A]


@jit
def _2d_hmt_1_vec_o_vec(v):
    return [v, eps_ij @ v]


@jit
def _2d_hmt_1_vec_o_s2(v):
    ev = eps_ij @ v
    return [_tprod(v, v), _tprod(v, ev) + _tprod(ev, v)]


@jit
def _2d_hmt_1_vec_o_s3(v):
    return [_tprod(v, _tprod(v, v))]


@jit
def _2d_hmt_1_vec_o_r3(v):
    vv = _tprod(v, v)
    ev = eps_ij @ v
    return [
        _tprod(v, vv),
        _tprod(vv, ev),
        _tprod(v, jnp.eye(2)),
        _tprod(ev, jnp.eye(2)),
    ]


@jit
def _2d_iso_1_vec_o_vec(v):
    return [v]


@jit
def _2d_iso_1_vec_o_s2(v):
    return [_tprod(v, v)]


@jit
def _2d_iso_1_vec_o_r3(v):
    return [_tprod(v, _tprod(v, v))] + tbrace(_tprod(v, jnp.eye(2)))


@jit
def _2d_iso_1r3_o_3(T):
    return [T]


@jit
def _2d_iso_1sr2_o_s2(A):
    return [A]


@jit
def _2d_iso_1ar2_o_a2(W):
    return [W]


@jit
def _2d_iso_2sr2_o_a2(A, B):
    return [A @ B - B @ A]


@jit
def _2d_iso_1sr2_1ar2_o_s2(A, W):
    return [A @ W - W @ A]


@jit
def _2d_iso_1sr2_1_vec_o_vec(A, v):
    return [A @ v]


@jit
def _2d_iso_1sr2_1_vec_o_a2(A, v):
    av = A @ v
    return [_tprod(v, av) - A @ _tprod(v, v)]


@jit
def _2d_iso_1sr2_1_vec_o_s3(A, v):
    return tbrace(_tprod(A @ v, jnp.eye(2)))


@jit
def _2d_iso_1ar2_1_vec_o_s3(W, v):
    return [symm_q3(_tprod(v, _tprod(v, W @ v)))]


@jit
def _2d_iso_2_vec_o_s2(v, u):
    return [_tprod(v, u) + _tprod(u, v)]


@jit
def _2d_iso_2_vec_o_a2(v, u):
    return [_tprod(v, u) - _tprod(u, v)]


@jit
def _2d_iso_2_vec_o_s3(v, u):
    return [symm_q3(_tprod(v, _tprod(v, u)))]


@jit
def _2d_iso_1r3_1_vec_o_vec(T, v):
    return [tv(T, v)]


@jit
def _2d_iso_1r3_1_vec_o_s2(T, v):
    return [Tv(T, v)]


@jit
def _2d_iso_1r3_1_vec_o_a2(T, v):
    ttv = tv(T, v)
    return [_tprod(v, ttv) - _tprod(ttv, v)]


@jit
def _2d_iso_1r3_1sr2_o_vec(T, A):
    return tA(T, A)


@jit
def _2d_iso_1r3_1sr2_o_s2(T, A):
    tta = tA(T, A)
    return [_tprod(tta, tta)]


@jit
def _2d_iso_1r3_1sr2_o_a2(T, A):
    tta = tA(T, A)
    ata = A @ tta
    return [_tprod(tta, ata) - _tprod(ata, tta)]


@jit
def _2d_iso_1r3_1sr2_o_3(T, A):
    tta = tA(T, A)
    return [symm_q3(_tprod(A @ tta, A))] + tbrace(_tprod(tta, jnp.eye(2)))


@jit
def _2d_iso_2_r3_o_a2(T, S):
    return TinnerS(T, S)


@jit
def _3d_hmt_1sr2_o_s2(A):
    return [A, A @ A]


@jit
def _3d_hmt_1ar2_o_s2(W):
    return [W @ W]


@jit
def _3d_hmt_1ar2_o_a2(W):
    return [W]


@jit
def _3d_hmt_1ar2_o_vec(W):
    return [axial_vector(W)]


@jit
def _3d_hmt_1vec_o_s2(v):
    return [jnp.tensordot(v, v, axes=0)]


@jit
def _3d_hmt_1vec_o_a2(v):
    return [jnp.einsum("ijk,k -> ij", eps_ijk, v, optimize=True)]


@jit
def _3d_hmt_1vec_o_vec(v):
    return [v]


@jit
def _3d_hmt_2sr2_o_s2(A, B):
    AB = A @ B
    BA = B @ A
    return [AB + BA, A @ AB + BA @ A, AB @ B + B @ BA]


@jit
def _3d_hmt_2sr2_o_a2(A, B):
    AB = A @ B
    BA = B @ A
    BAA = BA @ A
    BBA = B @ BA
    return [
        AB - BA,
        A @ AB - BAA,
        AB @ B - BBA,
        A @ BAA - A @ A @ BA,
        B @ AB @ B - BBA @ B,
    ]


@jit
def _3d_hmt_2sr2_o_vec(A, B):
    AB = A @ B
    ABB = AB @ B
    return [
        axial_vector(AB),
        axial_vector(A @ AB),
        axial_vector(ABB),
        axial_vector(AB @ A @ A),
        axial_vector(B @ ABB),
    ]


@jit
def _3d_hmt_1s1ar2_o_s2(A, W):
    AW = A @ W
    WA = W @ A
    W2 = W @ W
    return [AW - WA, AW @ W + W @ WA, WA @ W2 - W2 @ AW, A @ AW - WA @ A]


@jit
def _3d_empty():
    return jnp.array([])


@jit
def _2d_empty():
    return jnp.array([])


@jit
def _2d_idf():
    return jnp.eye(2)


@jit
def _3d_idf():
    return jnp.eye(3)


@jit
def _3d_hmt_1s1ar2_o_a2(A, W):
    AW = A @ W
    WA = W @ A
    return [AW + WA, AW @ W - W @ WA]


@jit
def _3d_hmt_1s1ar2_o_vec(A, W):
    AB = A @ B
    return [
        axial_vector(AB),
        axial_vector(A @ AB),
        axial_vector(AB @ B),
        axial_vector(AB @ A @ A),
        axial_vector(B @ AB @ B),
    ]


@jit
def _3d_hmt_2ar2_o_s2(W, V):
    WV = W @ V
    VW = V @ W
    return [WV + VW, W @ WV - VW @ W, WV @ V - V @ VW]


@jit
def _3d_hmt_2ar2_o_a2(W, V):
    return [W @ V - V @ W]


@jit
def _3d_hmt_2ar2_o_vec(W, V):
    return [axial_vector(W @ V)]


@jit
def _3d_hmt_1ar21vec_o_s2(W, v):
    ev = jnp.einsum("ijk,k -> ij", eps_ijk, v)
    wev = W @ ev
    return [symm(_tprod(v, W @ v)), symm(wev), symm(W @ wev)]


@jit
def _3d_hmt_1ar21vec_o_a2(W, v):
    return [antisymm(W @ jnp.einsum("ijk,k -> ij", eps_ijk, v))]


@jit
def _3d_hmt_1ar21vec_o_vec(W, v):
    return [W @ v]


@jit
def _3d_hmt_1sr21vec_o_s2(A, v):
    return [
        symm(_tprod(v, A @ v)),
        symm(A @ jnp.einsum("ijk,k -> ij", eps_ijk, v)),
        symm(_tprod(v, jnp.cross(v, A @ v))),
    ]


@jit
def _3d_hmt_1sr21vec_o_a2(A, v):
    return [
        antisymm(A @ jnp.einsum("ijk,k -> ij", eps_ijk, v)),
        antisymm(_tprod(v, A @ v)),
    ]


@jit
def _3d_hmt_1sr21vec_o_vec(A, v):
    Av = A @ v
    return [Av, jnp.cross(v, Av)]


@jit
def _3d_iso_1sr21vec_o_s2(A, v):
    av = A @ v
    return [symm(_tprod(v, av)), symm(_tprod(v, A @ av))]


@jit
def _3d_iso_1sr21vec_o_a2(A, v):
    av = A @ v
    aav = A @ av
    return [
        antisymm(_tprod(v, av)),
        antisymm(_tprod(v, aav)),
        antisymm(_tprod(av, aav)),
    ]


@jit
def _3d_iso_1sr21vec_o_vec(A, v):
    av = A @ v
    return [av, A @ av]


@jit
def _3d_iso_2vec_o_s2(v, u):
    return [symm(_tprod(v, u))]


@jit
def _3d_iso_2vec_o_a2(v, u):
    return [antisymm(_tprod(v, u))]


@jit
def _3d_hmt_2vec_o_s2(v, u):
    return [symm(_tprod(v, u))]


@jit
def _3d_hmt_2vec_o_a2(v, u):
    return [antisymm(_tprod(v, u))]


@jit
def _3d_hmt_2vec_o_vec(v, u):
    return [jnp.cross(v, u)]


@jit
def _3d_hmt_3sr2_o_s2(A, B, C):
    AB = A @ B
    BC = B @ C
    AC = A @ C
    A2 = A @ A
    B2 = B @ B
    C2 = C @ C
    ABC = AB @ C
    return [ABC, A @ ABC, B2 @ AC, C2 @ AB, A2 @ B2 @ C, B2 @ C2 @ A, C2 @ A2 @ B]


@jit
def _3d_hmt_3sr2_o_a2(A, B, C):
    AB = A @ B
    BC = B @ C
    AC = A @ C
    CB = C @ B
    return [AB @ C - CB @ A + BC @ A - A @ CB + C @ AB - B @ AC]


@jit
def _3d_hmt_3sr2_o_vec(A, B, C):
    BC = B @ C
    return [axial_vector(A @ BC + BC @ A + C @ A @ B)]


@jit
def _tprod(x, y):
    return jnp.tensordot(x, y, axes=0)


@jit
def _3d_iso_2sr21vec_o_a2(A, B, v):
    return [antisymm(_tprod(A @ v, B @ v)) + antisymm(_tprod(v, antisymm(A @ B) @ v))]


@jit
def _3d_iso_2sr21vec_o_vec(A, B, v):
    av = A @ v
    bv = B @ v
    return [A @ bv - B @ av]


@jit
def _3d_iso_1s1ar21vec_o_a2(A, W, v):
    wv = W @ v
    av = A @ v
    return [A @ wv + W @ av]


@jit
def _3d_iso_2ar21vec_o_vec(W, V, v):
    vv = V @ v
    wv = W @ v
    return [W @ vv - V @ wv]


@jit
def _3d_iso_1ar22vec_o_s2(W, v, u):
    vtu = antisymm(_tprod(v, u))
    return [W @ vtu + vtu @ W]


@jit
def _3d_iso_1ar22vec_o_a2(W, v, u):
    vtu = antisymm(_tprod(v, u))
    return [W @ vtu - vtu @ W]


@jit
def _3d_iso_1sr22vec_o_s2(A, v, u):
    vtu = antisymm(_tprod(v, u))
    return [A @ vtu - vtu @ A]


@jit
def _3d_iso_1sr22vec_o_a2(A, v, u):
    vtu = antisymm(_tprod(v, u))
    return [A @ vtu + vtu @ A]


@jit
def _3d_isotropic_2s_2_vec(A, B, v, u):
    return jnp.inner(v, commutator_action(A, B, u))


@jit
def _3d_isotropic_1s_1a_2_vec(A, W, v, u):
    return jnp.inner(v, anticommutator_action(A, W, u))


@jit
def _3d_isotropic_2a_2_vec(W, V, v, u):
    return jnp.inner(v, commutator_action(W, V, u))


@jit
def _3d_hemitropic_1_vec(v):
    return jnp.inner(v, v)


@jit
def _3d_isotropic_1s_rank_2_1_vec(A, v):
    Av = A @ v
    return jnp.array([jnp.inner(v, Av), jnp.inner(v, A @ Av)])


@jit
def _3d_isotropic_1a_rank_2_1_vec(W, v):
    return jnp.inner(v, W @ (W @ v))


@jit
def _3d_isotropic_2_vec(v, u):
    return jnp.inner(v, u)


@jit
def _3d_isotropic_2s_rank_2_1_vec(A, B, v):
    bv = B @ v
    return jnp.inner(v, A @ bv)


@jit
def _3d_isotropic_1s_1a_rank_2_1_vec(A, W, v):
    Wv = W @ v
    AWv = A @ Wv
    return jnp.array(
        [jnp.inner(v, AWv), jnp.inner(v, A @ AWv), jnp.inner(v, W @ (A @ (W @ Wv)))]
    )


@jit
def _3d_isotropic_2a_rank_2_1_vec(W, V, v):
    Vv = V @ v
    return jnp.array(
        [jnp.inner(v, W @ Vv), jnp.inner(v, W @ (W @ Vv)), jnp.inner(v, W @ (V @ Vv))]
    )


@jit
def _3d_isotropic_1s_rank_2_2_vec(A, v, u):
    Au = A @ u
    return jnp.array([jnp.inner(v, Au), jnp.inner(v, A @ Au)])


@jit
def _3d_isotropic_1a_rank_2_2_vec(W, v, u):
    Wu = W @ u
    return jnp.array(jnp.inner(v, Wu), jnp.inner(v, W @ Wu))


@jit
def _3d_hemitropic_1s_rank_2(A):
    A2 = A @ A
    return jnp.array([jnp.trace(A), jnp.trace(A2), jnp.trace(A @ A2)])


@jit
def _3d_hemitropic_1a_rank_2(W):
    return jnp.trace(W @ W)


@jit
def _3d_hemitropic_1_vec(v):
    return jnp.inner(v, v)


@jit
def _3d_hemitropic_2s_rank_2(A, B):
    A2 = A @ A
    B2 = B @ B
    return jnp.array(
        [jnp.trace(A @ B), jnp.trace(A2 @ B), jnp.trace(A @ B2), jnp.trace(A2 @ B2)]
    )


@jit
def _3d_hemitropic_2a_rank_2(W, V):
    return jnp.trace(W @ V)


@jit
def _3d_hemitropic_1s_1a_rank_2(A, W):
    A2 = A @ A
    W2 = W @ W
    A2W2 = A2 @ W2
    return jnp.array([jnp.trace(A @ W2), jnp.trace(A2W2), jnp.trace(A2W2 @ A @ W)])


@jit
def _3d_hemitropic_1s_rank_2_1_vec(A, v):
    av = A @ v
    aav = A @ av
    return jnp.array(
        [jnp.inner(v, A @ v), jnp.inner(v, aav), scalar_triple_prod(v, av, aav)]
    )


@jit
def _3d_hemitropic_1a_rank_2_1_vec(W, v):
    return jnp.inner(v, axial_vector(W))


@jit
def _3d_hemitropic_2_vec(v, u):
    return jnp.inner(v, u)


@jit
def _3d_hemitropic_3s_rank_2(A, B, C):
    return jnp.trace(A @ B @ C)


@jit
def _3d_hemitropic_2s_1a_rank_2(A, B, W):
    AB = A @ B
    BW = B @ W
    return jnp.array(
        [
            jnp.trace(AB @ W),
            jnp.trace(A @ AB @ W),
            jnp.trace(AB @ BW),
            jnp.trace(A @ W @ W @ BW),
        ]
    )


@jit
def _3d_hemitropic_1s_2a_rank_2(A, W, V):
    AW = A @ W
    AWV = AW @ V
    return jnp.array([jnp.trace(AWV), jnp.trace(AW @ W @ V), jnp.trace(AWV @ V)])


@jit
def _3d_hemitropic_3a_rank_2(W, V, U):
    return jnp.trace(W @ V @ U)


@jit
def _3d_hemitropic_2s_rank_2_1_vec(A, B, v):
    AB = A @ B
    return jnp.array(
        [
            jnp.inner(v, axial_vector(AB)),
            jnp.inner(v, axial_vector(A @ AB)),
            jnp.inner(v, axial_vector(AB @ B)),
            scalar_triple_prod(v, A @ v, B @ v),
        ]
    )


@jit
def _3d_hemitropic_1s_1a_rank_2_1_vec(A, W, v):
    AW = A @ W
    return jnp.array(
        [
            jnp.inner(v, AW @ v),
            jnp.inner(v, axial_vector(AW)),
            jnp.inner(v, axial_vector(AW @ W)),
        ]
    )


@jit
def _3d_hemitropic_2a_rank_2_1_vec(W, V, v):
    return jnp.inner(v, axial_vector(W @ V))


@jit
def _3d_hemitropic_1s_rank_2_2_vec(A, v, u):
    au = A @ u
    return jnp.array(
        [
            jnp.inner(v, au),
            scalar_triple_prod(v, u, A @ v),
            scalar_triple_prod(v, u, au),
        ]
    )


@jit
def _3d_hemitropic_1a_rank_2_2_vec(W, v, u):
    return jnp.inner(v, W @ u)


@jit
def _3d_hemitropic_3_vec(v, u, w):
    return scalar_triple_prod(v, u, w)


"""
2-d versions of the above (and more) where applicable
"""


@jit
def _2d_isotropic_1s_rank_2(A):
    return jnp.array([jnp.trace(A), jnp.trace(A @ A)])


@jit
def _2d_isotropic_1a_rank_2(W):
    return jnp.trace(W @ W)


@jit
def _2d_isotropic_1_vec(v):
    return jnp.inner(v, v)


@jit
def _2d_isotropic_1_rank_3(T):
    return TcontrS(T, T)


@jit
def _2d_isotropic_2s_rank_2(A, B):
    return jnp.trace(A @ B)


@jit
def _2d_isotropic_2a_rank_2(W, V):
    return jnp.trace(W @ V)


@jit
def _2d_isotropic_1s_rank_2_1_vec(A, v):
    return jnp.inner(v, A @ v)


@jit
def _2d_isotropic_2_vec(v, u):
    return jnp.inner(v, u)


@jit
def _2d_isotropic_2_rank_3(T, S):
    return TcontrS(T, S)


@jit
def _2d_isotropic_1_rank_3_1_vec(T, v):
    return jnp.inner(v, tv(T, v))


@jit
def _2d_isotropic_1_rank_3_1s_rank_2(T, A):
    ta = tA(T, A)
    return jnp.inner(tA, A @ tA)


@jit
def _2d_isotropic_1s_1a_rank_2(A, W):
    return jnp.array([])


@jit
def _2d_isotropic_1a_rank_2_1_vec(W, v):
    return jnp.array([])


@jit
def _2d_hemitropic_1a_rank_2(W):
    return jnp.trace(eps_ij @ W)


"""
These are tables mapping output tensor types to functions that compute the form-invariants that 
make up the output basis.
"""
_2d_hemitropic_1s_rank_2_outputs = {
    TensorType(2, (2, 2), True, False): _2d_hmt_1sr2_o_s2,
}

_2d_hemitropic_1a_rank_2_outputs = {}

_2d_hemitropic_1_vec_outputs = {
    TensorType(1, (2,), False, False): _2d_hmt_1_vec_o_vec,
    TensorType(
        2,
        (
            2,
            2,
        ),
        True,
        False,
    ): _2d_hmt_1_vec_o_s2,
    TensorType(3, (2, 2, 2), True, False): _2d_hmt_1_vec_o_s3,
    TensorType(3, (2, 2, 2), False, False): _2d_hmt_1_vec_o_r3,
}

_2d_hemitropic_1_rank_3_outputs = {
    TensorType(3, (2, 2, 2), False, False): _2d_hmt_1_r3_o_r3
}

_2d_isotropic_2s_rank_2_outputs = {
    TensorType(2, (2, 2), False, True): _2d_iso_2sr2_o_a2,
}


_2d_isotropic_2a_rank_2_outputs = {}


_2d_isotropic_1s_1a_rank_2_outputs = {
    TensorType(2, (2, 2), True, False): _2d_iso_1sr2_1ar2_o_s2,
}

_2d_isotropic_1s_rank_2_1_vec_outputs = {
    TensorType(1, (2,), False, False): _2d_iso_1sr2_1_vec_o_vec,
    TensorType(2, (2, 2), False, True): _2d_iso_1sr2_1_vec_o_a2,
    TensorType(3, (2, 2, 2), True, False): _2d_iso_1sr2_1_vec_o_s3,
}

_2d_isotropic_1a_rank_2_1_vec_outputs = {
    TensorType(3, (2, 2, 2), True, False): _2d_iso_1ar2_1_vec_o_s3,
}

_2d_isotropic_2_vec_outputs = {
    TensorType(2, (2, 2), True, False): _2d_iso_2_vec_o_s2,
    TensorType(2, (2, 2), False, True): _2d_iso_2_vec_o_a2,
    TensorType(3, (2, 2, 2), True, False): _2d_iso_2_vec_o_s3,
}

_2d_isotropic_2_rank_3_outputs = {
    TensorType(2, (2, 2), False, True): _2d_iso_2_r3_o_a2,
}


_2d_isotropic_1_rank_3_1_vec_outputs = {
    TensorType(1, (2,), False, False): _2d_iso_1r3_1_vec_o_vec,
    TensorType(2, (2, 2), True, False): _2d_iso_1r3_1_vec_o_s2,
    TensorType(2, (2, 2), False, True): _2d_iso_1r3_1_vec_o_a2,
}


_2d_isotropic_1_rank_3_1s_rank_2_outputs = {
    TensorType(1, (2,), False, False): _2d_iso_1r3_1sr2_o_vec,
    TensorType(2, (2, 2), True, False): _2d_iso_1r3_1sr2_o_s2,
    TensorType(2, (2, 2), False, True): _2d_iso_1r3_1sr2_o_a2,
    TensorType(3, (2, 2, 2), False, False): _2d_iso_1r3_1sr2_o_3,
}

_2d_isotropic_1_vec_outputs = {
    TensorType(1, (2,), False, False): _2d_iso_1_vec_o_vec,
    TensorType(2, (2, 2), True, False): _2d_iso_1_vec_o_s2,
    TensorType(3, (2, 2, 2), False, False): _2d_iso_1_vec_o_r3,
}

_2d_isotropic_1_rank_3_outputs = {
    TensorType(3, (2, 2, 2), False, False): _2d_iso_1r3_o_3,
}

_2d_isotropic_1s_rank_2_outputs = {
    TensorType(2, (2, 2), True, False): _2d_iso_1sr2_o_s2,
    # TensorType(2,(2,2),False,True) : ,
}

_2d_isotropic_1a_rank_2_outputs = {
    TensorType(2, (2, 2), False, True): _2d_iso_1ar2_o_a2,
}

_3d_identity_outputs = {
    TensorType(2, (3, 3), True, False): _3d_idf,
}

_2d_identity_outputs = {
    TensorType(2, (2, 2), True, False): _2d_idf,
}

_3d_hemitropic_1s_rank_2_outputs = {
    # rhs reads like "3-d hemitropic (1 symmetric rank 2) -> (symmetric rank 2) outputs function"
    TensorType(2, (3, 3), True, False): _3d_hmt_1sr2_o_s2,
}

_3d_hemitropic_1a_rank_2_outputs = {
    TensorType(2, (3, 3), True, False): _3d_hmt_1ar2_o_s2,
    TensorType(2, (3, 3), False, True): _3d_hmt_1ar2_o_a2,
    TensorType(1, (3,), False, False): _3d_hmt_1ar2_o_vec,
}

_3d_hemitropic_1_vec_outputs = {
    TensorType(2, (3, 3), True, False): _3d_hmt_1vec_o_s2,
    TensorType(2, (3, 3), False, True): _3d_hmt_1vec_o_a2,
    TensorType(1, (3,), False, False): _3d_hmt_1vec_o_vec,
}

_3d_isotropic_1s_rank_2_1_vec_outputs = {
    TensorType(2, (3, 3), True, False): _3d_iso_1sr21vec_o_s2,
    TensorType(2, (3, 3), False, True): _3d_iso_1sr21vec_o_a2,
    TensorType(1, (3,), False, False): _3d_iso_1sr21vec_o_vec,
}

_3d_isotropic_2_vec_outputs = {
    TensorType(2, (3, 3), True, False): _3d_iso_2vec_o_s2,
    TensorType(2, (3, 3), False, True): _3d_iso_2vec_o_a2,
}

_3d_hemitropic_3s_rank_2_outputs = {
    TensorType(2, (3, 3), True, False): _3d_hmt_3sr2_o_s2,
    TensorType(2, (3, 3), False, True): _3d_hmt_3sr2_o_a2,
    TensorType(1, (3,), False, False): _3d_hmt_3sr2_o_vec,
}

_3d_hemitropic_3a_rank_2_outputs = {
    # TensorType(2,(3,3),False,True) : _3d_hmt_3ar2_o_s2,
    # TensorType(2,(3,3),False,True) : _3d_hmt_3ar2_o_a2,
    # TensorType(1,(3,),False,False) : _3d_hmt_3ar2_o_vec,
}

_3d_hemitropic_2s_rank_2_1_vec_outputs = {
    # TensorType(2,(3,3),False,True) : None,#_3d_hmt_2sr21vec_o_s2,
    # TensorType(2,(3,3),False,True) : _3d_hmt_2sr21vec_o_a2,
    # TensorType(1,(3,),False,False) : None,
}

_3d_hemitropic_1s_1a_rank_2_1_vec_outputs = {
    # TensorType(2,(3,3),False,True) : None,#_3d_hmt_1s1ar21vec_o_s2,
    # TensorType(2,(3,3),False,True) : None,#_3d_hmt_1s1ar21vec_o_a2,
    # TensorType(1,(3,),False,False) : None#_3d_hmt_1s1ar21vec_o_vec,
}

_3d_hemitropic_2a_rank_2_1_vec_outputs = {
    # TensorType(2,(3,3),False,True) : _3d_hmt_2ar21vec_o_s2,
    # TensorType(2,(3,3),False,True) : _3d_hmt_2ar21vec_o_a2,
    # TensorType(1,(3,),False,False) : _3d_hmt_2ar21vec_o_vec,
}

_3d_hemitropic_1s_rank_2_2_vec_outputs = {
    # TensorType(2,(3,3),False,True) : _3d_hmt_1sr22vec_o_s2,
    # TensorType(2,(3,3),False,True) : _3d_hmt_1sr22vec_o_a2,
    # TensorType(1,(3,),False,False) : _3d_hmt_1sr22vec_o_vec,
}

_3d_hemitropic_1a_rank_2_2_vec_outputs = {
    # TensorType(2,(3,3),False,True) : _3d_hmt_1ar22vec_o_s2,
    # TensorType(2,(3,3),False,True) : _3d_hmt_1ar22vec_o_a2,
    # TensorType(1,(3,),False,False) : _3d_hmt_1ar22vec_o_vec,
}

_3d_hemitropic_3_vec_outputs = {
    # TensorType(2,(3,3),False,True) : _3d_hmt_3vec_o_s2,
    # TensorType(2,(3,3),False,True) : _3d_hmt_3vec_o_a2,
    # TensorType(1,(3,),False,False) : _3d_hmt_3vec_o_vec,
}

_3d_isotropic_2s_rank_2_1_vec_outputs = {
    # TensorType(2,(3,3),False,True) : None,#_3d_hmt_2sr21vec_o_s2,
    TensorType(2, (3, 3), False, True): _3d_iso_2sr21vec_o_a2,
    TensorType(1, (3,), False, False): _3d_iso_2sr21vec_o_vec,
}

_3d_isotropic_1s_1a_rank_2_1_vec_outputs = {
    # TensorType(2,(3,3),False,True) : None,#_3d_hmt_1s1ar21vec_o_s2,
    TensorType(2, (3, 3), False, True): _3d_iso_1s1ar21vec_o_a2,
    # TensorType(1,(3,),False,False) : None#_3d_hmt_1s1ar21vec_o_vec,
}

_3d_isotropic_2a_rank_2_1_vec_outputs = {
    # TensorType(2,(3,3),False,True) : _3d_hmt_2ar21vec_o_s2,
    # TensorType(2,(3,3),False,True) : _3d_hmt_2ar21vec_o_a2,
    TensorType(1, (3,), False, False): _3d_iso_2ar21vec_o_vec,
}

_3d_isotropic_1a_rank_2_2_vec_outputs = {
    TensorType(2, (3, 3), True, False): _3d_iso_1ar22vec_o_s2,
    TensorType(2, (3, 3), False, True): _3d_iso_1ar22vec_o_a2,
    # TensorType(1,(3,),False,False) : _3d_iso_1ar22vec_o_vec
}

_3d_isotropic_1s_rank_2_2_vec_outputs = {
    TensorType(2, (3, 3), True, False): _3d_iso_1sr22vec_o_s2,
    TensorType(2, (3, 3), False, True): _3d_iso_1sr22vec_o_a2,
    # TensorType(1,(3,),False,False) : _3d_iso_1sr22vec_o_vec
}

"""
These tables map specific combinations of input tensor types to a pair containing a function
to compute the input scalar invariants and one of the output tables from above.
"""


_3d_hemitropic_three_input_table = {
    (
        TensorType(2, (3, 3), True, False),
        TensorType(2, (3, 3), True, False),
        TensorType(2, (3, 3), True, False),
    ): (_3d_hemitropic_3s_rank_2, _3d_hemitropic_3s_rank_2_outputs),
    # (TensorType(2,(3,3),True,False),
    # TensorType(2,(3,3),True,False),
    # TensorType(2,(3,3),False,True)) : (_3d_hemitropic_2s_1a_rank_2,
    #                                    _3d_hemitropic_2s_1a_rank_2_outputs),
    # (TensorType(2,(3,3),True,False),
    # TensorType(2,(3,3),False,True),
    # TensorType(2,(3,3),False,True)) : (_3d_hemitropic_1s_2a_rank_2,
    #                                    _3d_hemitropic_1s_2a_rank_2_outputs),
    # (TensorType(2,(3,3),False,True),
    # TensorType(2,(3,3),False,True),
    # TensorType(2,(3,3),False,True)) : (_3d_hemitropic_3a_rank_2,
    #                                    _3d_hemitropic_3a_rank_2_outputs),
    (
        TensorType(2, (3, 3), True, False),
        TensorType(2, (3, 3), True, False),
        TensorType(1, (3,), False, False),
    ): (_3d_hemitropic_2s_rank_2_1_vec, _3d_hemitropic_2s_rank_2_1_vec_outputs),
    (
        TensorType(2, (3, 3), True, False),
        TensorType(2, (3, 3), False, True),
        TensorType(1, (3,), False, False),
    ): (_3d_hemitropic_1s_1a_rank_2_1_vec, _3d_hemitropic_1s_1a_rank_2_1_vec_outputs),
    (
        TensorType(2, (3, 3), False, True),
        TensorType(2, (3, 3), False, True),
        TensorType(1, (3,), False, False),
    ): (_3d_hemitropic_2a_rank_2_1_vec, _3d_hemitropic_2a_rank_2_1_vec_outputs),
    (
        TensorType(2, (3, 3), True, False),
        TensorType(1, (3,), False, False),
        TensorType(1, (3,), False, False),
    ): (_3d_hemitropic_1s_rank_2_2_vec, _3d_hemitropic_1s_rank_2_2_vec_outputs),
    (
        TensorType(2, (3, 3), False, True),
        TensorType(1, (3,), False, False),
        TensorType(1, (3,), False, False),
    ): (_3d_hemitropic_1a_rank_2_2_vec, _3d_hemitropic_1a_rank_2_2_vec_outputs),
    (
        TensorType(1, (3,), False, False),
        TensorType(1, (3,), False, False),
        TensorType(1, (3,), False, False),
    ): (_3d_hemitropic_3_vec, _3d_hemitropic_3_vec_outputs),
}


# future possible elements of the below table.
# (TensorType(2,(3,3),True,False),
#    TensorType(2,(3,3),True,False),
#     TensorType(2,(3,3),True,False)) : (None,None),
#    (TensorType(2,(3,3),True,False),
#     TensorType(2,(3,3),True,False),
#     TensorType(2,(3,3),False,True)) : (None,None),
#    (TensorType(2,(3,3),True,False),
#     TensorType(2,(3,3),False,True),
#     TensorType(2,(3,3),False,True)) : (None,None),
#    (TensorType(2,(3,3),False,True),
#     TensorType(2,(3,3),False,True),
#     TensorType(2,(3,3),False,True)) : (None,None),


_3d_isotropic_three_input_table = {
    (
        TensorType(2, (3, 3), True, False),
        TensorType(2, (3, 3), True, False),
        TensorType(1, (3,), False, False),
    ): (_3d_isotropic_2s_rank_2_1_vec, _3d_isotropic_2s_rank_2_1_vec_outputs),
    (
        TensorType(2, (3, 3), True, False),
        TensorType(2, (3, 3), False, True),
        TensorType(1, (3,), False, False),
    ): (_3d_isotropic_1s_1a_rank_2_1_vec, _3d_isotropic_1s_1a_rank_2_1_vec_outputs),
    (
        TensorType(2, (3, 3), False, True),
        TensorType(2, (3, 3), False, True),
        TensorType(1, (3,), False, False),
    ): (_3d_isotropic_2a_rank_2_1_vec, _3d_isotropic_2a_rank_2_1_vec_outputs),
    (
        TensorType(2, (3, 3), True, False),
        TensorType(1, (3,), False, False),
        TensorType(1, (3,), False, False),
    ): (_3d_isotropic_1s_rank_2_2_vec, _3d_isotropic_1s_rank_2_2_vec_outputs),
    (
        TensorType(2, (3, 3), False, True),
        TensorType(1, (3,), False, False),
        TensorType(1, (3,), False, False),
    ): (_3d_isotropic_1a_rank_2_2_vec, _3d_isotropic_1a_rank_2_2_vec_outputs),
}

# _3d_isotropic_four_input_table = {
#    '''(TensorType(2,(3,3),True,False),
#     TensorType(2,(3,3),True,False),
#     TensorType(1,(3,),False,False),
#     TensorType(1,(3,),False,False)) : (_3d_isotropic_2s_2_vec,
#                                        _3d_isotropic_2s_2_vec_outputs),
#    (TensorType(2,(3,3),True,False),
#     TensorType(2,(3,3),False,True),
#     TensorType(1,(3,),False,False),
#     TensorType(1,(3,),True,False)) : (_3d_isotropic_1s_1a_2_vec,
#                                       _3d_isotropic_1s_1a_2_vec_outputs),
#    (TensorType(2,(3,3),True,False),
#     TensorType(2,(3,3),False,True),
#     TensorType(1,(3,),False,False),
#     TensorType(1,(3,),False,False)) : (_3d_isotropic_2a_2_vec,
#                                        _3d_isotropic_2a_2_vec_outputs),'''
# }


# _3d_hemitropic_four_input_table = {
#    '''(TensorType(2,(3,3),True,False),
#     TensorType(2,(3,3),True,False),
#     TensorType(1,(3,),False,False),
#     TensorType(1,(3,),False,False)) : (None,None),
#    (TensorType(2,(3,3),True,False),
#     TensorType(2,(3,3),False,True),
#     TensorType(1,(3,),False,False),
#     TensorType(1,(3,),True,False)) : (None,None),
#    (TensorType(2,(3,3),True,False),
#     TensorType(2,(3,3),False,True),
#     TensorType(1,(3,),False,False),
#     TensorType(1,(3,),False,False)) : (None,None),'''
# }


_3d_isotropic_single_input_table = {
    # maps input types to invariant calculation functions
    # read "_3d_hemitroic_1s_rank_2" as "a function giving scalar invariants for SO(3) in 3-D where the input is one symmetric rank-two tensor", and likewise with "_1a_" and antisymmetric
    (TensorType(2, (3, 3), True, False),): (
        _3d_hemitropic_1s_rank_2,
        _3d_hemitropic_1s_rank_2_outputs,
    ),
    (TensorType(2, (3, 3), False, True),): (
        _3d_hemitropic_1a_rank_2,
        _3d_hemitropic_1a_rank_2_outputs,
    ),
    (TensorType(1, (3,), False, False),): (
        _3d_hemitropic_1_vec,
        _3d_hemitropic_1_vec_outputs,
    ),
    (TensorType(0, (), False, False),): (
        lambda x: x,
        {TensorType(0, (), False, False): lambda x: 1.0},
    ),
}

_3d_isotropic_1_vec_outputs = {
    # where they both exist, hemitropic and isotropic form-invariants are the same in this case
    TensorType(2, (3, 3), True, False): _3d_hmt_1vec_o_s2,
    TensorType(1, (3,), False, False): _3d_hmt_1vec_o_vec,
}

_3d_hemitropic_2s_rank_2_outputs = {
    TensorType(2, (3, 3), True, False): _3d_hmt_2sr2_o_s2,
    TensorType(2, (3, 3), False, True): _3d_hmt_2sr2_o_a2,
    TensorType(1, (3,), False, False): _3d_hmt_2sr2_o_vec,
}

_3d_hemitropic_1s_1a_rank_2_outputs = {
    TensorType(2, (3, 3), True, False): _3d_hmt_1s1ar2_o_s2,
    TensorType(2, (3, 3), False, True): _3d_hmt_1s1ar2_o_a2,
    TensorType(1, (3,), False, False): _3d_hmt_1s1ar2_o_vec,
}

_3d_hemitropic_2a_rank_2_outputs = {
    TensorType(2, (3, 3), True, False): _3d_hmt_2ar2_o_s2,
    TensorType(2, (3, 3), False, True): _3d_hmt_2ar2_o_a2,
    TensorType(1, (3,), False, False): _3d_hmt_2ar2_o_vec,
}

_3d_hemitropic_1s_rank_2_1_vec_outputs = {
    TensorType(2, (3, 3), True, False): _3d_hmt_1sr21vec_o_s2,
    TensorType(2, (3, 3), False, True): _3d_hmt_1sr21vec_o_a2,
    TensorType(1, (3,), False, False): _3d_hmt_1sr21vec_o_vec,
}

_3d_hemitropic_1a_rank_2_1_vec_outputs = {
    TensorType(2, (3, 3), True, False): _3d_hmt_1sr21vec_o_s2,
    TensorType(2, (3, 3), False, True): _3d_hmt_1sr21vec_o_a2,
    TensorType(1, (3,), False, False): _3d_hmt_1sr21vec_o_vec,
}

_3d_isotropic_1a_rank_2_1_vec_outputs = {
    TensorType(2, (3, 3), True, False): _3d_iso_1sr21vec_o_s2,
    TensorType(2, (3, 3), False, True): _3d_iso_1sr21vec_o_a2,
    TensorType(1, (3,), False, False): _3d_iso_1sr21vec_o_vec,
}

_3d_hemitropic_2_vec_outputs = {
    TensorType(2, (3, 3), True, False): _3d_hmt_2vec_o_s2,
    TensorType(2, (3, 3), False, True): _3d_hmt_2vec_o_a2,
    TensorType(1, (3,), False, False): _3d_hmt_2vec_o_vec,
}

_3d_hemitropic_two_input_table = {
    # read "_3d_hemitroic_2s_rank_2" as "a function giving scalar invariants for SO(3) in 3-D where the inputs are two symmetric rank-two tensors"
    (TensorType(2, (3, 3), True, False), TensorType(2, (3, 3), True, False)): (
        _3d_hemitropic_2s_rank_2,
        _3d_hemitropic_2s_rank_2_outputs,
    ),
    (TensorType(2, (3, 3), True, False), TensorType(2, (3, 3), False, True)): (
        _3d_hemitropic_1s_1a_rank_2,
        _3d_hemitropic_1s_1a_rank_2_outputs,
    ),
    (TensorType(2, (3, 3), False, True), TensorType(2, (3, 3), False, True)): (
        _3d_hemitropic_2a_rank_2,
        _3d_hemitropic_2a_rank_2_outputs,
    ),
    (TensorType(2, (3, 3), True, False), TensorType(1, (3,), False, False)): (
        _3d_hemitropic_1s_rank_2_1_vec,
        _3d_hemitropic_1s_rank_2_1_vec_outputs,
    ),
    (TensorType(2, (3, 3), False, True), TensorType(1, (3,), False, False)): (
        _3d_hemitropic_1a_rank_2_1_vec,
        _3d_hemitropic_1a_rank_2_1_vec_outputs,
    ),
    (TensorType(1, (3,), False, False), TensorType(1, (3,), False, False)): (
        _3d_hemitropic_2_vec,
        _3d_hemitropic_2_vec_outputs,
    ),
}


_2d_isotropic_two_input_table = {
    (TensorType(2, (2, 2), True, False), TensorType(2, (2, 2), True, False)): (
        _2d_isotropic_2s_rank_2,
        _2d_isotropic_2s_rank_2_outputs,
    ),
    (TensorType(2, (2, 2), False, True), TensorType(2, (2, 2), False, True)): (
        _2d_isotropic_2a_rank_2,
        _2d_isotropic_2a_rank_2_outputs,
    ),
    (TensorType(2, (2, 2), True, False), TensorType(2, (2, 2), False, True)): (
        _2d_isotropic_1s_1a_rank_2,
        _2d_isotropic_1s_1a_rank_2_outputs,
    ),
    (TensorType(2, (2, 2), True, False), TensorType(1, (2,), False, False)): (
        _2d_isotropic_1s_rank_2_1_vec,
        _2d_isotropic_1s_rank_2_1_vec_outputs,
    ),
    (TensorType(2, (2, 2), False, True), TensorType(1, (2,), False, False)): (
        _2d_isotropic_1a_rank_2_1_vec,
        _2d_isotropic_1a_rank_2_1_vec_outputs,
    ),
    (TensorType(1, (2,), False, False), TensorType(1, (2,), False, False)): (
        _2d_isotropic_2_vec,
        _2d_isotropic_2_vec_outputs,
    ),
    (TensorType(3, (2, 2, 2), False, False), TensorType(3, (2, 2, 2), False, False)): (
        _2d_isotropic_2_rank_3,
        _2d_isotropic_2_rank_3_outputs,
    ),
    (TensorType(3, (2, 2, 2), False, False), TensorType(1, (2,), False, False)): (
        _2d_isotropic_1_rank_3_1_vec,
        _2d_isotropic_1_rank_3_1_vec_outputs,
    ),
    (TensorType(3, (2, 2, 2), False, False), TensorType(2, (2, 2), True, False)): (
        _2d_isotropic_1_rank_3_1s_rank_2,
        _2d_isotropic_1_rank_3_1s_rank_2_outputs,
    ),
}


_3d_isotropic_two_input_table = {
    # read "_3d_hemitroic_2s_rank_2" as "a function giving scalar invariants for SO(3) in 3-D where the inputs are two symmetric rank-two tensors"
    (TensorType(2, (3, 3), True, False), TensorType(2, (3, 3), True, False)): (
        _3d_hemitropic_2s_rank_2,
        _3d_hemitropic_2s_rank_2_outputs,
    ),
    (TensorType(2, (3, 3), True, False), TensorType(2, (3, 3), False, True)): (
        _3d_hemitropic_1s_1a_rank_2,
        _3d_hemitropic_1s_1a_rank_2_outputs,
    ),
    (TensorType(2, (3, 3), False, True), TensorType(2, (3, 3), False, True)): (
        _3d_hemitropic_2a_rank_2,
        _3d_hemitropic_2a_rank_2_outputs,
    ),
    (TensorType(2, (3, 3), True, False), TensorType(1, (3,), False, False)): (
        _3d_isotropic_1s_rank_2_1_vec,
        _3d_isotropic_1s_rank_2_1_vec_outputs,
    ),
    (TensorType(2, (3, 3), False, True), TensorType(1, (3,), False, False)): (
        _3d_isotropic_1a_rank_2_1_vec,
        _3d_isotropic_1a_rank_2_1_vec_outputs,
    ),
    (TensorType(1, (3,), False, False), TensorType(1, (3,), False, False)): (
        _3d_isotropic_2_vec,
        _3d_isotropic_2_vec_outputs,
    ),
}

_3d_hemitropic_single_input_table = {
    # maps input types to invariant calculation functions
    # read "_3d_hemitroic_1s_rank_2" as "a function giving scalar invariants for SO(3) in 3-D where the input is one symmetric rank-two tensor", and likewise with "_1a_" and antisymmetric
    (TensorType(2, (3, 3), True, False),): (
        _3d_hemitropic_1s_rank_2,
        _3d_hemitropic_1s_rank_2_outputs,
    ),
    (TensorType(2, (3, 3), False, True),): (
        _3d_hemitropic_1a_rank_2,
        _3d_hemitropic_1a_rank_2_outputs,
    ),
    (TensorType(1, (3,), False, False),): (
        _3d_hemitropic_1_vec,
        _3d_hemitropic_1_vec_outputs,
    ),
    (TensorType(0, (), False, False),): (
        lambda x: x,
        {TensorType(0, (), False, False): lambda x: 1.0},
    ),
}

_2d_isotropic_single_input_table = {
    (TensorType(2, (2, 2), True, False),): (
        _2d_isotropic_1s_rank_2,
        _2d_isotropic_1s_rank_2_outputs,
    ),
    (TensorType(2, (2, 2), False, True),): (
        _2d_isotropic_1a_rank_2,
        _2d_isotropic_1a_rank_2_outputs,
    ),
    (TensorType(1, (2,), False, False),): (
        _2d_isotropic_1_vec,
        _2d_isotropic_1_vec_outputs,
    ),
    # doesn't matter if the rank-3 is totally symmetric/antisymmetric or not, they're all the same
    (TensorType(3, (2, 2, 2), False, False),): (
        _2d_isotropic_1_rank_3,
        _2d_isotropic_1_rank_3_outputs,
    ),
    (TensorType(3, (2, 2, 2), True, False),): (
        _2d_isotropic_1_rank_3,
        _2d_isotropic_1_rank_3_outputs,
    ),
    (TensorType(3, (2, 2, 2), False, True),): (
        _2d_isotropic_1_rank_3,
        _2d_isotropic_1_rank_3_outputs,
    ),
    (TensorType(0, (), False, False),): (
        lambda x: x,
        {TensorType(0, (), False, False): lambda x: [1.0]},
    ),
}

_2d_hemitropic_single_input_table = {
    # some of the entries are the same for hemi vs isotropic
    (TensorType(2, (2, 2), True, False),): (
        _2d_isotropic_1s_rank_2,
        _2d_hemitropic_1s_rank_2_outputs,
    ),
    (TensorType(2, (2, 2), False, True),): (
        _2d_hemitropic_1a_rank_2,
        _2d_hemitropic_1a_rank_2_outputs,
    ),
    (TensorType(1, (2,), False, False),): (
        _2d_isotropic_1_vec,
        _2d_hemitropic_1_vec_outputs,
    ),
    # doesn't matter if the rank-3 is totally symmetric/antisymmetric or not, they're all the same
    (TensorType(3, (2, 2, 2), False, False),): (
        _2d_isotropic_1_rank_3,
        _2d_hemitropic_1_rank_3_outputs,
    ),
    (TensorType(3, (2, 2, 2), True, False),): (
        _2d_isotropic_1_rank_3,
        _2d_hemitropic_1_rank_3_outputs,
    ),
    (TensorType(3, (2, 2, 2), False, True),): (
        _2d_isotropic_1_rank_3,
        _2d_hemitropic_1_rank_3_outputs,
    ),
    # a scalar
    (TensorType(0, (), False, False),): (
        lambda x: x,
        {TensorType(0, (), False, False): lambda x: 1.0},
    ),
}

_3d_zero_input_table = {(): (_3d_empty, _3d_identity_outputs)}

_2d_zero_input_table = {(): (_2d_empty, _2d_identity_outputs)}

"""
These tables map the number of inputs to the table above containing scalar invariant calculation
functions and output form-invariant calculation tables
"""

_2d_isotropic_scalar_input_table = {
    0: _2d_zero_input_table,
    1: _2d_isotropic_single_input_table,
    2: _2d_isotropic_two_input_table,
    # 3 : _2d_isotropic_three_input_table,
    # 4 : _2d_isotropic_four_input_table,
}

_2d_hemitropic_scalar_input_table = {
    0: _2d_zero_input_table,
    1: _2d_hemitropic_single_input_table,
    # 2 : _2d_isotropic_two_input_table,
    # 3 : _2d_isotropic_three_input_table,
    # 4 : _2d_isotropic_four_input_table,
}


_3d_hemitropic_scalar_input_table = {
    # maps number of inputs to (table mapping input types to invariant calculation functions)
    0: _3d_zero_input_table,
    1: _3d_hemitropic_single_input_table,
    2: _3d_hemitropic_two_input_table,
    3: _3d_hemitropic_three_input_table,
    # 4 : _3d_hemitropic_four_input_table,
}

_3d_isotropic_scalar_input_table = {
    # maps number of inputs to (table mapping input types to invariant calculation functions)
    0: _3d_zero_input_table,
    1: _3d_isotropic_single_input_table,
    2: _3d_isotropic_two_input_table,
    3: _3d_isotropic_three_input_table,
    # 4 : _3d_isotropic_four_input_table,
}


"""
For each supported group, these tables map that group to a table (above), which maps the number of inputs to a third table mapping input types to invariant calculation functions and an output fucntion table
"""

_3d_invariant_group_table = {
    # maps symmetry group to (table mapping number of inputs to (table mapping input types to invariant calculation functions))
    "O(3)": _3d_isotropic_scalar_input_table,
    "SO(3)": _3d_hemitropic_scalar_input_table,
}

_2d_invariant_group_table = {
    # maps symmetry group to (table mapping number of inputs to (table mapping input types to invariant calculation functions))
    "O(2)": _2d_isotropic_scalar_input_table,
    "SO(2)": _2d_hemitropic_scalar_input_table,
}

"""
The first layer of the hash table onion. Maps the number of spatial dimensions to a group table
"""

_scalar_invariant_function_table = {
    # maps spatial dimension to (table mapping symmetry group to (table mapping number of inputs to (table mapping input types to invariant calculation functions)))
    2: _2d_invariant_group_table,
    3: _3d_invariant_group_table,
}
