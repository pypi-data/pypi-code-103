from pyadjoint import Tape as pyadjoint_tape
from pyadjoint import get_working_tape, set_working_tape, Block

from contextlib import contextmanager


@contextmanager
def push_tape():
    """Creates a new tape in its scope that is a sub-tape of the current working tape"""
    orig_tape = get_working_tape()

    new_tape = Tape()
    set_working_tape(new_tape)
    yield new_tape

    set_working_tape(orig_tape)


def _find_relevant_nodes(tape, controls_or_block_variables):
    # This function is just a stripped down Block.optimize_for_controls
    blocks = tape.get_blocks()
    if len(controls_or_block_variables) > 0 and hasattr(
        next(iter(controls_or_block_variables)), "block_variable"
    ):
        nodes = set([control.block_variable for control in controls_or_block_variables])
    else:
        nodes = set([block_variable for block_variable in controls_or_block_variables])

    for block in blocks:
        depends_on_control = False
        for dep in block.get_dependencies():
            if dep in nodes:
                depends_on_control = True

        if depends_on_control:
            for output in block.get_outputs():
                nodes.add(output)
    return nodes


def _block_get_tf_blocks(block):
    if not hasattr(block, "tf_get_blocks"):
        return block
    tf_blocks = block.tf_get_blocks()
    if isinstance(tf_blocks, Block):
        return tf_blocks

    block, sub_blocks = tf_blocks
    sub_blocks = list(sub_blocks)
    for i, sub_block in enumerate(sub_blocks):
        sub_blocks[i] = _block_get_tf_blocks(sub_block)
    return [block, sub_blocks]


class Tape(pyadjoint_tape):

    __slots__ = ["_tf_output_block_lookup"]

    def __init__(self, *args, **kwargs):
        self._tf_output_block_lookup = {}
        super().__init__(*args, **kwargs)

    def evaluate_adj(self, inputs=None, outputs=None, markings=False):
        nodes, blocks = self.find_relevant_nodes(inputs, outputs)
        for block in reversed(blocks):
            block.evaluate_adj(markings=markings)

    def evaluate_tlm(self, inputs=None, outputs=None, markings=False):
        nodes, blocks = self.find_relevant_nodes(inputs, outputs)
        with self.marked_nodes(nodes):
            for block in blocks:
                block.evaluate_tlm(markings=True)

    def evaluate_tlm_matrix(self, inputs=None, outputs=None, markings=False):
        nodes, blocks = self.find_relevant_nodes(inputs, outputs)
        with self.marked_nodes(nodes, find_outputs=False):
            for block in blocks:
                block.evaluate_tlm_matrix(markings=True)

    def evaluate_hessian(self, inputs=None, outputs=None, markings=False):
        nodes, blocks = self.find_relevant_nodes(inputs, outputs)
        for block in reversed(blocks):
            block.evaluate_hessian(markings=markings)

    def recompute(self, inputs=None, outputs=None):
        nodes, blocks = self.find_relevant_nodes(inputs, outputs)
        for block in blocks:
            block.recompute()
            # print(f"output of block {block} is {block.get_outputs()}")

    def reset_tlm_matrix_values(self):
        for block in reversed(self._blocks):
            block.reset_variables(types=("tlm_matrix"))

    def find_relevant_dependencies(self, outputs):
        blocks = self.get_blocks()
        if len(outputs) > 0 and hasattr(next(iter(outputs)), "block_variable"):
            nodes = set([output.block_variable for output in outputs])
        else:
            nodes = set(outputs)
        relevant_blocks = [False] * len(blocks)

        for i in range(len(blocks) - 1, -1, -1):
            block = blocks[i]
            produces_output = False
            for dep in block.get_outputs():
                if dep in nodes:
                    produces_output = True

            relevant_blocks[i] = produces_output
            if produces_output:
                for dep in block.get_dependencies():
                    nodes.add(dep)
        return nodes, relevant_blocks

    def find_relevant_outputs(self, inputs):
        blocks = self.get_blocks()
        if len(inputs) > 0 and hasattr(next(iter(inputs)), "block_variable"):
            nodes = set([control.block_variable for control in inputs])
        else:
            nodes = set(inputs)
        relevant_blocks_mask = []

        for block in blocks:
            depends_on_control = False
            for dep in block.get_dependencies():
                if dep in nodes:
                    depends_on_control = True

            relevant_blocks_mask.append(depends_on_control)
            if depends_on_control:
                for output in block.get_outputs():
                    nodes.add(output)
        return nodes, relevant_blocks_mask

    def find_relevant_nodes(self, inputs=None, outputs=None):
        # TODO: double check that inputs and outputs are block variables or controls.
        blocks = self.get_blocks()

        if inputs is None:
            if outputs is None:
                nodes = set()
                for block in blocks:
                    for dep in block.get_dependencies():
                        nodes.add(dep)
                    for output in block.get_outputs():
                        nodes.add(output)
                return nodes, blocks
            else:
                nodes, relevant_blocks_masks = self.find_relevant_dependencies(outputs)
                relevant_blocks = [
                    block for i, block in enumerate(blocks) if relevant_blocks_masks[i]
                ]
                return nodes, relevant_blocks
        else:
            if outputs is None:
                nodes, relevant_blocks_masks = self.find_relevant_outputs(inputs)
                relevant_blocks = [
                    block for i, block in enumerate(blocks) if relevant_blocks_masks[i]
                ]
                return nodes, relevant_blocks
            else:
                i_nodes, i_blocks = self.find_relevant_outputs(inputs)
                o_nodes, o_blocks = self.find_relevant_dependencies(outputs)

                nodes = i_nodes.intersection(o_nodes)
                relevant_blocks_masks = [i and o for i, o in zip(i_blocks, o_blocks)]
                relevant_blocks = [
                    block for i, block in enumerate(blocks) if relevant_blocks_masks[i]
                ]
                return nodes, relevant_blocks

    def find_absolute_dependencies_outputs(self):
        dependencies = set()
        outputs = set()
        for block in self._blocks:
            for dep in block.get_dependencies():
                if dep not in outputs:
                    dependencies.add(dep)
            for output in block.get_outputs():
                outputs.add(output)
        return dependencies, outputs

    # This function was modified to work directly with block variables.
    @contextmanager
    def marked_nodes(self, controls_or_block_variables, find_outputs=True):
        if find_outputs:
            nodes = _find_relevant_nodes(self, controls_or_block_variables)
        else:
            nodes = controls_or_block_variables
        old_values = [node.marked_in_path for node in nodes]
        for node in nodes:
            node.marked_in_path = True
        yield
        for node, old_value in zip(nodes, old_values):
            node.marked_in_path = old_value

    @contextmanager
    def save_adj_values(self):
        nodes, _ = self.find_relevant_nodes()
        old_values = [node.adj_value for node in nodes]
        for node in nodes:
            node.adj_value = None
        yield
        for node, old_value in zip(nodes, old_values):
            node.adj_value = old_value

    def _get_tf_scope_name(self, node):
        """Return a TensorFlow scope name based on the node's class name or an attribute 'tf_name'."""
        # If the block is a BlockVariable we use block.output
        if node.__class__.__name__ == "BlockVariable":
            node = node.output
        if hasattr(node, "tf_name"):
            name = node.tf_name
        else:
            name = node.__class__.__name__
        return self._valid_tf_scope_name(name)

    def _tf_register_blocks(self, name=None):
        lst = [name]
        for block in self.get_blocks():
            if block in self._tf_added_blocks:
                continue
            self._tf_added_blocks.append(block)
            lst.append(_block_get_tf_blocks(block))
        self._tf_registered_blocks.append(lst)

    def _tf_rebuild_registered_blocks(self):
        """Remove blocks that no longer exist on the tape from registered blocks."""
        new_registered_blocks = []
        new_added_blocks = []
        for scope in self._tf_registered_blocks:
            lst = scope[:1]
            for block in scope[1:]:
                if isinstance(block, Block):
                    if block in self.get_blocks():
                        lst.append(block)
                else:
                    block, sub_blocks = block
                    if block in self.get_blocks():
                        lst.append(_block_get_tf_blocks(block))
                new_added_blocks.append(block)
            if len(lst) > 1:
                new_registered_blocks.append(lst)
        self._tf_registered_blocks = new_registered_blocks
        self._tf_added_blocks = new_added_blocks

    def _tf_add_blocks_scoped(self, blocks):
        """Add the given blocks (with possible sub-blocks) to the TensorFlow graph."""

        import tensorflow.compat.v1 as tf

        for block in blocks:
            self._tf_add_block(block)

        for block in blocks:
            if not isinstance(block, Block):
                block = block[0]
            for out in block.get_outputs():
                if id(out) not in self._tf_tensors:
                    t = self._tf_output_block_lookup.get(id(out), None)
                    if t is None:
                        # This block output wasn't created in the tensorflow
                        # graph, and I have no way to create it because I don't
                        # know what block generated the corresponding tensor.
                        raise ValueError(
                            "This output is expected to be created in a sub-block: {}".format(
                                str(out)
                            )
                        )
                    with tf.name_scope(self._get_tf_scope_name(out)):
                        tout = tf.py_function(
                            lambda: None,
                            [t],
                            [tf.float64],
                            name=self._valid_tf_scope_name(str(out)),
                        )
                    self._tf_tensors[id(out)] = tout

    def visualise(self, output="log", *args, **kwargs):
        """This resets the TensorFlow data, which allows a user to call tape.visualise() twice without error."""
        if not output.endswith(".dot"):
            self._tf_tensors = {}
            self._tf_added_blocks = []
            self._tf_registered_blocks = []
        return super().visualise(output, *args, **kwargs)

    def _tf_add_blocks(self):
        """Add new blocks to the TensorFlow graph while supporting the name_scope() method."""

        import tensorflow as tf

        self._tf_register_blocks()
        self._tf_rebuild_registered_blocks()

        for scope in self._tf_registered_blocks:
            scope_name = scope[0]
            if scope_name is None:
                self._tf_add_blocks_scoped(scope[1:])
            else:
                with tf.name_scope(scope_name):
                    self._tf_add_blocks_scoped(scope[1:])

    def _tf_add_block(self, block, sub_blocks=None):
        """Add a block to the TensorFlow graph, and recursively add its sub-blocks."""

        import tensorflow as tf

        if not isinstance(block, Block):
            if sub_blocks is not None:
                raise ValueError(
                    "If the input is not a Block, then it should be a tuple (block, sub_blocks) and the sub_blocks kwarg must be None"
                )
            block, sub_blocks = block

        # Block dependencies
        in_tensors = []
        for dep in block.get_dependencies():
            if id(dep) in self._tf_tensors:
                in_tensors.append(self._tf_tensors[id(dep)])
            else:
                # Look up the block variable in _tf_output_block_lookup to
                # connect it to a previously recorded block if necessary.
                inputs = self._tf_output_block_lookup.get(id(dep), [])
                with tf.name_scope(self._get_tf_scope_name(dep)):
                    tin = tf.numpy_function(
                        lambda: None,
                        inputs,
                        [tf.float64],
                        name=self._valid_tf_scope_name(str(dep)),
                    )
                    in_tensors.append(tin)
                    self._tf_tensors[id(dep)] = tin

        # Block node
        with tf.name_scope(self._get_tf_scope_name(block)):
            if sub_blocks is None:

                def tf_np_f(*args):
                    return None

                tensor = tf.numpy_function(
                    tf_np_f,
                    in_tensors,
                    [tf.float64],
                    name=self._valid_tf_scope_name(str(block)),
                )
                self._tf_tensors[id(block)] = tensor
            else:
                for sub_block in sub_blocks:
                    self._tf_add_block(sub_block)
            if hasattr(block, "tf_add_extra_to_graph"):
                block.tf_add_extra_to_graph(self._tf_tensors)

        # Block outputs.
        # To avoid incorrectly scoping the block outputs, these will be added
        # once they are used as input. The output tensor of the current block must
        # be saved to be used as input when the block outputs are created.
        if sub_blocks is None:
            for out in block.get_outputs():
                self._tf_output_block_lookup[id(out)] = tensor
