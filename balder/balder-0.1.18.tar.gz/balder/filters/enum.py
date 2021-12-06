import django_filters
from django import forms
from balder.enum import InputEnum
from graphene_django.forms.converter import convert_form_field


class EnumChoiceField(forms.CharField):

    def __init__(self, *args, choices=None, type=None, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.__choices = choices
        self.__type = type

    @property
    def overwritten_type(self):
        if self.__type: return self.__type
        return InputEnum.from_choices(self.__choices)



@convert_form_field.register(EnumChoiceField)
def convert_form_field_to_string_list(field):
    return field.overwritten_type(required=field.required)

class EnumFilter(django_filters.CharFilter):
    field_class = EnumChoiceField

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        assert self.field_name

    def filter(self, qs, value):
        """ Convert the filter value to a primary key before filtering """
        if value:
            return qs.filter(**{self.field_name: value})
        return qs
