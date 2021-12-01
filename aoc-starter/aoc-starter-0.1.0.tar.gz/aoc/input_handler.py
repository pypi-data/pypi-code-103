from typing import Any
from typing import Callable
from typing import Optional


class InputHandler:
    """Class to reformat and mutate input data"""

    def __init__(self, input_data: list[str]):
        self.__content = [x.strip() for x in input_data]

    @property
    def content(self) -> list[str]:
        return self.__content

    def as_list(
        self,
        mutate: Optional[Callable[[str, Any], Any]] = None,
        **kwargs: Optional[Any]
    ) -> list[Any]:
        """Mutate each element in the input list

        Parameters
        ----------
        mutate : Optional[Callable], optional
            A function to apply to each element, by default None

        Returns
        -------
        list[Any]
            The mutated data
        """
        if not mutate:
            mutate = str.strip

        return [mutate(x, **kwargs) for x in self.content]  # type: ignore

    def reformat(
        self, formater: Callable[[list[str], Any], list[str]], **kwargs: Optional[Any]
    ) -> None:
        """Change the format of the input data

        You might want to do this if the original list of strings from the input data
        doesn't lend itself to the desired format. For example, if the input data is has groups
        of lines that should be together, but are seperated by newlines, you can reformat the data
        to make each group a single element in the list.

        See `aoc.reformaters`

        Parameters
        ----------
        formater : Callable
            A function that takes a list of strings and returns a new list of strings.
        """
        if self.__content:
            self.__content = formater(self.content, **kwargs)  # type: ignore
