# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class Paper(Component):
    """A Paper component.
Paper component from Material UI
https://mui.com/components/paper/

Keyword arguments:

- children (a list of or a singular dash component, string or number; optional):
    Can be used to render elements inside the component.

- elevation (number; default 1):
    This number represents the elevation of the paper shadow.

- square (boolean; default False):
    By default, the paper will have a border radius. Set this to True
    to generate a paper with sharp corners."""
    @_explicitize_args
    def __init__(self, children=None, elevation=Component.UNDEFINED, square=Component.UNDEFINED, **kwargs):
        self._prop_names = ['children', 'elevation', 'square']
        self._type = 'Paper'
        self._namespace = 'dash_mdc_neptune'
        self._valid_wildcard_attributes =            []
        self.available_properties = ['children', 'elevation', 'square']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}
        for k in []:
            if k not in args:
                raise TypeError(
                    'Required argument `' + k + '` was not specified.')
        super(Paper, self).__init__(children=children, **args)
