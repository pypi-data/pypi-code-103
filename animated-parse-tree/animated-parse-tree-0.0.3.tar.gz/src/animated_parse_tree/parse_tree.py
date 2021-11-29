from .node import Node
from .operand import Operand
from .operator_ import Operator


class ParseTree:
    def __init__(self):
        self.expression = ''
        self.root = None
        self.currentPointer = None
        self.padding = 1
        self.left_edge = '\u2199'
        self.right_edge = '\u2198'

    def tokenise(self, expr):
        return expr.split(' ')

    def read(self, expr):
        for token in self.tokenise(expr):
            self.insertNode(token)

    def insertNode(self, token):
        if self.expression != '':
            self.expression += ' '
        self.expression += str(token)
        if self.root is None:
            self.root = Operand(token)
            self.currentPointer = self.root
        elif isinstance(self.currentPointer, Operand):
            newNode = Operator(token)
            self.float_node(newNode)
        elif isinstance(self.currentPointer, Operator):
            newNode = Operand(token)
            self.currentPointer.right = newNode
            newNode.parent = self.currentPointer
            self.currentPointer = newNode
        else:
            raise AssertionError('Invalid Node!')

    def float_node(self, newNode):
        if self.currentPointer is self.root:
            self.root.parent = newNode
            newNode.left = self.root
            self.root = newNode
            self.currentPointer = newNode
        else:
            if self.currentPointer.parent >= newNode:
                self.currentPointer = self.currentPointer.parent
                self.float_node(newNode)
            elif self.currentPointer.parent < newNode:
                newNode.parent = self.currentPointer.parent
                newNode.left = self.currentPointer.parent.right
                self.currentPointer.parent.right = newNode
                self.currentPointer = newNode
            else:
                raise AssertionError('Unexpected Situation')

    def update_values(self, node=None):
        if node is None:
            node = self.root
        if isinstance(node, Operator):
            self.update_values(node.left)
            self.update_values(node.right)
            node.value = node.fn(node.left.value, node.right.value)

    def update_dims(self, node=None):
        if node is None:
            node = self.root
        if isinstance(node, Operator):
            self.update_dims(node.left)
            self.update_dims(node.right)
            node.width = node.left.width + 1 + node.right.width
            node.height = max(node.left.height, node.right.height) + 1

    def generate_tmp_nodes(self, node=None, depth=1):
        if node is None:
            node = self.root
        if isinstance(node, Operator):
            self.generate_tmp_nodes(node.left, depth=depth + 1)
            self.generate_tmp_nodes(node.right, depth=depth + 1)
        else:
            if depth < self.root.height:
                node.left = Node()
                node.left.width = node.width
                node.left.value = ' '
                node.right = Node()
                node.right.width = 0
                node.right.value = ''
                self.generate_tmp_nodes(node.left, depth=depth + 1)

    def prune_tmp_nodes(self, current_node=None):
        if current_node is None:
            current_node = self.root
        if isinstance(current_node.left, Node):
            current_node.left = None
        if isinstance(current_node.right, Node):
            current_node.right = None
        if current_node.left is not None:
            self.prune_tmp_nodes(current_node=current_node.left)
        if current_node.right is not None:
            self.prune_tmp_nodes(current_node=current_node.right)

    def evaluate(self):
        self.update_values()
        return self.root.value

    def dimensions(self):
        self.update_dims()
        return self.root.height, self.root.width

    def __str__(self):
        self.update_dims()
        self.generate_tmp_nodes()
        current_children = [self.root]
        next_children = []
        result = ''
        for _ in range(self.root.height):
            for n in current_children:
                if isinstance(n, Operator):
                    result += ' ' * n.left.width + n.symbol + ' ' * n.right.width + ' ' * self.padding
                elif isinstance(n, Operand):
                    result += str(n.value) + ' ' * self.padding
                elif isinstance(n, Node):
                    result += n.value * (n.width - 1) + ' ' * self.padding
                else:
                    raise AssertionError('Unexpected Situation!')
                if n.left is not None:
                    next_children.append(n.left)
                if n.right is not None:
                    next_children.append(n.right)
            result += '\n'
            for n in current_children:
                if isinstance(n, Operator):
                    space_1 = n.left.width // 2
                    space_2 = n.left.width - space_1 - 1
                    space_3 = n.right.width // 2
                    space_4 = n.right.width - space_3 - 1
                    result += ' ' * space_1 + self.left_edge + ' ' * (space_2 + self.padding + space_3) + self.right_edge + ' ' * (space_4 + self.padding)
                elif isinstance(n, Operand):
                    result += ' ' * (n.width + self.padding)
            result += '\n'
            current_children = next_children
            next_children = []
        self.prune_tmp_nodes()
        return result
