from pyadjoint.tape import (
    get_working_tape,
    stop_annotating,
    annotate_tape,
    no_annotations,
)
from pyadjoint.block import Block
from pyadjoint.overloaded_type import create_overloaded_object

from fenics import *
from fenics_adjoint import *

import numpy as np


def backend_observe_error(u, rhat):
    uhat = u.vector()
    return 0.5 * np.dot(uhat - rhat, uhat - rhat) / len(rhat)


# Note that rhat has to be a constant. If rhat isn't a constant, I'll need to add a
# calculation for its adjoint value, because someone may want its derivative.


def observe_error(func, rhat, **kwargs):
    annotate = annotate_tape(kwargs)

    if annotate:
        tape = get_working_tape()
        block = ObserverErrorBlock(func, rhat, **kwargs)
        tape.add_block(block)

    with stop_annotating():
        output = backend_observe_error(func, rhat, **kwargs)

    output = create_overloaded_object(output)

    if annotate:
        block.add_output(output.create_block_variable())

    return output


class ObserverErrorBlock(Block):
    def __init__(self, func, rhat, **kwargs):
        super(ObserverErrorBlock, self).__init__()
        self.add_dependency(func)
        self.kwargs = kwargs
        self.rhat = rhat.copy()

    def __str__(self):
        return "ObserverErrorBlock"

    def evaluate_adj_component(
        self, inputs, adj_inputs, block_variable, idx, prepared=None
    ):
        adj_input = adj_inputs[0]
        func = block_variable.saved_output
        x = func.vector()

        adj_output = (x - self.rhat) * adj_input / len(self.rhat)

        u = Function(func.function_space())
        u.vector()[:] = adj_output
        return u.vector()

    def recompute(self):
        func = self.get_dependencies()[0].saved_output
        output = backend_observe_error(func, self.rhat, **self.kwargs)
        self.get_outputs()[0].checkpoint = output


if __name__ == "__main__":
    # Set up a space.
    mesh = UnitSquareMesh(10, 10)
    V = FunctionSpace(mesh, "CG", 1)

    # Get a test function.
    f = project(Expression("x[0]*x[1]", degree=1), V)
    fvec = f.vector()

    # Get a test comparison vector.
    r = np.random.uniform(0, 1, size=len(fvec))

    # Get a direction to test.
    h = Function(V)
    hvec = h.vector()
    hvec[:] = 0.1

    # Perform Taylor test.
    J = observe_error(f, r)
    taylor_test(ReducedFunctional(J, Control(f)), f, h)
