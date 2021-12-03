from abc import ABC, abstractmethod
from ..Phase import Phase
from ..decorator.Decorator import Decorator


class Publisher(Decorator):
    """
    A publisher is a specific abstract decorater that is expected to publish some results to a specific platform.
    The Decorator.filter method can be used to specify the phases that produce to be published data.
    """
    def after(self, phase: Phase):
        self.publish(phase)

    def publish(self, phase: Phase):
        """the actual publish method that needs to be overwritten
        """
        pass
