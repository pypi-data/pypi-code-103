"""NanamiLang Fn Handler"""

# This file is a part of NanamiLang Project
# This project licensed under GNU GPL version 2
# Initially made by @jedi2light (aka Stoian Minaiev)

# TODO: pretty unstable implementation, just want to play around

from copy import deepcopy
from functools import reduce
from nanamilang import datatypes
from nanamilang.spec import Spec


class Fn:
    """NanamiLang Fn Handler"""

    _env = None
    _fn_name = None
    _ev_func = None
    _token_cls = None
    _fn_arg_names: list = None
    _fn_body_form: list = None

    def __init__(self,
                 env,
                 fn_name,
                 ev_func,
                 token_cls,
                 fn_arg_names: list,
                 fn_body_token_or_form: list) -> None:
        """NanamiLang Fn Handler, initialize a new instance"""

        self._env = env
        self._fn_name = fn_name
        self._ev_func = ev_func
        self._token_cls = token_cls
        self._fn_arg_names = fn_arg_names

        self._fn_body_form = [
            token_cls(token_cls.Identifier, 'identity'),
            deepcopy(fn_body_token_or_form)
        ] if not isinstance(fn_body_token_or_form, list) else deepcopy(fn_body_token_or_form)

    def generate_meta__forms(self) -> list:
        """NanamiLang Fn Handler, generate that list of string"""

        # TODO: currently, we do not support more than ONE form, but...

        return [f'({self._fn_name} {" ".join([n for n in self._fn_arg_names])})']

    def _form_for_arg(self, dt_instance: datatypes.Base) -> list:
        """NanamiLang Fn Handler, convert dt instance to a form"""

        if isinstance(dt_instance, datatypes.Nil) \
                or isinstance(dt_instance, datatypes.Undefined):
            return [self._token_cls(dt_instance.name, dt_instance.origin())]
        elif isinstance(dt_instance, datatypes.Macro) \
                or isinstance(dt_instance, datatypes.Function):
            return [self._token_cls('Identifier', dt_instance.format())]
        elif isinstance(dt_instance, datatypes.Set) \
                or isinstance(dt_instance, datatypes.Vector) \
                or isinstance(dt_instance, datatypes.HashMap):
            return self._form_for_complex(dt_instance)
        else:
            return [self._token_cls(dt_instance.name, dt_instance.reference())]

    def _form_for_complex(self, dt_instance: (datatypes.Set or
                                              datatypes.Vector or
                                              datatypes.HashMap)) -> list:
        """NanamiLang Fn Handler, convert complex dt instance to a form"""

        def recursively(dt, dt_items) -> list:
            tokens_for_items = []
            for x in dt_items:
                if x.name not in ['Set', 'Vector', 'HashMap']:
                    tokens_for_items.append(self._token_cls(x.name,
                                                            x.reference()))
                else:
                    tokens_for_items.append(recursively(x, x.reference_as_list()))
            return [self._token_cls('Identifier', f'make-{dt.name.lower()}')] + tokens_for_items

        return recursively(dt_instance, dt_instance.reference_as_list())

    def handle(self, args: list) -> datatypes.Base:
        """NanamiLang Fn Handler, handle function evaluation"""

        Spec.validate(self._fn_name, list(args), [[Spec.ArityVariants, [len(self._fn_arg_names)]]])

        copied_body_form = deepcopy(self._fn_body_form)

        arg_values_as_tokens = []
        for arg in args:
            form = self._form_for_arg(arg)
            if len(form) > 1:
                arg_values_as_tokens.append(form)
            else:
                arg_values_as_tokens.append(form[0])

        arg_names_as_tokens = [self._token_cls(self._token_cls.Identifier, x) for x in self._fn_arg_names]

        if self._fn_arg_names:
            let_bindings_form = list(reduce(lambda e, n: e + n, zip(arg_names_as_tokens, arg_values_as_tokens)))
        else:
            let_bindings_form = []

        return self._ev_func(
            self._env,
            [self._token_cls(self._token_cls.Identifier, 'let'),
             [self._token_cls(self._token_cls.Identifier, 'make-vector')] + let_bindings_form, copied_body_form])
