from .equation import ReducedEquation


class ReducedEquationSolver(object):
    """An abstract base class that represents a reduced equation solver."""

    def __init__(self, eq, parameters=None):
        if parameters is None:
            parameters = {}
        self.__check_arguments(eq, parameters)

        #: eq: an ReducedEquation instance.
        self.eq = eq

        #: parameters: a dictionary of parameters.
        self.parameters = parameters

    def __check_arguments(self, eq, parameters):
        if not isinstance(eq, ReducedEquation):
            raise TypeError("eq should be a ReducedEquation.")

    def solve(self, *args, **kwargs):
        raise NotImplementedError("This class is abstract.")
