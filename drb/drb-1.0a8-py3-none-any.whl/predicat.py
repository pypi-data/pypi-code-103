import abc


class Predicate(abc.ABC):
    @abc.abstractmethod
    def matches(self, key) -> bool:
        raise NotImplementedError
