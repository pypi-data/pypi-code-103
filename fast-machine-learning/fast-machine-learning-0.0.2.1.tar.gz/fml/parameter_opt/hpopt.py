
from ..validates import Validate
from hyperopt import fmin, tpe, STATUS_OK
from ._utils import raise_dataobject as rd
from ..utils.base_func import define_task
from ..configs.auto_config import AutoConfig

import numpy as np

class HpOpt(object):

    def __init__(self, rounds=100, verbose=False):
        self.trials = []
        self.metrics = []
        self.rounds = rounds
        self.verbose = verbose

    def fit(self, dataobject, cv=5, task="reg"):
        """
        cv : 5, 10, True, False
        """
        rd(dataobject)
        if task == "reg":
            space = AutoConfig().regression
        else:
            raise Exception("cls not completed yet")
