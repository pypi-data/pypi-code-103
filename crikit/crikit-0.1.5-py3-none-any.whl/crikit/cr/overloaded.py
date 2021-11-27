from pyadjoint import OverloadedType
from pyadjoint.tape import (
    annotate_tape,
    no_annotations,
    stop_annotating,
    get_working_tape,
)
from pyadjoint.overloaded_type import create_overloaded_object
from pyadjoint.enlisting import Enlist
from pyadjoint_utils import Block


def overload_point_map_call(func):
    assert (
        func.__name__ == "__call__"
    ), "this decorator only works on the __call__ function"

    def decorator(*args, **kwargs):
        annotate = annotate_tape(kwargs)
        if annotate:
            b_kwargs = PointMapBlock.pop_kwargs(kwargs)
            b_kwargs.update(kwargs)

        with stop_annotating():
            output = func(*args, **kwargs)

        output = Enlist(output)
        r = [create_overloaded_object(o) for o in output]

        if annotate:
            block = PointMapBlock(*args, output.delist(r))
            get_working_tape().add_block(block)
        return output.delist(r)

    return decorator


def overloaded_point_map(cls):
    cls.__call__ = overload_point_map_call(cls.__call__)
    return cls


class PointMapBlock(Block):
    def __init__(self, amap, arg, output, **kwargs):
        super(PointMapBlock, self).__init__()
        self._amap = amap
        args = Enlist(arg)
        outputs = Enlist(output)

        is_overloaded = [isinstance(output, OverloadedType) for output in outputs]
        num_overloaded = sum(is_overloaded)
        overloaded_map = [sum(is_overloaded[0:i]) for i in range(num_overloaded)]
        self._out_map = overloaded_map

        is_overloaded = [isinstance(arg, OverloadedType) for arg in args]
        num_overloaded = sum(is_overloaded)
        overloaded_map = [sum(is_overloaded[0:i]) for i in range(num_overloaded)]
        self._arg_map = overloaded_map

        self._ag_outputs = outputs
        for argi in self._arg_map:
            self.add_dependency(args[argi])

        self._args = args
        for outi in self._out_map:
            self.add_output(outputs[outi].block_variable)

    def __repr__(self):
        return f"PointMapBlock({self._amap!r})"

    @no_annotations
    def recompute(self, markings=False):
        outputs = self.get_outputs()

        inputs = [bv.saved_output for bv in self.get_dependencies()]
        relevant_outputs = [
            (i, bv) for i, bv in enumerate(outputs) if bv.marked_in_path or not markings
        ]

        if len(relevant_outputs) <= 0:
            return

        full_arg = sparse_insert(
            self._amap.source, self._args, inputs, self._arg_map, copy=True
        )
        new_outputs = Enlist(self._amap(full_arg))

        for idx, out in relevant_outputs:
            output = new_outputs[self._out_map[idx]]
            out.checkpoint = output

    @no_annotations
    def evaluate_adj(self, markings=False):
        outputs = self.get_outputs()
        adj_inputs = []
        has_input = False
        for output in outputs:
            adj_inputs.append(output.adj_value)
            if output.adj_value is not None:
                has_input = True

        if not has_input:
            return

        deps = self.get_dependencies()
        inputs = [bv.saved_output for bv in deps]
        relevant_dependencies = [
            (i, bv)
            for i, bv in enumerate(deps)
            if (bv.marked_in_path or not markings) and (bv not in outputs)
        ]
        # TODO: Why did I add (bv not in outputs) as a condition here? When would that ever happen, and why?

        if len(relevant_dependencies) <= 0:
            return

        full_arg = sparse_insert(
            self._amap.source, self._args, inputs, self._arg_map, copy=True
        )
        full_adj_vec = sparse_insert(
            self._amap.target, self._ag_outputs, adj_inputs, self._out_map
        )
        adj_outputs = Enlist(self._amap.adjoint(full_arg, full_adj_vec))

        for idx, dep in relevant_dependencies:
            adj_output = adj_outputs[self._arg_map[idx]]
            if adj_output is not None:
                dep.add_adj_output(adj_output)

    @no_annotations
    def evaluate_tlm(self, markings=False):
        deps = self.get_dependencies()
        tlm_inputs = []
        has_input = False
        for dep in deps:
            tlm_inputs.append(dep.tlm_value)
            if dep.tlm_value is not None:
                has_input = True

        if not has_input:
            return

        outputs = self.get_outputs()
        inputs = [bv.saved_output for bv in deps]
        relevant_outputs = [
            (i, bv)
            for i, bv in enumerate(outputs)
            if (bv.marked_in_path or not markings) and (bv not in deps)
        ]

        if len(relevant_outputs) <= 0:
            return

        full_arg = sparse_insert(
            self._amap.source, self._args, inputs, self._arg_map, copy=True
        )
        full_tlm_vec = sparse_insert(
            self._amap.source, self._args, tlm_inputs, self._arg_map
        )
        tlm_outputs = Enlist(self._amap.tlm(full_arg, full_tlm_vec))

        for idx, out in relevant_outputs:
            tlm_output = tlm_outputs[self._out_map[idx]]
            if tlm_output is not None:
                out.add_tlm_output(tlm_output)

    @no_annotations
    def evaluate_hessian(self, markings=False):
        outputs = self.get_outputs()
        hessian_inputs = []
        adj_inputs = []
        has_input = False
        for output in outputs:
            hessian_inputs.append(output.hessian_value)
            adj_inputs.append(output.adj_value)
            if output.hessian_value is not None:
                has_input = True

        if not has_input:
            return

        deps = self.get_dependencies()
        tlm_inputs = []
        for dep in deps:
            tlm_inputs.append(dep.tlm_value)

        inputs = [bv.saved_output for bv in deps]
        relevant_dependencies = [
            (i, bv) for i, bv in enumerate(deps) if bv.marked_in_path or not markings
        ]

        if len(relevant_dependencies) <= 0:
            return

        full_arg = sparse_insert(
            self._amap.source, self._args, inputs, self._arg_map, copy=True
        )
        full_adj_vec = sparse_insert(
            self._amap.target, self._ag_outputs, adj_inputs, self._out_map
        )
        full_hes_vec = sparse_insert(
            self._amap.target, self._ag_outputs, hessian_inputs, self._out_map
        )
        full_tlm_vec = sparse_insert(
            self._amap.source, self._args, tlm_inputs, self._arg_map
        )
        adj_outputs = Enlist(self._amap.adjoint(full_arg, full_hes_vec))
        hes_outputs = Enlist(self._amap.hessian(full_arg, full_adj_vec, full_tlm_vec))
        for i in range(len(adj_outputs)):
            hes_outputs[i] = hes_outputs[i] + adj_outputs[i]

        for idx, dep in relevant_dependencies:
            hessian_output = hes_outputs[self._arg_map[idx]]
            if hessian_output is not None:
                dep.add_hessian_output(hessian_output)

    @no_annotations
    def evaluate_tlm_matrix(self, markings=False):
        deps = self.get_dependencies()
        tlm_inputs = []
        has_input = False
        for dep in deps:
            tlm_inputs.append(dep.tlm_matrix)
            if dep.tlm_matrix is not None:
                has_input = True

        if not has_input:
            return

        outputs = self.get_outputs()
        inputs = [bv.saved_output for bv in deps]
        relevant_outputs = [
            (i, bv)
            for i, bv in enumerate(outputs)
            if (bv.marked_in_path or not markings) and (bv not in deps)
        ]

        if len(relevant_outputs) <= 0:
            return

        full_arg = sparse_insert(
            self._amap.source, self._args, inputs, self._arg_map, copy=True
        )
        full_tlm_vec = sparse_insert(
            self._amap.source, self._args, tlm_inputs, self._arg_map
        )
        full_tlm_vec = tlm_inputs
        tlm_outputs = Enlist(self._amap.tlm_matrix(full_arg, full_tlm_vec))
        # TODO: currently, it is assumed that this map has only one output.

        tlm_outputs = [tlm_outputs]
        for idx, out in relevant_outputs:
            idx_out = self._out_map[idx]
            tlm_matrix = tlm_outputs[idx_out]
            if tlm_matrix is not None:
                out.add_tlm_matrix(tlm_matrix)


def sparse_insert(space, near, sparse_vals, idxmap, copy=False):
    if not copy:
        full_vals = Enlist(space.point(zero=True, near=near.delist(tuple(near))))
    else:
        full_vals = near.copy()
    for i, val in enumerate(sparse_vals):
        if val is not None:
            full_vals[i] = val
    return near.delist(tuple(full_vals))
