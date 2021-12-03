#!/usr/bin/env python
# -*-coding:utf-8-*-


from my_python_module.algorithm.tree import Tree


def test_tree():
    tree = Tree("a")
    tree.insert_child("a", "b")
    tree.insert_child("a", "c")
    tree.insert_child("b", "d")
    tree.insert_child("b", "e")
    tree.insert_child("b", "f")
    tree.insert_child("c", "g")
    tree.insert_child("c", "h")
    tree.insert_child("d", "i")
    tree.insert_child("e", "j")

    assert tree.has_node('c')
    assert tree['c'].has_child('g')

    assert tree['a'].level == 1
    assert tree['d'].level == 3

    assert [i.name for i in tree.shortest_path_to('h')] == ['a', 'c', 'h']
