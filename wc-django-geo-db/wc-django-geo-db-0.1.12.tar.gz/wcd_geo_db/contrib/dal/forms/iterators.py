from django.forms.models import ModelChoiceIterator
from django.db import models


__all__ = 'PreparableModelChoiceIterator',


class PreparableModelChoiceIterator(ModelChoiceIterator):
    def __iter__(self):
        if self.field.empty_label is not None:
            yield ("", self.field.empty_label)

        for obj in self.prepare_values(self.queryset):
            yield self.choice(obj)

    def prepare_values(self, qs: models.QuerySet):
        return self.field.prepare_values(qs)

    # def choice(self, obj):
    #     return (
    #         ModelChoiceIteratorValue(self.field.prepare_value(obj), obj),
    #         self.field.label_from_instance(obj),
    #     )
