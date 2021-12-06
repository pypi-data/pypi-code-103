"""NanamiLang Spec Class"""

# This file is a part of NanamiLang Project
# This project licensed under GNU GPL version 2
# Initially made by @jedi2light (aka Stoian Minaiev)

from nanamilang.shortcuts import (
    ASSERT_COLL_LENGTH_IS_EVEN,
    ASSERT_COLL_CONTAINS_ELEMENT,
    ASSERT_COLLECTION_IS_NOT_EMPTY,
    ASSERT_EVERY_COLLECTION_ITEM_IS_INSTANCE_OF
)


class Spec:
    """NanamiLang Spec"""
    ArityEven: str = 'ArityEven'
    ArityVariants: str = 'ArityVariants'
    ArityAtLeastOne: str = 'ArityAtLeastOne'
    EachArgumentTypeIs: str = 'EachArgumentTypeIs'
    EachArgumentTypeVariants: str = 'EachArgumentTypeVariants'
    ArgumentsTypeChainVariants: str = 'ArgumentsTypeChainVariants'

    @staticmethod
    def validate(label: str, collection: tuple, flags: list):
        """NanamiLang Spec.validate() function implementation"""

        for maybe_flag_pair in flags:
            if len(maybe_flag_pair) == 2:
                flag, values = maybe_flag_pair
            else:
                flag, values = maybe_flag_pair[0], None
            if flag == Spec.ArityAtLeastOne:
                ASSERT_COLLECTION_IS_NOT_EMPTY(
                    collection,
                    f'{label}: '
                    f'invalid arity, at least one form/argument expected')
            elif flag == Spec.EachArgumentTypeIs:
                desired = values[0]
                ASSERT_EVERY_COLLECTION_ITEM_IS_INSTANCE_OF(
                    collection,
                    desired, f'{label}: can only accept {desired.name} type')
            elif flag == Spec.ArityVariants:
                if len(values) == 1:
                    _ = f'{values[0]}'
                else:
                    _ = ' or '.join(map(str, values))
                ASSERT_COLL_CONTAINS_ELEMENT(
                    len(collection),
                    values,
                    f'{label}: invalid arity, form(s)/argument(s) possible: {_}')
            elif flag == Spec.ArityEven:
                ASSERT_COLL_LENGTH_IS_EVEN(
                    collection,
                    f'{label}: invalid arity, number of form(s)/argument(s) must be even')
            elif flag == Spec.EachArgumentTypeVariants:
                assert len(list(filter(lambda x: issubclass(x.__class__, tuple(values)),
                                       collection))) == len(collection), (
                    f'{label}: can only accept {" or ".join([possible.name for possible in values])} type')
            elif flag == Spec.ArgumentsTypeChainVariants:
                if collection:
                    for possible in values:
                        if len(list(filter(lambda p: issubclass(collection[p[0]].__class__, (p[1],)),
                                           enumerate(possible)))) == len(collection):
                            return
                    _ = '\n\t\t'.join([', '.join([x.name for x in chain]) for chain in values])
                    __ = ', '.join([x.name for x in collection])
                    raise AssertionError(f'{label}: function arguments types chain error:\n\tMay:\t{_}\n\tGot:\t{__}')
