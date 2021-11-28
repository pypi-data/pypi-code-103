"""NanamiLang BuiltinMacros and BuiltinFunctions classes"""

# This file is a part of NanamiLang Project
# This project licensed under GNU GPL version 2
# Initially made by @jedi2light (aka Stoian Minaiev)

import functools
from typing import List
from functools import reduce
from nanamilang import fn
from nanamilang import datatypes
from nanamilang.spec import Spec
from nanamilang.shortcuts import randstr
from nanamilang.shortcuts import (
    ASSERT_LIST_LENGTH_IS_EVEN, ASSERT_EVERY_COLLECTION_ITEM_EQUALS_TO,
    ASSERT_DICT_CONTAINS_KEY, ASSERT_IS_INSTANCE_OF, ASSERT_NO_DUPLICATES
)


def meta(meta_: dict):
    """
    NanamiLang, apply meta data to a function
    'name': fn or macro LISP name
    'type': 'macro' or 'function'
    'forms': possible fn or macro possible forms
    'docstring': what fn or macro actually does?
    May contain 'hidden' (do not show in completions)
    May contain 'spec' attribute, but its not required

    :param meta_: a function meta data Python dictionary
    """

    def wrapped(_fn):
        @functools.wraps(_fn)
        def function(*args, **kwargs):

            spec = meta_.get('spec')
            if spec:
                Spec.validate(meta_.get('name'), list(args[0]), spec)

            return _fn(*args, **kwargs)

        ASSERT_DICT_CONTAINS_KEY('name', meta_, 'function meta data must contain a name')
        ASSERT_DICT_CONTAINS_KEY('type', meta_, 'function meta data must contain a type')
        ASSERT_DICT_CONTAINS_KEY('forms', meta_, 'function meta data must contain a forms')
        ASSERT_DICT_CONTAINS_KEY('docstring', meta_, 'function meta data must contain a docstring')

        function.meta = meta_

        return function

    return wrapped


class BuiltinMacros:
    """NanamiLang Builtin Macros"""

    ########################################################################################################

    @staticmethod
    def resolve(mc_name: str) -> dict:
        """Resolve macro by its name"""

        for macro in BuiltinMacros.functions():
            if macro.meta.get('name') == mc_name:
                return {'macro_name': mc_name, 'macro_reference': macro}

    @staticmethod
    def completions() -> list:
        """Return all possible function names (for completion)"""

        _all = BuiltinMacros.functions()

        to_completion = filter(lambda f: not f.meta.get('hidden'), _all)

        return list(map(lambda func: func.meta.get('name'), to_completion))

    @staticmethod
    def env() -> dict:
        """As 'let' env"""

        variants = [f.meta.get('name') for f in BuiltinMacros.functions()]
        return {n: datatypes.Macro(BuiltinMacros.resolve(n)) for n in variants}

    @staticmethod
    def names() -> List[str]:
        """Return all possible function names"""

        return list(filter(lambda name: '_macro' in name, BuiltinMacros().__dir__()))

    @staticmethod
    def functions() -> list:
        """Return all possible functions"""

        return list(map(lambda n: getattr(BuiltinMacros, n, None), BuiltinMacros.names()))

    ########################################################################################################

    @staticmethod
    @meta({'spec': [[Spec.ArityVariants, [3]]],
           'name': 'if',
           'type': 'macro',
           'forms': ['(if condition true-branch else-branch)'],
           'docstring': 'Return true- or else-branch depending on condition'})
    def if_macro(tree_slice: list, env: dict, ev_func, token_cls) -> list:
        """
        Builtin 'if' macro implementation

        :param tree_slice: slice of encountered tree
        :param env: current environment during evaluation
        :param ev_func: reference to recursive evaluation function
        :param token_cls: nanamilang.token.Token class
        :return: converted slice of tree (as this would be expected)
        """

        condition, true_branch, else_branch = tree_slice

        if not isinstance(condition, list):
            condition = [token_cls(token_cls.Identifier, 'identity'), condition]
        if not isinstance(true_branch, list):
            true_branch = [token_cls(token_cls.Identifier, 'identity'), true_branch]
        if not isinstance(else_branch, list):
            else_branch = [token_cls(token_cls.Identifier, 'identity'), else_branch]

        return true_branch if ev_func(env, condition).reference() is True else else_branch

    ########################################################################################################

    @staticmethod
    @meta({'spec': [[Spec.ArityAtLeastOne]],
           'name': 'comment',
           'type': 'macro',
           'forms': ['(comment ...)'],
           'docstring': 'Turn form into just nothing'})
    def comment_macro(tree_slice: list, env: dict, ev_func, token_cls) -> list:
        """
        Builtin 'comment' macro implementation

        :param tree_slice: slice of encountered tree
        :param env: current environment during evaluation
        :param ev_func: reference to recursive evaluation function
        :param token_cls: nanamilang.token.Token class
        :return: converted slice of tree (as this would be expected)
        """

        return [token_cls(token_cls.Identifier, 'identity'), token_cls(token_cls.Nil, 'nil')]

    ########################################################################################################

    @staticmethod
    @meta({'spec': [[Spec.ArityAtLeastOne]],
           'name': 'and',
           'type': 'macro',
           'forms': ['(and form1 form2 ... formN)'],
           'docstring': 'Return false if the next cond evaluates to false, otherwise true'})
    def and_macro(tree_slice: list, env: dict, ev_func, token_cls) -> list:
        """
        Builtin 'and' macro implementation

        :param tree_slice: slice of encountered tree
        :param env: current environment during evaluation
        :param ev_func: reference to recursive evaluation function
        :param token_cls: nanamilang.token.Token class
        :return: converted slice of tree (as this would be expected)
        """

        for condition in tree_slice:
            if not isinstance(condition, list):
                condition = [token_cls(token_cls.Identifier, 'identity'), condition]
            if ev_func(env, condition).reference() is False:
                return [token_cls(token_cls.Identifier, 'identity'),
                        token_cls(token_cls.Boolean, False)]
        return [token_cls(token_cls.Identifier, 'identity'), token_cls(token_cls.Boolean, True)]

    ########################################################################################################

    @staticmethod
    @meta({'spec': [[Spec.ArityAtLeastOne]],
           'name': 'or',
           'type': 'macro',
           'forms': ['(or form1 form2 ... formN)'],
           'docstring': 'Return true if the next cond evaluates to true, otherwise false'})
    def or_macro(tree_slice: list, env: dict, ev_func, token_cls) -> list:
        """
        Builtin 'or' macro implementation

        :param tree_slice: slice of encountered tree
        :param env: current environment during evaluation
        :param ev_func: reference to recursive evaluation function
        :param token_cls: nanamilang.token.Token class
        :return: converted slice of tree (as this would be expected)
        """

        for condition in tree_slice:
            if not isinstance(condition, list):
                condition = [token_cls(token_cls.Identifier, 'identity'), condition]
            if ev_func(env, condition).reference() is True:
                return [token_cls(token_cls.Identifier, 'identity'),
                        token_cls(token_cls.Boolean, True)]
        return [token_cls(token_cls.Identifier, 'identity'), token_cls(token_cls.Boolean, False)]

    ########################################################################################################

    @staticmethod
    @meta({'spec': [[Spec.ArityAtLeastOne]],
           'name': '->',
           'type': 'macro',
           'forms': ['(->  form1 form2 ... formN)'],
           'docstring': 'Allows you to simplify your form'})
    def first_threading_macro(tree_slice: list,
                              env: dict, ev_func, token_cls) -> list:
        """
        Builtin '->' macro implementation

        :param tree_slice: slice of encountered tree
        :param env: current environment during evaluation
        :param ev_func: reference to recursive evaluation function
        :param token_cls: nanamilang.token.Token class
        :return: converted slice of tree (as this would be expected)
        """

        if len(tree_slice) > 1:

            for idx, tof in enumerate(tree_slice):
                if len(tree_slice) - 1 != idx:
                    if not isinstance(tof, list):
                        tof = [token_cls(token_cls.Identifier, 'identity'), tof]
                    next_tof = tree_slice[idx + 1]
                    if not isinstance(next_tof, list):
                        tree_slice[idx + 1] = [next_tof, tof]
                    else:
                        tree_slice[idx + 1].insert(1, tof)

            return tree_slice[-1]

        else:

            return [token_cls(token_cls.Identifier, 'identity'), tree_slice[-1]]

    ########################################################################################################

    @staticmethod
    @meta({'spec': [[Spec.ArityAtLeastOne]],
           'name': '->>',
           'type': 'macro',
           'forms': ['(->> form1 form2 ... formN)'],
           'docstring': 'Allows you to simplify your form'})
    def last_threading_macro(tree_slice: list,
                             env: dict, ev_func, token_cls) -> list:
        """
        Builtin '->>' macro implementation

        :param tree_slice: slice of encountered tree
        :param env: current environment during evaluation
        :param ev_func: reference to recursive evaluation function
        :param token_cls: nanamilang.token.Token class
        :return: converted slice of tree (as this would be expected)
        """

        if len(tree_slice) > 1:

            for idx, tof in enumerate(tree_slice):
                if len(tree_slice) - 1 != idx:
                    if not isinstance(tof, list):
                        tof = [token_cls(token_cls.Identifier, 'identity'), tof]
                    next_tof = tree_slice[idx + 1]
                    if not isinstance(next_tof, list):
                        tree_slice[idx + 1] = [next_tof, tof]
                    else:
                        tree_slice[idx + 1].append(tof)

            return tree_slice[-1]

        else:

            return [token_cls(token_cls.Identifier, 'identity'), tree_slice[-1]]

    ########################################################################################################

    @staticmethod
    @meta({'spec': [[Spec.ArityVariants, [2, 3, 4]]],
           'name': 'fn',
           'type': 'macro',
           'forms': ['(fn [n ...] f)',
                     '(fn name [n ...] f)',
                     '(fn "docstring" name [n ...] f)'],
           'docstring': 'Declare your NanamiLang function'})
    def fn_macro(tree_slice: list, env: dict, ev_func, token_cls) -> list:
        """
        Builtin 'fn' macro implementation

        :param tree_slice: slice of encountered tree
        :param env: current environment during evaluation
        :param ev_func: reference to recursive evaluation function
        :param token_cls: nanamilang.token.Token class
        :return: converted slice of tree (as this would be expected)
        """

        fn_name_token, fn_docstring_token, fn_arguments_form, fn_body_token_or_form = [None] * 4
        if len(tree_slice) == 2:
            fn_arguments_form, fn_body_token_or_form = tree_slice
        elif len(tree_slice) == 3:
            fn_name_token, fn_arguments_form, fn_body_token_or_form = tree_slice
        elif len(tree_slice) == 4:
            fn_name_token, fn_docstring_token, fn_arguments_form, fn_body_token_or_form = tree_slice

        # Sadly, we can't check that fn_name_token is actually a token, not anything else

        # Sadly, we can't check that fn_docstring_token is actually a token, not anything else

        ASSERT_IS_INSTANCE_OF(fn_arguments_form, list, 'fn: arguments form needs to be a vector')

        but_first = fn_arguments_form[1:]

        ASSERT_EVERY_COLLECTION_ITEM_EQUALS_TO(
            [x.type() for x in but_first], token_cls.Identifier,
            'fn: each element of fn arguments form needs to be an Identifier')

        fn_argument_names = [t.dt().origin() for t in but_first]

        ASSERT_NO_DUPLICATES(fn_argument_names,
                             'fn: function arguments vector could not contain duplicated arg names')

        fn_name = fn_name_token.dt().origin() if fn_name_token else randstr()

        fn_handle = fn.Fn(env, fn_name, ev_func, token_cls, fn_argument_names, fn_body_token_or_form)

        fn_docstring = None
        if fn_docstring_token:
            if fn_docstring_token.type() == 'String':
                fn_docstring = fn_docstring_token.dt().reference()

        BuiltinFunctions.install(
            {
                'name': fn_name,
                'type': 'function',
                'hidden': not bool(fn_name_token),
                'forms': fn_handle.generate_meta__forms(),
                'docstring': fn_docstring or 'This function has not docstring'
            },
            lambda args: fn_handle.handle(args)
        )

        return [token_cls(token_cls.Identifier, 'identity'), token_cls(token_cls.Identifier, fn_name)]

    ########################################################################################################

    @staticmethod
    @meta({'spec': [[Spec.ArityVariants, [2]]],
           'name': 'let',
           'type': 'macro',
           'forms': ['(let [b1 v1 ...] b1)'],
           'docstring': 'Declare your local bindings and access them'})
    def let_macro(tree_slice: list, env: dict, ev_func, token_cls) -> list:
        """
        Builtin 'let' macro implementation

        :param tree_slice: slice of encountered tree
        :param env: current environment during evaluation
        :param ev_func: reference to recursive evaluation function
        :param token_cls: nanamilang.token.Token class
        :return: converted slice of tree (as this would be expected)
        """

        bindings_form, body_form = tree_slice

        but_first = bindings_form[1:]

        ASSERT_LIST_LENGTH_IS_EVEN(but_first,
                                   'let: bindings form must be even')

        partitioned = [but_first[i:i + 2] for i in range(0, len(but_first), 2)]

        for [key_token, value_token_or_form] in partitioned:
            if isinstance(key_token, token_cls) and \
                    key_token.type() == token_cls.Identifier:
                env_key = key_token.dt().origin()
            else:
                raise AssertionError(f'let: can\'t assign to: {key_token}')
            if not isinstance(value_token_or_form, list):
                value_token_or_form = [token_cls(token_cls.Identifier, 'identity'), value_token_or_form]
            env[env_key] = ev_func(env, value_token_or_form)

        return body_form if isinstance(body_form, list) else [token_cls(token_cls.Identifier, 'identity'), body_form]


class BuiltinFunctions:
    """NanamiLang Builtin Functions"""

    #################################################################################################################

    @staticmethod
    def install(fn_meta: dict, fn_callback) -> bool:
        """
        Allow others to install own functions.
        For example: let the REPL install (exit) function

        :param fn_meta: required function meta information
        :param fn_callback: installed function callback reference
        """

        reference_key = f'{fn_meta.get("name")}_func'
        maybe_existing = getattr(BuiltinFunctions, reference_key, None)
        if maybe_existing:
            delattr(BuiltinFunctions, reference_key)

        setattr(BuiltinFunctions, reference_key, fn_callback)
        getattr(BuiltinFunctions, reference_key, None).meta = fn_meta
        return True if getattr(BuiltinFunctions, reference_key, None).meta == fn_meta else False

    #################################################################################################################

    @staticmethod
    def resolve(fn_name: str) -> dict:
        """Resolve function by its name"""

        for func in BuiltinFunctions.functions():
            if func.meta.get('name') == fn_name:
                return {'function_name': fn_name, 'function_reference': func}

    @staticmethod
    def completions() -> list:
        """Return all possible function names (for completion)"""

        _all = BuiltinFunctions.functions()

        to_completion = filter(lambda f: not f.meta.get('hidden'), _all)

        return list(map(lambda func: func.meta.get('name'), to_completion))

    @staticmethod
    def env() -> dict:
        """As 'let' env"""

        variants = [f.meta.get('name') for f in BuiltinFunctions.functions()]
        return {n: datatypes.Function(BuiltinFunctions.resolve(n)) for n in variants}

    @staticmethod
    def names() -> List[str]:
        """Return all possible function names"""

        return list(filter(lambda name: '_func' in name, BuiltinFunctions().__dir__()))

    @staticmethod
    def functions() -> list:
        """Return all possible functions"""

        return list(map(lambda n: getattr(BuiltinFunctions, n, None), BuiltinFunctions.names()))

    #################################################################################################################

    @staticmethod
    @meta({'spec': [[Spec.ArityVariants, [1]],
                    [Spec.EachArgumentTypeIs, [datatypes.String]]],
           'name': 'find-mc',
           'type': 'function',
           'forms': ['(find-mc mc-name)'],
           'docstring': 'Find a Macro by its name'})
    def find_mc_func(args: List[datatypes.String]) -> datatypes.Macro or datatypes.Nil:
        """
        Builtin 'find-mc' function implementation

        :param args: incoming 'find-mc' function arguments
        :return: datatypes.Macro or datatypes.Nil
        """

        macro_name_as_string: datatypes.String = args[0]

        resolved_macro_info = BuiltinMacros.resolve(macro_name_as_string.reference())

        return datatypes.Macro(resolved_macro_info) if resolved_macro_info else datatypes.Nil('nil')

    #################################################################################################################

    @staticmethod
    @meta({'spec': [[Spec.ArityVariants, [1]],
                    [Spec.EachArgumentTypeIs, [datatypes.String]]],
           'name': 'find-fn',
           'type': 'function',
           'forms': ['(find-fn fn-name)'],
           'docstring': 'Find a Function by its name'})
    def find_fn_func(args: List[datatypes.String]) -> datatypes.Function or datatypes.Nil:
        """
        Builtin 'find-fn' function implementation

        :param args: incoming 'find-fn' function arguments
        :return: datatypes.Function or datatypes.Nil
        """

        function_name_as_string: datatypes.String = args[0]

        resolved_function_info = BuiltinFunctions.resolve(function_name_as_string.reference())

        return datatypes.Function(resolved_function_info) if resolved_function_info else datatypes.Nil('nil')

    #################################################################################################################

    @staticmethod
    @meta({'spec': [[Spec.ArityVariants, [1]],
                    [Spec.EachArgumentTypeVariants, [datatypes.Macro,
                                                     datatypes.Function]]],
           'name': 'doc',
           'type': 'function',
           'forms': ['(doc function-or-macro)'],
           'docstring': 'Function or Macro documentation'})
    def doc_func(args: List[datatypes.Function or datatypes.Macro]) -> datatypes.HashMap:
        """
        Builtin 'doc' function implementation

        :param args: incoming 'doc' function arguments
        :return: datatypes.HashMap
        """

        function_or_macro: datatypes.Function or datatypes.Macro = args[0]

        _type = function_or_macro.reference().meta.get('type')

        return BuiltinFunctions.make_hashmap_func(
            [datatypes.Keyword('forms'),
             BuiltinFunctions.make_vector_func([datatypes.String(x)
                                                for x in function_or_macro.reference().meta.get('forms')]),
             datatypes.Keyword('macro?'), datatypes.Boolean(_type == 'macro'),
             datatypes.Keyword('function?'), datatypes.Boolean(_type == 'function'),
             datatypes.Keyword('docstring'), datatypes.String(function_or_macro.reference().meta.get('docstring'))])

    #################################################################################################################

    @staticmethod
    @meta({'spec': [[Spec.ArityVariants, [2]],
                    [Spec.ArgumentsTypeChainVariants, [[datatypes.HashMap, datatypes.Base],
                                                       [datatypes.Vector, datatypes.IntegerNumber]]]],
           'name': 'get',
           'type': 'function',
           'forms': ['(get collection key-or-index)'],
           'docstring': 'A collection item by its key or index'})
    def get_func(args: List[datatypes.Base]) -> datatypes.Base:
        """
        Builtin 'get' function implementation

        :param args: incoming 'get' function arguments
        :return: datatypes.Base
        """

        collection: datatypes.Vector or datatypes.HashMap
        key_or_index: datatypes.Base

        collection, key_or_index = args

        return collection.get(key_or_index)

    #################################################################################################################

    @staticmethod
    @meta({'spec': [[Spec.ArityVariants, [2]],
                    [Spec.ArgumentsTypeChainVariants, [[datatypes.Function, datatypes.Vector]]]],
           'name': 'map',
           'type': 'function',
           'forms': ['(map function collection)'],
           'docstring': 'A Vector of mapped collection items'})
    def map_func(args: List[datatypes.Base]) -> datatypes.Vector:
        """
        Builtin 'map' function implementation

        :param args: incoming 'map' function arguments
        :return: datatypes.Vector
        """

        function: datatypes.Function
        collection: datatypes.Vector

        function, collection = args

        return datatypes.Vector(list(map(lambda e: function.reference()([e]), collection.reference())))

    #################################################################################################################

    @staticmethod
    @meta({'spec': [[Spec.ArityVariants, [2]],
                    [Spec.ArgumentsTypeChainVariants, [[datatypes.Function, datatypes.Vector]]]],
           'name': 'filter',
           'type': 'function',
           'forms': ['(filter function collection)'],
           'docstring': 'A Vector of filtered collection items'})
    def filter_func(args: List[datatypes.Base]) -> datatypes.Vector:
        """
        Builtin 'filter' function implementation

        :param args: incoming 'filter' function arguments
        :return: datatypes.Vector
        """

        function: datatypes.Function
        collection: datatypes.Vector

        function, collection = args

        return datatypes.Vector(
            list(filter(lambda e: function.reference()([e]).reference() is True, collection.reference())))

    #################################################################################################################

    @staticmethod
    @meta({'spec': [[Spec.EachArgumentTypeVariants, [datatypes.Base]]],
           'name': 'make-set',
           'type': 'function',
           'forms': ['(make-set e1 e2 ... eX)'],
           'docstring': 'Create a Set data structure'})
    def make_set_func(args: List[datatypes.Base]) -> datatypes.Set:
        """
        Builtin 'make-set' function implementation

        :param args: incoming 'make-set' function arguments
        :return: datatypes.Set
        """

        return datatypes.Set(set(args))

    #################################################################################################################

    @staticmethod
    @meta({'spec': [[Spec.EachArgumentTypeVariants, [datatypes.Base]]],
           'name': 'make-vector',
           'type': 'function',
           'forms': ['(make-vector e1 e2 ... eX)'],
           'docstring': 'Create a Vector data structure'})
    def make_vector_func(args: List[datatypes.Base]) -> datatypes.Vector:
        """
        Builtin 'make-vector' function implementation

        :param args: incoming 'make-vector' function arguments
        :return: datatypes.Vector
        """

        return datatypes.Vector(list(args))

    #################################################################################################################

    @staticmethod
    @meta({'spec': [[Spec.ArityEven],
                    [Spec.EachArgumentTypeVariants, [datatypes.Base]]],
           'name': 'make-hashmap',
           'type': 'function',
           'forms': ['(make-hashmap k1 v2 ... kX vX)'],
           'docstring': 'Create a HashMap data structure'})
    def make_hashmap_func(args: List[datatypes.Base]) -> datatypes.HashMap:
        """
        Builtin 'make-hashmap' function implementation

        :param args: incoming 'make-hashmap' function arguments
        :return: datatypes.HashMap
        """

        return datatypes.HashMap(dict({k: v for [k, v] in [args[i:i + 2] for i in range(0, len(args), 2)]}))

    #################################################################################################################

    @staticmethod
    @meta({'spec': [[Spec.ArityVariants, [1]],
                    [Spec.EachArgumentTypeVariants, [datatypes.IntegerNumber,
                                                     datatypes.FloatNumber]]],
           'name': 'inc',
           'type': 'function',
           'forms': ['(inc number)'],
           'docstring': 'Return incremented number'})
    def inc_func(args: (List[datatypes.IntegerNumber]
                        or List[datatypes.FloatNumber])) -> (datatypes.IntegerNumber
                                                             or datatypes.FloatNumber):
        """
        Builtin 'inc' function implementation

        :param args: incoming 'inc' function arguments
        :return: datatypes.IntegerNumber or datatypes.FloatNumber
        """

        number: (datatypes.IntegerNumber or datatypes.FloatNumber) = args[0]

        return datatypes.IntegerNumber(number.reference() + 1) if \
            isinstance(number, datatypes.IntegerNumber) else datatypes.FloatNumber(number.reference() + 1)

    #################################################################################################################

    @staticmethod
    @meta({'spec': [[Spec.ArityVariants, [1]],
                    [Spec.EachArgumentTypeVariants, [datatypes.IntegerNumber,
                                                     datatypes.FloatNumber]]],
           'name': 'dec',
           'type': 'function',
           'forms': ['(dec number)'],
           'docstring': 'Return decremented number'})
    def dec_func(args: (List[datatypes.IntegerNumber]
                        or List[datatypes.FloatNumber])) -> (datatypes.IntegerNumber
                                                             or datatypes.FloatNumber):
        """
        Builtin 'dec' function implementation

        :param args: incoming 'dec' function arguments
        :return: datatypes.IntegerNumber or datatypes.FloatNumber
        """

        number: (datatypes.IntegerNumber or datatypes.FloatNumber) = args[0]

        return datatypes.IntegerNumber(number.reference() - 1) if \
            isinstance(number, datatypes.IntegerNumber) else datatypes.FloatNumber(number.reference() - 1)

    #################################################################################################################

    @staticmethod
    @meta({'spec': [[Spec.ArityVariants, [1]],
                    [Spec.EachArgumentTypeIs, [datatypes.Base]]],
           'name': 'identity',
           'type': 'function',
           'forms': ['(identity something)'],
           'docstring': 'Just return a something'})
    def identity_func(args: List[datatypes.Base]) -> datatypes.Base:
        """
        Builtin 'identity' function implementation

        :param args: incoming 'identity' function arguments
        :return: datatypes.Base
        """

        something: datatypes.Base = args[0]

        return something

    #################################################################################################################

    @staticmethod
    @meta({'spec': [[Spec.ArityVariants, [1]],
                    [Spec.EachArgumentTypeIs, [datatypes.Base]]],
           'name': 'type',
           'type': 'function',
           'forms': ['(type something)'],
           'docstring': 'Just return something type name'})
    def type_func(args: List[datatypes.Base]) -> datatypes.String:
        """
        Builtin 'type' function implementation

        :param args: incoming 'type' function arguments
        :return: datatypes.String
        """

        something: datatypes.Base = args[0]

        return datatypes.String(something.name)

    #################################################################################################################

    @staticmethod
    @meta({'spec': [[Spec.ArityVariants, [2]],
                    [Spec.EachArgumentTypeIs, [datatypes.Base]]],
           'name': '=',
           'type': 'function',
           'forms': ['(= f s)'],
           'docstring': 'Whether f equals to s or not'})
    def eq_func(args: List[datatypes.Base]) -> datatypes.Boolean:
        """
        Builtin '=' function implementation

        :param args: incoming '=' function arguments
        :return: datatypes.Boolean
        """

        # TODO: maybe refactor this function to support more than two arguments and use overloaded operators

        f: datatypes.Base
        s: datatypes.Base
        f, s = args

        return datatypes.Boolean(f.reference() == s.reference())

    #################################################################################################################

    @staticmethod
    @meta({'spec': [[Spec.ArityVariants, [2]],
                    [Spec.EachArgumentTypeVariants, [datatypes.IntegerNumber,
                                                     datatypes.FloatNumber]]],
           'name': '<',
           'type': 'function',
           'forms': ['(< f s)'],
           'docstring': 'Whether f lower than s or not'})
    def lower_than_func(args: (List[datatypes.IntegerNumber]
                               or List[datatypes.FloatNumber])) -> datatypes.Boolean:
        """
        Builtin '<' function implementation

        :param args: incoming '<' function arguments
        :return: datatypes.Boolean
        """

        # TODO: maybe refactor this function to support more than two arguments and use overloaded operators

        f: datatypes.IntegerNumber or datatypes.FloatNumber
        s: datatypes.IntegerNumber or datatypes.FloatNumber
        f, s = args

        return datatypes.Boolean(f.reference() < s.reference())

    #################################################################################################################

    @staticmethod
    @meta({'spec': [[Spec.ArityVariants, [2]],
                    [Spec.EachArgumentTypeVariants, [datatypes.IntegerNumber,
                                                     datatypes.FloatNumber]]],
           'name': '>',
           'type': 'function',
           'forms': ['(> f s)'],
           'docstring': 'Whether f greater than s or not'})
    def greater_than_func(args: (List[datatypes.IntegerNumber]
                                 or List[datatypes.FloatNumber])) -> datatypes.Boolean:
        """
        Builtin '>' function implementation

        :param args: incoming '>' function arguments
        :return: datatypes.Boolean
        """

        # TODO: maybe refactor this function to support more than two arguments and use overloaded operators

        f: datatypes.IntegerNumber or datatypes.FloatNumber
        s: datatypes.IntegerNumber or datatypes.FloatNumber
        f, s = args

        return datatypes.Boolean(f.reference() > s.reference())

    #################################################################################################################

    @staticmethod
    @meta({'spec': [[Spec.ArityVariants, [2]],
                    [Spec.EachArgumentTypeVariants, [datatypes.IntegerNumber,
                                                     datatypes.FloatNumber]]],
           'name': '<=',
           'type': 'function',
           'forms': ['(<= f s)'],
           'docstring': 'Whether f lower than or equals to s or not'})
    def lower_than_eq_func(args: (List[datatypes.IntegerNumber]
                                  or List[datatypes.FloatNumber])) -> datatypes.Boolean:
        """
        Builtin '<=' function implementation

        :param args: incoming '>=' function arguments
        :return: datatypes.Boolean
        """

        # TODO: maybe refactor this function to support more than two arguments and use overloaded operators

        f: datatypes.IntegerNumber or datatypes.FloatNumber
        s: datatypes.IntegerNumber or datatypes.FloatNumber
        f, s = args

        return datatypes.Boolean(f.reference() <= s.reference())

    #################################################################################################################

    @staticmethod
    @meta({'spec': [[Spec.ArityVariants, [2]],
                    [Spec.EachArgumentTypeVariants, [datatypes.IntegerNumber,
                                                     datatypes.FloatNumber]]],
           'name': '>=',
           'type': 'function',
           'forms': ['(>= f s)'],
           'docstring': 'Whether f greater than or equals to s or not'})
    def greater_than_eq_func(args: (List[datatypes.IntegerNumber]
                                    or List[datatypes.FloatNumber])) -> datatypes.Boolean:
        """
        Builtin '>=' function implementation

        :param args: incoming '>=' function arguments
        :return: datatypes.Boolean
        """

        # TODO: maybe refactor this function to support more than two arguments and use overloaded operators

        f: datatypes.IntegerNumber or datatypes.FloatNumber
        f: datatypes.IntegerNumber or datatypes.FloatNumber
        f, s = args

        return datatypes.Boolean(f.reference() >= s.reference())

    #################################################################################################################

    @staticmethod
    @meta({'spec': [[Spec.ArityAtLeastOne],
                    [Spec.EachArgumentTypeVariants, [datatypes.IntegerNumber,
                                                     datatypes.FloatNumber]]],
           'name': '+',
           'type': 'function',
           'forms': ['(+ n1 n2 ... nX)'],
           'docstring': 'All passed numbers summary'})
    def plus_func(args: (List[datatypes.IntegerNumber]
                         or List[datatypes.FloatNumber])) -> (datatypes.IntegerNumber
                                                              or datatypes.FloatNumber):
        """
        Builtin '+' function implementation

        :param args: incoming '+' function arguments
        :return: datatypes.IntegerNumber or datatypes.FloatNumber
        """

        result = reduce(lambda _, x: _ + x, list(map(lambda n: n.reference(), args)))

        return datatypes.IntegerNumber(result) if isinstance(result, int) else datatypes.FloatNumber(result)

    #################################################################################################################

    @staticmethod
    @meta({'spec': [[Spec.ArityAtLeastOne],
                    [Spec.EachArgumentTypeVariants, [datatypes.IntegerNumber,
                                                     datatypes.FloatNumber]]],
           'name': '-',
           'type': 'function',
           'forms': ['(- n1 n2 ... nX)'],
           'docstring': 'All passed numbers subtraction'})
    def minus_func(args: (List[datatypes.IntegerNumber]
                          or List[datatypes.FloatNumber])) -> (datatypes.IntegerNumber
                                                               or datatypes.FloatNumber):
        """
        Builtin '-' function implementation

        :param args: incoming '-' function arguments
        :return: datatypes.IntegerNumber or datatypes.FloatNumber
        """

        result = reduce(lambda _, x: _ - x, list(map(lambda n: n.reference(), args)))

        return datatypes.IntegerNumber(result) if isinstance(result, int) else datatypes.FloatNumber(result)

    #################################################################################################################

    @staticmethod
    @meta({'spec': [[Spec.ArityAtLeastOne],
                    [Spec.EachArgumentTypeVariants, [datatypes.IntegerNumber,
                                                     datatypes.FloatNumber]]],
           'name': '/',
           'type': 'function',
           'forms': ['(/ n1 n2 ... nX)'],
           'docstring': 'All passed numbers division'})
    def divide_func(args: (List[datatypes.IntegerNumber]
                           or List[datatypes.FloatNumber])) -> (datatypes.IntegerNumber
                                                                or datatypes.FloatNumber):
        """
        Builtin '/' function implementation

        :param args: incoming '/' function arguments
        :return: datatypes.IntegerNumber or datatypes.FloatNumber
        """

        result = reduce(lambda _, x: _ / x, list(map(lambda n: n.reference(), args)))

        return datatypes.IntegerNumber(result) if isinstance(result, int) else datatypes.FloatNumber(result)

    #################################################################################################################

    @staticmethod
    @meta({'spec': [[Spec.ArityAtLeastOne],
                    [Spec.EachArgumentTypeVariants, [datatypes.IntegerNumber,
                                                     datatypes.FloatNumber]]],
           'name': '*',
           'type': 'function',
           'forms': ['(* n1 n2 ... nX)'],
           'docstring': 'All passed numbers production'})
    def multiply_func(args: (List[datatypes.IntegerNumber]
                             or List[datatypes.FloatNumber])) -> (datatypes.IntegerNumber
                                                                  or datatypes.FloatNumber):
        """
        Builtin '*' function implementation

        :param args: incoming '*' function arguments
        :return: datatypes.IntegerNumber or datatypes.FloatNumber
        """

        result = reduce(lambda _, x: _ * x, list(map(lambda n: n.reference(), args)))

        return datatypes.IntegerNumber(result) if isinstance(result, int) else datatypes.FloatNumber(result)

    #################################################################################################################

    @staticmethod
    @meta({'spec': [[Spec.ArityAtLeastOne],
                    [Spec.EachArgumentTypeVariants, [datatypes.IntegerNumber,
                                                     datatypes.FloatNumber]]],
           'name': 'mod',
           'type': 'function',
           'forms': ['(mod n1 n2 ... nX)'],
           'docstring': 'All passed numbers modification'})
    def mod_func(args: (List[datatypes.IntegerNumber]
                        or List[datatypes.FloatNumber])) -> (datatypes.IntegerNumber
                                                             or datatypes.FloatNumber):
        """
        Builtin 'mod' function implementation

        :param args: incoming 'mod' function arguments
        :return: datatypes.IntegerNumber or datatypes.FloatNumber
        """

        result = reduce(lambda _, x: _ % x, list(map(lambda n: n.reference(), args)))

        return datatypes.IntegerNumber(result) if isinstance(result, int) else datatypes.FloatNumber(result)

    #################################################################################################################
