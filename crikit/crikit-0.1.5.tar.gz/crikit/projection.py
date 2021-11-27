from pyadjoint.tape import get_working_tape, stop_annotating, annotate_tape
from pyadjoint.overloaded_type import create_overloaded_object
from .fe import *
from .fe_adjoint import *

import ufl
from fenics_adjoint.blocks.solving import GenericSolveBlock as SolveBlock

# Copied from fenics/dolfin/python/dolfin/fem/projection.py. Added dx parameter.
def project_backend(
    v,
    V,
    bcs=None,
    mesh=None,
    function=None,
    solver_type="lu",
    preconditioner_type="default",
    form_compiler_parameters=None,
    dx=None,
):
    # Note: I removed the beginning part handling when V is None or V is a MultiMeshFunctionSpace.

    # Ensure we have a mesh and attach to measure
    if mesh is None:
        mesh = V.mesh()

    ######### This is the only part I modified. ##############
    if dx is None:
        dx = ufl.dx(mesh)

        def get_dx(el, dx):
            if el.family() == "Quadrature":
                quad_params = {
                    "quadrature_rule": el.quadrature_scheme(),
                    "quadrature_degree": el.degree(),
                    "representation": "quadrature",
                }
                dx = dx(metadata=quad_params)
            return dx

        dx = get_dx(V.ufl_element(), dx)
        if hasattr(v, "function_space"):
            dx = get_dx(v.function_space().ufl_element(), dx)
    #########################################################

    # Define variational problem for projection
    w = TestFunction(V)
    Pv = TrialFunction(V)
    a = ufl.inner(w, Pv) * dx
    L = ufl.inner(w, v) * dx

    # Assemble linear system
    A, b = assemble_system(
        a, L, bcs=bcs, form_compiler_parameters=form_compiler_parameters
    )

    # Solve linear system for projection
    if function is None:
        function = Function(V)
    cpp.la.solve(A, function.vector(), b, solver_type, preconditioner_type)

    return function


# Directly copied from pyadjoint/fenics_adjoint/projection.py
def project(*args, **kwargs):
    """The project call performs an equation solve, and so it too must be annotated so that the
    adjoint and tangent linear models may be constructed automatically by pyadjoint.

    To disable the annotation of this function, just pass :py:data:`annotate=False`. This is useful in
    cases where the solve is known to be irrelevant or diagnostic for the purposes of the adjoint
    computation (such as projecting fields to other function spaces for the purposes of
    visualisation)."""

    annotate = annotate_tape(kwargs)
    with stop_annotating():
        output = project_backend(*args, **kwargs)
    output = create_overloaded_object(output)

    if annotate:
        bcs = kwargs.pop("bcs", [])
        dx = kwargs.pop("dx", None)
        block = ProjectBlock(args[0], args[1], output, bcs, dx)

        tape = get_working_tape()
        tape.add_block(block)

        block.add_output(output.block_variable)

    return output


# Directly copied from pyadjoint/fenics_adjoint/projection.py
class ProjectBlock(SolveBlock):
    def __init__(self, v, V, output, bcs=[], dx=None, *args, **kwargs):
        if dx is None:
            dx = ufl.dx(V.mesh())

        w = TestFunction(V)
        Pv = TrialFunction(V)
        a = inner(w, Pv) * dx
        L = inner(w, v) * dx

        super(ProjectBlock, self).__init__(a, L, output, bcs, *args, **kwargs)
