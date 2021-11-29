from __future__ import annotations
from functools import reduce
from typing import TYPE_CHECKING, Any, Iterable, Optional, Tuple, cast
if TYPE_CHECKING:
    from .posets import Poset

from typing import List, Sequence
from ..iterators import product_list

from typing import TypeVar

Endomorphism = List[int]
PartialEndomorphism = TypeVar(
    'PartialEndomorphism',
    List[Optional[int]],
    Endomorphism,
)


def iter_f_all(self: Poset):
    'all endomorphisms'
    return product_list(range(self.n), repeat=self.n)


def num_f_all(self: Poset):
    return self.n**self.n


def iter_f_all_bottom(self: Poset):
    'all endomorphisms f with f[bottom]=bottom'
    n = self.n
    if n > 0:
        options = [range(n) if i != self.bottom else [i] for i in range(n)]
        for f in product_list(*options):
            yield f
    return


def num_f_all_bottom(self: Poset):
    return self.n**(self.n - 1)


def f_is_monotone(self: Poset, f, domain=None):
    'check if f is monotone over domain'
    n = self.n
    domain = range(n) if domain is None else domain
    leq = self.leq
    for i in domain:
        for j in domain:
            if leq[i, j] and not leq[f[i], f[j]]:
                return False
    return True


def iter_f_monotone_bruteforce(self: Poset):
    'all monotone functions'
    for f in self.iter_f_all():
        if self.f_is_monotone(f):
            yield f
    return


def iter_f_monotone_bottom_bruteforce(self: Poset):
    'all monotone functions with f[bottom]=bottom'
    for f in self.iter_f_all_bottom():
        if self.f_is_monotone(f):
            yield f
    return


def iter_f_monotone(self: Poset):
    'all monotone functions'
    f = [None] * self.n
    f = cast(PartialEndomorphism, f)
    yield from self.iter_f_monotone_restricted(_f=f)


def iter_f_lub_bruteforce(self: Poset):
    'all space functions. Throws if no bottom'
    for f in self.iter_f_monotone_bottom():
        if self.f_is_lub_pairs(f):
            yield f
    return


def iter_f_monotone_restricted(self: Poset, domain=None,
                               _f: PartialEndomorphism = None):
    'generate all monotone functions f : domain -> self, padding non-domain with None'
    n = self.n
    leq = self.leq
    geq_list = [[j for j in range(n) if leq[i, j]] for i in range(n)]
    f = [None for i in range(n)] if _f is None else _f
    f = cast(PartialEndomorphism, f)
    topo, children = self._toposort_children(domain)
    yield from self._iter_f_monotone_restricted(f, topo, children, geq_list)


def _iter_f_monotone_restricted(
    self: Poset,
    f: PartialEndomorphism,
    topo: List[int],
    children,
    geq_list: List[List[int]],
):
    m = len(topo)
    set_lub = self.set_lub
    lub_f = lambda elems: set_lub(*(f[i] for i in elems))  # type: ignore

    def backtrack(i):
        'f[topo[j]] is fixed for all j<i. Backtrack f[topo[k]] for all k>=i, k<m'
        if i == m:
            yield f
        else:
            for k in geq_list[lub_f(children[i])]:
                f[topo[i]] = k
                yield from backtrack(i + 1)

    yield from backtrack(0)


def _toposort_children(self: Poset, domain: Optional[Sequence[int]]):
    'Compute a toposort for domain and the children lists filtered for domain'
    'j in out.children[i] iff j in out.topo and j is children of out.topo[i]'
    n = self.n
    D = range(n) if domain is None else domain
    topo = [i for i in self.toposort if i in D]
    sub = self.subgraph(topo)
    children = [[topo[j] for j in l] for l in sub.children]
    return topo, children


def iter_f_monotone_bottom(self: Poset):
    'all monotone functions with f[bottom]=bottom'
    if self.n:
        return
    f = cast(List[int], [None] * self.n)
    f[self.bottom] = self.bottom
    domain = [i for i in range(self.n) if i != self.bottom]
    yield from self.iter_f_monotone_restricted(domain=domain, _f=f)


def irreducible_components(self: Poset):
    '''
    components of join irreducibles in toposort order and children
    lists for each component
    '''
    n = self.n
    if n <= 1:  # no join irreducibles at all
        return (0, [], [])
    irr = self.irreducibles
    sub = self.subgraph(irr)
    subcomps = sub.independent_components
    m = len(subcomps)
    irrcomps = [[irr[j] for j in subcomps[i]] for i in range(m)]
    m_topo, m_children = zip(
        *(self._toposort_children(irrcomps[i]) for i in range(m)))
    m_topo = cast(Tuple[List[int]], m_topo)
    m_children = cast(Tuple[List[List[int]]], m_children)
    return m, m_topo, m_children


def _interpolate_funcs(self: Poset, funcs, domain) -> Iterable[List[int]]:
    'extend each f in funcs outside domain using f[j]=lub(f[i] if i<=j and i in domain)'
    n = self.n
    lub = self.lub
    leq = self.leq
    bot = self.bottom
    no_domain = [i for i in range(n) if i not in domain]
    dom_leq = [[i for i in domain if leq[i, j]] for j in range(n)]
    lub_f = (lambda a, b: lub[a, b])
    for f in funcs:
        for j in no_domain:
            f[j] = reduce(lub_f, (f[x] for x in dom_leq[j]), bot)
        yield f


def iter_f_irreducibles_monotone_bottom(self: Poset) -> Iterable[List[int]]:
    'all functions given by f[non_irr]=lub(f[irreducibles] below non_irr)'
    if self.n == 0:
        return
    n = self.n
    leq = self.leq
    geq_list = [[j for j in range(n) if leq[i, j]] for i in range(n)]
    m, m_topo, m_children = self.irreducible_components
    f = [None for i in range(n)]
    f = cast(PartialEndomorphism, f)

    def backtrack(i):
        if i == m:
            yield f
        else:
            it = self._iter_f_monotone_restricted(
                f,
                m_topo[i],
                m_children[i],
                geq_list,
            )
            for _ in it:
                yield from backtrack(i + 1)

    funcs = backtrack(0)
    yield from self._interpolate_funcs(funcs, self.irreducibles)


def iter_f_irreducibles_monotone(self: Poset):
    'all functions given by f[non_irr]=lub(f[irreducibles] below non_irr) and'
    'f[bottom] = any below or equal to glb(f[irreducibles])'
    n = self.n
    if n == 0:
        return
    glb = self.glb
    leq = self.leq
    below = [[i for i in range(n) if leq[i, j]] for j in range(n)]
    bottom = self.bottom
    irreducibles = self.irreducibles
    for f in self.iter_f_irreducibles_monotone_bottom():
        _glb_f = (lambda acum, b: glb[acum, f[b]])
        glb_f = lambda elems: reduce(_glb_f, elems, self.top)
        for i in below[glb_f(irreducibles)]:
            f[bottom] = i
            yield f


'''
@section
    Methods for endomorphisms that preserve lub
'''


def f_is_lub(self: Poset, f, domain=None):
    '''
    check if f preserves lubs for sets:
        f_is_lub_pairs and f[bottom]=bottom.
    Throws if no bottom
    '''
    n = self.n
    if n == 0 or (domain is not None and len(domain) <= 1):
        return True
    bot = self.bottom
    if f[bot] != bot or (domain is not None and bot not in domain):
        return False
    return self.f_is_lub_pairs(f, domain)


def f_is_lub_pairs(self: Poset, f, domain=None):
    '''
    check if f preserves lubs for pairs:
        f[lub[i,j]]=lub[f[i],f[j]]
    '''
    n = self.n
    domain = range(n) if domain is None else domain
    lub = self.lub
    for i in domain:
        for j in domain:
            if f[lub[i, j]] != lub[f[i], f[j]]:
                return False
    return True


def iter_f_lub_pairs_bruteforce(self: Poset):
    'all functions that statisfy f_is_lub_pairs'
    for f in self.iter_f_monotone():
        if self.f_is_lub_pairs(f):
            yield f
    return


def iter_f_lub_pairs(self: Poset):
    'all functions that statisfy f_is_lub'
    it = self.iter_f_irreducibles_monotone()
    if self.is_distributive:
        yield from it
    else:
        for f in it:
            if self.f_is_lub_pairs(f):
                yield f


def iter_f_lub(self: Poset):
    'all functions that preserve lubs for sets'
    it = self.iter_f_irreducibles_monotone_bottom()
    if self.is_distributive:
        yield from it
    else:
        for f in it:
            if self.f_is_lub_pairs(f):
                yield f


def num_f_lub_pairs(self: Poset):
    return self.count_f_lub_pairs_bruteforce()


def count_f_lub_pairs_bruteforce(self: Poset):
    return sum(1 for f in self.iter_f_lub_pairs())


def num_f_lub(self: Poset):
    return self.count_f_lub()


def count_f_lub(self: Poset):
    if self.is_distributive:
        num = self.count_f_lub_distributive()
    else:
        num = self.count_f_lub_bruteforce()
    return num


def count_f_lub_bruteforce(self: Poset):
    return sum(1 for f in self.iter_f_lub())


def f_is_lub_of_irreducibles(self: Poset, f, domain=None):
    '''
    check if f satisfies for all x in range(n) that
        f(x) == self.set_lub(*[f[i] for i in I(x)])
    where
        I(x) = list of irreducibles below (leq) x
    '''
    n = self.n
    set_lub = self.set_lub
    I = self.irreducibles_leq
    for a in range(n):
        if f[a] != set_lub(*I[a]):
            return False
    return True
