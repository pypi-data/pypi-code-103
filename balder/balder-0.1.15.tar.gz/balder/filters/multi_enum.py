import django_filters
from django import forms
from balder.enum import InputEnum
from graphene_django.forms.converter import convert_form_field
import graphene


class EnumMultiChoiceField(forms.MultipleChoiceField):

    def __init__(self, *args, choices=None, type=None, **kwargs) -> None:
        
        self.__choices = choices
        self.__type = type
        self.__choices = [ (str(value.value), str(value.value)) for key, value in self.__type._meta.enum.__members__.items()]
        # casting here is weird as we will get the actual value from our graphene type again

        super().__init__(*args, choices=self.__choices, **kwargs)


    @property
    def overwritten_type(self):

        def construct(*args, **kwargs):
            return graphene.List(self.__type, **kwargs)

        if self.__type: return construct



@convert_form_field.register(EnumMultiChoiceField)
def convert_form_field_to_string_list(field):
    return field.overwritten_type(required=field.required)

class MultiEnumFilter(django_filters.MultipleChoiceFilter):
    field_class = EnumMultiChoiceField


