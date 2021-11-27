import jax
import jax.numpy as jnp
from pyadjoint_utils.jax_adjoint import ndarray, array
from pyadjoint import AdjFloat
from pyadjoint.enlisting import Enlist
from pyadjoint_utils import Block, JacobianIdentity
from pyadjoint import Control
from pyadjoint.overloaded_type import (
    OverloadedType,
    register_overloaded_type,
    create_overloaded_object,
)
from pyadjoint.overloaded_function import overload_function
from pyadjoint.tape import annotate_tape, get_working_tape, stop_annotating
from functools import wraps
from jax.tree_util import Partial as partial  # JAX-friendlier functools.partial
from jax.tree_util import tree_flatten, tree_unflatten, tree_leaves, tree_map
from itertools import product
from typing import Tuple, Optional, Callable, Iterable, Sequence, Union, Any, TypeVar
from .array import convert_arg
import logging

logger = logging.getLogger("CRIKit")

# These TypeVars express the fact that
# the overload_jax() function is a transformation
# from a general function to a pyadjoint-overloaded function
# (i.e. one that can take in OverloadedObject instances as inputs
# and return them as outputs, correctly taping the operation they represent)
Function = TypeVar("Function", bound=Callable)
OverloadedFunction = TypeVar("OverloadedFunction", bound=Callable)


class JAXBlock(Block):
    def __init__(
        self,
        func,
        args,
        outputs,
        argnums=None,
        nojit=False,
        jit_kwargs=None,
        pointwise=False,
        out_pointwise=None,
        compile_jacobian_stack=True,
        **kwargs,
    ):
        super().__init__()
        self._func_name = kwargs.get("func_name", None) or func.__name__
        self._holomorphic = kwargs.get("holomorphic", False)
        self._func = func
        self._differentiable_func = self._diff_func
        self._nojit = nojit
        self._jit_kwargs = jit_kwargs if jit_kwargs is not None else {}
        self._compiled_jacobian_stack = compile_jacobian_stack
        num_inputs = len(args)
        num_outputs = len(outputs)
        if argnums:
            self._tlm = jax.jacrev(
                self._differentiable_func,
                argnums=argnums,
                holomorphic=self._holomorphic,
            )
        else:
            self._tlm = jax.jacrev(
                self._differentiable_func, holomorphic=self._holomorphic
            )
        self._jvp_maker = _pushforward(self._differentiable_func)

        argnum_range = tuple(argnums) if argnums else range(num_inputs)
        self._tlm_argnums = argnum_range
        self._tlm_outnums = tuple(range(num_outputs))
        self._tlm_matrix_func = self._jit(
            jax.jacrev(self._diff_func, argnums=self._tlm_argnums)
        )
        self._pw_tlm_matrix_func = None
        self._vjpfuncs = [
            vector_jacobian_product(self._func, i, jitfun=self._jit)
            for i in argnum_range
        ]
        self._hesfuncs = [
            vector_jacobian_product(self._vjpfuncs[i], j, False, jitfun=self._jit)
            for i, j in product(range(len(argnum_range)), argnum_range)
        ]

        iarange = range(len(argnum_range))
        self._make_hvpfun = _make_hvpfun(self._differentiable_func)
        self._hessian = jax.hessian(
            self._differentiable_func, argnums=range(len(argnum_range))
        )
        self._dependencies = []
        self._outputs = []
        self._param_range = argnum_range

        # flatten args and add all dependencies. The input signature of the function is
        # typically something like ((arg1,arg2,...),param1,param2,...), so JAX's pytree
        # utilities are helpful for this stuff
        arg_leaves = []
        for a in args:
            if isinstance(a, (tuple, list)):
                for v in a:
                    arg_leaves.append(v)
            else:
                arg_leaves.append(a)

        if len(self._param_range) > len(arg_leaves):
            raise ValueError(
                f"There are more argument indices in argnums than there are arguments ({len(self._param_range)} > {len(arg_leaves)})"
            )
        if max(self._param_range) >= len(arg_leaves):
            raise ValueError(
                f"There is an argument index in argnums that is higher than the number of arguments ({max(self._param_range)} >= {len(arg_leaves)})"
            )

        # Record dependencies only for the specified arguments.
        for idx in self._param_range:
            self.add_dependency(arg_leaves[idx])

        leaves, self._treedef = tree_flatten(tuple(args))

        self._args = [convert_arg(x) for x in leaves]

        for out in outputs:
            self.add_output(out.create_block_variable())

        self._saved_outs = outputs
        self._single_output = num_outputs == 1

        # Handle pointwise specifications.
        self._in_pointwise = (
            (pointwise,) * num_inputs if isinstance(pointwise, bool) else pointwise
        )
        self._any_pointwise = any(self._in_pointwise)
        if out_pointwise is None:
            out_pointwise = self._any_pointwise
        self._out_pointwise = (
            (out_pointwise,) * num_outputs
            if isinstance(out_pointwise, bool)
            else out_pointwise
        )
        if len(self._in_pointwise) != num_inputs:
            raise ValueError(
                f"len(pointwise) != num_inputs. For each input, you must specify if it is defined pointwise. ({len(self._in_pointwise)} != {num_inputs})"
            )
        if len(self._out_pointwise) != num_outputs:
            raise ValueError(
                f"len(pointwise) != num_outputs. For each output, you must specify if it is defined pointwise. ({len(self._out_pointwise)} != {num_outputs})"
            )
        if any(self._in_pointwise) and not any(self._out_pointwise):
            raise ValueError(
                "There is a pointwise input and no pointwise outputs. If an input is specified as pointwise, then at least one output must be specified as pointwise."
            )
        if any(self._out_pointwise) and not any(self._in_pointwise):
            raise ValueError(
                "There is a pointwise output and no pointwise inputs. If an output is specified as pointwise, then at least one input must be specified as pointwise."
            )

        self._compiled_jacobian = False

    def _jit(self, func):
        return func if self._nojit else jax.jit(func, **self._jit_kwargs)

    def _diff_func(self, *args):
        leaves, treedef = tree_flatten(tuple(args))
        self._replace_params(leaves)
        argtree = tree_unflatten(self._treedef, self._args)
        args = tuple(convert_arg(x) for x in argtree)
        return self._func(*args)

    def _make_partial_diff_func(self, idxs):
        def _pdiff_func(*args):
            leaves, treedef = tree_flatten(tuple(args))
            param_idxs = [self._param_range[idx] for idx in idxs]
            self._replace_params_partial(args, param_idxs)
            argtree = tree_unflatten(self._treedef, self._args)
            args = tuple(convert_arg(x) for x in argtree)
            return self._func(*args)

        return _pdiff_func

    def _replace_params(self, new_params):
        for new_param, idx in zip(new_params, self._param_range):
            par = convert_arg(new_param)
            self._args[idx] = par

    def _replace_params_partial(self, new_params, idxs):
        for i, idx in enumerate(idxs):
            self._args[idx] = convert_arg(new_params[i])

    def _get_reduced_output_diff_func(self, output_ids):
        if self._single_output:
            return self._diff_func

        def diff_func_relevant(*args):
            outputs = self._diff_func(*args)
            outputs = tuple(outputs[idx] for idx in output_ids)
            return outputs

        return diff_func_relevant

    def _add_params(self, deltas):
        for i, idx in enumerate(self._param_range):
            self._args[idx] += convert_arg(deltas[i])

    def __repr__(self):
        return f"JAXBlock({self._func_name})"

    def prepare_recompute_component(self, inputs, relevant_outputs):
        return Enlist(self._diff_func(*inputs))

    def recompute_component(self, inputs, block_variable, idx, prepared):
        if prepared:
            return prepared[idx]
        elif self._saved_outs:
            return self._saved_outs[idx]
        else:
            self._replace_params(inputs)
            self._saved_outs = Enlist(self._differentiable_func(*self._args))
            return self._saved_outs[idx]

    def prepare_evaluate_hessian(
        self, inputs, hessian_inputs, adj_inputs, relevant_dependencies
    ):

        raise NotImplementedError
        tlm_inputs = [dep.tlm_value for dep in self.get_dependencies()]

        out_idx = []
        ipts = []
        for i, ip in enumerate(inputs):
            if ip is not None:
                out_idx.append(i)
                ipts.append(convert_arg(ip))

        N = len(self._vjpfuncs)
        hvp = [None] * N
        for (i, j), f in zip(
            product(self._tlm_argnums, self._tlm_argnums), self._hesfuncs
        ):
            x_dot = convert_arg(tlm_inputs[i])
            if x_dot is None:
                continue

            tmp = f(*ipts, *tuple(convert_arg(x) for x in adj_inputs), x_dot)
            if hvp[j] is None:
                hvp[j] = tmp
            else:
                hvp[j] = hvp[j] + tmp

        return hvp

    def evaluate_hessian_component(
        self,
        inputs,
        hessian_inputs,
        adj_inputs,
        block_variable,
        idx,
        relevant_dependencies,
        prepared=None,
    ):
        return prepared[idx]

    def prepare_evaluate_tlm(self, inputs, tlm_inputs, relevant_outputs):
        out_idx = []
        ipts = []
        tips = []
        for i, (ip, ti) in enumerate(zip(inputs, tlm_inputs)):
            if ti is not None:
                out_idx.append(i)
                ipts.append(convert_arg(ip))
                tips.append(convert_arg(ti))
        jvp_maker = _pushforward(self._make_partial_diff_func(out_idx))
        jvpfun = jvp_maker(ipts)
        val = Enlist(jvpfun(*tips))
        return val

    def evaluate_tlm_component(
        self, inputs, tlm_inputs, block_variable, idx, prepared=None
    ):
        return prepared[idx]

    def prepare_evaluate_tlm_matrix(self, inputs, tlm_inputs, relevant_outputs):
        # Standardize argnums as collection to ensure return type from jacrev is also a collection
        argnums = []
        for i, x in enumerate(tlm_inputs):
            if x is not None:
                argnums.append(i)
                for j, di_dj in enumerate(x):
                    if (i != j and di_dj is not None) or (
                        i == j and not isinstance(di_dj, JacobianIdentity)
                    ):
                        raise NotImplementedError(
                            "Non-identity inputs cannot be handled yet."
                        )
        outnums = [idx for idx, bv in relevant_outputs]

        recompute_jac = (tuple(argnums) != tuple(self._tlm_argnums)) or (
            tuple(outnums) != tuple(self._tlm_outnums)
        )
        if recompute_jac:
            self._tlm_argnums = argnums
            diff_func_relevant = self._get_reduced_output_diff_func(outnums)
            self._tlm_matrix_func = self._jit(
                jax.jacrev(diff_func_relevant, argnums=argnums)
            )

        cargs = tuple(convert_arg(x) for x in inputs)
        if not self._any_pointwise:
            val = self._tlm_matrix_func(*cargs)
            if self._single_output:
                return (val,)

            # Expand reduced outputs back to the expected length.
            rv = [None] * len(self.get_outputs())
            for i, idx in enumerate(outnums):
                rv[idx] = val[i]
            return rv

        # Set up all arguments into a standard format that can be looped through pointwise.
        outputs = [bv.saved_output for bv in self.get_outputs()]
        out_shapes = [
            a.shape[1:] if pw else a.shape
            for a, pw in zip(outputs, self._out_pointwise)
        ]
        n = max(
            [a.shape[0] for a, pw in zip(cargs, self._in_pointwise) if pw]
            + [a.shape[0] for a, pw in zip(outputs, self._out_pointwise) if pw]
        )
        # Pad extra axis for cases where internal func is already vmapped
        standard_args = []
        for i, (a, pw) in enumerate(zip(cargs, self._in_pointwise)):
            if pw:
                if a.shape[0] not in (1, n):
                    raise ValueError(
                        f"Argument {i} is marked as pointwise but first axis doesn't match expected size ({a.shape[0]} != {n})"
                    )
                s = jnp.reshape(a, (a.shape[0], 1, *a.shape[1:]))
                s = jnp.broadcast_to(s, (n, *s.shape[1:]))
            else:
                s = a
            standard_args.append(s)

        # v is a tuple of size n. Each one is a tuple of size num_relevant_outputs. Each entry in that tuple is a tuple of size num_relevant_inputs.
        doutput_dinput = [None] * len(self.get_outputs())
        squeeze_didj = jax.jit(partial(jnp.squeeze, axis=1))
        # Build vmap spec based on input format
        tree_def = jax.tree_structure(standard_args)
        in_axes = jax.tree_util.build_tree(
            tree_def, [0 if a else None for a in self._in_pointwise]
        )
        # It doesn't seem possible to use a more fine-grained vmap for un-vmapped outputs since the Jacobian is
        # defined for any vmapped inputs even if the Jacobian is always going to be zero.
        out_axes = tuple(tuple(0 for j in argnums) for i in outnums)
        if self._single_output:
            out_axes = out_axes[0]
        # Generate block-wise jacobians in a batch then post-process
        if self._pw_tlm_matrix_func is None or recompute_jac:
            self._pw_tlm_matrix_func = self._jit(
                jax.vmap(self._tlm_matrix_func, in_axes=in_axes, out_axes=out_axes)
            )
        jac_blocks = self._pw_tlm_matrix_func(*standard_args)
        # Singleton outputs need to be padded
        if self._single_output:
            jac_blocks = [jac_blocks]

        # Iterate through and squeeze out unecessary axes generated by axis padding to match other backends.
        # It's probably possible to standardize this so we neither pad or squeeze,
        # but it's hard to see how without requiring the user to specify whether the inner function is already vmapped
        for i, out_idx in enumerate(outnums):
            out_pw = self._out_pointwise[out_idx]
            out_rank = len(out_shapes[out_idx])
            squeeze_didj_pw = jax.jit(partial(jnp.squeeze, axis=(1, 2 + out_rank)))
            squeeze_didj_in_pw = jax.jit(partial(jnp.squeeze, axis=1 + out_rank))
            if self._compiled_jacobian_stack and not self._compiled_jacobian:
                logger.warning(
                    "About to compile pointwise Jacobian-stacking function; this may take a few minutes..."
                )
                self._compiled_jacobian = True  # rather, it will be True in
                # a few lines once we call _pointjac_stack_XXX for the first
                # time
            di_dinput = [None] * len(argnums)
            for j, in_idx in enumerate(argnums):
                in_pw = self._in_pointwise[in_idx]
                di_dj = jac_blocks[i][j]
                if out_pw:
                    if in_pw:
                        #  out_i: (n, *output_shape)
                        #  arg_j: (n, *input_shape)
                        #  di_dj: (n, 1, *output_shape, 1, *input_shape)
                        # di_dj': (n, *output_shape, *input_shape)
                        di_dj = squeeze_didj_pw(di_dj)
                    else:
                        #  out_i: (n, *output_shape)
                        #  arg_j: (*input_shape)
                        #  di_dj: (n, 1, *output_shape, *input_shape)
                        # di_dj': (n, *output_shape, *input_shape)
                        di_dj = squeeze_didj(di_dj)
                elif in_pw:
                    #  out_i: (*output_shape)
                    #  arg_j: (n, *input_shape)
                    #  di_dj: (*output_shape, n, 1, *input_shape)
                    # di_dj': (*output_shape, n, *input_shape)
                    di_dj = squeeze_didj_in_pw(di_dj)
                else:
                    # If neither is defined pointwise, the shapes should be this:
                    #  out_i: (*output_shape)
                    #  arg_j: (*input_shape)
                    #  di_dj: (n, *output_shape, *input_shape)
                    # di_dj': (*output_shape, *input_shape)
                    di_dj = di_dj[0, ...]
                di_dinput[j] = di_dj
            doutput_dinput[out_idx] = di_dinput
        return doutput_dinput

    def evaluate_tlm_matrix_component(
        self, inputs, tlm_inputs, block_variable, idx, prepared=None
    ):
        return prepared[idx]

    def prepare_evaluate_adj(self, inputs, adj_inputs, relevant_dependencies):
        relevant_outputs_idxs = [
            idx for idx, adj in enumerate(adj_inputs) if adj is not None
        ]
        diff_func_relevant = self._get_reduced_output_diff_func(relevant_outputs_idxs)

        outs, fvjp = jax.vjp(diff_func_relevant, *tuple(convert_arg(x) for x in inputs))
        fvjp = self._jit(fvjp)

        adj_inputs = tuple(
            convert_arg(adj_inputs[idx]) for idx in relevant_outputs_idxs
        )
        if self._single_output:
            adj_inputs = adj_inputs[0]
        return Enlist(fvjp(adj_inputs))

    def evaluate_adj_component(
        self, inputs, adj_inputs, block_variable, idx, prepared=None
    ):
        return prepared[idx]


def _pushforward(func):
    def prepare_jvp(inputs):
        outputs, jvp_func = jax.linearize(func, *inputs)
        return jax.jit(jvp_func)

    return prepare_jvp


def _pullback(func, argnum):
    def prepare_vjp(inputs, adj_inputs):
        outputs, vjp_func = jax.vjp(func, *inputs)
        vjp_func = jax.jit(vjp_func)
        return vjp_func(*adj_inputs)

    def eval_vjp_component(prepared):
        return prepared[argnum]

    return prepare_vjp, eval_vjp_component


def _make_hvpfun(f):
    def make_hvp(inputs, adj_inputs):
        outs, fvjp = jax.vjp(f, *tuple(convert_arg(x) for x in inputs))
        outs, fhvp = jax.linearize(
            jax.jit(fvjp), *tuple(convert_arg(x) for x in adj_inputs)
        )
        return jax.jit(fhvp)

    return make_hvp


def vector_jacobian_product(fun, argnum, reverse=True, jitfun=jax.jit):
    # based on the old autograd implementation
    def vec_prod(*args, **kwargs):
        args, x_dot = args[:-1], args[-1]
        return jnp.tensordot(x_dot, fun(*args, **kwargs), axes=jnp.ndim(x_dot))

    if reverse:
        return jax.jacrev(vec_prod, argnums=argnum)
    return jitfun(jax.jacfwd(vec_prod, argnums=argnum))


def is_tracer(x):
    return isinstance(x, jax.core.Tracer)


def get_overloaded(x: Any) -> OverloadedType:
    if isinstance(x, (ndarray, tuple)):
        return x
    return create_overloaded_object(x)


def overload_jax(
    func: Function,
    static_argnums: Optional[Union[int, Iterable[int]]] = None,
    argnums: Optional[Union[int, Iterable[int]]] = None,
    nojit: Optional[bool] = False,
    function_name: Optional[str] = None,
    checkpoint: bool = False,
    concrete: bool = False,
    backend: Optional[str] = None,
    donate_argnums: Optional[Union[int, Iterable[int]]] = None,
    pointwise: Union[bool, Sequence[bool]] = False,
    out_pointwise: Optional[Union[bool, Sequence[bool]]] = None,
    compile_jacobian_stack: bool = True,
    **jax_kwargs,
) -> OverloadedFunction:
    """
    Creates a pyadjoint-overloaded version of a JAX-traceable function.

    :param func: The function to JIT compile and make differentiable
    :type func: Function
    :param static_argnums: The static_argnums parameter of jax.jit (e.g. numbers
        of arguments that, if changed, should trigger recompilation)
    :type static_argnums: Union[int,Iterable[int]], optional
    :param argnums: The numbers of the arguments you want to differentiate
        with respect to. For example, if you have a function f(x,p,w) and
        want the derivative with respect to p and w, pass argnums=(1,2).
    :type argnums: Union[int,Iterable[int]], optional
    :param nojit:  If True, do NOT JIT compile the function, defaults to False
    :type nojit: bool, optional
    :param function_name:  if you want the function's name on the JAXBlock recorded as
        something other than func.__name__, use this parameter
    :type function_name: str, optional
    :param checkpoint: if True, make `func` recompute internal linearization
        points when differentiated (as opposed to computing these in the forward
        pass and storing the results). This increases total FLOPs in exchange for
        less memory usage/fewer acceses, defaults to False
    :type checkpoint: bool, optional
    :param concrete: if True, indicates that the function requires value-dependent
        Python control flow, defaults to False
    :type concrete: bool, optional
    :param backend: String representing the XLA backend to use (e.g. 'cpu', 'gpu',
           'tpu'). (Note that this is an experimental JAX feature, and its API is
           likely to change), defaults to None
    :type backend: str, optional
    :param donate_argnums: Which arguments are 'donated' to the computation? In other
           words, you cannot reuse these arguments after calling the function. This
           lets XLA more aggresively re-use donated buffers., default None
    :type donate_argnums: Union[int,Iterable[int]], optional
    :param pointwise: By default, this is false. True means the function performs
        operations on a batch of points. This allows optimizing the Jacobian calculations
        by only computing the diagonal component. If a list, then there should be a bool
        for each argnum.
    :type pointwise: Union[bool,Sequence[bool]], optional
    :param out_pointwise: If any inputs are defined pointwise, this specifies which
        outputs are defined pointwise. If a list, then there should be abool for each
        output. By default, all outputs will be assumed pointwise if any inputs are
        pointwise.
    :type out_pointwise: Union[bool,Sequence[bool]], optional
    :param compile_jacobian_stack: If we need to make a Jacobian matrix
        corresponding to this function, and that computation is done pointwise,
        we have to `jnp.stack` the pointwise Jacobians into one full Jacobian.
        This parameter controls whether or not we compile that stack operation
        with `jax.jit`, which can take several minutes to compile the stack
        the first time a Jacobian is requested (since it requires unrolling
        a Python-mode loop over quadrature points), but often leads to
        factor-of-5-or-more improvements in the total time
        required to compute the Jacobian for subsequent evaluations. Defaults to True
    :type compile_jacobian_stack: bool, optional

    :return: A function with the same signature as `func` that performs the same
      computation, just with JAX JIT compilation, and being differentiable
      by both JAX and Pyadjoint
    :rtype: OverloadedFunction
    """

    if checkpoint:
        func = jax.checkpoint(func, concrete=concrete)
    # first, jit compile
    if not nojit:
        static_argnums = static_argnums or ()
        donate_argnums = donate_argnums or ()
        jit_kwargs = dict(
            static_argnums=static_argnums,
            backend=backend,
            donate_argnums=donate_argnums,
            **jax_kwargs,
        )
        func = jax.jit(func, **jit_kwargs)
    else:
        jit_kwargs = None
    # now overload

    @wraps(func)
    def _overloaded_func(*args, **kwargs):
        annotate = annotate_tape(kwargs)
        with stop_annotating():
            cargs = tuple(convert_arg(x) for x in args)
            out = func(*cargs, **kwargs)
            if is_tracer(out):
                return out
            for arg in cargs:
                if is_tracer(arg):
                    return out

        out = Enlist(out)
        overloads = [create_overloaded_object(arr) for arr in out]
        if annotate:
            tape = get_working_tape()
            kwargs["func_name"] = function_name
            block = JAXBlock(
                func,
                args,
                overloads,
                argnums=argnums,
                nojit=nojit,
                jit_kwargs=jit_kwargs,
                pointwise=pointwise,
                out_pointwise=out_pointwise,
                compile_jacobian_stack=compile_jacobian_stack,
                **kwargs,
            )
            tape.add_block(block)

        return out.delist(overloads)

    return _overloaded_func
