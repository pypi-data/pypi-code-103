from cfp.exceptions.stack_parameters import StackParametersError
from cfp.sources import AnySource


class NoResolverError(StackParametersError):
    def __init__(self, source: AnySource) -> None:
        super().__init__(f"no resolver for {repr(source)}")
