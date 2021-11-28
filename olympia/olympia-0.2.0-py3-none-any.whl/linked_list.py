"""An implementation of a Node and a Linked List data structure."""

from typing import Any, Iterator, List, Optional


class Node:
    """A Node data structure.

    Attributes:
        data: The data stored in the node.
        next: A pointer to the next node.
    """

    def __init__(self, data: Any) -> None:
        """Initialises a Node."""
        self.data: Any = data
        self.next: Optional[Node] = None

    def __repr__(self) -> str:
        """Returns a string representation of a Node."""
        return str(self.data)


class LinkedList:
    """A Linked List data structure.

    Attributes:
        head: A pointer to the first node in the linked list.
    """

    def __init__(self) -> None:
        """Initialises a Linked List."""
        self.head: Optional[Node] = None

    def __repr__(self) -> str:
        """Returns a string representation of a Linked List."""
        current = self.head
        nodes: List[str] = []
        while current:
            nodes.append(str(current.data))
            current = current.next
        nodes.append("None")
        return " -> ".join(nodes)

    def __iter__(self) -> Iterator[Any]:
        """Returns an iterator of the linked list."""
        current = self.head
        while current:
            yield current
            current = current.next

    def add_first(self, data: Any) -> None:
        """Adds a node at the first index.

        Args:
            data: The data to be added.
        """
        new_node = Node(data)
        new_node.next = self.head
        self.head = new_node

    def add_last(self, data: Any) -> None:
        """Adds a node at the last index.

        Args:
            data: The data to be added
        """
        new_node = Node(data)
        if self.head is None:
            self.head = new_node
        else:
            current = self.head
            while current.next:
                current = current.next
            current.next = new_node

    def add_before(self, data: Any, target_data: Any) -> None:
        """Adds a node before a given data point.

        Args:
            data: The data to be added.
            target_data: The data point to be added before.

        Raises:
            Exception: If the linked list is empty.
            Exception: If the target data point is not found.
        """
        if self.head is None:
            raise Exception("Linked list is empty")

        if self.head.data == target_data:
            self.add_first(data)
            return

        new_node = Node(data)
        prev_node = self.head
        for node in self:
            if node.data == target_data:
                prev_node.next = new_node
                new_node.next = node
                return
            prev_node = node

        raise Exception(f"Node data not found: {target_data}")

    def add_after(self, data: Any, target_data: Any) -> None:
        """Adds a node after a given data point.

        Args:
            data: The data to be added.
            target_data: The data point to be added after.

        Raises:
            Exception: If the linked list is empty.
            Exception: If the target data point is not found.
        """
        if self.head is None:
            raise Exception("Linked list is empty")

        new_node = Node(data)
        for node in self:
            if node.data == target_data:
                new_node.next = node.next
                node.next = new_node
                return

        raise Exception(f"Node data not found: {target_data}")

    def remove_first_occurence(self, data: Any) -> None:
        """Adds a node after a given data point.

        Args:
            data: The data to be added.
            target_data: The data point to be added after.

        Raises:
            Exception: If the linked list is empty.
            Exception: If the target data point is not found.
        """
        if self.head is None:
            raise Exception("Linked list is empty")

        if self.head.data == data:
            self.head = self.head.next
            return

        prev_node = self.head
        for node in self:
            if node.data == data:
                prev_node.next = node.next
                return
            prev_node = node

        raise Exception(f"Node data not found: {data}")

    def clear(self) -> None:
        """Clears all node pointers."""
        self.head = None

    def contains(self, data: Any) -> bool:
        """Checks if a data point exists within the linked list.

        Args:
            data: The data to be checked.

        Returns:
            A boolean indicating whether the data point exists within the linked list.
        """
        current = self.head
        while current:
            if current.data == data:
                return True
            current = current.next
        return False

    def size(self) -> int:
        """Determines the size of the linked list by number of nodes.

        Returns:
            An integer indicating the number of nodes in the linked list.
        """
        current = self.head
        count = 0
        while current:
            count += 1
            current = current.next
        return count
