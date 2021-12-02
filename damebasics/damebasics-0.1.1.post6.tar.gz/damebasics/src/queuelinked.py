from linkedlist import LinkedList

class QueueLinked:
    def __init__(self):
        self.items = LinkedList()

    def enqueue(self, data):
        self.items.add_last(data)

    def dequeue(self):
        if self.items.head is None:
            print("The queue is empty")
            return None
        else:
            element = self.items.head
            self.items.head = self.items.head.next
            return element.data

    def peek(self):
        return self.items.head.data

    def size(self):
        count = 0
        if self.items.head is not None:
            node = self.items.head
            while node:
                count += 1
                node = node.next
        return count

    def clone(self):
        cloned = QueueLinked()
        node = self.items.head
        while node:
            cloned.enqueue(node.data)
            node = node.next
        return cloned

    def empty_queue(self):
        self.items.head = None
        self.items = LinkedList()

    def print_queue(self):
        self.items.print_linked_list()

