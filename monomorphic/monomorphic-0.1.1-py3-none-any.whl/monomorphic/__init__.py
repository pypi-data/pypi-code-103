
#
# monomorph -- convert subclasses of string, int, double, etc. to pure strings, ints, double, etc. to address
# brittle software that doesn't support polymorphism.
import inspect
from copy import deepcopy, copy
from typing import Any, List, Type

base_types = (bool, bytearray, bytes, complex, float, int, str, dict, set, list, tuple)


def monomorph(d: Any, full_copy: bool = False, convert_types: List[Type] = base_types) -> Any:
    """
    Convert d, which may be (or contain) polymorphic types into its non-polymorphic equivalent
    :param d: Element to convert
    :param full_copy: True means everything.  False means only copy python types.  Default: False
    :param convert_types: List of types co convert.  Default is base_types
    :return: Converted element
    """
    if isinstance(d, dict) and dict in convert_types:
        return {k: monomorph(v, full_copy, convert_types) for k, v in d.items()}
    elif isinstance(d, set) and set in convert_types:
        return {monomorph(v, full_copy, convert_types) for v in d}
    elif isinstance(d, tuple) and tuple in convert_types:
        return tuple(monomorph(v, full_copy, convert_types) for v in d)
    elif isinstance(d, list) and list in convert_types:
        return [monomorph(v, full_copy, convert_types) for v in d]
    else:
        # This has to occur before the class check below
        for bt in convert_types:
            if isinstance(d, bt):
                return d if type(d) is bt else bt(d)
    if inspect.isclass(type(d)) and hasattr(d, '__dict__'):
        d_copy = deepcopy(d) if full_copy else d
        for p, v in d.__dict__.items():
            if isinstance(v, object):
                v_morph = monomorph(v, full_copy, convert_types)
                if v_morph is not v:
                    if d is d_copy:
                        d_copy = copy(d)
                    setattr(d_copy, p, v_morph)
        return d_copy
    return d.deepcopy() if full_copy else d
