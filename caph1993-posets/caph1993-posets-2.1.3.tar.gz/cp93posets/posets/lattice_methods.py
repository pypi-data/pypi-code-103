from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .posets import Poset

import numpy as np
from typing import List, Sequence
from ..poset_exceptions import PosetExceptions


def is_lattice(self: Poset):
    try:
        if self.n > 0:
            self.lub
            self.bottom
    except PosetExceptions.NotUniqueBottomException as e:
        reason = f"Not unique bottom: {self.bottoms}"
        return self._wbool(False, reason)
    except PosetExceptions.NotLatticeException as e:
        i, j = e.args
    else:
        return self._wbool(True)
    n = self.n
    leq = self.leq
    above = [k for k in range(n) if leq[i, k] and leq[j, k]]
    below = [k for k in range(n) if leq[k, i] and leq[k, j]]
    if not above:
        reason = f'Not a lattice: {i} lub {j} => (no common ancestor)'
        return self._wbool(False, reason)
    if not below:
        reason = f'Not a lattice: {i} glb {j} => (no common descendant)'
        return self._wbool(False, reason)
    lub = min(above, key=lambda k: sum(leq[:, k]))
    glb = max(below, key=lambda k: sum(leq[:, k]))
    for x in above:
        if not leq[lub, x]:
            reason = f'Not a lattice: {i} lub {j} => {lub} or {x}'
            return self._wbool(False, reason)
    for x in below:
        if not leq[x, glb]:
            reason = f'Not a lattice: {i} glb {j} => {glb} or {x}'
            return self._wbool(False, reason)
    return self._wbool(False, 'Unknown reason')


def lub(self: Poset):
    'matrix of i lub j, i.e. i join j'
    n = self.n
    leq = self.leq
    lub_id = {tuple(leq[i, :]): i for i in range(n)}
    lub = np.zeros((n, n), int)
    for i in range(n):
        for j in range(n):
            above = tuple(leq[i, :] & leq[j, :])
            if above not in lub_id:
                # self._lub_issue = (i, j)
                raise PosetExceptions.NotLatticeException(args=(i, j))
            lub[i, j] = lub_id[above]
    lub.flags.writeable = False
    return lub


def bottom(self: Poset):
    'unique bottom element of the Poset. Throws if not present'
    bottoms = self.bottoms
    if not bottoms:
        raise PosetExceptions.NoBottomsException()
    if len(bottoms) > 1:
        hook = lambda: f'Multiple bottoms found: {bottoms}'
        raise PosetExceptions.NotUniqueBottomException(hook)
    return bottoms[0]


def set_lub(self: Poset, *elems: int) -> int:
    if not elems:
        return self.bottom
    lub = self.lub
    acum = elems[0]
    for elem in elems[1:]:
        acum = lub[acum, elem]
    return acum


def top(self: Poset):
    'unique top element of the Poset. Throws if not present'
    tops = self.tops
    if not tops:
        raise PosetExceptions.NoTopsException()
    if len(tops) > 1:
        hook = lambda: f'Multiple tops found: {tops}'
        raise PosetExceptions.NotUniqueTopException(hook)
    return tops[0]


def set_glb(self: Poset, *elems: int) -> int:
    if not elems:
        return self.top
    glb = self.glb
    acum = elems[0]
    for elem in elems[1:]:
        acum = glb[acum, elem]
    return acum


def irreducibles(self: Poset):
    n = self.n
    children = self.children
    return [i for i in range(n) if len(children[i]) == 1]


def glb(self: Poset):
    geq = self.leq.T
    return self.__class__(geq).lub


def irreducibles_leq(self: Poset):
    '''Irreducibles below (leq) x for each x'''
    Rn = range(self.n)
    I = self.irreducibles
    leq = self.leq
    return [[i for i in I if leq[i, x]] for x in Rn]
