from __future__ import annotations
from typing import Any, Iterable, List, Optional, Sequence, Set, Tuple, Union, cast
from cp93pytools.methodtools import cached_property

#from numpy.random.mtrand import permutation
from ..iterators import cartesian
from ..poset_exceptions import (
    NotUniqueBottomException,
    PosetExceptions,
    NotLatticeException,
)
from ..help_index import HelpIndex
from ..poset_wbools import WBools
from ..algorithm_random_poset_czech import random_lattice as random_lattice_czech
import pyhash
import numpy as np
from collections import deque
from functools import reduce
import time
from .relations import Relation
from ..numpy_types import npBoolMatrix
from ..algorithm_floyd_warshall import floyd_warshall
from ..outfile import Outfile

from . import (
    graphviz,
    description,
    graph_methods,
    lattice_methods,
    hash_methods,
    grow_methods,
    endomorphisms,
)
from cp93pytools.methodtools import implemented_at


class Poset(HelpIndex, WBools):
    '''
    Hashable object that represents an inmutable finite partial order.
    Uses a matrix and hashing is invariant under permutations.

    Run print(Poset.usage) for details and usage examples.

    The main attributes (always present) are:
        n: size of the poset.
            The elements of the poset are range(n)
        leq: read only less-or-equal boolean nxn matrix:
            leq[i,j] is True if and only "i <= j" in the poset order
        _labels: optional sequence of n strings.
            Only used for displaying
    '''

    def __init__(self, leq: npBoolMatrix, labels: Sequence[str] = None,
                 _validate=False):
        rel = Relation(leq)
        if labels is not None:
            m = len(labels)
            assert m == rel.n, f'{m} labels found. Expected {rel.n}'
            non = [l for l in labels if not isinstance(l, str)]
            assert not non, f'non-string label found: {non[0]}'
        self.n = rel.n
        self.leq = leq
        self._labels = labels
        if _validate:
            self.assert_is_poset()

    def assert_is_poset(self):
        rel = Relation(self.leq)
        return rel.is_poset.assert_explain()

    @property
    def labels(self):
        return self._labels or tuple(f'{i}' for i in range(self.n))

    '''
    @section
        Fundamental methods 
    '''

    @cached_property
    def child(self):
        '''
        nxn boolean matrix: transitive reduction of the poset.
        child[i,j] == True iff j covers i (with no elements inbetween)
        '''
        red = Relation(self.leq).transitive_reduction(_assume_poset=True)
        return red.rel

    @cached_property
    def children(self):
        ''' top-down adjoint list (j in G[i] iff i covers j)'''
        n = self.n
        child = self.child
        return [[j for j in range(n) if child[j, i]] for i in range(n)]

    @cached_property
    def parents(self):
        '''bottom-up adjoint list (j in G[i] iff j covers i)'''
        n = self.n
        child = self.child
        return [[j for j in range(n) if child[i, j]] for i in range(n)]

    @cached_property
    def dist(self):
        'Matrix of shortest distance from i upwards to j through child'
        cls = self.__class__
        child = self.child
        return cls.child_to_dist(child, assume_poset=True)

    '''
    @section
        Display methods
    '''

    @implemented_at(graphviz.show)
    def show(self):
        ...

    def __repr__(self):
        return self.name

    @cached_property
    def name(self):
        return description.name(self)

    def describe(self):
        return description.describe(self)

    '''
    @section
        Interface methods
    '''

    @classmethod
    def from_parents(cls, parents, labels=None):
        'create Poset from list: parents[i] = list of parents of i'
        n = len(parents)
        children = [[] for _ in range(n)]
        for ch in range(n):
            for pa in parents[ch]:
                children[pa].append(ch)
        return cls.from_children(children, labels)

    @classmethod
    def from_children(cls, children: List[List[int]], labels=None):
        'create Poset from list: children[i] = list of covers of i'
        n = len(children)
        child = np.zeros((n, n), dtype=bool)
        for pa in range(n):
            for ch in children[pa]:
                child[ch, pa] = True
        child.flags.writeable = False
        dist = cls.child_to_dist(child, assume_poset=True)
        dist.flags.writeable = False
        leq = dist < n
        leq.flags.writeable = False
        poset = cls(leq, labels, _validate=True)
        poset.__dict__['child'] = child
        poset.__dict__['dist'] = dist
        return poset

    @classmethod
    def from_down_edges(cls, n, edges):
        'create Poset of size n respecting all given relations (ancestor, descendant)'
        return cls.from_up_edges(n, [(j, i) for i, j in edges])

    @classmethod
    def from_up_edges(cls, n, edges):
        'create Poset of size n respecting all given relations (descendant, ancestor)'
        leq = np.zeros((n, n), dtype=bool)
        leq[np.diag_indices_from(leq)] = True
        for des, anc in edges:
            leq[des, anc] = True
        leq.flags.writeable = False
        closure = Relation(leq).transitive_closure()
        return cls(closure.rel, _validate=True)

    @classmethod
    def from_lambda(cls, elems, f_leq, labels=None):
        'create Poset with: leq[i,j] = f_leq(elems[i], elems[j])'
        m = len(elems)
        leq = np.zeros((m, m), dtype=bool)
        for i in range(m):
            for j in range(m):
                leq[i, j] = f_leq(elems[i], elems[j])
        leq.flags.writeable = False
        return cls(leq, labels, _validate=True)

    @cached_property
    def heights(self):
        'Array of distance from i down to any bottom'
        dist = self.dist
        bottoms = self.bottoms
        return tuple(np.min([dist[i, :] for i in bottoms], axis=0))

    @cached_property
    def height(self):
        return max(self.heights)

    @classmethod
    def child_to_dist(cls, child: npBoolMatrix, assume_poset=False):
        'Compute all pairs shortest distances using Floyd-Warshall algorithm'
        # To do: use toposort or repeated dijsktra if assume_poset==True
        dist = floyd_warshall(child, infinity=child.shape[0])
        dist.flags.writeable = False
        return dist

    '''
    @section
        Graph structure methods
    '''

    @implemented_at(graph_methods.subgraph)
    def subgraph(self):
        ...

    @cached_property
    def toposort(self):
        return graph_methods.toposort(self)

    @cached_property
    def toporank(self):
        return graph_methods.toporank(self)

    @cached_property
    def independent_components(self):
        return graph_methods.independent_components(self)

    @cached_property
    def bottoms(self):
        return graph_methods.bottoms(self)

    @cached_property
    def tops(self):
        return graph_methods.tops(self)

    @cached_property
    def non_bottoms(self):
        return graph_methods.non_bottoms(self)

    @cached_property
    def non_tops(self):
        return graph_methods.non_tops(self)

    '''
    @section
        Lattice methods
    '''

    def assert_lattice(self):
        self.is_lattice.assert_explain()

    @cached_property
    def is_lattice(self):
        return lattice_methods.is_lattice(self)

    @cached_property
    def bottom(self):
        return lattice_methods.bottom(self)

    @cached_property
    def top(self):
        return lattice_methods.top(self)

    @cached_property
    def lub(self):
        return lattice_methods.lub(self)

    @cached_property
    def glb(self):
        return lattice_methods.glb(self)

    @implemented_at(lattice_methods.set_lub)
    def set_lub(self):
        ...

    @implemented_at(lattice_methods.set_glb)
    def set_glb(self):
        ...

    @cached_property
    def irreducibles(self):
        return lattice_methods.irreducibles(self)

    @cached_property
    def irreducibles_leq(self):
        return lattice_methods.irreducibles_leq(self)

    '''
    @section
        Hashing and isomorphisms
    '''

    def __hash__(self):
        return self.hash

    def __eq__(self, other: Poset):
        'Equality up to isomorphism, i.e. up to reindexing'
        return self.find_isomorphism(other) is not None

    _hasher = pyhash.xx_64(seed=0)

    @classmethod
    def hasher(cls, ints: Sequence[int]):
        '''
        Fast numeric hashing function that is consistent across runs.
        Independent of PYTHONHASHSEED unlike Python's hash.
        The output space is range(2**63), i.e. 1e18 approximately 
        '''
        uint64hash = cls._hasher(str(ints)[1:-1])
        int64hash = uint64hash >> 1  # Prevent overflow
        return int64hash

    @cached_property
    def hash_elems(self):
        return self._hash_elems(rounds=2, salt=0)

    @implemented_at(hash_methods._hash_elems)
    def _hash_elems(self):
        ...

    @cached_property
    def hash(self):
        return self.__class__.hasher(sorted(self.hash_elems))

    @implemented_at(hash_methods.find_isomorphism)
    def find_isomorphism(self):
        ...

    @cached_property
    @implemented_at(hash_methods.canonical)
    def canonical(self):
        ...

    @implemented_at(hash_methods.reindex)
    def reindex(self):
        ...

    def relabel(self, labels: Sequence[str] = None):
        'copy of self with different labels'
        return self.__class__(self.leq, labels=labels)

    '''
    @section
        Methods for atomic changes (grow-by-one inductively)
    '''

    @classmethod
    def all_latices(cls, max_size: int):
        return list(cls.iter_all_latices(max_size))

    @classmethod
    def iter_all_latices(cls, max_size: int):
        return grow_methods.iter_all_latices(cls, max_size=max_size)

    @cached_property
    @implemented_at(grow_methods.forbidden_pairs)
    def forbidden_pairs(self):
        ...

    @implemented_at(grow_methods.iter_add_edge)
    def iter_add_edge(self):
        ...

    @implemented_at(grow_methods.iter_add_node)
    def iter_add_node(self):
        ...

    @implemented_at(grow_methods._add_edge)
    def _add_edge(self):
        ...

    @implemented_at(grow_methods._add_node)
    def _add_node(self):
        ...

    '''
    @section
        Methods for all endomorphisms
    '''

    @implemented_at(endomorphisms.iter_f_all)
    def iter_f_all(self):
        ...

    @cached_property
    @implemented_at(endomorphisms.num_f_all)
    def num_f_all(self):
        ...

    @implemented_at(endomorphisms.iter_f_all_bottom)
    def iter_f_all_bottom(self):
        ...

    @cached_property
    @implemented_at(endomorphisms.num_f_all_bottom)
    def num_f_all_bottom(self):
        ...

    '''
    @section
        Methods for all monotonic endomorphisms
    '''

    @implemented_at(endomorphisms.f_is_monotone)
    def f_is_monotone(self):
        ...

    @implemented_at(endomorphisms.iter_f_monotone_bruteforce)
    def iter_f_monotone_bruteforce(self):
        ...

    @implemented_at(endomorphisms.iter_f_monotone_bottom_bruteforce)
    def iter_f_monotone_bottom_bruteforce(self):
        ...

    @implemented_at(endomorphisms.iter_f_monotone)
    def iter_f_monotone(self):
        ...

    @implemented_at(endomorphisms.iter_f_lub_bruteforce)
    def iter_f_lub_bruteforce(self):
        ...

    @implemented_at(endomorphisms.iter_f_monotone_restricted)
    def iter_f_monotone_restricted(self):
        ...

    @implemented_at(endomorphisms._iter_f_monotone_restricted)
    def _iter_f_monotone_restricted(self):
        ...

    @implemented_at(endomorphisms._toposort_children)
    def _toposort_children(self):
        ...

    @implemented_at(endomorphisms.iter_f_monotone_bottom)
    def iter_f_monotone_bottom(self):
        ...

    '''
    @section
        Methods for monotonic endomorphisms over irreducibles
    '''

    @cached_property
    @implemented_at(endomorphisms.irreducible_components)
    def irreducible_components(self):
        ...

    @implemented_at(endomorphisms._interpolate_funcs)
    def _interpolate_funcs(self):
        ...

    @implemented_at(endomorphisms.iter_f_irreducibles_monotone_bottom)
    def iter_f_irreducibles_monotone_bottom(self):
        ...

    @implemented_at(endomorphisms.iter_f_irreducibles_monotone)
    def iter_f_irreducibles_monotone(self):
        ...

    '''
    @section
        Methods for endomorphisms that preserve lub
    '''

    @implemented_at(endomorphisms.f_is_lub)
    def f_is_lub(self):
        ...

    @implemented_at(endomorphisms.f_is_lub_pairs)
    def f_is_lub_pairs(self):
        ...

    @implemented_at(endomorphisms.iter_f_lub_pairs_bruteforce)
    def iter_f_lub_pairs_bruteforce(self):
        ...

    @implemented_at(endomorphisms.iter_f_lub_pairs)
    def iter_f_lub_pairs(self):
        ...

    @implemented_at(endomorphisms.iter_f_lub)
    def iter_f_lub(self):
        ...

    @cached_property
    @implemented_at(endomorphisms.num_f_lub_pairs)
    def num_f_lub_pairs(self):
        ...

    @implemented_at(endomorphisms.count_f_lub_pairs_bruteforce)
    def count_f_lub_pairs_bruteforce(self):
        ...

    @cached_property
    @implemented_at(endomorphisms.num_f_lub)
    def num_f_lub(self):
        ...

    @implemented_at(endomorphisms.count_f_lub)
    def count_f_lub(self):
        ...

    @implemented_at(endomorphisms.count_f_lub_bruteforce)
    def count_f_lub_bruteforce(self):
        ...

    @implemented_at(endomorphisms.f_is_lub_of_irreducibles)
    def f_is_lub_of_irreducibles(self):
        ...

    '''
    @section
        Methods and optimizations for distributive lattices
    '''

    @cached_property
    def is_distributive(self):
        return self.explain_non_distributive is None

    @cached_property
    def explain_non_distributive(self):
        'Find i, j, k that violate distributivity. None otherwise'
        n = self.n
        lub = self.lub
        glb = self.glb
        for i in range(n):
            diff = glb[i, lub] != lub[np.ix_(glb[i, :], glb[i, :])]
            if diff.any():
                j, k = next(zip(*np.where(diff)))  # type:ignore
                return (
                    f'Non distributive lattice:\n'
                    f'{i} glb ({j} lub {k}) = {i} glb {lub[j,k]} = '
                    f'{glb[i,lub[j,k]]} != {lub[glb[i,j],glb[i,k]]} = '
                    f'{glb[i,j]} lub {glb[i,k]} = ({i} glb {j}) lub ({i} glb {k})'
                )
        return None

    def assert_distributive(self):
        if not self.is_distributive:
            hook = lambda: print(self.explain_non_distributive)
            raise PosetExceptions.NotDistributiveException(hook)

    def iter_f_lub_distributive(self):
        'generate and interpolate all monotone functions over irreducibles'
        self.assert_distributive()
        yield from self.iter_f_irreducibles_monotone_bottom()

    def count_f_lub_distributive(self):
        self.assert_distributive()
        if self.n == 0:
            return 0
        n = self.n
        leq = self.leq
        geq_list = [[j for j in range(n) if leq[i, j]] for i in range(n)]
        m, m_topo, m_children = self.irreducible_components
        f = [None for _ in range(n)]
        f = cast(endomorphisms.PartialEndomorphism, f)

        def num(i: int):
            'num of monotone functions restricted to domain k_topo[i]'
            it = self._iter_f_monotone_restricted(
                f,
                m_topo[i],
                m_children[i],
                geq_list,
            )
            return sum(1 for _ in it)

        k_independent = [num(k) for k in range(m)]
        return reduce(lambda a, b: a * b, k_independent, 1)

    '''
    @section
        Methods and optimizations for modular lattices
    '''

    @cached_property
    def is_modular(self):
        return self.explain_non_modular is None

    @cached_property
    def explain_non_modular(self):
        'Find i, j, k that violate modularity. None otherwise'
        n = self.n
        lub = self.lub
        glb = self.glb
        problem = lambda i, j, k: (
            f'Non modular lattice:\n'
            f'{i} leq {k} and '
            f'{i} glb ({j} lub {k}) = {i} glb {lub[j,k]} = '
            f'{glb[i,lub[j,k]]} != {lub[glb[i,j],glb[i,k]]} = '
            f'{glb[i,j]} lub {glb[i,k]} = ({i} glb {j}) lub ({i} glb {k})')
        for i in range(n):
            diff = glb[i, lub] != lub[np.ix_(glb[i, :], glb[i, :])]
            if diff.any():
                issues: List[Tuple[int, int]]
                issues = list(zip(*np.where(diff)))  # type:ignore
                for j, k in issues:
                    if lub[i, k] == k:
                        return problem(i, j, k)
        return None

    def assert_modular(self):
        if not self.is_modular:
            hook = lambda: print(self.explain_non_modular)
            raise PosetExceptions.NotModularException(hook)

    '''
    @section
        Methods for high level (meta) relatives of self 
    '''

    @cached_property
    def meta_J(self):
        'subposet of join irreducibles'
        assert self.is_distributive
        return self.subgraph(self.irreducibles)

    @cached_property
    def meta_O(self):
        'distributive lattice of the closure of downsets of self'
        n = self.n
        leq = self.leq
        labels = self.labels
        P_down = [frozenset(i for i in range(n) if leq[i, j]) for j in range(n)]
        P_layer = [set() for i in range(n + 1)]
        for s in P_down:
            P_layer[len(s)].add(s)

        def iter_diff(a):
            n = len(a)
            yield from ((a[i], a[j]) for i in range(n) for j in range(i + 1, n))

        E = []
        layer: Sequence[Set] = []
        layer.append(set([frozenset()]))
        for k in range(n):
            layer.append(P_layer[k + 1])
            for u in P_layer[k + 1]:
                for below in layer[k]:
                    if below <= u:
                        E.append((below, u))
            for u, v in iter_diff(list(layer[k])):
                if u & v in layer[k - 1]:
                    above = u | v
                    layer[k + 1].add(above)
                    E.append((v, above))
                    E.append((u, above))
        nodes = list(set(u for u, v in E) | set(v for u, v in E))
        encode = {s: i for i, s in enumerate(nodes)}
        children = [[] for i in range(len(nodes))]
        for s, r in E:
            children[encode[r]].append(encode[s])
        label_of = lambda s: '{' + ','.join(self._label(*sorted(s))) + '}'
        labels = tuple(map(label_of, nodes))
        return self.__class__.from_children(children, labels=labels)

    def _label(self, *nodes):
        return tuple(self.labels[x] for x in nodes)

    def _meta_mat(self, F, leq_F):
        m = len(F)
        mat = np.zeros((m, m), dtype=bool)
        for i, j in cartesian(m, m):
            mat[i, j] = leq_F(F[i], F[j])
        mat.flags.writeable = False
        return mat

    @cached_property
    def meta_E(self):
        'lattice of join endomorphisms of self'
        elems = list(map(tuple, self.iter_f_irreducibles_monotone_bottom()))
        labels = tuple(','.join(self._label(*f)) for f in elems)
        return self.__class__.from_lambda(elems, self._leq_E, labels=labels)

    def _leq_E(self, f, g):
        'natural order of the space of endomorphisms'
        n = self.n
        leq = self.leq
        return all(leq[f[i], g[i]] for i in range(n))

    @cached_property
    def meta_JE(self):
        'poset of functions that are join irreducibles in meta_E'
        'this is equivalent to meta_E.meta_J'
        n = self.n
        leq = self.leq
        bot = self.bottom
        J = self.irreducibles
        f = lambda i, fi: tuple(bot if not leq[i, x] else fi for x in range(n))
        elems = [f(i, fi) for i in J for fi in J]
        labels = tuple(','.join(self._label(*f)) for f in elems)
        return self.__class__.from_lambda(elems, self._leq_E, labels=labels)

    @cached_property
    def meta_JJ(self):
        'poset of self upside down times self, i.e. (~self)*self'
        'with labels showing homomorphism with meta_O.meta_JE'
        n = self.n
        leq = self.leq
        elems = [(i, fi) for i in range(n) for fi in range(n)]
        label_of = lambda i, fi: f'f({i})={fi}'
        labels = tuple(label_of(*self._label(i, fi)) for i, fi in elems)

        def f_leq(tup_i, tup_j):
            i, fi = tup_i
            j, fj = tup_j
            return leq[j, i] and leq[fi, fj]

        return self.__class__.from_lambda(elems, f_leq, labels=labels)

    '''
    @section
        Constructors and operations between lattices
    '''

    @classmethod
    def total(cls, n: int):
        'total order of n elements'
        G = [[i - 1] if i > 0 else [] for i in range(n)]
        return cls.from_children(G)

    def __invert__(self):
        'flip the poset upside down'
        cls = self.__class__
        return cls.from_children(self.parents, labels=self.labels)

    def __add__(self, other: Poset):
        if isinstance(other, int):
            out = self.add_number(other)
        else:
            out = self.add_poset(other)
        return out

    def __mul__(self, other: Poset):
        if isinstance(other, int):
            out = self.mul_number(other)
        else:
            out = self.mul_poset(other)
        return out

    def __or__(self, other: Poset):
        if isinstance(other, int):
            out = self.or_number(other)
        else:
            out = self.or_poset(other)
        return out

    def __and__(self, other: Poset):
        if isinstance(other, int):
            out = self.and_number(other)
        else:
            out = self.and_poset(other)
        return out

    def add_poset(self, other: Poset):
        'stack other above self and connect all self.tops with all other.bottoms'
        cls = self.__class__
        n = self.n
        C = [
            *([j for j in Ci] for Ci in self.children),
            *([j + n for j in Ci] for Ci in other.children),
        ]
        for i in self.tops:
            for j in other.bottoms:
                C[j + n].append(i)
        return cls.from_children(C)

    def mul_poset(self, other: Poset):
        'poset standard multiplication'
        cls = self.__class__
        n = self.n
        m = other.n
        labels = [None] * (n * m)
        labels = cast(List[str], labels)
        G = [[] for i in range(n * m)]
        for i, j in cartesian(n, m):
            for k in self.children[i]:
                G[i + j * n].append(k + j * n)
            for k in other.children[j]:
                G[i + j * n].append(i + k * n)
            labels[i + j * n] = f'({self.labels[i]},{other.labels[j]})'
        return cls.from_children(G, labels=labels)

    def or_poset(self, other: Poset):
        'put other at the right of self without connections'
        cls = self.__class__
        n = self.n
        C = [
            *([j for j in Ci] for Ci in self.children),
            *([j + n for j in Ci] for Ci in other.children),
        ]
        return cls.from_children(C)

    def and_poset(self, other: Poset):
        'stack other above self and put self.tops * other.bottoms inbetween'
        cls = self.__class__
        n = self.n
        nodes = [
            *((-1, i) for i in self.non_tops),
            *((i, j) for i in self.tops for j in other.bottoms),
            *((n, j) for j in other.non_bottoms),
        ]
        C = {v: [] for v in nodes}
        for i in self.non_tops:
            for j in self.children[i]:
                C[(-1, i)].append((-1, j))
        for i in other.non_bottoms:
            for j in other.parents[i]:
                C[(n, j)].append((n, i))
        for i in self.tops:
            for j in self.children[i]:
                for k in other.bottoms:
                    C[(i, k)].append((-1, j))
        for i in other.bottoms:
            for j in other.parents[i]:
                for k in self.tops:
                    C[(n, j)].append((k, i))
        f = {node: i for i, node in enumerate(sorted(nodes))}
        children = [[] for i in range(len(f))]
        for i, Ci in C.items():
            for j in Ci:
                children[f[i]].append(f[j])
        return cls.from_children(children)

    def add_number(self, n: int):
        'add self with itself n times'
        assert isinstance(n, int) and n >= 0, f'{n}'
        cls = self.__class__
        if n == 0:
            out = cls.total(0)
        else:
            out = self._operation_number(lambda a, b: a + b, n)
        return out

    def mul_number(self, n: int):
        'multiply self with itself n times'
        assert isinstance(n, int) and n >= 0, f'{n}'
        cls = self.__class__
        if n == 0:
            out = cls.total(1)
        else:
            out = self._operation_number(lambda a, b: a * b, n)
        return out

    def or_number(self, n: int):
        'OR operation of self with itself n times'
        assert isinstance(n, int) and n >= 0, f'{n}'
        cls = self.__class__
        if n == 0:
            out = cls.total(0)
        else:
            out = self._operation_number(lambda a, b: a | b, n)
        return out

    def and_number(self, n: int):
        'AND operation of self with itself n times'
        assert isinstance(n, int) and n >= 0, f'{n}'
        cls = self.__class__
        if n == 0:
            out = cls.total(1)
        else:
            out = self._operation_number(lambda a, b: a & b, n)
        return out

    def _operation_number(self, operation, n: int):
        'operate self with itself n>=1 times. operation must be associative'
        if n == 1:
            out = self
        else:
            out = self._operation_number(operation, n // 2)
            out = operation(out, out)
            if n % 2 == 1:
                out = operation(out, self)
        return out

    '''
    @section
        Testing methods
    '''

    def _test_iters_diff(self, it1, it2):
        '''Compute set1 = set(it1)-set(it2) and set2 = set(it2)-set(it1)
        Assumes that the iterators do not repeat elements'''
        set1 = set()
        set2 = set()
        for x, y in zip(it1, it2):
            if x != y:
                if x in set2:
                    set2.discard(x)
                else:
                    set1.add(x)
                if y in set1:
                    set1.discard(y)
                else:
                    set2.add(y)
        for x in it1:
            set1.add(x)
        for y in it2:
            set2.add(y)
        return set1, set2

    def _test_iters(self, it1, it2):
        'Check if two iterators yield the same values'

        def timed(it, key):
            cnt = total = 0
            t = time.time()
            for i in it:
                total += time.time() - t
                yield i
                t = time.time()
                cnt += 1
            times[key] = total
            count[key] = cnt

        times = {}
        count = {}
        it1 = timed(it1, 0)
        it2 = timed(it2, 1)
        set1, set2 = self._test_iters_diff(it1, it2)
        same = not set1 and not set2
        reason = not same and (f'Iterators are different:\n'
                               f'Found by 1 not by 2: {set1}\n'
                               f'Found by 2 not by 1: {set2}')
        self._test_summary(times, count, same, reason)

    def _test_counts(self, f1, f2):
        times = {}
        count = {}
        t = time.time()
        count[0] = f1()
        times[0] = time.time() - t
        t = time.time()
        count[1] = f2()
        times[1] = time.time() - t
        same = count[0] == count[1]
        reason = not same and (f'Methods are different:\n'
                               f'Output of 1: {count[0]}\n'
                               f'Output of 2: {count[1]}')
        self._test_summary(times, count, same, reason)

    def _test_summary(self, times, count, same, reason):
        print(f'repr: {self}\n'
              f'hash: {hash(self)}\n'
              f'n: {self.n}\n'
              f'is_distributive: {self.is_distributive}\n'
              f'Time used by method 1: {round(times[0], 2)}s\n'
              f'Time used by method 2: {round(times[1], 2)}s\n'
              f'Elements found by method 1: {count[0]}\n'
              f'Elements found by method 2: {count[1]}\n'
              f'Same output: {same}\n')
        if not same:
            self.describe()
            raise Exception(reason)

    def _test_assert_distributive(self):
        try:
            self.assert_distributive()
        except PosetExceptions.NotDistributiveException:
            print(
                'The test can not be executed because the lattice is not distributive'
            )
            raise

    def test_iter_f_monotone(self, outfile=None):
        it1 = map(tuple, self.iter_f_monotone())
        it2 = map(tuple, self.iter_f_monotone_bruteforce())
        with Outfile(outfile):
            self._test_iters(it1, it2)

    def test_iter_f_monotone_bottom(self, outfile=None):
        it1 = map(tuple, self.iter_f_monotone_bottom())
        it2 = map(tuple, self.iter_f_monotone_bottom_bruteforce())
        with Outfile(outfile):
            self._test_iters(it1, it2)

    def test_iter_f_lub(self, outfile=None):
        it1 = map(tuple, self.iter_f_lub())
        it2 = map(tuple, self.iter_f_lub_bruteforce())
        with Outfile(outfile):
            self._test_iters(it1, it2)

    def test_iter_f_lub_pairs(self, outfile=None):
        it1 = map(tuple, self.iter_f_lub_pairs())
        it2 = map(tuple, self.iter_f_lub_pairs_bruteforce())
        with Outfile(outfile):
            self._test_iters(it1, it2)

    def test_iter_f_lub_distributive(self, outfile=None):
        self._test_assert_distributive()
        it1 = map(tuple, self.iter_f_lub())
        it2 = map(tuple, self.iter_f_lub_distributive())
        with Outfile(outfile):
            self._test_iters(it1, it2)

    def test_count_f_lub_distributive(self, outfile=None):
        self._test_assert_distributive()
        f1 = lambda: self.count_f_lub_distributive()
        f2 = lambda: self.count_f_lub_bruteforce()
        with Outfile(outfile):
            self._test_counts(f1, f2)

    '''
    @section
        Random generation of posets 
    '''

    @classmethod
    def random_poset(cls, n: int, p: float, seed=None):
        '''
        Generates a random poset.
        All posets (modulo labels) have positive probability of being generated.
        If p is close to 0, the poset is very sparse.
        If p is close to 1, the poset is very dense.
        '''
        R = np.random.RandomState(seed=seed)
        rel = np.zeros((n, n), dtype=bool)
        for i in range(n):
            for j in range(i + 1, n):
                if R.random() < p:
                    rel[i, j] = 1
        for i in range(n):
            rel[i, i] = 1
        rel.flags.writeable = False
        leq = Relation(rel).transitive_closure().rel
        poset = cls(leq, _validate=False)
        return poset

    @classmethod
    def random_lattice_czech(cls, n: int, seed=None):
        '''
        Description: http://ka.karlin.mff.cuni.cz/jezek/093/random.pdf
        '''
        lub = random_lattice_czech(n, seed)
        rel = (lub <= np.arange(n)[None, :])
        rel.flags.writeable = False
        poset = cls(rel, _validate=True)
        if len(poset.bottoms) >= 2:  # Collapse bottoms
            bottoms = poset.bottoms
            bot = bottoms[0]
            rel.flags.writeable = True
            for i in bottoms:
                rel[bot, i] = True
            rel.flags.writeable = False
            rel = Relation(rel).transitive_closure().rel
            poset = cls(rel, _validate=True)
            poset.assert_lattice()
        return poset

    # @classmethod
    # def random_modular(cls):
    #     return

    # @classmethod
    # def random_distributive(cls):
    #     return
    '''
    @section
        Methods related with entropy
    '''

    def count_antichains_bruteforce(self):
        return self.brute_downset_closure.n

    @cached_property
    def num_antichains(self):
        return self.count_antichains_bruteforce()

    @cached_property
    def brute_downset_closure(self):
        n = self.n
        leq = self.leq
        sets = set([frozenset()])
        last = set(
            frozenset(j for j in range(n) if leq[j, i]) for i in range(n))
        while last:
            curr = set(c for a in last
                       for b in last for c in (a | b, a & b) if c not in sets)
            sets |= last
            last = curr
        f = {s: i for i, s in enumerate(sorted(sets, key=lambda s: len(s)))}
        E = [(f[b], f[a]) for a in sets for b in sets if a < b]
        return self.__class__.from_down_edges(len(sets), E)

    '''
    @section
        Help and examples
    '''

    usage = '''
    Except for n, leq and _labels, all other attributes are
    lazy loaded and usually cached.
    
    Conventions:
        - child[i,j]==True iff j covers i (with no elements inbetween)
        - children[j] = [i for i in range(n) if leq[i,j]]
        - parents[i] = [j for j in range(n) if leq[i,j]]

        For lattices:
            - lub[i,j] is the least upper bound for i and j.
            - glb[i,j] is the greatest lower bound for i and j
    
    Requires external packages:
        - numpy
        - cached_property
        - pyhash
        - pydotplus (and graphviz 'dot' program)

    Why pyhash?
        Because it is stable (like hashlib) and fast (like hash).
        hashlib is not adequate because it adds an unnecessary computation footrint.
        hash(tuple(...)) is not adequate because it yields different
        results across several runs unless PYTHONHASHSEED is set
        prior to execution.
    
    Examples:

    V = Poset.from_parents([[1,2],[],[],[1]])
    V.show()
    V = (V|Poset.total(1)).meta_O
    V.show()
    print(V.is_distributive)
    print(V.num_f_lub_pairs)
    for f in V.iter_f_lub_pairs_bruteforce():
        V.show(f)
        print(f)
    V.meta_O.show()
    '''
    '''
    @section
        Unclassified methods that will probably dissapear in the future
    '''

    def decompose_series(self):
        n = self.n
        leq = self.leq
        cmp = leq | leq.T
        nodes = sorted(range(n), key=lambda i: leq[:, i].sum())
        cuts = [i for i in nodes if cmp[i, :].sum() == n]
        subs = [nodes[i:j] for i, j in zip(cuts, cuts[1:])]
        return [self.subgraph(sub) for sub in subs]

    @classmethod
    def examples(cls):
        examples = {}
        grid = [[], [0], [0], [1], [1, 2], [2], [3, 4], [4, 5], [6, 7]]
        grid.extend([[0], [0], [9, 2], [10, 1]])
        for i, j in [(3, 9), (5, 10), (6, 11), (7, 12)]:
            grid[i].append(j)
        examples['portrait-2002'] = cls.from_children(grid)
        examples['portrait-2002'].__dict__['num_f_lub'] = 13858
        grid = [[], [0], [0], [1], [1, 2], [2], [3, 4], [4, 5], [6, 7]]
        grid = [[j + 9 * (i >= 9) for j in grid[i % 9]] for i in range(18)]
        for i, j in [(9, 4), (10, 6), (11, 7), (13, 8)]:
            grid[i].append(j)
        examples['portrait-1990'] = cls.from_children(grid)
        examples['portrait-1990'].__dict__['num_f_lub'] = 1460356
        examples['T1'] = cls.from_children([[]])
        examples['T2'] = cls.from_children([[], [0]])
        #for k in range(1, 10):
        #    examples[f'2^{k+1}'] = examples[f'2^{k}'] * examples[f'2^{k}']
        #examples['tower-crane'] =
        #examples['tower-crane'] =
        return examples

    @cached_property
    def num_paths_matrix(self):
        B = C = self.child.astype(int)
        A = np.zeros_like(B)
        A[np.diag_indices_from(A)] = 1
        while C.sum():
            A = A + C
            C = np.matmul(C, B)
        return A

    @cached_property
    def num_ace(self):
        d = self.dist
        A = self.num_paths_matrix
        bot = A[self.bottom, :]
        top = A[:, self.top]
        bot_top = A[self.bottom, self.top]
        middle = ((d == 2) * (bot[:, None] * top[None, :])).sum()
        return 2 * bot_top + (middle if self.n > 2 else 0)

    @classmethod
    def all_lattices_adding(cls, n: int):
        E = [pair for i in range(1, n - 1) for pair in [(0, i), (i, n - 1)]]
        MN_poset = cls.from_up_edges(n, E)
        num = {MN_poset: 0}
        V = [MN_poset]
        G = {0: []}
        q = deque([MN_poset])
        while q:
            P = q.popleft()
            for Q in P.iter_add_edge():
                if Q not in num:
                    num[Q] = len(V)
                    V.append(Q)
                    G[num[Q]] = []
                    q.append(Q)
                G[num[P]].append(num[Q])
        E = [(i, j) for i in G for j in G[i]]
        poset_of_posets = cls.from_up_edges(len(V), E)
        return V, poset_of_posets
