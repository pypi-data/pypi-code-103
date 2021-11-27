from .types import PointMap
from contextlib import contextmanager
from pyadjoint.enlisting import Enlist
from pyadjoint import annotate_tape, get_working_tape, stop_annotating
from pyadjoint_utils import Tape, push_tape
from pyadjoint_utils.fenics_adjoint import assemble
from pyadjoint_utils.tape_block import record_tape_block, TapeBlock
from pyadjoint_utils import ReducedFunctionNumPy
from pyadjoint_utils.identity import JacobianIdentity, make_jacobian_identities
from dolfin.fem.formmanipulations import derivative
from ufl import replace, dot, inner, grad, Form, Coefficient
from ufl.algorithms import expand_derivatives
from ufl.core.expr import Expr
from ufl.log import error
from crikit.fe import contraction
from ..covering import get_composite_cr
from .ufl import UFLExprSpace, UFLFunctionSpace
from .space_builders import DirectSum
from ..cr.quadrature import (
    get_quadrature_params,
    make_quadrature_spaces,
    make_quadrature_space,
)
from ..cr.quadrature import estimate_total_polynomial_degree as est_degree
from .map_builders import CompositePointMap
import numpy as np
import jax.numpy as jnp
import jax
import ufl

from typing import Tuple, Union, Optional
import backend
from fenics_adjoint.compat import compat

compat = compat(backend)


def form_get_expr_space(form, exprs):
    terms = Enlist(exprs)
    domain = form.ufl_domain()
    spaces = tuple(UFLExprSpace(t, ufl_domains=(domain,)) for t in terms)
    space = terms.delist(spaces)
    if not isinstance(space, UFLExprSpace):
        space = DirectSum(*space)
    return space


def _assemble_with_cr(
    form, cr, arg, out_terms, quad_params=None, force_explicit=False, **kwargs
):
    """Substitute the output of cr applied to arg (tuple of UFL Exprs) in the form.

    If the cr does not handle UFL Expr inputs, convert to a quadrature element."""
    annotate = annotate_tape(kwargs)
    b_kwargs = AssembleWithCRBlock.pop_kwargs(kwargs)
    b_kwargs.update(kwargs)

    with push_tape() as assemble_tape:
        # First, the CR is converted to a ufl CR if necessary.
        explicit = force_explicit or not cr.source.is_point(arg)
        if not explicit:
            with stop_annotating():
                newexprs = cr(arg)
            term_space = form_get_expr_space(form, out_terms)
            explicit = not term_space.is_point(newexprs)
        if explicit:
            form, ufl_cr, quad_params = get_ufl_composite_cr(
                form, cr, arg, out_terms, quad_params=quad_params
            )
        else:
            ufl_cr = cr

        # Then, the CR is run on a separate tape (to facilitate faster Jacobian calculations).
        with record_tape_block(name="FullCRTapeBlock") as cr_tape_full:
            if explicit:
                # This assumes the cr consists of three point maps: input Covering, inner CR, and output Covering.
                point_maps = ufl_cr.point_maps()
                if len(point_maps) != 3:
                    raise ValueError(
                        "Expected 3 point maps in composite cr (got %d)"
                        % len(point_maps)
                    )
                if point_maps[1] != cr:
                    raise ValueError(
                        "Expected second point map in composite cr to be the original cr (%s != %s)"
                        % (point_maps[1], cr)
                    )

                inner_inputs = point_maps[0](arg)
                with record_tape_block(name="InnerCRTapeBlock") as cr_tape_inner:
                    inner_outputs = point_maps[1](inner_inputs)
                cr_outputs = point_maps[2](inner_outputs)

                cr_tape_info = {
                    "inner_inputs": Enlist(inner_inputs),
                    "cr_tape_inner": cr_tape_inner,
                    "inner_outputs": Enlist(inner_outputs),
                    "cr_outputs": Enlist(cr_outputs),
                }
            else:
                cr_tape_info = {}
                cr_outputs = ufl_cr(arg)

        # Finally, the outputs of the CR are put into the form, and the form is assembled.
        out_map = {}
        for expr, term in zip(Enlist(cr_outputs), Enlist(out_terms)):
            out_map[term] = expr
        newform = replace(form, out_map)
        a = assemble(newform, **kwargs)

    if annotate:
        working_tape = get_working_tape()
        block = AssembleWithCRBlock(
            assemble_tape,
            form,
            cr,
            arg,
            out_terms,
            quad_params=quad_params,
            cr_tape_full=cr_tape_full,
            explicit=explicit,
            **cr_tape_info,
            **b_kwargs,
        )
        working_tape.add_block(block)
    return a, form, ufl_cr


def assemble_with_cr(
    form: Form,
    cr: PointMap,
    arg: Union[Expr, Tuple[Expr]],
    out_terms: Union[Coefficient, Tuple[Coefficient]],
    quad_params: Optional[dict] = None,
    force_explicit: Optional[bool] = False,
    return_all: Optional[bool] = False,
    **kwargs,
):
    """Substitute the output of ``cr`` applied to ``arg`` in the form and then assemble the form.

    Given a UFL form that contains ``out_terms``, this function calculates
    ``cr_out = cr(arg)``, replaces each term in ``out_terms`` with the
    corresponding term in ``cr_out``, and assembles the resulting form.

    If ``cr`` can't take ``arg`` directly as input, or if it doesn't output
    Functions, or if ``force_explicit=True``, then
    :func:`~crikit.covering.covering.get_composite_cr` used to to map ``arg`` to
    the CR's input space and to map the CR's output to a UFL function space.

    Args:
        form (~ufl.classes.Form): the form
        cr (PointMap): a point map whose input is compatible with ``arg`` and
            whose output is compatible with ``out_terms``.
        arg (~ufl.classes.Expr or tuple[~ufl.classes.Expr]): input expressions to
            the CR
        out_terms (~ufl.classes.Coefficient or tuple[~ufl.classes.Coefficient]):
            terms in the form that will be replaced by the output of the CR
        quad_params (dict, optional): parameters for the quadrature space
        force_explicit (bool, optional): pass ``True`` to force
            ``get_composite_cr`` to be called.
        return_all (bool, optional): Set to ``True`` to have the unassemled form
            and composite CR returned.

        **kwargs: passed through to the ``assemble`` function of the backend

    Returns:
        float or ~ufl.classes.Coefficient: the output of ``pyadjoint_utils.fenics_adjoint.assemble``

        If ``return_all`` is true, additionally returns:

            * :class:`~ufl.classes.Form`: the form with the output of the CR inserted
            * :class:`~crikit.cr.types.PointMap`: the output of :func:`~crikit.covering.covering.get_composite_cr`

    """
    a, form, ufl_cr = _assemble_with_cr(
        form, cr, arg, out_terms, quad_params, force_explicit, **kwargs
    )

    if return_all:
        return a, form, ufl_cr
    return a


def get_ufl_composite_cr(form, cr, arg_terms, out_terms, quad_params=None):
    arg_terms = Enlist(arg_terms)
    out_terms = Enlist(out_terms)
    degree = get_cr_form_degree(form, cr, arg_terms, out_terms)
    quad_params = get_quadrature_params(quad_params, degree)

    # This assumes the form only has one domain, which is also an assumption
    # dolfin makes, so it should be good.
    domain = form.ufl_domain()

    # Create quadrature spaces for output.
    quad_spaces, quad_params = make_quadrature_spaces(
        tuple(UFLExprSpace(o, ufl_domains=(domain,)) for o in out_terms),
        quad_params=quad_params,
        domain=domain,
    )

    # Build a composite CR to work with arg_terms as input and out_funcs as output.
    input_space = arg_terms.delist(
        DirectSum(*tuple(UFLExprSpace(a, ufl_domains=(domain,)) for a in arg_terms))
    )
    output_space = out_terms.delist(
        DirectSum(*tuple(UFLExprSpace(o, ufl_domains=(domain,)) for o in out_terms))
    )
    # output_space = out_terms.delist(DirectSum(tuple(UFLFunctionSpace(Q) for Q in quad_spaces)))

    composite_cr = get_composite_cr(
        input_space, cr, output_space, domain=domain, quad_params=quad_params
    )

    # Add the quadrature info to the form by updating the metadata of each integral.
    new_metadata = [ig.metadata().copy() for ig in form.integrals()]
    for m in new_metadata:
        m.update(quad_params)
    new_integrals = [
        ig.reconstruct(metadata=m) for ig, m in zip(form.integrals(), new_metadata)
    ]
    new_form = Form(new_integrals)

    return new_form, composite_cr, quad_params


def get_cr_form_degree(form, cr, arg_terms, out_terms):
    # Get degree of all arguments to the CR.
    arg_degrees = tuple(est_degree(a) for a in arg_terms)
    max_arg_degree = max(arg_degrees)
    form_degree = est_degree(form, default_degree=max_arg_degree)

    # Get the degrees of the outputs of the CR.
    cr_degrees = cr.est_degree(*arg_degrees)
    if cr_degrees is not None:
        cr_degrees = Enlist(cr_degrees)
        assert len(cr_degrees) == len(out_terms)

        # Get the degree of the form by telling UFL the degree of each output of the CR.
        cr_degree_map = dict(
            (coeff, degree) for coeff, degree in zip(out_terms, cr_degrees)
        )
        d = est_degree(
            form, default_degree=max_arg_degree, coefficient_replace_map=cr_degree_map
        )
        form_degree = max(form_degree, d)
    degree = max(max_arg_degree, form_degree)
    return degree


class AssembleWithCRBlock(TapeBlock):
    """This block represents both an AssemblyBlock (for the assemble call) and a
    TapeBlock (for the CR call).

    Almost all calls are passed through to the original tape, which consists of
    calling a CR and running assemble(). This block optimizes the tlm matrix
    computation by avoiding the Covering projection calls and inserting the CR's
    Jacobian directly into the form for assemble().

    Steps:
        1. Get CR Jacobian.
        2. Insert it into form by replacing out_terms with Jacobian contracted with arg_terms.
        3. Replace coefficients in arg_terms with the appropriate UFL arguments.
    """

    pop_kwargs_keys = ["name", "tlm_mat_skip_covering"]

    def __init__(self, tape, form, cr, arg_terms, out_terms, **kwargs):
        super().__init__(tape)
        self._form = form
        self._cr = cr
        self._arg_terms = Enlist(arg_terms)
        self._out_terms = Enlist(out_terms)

        # There are three tapes to keep track of.
        # 1. self.tape: this is the tape that tracks everything done in this block.
        # 2. self.cr_tape_full: this is the tape that records the CR call, including the Covering stuff.
        # 3. self.cr_tape_inner: this is the tape that records the CR call, not including the Covering stuff.
        self.explicit = kwargs.pop("explicit")
        if self.explicit:
            self.cr_tape_full = kwargs.pop("cr_tape_full")
            self.cr_tape_inner = kwargs.pop("cr_tape_inner")
            self.quad_params = kwargs.pop("quad_params")

            self.inner_inputs = kwargs.pop("inner_inputs")
            self.inner_outputs = kwargs.pop("inner_outputs")
            self.cr_outputs = kwargs.pop("cr_outputs")

            self.tlm_mat_skip_covering = kwargs.pop("tlm_mat_skip_covering", None)
            if self.tlm_mat_skip_covering is None:
                self.tlm_mat_skip_covering = True
        else:
            self.tlm_mat_skip_covering = False

        self.name = kwargs.pop("name", None)
        if self.name is None:
            self.name = "AssembleWithCRBlock"

        # This kwarg will only mess things up.
        kwargs.pop("tensor", None)
        self._assemble_kwargs = kwargs

    def _create_expressions_with_tape_values(self):
        """Replaces original coefficient values with checkpointed values,"""
        replaced_coeffs = {}
        for block_variable in self.get_dependencies():
            coeff = block_variable.output
            c_rep = block_variable.saved_output
            if isinstance(coeff, Expr):
                replaced_coeffs[coeff] = c_rep

        for coeff, out in zip(self._out_terms, self.cr_outputs):
            replaced_coeffs[coeff] = out.block_variable.saved_output

        form = replace(self._form, replaced_coeffs)
        cr_outputs = [r_orig.block_variable.saved_output for r_orig in self.cr_outputs]
        arg_terms = [replace(q, replaced_coeffs) for q in self._arg_terms]
        return form, cr_outputs, arg_terms

    def prepare_evaluate_tlm_matrix(self, inputs, tlm_inputs, relevant_outputs):
        if not self.tlm_mat_skip_covering:
            return super().prepare_evaluate_tlm_matrix(
                inputs, tlm_inputs, relevant_outputs
            )

    def _evaluate_cr_tlm_matrix(self, inputs, relevant_cr_inputs, relevant_cr_outputs):
        """Evaluates the Jacobian of the relevant_outputs for just the CR (no Covering stuff)."""

        # Find the relevant nodes on the tape.
        relevant_cr_input_values = [self.inner_inputs[i] for i in relevant_cr_inputs]
        relevant_cr_input_block_variables = [
            o.block_variable for o in relevant_cr_input_values
        ]
        relevant_cr_output_block_variables = [
            self.cr_outputs[i].block_variable for i in relevant_cr_outputs
        ]

        nodes, blocks = self.tape.find_relevant_nodes(
            relevant_cr_input_block_variables, relevant_cr_output_block_variables
        )
        nodes |= set(relevant_cr_input_block_variables) | set(
            relevant_cr_output_block_variables
        )
        nodes, blocks = self.cr_tape_full.find_relevant_nodes(nodes, nodes)

        # Run inner CR with identity inputs.
        identities = make_jacobian_identities(len(relevant_cr_inputs))
        for bv, identity in zip(relevant_cr_input_block_variables, identities):
            bv.tlm_matrix = identity
        self.cr_tape_inner.evaluate_tlm_matrix(
            inputs=nodes, outputs=nodes, markings=True
        )

        # Extract Jacobian of inner CR, and propagate it to the outer outputs.
        jacobian = []
        for cov_in, cov_out in zip(self.inner_outputs, self.cr_outputs):
            cov_out.block_variable.add_tlm_matrix(cov_in.block_variable.tlm_matrix)
            jacobian.append(cov_in.block_variable.tlm_matrix)

        return jacobian

    def evaluate_tlm_matrix_component(
        self, inputs, tlm_inputs, block_variable, idx, prepared=None
    ):
        """Evaluates the Jacobian for Pyadjoint.

        Let c be the input variables. We want to calculate dF/dc, which is the
        Jacobian of the form F. Then we can assemble that to get the
        actual desired Jacobian.

        Let r = r(q) be the outputs of the CR and q = q(c) be its inputs. The
        Jacobian dr/dq can be computed separately on its own tape (self.cr_tape_inner)
        in self._evaluate_cr_tlm_matrix.

        The full Jacobian dF/dc = partialF/partialc +  sum_q sum_r (partialF/partialr * dr/dq) * partialq/partialc.
        The partial derivatives can be taken with UFL.

        The return value is a list of Jacobians in the form dF/dc = [dF/dc_1, dF/dc_2, ..., dF/dc_m], where m is
        the number of inputs.
        """
        if not self.tlm_mat_skip_covering:
            return super().evaluate_tlm_matrix_component(
                inputs, tlm_inputs, block_variable, idx, prepared
            )

        F_form, cr_outputs, arg_terms = self._create_expressions_with_tape_values()

        # See which CR outputs are required for the Jacobian.
        relevant_cr_outputs = []
        for i, r in enumerate(cr_outputs):
            if r in F_form.coefficients():
                relevant_cr_outputs.append(i)

        # See which CR inputs are required for the Jacobian.
        relevant_cr_inputs = []
        for i, q in enumerate(arg_terms):
            q_coeffs = ufl.algorithms.analysis.extract_coefficients(q)
            for c_rep, c_jac in zip(inputs, tlm_inputs):
                if (
                    c_jac is not None
                    and isinstance(c_rep, ufl.Coefficient)
                    and c_rep in q_coeffs
                ):
                    relevant_cr_inputs.append(i)
                    break
        drdq_arrays_relevant = self._evaluate_cr_tlm_matrix(
            inputs, relevant_cr_inputs, relevant_cr_outputs
        )

        # Convert the drdq arrays into tensor functions.
        drdq_funcs_relevant = []
        assert len(relevant_cr_outputs) == len(
            drdq_arrays_relevant
        ), f"{len(relevant_cr_outputs)} != {len(drdq_arrays_relevant)}"
        for r_idx, drdq_array_r in zip(relevant_cr_outputs, drdq_arrays_relevant):
            r = cr_outputs[r_idx]
            assert len(relevant_cr_inputs) == len(
                drdq_array_r
            ), f"{len(relevant_cr_inputs)} != {len(drdq_array_r)}"
            drdq_func = []
            for q_idx, drdq_array in zip(relevant_cr_inputs, drdq_array_r):
                if drdq_array is None:
                    drdq_func.append(None)
                    continue
                q = arg_terms[q_idx]
                r_rank, q_rank = len(r.ufl_shape), len(q.ufl_shape)

                # Stick the Jacobian drdq_array into a TensorFunction of the right shape.
                if hasattr(drdq_array, "shape"):
                    if len(drdq_array.shape) > r_rank + q_rank + 1:
                        # Handle the case where the array is the full Jacobian instead of the pointwise-computed Jacobian.
                        drdq_array = np.sum(drdq_array, axis=r_rank + 1)
                    tlm_shape = drdq_array.shape[1:]
                    data = drdq_array.flatten()
                else:
                    # Handle the case where the Jacobian was stored as a Function.
                    tlm_shape = drdq_array.tlm_shape
                    data = drdq_array.vector()[:]

                # Remove 1's from tlm_shape or else the derivative will get mad for shapes not matching.
                tlm_shape = tuple(filter(lambda s: s != 1, tlm_shape))

                T = make_quadrature_space(
                    tlm_shape, self.quad_params, domain=self._form.ufl_domain()
                )

                drdq = backend.Function(T)
                drdq.vector()[:] = data

                drdq_func.append(drdq)
            drdq_funcs_relevant.append(drdq_func)

        # Contract drdq_funcs_relevant with appropriate UFL Jacobians to get desired Jacobian.
        dFdc_all = []
        assert len(inputs) == len(tlm_inputs)
        for c_rep, c_jac in zip(inputs, tlm_inputs):
            if c_jac is None:
                dFdc_all.append(None)
                continue

            c_hat = backend.TrialFunction(c_rep.function_space())

            # First get partial derivative of this coefficient.
            dFdc = derivative(F_form, c_rep, c_hat)

            # Then get derivative contributions from the CRs.
            for r_idx, drdq_r in zip(relevant_cr_outputs, drdq_funcs_relevant):
                r = cr_outputs[r_idx]
                r_rank = len(r.ufl_shape)
                for q_idx, drdq in zip(relevant_cr_inputs, drdq_r):
                    if drdq is None:
                        continue
                    q = arg_terms[q_idx]
                    q_rank = len(q.ufl_shape)

                    # Contract just over the q axes.
                    q_axes = list(range(q_rank))
                    drdq_axes = [a + r_rank for a in q_axes]

                    # Note: this derivative has to be expanded in order for the assembly to not throw an error.
                    dqdc = expand_derivatives(derivative(q, c_rep, c_hat))
                    if q_rank == 0:
                        drdc = drdq * dqdc
                    else:
                        drdc = contraction(drdq, drdq_axes, dqdc, q_axes)
                    dFdc += derivative(F_form, r, drdc)

            J = backend.assemble(
                dFdc, form_compiler_parameters=self.quad_params, **self._assemble_kwargs
            )
            dFdc_all.append(J)

        # Contract dFdc_all with the tlm_inputs to get dFdx_all.
        dcdx_all = tlm_inputs
        dFdx_all = None
        for i, (dFdc, dcdx) in enumerate(zip(dFdc_all, dcdx_all)):
            if dcdx is None:
                continue
            if dFdx_all is None:
                dFdx_all = [None] * len(dcdx)

            for j, dcdx_j in enumerate(dcdx):
                # Add dFdc @ dc_dx_j to dFdx_all[j].
                if isinstance(dcdx_j, JacobianIdentity):
                    dot = dFdc
                else:
                    raise ValueError("Cannot handle non-identity inputs")
                if dFdx_all[j] is None:
                    dFdx_all[j] = dot
                else:
                    dFdx_all[j] += dot

        return dFdx_all
