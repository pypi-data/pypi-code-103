# -*- coding: utf-8 -*-

# Author: Daniel Yang <daniel.yj.yang@gmail.com>
#
# License: MIT

from treekit import binarytree, bst

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

bst1 = bst(h=6)
