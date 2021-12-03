#!/usr/bin/env python
# -*-coding:utf-8-*-

from my_python_module.algorithm.graph.directed_graph import DirectedGraph


def test_dg():
    dg = DirectedGraph()
    dg.add_edge(("a", "d"))
    dg.add_edge(("d", "c"))
    dg.add_edge(("c", "b"))
    dg.add_edge(("c", "e"))
    dg.add_edge(("c", "c"))
    dg.add_edge(('b', 'f'))

    assert dg.order() == 6
    assert dg.has_node('a')
    assert dg.has_edge(('a', 'd'))

    dg.del_edge(('c', 'e'))
    assert not dg.has_edge(('c', 'e'))

    dg.del_node('c')

    assert not dg.has_node('c')
    assert dg.order() == 5
