from django import template
from django.conf import settings
from django.template import loader

register = template.Library()


@register.simple_tag
def include_js(name):
    js_url = settings.ANY_JS[name]['js_url']

    template = loader.get_template('django_any_js/js.html')
    context = {'js_url': js_url}

    return template.render(context)


@register.simple_tag
def include_css(name):
    css_url = settings.ANY_JS[name]['css_url']

    template = loader.get_template('django_any_js/css.html')
    context = {'css_url': css_url}

    return template.render(context)
