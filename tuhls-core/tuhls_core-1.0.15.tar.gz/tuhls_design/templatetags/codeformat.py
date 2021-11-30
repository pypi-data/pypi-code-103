from django import template
from django.utils.safestring import mark_safe
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name

register = template.Library()


@register.simple_tag()
def codeformat(code, format):
    lexer = get_lexer_by_name(format, stripall=True)
    formatter = HtmlFormatter(linenos=True, cssclass="source")
    return mark_safe(highlight(code, lexer, formatter))
