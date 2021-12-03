from pysimmods.model.config import ModelConfig
from pysimmods.model.inputs import ModelInputs
from pysimmods.model.model import Model
from pysimmods.model.state import ModelState


class DummyConfig(ModelConfig):
    def __init__(self, params):
        super().__init__(params)

        self._default_schedule = [10 for _ in range(24)]

    @property
    def p_max_kw(self):
        return 500

    @property
    def p_min_kw(self):
        return 0


class DummyState(ModelState):
    def __init__(self, inits):
        super().__init__(inits)


class DummyInputs(ModelInputs):
    pass


class DummyModel(Model):
    def __init__(self, params, inits):
        self.config = DummyConfig(params)
        self.state = DummyState(inits)
        self.inputs = DummyInputs()

    def step(self):
        self.state.p_kw = self.inputs.p_set_kw

    @property
    def set_percent(self):
        return self.inputs.p_set_kw / self.config.p_max_kw * 100

    @set_percent.setter
    def set_percent(self, value):
        self.inputs.p_set_kw = value * self.config.p_max_kw / 100
