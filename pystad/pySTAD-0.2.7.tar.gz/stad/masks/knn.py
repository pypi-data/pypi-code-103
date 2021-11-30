import numpy as np
from stad import sparse


def knn(distances: np.ndarray, k: int):
  """
  Computes the mask for a knn-graph from a distance matrix.

  Parameters
  ----------
  distances : 2D numpy array
    Full square distance matrix
  k : int
    The number of neighbours to add to the graph.

  Returns
  -------
  A boolean 1D numpy array indicating the edges of the knn-graph
  """
  distances = distances.copy()
  np.fill_diagonal(distances, np.inf)
  threshold = np.partition(distances, k - 2, axis = 1)[:, k - 2]
  knn_mask = distances <= threshold[np.newaxis].T
  return sparse.squareform(knn_mask + knn_mask.T)
