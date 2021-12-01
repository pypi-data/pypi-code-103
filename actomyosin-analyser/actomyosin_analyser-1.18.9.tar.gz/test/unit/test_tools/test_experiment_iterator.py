import numpy as np
import pandas as pd
from actomyosin_analyser.tools.experiment_iterator import ExperimentIterator

MockDataReader = None


def test_assign_group_labels():
    a, b, iterator = create_iterator()

    iterator.assign_group_labels("a is {a} and b is {b}")
    labels = [g.label for g in iterator]
    for i in range(8):
        assert f"a is {a[i]} and b is {b[i]}" in labels, (a[i], b[i], labels)

    iterator.assign_group_labels("b is {b}")
    labels = [g.label for g in iterator]
    for i in range(8):
        assert f"b is {b[i]}" in labels


def create_iterator():
    a = [0.1, 0.2, 0.8, 0.4, 0.1, 0.2, 0.4, 0.8]
    b = [1, 1, 1, 1, 2, 2, 2, 2]
    experiment_index = pd.DataFrame(
        data=np.array([a, b]).transpose(),
        columns=['a', 'b']
    )
    experiment_index['b'] = experiment_index['b'].astype(int)
    iterator = ExperimentIterator(
        MockDataReader,
        [(experiment_index, ['a', 'b'])],
        simulation_folder_template="",
        exclude=[]
    )
    return a, b, iterator
