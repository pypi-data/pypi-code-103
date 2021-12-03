from django.forms import ModelMultipleChoiceField, ModelChoiceField

from ..preparators import Preparator
from .iterators import PreparableModelChoiceIterator


__all__ = (
    'PreparableChoicesFieldMixin',
    'PreparableModelChoiceField',
    'PreparableModelMultipleChoiceField',
)


class PreparableChoicesFieldMixin:
    iterator = PreparableModelChoiceIterator
    preparator: Preparator

    def __init__(self, *a, preparator: Preparator = None, **kw):
        super().__init__(*a, **kw)

        assert preparator is not None, '`preparator` must be provided'
        self.preparator = preparator

    def prepare_values(self, qs):
        return self.preparator.prepare(qs)

    def prepare_value(self, value):
        if isinstance(value, self.preparator.type):
            return self.preparator.get_value(value)

        return super().prepare_value(value)

    def label_from_instance(self, value):
        return self.preparator.get_label(value)


class PreparableModelChoiceField(PreparableChoicesFieldMixin, ModelChoiceField):
    pass


class PreparableModelMultipleChoiceField(PreparableChoicesFieldMixin, ModelMultipleChoiceField):
    pass
