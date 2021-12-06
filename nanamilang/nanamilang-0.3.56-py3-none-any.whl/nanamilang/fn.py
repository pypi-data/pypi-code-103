"""NanamiLang Fn Handler"""

# This file is a part of NanamiLang Project
# This project licensed under GNU GPL version 2
# Initially made by @jedi2light (aka Stoian Minaiev)

from copy import deepcopy

from nanamilang import datatypes
from nanamilang.spec import Spec


class Fn:
    """NanamiLang Fn Handler"""

    _environment: dict = None
    _function_name: str = None
    _recursive_evaluate_function = None
    _token_class = None
    _function_arg_names: list = None
    _function_body_token_or_form: list = None

    def __init__(self,
                 environment: dict,
                 function_name: str,
                 recursive_evaluate_function,
                 token_class,
                 function_arg_names: list,
                 function_body_token_or_form: list) -> None:
        """NanamiLang Fn Handler, initialize a new instance"""

        self._environment = deepcopy(environment)
        self._function_name = function_name
        self._recursive_evaluate_function = recursive_evaluate_function
        self._token_class = token_class
        self._function_arg_names = function_arg_names

        if not isinstance(function_body_token_or_form, list):
            self._function_body_token_or_form = [
                token_class(token_class.Identifier, 'identity'),
                deepcopy(function_body_token_or_form)
            ]
        else:
            self._function_body_token_or_form = deepcopy(function_body_token_or_form)

    def env(self) -> dict:
        """NanamiLang Fn Handler, self._environment getter"""

        return self._environment

    def generate_meta__forms(self) -> list:
        """NanamiLang Fn Handler, generate function meta data :: forms"""

        return [f'({self._function_name} {" ".join([n for n in self._function_arg_names])})']

    def handle(self, args: tuple) -> datatypes.Base:
        """NanamiLang Fn Handler, handle function evaluation"""

        Spec.validate(
            self._function_name, args, [[Spec.ArityVariants, [len(self._function_arg_names)]]]
        )

        self._environment.update({key: value for key, value in zip(self._function_arg_names, args)})

        return self._recursive_evaluate_function(self._environment, self._function_body_token_or_form)
