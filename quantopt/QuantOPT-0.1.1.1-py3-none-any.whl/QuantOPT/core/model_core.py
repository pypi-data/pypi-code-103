# coding=utf-8
from QuantOPT.core.base import _SimpleOpt
from QuantOPT.models.model_MaxIR import MaxIR
from QuantOPT.models.model_MaxRiskAdjReturn import MaxRiskAdjReturn
from QuantOPT.models.model_MinVar import MinVar
from QuantOPT.utils.singleton import singleton

__all__ = ['_SimpleOpt', 'MinVar', 'MaxRiskAdjReturn', 'MaxIR']


@singleton
class Models(object):
    MinVar = MinVar
    MaxRiskAdjReturn = MaxRiskAdjReturn
    MaxIR = MaxIR
    _SimpleOpt = _SimpleOpt

    def __init__(self, *agrs, **kwargs):
        pass

    @classmethod
    def add_model(cls, name, model):
        setattr(cls, name, model)


Holder = Models()
if __name__ == '__main__':
    pass
