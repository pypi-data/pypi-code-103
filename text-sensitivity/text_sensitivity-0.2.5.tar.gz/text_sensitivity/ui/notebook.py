"""Extension of `genbase.ui.notebook` for custom rendering of `text_sensitivity."""

import copy

from genbase.ui import get_color
from genbase.ui.notebook import Render as BaseRender
from genbase.ui.notebook import format_instances
from text_explainability.ui.notebook import (default_renderer,
                                             get_meta_descriptors)

TEST_EXP = {'robustness+input_space': 'This sensitivity test checks if your model is able to handle ' +
                                      'different input character (sequences) without throwing errors.',
            'sensitivity+invariance': 'This sensitivity test has the assumption that all instances will have the ' +
                                      'same expected prediction for all instances.'}


def success_test_renderer(meta: dict, content: dict, **renderargs) -> str:
    def h(title):
        return f'<h3>{title}</h3>'

    def none_to_show(success_failure: str, succeeded_failed: str):
        return f'<p>No {success_failure} to show, because all instances {succeeded_failed}.</p>'

    n_success, n_fail = len(content['successes']), len(content['failures'])
    kwargs = {'predictions': content['predictions']} if 'predictions' in content else {}

    color = get_color(content['success_percentage'],
                      min_value=0.0,
                      max_value=1.0,
                      colorscale=[(0, '#A50026'), (0.5, '#BBBB00'), (1.0, '#006837')])
    html = h('Test results')
    html += f'<p style="font-size: 110%">Success: <b style="color: {color}">{content["success_percentage"]:0.00%}</b> '
    html += f'({n_success} out of {n_success + n_fail}).</p>'
    html += h('Success')
    html += format_instances(content['successes'], **kwargs) if n_success > 0 \
        else none_to_show('successes', 'failed')
    html += h('Failures')
    html += format_instances(content['failures'], **kwargs) if n_fail \
        else none_to_show('failures', 'succeeded')
    return html


class Render(BaseRender):
    def __init__(self, *configs):
        super().__init__(*configs) 
        self.main_color = '#D32F2F'
        self.package_link = 'https://git.io/text_sensitivity'

    @property
    def tab_title(self):
        return 'Sensitivity Test Results'

    @property
    def custom_tab_title(self):
        return 'Test Settings'

    def get_renderer(self, meta: dict):
        type, subtype, _ = get_meta_descriptors(meta)

        if type == 'robustness':
            if subtype == 'input_space':
                return success_test_renderer
        if subtype == 'invariance':
            return success_test_renderer
        return default_renderer

    def format_title(self, title: str, h: str = 'h1', **renderargs) -> str:
        return super().format_title(title, h=h, **renderargs).replace('_', ' ').title()

    def render_subtitle(self, meta: dict, content, **renderargs) -> str:
        type, subtype, _ = get_meta_descriptors(meta)
        name = f'{type}+{subtype}'
        return self.format_subtitle(TEST_EXP[name]) if name in TEST_EXP else ''

    def custom_tab(self, config: dict, **renderargs) -> str:
        meta = config["META"]
        if 'callargs' not in meta:
            return ''
        callargs = copy.deepcopy(meta['callargs'])
        _ = callargs.pop('__name__')
        _ = callargs.pop('model')
        if 'kwargs' in callargs:
            kwargs = callargs.pop('kwargs')
            for k, v in kwargs.items():
                callargs[k] = v

        def fmt(k, v) -> str:
            if isinstance(v, list):
                return '<ul>' + ''.join([f'<li>{fmt(k, v_)}</li>' for v_ in v]) + '</ul>'
            elif isinstance(v, dict) and '__class__' in v:
                if v['__class__'].startswith('text_sensitivity.data.random.string'):
                    options = v['options']
                    if isinstance(options, str):
                        options = f'"{options}"'
                    return f'<kbd>{v["__class__"]}</kbd> ({options})'
            elif str.lower(k) == 'expectation':
                return f'<kbd>{v}</kbd>'
            return str(v)

        html = ''.join([f'<tr><td>{k}:</td><td>{fmt(k, v)}</td></tr>' for k, v in callargs.items()])
        return f'<div class="table-wrapper"><table class="sensitivity-test-settings">{html}</table></div>'
