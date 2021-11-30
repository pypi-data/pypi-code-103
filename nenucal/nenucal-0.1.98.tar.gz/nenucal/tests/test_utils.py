import numpy as np

from nenucal import utils


def test_chunks():
    for i in range(50):
        l = np.arange(np.random.randint(1, 200))
        n_max = np.random.randint(1, 100)
        chunks = list(utils.chunks(l, n_max))
        print(len(l), n_max, len(chunks))
        assert len(chunks) >= np.floor(len(l) / n_max)
        assert len(chunks) <= np.ceil(len(l) / n_max)
        assert np.allclose(np.concatenate(chunks), l)
