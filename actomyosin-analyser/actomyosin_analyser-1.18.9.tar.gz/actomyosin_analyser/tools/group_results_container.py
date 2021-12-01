from typing import Generic, TypeVar, Dict

from actomyosin_analyser.tools.experiment_iterator import GroupIterator

T = TypeVar('T')


class GroupResultsContainer(Generic[T]):
    """
    Container to store results for groups (see GroupIterator class).
    Results can be accessed via ``GroupIterator`` instances, e.g.
    ``value = container[group]``, where ``container`` is an instance
    of ``GroupResultsContainer``.
    """

    def __init__(self) -> None:
        self.items: Dict[str, T] = {}

    def __setitem__(self, group: GroupIterator, value: T):
        key = group.get_label_from_values()
        if key in self.items:
            raise KeyError(f"Results for group with label {key} are already"
                           "in present int he container.")
        self.items[key] = value

    def __getitem__(self, group: GroupIterator) -> T:
        key = group.get_label_from_values()
        if key not in self.items:
            raise KeyError(f"No results for group with label {key} found.")
        return self.items[key]
