from fenics_adjoint import backend, compat
from pyadjoint.enlisting import Enlist


def homogenize_bcs(bcs):
    bcs = Enlist(bcs)
    h_bcs = []
    for bc in bcs:
        if isinstance(bc, backend.DirichletBC):
            bc = compat.create_bc(bc, homogenize=True)
        h_bcs.append(bc)
    return bcs.delist(h_bcs)
