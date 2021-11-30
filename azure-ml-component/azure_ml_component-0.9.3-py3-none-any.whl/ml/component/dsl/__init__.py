# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""The package dsl (domain-specific language) is a set of decorators for component manipulations.

You can utilize this package to build :class:`azure.ml.component.Component` and
:class:`azure.ml.component.Pipeline`.
"""

from ._component import _component
from ._generate_package import _generate_package as generate_package
from ._pipeline import pipeline
from .types import _parameter_group as parameter_group

__all__ = [
    '_component',
    'generate_package',
    'parameter_group',
    'pipeline',
]
