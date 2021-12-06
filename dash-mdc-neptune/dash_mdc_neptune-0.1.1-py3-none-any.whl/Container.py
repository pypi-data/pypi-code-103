# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class Container(Component):
    """A Container component.
Container component from Material UI
https://mui.com/components/container/

Keyword arguments:

- children (a list of or a singular dash component, string or number; optional):
    Can be used to render elements inside the component.

- fixed (boolean; default False):
    If True, the container max-width will be fixed.

- maxWidth (string; default 'sm'):
    Maximum width boundary for the container."""
    @_explicitize_args
    def __init__(self, children=None, maxWidth=Component.UNDEFINED, fixed=Component.UNDEFINED, **kwargs):
        self._prop_names = ['children', 'fixed', 'maxWidth']
        self._type = 'Container'
        self._namespace = 'dash_mdc_neptune'
        self._valid_wildcard_attributes =            []
        self.available_properties = ['children', 'fixed', 'maxWidth']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}
        for k in []:
            if k not in args:
                raise TypeError(
                    'Required argument `' + k + '` was not specified.')
        super(Container, self).__init__(children=children, **args)
