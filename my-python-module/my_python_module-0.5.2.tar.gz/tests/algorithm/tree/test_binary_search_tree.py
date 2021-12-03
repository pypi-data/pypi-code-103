#!/usr/bin/env python
# -*-coding:utf-8-*-


from my_python_module.algorithm.tree import BinarySearchTree


def test_binary_search_tree():
    tree = BinarySearchTree(8)

    tree.insert(3)
    tree.insert(10)
    tree.insert(1)
    tree.insert(6)
    tree.insert(14)
    tree.insert(4)
    tree.insert(7)
    tree.insert(13)

    assert tree.find(4)
    assert not tree.find(50)
