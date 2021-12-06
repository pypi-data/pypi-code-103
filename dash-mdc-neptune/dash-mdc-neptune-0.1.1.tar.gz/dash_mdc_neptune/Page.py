# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class Page(Component):
    """A Page component.
Page component
Dashboard > Page
https://github.com/danielfrg/jupyter-flex/blob/main/js/src/Section/index.js

Keyword arguments:

- children (optional):
    Can be used to render elements inside the component.

- orientation (default 'columns'):
    Dashboard general orientation (rows or columns).

- verticalLayout (default 'fill'):
    Dashboard general layout (fill or scroll)."""
    @_explicitize_args
    def __init__(self, children=None, orientation=Component.UNDEFINED, verticalLayout=Component.UNDEFINED, **kwargs):
        self._prop_names = ['children', 'orientation', 'verticalLayout']
        self._type = 'Page'
        self._namespace = 'dash_mdc_neptune'
        self._valid_wildcard_attributes =            []
        self.available_properties = ['children', 'orientation', 'verticalLayout']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}
        for k in []:
            if k not in args:
                raise TypeError(
                    'Required argument `' + k + '` was not specified.')
        super(Page, self).__init__(children=children, **args)
