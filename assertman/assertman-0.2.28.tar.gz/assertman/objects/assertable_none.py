from assertman.assertable_mixin import AssertableMixin


class AssertableNone(AssertableMixin):
    _assertion_processing = "hamcrest"

    def __init__(self, value):
        if value is not None:
            raise TypeError('AssertableNone может содержать только none-значение')
        self.value = value

    def __repr__(self):
        return str(self.value)

    def __eq__(self, other):
        return self.value == other

    @property
    def _assertable_data(self):
        return self.value

