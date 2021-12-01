# """This module includes methods to fine-tune the parameters of a sweep.
#
# The grid search provided by [ParameterGrid](grid.sdk.sweeps.grid_search_strategy.ParameterGrid)
# exhaustively generates candidates from a grid of parameter values specified
# with the param_grid parameter. For instance, the following param_grid:
#
#     param_grid = [
#         {'C': [1, 10, 100, 1000], 'kernel': ['linear']},
#         {'C': [1, 10, 100, 1000], 'gamma': [0.001, 0.0001], 'kernel': ['rbf']},
#     ]
#
# specifies that two grids should be explored: one with a linear kernel and C
# values in `[1, 10, 100, 1000]`, and the second one with an RBF kernel, and the
# cross-product of C values ranging in `[1, 10, 100, 1000]` and gamma values
# in `[0.001, 0.0001]`.
# """
from grid.sdk.sweeps.grid_search_strategy import ParameterGrid, ParameterSampler

__all__ = ["ParameterGrid", "ParameterSampler"]
