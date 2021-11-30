from __future__ import annotations
from typing import TYPE_CHECKING, List, Sequence
if TYPE_CHECKING:
    from .posets import Poset

from collections import deque
import numpy as np


def _parse_domain(n: int, domain: List[int] | List[bool]) -> List[int]:
    assert len(domain) <= n, f'Invalid domain: {domain}'
    if len(domain) == n > 0:
        if isinstance(domain[0], bool):
            domain = [i for i in range(n) if domain[i]]
    else:
        assert len(set(domain)) == len(domain), f'Invalid domain: {domain}'
    return domain  # type:ignore


def subgraph(self: Poset, domain: List[int] | List[bool]):
    domain = _parse_domain(self.n, domain)
    m = len(domain)
    leq = self.leq
    sub = np.zeros((m, m), dtype=bool)
    for i in range(m):
        for j in range(m):
            sub[i, j] = leq[domain[i], domain[j]]
    sub.flags.writeable = False
    labels = tuple(self.labels[i] for i in domain)
    return self.__class__(sub, labels=labels)


def toposort(self: Poset):
    n = self.n
    G = self.parents
    child = self.child
    indeg = [child[:, i].sum() for i in range(n)]
    topo: List[int] = []
    q = deque([i for i in range(n) if indeg[i] == 0])
    while q:
        u = q.popleft()
        topo.append(u)
        for v in G[u]:
            indeg[v] -= 1
            if indeg[v] == 0:
                q.append(v)
    assert len(topo) == n, f'Not antisymmetric, cycle found'
    return tuple(topo)


def toporank(self: Poset):
    return tuple(inverse_permutation(self.toposort))


def inverse_permutation(perm: Sequence[int], check=False):
    n = len(perm)
    if check:
        assert set(perm) == set(range(n)), f'Invalid permutation {perm}'
    rank = [-1] * n
    for i in range(n):
        rank[perm[i]] = i
    return rank


def independent_components(self: Poset):
    'Graph components if all edges were bidirectional'
    n = self.n
    cmp = self.leq | self.leq.T
    G = [[j for j in range(n) if cmp[i, j]] for i in range(n)]
    color = np.ones(n, dtype=int) * -1

    def component(i: int):
        q = deque([i])
        found = []
        while q:
            u = q.popleft()
            for v in G[u]:
                if color[v] != color[u]:
                    color[v] = color[u]
                    q.append(v)
            found.append(u)
        return found

    comps: List[List[int]] = []
    for i in range(n):
        if color[i] == -1:
            color[i] = len(comps)
            comps.append(component(i))
    return comps


def bottoms(self: Poset):
    'bottom elements of the poset'
    n = self.n
    nleq = self.leq.sum(axis=0)
    return [i for i in range(n) if nleq[i] == 1]


def non_bottoms(self: Poset):
    'non-bottom elements of the poset'
    n = self.n
    nleq = self.leq.sum(axis=0)
    return [i for i in range(n) if nleq[i] > 1]


def tops(self: Poset):
    'top elements of the poset'
    n = self.n
    nleq = self.leq.sum(axis=0)
    return [i for i in range(n) if nleq[i] == n]


def non_tops(self: Poset):
    'non-top elements of the poset'
    n = self.n
    nleq = self.leq.sum(axis=0)
    return [i for i in range(n) if nleq[i] < n]
