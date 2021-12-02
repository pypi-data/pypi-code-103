"""A Python implementation of the EMuLSion framework.

(Epidemiologic MUlti-Level SImulatiONs).

Classes and functions for process management in
MultiProcessCompartments.

"""

from   abc                     import abstractmethod


class AbstractProcess(object):
    """An AbstractProcess is aimed at controlling a specific activity
    in a compartment, and is identified by its name.

    """
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return 'Process "{}"'.format(self.name)

    __str__ = __repr__

    @abstractmethod
    def evolve(self):
        """Define the actions that the process must perform."""
        pass


class MethodProcess(AbstractProcess):
    """A MethodProcess is aimed at running a specific method (and
    possibly any function or even any callable object).

    """
    def __init__(self, name, method, lparams=[], dparams={}):
        super().__init__(name)
        self.method = method
        self.lparams = lparams
        self.dparams = dparams

    def evolve(self):
        """Define the actions that the process must perform. In a
        MethodProcess, those actions consist in running the method of
        the target compartment.

        """
        self.method(*self.lparams, **self.dparams)

