from autograd import vector_jacobian_product, jacobian
from autograd.numpy.numpy_boxes import ArrayBox
from autograd.numpy.numpy_vspaces import ArrayVSpace
from pyadjoint.enlisting import Enlist
from pyadjoint.overloaded_type import create_overloaded_object
from pyadjoint.tape import annotate_tape, get_working_tape, stop_annotating
from pyadjoint_utils import Block, JacobianIdentity
from pyadjoint import AdjFloat
from pyadjoint_utils.numpy_adjoint import ndarray
from itertools import product
from functools import wraps
import numpy as np

ArrayBox.register(ndarray)
ArrayBox.register(AdjFloat)
ArrayVSpace.register(ndarray)
ArrayVSpace.register(AdjFloat)


def overload_autograd(func, pointwise):
    """Create an overloaded version of an Autograd function.

    This method makes several assumptions:
    1) The function is explicit, i.e. ``y = func(x)``, where y is the output of the operation.
    2) All of y is possible to convert to an OverloadedType.
    3) Unless annotation is turned off, the operation should always be annotated when calling the overloaded function.

    After the overloaded function is called, the pointwise bool for each input
    is recorded in the function's pointwise attribute.

    Args:
        func (function): The target function for which to create an overloaded version.
        pointwise (bool or list[bool]): True means the function performs
            operations on a batch of points. This allows optimizing the Jacobian
            calculations by only computing the diagonal component. If a list,
            then there should be a bool for each input.
    Returns:
        function: An overloaded version of ``func``
    """

    @wraps(func)
    def _overloaded_function(*args, **kwargs):
        annotate = annotate_tape(kwargs)
        with stop_annotating():
            func_output = func(*args, **kwargs)

        func_output = Enlist(func_output)

        if len(func_output) > 1:
            raise ValueError(
                "overload_autograd currently only works with functions that output a single numpy array"
            )

        r = [create_overloaded_object(out) for out in func_output]
        if annotate:
            block = AutogradBlock(func, args, r, kwargs, pointwise=pointwise)
            _overloaded_function.pointwise = block._pointwise
            tape = get_working_tape()
            tape.add_block(block)

        return func_output.delist(r)

    _overloaded_function.pointwise = pointwise
    return _overloaded_function


def overloaded_autograd(pointwise):
    """Returns a decorator for Autograd functions that should be overloaded

    Args:
        pointwise (bool or list[bool]): See :func:`overload_autograd`.
    """

    def decorator(func):
        return overload_autograd(func, pointwise)

    return decorator


class AutogradBlock(Block):
    def __init__(self, func, args, outputs, func_kwargs, pointwise):
        super().__init__()

        self._func = func
        self._kwargs = func_kwargs

        nterms = len(args)

        if isinstance(pointwise, bool):
            self._pointwise = (pointwise,) * nterms
        else:
            self._pointwise = pointwise
        if len(self._pointwise) != nterms:
            raise ValueError(
                f"len(pointwise) != nterms. For each input, you must specify if it is defined pointwise. ({len(self._pointwise)} != {nterms})"
            )

        self._arg_shapes = [
            a.shape[1:] if pw else a.shape for a, pw in zip(args, self._pointwise)
        ]
        self._out_pointwise = any(self._pointwise)
        self._out_shape = (
            outputs[0].shape[1:] if self._out_pointwise else outputs[0].shape
        )

        self._vjpfuncs = [
            vector_jacobian_product(self._func, argnum=i) for i in range(nterms)
        ]

        # there is an autograd-forward project, but afaik it is not integrated yet, so we use the
        # twice-backwards trick with a dummy argument (Jamie Townsend,
        # https://j-towns.github.io/2017/06/12/A-new-trick.html)
        self._vjp2funcs = [
            vector_jacobian_product(self._vjpfuncs[i], argnum=nterms)
            for i in range(nterms)
        ]
        self._hesfuncs = [
            vector_jacobian_product(self._vjpfuncs[i], argnum=j)
            for i, j in product(range(nterms), range(nterms))
        ]

        self._tlm_matrix_funcs = [jacobian(self._func, argnum=i) for i in range(nterms)]

        for arg in args:
            self.add_dependency(arg)

        for out in outputs:
            self.add_output(out.block_variable)

    def __repr__(self):
        return f"AutogradBlock({self._func})"

    def prepare_recompute_component(self, inputs, relevant_outputs):
        return Enlist(self._func(*inputs, **self._kwargs))

    def recompute_component(self, inputs, block_variable, idx, prepared):
        return prepared[idx]

    def evaluate_adj_component(
        self, inputs, adj_inputs, block_variable, idx, prepared=None
    ):
        if len(adj_inputs) == 1:
            adj_inputs = adj_inputs[0]
        return self._vjpfuncs[idx](*inputs, adj_inputs, **self._kwargs)

    def prepare_evaluate_tlm(self, inputs, tlm_inputs, relevant_outputs):
        func_output = [bv.saved_output for bv in self.get_outputs()]
        jvp = None
        for f, x_dot in zip(self._vjp2funcs, tlm_inputs):
            if x_dot is None:
                continue
            tmp = Enlist(f(*inputs, *func_output, x_dot, **self._kwargs))
            if jvp is None:
                jvp = tmp
            else:
                for i in range(len(jvp)):
                    jvp[i] = jvp[i] + tmp[i]
        return jvp

    def evaluate_tlm_component(
        self, inputs, tlm_inputs, block_variable, idx, prepared=None
    ):
        return prepared[idx]

    def prepare_evaluate_hessian(
        self, inputs, hessian_inputs, adj_inputs, relevant_dependencies
    ):
        nterms = len(self._vjpfuncs)
        hvp = [None] * nterms
        tlm_inputs = [dep.tlm_value for dep in self.get_dependencies()]

        for (i, j), f in zip(product(range(nterms), range(nterms)), self._hesfuncs):
            x_dot = tlm_inputs[i]
            if x_dot is None:
                continue
            tmp = f(*inputs, *adj_inputs, x_dot, **self._kwargs)
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

    def _jac_iterator(self, inputs, mask):
        if self._out_pointwise:
            # Set up all standard arguments that can be looped through pointwise.
            n = self.get_outputs()[0].saved_output.shape[0]
            standard_args = []
            for i, (a, pw) in enumerate(zip(inputs, self._pointwise)):
                if pw:
                    if a.shape[0] not in (1, n):
                        raise ValueError(
                            f"Argument {i} is marked as pointwise but first axis doesn't match output ({a.shape[0]} != {n})"
                        )
                    s = np.reshape(a, (a.shape[0], 1, *a.shape[1:]))
                    s = np.broadcast_to(s, (n, *s.shape[1:]), subok=True)
                else:
                    s = np.broadcast_to(a, (n, *a.shape), subok=True)
                standard_args.append(s)

        # Compute Autograd Jacobian df_dy.
        for input_shape, pw, jac_func, mask_i in zip(
            self._arg_shapes, self._pointwise, self._tlm_matrix_funcs, mask
        ):
            if mask_i is None:
                yield None
                continue
            if pw:
                # Need to extract some shape information and then create the outputs with the correct shape.
                # The shapes should be the following:
                #   -     arg_i: (n, *input_shape)
                #   -    df_dyi: (n, *output_shape, *input_shape).
                point_rank = len(input_shape)
                df_dyi_shape = (n, 1) + self._out_shape + (1,) + input_shape
                v = (jac_func(*args, **self._kwargs) for args in zip(*standard_args))
                df_dyi = np.zeros(df_dyi_shape)
                for k, df_dyik in enumerate(v):
                    df_dyi[k, ...] = df_dyik
                df_dyi = np.squeeze(df_dyi, axis=(1, -point_rank - 1))
            else:
                df_dyi = jac_func(*inputs, **self._kwargs)
            yield (df_dyi)

    def evaluate_tlm_matrix_component(
        self, inputs, tlm_inputs, block_variable, idx, prepared=None
    ):
        """
        If df_dy is the Jacobian of the Autograd function, this will give
        the matrix product df_dx = df_dy * dy_dx, where df_dx is a list
        df_dx[i] = df_dxi and dy_dx is a list of lists such that dy_dx[i][j]
        is dyi_dxj.
        """
        # Just renaming.
        dy_dx = tlm_inputs

        # Get length of return value.
        for dyi_dx in dy_dx:
            if dyi_dx is not None:
                num_controls = len(dyi_dx)
                break
        else:
            return None
        rv = [None] * num_controls

        # Compute df_dx[j] = sum_f(df_dy[i] * dy_dx[i][j])
        n = self.get_outputs()[0].saved_output.shape[0]
        df_dy = self._jac_iterator(inputs, dy_dx)
        for df_dyi, dyi_dx, input_shape, pw in zip(
            df_dy, dy_dx, self._arg_shapes, self._pointwise
        ):
            if dyi_dx is None:
                continue
            for j in range(num_controls):
                if dyi_dx[j] is None:
                    continue
                # Multiply df_dyi (Jacobian) by dyi_dx[j] (the input Jacobian).
                if isinstance(dyi_dx[j], JacobianIdentity):
                    df_dxj = df_dyi
                else:
                    point_rank = len(input_shape)
                    if pw:
                        # The `extra` is e.g. the shape of the control xj.
                        # The shapes should be the following:
                        #   -    df_dyi: (n, *output_shape, *input_shape).
                        #   - dyi_dx[j]: (n, *input_shape, *extra)
                        #   -    df_dxj: (n, *output_shape, *extra).
                        # df_dxj is computed by contracting `df_dyi` with dyi_dx[j]
                        # pointwise along the *input_shape axes.
                        extra = dyi_dx[j].shape[1 + point_rank :]
                        df_dxj_shape = (n,) + self._out_shape + extra
                        w = (
                            np.tensordot(a, b, axes=point_rank)
                            for a, b in zip(df_dyi, dyi_dx[j])
                        )
                        df_dxj = np.zeros(df_dxj_shape)
                        for k, df_dxjk in enumerate(w):
                            df_dxj[k, ...] = df_dxjk
                    else:
                        df_dxj = np.tensordot(df_dyi, dyi_dx[j], axes=point_rank)

                if rv[j] is None:
                    rv[j] = df_dxj
                else:
                    rv[j] += df_dxj
        return rv
