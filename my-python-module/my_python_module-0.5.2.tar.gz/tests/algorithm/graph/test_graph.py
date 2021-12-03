#!/usr/bin/env python
# -*-coding:utf-8-*-


from my_python_module.algorithm.graph.directed_graph import DirectedGraph


def test_bfs_search_tree():
    graph_data = {
        'a': ['b', 'c'],
        'b': ['e', 'd'],
        'd': ['f'],
        'c': [],
        'e': [],
        'f': []
    }
    graph1 = DirectedGraph(graph_data)
    graph1_bfs_search_tree = graph1.bfs_search('a')
    assert graph1_bfs_search_tree.has_node('b')
    assert graph1_bfs_search_tree['b'].has_child('d')


def test_dfs_search_tree():
    graph1 = DirectedGraph()
    graph1.add_edge(("name", "symbol"))
    graph1.add_edge(("symbol", "name"))
    graph1.add_edge(("symbol", "mass"))
    graph1.add_edge(("name", "mass"))
    graph1.add_edge(("mass", "valume"))

    graph1_dfs_search_tree = graph1.dfs_search('name')
    assert graph1_dfs_search_tree.has_node('mass')

    graph1_dfs_search_tree2 = graph1.dfs_search('mass')
    assert not graph1_dfs_search_tree2.has_node('name')


def test_shortest_path():
    graph_data2 = {
        'you': ['alice', 'bob', 'claire'],
        'bob': ['anuj', 'peggy'],
        'alice': ['peggy'],
        'claire': ['thom', 'jonny'],
        'anuj': [],
        'peggy': [],
        'thom': [],
        'jonny': []
    }
    graph2 = DirectedGraph(graph_data2)

    graph2_shortest_path = graph2.dfs_shortest_path(start='you', end='anuj')
    assert graph2_shortest_path == ['you', 'bob', 'anuj']
    graph2_shortest_path2 = graph2.dfs_shortest_path(start='you', end='peggy')
    assert graph2_shortest_path2 == ['you', 'alice', 'peggy'] \
           or graph2_shortest_path2 == ['you', 'bob', 'peggy']

    graph2_shortest_path3 = graph2.bfs_shortest_path(start='you', end='anuj')
    assert graph2_shortest_path3 == ['you', 'bob', 'anuj']
