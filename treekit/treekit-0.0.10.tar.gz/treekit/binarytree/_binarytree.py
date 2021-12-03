# -*- coding: utf-8 -*-

# Author: Daniel Yang <daniel.yj.yang@gmail.com>
#
# License: MIT


from typing import List, Union
from pyvis.network import Network # see also https://visjs.org/
from pathlib import Path
import webbrowser
import sys


class Node:
    def __init__(self, val: Union[float, int, str] = None, left = None, right = None, parent = None):
        self.val = val
        self.left = left    # left child pointer
        self.right = right  # right child pointer
        self.parent = parent # parent pointer

    def __repr__(self) -> str:
        return f"Node({self.val})"


class binarytree(object):
    def __init__(self, data: List[Union[float, int, str]] = [], *args, **kwargs):
        """
        https://en.wikipedia.org/wiki/Binary_tree#Arrays
        "Binary trees can also be stored in breadth-first order as an implicit data structure in arrays"
        """
        super().__init__(*args, **kwargs)
        self.treetype = 'Binary Tree'
        self.data_array = data.copy()
        self._construct_from_data_array()

    def _construct_from_data_array(self):
      nodes = [None if d is None else Node(d) for d in self.data_array] # 'if d is None' is important because sometimes d = 0 but we still want Node(0)
      for i in range(1, len(nodes)):
          curr = nodes[i]
          if curr:
              # for a geometric sequence, a = 1, r = 2, a_n = a*r**(n-1) => a_1=a, a_2=ar, a_3=ar^2, ...
              # Sn = a*(1-r^n)/(1-r) = (2^n - 1) => let's say parent index: Sn-1, child index: Sn
              # then it follows: (Sn - 1)/2 = 2^n - 2 = 2*(2^n-1 - 1) = Sn-1
              # See also: https://en.wikipedia.org/wiki/Binary_tree#Arrays
              # Thus, the indices for parent and child nodes follow this pattern
              parent = nodes[(i - 1) // 2]
              curr.parent = parent # only 1 parent
              if i % 2:
                  parent.left = curr
              else:
                  parent.right = curr
      self.root = nodes[0] if nodes else None
        
    def __repr__(self) -> str:
        if self.root:
            return f"Node({self.root.val})"

    # height — The number of edges on the longest path between a node and a descendant leaf.
    @property
    def height(self): # iteration-based binary tree path
      if not self.root:
        return 0
      max_height = -1
      stack = [(self.root, 0)]
      while stack:
          node, height = stack.pop()
          if node.right:
              stack.append((node.right, height+1))
          if node.left:
              stack.append((node.left, height+1))
          if not node.left and not node.right:
              max_height = max(height, max_height)
      return max_height

    def flatten(self, target: str = "preorder", inplace: bool = True):
      """
      Flatten the BT to linked list
      this will modify the links between existing nodes
      also known as Morris's traversal, or threaded binary tree
      """
      if not self.root:
          return None
      if inplace:
        node = self.root # to begin with. 'node' points to the same node instance that 'self.root' is pointed to, but it will point to other node instance later
        if target == "preorder":
          while node:
            if node.left:
              rightmost = node.left
              while rightmost.right:
                rightmost = rightmost.right
              rightmost.right = node.right
              node.right = node.left
              node.left = None
            node = node.right
        elif target == "inorder":
          while node:
            if node.left:
              rightmost = node.left
              while rightmost.right:
                rightmost = rightmost.right
              rightmost.right, original_left, original_parent = node, node.left, node.parent
              node.parent = rightmost
              node.left = None
              node = original_left
              node.parent = original_parent
              if original_parent:
                original_parent.right = node
            else:
              node = node.right
          while self.root.parent:
            self.root = self.root.parent
        else:
          print(f'Error: the target [{target}] has not been implemented')
          sys.exit(1)
      else:
        if target == "preorder":
          def dfs(curr):
            nonlocal head
            if curr:
              head.right = Node(curr.val)
              head = head.right
              dfs(curr.left)
              dfs(curr.right)
          new_root = Node()
          head = new_root
          dfs(self.root)
          return new_root.right
        else:
          print(f'Error: the target [{target}] has not been implemented')
          sys.exit(1)

    def find_maximum_path_sum(self):
      """
      returns the global maxium path sum and the node that has it
      """
      def max_NNG(node): # return the maximum non-negative gain from a given node
        nonlocal global_max, critical_node
        if not node:
          return 0
        left_maxNNG = max_NNG(node.left)
        right_maxNNG = max_NNG(node.right)
        local_max = node.val + left_maxNNG + right_maxNNG
        if local_max > global_max:
          global_max = local_max
          critical_node = node
        return max(0, node.val + max(left_maxNNG, right_maxNNG))
      global_max = float('-inf')
      critical_node = None
      max_NNG(self.root)
      return global_max, critical_node

    @property
    def inorder(self): # Don't use Morris Traversal as it will modify the original tree
        def dfs(curr):
          if curr:
            dfs(curr.left)
            res.append(curr.val)
            dfs(curr.right)
        res = []
        dfs(self.root)
        return res

    @property
    def preorder(self):
        def dfs(curr):
          if curr:
            res.append(curr.val)
            dfs(curr.left)
            dfs(curr.right)
        res = []
        dfs(self.root)
        return res

    @property
    def postorder(self):
        def dfs(curr):
          if curr:
            dfs(curr.left)
            dfs(curr.right)
            res.append(curr.val)
        res = []
        dfs(self.root)
        return res

    @property
    def levelorder(self):
      if not self.root:
        return
      this_level_array = [self.root]
      res = []
      while this_level_array:
        next_level_array = []
        for node in this_level_array:
          if node:
            res.append(node.val)
            next_level_array.append(node.left)
            next_level_array.append(node.right)
        this_level_array = next_level_array
      return res

    @property
    def data(self):
      return self.data_array

    def show(self, filename: str = 'output.html'):
        if not self.root:
            return
        def dfs(node, level=0):
            level += 1
            if node.left:
                g.add_node(node.left.val, shape="circle", level=level, title=f"left child node of Node({node.val}), level={level}")
                g.add_edge(node.val, node.left.val)
                dfs(node.left, level=level)
            else:
                hidden_left_n_id = f"{node.val}'s left child = None"
                g.add_node(hidden_left_n_id, level=level, hidden = True) # label = ' ', color = 'white')
                g.add_edge(node.val, hidden_left_n_id, hidden = True) # color = 'white')
            if node.right:
                g.add_node(node.right.val, shape="circle", level=level, title=f"right child node of Node({node.val}), level={level}")
                g.add_edge(node.val, node.right.val)
                dfs(node.right, level=level)
            else:
                hidden_right_n_id = f"{node.val}'s right child = None"
                g.add_node(hidden_right_n_id, level=level, hidden = True) # label = ' ', color = 'white')
                g.add_edge(node.val, hidden_right_n_id, hidden = True) # color = 'white')                    
        g = Network(width='100%', height='60%')
        g.add_node(self.root.val, shape="circle", level=0, title=f"root node of the tree, level=0")
        dfs(self.root)
        g.heading = f"{self.treetype}, height = {self.height}"
        g.set_options("""
var options = {
  "nodes": {
    "font": {
      "size": 40
    }
  },
  "edges": {
    "arrows": {
      "to": {
        "enabled": true
      }
    },
    "color": {
      "inherit": true
    },
    "smooth": false
  },
  "layout": {
    "hierarchical": {
      "enabled": true,
      "sortMethod": "directed"
    }
  },
  "physics": {
    "hierarchicalRepulsion": {
      "centralGravity": 0,
      "springConstant": 0.2,
      "nodeDistance": 80
    },
    "minVelocity": 0.75,
    "solver": "hierarchicalRepulsion"
  },
  "configure": {
      "enabled": true,
      "filter": "layout,physics" 
  }
}""")
        full_filename = Path.cwd() / filename
        g.write_html(full_filename.as_posix())
        webbrowser.open(full_filename.as_uri(), new = 2)
        return g


class bst(binarytree):

  def __init__(self, h=2, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.root = self.from_sortedarray(array = range(2**(h+1) - 1))
    self.data_array = self.levelorder # this needs improvement to include None in child node, i.e., it cannot use levelorder, but it needs to use 'values'
    self.treetype = 'Binary Search Tree'

  def from_sortedarray(self, array: List[Union[float, int, str]]) -> Node:
    if not array:
      return None
    mid = len(array) // 2
    root = Node(array[mid])
    root.left = self.from_sortedarray(array[:mid])
    root.right = self.from_sortedarray(array[mid+1:])
    return root

  def from_preorder(self, preorder: List[Union[float, int, str]]) -> Node:
        n = len(preorder)
        if not n:
            return None
        root = Node(preorder[0])         
        stack = [root, ]
        for i in range(1, n):
            node, child = stack[-1], Node(preorder[i])
            while stack and stack[-1].val < child.val: 
                node = stack.pop()
            if node.val < child.val:
                node.right = child 
            else:
                node.left = child 
            stack.append(child)
        return root

        