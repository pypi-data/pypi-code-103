from pyadjoint import Block as pyadjoint_block
from pyadjoint.tape import no_annotations


class Block(pyadjoint_block):
    @no_annotations
    def evaluate_tlm_matrix(self, markings=False):
        """Computes the tangent linear action and stores the result in the
        ``tlm_matrix`` attribute of the outputs.

        This method will by default call the :meth:`evaluate_tlm_matrix_component` method for each output.

        Args:
            markings (bool): If True, then each block_variable will have set ``marked_in_path`` attribute indicating
                whether their tlm components are relevant for computing the final target tlm values.
                Default is False.

        """
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
            (i, bv) for i, bv in enumerate(outputs) if bv.marked_in_path or not markings
        ]

        if len(relevant_outputs) <= 0:
            return

        prepared = self.prepare_evaluate_tlm_matrix(
            inputs, tlm_inputs, relevant_outputs
        )

        for idx, out in relevant_outputs:
            tlm_matrix = self.evaluate_tlm_matrix_component(
                inputs, tlm_inputs, out, idx, prepared
            )
            if tlm_matrix is not None:
                out.add_tlm_matrix(tlm_matrix)

    def prepare_evaluate_tlm_matrix(self, inputs, tlm_inputs, relevant_outputs):
        """Runs preparations before :meth:`evaluate_tlm_matrix_component` is ran.

        The return value is supplied to each of the subsequent :meth`evaluate_tlm_matrix_component` calls.
        This method is intended to be overridden for blocks that require such preparations, by default there is none.

        Args:
            inputs: The values of the inputs
            tlm_inputs: The tlm inputs
            relevant_outputs: A list of the relevant block variables for :meth:`evaluate_tlm_matrix_component`.

        Returns:
            Anything. The returned value is supplied to :meth:`evaluate_tlm_matrix_component`

        """
        return None

    def evaluate_tlm_matrix_component(
        self, inputs, tlm_inputs, block_variable, idx, prepared=None
    ):
        """This method should be overridden.

        The method should implement a routine for computing the Jacobian of the
        block that corresponds to one output. Consider evaluating the Jacobian
        of a tape with n inputs and m outputs. A block on the tape has n' inputs
        and m' outputs. That block should take an n' x n Jacobian as input, and
        it should output an m' x n Jacobian. This function should return the
        Jacobian for just one output applied to the input Jacobian. The return
        value should be a list with n entries.

        Args:
            inputs (list): A list of the saved input values, determined by the dependencies list.
            tlm_inputs (list[list]): The Jacobian of the inputs, determined by the dependencies list.
            block_variable (pyadjoint_utils.BlockVariable): The block variable of the output corresponding to index `idx`.
            idx (int): The index of the component to compute.
            prepared (object): Anything returned by the :meth:`prepare_evaluate_tlm_matrix` method. Default is None.

        Returns:
            An object of the same type as ``block_variable.saved_output``: The resulting product.

        """
        raise NotImplementedError(
            "evaluate_tlm_matrix_component is not implemented for Block-type: {}".format(
                type(self)
            )
        )
