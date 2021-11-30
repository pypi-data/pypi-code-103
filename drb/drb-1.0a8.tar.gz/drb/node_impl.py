import abc
from typing import Any


class NodeImpl(abc.ABC):
    """
    This class adds functions allowing to use a specific implementation of a
    node.
    """

    @abc.abstractmethod
    def has_impl(self, impl: type) -> bool:
        """
        Tests if a specific interface can be provided. This operations tests
        with a minimum of time and memory consumption if the current
        implementation can provide a specific interface. It important to
        consider that has_impl() provides information about the ability to
        provide such interface in general cases but not focused on the current
        instance. It may therefore be impossible to get a specific
        implementation from a node whereas has_impl() operation returns true.
        :param impl: the implementation type expected
        :type impl: type
        :return: True if an implementation of the interface can be provided
        and False otherwise.
        :rtype: bool
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_impl(self, impl: type) -> Any:
        """
        This operation returns a reference to an object implementing a
        specific interface. This method authorizes a specific and/or direct
        API instead of using the DrbNode interface. The provided object is
        independent from this node and shall be released/closed by the caller
        when interface requires such finally operations.
        :param impl: the implementation type expected
        :type impl: type
        :return: the expected implementation.
        :rtype: Any
        :raises: DrbNotImplementedException
        """
        raise NotImplementedError
