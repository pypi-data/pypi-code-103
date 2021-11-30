"""
A module containing masking functions.

These functions are used to extract edges from the complete distance matrix that
satisfy several criteria.

Functions
---------
distances :
  Returns a mask for all edges with a distance below the given threshold.
edges :
  Returns the k smallest edges.
mst :
  Returns the edges of the minimum spanning tree.
knn:
  Returns a mask for a knn-graph
knn_condensed:
  Same as knn, but with lower memory requirements
knn_condensed_par:
  Same as knn_condensed, but parallelized using Cython.
"""
from .distances import distances
from .edges import edges
from .mst import mst
from .knn import knn

try:
  from ._impl_fast import knn_condensed, knn_condensed_par
except ImportError:
  from ._impl_slow import knn_condensed
  from sys import stderr
  print("Falling back to slow stad.masks implementation", file=stderr)