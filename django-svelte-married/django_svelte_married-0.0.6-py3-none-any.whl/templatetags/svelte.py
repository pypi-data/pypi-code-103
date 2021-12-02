# -*- coding: utf-8 -*-
import hashlib
import json

from typing import Dict

from django import template
from django.template import Node
from django.utils.safestring import mark_safe

from django_svelte_married.settings import (SVELTE_RELOADING_ENABLED, SVELTE_RELOADING_HOSTNAME, SVELTE_RELOADING_PORT,
                                            SVELTE_RENDERER)

register = template.Library()


def _hash_component_props(component: str, props: any = None, idx: int = 0) -> str:
    """Creates unique hash of component and props to uniquely identify component in `SVELTE_COMPONENTS`"""
    component_props_str = json.dumps([component, props, idx])
    return hashlib.md5(component_props_str.encode('utf-8')).hexdigest()


class SvelteNode(Node):
    def __init__(self, nodelist, args):
        self.nodelist = nodelist
        self.args = args
        super().__init__()

    def render(self, context):
        if 'SVELTE_COMPONENTS' not in context:
            raise Exception("You need to add 'django_svelte_married.context_processors.svelte' as a context processor "
                            "in `TEMPLATES` of your project's settings.py")
        if len(self.args) < 2:
            raise Exception("tbd")
        component, props = self.args[0].resolve(context), self.args[1].resolve(context)
        props_jsons = json.loads(props) if isinstance(props, str) else props
        mount_id = _hash_component_props(component, props_jsons, len(context['SVELTE_COMPONENTS'].keys()))
        context['SVELTE_COMPONENTS'][mount_id] = {'component': component, 'props': props_jsons}
        context.update(dict(id=mount_id, content=mark_safe(self.render_ssr(component, props))))
        return self.nodelist.render(context).strip()

    def render_ssr(self, component, props):
        return SVELTE_RENDERER(component=component, props=props)


@register.tag("svelte")
def svelte(parser, token):
    args = [parser.compile_filter(t) for t in token.split_contents()[1:]]
    nodelist = parser.parse(('endsvelte',))
    parser.delete_first_token()
    return SvelteNode(nodelist, args)


@register.inclusion_tag('svelte_print.html', takes_context=True)
def svelte_print(context: Dict[str, any]):
    return {'SVELTE_PRINT': mark_safe(json.dumps(context.get('SVELTE_COMPONENTS', {}))),
            'SVELTE_RELOADING_ENABLED': SVELTE_RELOADING_ENABLED,
            'SVELTE_RELOADING_HOSTNAME': SVELTE_RELOADING_HOSTNAME,
            'SVELTE_RELOADING_PORT': SVELTE_RELOADING_PORT}
