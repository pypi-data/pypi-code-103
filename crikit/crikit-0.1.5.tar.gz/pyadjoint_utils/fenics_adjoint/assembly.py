from ufl import Form
from fenics_adjoint import backend, Function
from fenics_adjoint.assembly import AssembleBlock as AssembleBlockOrig
from pyadjoint.tape import annotate_tape, stop_annotating, get_working_tape
from pyadjoint.overloaded_type import OverloadedType, create_overloaded_object

import backend
from fenics_adjoint.compat import compat

compat = compat(backend)


class OverloadedUFLArgument(object):
    """An overloaded argument whose adjoint values on a tape should be returned as rank-1 Forms"""

    pass


def assemble(*args, **kwargs):
    """Use the assemble syntax of firedrake, where the 'tensor' kwarg can take a Function.
    If that is the case (or if firedrake is the backend and the returned tensor is a Function),
    convert the result to an overloaded function so that an AssembleBlock can be created,
    even if the output is not a scalar."""

    annotate = annotate_tape(kwargs)

    with stop_annotating():
        if "tensor" in kwargs and isinstance(kwargs["tensor"], backend.Function):
            outputfunc = kwargs["tensor"]
            new_kwargs = kwargs.copy()
            new_kwargs["tensor"] = outputfunc.vector()
            backend.assemble(*args, **new_kwargs)
            output = outputfunc
        else:
            output = backend.assemble(*args, **kwargs)

    form = args[0]
    if isinstance(output, float) or isinstance(output, backend.Function):
        output = create_overloaded_object(output)

        if annotate:
            block = AssembleBlock(form)

            tape = get_working_tape()
            tape.add_block(block)

            block.add_output(output.block_variable)
    else:
        # Assembled a matrix
        output.form = form

    return output


class AssembleBlock(AssembleBlockOrig):
    def __init__(self, form):
        super(AssembleBlockOrig, self).__init__(form)
        self.form = form
        if backend.__name__ != "firedrake":
            mesh = self.form.ufl_domain().ufl_cargo()
        else:
            mesh = self.form.ufl_domain()
        self.add_dependency(mesh)
        for c in self.form.coefficients():
            if isinstance(c, OverloadedType):
                self.add_dependency(c, no_duplicates=True)

    def evaluate_adj_component(
        self, inputs, adj_inputs, block_variable, idx, prepared=None
    ):
        """catch when the adj_input is a Function, or when the return value
        should be a Form, otherwise do the default"""

        form = prepared
        adj_input = adj_inputs[0]
        c = block_variable.output
        c_rep = block_variable.saved_output

        args = form.arguments()
        n_args = len(args)
        if isinstance(c, OverloadedUFLArgument):
            if n_args == 0:
                form = adj_input * form
            elif n_args == 1:
                form = form * adj_input
            if isinstance(c, backend.Function):
                V = c.function_space()
            else:
                mesh = compat.extract_mesh_from_form(self.form)
                V = c._ad_function_space(mesh)
            dc = backend.TestFunction(V)
            dform = backend.derivative(form, c_rep, dc)
            return dform

        if n_args == 0:
            return super(AssembleBlock, self).evaluate_adj_component(
                inputs, adj_inputs, block_variable, idx, prepared=form
            )

        # In this case, adj_input may be a vector. It needs to be made into a function to put it into the form.
        if isinstance(adj_input, backend.Function):
            adj_input_func = adj_input
        else:
            # import crikit.utils as utils; utils.debug(locals(), globals())
            adj_input_func = backend.Function(args[0].function_space())
            adj_input_func.vector()[:] = adj_input[:]

        # if the output of the original is an assembled function, then
        # it should have exactly one argument, so we can apply it to adj_input.
        form = form * adj_input_func
        if isinstance(c, compat.ExpressionType):
            # Create a FunctionSpace from self.form and Expression.
            # And then make a TestFunction from this space.
            mesh = self.form.ufl_domain().ufl_cargo()
            V = c._ad_function_space(mesh)
            dc = backend.TestFunction(V)

            dform = backend.derivative(form, c_rep, dc)
            # print(c)
            # import crikit.utils as utils; utils.debug(locals(), globals())
            # output = backend.Function(c.function_space())
            # backend.assemble(dform,tensor=output.vector())
            output = compat.assemble_adjoint_value(dform)
            return [[output, V]]
        elif isinstance(c, compat.MeshType):
            X = backend.SpatialCoordinate(c_rep)
            dform = backend.derivative(form, X)
            output = compat.assemble_adjoint_value(dform)
            return output
        if isinstance(c, backend.Function):
            V = c.function_space()
        else:
            mesh = compat.extract_mesh_from_form(self.form)
            V = c._ad_function_space(mesh)
        dc = backend.TestFunction(V)
        dform = backend.derivative(form, c_rep, dc)
        output = compat.assemble_adjoint_value(dform)
        return output

    def evaluate_tlm_component(
        self, inputs, tlm_inputs, block_variable, idx, prepared=None
    ):
        """catch when the output is a Function, otherwise do the default"""
        output = super(AssembleBlock, self).evaluate_tlm_component(
            inputs, tlm_inputs, block_variable, idx, prepared=prepared
        )
        saved_output = self.get_outputs()[idx].saved_output
        if isinstance(saved_output, backend.Function):
            output = backend.Function(saved_output.function_space(), output)
        return output

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
        form = prepared
        hessian_input = hessian_inputs[0]
        adj_input = adj_inputs[0]

        c1 = block_variable.output
        c1_rep = block_variable.saved_output

        args = form.arguments()
        n_args = len(args)
        if n_args > 0 or isinstance(
            c1, OverloadedUFLArgument
        ):  # or isinstance(adj_input, backend.Function):
            if isinstance(adj_input, backend.Function):
                adj_input_func = adj_input
            else:
                adj_input_func = backend.Function(args[0].function_space())
                adj_input_func.vector()[:] = adj_input[:]

            if isinstance(hessian_input, backend.Function):
                hessian_input_func = hessian_input
            else:
                hessian_input_func = backend.Function(args[0].function_space())
                hessian_input_func.vector()[:] = hessian_input[:]

            if n_args == 0:
                hform = adj_input * form
                aform = hessian_input * form
            else:
                hform = form * hessian_input_func
                aform = form * adj_input_func
            mesh = self.form.ufl_domain().ufl_cargo()
            if isinstance(c1, backend.Function):
                V = c1.function_space()
            else:
                V = c1._ad_function_space(mesh)
            dc = backend.TestFunction(V)
            dform = backend.derivative(hform, c1_rep, dc)
            dforma = backend.derivative(aform, c1_rep, dc)
            for other_idx, bv in relevant_dependencies:
                c2_rep = bv.saved_output
                tlm_input = bv.tlm_value

                if tlm_input is None:
                    continue

                if isinstance(c2_rep, compat.MeshType):
                    X = backend.SpatialCoordinate(c2_rep)
                    ddform = backend.derivative(dforma, X, tlm_input)
                else:
                    ddform = backend.derivative(dforma, c2_rep, tlm_input)
                dform += ddform
            if not isinstance(c1, OverloadedUFLArgument):
                return compat.assemble_adjoint_value(dform)
            return dform

        return super(AssembleBlock, self).evaluate_hessian_component(
            inputs,
            hessian_inputs,
            adj_inputs,
            block_variable,
            idx,
            relevant_dependencies,
            prepared,
        )

    def recompute_component(self, inputs, block_variable, idx, prepared):
        saved_output = self.get_outputs()[idx].saved_output
        if isinstance(saved_output, backend.Function):
            form = prepared
            V = saved_output.function_space()
            output = backend.Function(V)
            backend.assemble(form, tensor=output.vector())
            output = create_overloaded_object(output)
            return output
        else:
            return super(AssembleBlock, self).recompute_component(
                inputs, block_variable, idx, prepared
            )
