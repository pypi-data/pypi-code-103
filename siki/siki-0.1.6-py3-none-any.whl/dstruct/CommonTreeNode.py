# -*- coding: utf-8 -*-
# Author: Orlando Chen
# Created: Mar 03, 2020
# Modified: May 18, 2020

from siki.basics import Exceptions
from siki.basics import Convert
from siki.dstruct import ListExtern


class CommonTreeNode(object):

    def __init__(self, item_id, item_name):
        self._item_id = item_id
        self._item_val = item_name
        self._item_leaves = []
        self._item_root = None

    def root_id(self):
        if isinstance(self._item_root, CommonTreeNode):
            return self._item_root._item_id

    def self_id(self):
        return self._item_id

    def _append_node(self, leaf: object):
        if not isinstance(leaf, CommonTreeNode):
            raise Exceptions.InvalidParamException("node must be an instance of TreeNode")

        if self._check_id_valid(leaf._item_id):
            leaf._item_root = self
            self._item_leaves.append(leaf)

        else:
            raise Exceptions.InvalidParamException("node id can not be the same in tree")

    def search_append(self, item_id, item_name, item_fid):
        tree = self.search_tree(item_fid)

        if isinstance(tree, CommonTreeNode):
            node = CommonTreeNode(item_id, item_name)
            tree._append_node(node)

        return tree

    def search_delete(self, leaf_id):
        if not isinstance(leaf_id, type(self._item_id)):
            raise Exceptions.InvalidParamException("leaf id must be the same type of TreeNode id")

        leaf = self.search_tree(leaf_id)
        if leaf is None:
            return None  # nothing to delete

        root = leaf._item_root
        if isinstance(root, CommonTreeNode):
            return ListExtern.cherry_pick(root._item_leaves, leaf)

        else:  # the leaf is not real leaf, it is the root of tree
            return self

    def search_tree(self, leaf_id):
        if not isinstance(leaf_id, type(self._item_id)):
            raise Exceptions.InvalidParamException("leaf id must be the same type of TreeNode id")

        if self._item_id == leaf_id:  # found
            return self

        for leaf in self._item_leaves:   # this node is not we want
            if leaf.self_id() == leaf_id:  # found
                return leaf

            else:
                if len(leaf) > 0:
                    sub_leaf = leaf.search_tree(leaf_id)
                    if isinstance(sub_leaf, CommonTreeNode):
                        return sub_leaf

        return None  # nothing found

    def search_update(self, leaf_id, leaf_val):
        # search leaf if exists
        leaf = self.search_tree(leaf_id)

        if isinstance(leaf, CommonTreeNode):
            leaf._item_val = leaf_val

        return leaf

    def _check_id_valid(self, leaf_id):
        if not isinstance(leaf_id, type(self._item_id)):
            raise Exceptions.InvalidParamException("leaf id must be the same type of TreeNode id")

        if leaf_id == self._item_id:
            return False

        for leaf in self._item_leaves:
            if leaf.self_id() == leaf_id:
                return False

        return True

    def generate_tree(self):
        if isinstance(self._item_root, CommonTreeNode):
            output = {
                "id": self._item_id,
                "name": self._item_val,
                "fid": self._item_root._item_id
            }
        else:
            output = {
                "id": self._item_id,
                "name": self._item_val,
                "fid": None
            }

        # trying to add children to list
        if len(self._item_leaves) <= 0:
            return output

        else:
            subtrees = []
            for child in self._item_leaves:
                subtrees.append(child.generate_tree())

            output["leaves"] = subtrees
            return output

    def generate_list(self):
        if isinstance(self._item_root, CommonTreeNode):
            output = [{
                "id": self._item_id,
                "name": self._item_val,
                "fid": self._item_root._item_id
            }]
        else:
            output = [{
                "id": self._item_id,
                "name": self._item_val,
                "fid": None
            }]

        # trying to add children to list
        if len(self._item_leaves) <= 0:
            return output

        else:
            for child in self._item_leaves:
                output.extend(child.generate_list())

            return output

    def __str__(self):
        return Convert.dict_to_string(self.generate_tree())

    def __len__(self):
        return len(self._item_leaves)

# if __name__ == "__main__":
#     tree = CommonTreeNode(0, 'root')
#
#     tree.search_append(1, 'v1', 0)
#     tree.search_append(2, 'v2', 0)
#     tree.search_append(3, 'v3', 0)
#     tree.search_append(4, 'v4', 0)
#     tree.search_append(5, 'v5', 0)
#
#     tree.search_append(21, 'a1', 1)
#     tree.search_append(22, 'a2', 1)
#     tree.search_append(23, 'a3', 1)
#     tree.search_append(24, 'a4', 1)
#
#     tree.search_append(31, 'b1', 23)
#     tree.search_append(32, 'b2', 23)
#     tree.search_append(33, 'b3', 23)
#     tree.search_append(34, 'b4', 23)
#
#     # print generated tree
#     print(tree)
#
#     # delete tree from root
#     deleted = tree.search_delete(23)
#     print(deleted)
#
#     # update a leaf
#     tree.search_update(24, "changed val")
#     print(tree)
