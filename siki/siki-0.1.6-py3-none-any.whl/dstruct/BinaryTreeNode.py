# -*- coding: utf-8 -*-
# Author: Orlando Chen
# Created: Jun 1, 2020
# Modified: Jun 11, 2020

import pptree


class BinaryTreeNode:

    def __init__(self, index=None, data=None):

        self.left = None
        self.right = None
        self.root = None
        self.data = (index, data)

    def __str__(self):
        desc_str = f"[<data: {self.data}> :"

        if self.root is not None:
            desc_str += " T"

        if self.left is not None:
            desc_str += "L"

        if self.right is not None:
            desc_str += "R"

        return desc_str + "]"

    def search_append(self, index, data=None, allow_replace=False):
        if self.data:

            if index < self.data[0]:  # put the data to the left

                if self.left is None:
                    node = BinaryTreeNode(index, data)
                    node.root = self
                    self.left = node

                else:
                    self.left.search_append(index, data, allow_replace)

            elif index > self.data[0]:  # put the data to the right

                if self.right is None:
                    self.right = BinaryTreeNode(index, data)
                    self.right.root = self

                else:
                    self.right.search_append(index, data, allow_replace)

            else:
                if allow_replace:
                    self.data = (index, data)

                # else pass

        else:  # if current
            self.data = (index, data)

    def search_append_tree(self, sub_tree, allow_replace=False):
        if self.data:
            if sub_tree.data[0] < self.data[0]:  # put the tree to the left

                if self.left is None:
                    self.left = sub_tree
                    sub_tree.root = self

                else:
                    self.left.search_append_tree(sub_tree)

            elif sub_tree.data[0] > self.data[0]:  # put the tree to the right

                if self.right is None:
                    self.right = sub_tree
                    sub_tree.root = self

                else:
                    self.right.search_append_tree(sub_tree)

            else:
                if allow_replace:
                    self.left = sub_tree.left
                    self.right = sub_tree.right
                    self.data = sub_tree.data

                # else pass
        else:
            self.left = sub_tree.left
            self.right = sub_tree.right
            self.data = sub_tree.data

    def search_tree(self, index):
        if self.data[0] == index:
            return self

        elif index < self.data[0]:  # search by left side
            if self.left is not None:
                return self.left.search_tree(index)

            else:
                return None

        else:  # search by right side
            if self.right is not None:
                return self.right.search_tree(index)

            else:
                return None

    def search_update(self, index, data):
        leaf = self.search_tree(index)

        if leaf is not None:
            leaf.data = (index, data)

        return self

    def search_delete_bunch_tree(self, index):
        leaf = self.search_tree(index)

        if leaf is None:
            return None

        if leaf.root is not None:
            root = leaf.root

            # leaf is the left side of root?
            if leaf == root.left:
                root.left = None

            else:  # leaf is the right side of root
                root.right = None

            leaf.root = None

        # whatever leaf is none, return the leaf directly
        return leaf

    def search_delete_single_node(self, index):
        # delete a sub tree from tree
        leaf = self.search_delete_bunch_tree(index)

        if leaf is None:
            return None

        # generate a post traversal
        post_list = leaf.post_order_traversal()
        post_list = post_list[:-1]  # remove the last item from the list

        # generate a new tree
        sub_tree = self.re_balance(post_list)
        if sub_tree is not None:
            self.search_append_tree(sub_tree)

        leaf.left = leaf.right = None

        return leaf

    def pre_order_traversal(self):
        traversal_list = [self.data]

        if self.left is not None:
            left_children = self.left.pre_order_traversal()

            if isinstance(left_children, list):
                traversal_list.extend(left_children)

        if self.right is not None:
            right_children = self.right.pre_order_traversal()

            if isinstance(right_children, list):
                traversal_list.extend(right_children)

        return traversal_list

    def in_order_traversal(self):
        traversal_list = []

        if self.left is not None:
            left_children = self.left.in_order_traversal()

            if isinstance(left_children, list):
                traversal_list.extend(left_children)

        traversal_list.append(self.data)

        if self.right is not None:
            right_children = self.right.in_order_traversal()

            if isinstance(right_children, list):
                traversal_list.extend(right_children)

        return traversal_list

    def post_order_traversal(self):
        traversal_list = []

        if self.left is not None:
            left_children = self.left.in_order_traversal()

            if isinstance(left_children, list):
                traversal_list.extend(left_children)

        if self.right is not None:
            right_children = self.right.in_order_traversal()

            if isinstance(right_children, list):
                traversal_list.extend(right_children)

        traversal_list.append(self.data)

        return traversal_list

    def generate_tree_architecture(self, root_node=None):
        if root_node is None:
            the_node = pptree.Node(str(self))
        else:
            the_node = pptree.Node(str(self), root_node)

        if self.left is not None:
            self.left.generate_tree_architecture(the_node)

        if self.right is not None:
            self.right.generate_tree_architecture(the_node)

        return the_node

    def print_architecture(self):
        the_tree_node = self.generate_tree_architecture()
        pptree.print_tree(the_tree_node)

    def re_balance(self, the_list=None):
        if the_list is None:  # first time calling this method
            the_list = self.in_order_traversal()

        # if the in order list is empty
        if len(the_list) <= 0:
            return None  # nothing need to do

        # if the 
        if len(the_list) == 1:
            the_element = the_list[0]
            selected_root = BinaryTreeNode(the_element[0], the_element[1])
            return selected_root

        if len(the_list) == 2:
            the_left = the_list[0]
            the_right = the_list[1]
            selected_root = BinaryTreeNode(the_left[0], the_left[1])
            selected_root.search_append(the_right[0], the_right[1])
            return selected_root

        # pick a middle item from list
        selected_root = the_list[int(len(the_list) / 2)]
        selected_root = BinaryTreeNode(selected_root[0], selected_root[1])

        # splits the list into two parts
        left_list = the_list[:int(len(the_list) / 2)]
        right_list = the_list[int(len(the_list) / 2) + 1:]

        # assign sub tree to the root
        selected_root.search_append_tree(self.re_balance(left_list))
        selected_root.search_append_tree(self.re_balance(right_list))

        return selected_root


if __name__ == "__main__":
    tree = BinaryTreeNode(10)
    tree.search_append(7)
    tree.search_append(11)
    tree.search_append(5)
    tree.search_append(9)
    tree.search_append(8)
    tree.search_append(15)
    tree.search_append(14)
    tree.search_append(13)
    tree.search_append(1)
    tree.search_append(2)
    tree.search_append(3)
    tree.search_append(19)

    # print the architecture of tree
    # tree.print_architecture()
    tree = tree.re_balance()
    tree.print_architecture()

    print("--------------------------------------------------------------------------------------------------------")

    tree.search_delete_bunch_tree(15)
    tree.print_architecture()

    print("--------------------------------------------------------------------------------------------------------")

    tree.search_delete_single_node(2)
    tree.print_architecture()

    print("--------------------------------------------------------------------------------------------------------")

    tree = tree.re_balance()
    tree.print_architecture()

    print("--------------------------------------------------------------------------------------------------------")

    tree.search_update(5, "hello world")
    tree.print_architecture()
