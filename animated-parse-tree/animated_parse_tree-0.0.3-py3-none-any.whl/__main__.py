from .parse_tree import ParseTree
from sys import argv

if len(argv) == 1:
    expr = input('Enter Expression: ')
else:
    expr = ' '.join(argv[1:])

t = ParseTree()
t.read(expr)
print(t.expression, '=', t.evaluate())
print(str(t))