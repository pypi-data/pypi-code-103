from unittest import mock

import numpy as np

from nenucal import msutils


class MockTable(object):

    def __init__(self, data, keywords):
        self.data = data
        self.keywords = keywords

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass

    def getcol(self, col):
        return self.data[col]

    def getcell(self, col, i):
        return self.data[col][i]

    def nrows(self):
        return self.data[list(self.data.keys())[0]].shape[0]

    def putcol(self, col, newdata):
        self.data[col] = newdata

    def getkeyword(self, col):
        return self.keywords[col]

    def close(self):
        pass


class MockTables(object):

    def __init__(self):
        self.tables = dict()

    def set(self, name, data, keywords=None):
        self.tables[name] = (data, keywords)

    def table(self, name, **karg):
        return MockTable(*self.tables[name])


def test_get_info_from_ms_files():
    t = MockTables()
    t.set('a', {'TIME': np.arange(0, 16, 4), 'INTERVAL': np.ones(4) * 4}, {'SPECTRAL_WINDOW': 'SPECTRAL_WINDOW'})
    t.set('b', {'TIME': np.arange(8, 22, 4), 'INTERVAL': np.ones(4) * 4}, {'SPECTRAL_WINDOW': 'SPECTRAL_WINDOW'})
    t.set('c', {'TIME': np.arange(20, 40, 4), 'INTERVAL': np.ones(4) * 4}, {'SPECTRAL_WINDOW': 'SPECTRAL_WINDOW'})
    t.set('a/SPECTRAL_WINDOW', {'CHAN_FREQ': np.arange(100, 140, 10), 'CHAN_WIDTH': np.ones(10) * 4})
    t.set('b/SPECTRAL_WINDOW', {'CHAN_FREQ': np.arange(100, 140, 10), 'CHAN_WIDTH': np.ones(10) * 4})
    t.set('c/SPECTRAL_WINDOW', {'CHAN_FREQ': np.arange(100, 140, 10), 'CHAN_WIDTH': np.ones(10) * 4})

    with mock.patch.object(msutils, 'tables', t):
        d = msutils.get_info_from_ms_files(['a', 'b', 'c'])
        assert d['start_time'] == 0
        assert d['end_time'] == 36
        assert d['total_time'] == 12 + 12 + 16
        assert d['n_channels'] == 4
        assert d['chan_width'] == 4


def test_flag_manager(tmp_path):
    t = MockTables()
    time = np.arange(5)
    flag = np.array([0, 0, 1, 0, 1])
    freqs = np.arange(100, 140, 10)
    t.set('a', {'FLAG': flag, 'TIME': time}, {'SPECTRAL_WINDOW': 'sw'})
    t.set('b', {'FLAG': np.zeros(5), 'TIME': time}, {'SPECTRAL_WINDOW': 'sw'})
    t.set('a/SPECTRAL_WINDOW', {'CHAN_FREQ': freqs, 'CHAN_WIDTH': np.ones(10) * 4})
    t.set('b/SPECTRAL_WINDOW', {'CHAN_FREQ': freqs, 'CHAN_WIDTH': np.ones(10) * 4})

    with mock.patch.object(msutils, 'tables', t):
        fm = msutils.FlagManager.load_from_ms('a')
        assert np.allclose(fm.time, time)
        assert np.allclose(fm.flag, flag)
        assert np.allclose(fm.freqs, freqs)

        fm.save(tmp_path / 'test.h5')

        fm2 = msutils.FlagManager.load(tmp_path / 'test.h5')
        assert np.allclose(fm2.time, time)
        assert np.allclose(fm2.flag, flag)
        assert np.allclose(fm2.freqs, freqs)

        fm2.save_to_ms('b')

        fm3 = msutils.FlagManager.load_from_ms('b')
        assert np.allclose(fm3.time, time)
        assert np.allclose(fm3.flag, flag)
        assert np.allclose(fm3.freqs, freqs)


def test_slice_dim():
    l = np.random.randn(100, 20, 5)
    assert np.allclose(msutils.slice_dim(l, 1, slice(1, 3)), l[:, 1:3])
    assert np.allclose(msutils.slice_dim(l, 1, slice(1, None)), l[:, 1:])
    assert np.allclose(msutils.slice_dim(l, 0, slice(None, 20)), l[:20, :])
    assert np.allclose(msutils.slice_dim(l, 2, slice(None, -1)), l[:, :, :-1])
