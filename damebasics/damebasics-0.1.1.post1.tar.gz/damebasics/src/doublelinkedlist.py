from node import Node

class DoubleLinkedList:
   def __init__(self):
       self.head = None
       self.prev = None
       self.next = None

   def add_first(self, data):
       if self.head is None:
           self.head  = Node(data)
       else:
           new_node = Node(data)
           new_node.next = self.head
           self.head = new_node

   def add_last(self, data):
       node = self.head
       if node is None:
           self.head = Node(data)
       else:
           while not node.next is None:
               node = node.next
           node.next = Node(data)

   def find(self, data):
       if self.head is None:
           return None
       else:
           node = self.head
           while not node is None:
               if node.data == data:
                   return node
               node = node.next
           return None

   def delete(self, data):
       if self.head is None:
           print("The list is empty")
       else:
           node = self.head
           node_prev = self.head
           while not node is None:
               if node.data == data:
                   node_prev.next = node.next
                   print("Node deleted")
                   return
               node_prev = node
               node = node.next
           print("Node with data", data, "was not found.")
           return

   def print_linked_list(self):
       print("--- LINKED LIST ---")
       if self.head is None:
           print("There are no elements in the current linked list")
       else:
           node = self.head
           while not node is None:
               print(node.data)
               node = node.next
           print("--------------")

   @staticmethod
   def iterate_backwards(node):
       if node.next:
           LinkedList.iterate_backwards(node.next)
           print(node.data)
       else:
           print(node.data)
           return

   def print_linked_list_backwards_v2(self):
       print("--- LINKED LIST BACKWARDS ---")
       if self.head is None:
           print("There are no elements in the current linked list")
       else:
           LinkedList.iterate_backwards(self.head)
       print("-----------------------------")

   def print_linked_list_backwards_v1(self):
       print("--- LINKED LIST BACKWARDS ---")
       if self.head is None:
           print("There are no elements in the current linked list")
       else:
           node_list = []
           node = self.head
           while not node is None:
               node_list.append(node)
               node = node.next
           for element in reversed(node_list):
               print(element.data)
           """for i in range(-1, -len(node_list) - 1, -1):
               print(node_list[i].data)"""


       print("-----------------------------")
