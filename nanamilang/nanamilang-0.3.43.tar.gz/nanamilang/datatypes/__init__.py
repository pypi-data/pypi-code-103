"""NanamiLang Data Types Package"""

# This file is a part of NanamiLang Project
# This project licensed under GNU GPL version 2
# Initially made by @jedi2light (aka Stoian Minaiev)

from typing import List
from .base import Base
from .undefined import Undefined
from .macro import Macro
from .function import Function
from .nil import Nil
from .boolean import Boolean
from .string import String
from .date import Date
from .floatnumber import FloatNumber
from .integernumber import IntegerNumber
from .keyword import Keyword
from .set import Set
from .vector import Vector
from .hashmap import HashMap


class DataType:
    """NanamiLang DataType class"""

    Undefined: dict = {'name': Undefined.name, 'class': Undefined}
    Macro: dict = {'name': Macro.name, 'class': Macro}
    Function: dict = {'name': Function.name, 'class': Function}
    Nil: dict = {'name': Nil.name, 'class': Nil}
    Boolean: dict = {'name': Boolean.name, 'class': Boolean}
    String: dict = {'name': String.name, 'class': String}
    Date: dict = {'name': Date.name, 'class': Date}
    FloatNumber: dict = {'name': FloatNumber.name, 'class': FloatNumber}
    IntegerNumber: dict = {'name': IntegerNumber.name, 'class': IntegerNumber}
    Keyword: dict = {'name': Keyword.name, 'class': Keyword}
    Set: dict = {'name': Set.name, 'class': Set}
    Vector: dict = {'name': Vector.name, 'class': Vector}
    HashMap: dict = {'name': HashMap.name, 'class': HashMap}

    complex_types: List[str] = [Set.get('name'),
                                Vector.get('name'),
                                HashMap.get('name')]
    simple_types: List[str] = [Undefined.get('name'), Macro.get('name'),
                               Function.get('name'), Nil.get('name'),
                               Boolean.get('name'), String.get('name'),
                               Date.get('name'), FloatNumber.get('name'),
                               IntegerNumber.get('name'), Keyword.get('name')]

    @staticmethod
    def resolve(data_type_class_name: str):
        """NanamiLang DataType, resolve which class is needed"""

        return DataType.__dict__.get(data_type_class_name, None).get('class', None)
