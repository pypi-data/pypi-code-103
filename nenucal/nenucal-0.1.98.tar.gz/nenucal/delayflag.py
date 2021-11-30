import os

import numpy as np

import scipy.signal
import scipy.ndimage
import scipy.stats

import astropy.constants as const
import astropy.stats as astats
import astropy.time as at

from . import utils, msutils

import matplotlib as mpl
mpl.use('Agg')

import matplotlib.pyplot as plt


def flag_time(ms_cube, threshold=0.15):
    s = ms_cube.data.shape
    mask_freqs = (ms_cube.data.mask.sum(axis=(0, 3)) > threshold * (s[0] * s[3]))[None, :, :, None]
    ms_cube.data.mask = (ms_cube.data.mask + mask_freqs).astype(bool)
    ms_cube.data_dt.mask = (ms_cube.data_dt.mask + mask_freqs[:, ::2][:, :ms_cube.data_dt.mask.shape[1]]).astype(bool)


def hpass_flag(data, fill=0):
    d = data.filled(fill)
    k = scipy.signal.gaussian(150, 20)
    fit_r = scipy.ndimage.filters.convolve1d(d.real, k / k.sum(), mode='nearest', axis=0)
    fit_i = scipy.ndimage.filters.convolve1d(d.imag, k / k.sum(), mode='nearest', axis=0)
    fit = (fit_r + 1j * fit_i)
    return np.ma.array(d - fit, mask=data.mask)


def get_lst(obs_mjd, longitude=6.57):
    return at.Time(obs_mjd, scale='utc', format='mjd').sidereal_time('mean', longitude=longitude).value


def binned_sigma_clip(ru, d, bins=[0, 250], detrend_deg=0, **kargs):
    y = d.flatten()
    if detrend_deg > 0:
        detrend_y = astats.sigma_clip(y, sigma=6)
        d_fit = np.poly1d(np.polyfit(ru[~detrend_y.mask], y[~detrend_y.mask], detrend_deg))(ru)
        y = y - d_fit

    r = np.ma.zeros(y.shape)
    indices = np.digitize(ru, bins)
    for i in np.unique(indices):
        r[indices == i] = astats.sigma_clip(y[indices == i], **kargs)
    return np.ma.array(d, mask=r.mask.reshape(*d.shape))


def make_ps(d, freq, half=True, window_fct='blackmanharris'):
    s = d.shape
    w = scipy.signal.get_window(window_fct, s[0])[:, None]
    w = w / w.mean()

    if len(s) > 2:
        d = d.reshape((s[0], s[1] * s[2]))

    _, tf = utils.nudft(freq, utils.rmean(d), s[0], w=w)

    if len(s) > 2:
        tf = tf.reshape((s[0], s[1], s[2]))

    ps = abs(tf) ** 2

    if half:
        M = ps.shape[0]
        if utils.is_odd(M):
            ps = 0.5 * (ps[M // 2 + 1:] + ps[:M // 2][::-1])
        else:
            ps = 0.5 * (ps[M // 2 + 1:] + ps[1:M // 2][::-1])

    return np.ma.array(ps, mask=ps == 0)


class DelayFlaggerResult(object):

    def __init__(self, n_times, n_sigma_i, n_sigma_v, all_m_i_masked, all_m_v_masked):
        self.n_times = n_times
        self.n_sigma_i = n_sigma_i
        self.n_sigma_v = n_sigma_v
        self.all_m_i_masked = all_m_i_masked
        self.all_m_v_masked = all_m_v_masked


class DelayFlagger(object):

    def __init__(self, ms_file, ntime_avg, data_col='DATA', umin=50, umax=400):
        self.ms_file = ms_file
        self.ms_cube = msutils.MsDataCube.load(ms_file, umin, umax, data_col, n_time_avg=1)

        flag_time(self.ms_cube)
        m_vis_i, m_vis_v, m_vis_dt = self._get_stokes(ntime_avg)

        half = False
        window_fct = 'blackmanharris'

        self.all_ps_dt = make_ps(m_vis_dt.filled(0), self.ms_cube.freq, half=half, window_fct=window_fct)
        self.all_ps_v = make_ps(m_vis_v.filled(0), self.ms_cube.freq, half=half, window_fct=window_fct)
        self.all_ps_i = make_ps(hpass_flag(m_vis_i).filled(0), self.ms_cube.freq, half=half, window_fct=window_fct)

        self.delay = utils.get_delay(self.ms_cube.freq * 1e-6, half=half)

        freq = self.ms_cube.freq.mean()
        self.lamb = const.c.value / freq
        self.horizon = utils.get_wedge_delay(np.radians(90), self.ms_cube.bu / self.lamb, freq) * 1e6

    def _get_stokes(self, ntime_avg=50):
        m_vis_dt = self.ms_cube.data_dt[:, :, :, 0]
        m_vis_v = 0.5 * (-1j * (self.ms_cube.data[:, :, :, 1] - self.ms_cube.data[:, :, :, 2]))
        m_vis_i = 0.5 * (self.ms_cube.data[:, :, :, 0] + self.ms_cube.data[:, :, :, 3])

        m_vis_i, m_vis_i_n = msutils.mean_consecutive(m_vis_i, axis=1, n=ntime_avg, return_n=True)
        m_vis_i = m_vis_i * np.sqrt(m_vis_i_n)

        m_vis_v, m_vis_v_n = msutils.mean_consecutive(m_vis_v, axis=1, n=ntime_avg, return_n=True)
        m_vis_v = m_vis_v * np.sqrt(m_vis_v_n)

        m_vis_dt, m_vis_dt_n = msutils.mean_consecutive(m_vis_dt, axis=1, n=ntime_avg, return_n=True)
        m_vis_dt = m_vis_dt * np.sqrt(m_vis_dt_n)

        return m_vis_i, m_vis_v, m_vis_dt

    def do_flag(self, n_times, n_sigma_i, n_sigma_v):
        all_m_i_masked = self.filter_delay_ps(self.all_ps_i, n_times, n_sigma_i)
        all_m_v_masked = self.filter_delay_ps(self.all_ps_v, n_times, n_sigma_v)

        all_m_i_masked_1 = self.filter_delay_ps(self.all_ps_i, 1, n_sigma_i)
        all_m_v_masked_1 = self.filter_delay_ps(self.all_ps_v, 1, n_sigma_v)

        all_m_i_masked.mask = all_m_i_masked.mask + all_m_i_masked_1.mask
        all_m_v_masked.mask = all_m_v_masked.mask + all_m_v_masked_1.mask

        return DelayFlaggerResult(n_times, n_sigma_i, n_sigma_v, all_m_i_masked, all_m_v_masked)

    def save_flag(self, result):
        new_mask = self.ms_cube.data.mask.copy()
        print('Before:', new_mask.sum() / self.ms_cube.data.mask.size)

        all_m_mask = result.all_m_i_masked.mask + result.all_m_v_masked.mask
        idx = list(np.linspace(0, all_m_mask.shape[1] - 1, len(self.ms_cube.time)).astype(int))
        new_mask = (new_mask + all_m_mask[:, idx].T[None, :, :, None]).astype(bool)
        print('After flagging:', new_mask.sum() / self.ms_cube.data.mask.size)

        self.ms_cube.save_flag(self.ms_file, new_mask)

    def get_delay_power_ratio_map(self, all_ps, n_times):
        all_m = []
        for i in np.arange(len(self.ms_cube.ru)):
            mean = np.mean(self.all_ps_dt[:, :, i] / 4.)
            m = np.mean(all_ps[(abs(self.delay) > 1.2 * self.horizon[i]) & (abs(self.delay) < 4), :, i], axis=0) / mean
            if np.alltrue(m.mask):
                all_m.append(np.ones((n_times)) * np.nan)
                continue
            m[m.mask] = np.nanmean(m)
            if n_times is None:
                all_m.append(m)
            else:
                all_m.append(scipy.stats.binned_statistic(np.arange(len(m)), m.filled(0),
                                                          statistic=np.ma.mean, bins=n_times)[0])

        return np.array(all_m)

    def filter_delay_ps(self, all_ps, n_times, n_sigma):
        all_m = self.get_delay_power_ratio_map(all_ps, n_times)
        ru = np.repeat(self.ms_cube.ru, n_times)

        return binned_sigma_clip(ru, all_m, sigma=n_sigma, stdfunc=astats.mad_std)

    def plot_delay_flag(self, result, plot_dir):
        cmap = mpl.cm.get_cmap('magma')
        cmap.set_bad(color='blue')
        props = dict(boxstyle='round', facecolor='white', alpha=0.8)
        extent = [0, len(self.ms_cube.ru) - 1, 0, len(self.ms_cube.time) - 1]
        lsts = get_lst(self.ms_cube.time[:] / 3600. / 24.)

        fig, (axi1, axi2, axv1, axv2) = plt.subplots(nrows=4, figsize=(12, 11), sharex=True)

        for ax1, ax2, all_m_masked, stokes in [(axi1, axi2, result.all_m_i_masked, 'I'),
                                               (axv1, axv2, result.all_m_v_masked, 'V')]:
            im = ax1.imshow(all_m_masked.data[np.argsort(self.ms_cube.ru)].T,
                            aspect='auto', vmax=2, vmin=0.9, cmap=cmap, extent=extent)
            plt.colorbar(im, ax=ax1)
            ax1.set_ylabel('LST Time (hour)')
            ax1.set_yticks(np.linspace(0, len(self.ms_cube.time) - 1, result.n_times))
            ax1.set_yticklabels(['%.1f' % lsts[int(i)] for i in ax1.get_yticks()])

            txt = f'Stokes {stokes}: Max: {np.nanmax(all_m_masked.data):.1f}, \
            Med: {np.nanmedian(all_m_masked.data):.2f}'

            ax1.text(0.05, 0.95, txt, transform=ax1.transAxes, va='top', ha='left', bbox=props)

            ax2.imshow(all_m_masked[np.argsort(self.ms_cube.ru)].T, aspect='auto',
                       vmax=2, vmin=0.9, cmap=cmap, extent=extent)
            plt.colorbar(im, ax=ax2)
            ax2.set_ylabel('LST Time (hour)')
            ax2.set_xlabel('Baseline number')
            ax2.set_yticks(np.linspace(0, len(self.ms_cube.time) - 1, result.n_times))
            ax2.set_yticklabels(['%.1f' % lsts[int(i)] for i in ax2.get_yticks()])

            txt = f'Stokes {stokes}: Max: {all_m_masked.max():.1f}, Med: \
            {np.ma.median(all_m_masked):.2f}, Flagged: {all_m_masked.mask.sum() / all_m_masked.size * 100:.1f} %'

            ax2.text(0.05, 0.95, txt, transform=ax2.transAxes, va='top', ha='left', bbox=props)

            for ax in [ax1, ax2]:
                for l in [50, 100, 150]:
                    x = np.where(self.ms_cube.ru[np.argsort(self.ms_cube.ru)] / self.lamb > l)[0]
                    if len(x) > 0:
                        ax.axvline(x[0], c='red', ls='--')
                        ax.text(x[0], 0, str(l), c='red')

        fig.tight_layout()

        if not os.path.exists(plot_dir):
            os.makedirs(plot_dir)

        fig.savefig(plot_dir + f'/all_delay_ps_mask_i{result.n_sigma_i}_v{result.n_sigma_v}.pdf')

    def plot_delay_ps_iv(self, plot_dir):
        # stat_names = self.ms_cube.ant_name
        stat_names = np.array(['STA' + str(k) for k in np.arange(56)])
        nrows = int(np.ceil(self.all_ps_i.shape[2] / 5.))
        fig, axs = plt.subplots(ncols=5, nrows=nrows, sharex=True, sharey=True, figsize=(12, 1 + nrows * 2))

        all_noise_levels = []
        props = dict(boxstyle='round', facecolor='white', alpha=0.6)

        for i_ax, i in enumerate(np.argsort(self.ms_cube.ru)):
            ax = axs.flatten()[i_ax]
            txt = '%.2f / %s - %s' % (self.ms_cube.ru[i] / self.lamb, stat_names[self.ms_cube.ant1[i]]
                                      [3:], stat_names[self.ms_cube.ant2[i]][3:])

            if np.alltrue(self.ms_cube.data[:, :, i, 0].mask):
                all_noise_levels.append((np.nan, np.nan))
                ax.text(0.05, 0.95, txt, transform=ax.transAxes, va='top', ha='left', bbox=props)
                continue

            mean = np.mean(self.all_ps_dt[:, :, i] / 4.)

            ax.plot(self.delay, np.ma.mean(self.all_ps_v[:, :, i], axis=1))
            ax.plot(self.delay, np.ma.mean(self.all_ps_i[:, :, i], axis=1))
            ax.axvline(self.horizon[i], ls='--', c=utils.black)
            ax.axvline(- self.horizon[i], ls='--', c=utils.black)
            ax.axhline(mean, ls='--', c=utils.black)
            ax.set_yscale('log')
            ax.set_xlim(-4, 4)

            noise_r_i = np.mean(self.all_ps_i[(abs(self.delay) > 1.2 * self.horizon[i]) & (abs(self.delay) < 4), :, i]) / mean
            noise_r_v = np.mean(self.all_ps_v[(abs(self.delay) > 1.2 * self.horizon[i]) & (abs(self.delay) < 4), :, i]) / mean
            all_noise_levels.append((noise_r_i, noise_r_v))

            color = 'black'

            txt += '\n%s: I:%.1f V:%.1f' % (i, noise_r_i, noise_r_v)
            ax.text(0.05, 0.95, txt, transform=ax.transAxes, va='top', ha='left', bbox=props, color=color)

        fig.tight_layout(pad=0)
        fig.savefig(plot_dir + '/all_delay_ps_iv.pdf')
