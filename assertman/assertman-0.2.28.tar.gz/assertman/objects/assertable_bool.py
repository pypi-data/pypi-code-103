from assertman.assertable_mixin import AssertableMixin


class AssertableBool(AssertableMixin):
    _assertion_processing = "hamcrest"

    def __init__(self, value):
        if not isinstance(value, (bool, AssertableBool)):
            raise TypeError('AssertableBool может содержать только boolean-значение')
        self.value = value

    def __repr__(self):
        return str(self.value)

    def __eq__(self, other):
        return self.value == other

    @property
    def _assertable_data(self):
        return self.value

