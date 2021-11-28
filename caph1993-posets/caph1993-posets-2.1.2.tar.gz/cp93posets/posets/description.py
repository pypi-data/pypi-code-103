from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .posets import Poset
from typing import Sequence, Tuple


def describe(self: Poset):
    self.show()
    print('Relation matrix:')
    print(self.leq.astype(int))
    print('Covers:', self)
    print(f'Lattice? {self.is_lattice}')
    if self.is_lattice:
        print(f'Distributive? {self.is_distributive}')
    else:
        print(f'# bottoms: {len(self.bottoms)}')
        print(f'# tops: {len(self.tops)}')
    return


def name(self: Poset):
    'Compact and readable representation of self based on parents'
    n = self.n
    P = self.parents
    topo = self.toposort
    Pstr = lambda i: ','.join(map(str, P[i]))
    it = (f'{i}<{Pstr(i)}' for i in topo if P[i])
    name = ' : '.join([f'{n}', *it])
    labels = ''
    if self.labels != tuple(range(n)):
        labels = ', '.join(self.labels)
        labels = f' with labels {labels}'
    return f'P({name}){labels}'