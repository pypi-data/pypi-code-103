import numpy as np
from tqdm import tqdm
from hyperactive import Hyperactive


def objective_function(opt):
    score = -opt["x1"] * opt["x1"]
    return score


search_space = {
    "x1": list(np.arange(-100, 101, 1)),
}


def test_verb_0():
    hyper = Hyperactive(verbosity=False)
    hyper.add_search(objective_function, search_space, n_iter=15)
    hyper.run()


def test_verb_1():
    hyper = Hyperactive(verbosity=False)
    hyper.add_search(objective_function, search_space, n_iter=15, n_jobs=2)
    hyper.run()


def test_verb_2():
    hyper = Hyperactive(verbosity=["progress_bar"])
    hyper.add_search(objective_function, search_space, n_iter=15)
    hyper.run()


def test_verb_3():
    hyper = Hyperactive(verbosity=["progress_bar"])
    hyper.add_search(objective_function, search_space, n_iter=15, n_jobs=2)
    hyper.run()


def test_verb_4():
    hyper = Hyperactive(verbosity=["print_results", "print_times"])
    hyper.add_search(objective_function, search_space, n_iter=15)
    hyper.run()


def test_verb_5():
    hyper = Hyperactive(verbosity=["print_results", "print_times"])
    hyper.add_search(objective_function, search_space, n_iter=15, n_jobs=2)
    hyper.run()
