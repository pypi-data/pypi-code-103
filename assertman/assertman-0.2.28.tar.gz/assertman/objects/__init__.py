from assertman.assertable_mixin import AssertableMixin
from assertman.objects.assertable_string import AssertableString
from assertman.objects.assertable_list import AssertableList
from assertman.objects.assertable_dict import AssertableDict
from assertman.objects.assertable_int import AssertableInt
from assertman.objects.assertable_float import AssertableFloat
from assertman.objects.assertable_datetime import AssertableDatetime
from assertman.objects.assertable_bool import AssertableBool
from assertman.objects.assertable_none import AssertableNone
import datetime


def make_assertable_object(arg):
    if isinstance(arg, bool):
        return AssertableBool(arg)
    if isinstance(arg, str):
        return AssertableString(arg)
    elif isinstance(arg, int):
        return AssertableInt(arg)
    elif isinstance(arg, float):
        return AssertableFloat(arg)
    elif isinstance(arg, list):
        return AssertableList(arg)
    elif isinstance(arg, dict):
        return AssertableDict(arg)
    elif isinstance(arg, datetime.datetime):
        return AssertableDatetime(arg)
    elif arg is None:
        return AssertableNone(arg)
    elif AssertableMixin in type(arg).__bases__:
        return arg
    raise ValueError(f"Для переданнного типа даннных <{type(arg)}> нет маппинга")