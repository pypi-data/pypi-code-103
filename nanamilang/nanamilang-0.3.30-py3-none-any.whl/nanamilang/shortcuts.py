"""NanamiLang Shortcuts"""

# This file is a part of NanamiLang Project
# This project licensed under GNU GPL version 2
# Initially made by @jedi2light (aka Stoian Minaiev)

import string
import random
from typing import Any


def randstr(length: int = 10) -> str:
    """Return randomly generated string"""

    return ''.join(random.choice(string.ascii_lowercase) for _ in range(length))


def identity(something):
    """Why Python does not contain this simplest ever builtin function?"""

    return something


# LIST LENGTH ASSERTIONS ##################################################################


def ASSERT_LIST_LENGTH_IS(lst: list, length: int, message: str = '') -> None:
    """ASSERT_LIST_LENGTH_IS: whether list length equals desired or not?"""
    assert isinstance(lst, list), 'ASSERT_LIST_LENGTH_IS: not a list'
    assert len(lst) == length, message or f'list length must be {length}'


def ASSERT_LIST_LENGTH_IS_EVEN(lst: list, message: str = '') -> None:
    """ASSERT_LIST_LENGTH_IS_EVEN: whether list length is even or not?"""
    assert isinstance(lst, list), 'ASSERT_LIST_LENGTH_IS_EVEN: not a list'
    assert len(lst) % 2 == 0, message or 'list length must be even'


# COLLECTION EMPTINESS ####################################################################


def ASSERT_COLLECTION_IS_NOT_EMPTY(collection: Any, message: str = '') -> None:
    """ASSERT_COLLECTION_IS_NOT_EMPTY: whether collection (or string) empty or not?"""
    assert hasattr(collection, '__len__'), 'ASSERT_COLLECTION_IS_NOT_EMPTY: has no __len__'
    assert len(collection) > 0,  message or 'collection (or string) could not be empty'


# IN ######################################################################################


def ASSERT_DICT_CONTAINS_KEY(key: Any, dct: dict, message: str = '') -> None:
    """ASSERT_DICT_CONTAINS_KEY: does the dict keys contain key?"""
    assert isinstance(dct, dict), 'ASSERT_DICT_CONTAINS_KEY: not a dict'
    assert key in dct.keys(), message or f'dictionary does not contain "{key}" key'


def ASSERT_LIST_CONTAINS_ELEMENT(elem: Any, lst: list, message: str = '') -> None:
    """ASSERT_LIST_CONTAINS_ELEMENT: does the list contain element?"""
    assert isinstance(lst, list), 'ASSERT_LIST_CONTAINS_ELEMENT: not a list'
    assert elem in lst, message or f'list does not contain "{elem}", valid values: "{lst}"'


# DATA CONSISTENCY ########################################################################


def ASSERT_NO_DUPLICATES(lst: list, message: str = '') -> None:
    """ASSERT_NO_DUPLICATES: does the list contain duplicates?"""
    assert isinstance(lst, list), 'ASSERT_NO_DUPLICATES: not a list'
    assert len(lst) == len(set(lst)), message or 'list could not contain duplicates'


# TYPE CHECK ##############################################################################


def ASSERT_IS_INSTANCE_OF(inst: Any, _type: Any, message: str = '') -> None:
    """ASSERT_IS_INSTANCE_OF: whether given instance is actually instance of ...?"""
    assert isinstance(inst, _type), message or f'must be an instance of {_type.__name__}"'


def ASSERT_IS_CHILD_OF(inst: Any, _type: Any, message: str = '') -> None:
    """ASSERT_IS_CHILD_OF: whether given instance is actually child of ...?"""
    assert issubclass(inst.__class__, (_type,)), message or f'must be an child of {_type.__name__}"'


def ASSERT_EVERY_COLLECTION_ITEM_IS_INSTANCE_OF(lst: list,
                                                _type: Any, message: str = '') -> None:
    """ASSERT_EVERY_COLLECTION_ITEM_IS_INSTANCE_OF: whether all list instances the same?"""
    assert isinstance(lst, list), 'ASSERT_EVERY_COLLECTION_ITEM_IS_INSTANCE_OF: not a list'
    assert len(list(filter(lambda x: isinstance(x, _type), lst))) == len(lst), message or (
        f'every collection item must be an instance of {_type.__name__}'
    )


def ASSERT_EVERY_COLLECTION_ITEM_IS_CHILD_OF(lst: list,
                                             _type: Any, message: str = '') -> None:
    """ASSERT_EVERY_COLLECTION_ITEM_IS_CHILD_OF: whether all list instances the same?"""
    assert isinstance(lst, list), 'ASSERT_EVERY_COLLECTION_ITEM_IS_CHILD_OF: not a list'
    assert len(list(filter(lambda x: issubclass(x.__class__, (_type,)), lst))) == len(lst), message or (
        f'every collection item must be an instance of {_type.__name__}'
    )


def ASSERT_EVERY_COLLECTION_ITEM_EQUALS_TO(lst: list,
                                           _to: Any, message: str = '') -> None:
    """ASSERT_EVERY_COLLECTION_ITEM_EQUALS_TO: whether all list instances the same?"""
    assert isinstance(lst, list), 'ASSERT_EVERY_COLLECTION_ITEM_EQUALS_TO: not a list'
    assert len(list(filter(lambda x: x == _to, lst))) == len(lst), message or (
        f'every collection item must be equal to a {_to.__name__}, but it does not'
    )

# TOKENIZER SPECIAL #######################################################################


def UNTERMINATED_SYMBOL(sym: str, m: str = ''):
    """UNTERMINATED_SYMBOL(sym) -> message"""
    return m or f'Encountered an unterminated \'{sym}\' symbol'


def UNTERMINATED_SYMBOL_AT_EOF(sym: str, m: str = ''):
    """UNTERMINATED_SYMBOL_AT_EOF(sym) -> message"""
    return m or f'Encountered an unterminated symbol \'{sym}\' symbol at the end of file'


###########################################################################################
