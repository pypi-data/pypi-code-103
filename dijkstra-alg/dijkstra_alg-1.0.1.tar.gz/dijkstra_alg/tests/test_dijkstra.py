"""
Модуль для тестрирования dijkstra,
при помощи библиотеки pytest
"""

import dijkstra_alg
from ..dijkstra import dijkstra


def test_first_to_last():
    assert dijkstra(dijkstra_alg.__path__[0] +
                    '\\tests\\test_matrix.txt', 1, 5) == (12, (1, 2, 5))


def test_last_to_first():
    assert dijkstra(dijkstra_alg.__path__[0] +
                    '\\tests\\test_matrix.txt', 5, 1) == (12, (5, 2, 1))


def test_unconnected_nodes():
    assert dijkstra(dijkstra_alg.__path__[0] +
                    '\\tests\\test_matrix.txt', -1, 10)


def test_some_nodes():
    assert dijkstra(dijkstra_alg.__path__[0] +
                    '\\tests\\test_matrix.txt', 4, 1) == (7, (4, 0, 1))


def test_invalid_matrix():
    assert dijkstra(dijkstra_alg.__path__[0] +
                    '\\tests\\inv_test_matrix.txt', 1, 2)
