#!/usr/bin/env python3

"""
** Lists the atomic functions that serialize each case separately. **
---------------------------------------------------------------------

The main serialization function ``raisin.serialization.serialize``,
looks at the nature of the object to serialize.
It applies the appropriate function by picking it up here.
It is also here that the deserialization function
``raisin.serialization.deserialize`` will draw the right function.
"""

import inspect

from raisin.serialization.atoms import small
from raisin.serialization.atoms import dumps

__all__ = ['SERIALIZE_TABLE', 'DESERIALIZE_TABLE']

modules = (small, dumps)

SERIALIZE_TABLE = {
    func_name[10:]: func
    for module in modules
    for func_name, func in inspect.getmembers(module)
    if func_name.startswith('serialize_')
}

DESERIALIZE_TABLE = {
    func_name[12:]: func
    for module in modules
    for func_name, func in inspect.getmembers(module)
    if func_name.startswith('deserialize_')
}
