class QueueList:
    def __init__(self):
        self.items = []

    def enqueue(self, data):
        self.items.insert(0, data)

    def dequeue(self):
        if len(self.items) > 0:
            item = self.items.pop(0)
            return item
        else:
            print("The queue is empty.")
            return None

    def print_queue(self):
        if len(self.items) > 0:
            for item in self.items:
                print(item)
        else:
            print("The queue is empty")

    def empty_queue(self):
        self.items = []

    def size(self):
        return len(self.items)
