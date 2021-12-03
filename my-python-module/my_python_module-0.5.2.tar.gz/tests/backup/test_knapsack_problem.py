#!/usr/bin/env python
# -*-coding:utf-8-*-


from my_python_module.algorithm.problems.knapsack_problem import Item, Knapsack, greedy_algorithm, dynamic_programming

def test_greedy_algorithem():
    item_1 = Item('吉他', 1500, 15)
    item_2 = Item('音响', 3000, 30)
    item_3 = Item('笔记本电脑', 2000, 20)

    items = [item_1, item_2, item_3]
    knapsack = Knapsack(capacity=35)

    assert item_2 in greedy_algorithm(knapsack, items).items


def test_dynamic_programming():
    item_1 = Item('吉他', 1500, 15)
    item_2 = Item('音响', 3000, 30)
    item_3 = Item('笔记本电脑', 2000, 20)

    items = [item_1, item_2, item_3]
    knapsack = Knapsack(capacity=35)

    assert item_1 in dynamic_programming(knapsack, items).items
    assert item_3 in dynamic_programming(knapsack, items).items