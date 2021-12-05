from django import template

from usefathom import GOALS

register = template.Library()


@register.inclusion_tag("usefathom/click.html")
def click_goal(goal: str, value: int = 0):
    return _set_context(goal, value)


@register.inclusion_tag("usefathom/submit.html")
def submit_goal(goal: str, value: int = 0):
    return _set_context(goal, value)


def _set_context(goal: str, value: int):
    if goal in GOALS:
        goal = GOALS[goal]
    return {
        "goal": goal,
        "value": value,
    }