from assertman.assertable_mixin import AssertableMixin


class AssertableDatetime(str, AssertableMixin):

    @property
    def _assertable_data(self):
        return self
