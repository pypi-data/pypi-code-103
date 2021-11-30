import numpy as np

from stad import sparse


def knn_condensed(condensed_distances: np.ndarray, k: int):
  """
  Computes the mask for a knn-graph from a condensed distance matrix.

  Maintains memory efficiency of condensed matrix at the cost of
  additional run time.

  Parameters
  ----------
  condensed_distances : 1D numpy array
    The pair-wise distances
  k : int
    The number of neighbours to add to the graph.

  Returns
  -------
  A boolean 1D numpy array indicating the edges of the knn-graph
  """
  n = np.ceil(np.sqrt(len(condensed_distances) * 2)).astype('int')
  res = np.zeros(len(condensed_distances), dtype='bool')
  if k <= 1:
    return res
  k -= 2
  for row in range(n):
    indices = np.asarray([
      sparse.sub2ind(row, i, n)
       for i in range(n) if i != row
    ])
    row_distances = condensed_distances[indices]
    threshold = np.partition(row_distances, k)[k]
    res[indices[row_distances <= threshold]] = True
  return res
