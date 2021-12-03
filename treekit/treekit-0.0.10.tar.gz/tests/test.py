# -*- coding: utf-8 -*-

# Author: Daniel Yang <daniel.yj.yang@gmail.com>
#
# License: MIT

from treekit import binarytree, bst, Node

bt1 = binarytree([15, 7, 23, 3, 11, 19, 27, 1, 5, 9, 13, 17, 21, 25, 29, 0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30])
print(bt1.inorder)
print(bt1.preorder)
print(bt1.postorder)
print(bt1.levelorder)

bt1.flatten(target="preorder", inplace=True)
print(bt1.inorder)
print(bt1.preorder)
print(bt1.postorder)
print(bt1.levelorder)

bt2 = binarytree()
bt2.root = Node(-4)
bt2.root.left = Node(4)
bt2.root.right = Node(-5)
bt2.root.left.left = Node(-2)
bt2.root.left.right = Node(-3)
bt2.root.right.right = Node(3)
bt2.root.right.right.left = Node(1)
bt2.root.right.right.right = Node(9)
bt2.root.right.right.left.left = Node(6)
bt2.root.right.right.left.right = Node(7)
bt2.root.right.right.right.left = Node(-8)
bt2.root.right.right.right.right = Node(12)
max_path_sum, critical_node = bt2.find_maximum_path_sum()
print(f"The maximum path sum was found to be [{max_path_sum}] at the root node of [{critical_node}]")

bst1 = bst(h=6)
