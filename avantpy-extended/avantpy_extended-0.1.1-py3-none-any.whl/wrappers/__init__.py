from contextlib import contextmanager
from ._translated import TranslatedClass


# https://gist.github.com/pysquared/1927707
from ctypes import pythonapi, POINTER, py_object
get_type_dict_ptr = pythonapi._PyObject_GetDictPtr
get_type_dict_ptr.restype = POINTER(py_object)
get_type_dict_ptr.argtypes = [py_object]

def get_type_dict_of(ob):
    dict_ptr = get_type_dict_ptr(ob)
    if dict_ptr and dict_ptr.contents:
        return dict_ptr.contents.value

def remap_type(typ, typ_map):
    typ_dict = get_type_dict_of(typ)
    for k, v in typ_map.items():
        typ_dict[v] = typ_dict[k]

STR_MAP = {
    'strip': 'lomadh',
    'join': 'comhcheanglaíodh'
}
LIST_MAP = {
    'append': 'iarcheanglaíodh',
    'remove': 'baineadh'
}

remap_type(str, STR_MAP)
remap_type(list, LIST_MAP)

OPEN_MAP = {
    'readlines': 'léadhlínte'
}

open_orig = open
@contextmanager
def open_tr(*args, **kwargs):
    fh = TranslatedClass(open_orig, OPEN_MAP, *args, soft=True, **kwargs)
    yield fh
    fh.close()

__builtins__['open'] = open_tr
