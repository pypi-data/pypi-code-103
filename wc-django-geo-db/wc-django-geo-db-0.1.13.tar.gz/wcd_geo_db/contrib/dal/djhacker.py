from typing import Optional, Type
import types
import djhacker
from django import forms
from django.db import models
from dal.autocomplete import ModelSelect2

from .forms import PreparableModelChoiceField


__all__ = (
    'formfield',
)


def default_field_callback(model_field: models.Field, **kwargs):
    return None, kwargs


def djhacker_formfield(model_field, cls=None, /, **kwargs):
    def _formfield(self, *args, **kw):
        cls = self.djhacker['cls']
        formfield = self.djhacker['django'](*args, **{
            # FIXME: This copypaste happened because of this line here:
            **({'form_class': cls} if cls is not None else {}),
            # FIXME: This entire function was copy-pasted only to change
            # the order of kwargs passed to formfield:
            # In original function it was:
            # **self.djhacker['kwargs'],
            # **kw,
            **kw,
            **self.djhacker['kwargs'],
        })
        return formfield

    if not cls:
        # FIXME: Copypaste also happened because of this `default` value here:
        cb = djhacker.registry.get(model_field.field, default_field_callback)
        cls, kwargs = cb(model_field, **kwargs)

    current = getattr(model_field.field, 'djhacker', None)
    if current:
        # In case of re-registration
        model_field.field.formfield = model_field.field.djhacker['django']

    model_field.field.djhacker = dict(
        django=model_field.field.formfield,
        cls=cls,
        kwargs=kwargs,
    )
    model_field.field.formfield = types.MethodType(
        _formfield, model_field.field
    )


def formfield(
    url: str,
    model_field: models.Field,
    field_class: Optional[Type[forms.Field]] = None,
    widget_class: Type[forms.Widget] = ModelSelect2,
    **kwargs
) -> None:
    if 'preparator' in kwargs and kwargs['preparator'] is not None and field_class is None:
        field_class = PreparableModelChoiceField

    return djhacker_formfield(
        model_field,
        field_class,
        widget=widget_class(url=url),
        **kwargs
    )
