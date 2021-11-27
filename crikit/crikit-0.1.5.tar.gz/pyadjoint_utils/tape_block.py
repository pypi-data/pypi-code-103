from pyadjoint.tape import get_working_tape, annotate_tape
from pyadjoint_utils.block import Block
from pyadjoint_utils.tape import push_tape
from contextlib import contextmanager


@contextmanager
def record_tape_block(**kwargs):
    with push_tape() as new_tape:
        yield new_tape
    add_tape_block(new_tape, **kwargs)


def add_tape_block(tape, **kwargs):
    annotate = annotate_tape(kwargs)
    if annotate:
        working_tape = get_working_tape()
        if tape == working_tape:
            raise ValueError("TapeBlock must be recorded on a separate tape")
        block = TapeBlock(tape, **kwargs)
        # TODO: should I have a check here to make sure the same tape bock isn't added twice?
        working_tape.add_block(block)


class TapeBlock(Block):
    """A block that represents an entire tape.

    This idea could also be expressed as a ReducedFunctionBlock. In many cases,
    the user wll already know what the desired dependencies and outputs are. If
    they give the ReducedFunction, then it is possible to avoid computing blocks
    that don't show up in the list of the ReducedFunction's outputs.
    """

    def __init__(self, tape, name=None):
        super().__init__()
        self.tape = tape

        # Note: add_dependency() and add_output() are not used here because they
        #   call the _ad_will_add_as_xxxx() functions, which sometimes make
        #   copies of the variable. The tape visualization (and maybe
        #   computation?) will be messed up if there are extraneous
        #   BlockVariable copies.
        dependencies, outputs = self.tape.find_absolute_dependencies_outputs()
        self._dependencies += dependencies
        self._outputs += outputs

        self.name = name if name is not None else "TapeBlock"

    def __str__(self):
        return self.name

    @property
    def tf_name(self):
        return self.name

    def reset_variables(self, types=None):
        self.tape.reset_variables(types)

    def prepare_recompute_component(self, inputs, relevant_outputs):
        block_variables = [bv for i, bv in relevant_outputs]
        self.tape.recompute(outputs=block_variables)

    def prepare_evaluate_adj(self, inputs, adj_inputs, relevant_dependencies):
        block_variables = [bv for i, bv in relevant_dependencies]
        # FIXME: I actually have to overwrite evaluate_adj() to get the correct
        # value for markings, but it's usually going to be True.
        self.tape.evaluate_adj(inputs=block_variables, markings=True)

    def prepare_evaluate_tlm(self, inputs, tlm_inputs, relevant_outputs):
        block_variables = [bv for i, bv in relevant_outputs]
        self.tape.evaluate_tlm(outputs=block_variables)

    def prepare_evaluate_hessian(
        self, inputs, hessian_inputs, adj_inputs, relevant_dependencies
    ):
        block_variables = [bv for i, bv in relevant_dependencies]
        self.tape.evaluate_hessian(inputs=block_variables, markings=True)

    def prepare_evaluate_tlm_matrix(self, inputs, tlm_inputs, relevant_outputs):
        block_variables = [bv for i, bv in relevant_outputs]
        self.tape.evaluate_tlm_matrix(outputs=block_variables, markings=True)

    # These functions don't need to do anything because everything is handled in the 'prepare_*' functions.
    def _nothing(*args, **kwargs):
        pass

    recompute_component = _nothing
    evaluate_adj_component = _nothing
    evaluate_tlm_component = _nothing
    evaluate_tlm_matrix_component = _nothing
    evaluate_hessian_component = _nothing

    def tf_get_blocks(self):
        return (self, self.tape.get_blocks())
