from .equation_solver import ReducedEquationSolver

from pyadjoint.tape import (
    get_working_tape,
    set_working_tape,
    stop_annotating,
    no_annotations,
    annotate_tape,
)
from pyadjoint.block import Block
from pyadjoint.overloaded_type import create_overloaded_object, OverloadedType
from pyadjoint.enlisting import Enlist
from pyadjoint_utils import *

from petsc4py import PETSc
import numpy as np


def _get_enum_lookup(enum, lookup=None):
    lookup = lookup if lookup is not None else {}
    names = (name for name in dir(enum) if not name.startswith("_"))
    for name in names:
        val = getattr(enum, name)
        lookup[val] = name
    return lookup


# Build lookup tables for printing out the converged reasons.
_defaults = {
    -3: "DIVERGED_LINEAR_SOLVE",
}
snes_converged_reason_lookup = _get_enum_lookup(PETSc.SNES.ConvergedReason, _defaults)


_defaults = {
    -11: "DIVERGED_PC_FAILED",
    -3: "DIVERGED_ITS",
}
ksp_converged_reason_lookup = _get_enum_lookup(PETSc.KSP.ConvergedReason, _defaults)


class SNESSolver(ReducedEquationSolver):
    def __init__(self, eq, parameters=None):
        ReducedEquationSolver.__init__(self, eq, parameters)

        self.rf_np = ReducedFunctionNumPy(self.eq.reduced_function)

        param_copy = self.parameters.copy()

        self.jmat_type = param_copy.pop("jmat_type", "assembled")
        self.pmat_type = param_copy.pop("pmat_type", "J")
        self.adj_jmat_type = param_copy.pop("adj_jmat_type", self.jmat_type)
        self.adj_pmat_type = param_copy.pop("adj_pmat_type", "J")
        self.assembled_force_dense = param_copy.pop("assembled_force_dense", True)

        if self.jmat_type not in ("action", "assembled"):
            raise ValueError("Invalid jmat_type: %s" % self.jmat_type)
        if self.pmat_type not in ("J", "assembled"):
            raise ValueError("Invalid pmat_type: %s" % self.pmat_type)

        if self.adj_jmat_type not in ("action", "assembled"):
            raise ValueError("Invalid adj_jmat_type: %s" % self.adj_jmat_type)
        if self.adj_pmat_type not in ("J", "assembled"):
            raise ValueError("Invalid adj_pmat_type: %s" % self.adj_pmat_type)

        if len(param_copy) > 0:
            import warnings

            warnings.warn(
                "Extra parameters given to SNESSolver: " + ", ".join(parameters.keys()),
                stacklevel=2,
            )

    def solve(self, solution_controls, **kwargs):
        annotate = annotate_tape(kwargs)
        solution_controls = Enlist(solution_controls)

        if annotate:
            tape = get_working_tape()
            if tape == self.eq.reduced_function.tape:
                raise ValueError("reduced_function must be recorded on a separate tape")

            b_kwargs = SNESSolveBlock.pop_kwargs(kwargs)
            b_kwargs.update(kwargs)
            block = SNESSolveBlock(self, solution_controls, **b_kwargs)

        # Compute solution.
        solution = self.backend_solve(solution_controls, **kwargs)

        for i, obj in enumerate(solution):
            solution[i] = create_overloaded_object(obj)

        if annotate:
            for obj in solution:
                block.add_output(obj.create_block_variable())
            tape.add_block(block)

        return solution_controls.delist(solution)

    @no_annotations
    def backend_solve(self, solution_controls, **kwargs):
        self.snes_solve(solution_controls, **kwargs)
        return [p.data() for p in self.eq.reduced_function.controls]

    class SNESInterface(object):
        def __init__(self, rf_np, bc, h_bc, dense=True, disp=True, cback=None):
            self.rf_np = rf_np
            self.bc = bc
            self.h_bc = h_bc
            self.dense = dense
            self.disp = disp
            self.cback = cback
            self.i = 0
            self.mults = 0

        def formFunction(self, snes, X, F):
            # Apply boundary conditions.
            X_np = X[:]

            X_rf = self.bc(X_np, return_numpy=False)

            if self.cback is not None:
                self.cback(X_rf)

            X_bc_np = self.rf_np.get_outputs_array(Enlist(X_rf))
            res_np = X_np - X_bc_np

            # Evaluate residual.
            res_rf = self.rf_np.rf(X_rf)

            # Apply homogeneous boundary conditions.
            res_np += self.h_bc(res_rf, adjoint=True, input_numpy=False)

            F[:] = res_np
            F.assemble()
            if self.disp:
                print("%2d: ||residual||: % 18.15g" % (self.i, np.linalg.norm(res_np)))
            self.i += 1

        def formJacobian(self, snes, X, J, P):
            P.zeroEntries()
            if self.disp:
                print("%2d: Jacobian" % (self.i))
            res_np = self.rf_np(X[:])
            J_dolfin = self.rf_np.jac_matrix()
            J_dolfin = self.bc(J_dolfin, False, False)
            if self.disp:
                J_np = J_dolfin.array()
                s = np.linalg.svd(J_np, full_matrices=False, compute_uv=False)
                print("%2d: svd: " % (self.i), s)

            if self.dense:
                J[:, :] = J_dolfin.array()
            else:
                J_petsc = J_dolfin.instance().mat()
                J_petsc.copy(J)
            J.assemble()

        def formPreconditioner(self, snes, X, J, P):
            if self.disp:
                print("%2d: Preconditioner" % (self.i), J, P)
            res_np = self.rf_np(X[:])
            J_dolfin = self.rf_np.jac_matrix()
            J_dolfin = self.bc(J_dolfin, False, False)
            if self.disp:
                J_np = J_dolfin.array()
                s = np.linalg.svd(J_np, full_matrices=False, compute_uv=False)
                print("%2d: svd: " % (self.i), s)

            if self.dense:
                P[:, :] = J_dolfin.array()
            else:
                J_petsc = J_dolfin.instance().mat()
                J_petsc.copy(P)
            P.assemble()

        def dummyJacobian(self, snes, X, J, P):
            """Uses X to set the values on the tape so that the correct Jacobian is generated."""
            if self.disp:
                print("Finished Jacobian mults: %d/%d" % (self.mults, X.size))
                print("%2d: dummy Jacobian" % self.i)
            m = self.rf_np(X[:])
            self.mults = 0

        def mult(self, mat, dx_vec, y):
            self.mults += 1

            # Apply homogeneous boundary conditions.
            dx_rf = self.h_bc(dx_vec[:], return_numpy=False)

            y_rf = self.rf_np.rf.jac_action(dx_rf)

            # Apply homogeneous boundary conditions.
            y_np = self.h_bc(y_rf, input_numpy=False)

            y.setArray(y_np)

        def multTranspose(self, mat, dx_vec, y):
            self.mults += 1

            # Apply homogeneous boundary conditions.
            dx_rf = self.h_bc(dx_vec[:], return_numpy=False)

            y_rf = self.rf_np.rf.adj_jac_action(dx_rf)

            # Apply homogeneous boundary conditions.
            y_np = self.h_bc(y_rf, input_numpy=False)

            y.setArray(y_np)

    def bc(self, x, input_numpy=True, return_numpy=True):
        if input_numpy:
            x_rf = self.rf_np.get_rf_input(x)
            x_rf = self.rf_np.controls.delist(x_rf)
        else:
            x_rf = x

        for bc in self.eq.bcs:
            x_rf = bc(x_rf)

        if return_numpy:
            x_np = self.rf_np.get_outputs_array(Enlist(x_rf))
            return x_np
        return x_rf

    def h_bc(self, x, adjoint=False, input_numpy=True, return_numpy=True):
        if input_numpy:
            if adjoint:
                x_rf = self.rf_np.get_rf_adj_input(x)
                x_rf = self.rf_np.outputs.delist(x_rf)
            else:
                x_rf = self.rf_np.get_rf_input(x)
                x_rf = self.rf_np.controls.delist(x_rf)
        else:
            x_rf = x

        # This assumes that the h_bc works on both the rf's inputs and its outputs.
        for bc in self.eq.h_bcs:
            x_rf = bc(x_rf)

        if return_numpy:
            if adjoint:
                x_np = self.rf_np.get_global(x_rf)
            else:
                x_np = self.rf_np.get_outputs_array(x_rf)
            return x_np
        return x_rf

    def setup_snes(
        self,
        m_global,
        disp=False,
        ksp_type="gmres",
        pc_type="none",
        rtol=None,
        atol=None,
        stol=None,
        max_it=None,
        cback=None,
    ):

        snes_interface = self.SNESInterface(
            self.rf_np,
            self.bc,
            self.h_bc,
            dense=self.assembled_force_dense,
            disp=disp,
            cback=cback,
        )

        n = m_global.size

        snes = PETSc.SNES().create()

        if self.jmat_type == "assembled":
            J_dolfin = self.rf_np.jac_matrix()
            if self.assembled_force_dense:
                J = PETSc.Mat()
                J.createDense(n)
                J.setUp()
            else:
                J = J_dolfin.instance().mat()
                J_dolfin = self.bc(J_dolfin, False, False)
            snes.setJacobian(snes_interface.formJacobian, J)
        elif self.jmat_type == "action":
            J = PETSc.Mat()
            J.createPython(n, snes_interface)
            J.setUp()
            if self.pmat_type == "assembled":
                P = PETSc.Mat()
                P.createDense(n)
                P.setUp()
                raise ValueError(
                    'pmat_type "assembled" cannot be used with jmat_type "action" yet'
                )
                # snes.setJacobian(snes_interface.formPreconditioner, J=J, P=P)
            elif self.pmat_type == "J":
                P = J
            else:
                raise ValueError("Invalid pmat_type: %s" % self.pmat_type)
            snes.setJacobian(snes_interface.dummyJacobian, J, P)
        else:
            raise ValueError("Invalid jmat_type: %s" % self.jmat_type)

        X, F = J.createVecs()
        snes.setFunction(snes_interface.formFunction, F)
        snes.setTolerances(rtol=rtol, atol=atol, stol=stol, max_it=max_it)
        self._tolerances = {"rtol": rtol, "atol": atol, "stol": stol, "max_it": max_it}
        self._ksp_type = ksp_type
        ksp = snes.getKSP()
        ksp.setType(ksp_type)
        self._pc_type = pc_type
        pc = ksp.getPC()
        pc.setType(pc_type)
        snes.setFromOptions()

        return snes, X, F, J

    @no_annotations
    def snes_solve(self, solution_controls, **kwargs):
        disp = kwargs.get("disp", False)

        m_global = self.rf_np.get_controls(solution_controls)
        # m_global = self.rf_np.obj_to_array([p.tape_value() for p in solution_controls])

        snes, X, F, J = self.setup_snes(m_global, **kwargs)

        X[:] = self.bc(m_global)

        snes.solve(None, X)

        reason = snes.getConvergedReason()
        if reason < 0:
            # Hack to get an optimization line search to maybe keep going.
            X[:] = np.full_like(X[:], np.inf)

        reasonMessage = snes_converged_reason_lookup.get(
            reason, "UNKNOWN (%s)" % reason
        )

        if disp or reason < 0:
            if reason < 0:
                print("SNES solver failed with reason %s" % reasonMessage)
            else:
                print("SNES Converged reason:", reasonMessage)
            print("SNES Num iterations:", snes.getIterationNumber())
            if reason < 0 and reasonMessage == "DIVERGED_LINEAR_SOLVE":
                ksp = snes.getKSP()
                reason = ksp.getConvergedReason()
                reasonMessage = ksp_converged_reason_lookup.get(
                    reason, "UNKNOWN (%s)" % reason
                )

                if disp or reason < 0:
                    if reason < 0:
                        print("  KSP solver failed with reason %s" % reasonMessage)
                    else:
                        print("  KSP Converged reason:", reasonMessage)
                    print("  KSP Num iterations:", ksp.getIterationNumber())
            print()
        self.rf_np.set_controls(self.bc(X[:]))

    class AdjJContext(object):
        def __init__(self, rf_np, bc):
            self.rf_np = rf_np
            self.bc = bc

        def mult(self, mat, dx_vec, y):
            dx_rf = self.bc(dx_vec[:], return_numpy=False)
            y_rf = self.rf_np.rf.adj_jac_action(dx_rf)
            y_np = self.bc(y_rf, input_numpy=False)
            y.setArray(y_np)

    @no_annotations
    def _adjoint_ksp_solve(self, adj_inputs, disp=False):
        m_global = self.rf_np.get_outputs_array(adj_inputs)
        n = m_global.size

        # Set up solver.
        ksp = PETSc.KSP().create()
        ksp.setOptionsPrefix("adj_")

        pc = ksp.getPC()
        ksp.setType(self._ksp_type)
        pc.setType(self._pc_type)
        ksp.setFromOptions()

        if self.adj_jmat_type == "assembled":
            J_dolfin = self.rf_np.jac_matrix()

            # Transpose petsc4py Mat local-to-global mapping.
            # Note: this won't work for complex values and maybe not for multiple processes.
            J = J_dolfin.instance().mat()
            lgmap = J.getLGMap()
            J.transpose()
            J.setLGMap(lgmap[1], lgmap[0])
            J_dolfin = self.bc(J_dolfin, False, False)

            if self.assembled_force_dense:
                if disp:
                    J_np = J_dolfin.array()
                    s = np.linalg.svd(J_np, full_matrices=False, compute_uv=False)
                    print("adj: svd: ", s)
                J = PETSc.Mat()
                J.createDense(n)
                J.setUp()
                J[:, :] = J_dolfin.array().conj()
                J.assemble()

            if disp:
                J_np = J_dolfin.array()
                s = np.linalg.svd(J_np, full_matrices=False, compute_uv=False)
                print("adj: svd: ", s)
            ksp.setOperators(J)
        elif self.adj_jmat_type == "action":
            ksp_interface = self.AdjJContext(self.rf_np, self.h_bc)
            J = PETSc.Mat()
            J.createPython(n, ksp_interface)
            J.setUp()
            if self.adj_pmat_type == "assembled":
                P = PETSc.Mat()
                P.createDense(n)
                P.setUp()
                raise ValueError(
                    'adj_pmat_type "assembled" cannot be used with adj_jmat_type "action" yet'
                )
            elif self.adj_pmat_type == "J":
                P = J
            else:
                raise ValueError("Invalid adj_pmat_type: %s" % self.adj_pmat_type)
            ksp.setOperators(J, P)
        else:
            raise ValueError("Invalid adj_jmat_type: %s" % self.adj_jmat_type)

        # Set up the system's vectors.
        X, F = J.createVecs()
        X.set(0)
        F[:] = self.h_bc(m_global[:])

        # Solve.
        ksp.solve(F, X)
        reason = ksp.getConvergedReason()
        reasonMessage = ksp_converged_reason_lookup.get(reason, "UNKNOWN (%s)" % reason)

        if disp or reason < 0:
            if reason < 0:
                print("KSP solver failed with reason %s" % reasonMessage)
            else:
                print("KSP Converged reason:", reasonMessage)
            print("KSP Num iterations:", ksp.getIterationNumber())
            print()

        # Convert X to list of controls
        adj_sol = self.rf_np.get_rf_input(X[:])
        return adj_sol


class SNESSolveBlock(Block):

    pop_kwargs_keys = ["adj_cb"]

    def __init__(self, solver, solution_controls, **kwargs):
        super(SNESSolveBlock, self).__init__()
        self.adj_cb = kwargs.pop("adj_cb", None)

        self.solver = solver
        self.rf = self.solver.eq.reduced_function
        self.solution_controls = solution_controls
        self.forward_kwargs = kwargs

        # The dependencies consist of every block variable that contributes to the rf's output but
        # is not dependendent on the initial guess.
        with self.rf.tape.marked_nodes(self.solution_controls):
            dependencies, blocks = self.rf.tape.find_relevant_dependencies(
                self.rf.outputs
            )
            for dep in dependencies:
                if not dep.marked_in_path:
                    self.add_dependency(dep.output)

        # It might be nice to recompute the solution based on the initial guess, too.
        self.solution_block_variables = []
        for c in self.solution_controls:
            self.add_dependency(c.control)
            self.solution_block_variables.append(c.block_variable)

    def __str__(self):
        return "SNESSolveBlock"

    def reset_variables(self, types=None):
        super().reset_variables(types)
        self.rf.tape.reset_variables(types)

    def prepare_recompute_component(self, inputs, relevant_outputs):
        solution = self.solver.backend_solve(
            self.solution_controls, **self.forward_kwargs
        )
        return solution

    def recompute_component(self, inputs, block_variable, idx, prepared):
        solution = prepared
        return solution[idx]

    def prepare_evaluate_adj(self, inputs, adj_inputs, relevant_dependencies):
        # Important: the rf tape needs to be reset because the _adjoint_ksp_solve needs to use the adj_values.
        # But we don't want to lose the adjoint values that have already been computed on the working tape.
        # So this saves the current adjoint values before doing the adjoint solve and then reinstates those values.
        tape = self.rf.tape
        with tape.save_adj_values():
            adj_sol = self.solver._adjoint_ksp_solve(adj_inputs)

        if self.adj_cb is not None:
            self.adj_cb(adj_sol)

        relevant_block_variables = [bv for i, bv in relevant_dependencies]

        # Pass the adj_sol to the rf tape to calculate the adjoint of all the controls.
        # FIXME: A problem here is that not all block variables use the same
        #        type in their adj_value as in their normal overloaded type.
        #        E.g., Function types use dolfin vectors to pass the adj_value.
        with tape.save_adj_values():
            for i, bv in enumerate(self.rf.outputs):
                bv.adj_value = create_overloaded_object(adj_sol[i])._ad_mul(-1)

            with stop_annotating():
                with tape.marked_nodes(relevant_block_variables):
                    tape.evaluate_adj(markings=True)

            # Extract adjoint values from controls.
            adj_values = [bv.adj_value for bv in self.get_dependencies()]
        return adj_values

    def evaluate_adj_component(
        self, inputs, adj_inputs, block_variable, idx, prepared=None
    ):
        return prepared[idx]

    def tf_add_extra_to_graph(self, tf_tensors):
        import tensorflow as tf

        self.rf.tape._tf_tensors.update(tf_tensors)
        # Add rf tape as a sub-block.
        with tf.name_scope("Residual_tape"):
            self.rf.tape._tf_add_blocks()

        tf_tensors.update(self.rf.tape._tf_tensors)
