#!/usr/bin/env python
# -*-coding:utf-8-*-


from my_python_module.algorithm.graph.undirected_graph import UndirectedGraph


def test_ug():
    ug = UndirectedGraph()

    ug.add_edge({"a", "d"})

    ug.add_edge({"d", "c"})

    ug.add_edge({"c", "b"})

    ug.add_edge({"c", "e"})

    ug.add_edge({"c", "c"})

    assert ug.order() == 5
    assert ug.has_node('a')
    assert ug.has_edge({'c', 'e'})

    ug.del_edge(('c', 'c'))
    assert not ug.has_edge(('c', 'c'))

    ug.del_node('c')

    assert not ug.has_node('c')
    assert not ug.has_edge(('c', 'b'))
    assert ug.order() == 4
