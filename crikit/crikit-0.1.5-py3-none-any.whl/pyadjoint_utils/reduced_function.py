from pyadjoint.enlisting import Enlist
from pyadjoint.tape import stop_annotating, get_working_tape

from .drivers import (
    compute_gradient,
    compute_jacobian_action,
    compute_jacobian_matrix,
    compute_hessian_action,
)

# This is copied and extended from work by Sebastian Mitusch in pyadjoint
# [https://bitbucket.org/dolfin-adjoint/pyadjoint/commits/4b67f3e07579501ab95b1fad143d98253a15f7ae?at=reduced-function]


class ReducedFunction(object):
    def __init__(
        self,
        outputs,
        controls,
        tape=None,
        eval_cb_pre=None,
        eval_cb_post=None,
        jac_action_cb_pre=None,
        jac_action_cb_post=None,
        adj_jac_action_cb_pre=None,
        adj_jac_action_cb_post=None,
        hess_action_cb_pre=None,
        hess_action_cb_post=None,
    ):
        self.output_vals = Enlist(outputs)
        self.outputs = Enlist([out.block_variable for out in self.output_vals])
        self.outputs.listed = self.output_vals.listed

        self.controls = Enlist(controls)
        self.tape = get_working_tape() if tape is None else tape

        nothing = lambda *args: None
        self.eval_cb_pre = nothing if eval_cb_pre is None else eval_cb_pre
        self.eval_cb_post = nothing if eval_cb_post is None else eval_cb_post
        self.jac_action_cb_pre = (
            nothing if jac_action_cb_pre is None else jac_action_cb_pre
        )
        self.jac_action_cb_post = (
            nothing if jac_action_cb_post is None else jac_action_cb_post
        )
        self.adj_jac_action_cb_pre = (
            nothing if adj_jac_action_cb_pre is None else adj_jac_action_cb_pre
        )
        self.adj_jac_action_cb_post = (
            nothing if adj_jac_action_cb_post is None else adj_jac_action_cb_post
        )
        self.hess_action_cb_pre = (
            nothing if hess_action_cb_pre is None else hess_action_cb_pre
        )
        self.hess_action_cb_post = (
            nothing if hess_action_cb_post is None else hess_action_cb_post
        )

    def jac_action(self, inputs, options=None):
        inputs = Enlist(inputs)
        if len(inputs) != len(self.controls):
            raise TypeError(
                "The length of inputs must match the length of function controls."
            )

        values = [c.data() for c in self.controls]
        self.jac_action_cb_pre(
            self.controls.delist(values), self.controls.delist(inputs)
        )

        derivatives = compute_jacobian_action(
            self.output_vals, self.controls, inputs, options=options, tape=self.tape
        )
        # Call callback
        self.jac_action_cb_post(
            self.outputs.delist([bv.saved_output for bv in self.outputs]),
            self.outputs.delist(derivatives),
            self.controls.delist(values),
        )

        return self.outputs.delist(derivatives)

    def adj_jac_action(self, inputs, options=None):
        inputs = Enlist(inputs)
        if len(inputs) != len(self.outputs):
            raise TypeError(
                "The length of inputs must match the length of function outputs."
            )

        values = [c.data() for c in self.controls]
        self.adj_jac_action_cb_pre(self.controls.delist(values))

        derivatives = compute_gradient(
            self.output_vals,
            self.controls,
            options=options,
            tape=self.tape,
            adj_value=inputs,
        )

        # Call callback
        self.adj_jac_action_cb_post(
            self.outputs.delist([bv.saved_output for bv in self.outputs]),
            self.controls.delist(derivatives),
            self.controls.delist(values),
        )

        return self.controls.delist(derivatives)

    def jac_matrix(self, m_jac=None):
        if m_jac is not None:
            m_jac = Enlist(m_jac)
            if len(m_jac) != len(self.controls):
                raise TypeError(
                    "The length of m_jac must match the length of function controls."
                )

            for i, jac in enumerate(m_jac):
                m_jac[i] = Enlist(jac)
                if len(m_jac[i]) != len(self.controls):
                    raise TypeError(
                        "The length of each identity must match the length of function controls."
                    )

        jacobian = compute_jacobian_matrix(
            self.output_vals, self.controls, m_jac, tape=self.tape
        )
        for i, jac in enumerate(jacobian):
            if jac is not None:
                jacobian[i] = self.controls.delist(jac)
        jacobian = self.outputs.delist(jacobian)
        return jacobian

    def hess_action(self, m_dot, adj_input, options=None):
        m_dot = Enlist(m_dot)
        if len(m_dot) != len(self.controls):
            raise TypeError(
                "The length of m_dot must match the length of function controls."
            )

        adj_input = Enlist(adj_input)
        if len(adj_input) != len(self.outputs):
            raise TypeError(
                "The length of adj_input must match the length of function outputs."
            )

        values = [c.data() for c in self.controls]
        self.hess_action_cb_pre(self.controls.delist(values))

        derivatives = compute_gradient(
            self.output_vals,
            self.controls,
            options=options,
            tape=self.tape,
            adj_value=adj_input,
        )

        # TODO: there should be a better way of generating hessian_input.
        zero = [0 * v for v in adj_input]
        hessian = compute_hessian_action(
            self.output_vals,
            self.controls,
            m_dot,
            options=options,
            tape=self.tape,
            hessian_value=zero,
        )

        # Call callback
        self.hess_action_cb_post(
            self.outputs.delist([bv.saved_output for bv in self.outputs]),
            self.controls.delist(hessian),
            self.controls.delist(values),
        )

        return self.controls.delist(hessian)

    def __call__(self, inputs):
        inputs = Enlist(inputs)
        if len(inputs) != len(self.controls):
            raise TypeError("The length of inputs must match the length of controls.")

        # Call callback.
        self.eval_cb_pre(self.controls.delist(inputs))

        for i, value in enumerate(inputs):
            self.controls[i].update(value)

        # self.tape.reset_blocks()
        with self.marked_controls():
            with stop_annotating():
                self.tape.recompute()

        output_vals = self.outputs.delist(
            [output.checkpoint for output in self.outputs]
        )

        # Call callback
        self.eval_cb_post(output_vals, self.controls.delist(inputs))

        return output_vals

    def marked_controls(self):
        return marked_controls(self)


class marked_controls(object):
    def __init__(self, rf):
        self.rf = rf

    def __enter__(self):
        for control in self.rf.controls:
            control.mark_as_control()

    def __exit__(self, *args):
        for control in self.rf.controls:
            control.unmark_as_control()
