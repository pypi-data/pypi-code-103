# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class Card(Component):
    """A Card component.
Card component
Dashboard > Page > Section > Card
https://github.com/danielfrg/jupyter-flex/blob/main/js/src/Card/index.js

Keyword arguments:

- children (a list of or a singular dash component, string or number; optional):
    Can be used to render elements inside the component.

- size (number; default 0):
    Card container size (0 < grid size <= 12).

- title (string; default ''):
    Card overall title."""
    @_explicitize_args
    def __init__(self, children=None, title=Component.UNDEFINED, size=Component.UNDEFINED, **kwargs):
        self._prop_names = ['children', 'size', 'title']
        self._type = 'Card'
        self._namespace = 'dash_mdc_neptune'
        self._valid_wildcard_attributes =            []
        self.available_properties = ['children', 'size', 'title']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}
        for k in []:
            if k not in args:
                raise TypeError(
                    'Required argument `' + k + '` was not specified.')
        super(Card, self).__init__(children=children, **args)
