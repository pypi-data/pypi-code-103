import numpy as np
from stad import sparse


def knn_distance_condensed(condensed_distances, k):
  """
  Computes the distance of each node's k-closest neighbour.

  Performs all operations on the condensed distance matrix. Uses less
  memory, but more compute time than the dense version.

  Parameters
  ----------
  condensed_distances : a condensed distance matrix (upper triangle)
  k : the closest neighbour to find

  Returns
  -------
  A 1D numpy vector with the distance to each node's k-closest neighbour.
  """
  n = np.ceil(np.sqrt(len(condensed_distances) * 2)).astype('int')
  res = np.zeros(n)
  if k <= 1:
    return res
  k -= 1
  for row in range(n):
    row_distances = np.asarray(
      [condensed_distances[sparse.sub2ind(row, i, n)]
       for i in range(n) if i != row]
    )
    res[row] = np.partition(row_distances, k)[k]
  return res
