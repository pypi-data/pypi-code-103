from django import template

register = template.Library()


@register.filter
def separate_by_slash(value):
    if not value:
        return value

    value = value.replace("(", "")
    value = value.replace(")", " /")
    return value
