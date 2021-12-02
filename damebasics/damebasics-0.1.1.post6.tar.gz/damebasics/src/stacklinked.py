from linkedlist import LinkedList

class StackLinked:
    class EmptyStack(Exception):
        pass

    def __init__(self):
        self.items = LinkedList()

    def push(self, data):
        self.items.add_first(data)

    def pop(self):
        if self.items.head:
            item = self.items.head
            self.items.head = self.items.head.next
            return item
        else:
            raise StackLinked.EmptyStack

    def print_stack(self):
        self.items.print_linked_list()