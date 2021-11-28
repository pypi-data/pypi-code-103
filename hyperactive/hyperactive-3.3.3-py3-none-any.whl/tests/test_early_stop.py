import time
import pytest
import numpy as np
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import cross_val_score
from sklearn.tree import DecisionTreeClassifier
from hyperactive import (
    Hyperactive,
    RandomSearchOptimizer,
    HillClimbingOptimizer,
)


def objective_function(para):
    score = -para["x1"] * para["x1"]
    return score


search_space = {
    "x1": np.arange(0, 100000, 0.1),
}


def test_early_stop_0():
    early_stopping = {
        "n_iter_no_change": 5,
        "tol_abs": 0.1,
        "tol_rel": 0.1,
    }

    hyper = Hyperactive()
    hyper.add_search(
        objective_function,
        search_space,
        n_iter=1000,
        initialize={"warm_start": [{"x1": 0}]},
        early_stopping=early_stopping,
    )
    hyper.run()


def test_early_stop_1():
    early_stopping = {
        "n_iter_no_change": 5,
        "tol_abs": None,
        "tol_rel": 5,
    }

    hyper = Hyperactive()
    hyper.add_search(
        objective_function,
        search_space,
        n_iter=1000,
        initialize={"warm_start": [{"x1": 0}]},
        early_stopping=early_stopping,
    )
    hyper.run()


def test_early_stop_2():
    early_stopping = {
        "n_iter_no_change": 5,
        "tol_abs": 0.1,
        "tol_rel": None,
    }

    hyper = Hyperactive()
    hyper.add_search(
        objective_function,
        search_space,
        n_iter=1000,
        initialize={"warm_start": [{"x1": 0}]},
        early_stopping=early_stopping,
    )
    hyper.run()


def test_early_stop_3():
    def objective_function(para):
        score = -para["x1"] * para["x1"]
        return score

    search_space = {
        "x1": np.arange(0, 100, 0.1),
    }

    n_iter_no_change = 5
    early_stopping = {
        "n_iter_no_change": n_iter_no_change,
    }

    hyper = Hyperactive()
    hyper.add_search(
        objective_function,
        search_space,
        n_iter=100000,
        initialize={"warm_start": [{"x1": 0}]},
        early_stopping=early_stopping,
    )
    hyper.run()

    search_data = hyper.results(objective_function)
    n_performed_iter = len(search_data)

    print("\n n_performed_iter \n", n_performed_iter)
    print("\n n_iter_no_change \n", n_iter_no_change)

    assert n_performed_iter == (n_iter_no_change + 1)


def test_early_stop_4():
    def objective_function(para):
        return para["x1"]

    search_space = {
        "x1": np.arange(0, 100, 0.1),
    }

    n_iter_no_change = 5
    early_stopping = {
        "n_iter_no_change": 5,
        "tol_abs": 0.1,
        "tol_rel": None,
    }

    start1 = {"x1": 0}
    start2 = {"x1": 0.1}
    start3 = {"x1": 0.2}
    start4 = {"x1": 0.3}
    start5 = {"x1": 0.4}

    warm_start_l = [
        start1,
        start1,
        start1,
        start1,
        start1,
        start2,
        start2,
        start2,
        start3,
        start3,
        start3,
        start4,
        start4,
        start4,
        start5,
        start5,
        start5,
    ]
    n_iter = len(warm_start_l)

    hyper = Hyperactive()
    hyper.add_search(
        objective_function,
        search_space,
        n_iter=n_iter,
        initialize={"warm_start": warm_start_l},
        early_stopping=early_stopping,
    )
    hyper.run()

    search_data = hyper.results(objective_function)
    n_performed_iter = len(search_data)

    print("\n n_performed_iter \n", n_performed_iter)
    print("\n n_iter_no_change \n", n_iter_no_change)

    assert n_performed_iter == n_iter


def test_early_stop_5():
    def objective_function(para):
        return para["x1"]

    search_space = {
        "x1": np.arange(0, 100, 0.01),
    }

    n_iter_no_change = 5
    early_stopping = {
        "n_iter_no_change": n_iter_no_change,
        "tol_abs": 0.1,
        "tol_rel": None,
    }

    start1 = {"x1": 0}
    start2 = {"x1": 0.09}
    start3 = {"x1": 0.20}

    warm_start_l = [
        start1,
        start1,
        start1,
        start1,
        start1,
        start2,
        start2,
        start2,
        start3,
        start3,
        start3,
    ]
    n_iter = len(warm_start_l)

    hyper = Hyperactive()
    hyper.add_search(
        objective_function,
        search_space,
        n_iter=n_iter,
        initialize={"warm_start": warm_start_l},
        early_stopping=early_stopping,
    )
    hyper.run()

    search_data = hyper.results(objective_function)
    n_performed_iter = len(search_data)

    print("\n n_performed_iter \n", n_performed_iter)
    print("\n n_iter_no_change \n", n_iter_no_change)

    assert n_performed_iter == (n_iter_no_change + 1)


def test_early_stop_6():
    def objective_function(para):
        return para["x1"]

    search_space = {
        "x1": np.arange(0, 100, 0.01),
    }

    n_iter_no_change = 5
    early_stopping = {
        "n_iter_no_change": 5,
        "tol_abs": None,
        "tol_rel": 10,
    }

    start1 = {"x1": 1}
    start2 = {"x1": 1.1}
    start3 = {"x1": 1.22}
    start4 = {"x1": 1.35}
    start5 = {"x1": 1.48}

    warm_start_l = [
        start1,
        start1,
        start1,
        start1,
        start1,
        start2,
        start2,
        start2,
        start3,
        start3,
        start3,
        start4,
        start4,
        start4,
        start5,
        start5,
        start5,
    ]
    n_iter = len(warm_start_l)

    hyper = Hyperactive()
    hyper.add_search(
        objective_function,
        search_space,
        n_iter=n_iter,
        initialize={"warm_start": warm_start_l},
        early_stopping=early_stopping,
    )
    hyper.run()

    search_data = hyper.results(objective_function)
    n_performed_iter = len(search_data)

    print("\n n_performed_iter \n", n_performed_iter)
    print("\n n_iter_no_change \n", n_iter_no_change)

    assert n_performed_iter == n_iter


def test_early_stop_7():
    def objective_function(para):
        return para["x1"]

    search_space = {
        "x1": np.arange(0, 100, 0.01),
    }

    n_iter_no_change = 5
    early_stopping = {
        "n_iter_no_change": n_iter_no_change,
        "tol_abs": None,
        "tol_rel": 10,
    }

    start1 = {"x1": 1}
    start2 = {"x1": 1.09}
    start3 = {"x1": 1.20}

    warm_start_l = [
        start1,
        start1,
        start1,
        start1,
        start1,
        start2,
        start2,
        start2,
        start3,
        start3,
        start3,
    ]
    n_iter = len(warm_start_l)

    hyper = Hyperactive()
    hyper.add_search(
        objective_function,
        search_space,
        n_iter=n_iter,
        initialize={"warm_start": warm_start_l},
        early_stopping=early_stopping,
    )
    hyper.run()

    search_data = hyper.results(objective_function)
    n_performed_iter = len(search_data)

    print("\n n_performed_iter \n", n_performed_iter)
    print("\n n_iter_no_change \n", n_iter_no_change)

    assert n_performed_iter == (n_iter_no_change + 1)
