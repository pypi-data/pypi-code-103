from pyadjoint import set_working_tape
from pyadjoint_utils import Tape

set_working_tape(Tape())
del Tape
del set_working_tape

from .utils import homogenize_bcs
from .assembly import assemble, AssembleBlock
from .array import function_get_local, function_set_local

from fenics_adjoint import backend, compat

if backend.__name__ == "fenics":
    # Fix for https://bitbucket.org/dolfin-adjoint/pyadjoint/issues/118/fenics-compatassemble_adjoint_value-throws
    def assemble_adjoint_value(*args, **kwargs):
        """Wrapper that assembles a matrix with boundary conditions"""
        bcs = kwargs.pop("bcs", ())
        result = backend.assemble(*args, **kwargs)
        for bc in bcs:
            bc.apply(result)
        return result

    compat.assemble_adjoint_value = assemble_adjoint_value
    del assemble_adjoint_value
