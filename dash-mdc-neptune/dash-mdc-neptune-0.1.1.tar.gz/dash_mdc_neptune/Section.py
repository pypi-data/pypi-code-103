# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class Section(Component):
    """A Section component.
Section component
Dashboard > Page > Section
https://github.com/danielfrg/jupyter-flex/blob/main/js/src/Section/index.js

Keyword arguments:

- children (a list of or a singular dash component, string or number; optional):
    Can be used to render elements inside the component.

- orientation (string; default 'rows'):
    Section general orientation (rows or columns).

- size (number; default 0):
    Section container size (0 < grid size <= 12)."""
    @_explicitize_args
    def __init__(self, children=None, size=Component.UNDEFINED, orientation=Component.UNDEFINED, **kwargs):
        self._prop_names = ['children', 'orientation', 'size']
        self._type = 'Section'
        self._namespace = 'dash_mdc_neptune'
        self._valid_wildcard_attributes =            []
        self.available_properties = ['children', 'orientation', 'size']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}
        for k in []:
            if k not in args:
                raise TypeError(
                    'Required argument `' + k + '` was not specified.')
        super(Section, self).__init__(children=children, **args)
