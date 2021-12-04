from typing import Dict, List, Optional, Union

from cline.exceptions import CannotMakeArguments

ArgumentsType = Dict[str, Union[bool, List[str], str, None]]


class CommandLineArguments:
    """
    Parsed command line arguments.

    Arguments:
        known:   Dictionary of known arguments.
        unknown: List of unknown arguments.
    """

    def __init__(
        self,
        known: Optional[ArgumentsType] = None,
        unknown: Optional[List[str]] = None,
    ) -> None:
        self._known = known or {}
        self._unknown = unknown or []

    def assert_string(self, arg: str, value: Union[List[str], str]) -> None:
        """
        Asserts that the argument `arg` matches the string value or is in the
        list of `value`.

        Raises:
            CannotMakeArguments: If the argument is not set or does not match.
        """

        actual = self.get_string(arg)

        if isinstance(value, str) and actual != value:
            raise CannotMakeArguments()

        if actual not in value:
            raise CannotMakeArguments()

    def assert_true(self, arg: str) -> None:
        """
        Asserts that the command line flag `arg` is truthy.

        Raises:
            CannotMakeArguments: If the argument is not a boolean or not truthy.
        """

        if not self.get_bool(arg):
            raise CannotMakeArguments()

    def get_bool(self, arg: str, default: Optional[bool] = None) -> bool:
        """
        Gets the command line argument `arg` as a boolean.

        Returns `default` if the argument is not set but `default` is.

        Raises:
            CannotMakeArguments: If the argument is not a boolean and a default
            is not set.
        """

        value = self._known.get(arg, None)

        if value is None and default is not None:
            return default
        if not isinstance(value, bool):
            raise CannotMakeArguments()
        return value

    def get_integer(self, arg: str) -> int:
        """
        Gets the command line argument `arg` as an integer.

        Raises:
            CannotMakeArguments: f the argument is not an integer.
        """

        try:
            return int(self.get_string(arg))
        except ValueError:
            raise CannotMakeArguments()

    def get_list(self, arg: str, default: Optional[List[str]] = None) -> List[str]:
        """
        Gets the command line argument `arg` as a list of strings.

        Arguments:
            arg:     Argument name
            default: Default value to return if the argument is not set.

        Raises:
            CannotMakeArguments: If neither the argument nor a default are set.

        Returns:
            Argument value if set, otherwise default if set.
        """

        value = self._known.get(arg, None)

        if value is None and default is not None:
            return default

        if not isinstance(value, list):
            raise CannotMakeArguments()

        return value

    def get_string(self, arg: str, default: Optional[str] = None) -> str:
        """
        Gets the command line argument `arg` as a string.

        Arguments:
            arg:     Argument name
            default: Default value to return if the argument is not set.

        Raises:
            CannotMakeArguments: If neither the argument nor a default are set.

        Returns:
            Argument value if set, otherwise default if set.
        """

        value = self._known.get(arg, None)

        if value is None and default is not None:
            return default

        if not isinstance(value, str):
            raise CannotMakeArguments()

        return value
