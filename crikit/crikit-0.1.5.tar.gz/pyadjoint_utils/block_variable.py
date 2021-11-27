from pyadjoint.block_variable import BlockVariable as pyadjoint_block_variable


class BlockVariable(pyadjoint_block_variable):
    """References a block output variable."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tlm_matrix = None

    def add_tlm_matrix(self, val):
        if self.tlm_matrix is None:
            self.tlm_matrix = val
        else:
            self.tlm_matrix += val

    def reset_variables(self, types):
        super().reset_variables(types)

        if "tlm_matrix" in types:
            self.tlm_matrix = None
