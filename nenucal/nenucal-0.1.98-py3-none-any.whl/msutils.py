import os

import numpy as np

import tables as h5_tables
from casacore import tables


class FlagManager(object):

    def __init__(self, time, freqs, flag):
        self.time = time
        self.freqs = freqs
        self.flag = flag

    @staticmethod
    def load_from_ms(ms_file):
        print(f'Loading flag from MS {ms_file} ...')
        with tables.table(ms_file, readonly=True) as t:
            flag = t.getcol('FLAG')
            time = t.getcol('TIME')
            freqs, _ = get_ms_freqs(ms_file)

        return FlagManager(time, freqs, flag)

    def save_to_ms(self, ms_file):
        print(f'Saving flag to MS {ms_file} ...')
        with tables.table(ms_file, readonly=False) as t:
            current_flag = t.getcol('FLAG')
            assert current_flag.shape == self.flag.shape
            t.putcol('FLAG', self.flag)

    @staticmethod
    def reset(ms_file):
        print(f'Reseting flag in MS {ms_file} ...')
        with tables.table(ms_file, readonly=False) as t:
            current_flag = t.getcol('FLAG')
            t.putcol('FLAG', np.zeros_like(current_flag, dtype=bool))

    @staticmethod
    def fully_flag(ms_file):
        print(f'Fully flagging MS {ms_file} ...')
        with tables.table(ms_file, readonly=False) as t:
            current_flag = t.getcol('FLAG')
            t.putcol('FLAG', np.ones_like(current_flag, dtype=bool))

    @staticmethod
    def load(h5_file):
        print(f'Loading flag file {h5_file} ...')
        with h5_tables.open_file(h5_file, 'r') as h5:
            flag = h5.root.flag.flag.read()
            freqs = h5.root.flag.freqs.read()
            time = h5.root.flag.time.read()

        return FlagManager(time, freqs, flag)

    def save(self, h5_file):
        print(f'Saving flag file {h5_file} ...')
        with h5_tables.open_file(h5_file, 'w') as h5:
            group = h5.create_group("/", 'flag', 'Flag cube')
            h5.create_array(group, 'flag', self.flag, "Flags")
            h5.create_array(group, 'freqs', self.freqs, "Frequencies (Hz)")
            h5.create_array(group, 'time', self.time, "Time")


class MsDataCube(object):

    def __init__(self, m_vis, m_vis_dt, time, weights, bu, ru, ant1, ant2, idx_baselines, freq, ant_name):
        self.data = m_vis
        self.data_dt = m_vis_dt
        self.time = time
        self.ru = ru
        self.bu = bu
        self.ant1 = ant1
        self.ant2 = ant2
        self.idx_baselines = idx_baselines
        self.freq = freq
        self.weights = weights
        self.ant_name = ant_name

    @staticmethod
    def load(ms_file, umin, umax, data_col, n_time_avg=1, flag_interstations=True, verbose=True, baselines='*&&',
             time_start_end=None):
        if verbose:
            print('Opening %s ...' % ms_file)
        if time_start_end is not None:
            start, end = time_start_end
            time_constraint = f'and TIME > {start} and TIME < {end}'
        else:
            time_constraint = ''
        with tables.taql(f"select from $ms_file where mscal.baseline($baselines) {time_constraint}") as t:
            uvw = t.getcol('UVW')
            data = t.getcol(data_col)
            flag = t.getcol('FLAG')
            time = t.getcol('TIME')
            a1 = t.getcol('ANTENNA1')
            a2 = t.getcol('ANTENNA2')

            weights = None
            if 'WEIGHT_SPECTRUM' in t.colnames() and t.iscelldefined('WEIGHT_SPECTRUM', 0):
                weights = t.getcol('WEIGHT_SPECTRUM')

        ant_name = tables.table(os.path.join(ms_file, 'ANTENNA')).getcol('NAME')

        baselines = a1 + 10000 * a2

        freq, _ = get_ms_freqs(ms_file)

        uu, vv, ww = uvw.T
        bu = np.sqrt(uu ** 2 + vv ** 2 + ww ** 2)
        ru = np.sqrt(uu ** 2 + vv ** 2)

        idx = (bu > umin) & (bu < umax)

        if is_lofar(ms_file) and flag_interstations:
            stat_name = np.array([k[:5] for k in ant_name])
            idx = idx & (stat_name[a1] != stat_name[a2])

        sel_baselines = np.unique(baselines[idx])

        if verbose:
            print('Selecting %s baselines between %s and %s meter' % (len(sel_baselines), umin, umax))

        idx_baselines = np.in1d(baselines, sel_baselines)
        n_time = data[idx_baselines].shape[0] // len(sel_baselines)

        vis = data[idx_baselines].reshape(n_time, len(sel_baselines), data.shape[1], data.shape[2])
        flag = flag[idx_baselines].reshape(n_time, len(sel_baselines), data.shape[1], data.shape[2])
        m_vis = np.ma.masked_array(vis, flag)

        time = time[idx_baselines].reshape(n_time, len(sel_baselines))[:, 0]
        if weights is not None:
            weights = weights[idx_baselines].reshape(n_time, -1, data.shape[1], data.shape[2])

        ant1 = a1[idx_baselines].reshape(n_time, len(sel_baselines))[0]
        ant2 = a2[idx_baselines].reshape(n_time, len(sel_baselines))[0]

        ru = ru[idx_baselines][:len(sel_baselines)]
        bu = bu[idx_baselines][:len(sel_baselines)]

        m_vis_dt = diff_consecutive(m_vis)

        if n_time_avg > 1:
            m_vis = mean_consecutive(m_vis, n=n_time_avg, axis=0)
            time = mean_consecutive(time, n=n_time_avg, axis=0)
            m_vis_dt = mean_consecutive(m_vis_dt, n=n_time_avg, axis=0)

        m_vis = m_vis.transpose((2, 0, 1, 3))
        m_vis_dt = m_vis_dt.transpose((2, 0, 1, 3))

        if weights is not None:
            weights = weights.transpose((2, 0, 1, 3))

        return MsDataCube(m_vis, m_vis_dt, time, weights, bu, ru, ant1, ant2, idx_baselines, freq, ant_name)

    def save_flag(self, ms, flag_new):
        with tables.table(ms, readonly=False) as t:
            flag_new = flag_new.transpose(1, 2, 0, 3)
            flag_new = flag_new.reshape(-1, flag_new.shape[2], flag_new.shape[3])

            flag = t.getcol('FLAG')
            flag[self.idx_baselines] = flag[self.idx_baselines] + flag_new

            t.putcol('FLAG', flag.astype(bool))


def slice_dim_idx(a, axis, s):
    idx = [slice(None) for k in range(a.ndim)]
    idx[axis] = s
    return tuple(idx)


def slice_dim(a, axis, s):
    return a[slice_dim_idx(a, axis, s)]


def mean_consecutive(a, n=2, axis=0, return_n=False):
    if isinstance(a, np.ma.MaskedArray):
        a_sum = np.add.reduceat(a.filled(0), np.arange(0, a.shape[axis], n), axis=axis)
        a_n_sum = np.add.reduceat((~a.mask).astype(int), np.arange(0, a.shape[axis], n), axis=axis)
        if return_n:
            return np.ma.array(a_sum / a_n_sum, mask=(a_n_sum == 0)), a_n_sum
        return np.ma.array(a_sum / a_n_sum, mask=(a_n_sum == 0))
    a_sum = np.add.reduceat(a, np.arange(0, a.shape[axis], n), axis=axis)
    return a_sum / float(n)


def diff_consecutive(a, axis=0):
    d = slice_dim(np.diff(a, axis=axis), axis, slice(None, None, 2))
    if isinstance(d, np.ma.MaskedArray) and d.mask.ndim == 0:
        d.mask = np.zeros_like(d)

    return d


def get_ms_freqs(ms_file):
    with tables.table(os.path.join(ms_file, 'SPECTRAL_WINDOW'), readonly=True, ack=False) as t_spec_win:
        freqs = t_spec_win.getcol('CHAN_FREQ').squeeze()
        chan_widths = t_spec_win.getcol('CHAN_WIDTH').squeeze()

    return freqs, chan_widths


def get_ms_time_interval(ms_file):
    with tables.table(ms_file) as t:
        return t.getcell('INTERVAL', 0)


def get_info_from_ms_files(files):
    t_start = []
    t_end = []
    t_total = 0

    for file in files:
        with tables.table(file, ack=False) as t:
            start = t.getcell('TIME', 0)
            end = t.getcell('TIME', t.nrows() - 1)
            t_int = t.getcell('INTERVAL', 0)
        t_start.append(start)
        t_end.append(end)
        t_total += end - start
        freqs, chan_widths = get_ms_freqs(file)
        n_chan = len(freqs)
        chan_width = chan_widths.mean()

    t_start = min(t_start)
    t_end = max(t_end)

    return {'start_time': t_start, 'end_time': t_end, 'int_time': t_int,
            'total_time': t_total, 'n_channels': n_chan, 'chan_width': chan_width}


def make_ant_matrix(ant1, ant2, m, a_max=54):
    m_map = np.ma.zeros((a_max, a_max)) * np.nan
    for a1, a2, i in zip(ant1, ant2, m):
        if (a1 < a_max) and (a2 < a_max):
            m_map[a1, a2] = i

    return m_map


def is_lofar(ms_file):
    return all(np.array(tables.table(os.path.join(ms_file, 'ANTENNA')).getcol('STATION')) == 'LOFAR')
