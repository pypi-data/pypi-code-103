"""NanamiLang Spec Class"""

# This file is a part of NanamiLang Project
# This project licensed under GNU GPL version 2
# Initially made by @jedi2light (aka Stoian Minaiev)

from nanamilang.shortcuts import (
    ASSERT_LIST_LENGTH_IS_EVEN, identity,
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
    def validate(label: str, collection: list, flags: list):
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
                    f'invalid arity, expected at least one form/argument'
                )
            elif flag == Spec.ArityVariants:
                assert len(collection) in values, (
                    f'{label}: '
                    f'invalid arity, form(s)/argument(s) possible: {values}'
                )
            elif flag == Spec.EachArgumentTypeIs:
                desired = values[0]
                ASSERT_EVERY_COLLECTION_ITEM_IS_INSTANCE_OF(
                    collection, desired,
                    f'{label}: '
                    f'each function argument needs to be a type of {desired}'
                )
            elif flag == Spec.ArityEven:
                ASSERT_LIST_LENGTH_IS_EVEN(
                    collection,
                    f'{label}: invalid arity, number of function arguments must be even')
            elif flag == Spec.ArgumentsTypeChainVariants:
                if collection:
                    for possible in values:
                        trues = []
                        for idx, dt in enumerate(possible):
                            trues.append(issubclass(collection[idx].__class__, (dt,)))
                        if len(list(filter(identity, trues))) == len(collection):
                            return
                    _ = [[x.name for x in chain] for chain in values]
                    __ = [x.name for x in collection]
                    raise AssertionError(f'{label}: unexpected args type chain, may: {_}, got: {__}')
            elif flag == Spec.EachArgumentTypeVariants:
                assert len(list(filter(lambda x: issubclass(x.__class__, tuple(values)),
                                       collection))) == len(collection), (
                    f'{label}: possible function argument types {[possible.name for possible in values]}')
