from assertman.assertable_mixin import AssertableMixin


class AssertableInt(int, AssertableMixin):
    _assertion_processing = "hamcrest"

    @property
    def _assertable_data(self):
        return self

