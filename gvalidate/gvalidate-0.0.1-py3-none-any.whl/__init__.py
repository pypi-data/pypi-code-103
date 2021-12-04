"""
Argument validation for Python functions using decorators.

The package `generic_validation`provides the
following modules:

- generic: Module containing the generic function [`validate`][validate].
- numerical
- callable
- string

[validate]:
https://gvalidate.simphotonics.com/reference/gvalidate/validators/#validate

"""
from .generic import validate
from .callable import validate_callable
from .numerical import validate_in_interval, validate_positive
from .string import validate_non_whitespace
