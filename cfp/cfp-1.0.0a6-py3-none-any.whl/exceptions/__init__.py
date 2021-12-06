from cfp.exceptions.no_resolver import NoResolverError
from cfp.exceptions.stack_parameters import StackParametersError


class ResolutionError(StackParametersError):
    pass


class ParameterStoreResolutionError(ResolutionError):
    pass


__all__ = [
    "NoResolverError",
    "StackParametersError",
]
