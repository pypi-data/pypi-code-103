from .node import Node


class Operand(Node):
    def __init__(self, value):
        super().__init__()
        self.value = float(value)
        self.width = len(str(float(value)))