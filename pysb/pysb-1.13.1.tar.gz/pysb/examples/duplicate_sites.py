from pysb import *

Model()

Monomer('A', ['a', 'a'], {'a': ['u', 'p']})
Monomer('B', ['b'])

Parameter('P', 1.0)

Initial(A(a=(('u', 1), 'u')) % B(b=1), P)

Rule('r1', A(a=(1, 'u')) % B(b=1) >> None, P)
