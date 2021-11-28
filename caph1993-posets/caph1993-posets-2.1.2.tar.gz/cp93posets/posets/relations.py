from __future__ import annotations
from typing import Any, Dict, Generator, Iterable, List, Optional, Sequence, Set, Tuple, Union, cast
from cp93pytools.methodtools import cached_property
from ..algorithm_tarjan import Tarjan
from ..help_index import HelpIndex
from ..poset_wbools import WBools
import numpy as np
from ..numpy_types import npBoolMatrix, npUInt64Matrix
from ..algorithm_floyd_warshall import floyd_warshall
from .graphviz import graphviz


class Relation(HelpIndex, WBools):
    '''
    Class for boolean relation matrices intended mostly for asserting that
    a matrix relation can be used with the fully featured Poset class.
    '''

    def __init__(self, rel: npBoolMatrix):
        shape = tuple(rel.shape)
        assert len(shape) == 2, f'{shape}? matrix must be 2-dimensional'
        n = shape[0]
        assert shape == (n, n), f'{shape}? matrix must be squared'
        assert rel.dtype == bool, 'matrix must be a boolean numpy array'
        assert rel.flags.writeable == False, 'matrix must be read-only'
        self.n = rel.shape[0]
        self.rel = rel
        return

    '''
    @section
        Display methods
    '''

    def describe(self):
        self.show()
        print('Relation matrix:')
        print(self.rel.astype(int))
        print('Reflexive?', self.is_reflexive)
        print('Antisymmetric?', self.is_antisymmetric)
        print('Transitive?', self.is_transitive)
        return

    def show(self, labels=None, save=None):
        'Display the relation using graphviz. Groups SCCs together'
        scc_components, scc_edges = self.scc_reduction()
        if labels is None:
            labels = [f'{i}' for i in range(self.n)]
        n = len(scc_components)
        labels = ['-'.join(labels[i] for i in I) for I in scc_components]
        return graphviz(n, edges=scc_edges, labels=labels, save=save)

    '''
    @section
        Validation and boolean property methods
    '''

    @cached_property
    def is_poset(self):
        return (self.is_reflexive and self.is_antisymmetric and
                self.is_transitive)

    @cached_property
    def is_reflexive(self):
        rel = self.rel
        I, = np.where(~rel[np.diag_indices_from(rel)])
        why = I.size and f'Not reflexive: rel[{I[0]},{I[0]}] is False'
        return self._wbool(not why, why)

    @cached_property
    def is_antisymmetric(self):
        rel = self.rel
        eye = np.identity(self.n, dtype=np.bool_)
        I, J = np.where(rel & rel.T & ~eye)
        why = I.size and f'Not antisymmetric: cycle {I[0]}<={I[1]}<={I[0]}'
        return self._wbool(not why, why)

    @cached_property
    def is_transitive(self):
        rel = self.rel
        rel2 = np.matmul(rel, rel)
        I, J = np.where(((~rel) & rel2))
        why = I.size and (
            f'Not transitive: rel[{I[0]},{J[0]}] is False but there is a path')
        return self._wbool(not why, why)

    @classmethod
    def validate(cls, rel: npBoolMatrix, expect_poset: bool = False):
        instance = cls(rel)
        if expect_poset:
            instance.is_poset.assert_explain()
        return instance

    '''
    @section
        Graph operations
    '''

    def scc_reduction(self):
        n = self.n
        rel = self.rel
        G = [[] for _ in range(n)]
        for i in range(n):
            for j in range(n):
                if rel[i, j] and i != j:
                    G[i].append(j)
        return Tarjan(G).tarjan()

    def transitive_closure(self):
        if self.is_transitive:
            return self
        dist = floyd_warshall(self.rel, infinity=self.n)
        rel = (dist < len(dist))
        rel.flags.writeable = False
        return self.__class__(rel)

    def transitive_reduction(self, _assume_poset=False):
        ''''
        Compute in O(n^3) the transitive reduction of the given relation
        Raises an exception if the relation is not a poset
        The output relation is also known as "Hasse diagram"
        '''
        if not _assume_poset:
            self.is_poset.assert_explain()
        lt = self.rel.copy()
        lt[np.diag_indices_from(lt)] = False
        any_inbetween = np.matmul(lt, lt)
        child = lt & ~any_inbetween
        child.flags.writeable = False
        return self.__class__(child)
