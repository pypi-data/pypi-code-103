import numpy as np


def _k_min(distances: np.array, k: int):
  """ Finds k-closest neighbours

  For each node, returns the distances of the k-closest neighbours.

  Parameters
  ----------
  distances : dense square 2D numpy array
      The distance matrix to evaluate.
  k : int
      number of distances to return.
      The 1st closest neighbour is every node itself.

  Returns
  -------
  - N by k numpy array
  """
  return np.partition(distances, k, axis=1)[:, :k+1]
