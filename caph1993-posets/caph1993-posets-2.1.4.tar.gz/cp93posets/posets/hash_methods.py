from __future__ import annotations
import itertools
from typing import TYPE_CHECKING, List, Optional, Sequence, Union, cast
if TYPE_CHECKING:
    from .posets import Poset

from math import factorial
from collections import deque
import numpy as np
from ..numpy_types import npUInt64Matrix, npInt64Array

Ints = Union[Sequence[int], npInt64Array]


def _hash(self: Poset, rounds: int):
    cls = self.__class__
    elems = self._hash_elems(rounds=rounds, salt=0)
    return cls.hasher(sorted(elems))


def _hash_elems(self: Poset, rounds: int, salt: int):
    mat: npUInt64Matrix = self.leq.astype(np.int64)
    with np.errstate(over='ignore'):
        H = hash_perm_invariant(self, salt + mat)
        for repeat in range(rounds):
            mat += np.matmul(H[:, None], H[None, :])
            H = hash_perm_invariant(self, salt + mat)
    return cast(npInt64Array, H)


def hash_perm_invariant(self: Poset, mat: npUInt64Matrix):
    HASH = self.__class__.hasher
    h = lambda l: HASH(sorted(l))
    a = [HASH((h(mat[:, i]), h(mat[i, :]))) for i in range(self.n)]
    return np.array(a, dtype=int)


def find_isomorphism(self: Poset, other: Poset):
    # Quick check:
    if self.n != other.n or hash(self) != hash(other):
        return None

    # Find the isomorphism
    n = self.n
    A = self.leq
    B = other.leq
    IJ = [(i, j) for i in range(n) for j in range(n)]

    def is_isomorphism(f):
        return all(A[i, j] == B[f[i], f[j]] for i, j in IJ)

    Ah = self.hash_elems
    Bh = other.hash_elems
    total, it = isomorphism_candidates(Ah, Bh)
    if total > n**2:
        # Try to hash more deeply to separate
        AAh = Ah + self._hash_elems(rounds=4, salt=1)
        BBh = Bh + other._hash_elems(rounds=4, salt=1)
        total, it = isomorphism_candidates(AAh, BBh)

    for f in it:
        if is_isomorphism(f):
            return f
    return None


def reindex(self: Poset, f, inverse=False, reset_labels=False):
    'Reindexed copy of self such that i is to self as f[i] to out'
    'If inverse==True, then f[i] is to self as i to out'
    n = self.n
    assert len(f) == n and sorted(set(f)) == list(
        range(n)), f'Invalid permutation {f}'
    if inverse:
        inv = [0] * n
        for i in range(n):
            inv[f[i]] = i
        f = inv
    leq = self.leq
    out = np.zeros_like(leq)
    for i in range(n):
        for j in range(n):
            out[f[i], f[j]] = leq[i, j]
    out.flags.writeable = False
    out_labels: Optional[Sequence[str]]
    if reset_labels:
        out_labels = None
    else:
        out_labels = ['' for i in range(n)]
        for i in range(n):
            out_labels[f[i]] = self.labels[i]
        out_labels = tuple(out_labels)
    return self.__class__(out, labels=out_labels)


def relabel(self: Poset, labels=None):
    'copy of self with different labels'
    return self.__class__(self.leq, labels=labels)


def canonical(self: Poset):
    'equivalent poset with enumerated labels and stable order'
    n = self.n
    group_by = {h: [] for h in range(n)}
    for i in range(n):
        group_by[self.heights[i]].append(i)
    topo = []
    rank = [-1] * n
    G = self.parents
    R = self.children
    nleq = self.leq.sum(axis=0)
    ngeq = self.leq.sum(axis=1)
    order = list(zip(nleq, ngeq, self.hash_elems, self.labels, range(n)))

    def key(i):
        t = tuple(sorted((rank[i] for i in R[i])))
        return (t, len(G[i]), order[i])

    for h in range(n):
        for i in sorted(group_by[h], key=key):
            rank[i] = len(topo)
            topo.append(i)
    leq = self.reindex(rank).leq
    return self.__class__(leq, labels=None)


def isomorphism_candidates(hashesA: Ints, hashesB: Ints, out=None):
    '''
    Total number and iterator of all injective and surjective mappings
        f from range(n) to range(n)
    such that
        all(hashesA[i] == hashesB[f[i]] for i in range(n))
    where n = len(hashesA) = len(hashesB).
    '''
    n = len(hashesA)
    if len(hashesA) != len(hashesB):
        return 0, iter([])
    if out is not None:
        assert len(out) == n, f'Incompatible output shape'

    out = [None] * n if out is None else out
    out = cast(List[int], out)

    if sorted(hashesA) != sorted(hashesB):
        return 0, iter([])
    total = 1

    empty = lambda: cast(List[int], [])
    groups = {v: (empty(), empty()) for v in [*hashesA, *hashesB]}
    for i, v in enumerate(hashesA):
        groups[v][0].append(i)
    for i, v in enumerate(hashesB):
        groups[v][1].append(i)

    groups = [*groups.values()]
    for idxA, idxB in groups:
        if len(idxA) != len(idxB):
            return 0, iter([])
        total *= factorial(len(idxA))

    m = len(groups)

    def backtrack(group_i):
        if group_i == m:
            yield out
        else:
            gA, gB = groups[group_i]
            for gBperm in itertools.permutations(gB):
                for i, j in zip(gA, gBperm):
                    out[i] = j
                yield from backtrack(group_i + 1)

    return total, backtrack(0)
