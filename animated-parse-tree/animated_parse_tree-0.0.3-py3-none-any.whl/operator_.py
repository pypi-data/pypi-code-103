from .node import Node


class Operator(Node):
    def __init__(self, op):
        super().__init__()
        self.symbol = op
        op_dict = {
            '+': (1, lambda a, b: a + b),
            '-': (1, lambda a, b: a - b),
            '*': (2, lambda a, b: a * b),
            '/': (2, lambda a, b: a / b),
            '^': (3, lambda a, b: a ** b)
        }
        self.priority = op_dict.get(op)[0]
        self.fn = op_dict.get(op)[1]
        self.width = len(str(op))

    def __lt__(self, otherOperator):
        return self.priority < otherOperator.priority

    def __le__(self, otherOperator):
        return self.priority <= otherOperator.priority

    def __gt__(self, otherOperator):
        return self.priority > otherOperator.priority

    def __ge__(self, otherOperator):
        return self.priority >= otherOperator.priority
