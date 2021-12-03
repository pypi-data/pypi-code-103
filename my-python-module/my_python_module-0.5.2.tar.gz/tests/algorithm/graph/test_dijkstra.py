#!/usr/bin/env python
# -*-coding:utf-8-*-


from my_python_module.algorithm.graph.weighted_dag import WeightedDAG


def test_dijkstra():
    graph = WeightedDAG()
    graph.add_edge(('1', '3'), 9)
    graph.add_edge(('1', '6'), 14)
    graph.add_edge(('1', '2'), 7)
    graph.add_edge(('2', '3'), 10)
    graph.add_edge(('6', '5'), 9)
    graph.add_edge(('5', '4'), 6)
    graph.add_edge(('3', '4'), 11)
    graph.add_edge(('2', '4'), 15)

    assert graph.dijkstra_shortest_path('1', '4') == ['1', '3', '4']
