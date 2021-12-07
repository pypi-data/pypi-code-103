from assertman.assertable_mixin import AssertableMixin


class AssertableFloat(float, AssertableMixin):
    _assertion_processing = "hamcrest"

    @property
    def _assertable_data(self):
        return self

