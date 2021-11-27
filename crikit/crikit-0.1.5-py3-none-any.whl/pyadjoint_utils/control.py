from pyadjoint import Control as pyadjoint_control


class Control(pyadjoint_control):
    @property
    def tlm_matrix(self):
        return self.block_variable.tlm_matrix

    @tlm_matrix.setter
    def tlm_matrix(self, value):
        self.block_variable.tlm_matrix = value
