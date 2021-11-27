from pyadjoint.overloaded_type import register_overloaded_type
from pyadjoint import AdjFloat as AdjFloatOrig


class AdjFloat(AdjFloatOrig):
    def _ad_dim(self):
        return 1

    def _ad_iadd(self):
        raise NotImplementedError("'AdjFloat' cannot do in-place operations")

    def _ad_imul(self):
        raise NotImplementedError("'AdjFloat' cannot do in-place operations")

    @property
    def tf_name(self):
        return str(self.__class__.__name__) + "_" + str(self.block_variable)


register_overloaded_type(AdjFloat, float)
