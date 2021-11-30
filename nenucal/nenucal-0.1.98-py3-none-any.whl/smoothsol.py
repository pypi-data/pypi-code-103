#!/usr/bin/env python

import os

import numpy as np

from scipy.interpolate import interp1d
from scipy.interpolate import SmoothBivariateSpline

import GPy

import astropy.stats as astats
import astropy.time as atime

from casacore import tables as pt

import losoto
import losoto.h5parm

import matplotlib as mpl
mpl.use('Agg')

import matplotlib.pyplot as plt

mpl.rcParams['image.cmap'] = 'Spectral_r'
mpl.rcParams['image.origin'] = 'lower'
mpl.rcParams['image.interpolation'] = 'nearest'
mpl.rcParams['axes.grid'] = True
mpl.rcParams['savefig.dpi'] = 150


def ctoap(r, i):
    c = r + 1j * i
    return abs(c), np.angle(c)


def aptoc(amp, phase):
    c = amp * np.exp(1j * phase)
    return c.real, c.imag


class Gains(object):

    def __init__(self, times, freqs, amp, phase, ant, pol, direction):
        self.times = times
        self.freqs = freqs
        self.amp = amp
        self.phase = phase
        self.ant = ant
        self.pol = pol
        self.direction = direction
        self.freqs_norm = freqs * 1e-6
        self.times_norm = times / 3600.

    @staticmethod
    def norm_dir(direction):
        return direction.strip('[]')

    @staticmethod
    def norm_dirs(directions):
        return np.array([Gains.norm_dir(k) for k in directions])

    @staticmethod
    def from_h5_files(h5_files, direction='Main'):
        amp_gains = []
        phase_gains = []
        times = []
        freqs = []
        ant = None
        pol = None

        for file_h5 in h5_files:
            sol_file = losoto.h5parm.h5parm(file_h5)
            solset = sol_file.getSolsets()[0]
            soltab, soltab_phase = solset.getSoltabs(useCache=True)

            idx_main = np.where(Gains.norm_dirs(soltab.getAxisValues('dir')) == Gains.norm_dir(direction))[0]
            if len(idx_main) == 0:
                continue
            idx_main = idx_main[0]

            ant = soltab.getAxisValues('ant')
            pol = soltab.getAxisValues('pol')

            freq = soltab.getAxisValues('freq')
            i_freq = [0, int(len(freq) / 2), len(freq) - 1]

            weight = soltab.getValues(weight=True)[0].astype(bool)
            amp = np.ma.mean(np.ma.array(soltab.getValues(weight=False)[0], mask=~weight), axis=0)[i_freq]
            phase = np.ma.mean(np.ma.array(soltab_phase.getValues(weight=False)[0], mask=~weight), axis=0)[i_freq]

            amp = amp[:, :, idx_main]
            phase = phase[:, :, idx_main]

            time = np.ma.array(soltab.getAxisValues('time'),
                               mask=~weight[:, :, :, idx_main, 0].mean(axis=(1, 2)).astype(bool))

            sol_file.close()

            if time.mask.sum() == time.size:
                print("Skipping", file_h5)
                continue

            time = [time.mean()] * len(i_freq)
            freq = freq[i_freq]

            amp_gains.extend(amp)
            phase_gains.extend(phase)
            times.extend(time)
            freqs.extend(freq)

        amp_gains = np.ma.array(amp_gains)
        phase_gains = np.ma.array(phase_gains)
        times = np.array(times)
        freqs = np.array(freqs)

        return Gains(times, freqs, amp_gains, phase_gains, ant, pol, direction)

    def build_gain_model(self, times_pre, freqs_pre, time_coh_scale_hour=20,
                         freq_coh_scale_mhz=10, method='gpr', var_snr=0.01):
        assert method in ['spline', 'gpr']

        kern = GPy.kern.RBF(2, ARD=True, lengthscale=[time_coh_scale_hour, freq_coh_scale_mhz])
        var_noise = var_snr * np.sqrt(0.5) * np.ma.median(self.amp)

        times_pre_norm = times_pre / 3600.
        freqs_pre_norm = freqs_pre * 1e-6
        X_pre = np.vstack([times_pre_norm.flatten(), freqs_pre_norm.flatten()]).T

        pre_amp = np.zeros((times_pre.size, self.amp.shape[1], self.amp.shape[2]))
        pre_phase = np.zeros((times_pre.size, self.amp.shape[1], self.amp.shape[2]))

        for pol_id in range(self.amp.shape[2]):
            for i in range(self.amp.shape[1]):
                m = ~self.amp[:, i, pol_id].mask
                if not np.all(m):
                    continue
                if np.all(m):
                    m = slice(None)
                freqs_norm = self.freqs[m] * 1e-6
                times_norm = self.times[m] / 3600.

                X = np.vstack((times_norm, freqs_norm)).T
                Y = np.dstack(aptoc(self.amp[m, i, pol_id], self.phase[m, i, pol_id])).reshape((X.shape[0], -1))

                mask_k_sigma = astats.sigma_clip(Y, sigma=4).mask.sum(axis=1) > 0
                X = X[~mask_k_sigma]
                Y = Y[~mask_k_sigma]

                Y_detrend = np.array([k - np.poly1d(np.polyfit(X[:, 1], Y[:, 0], 2))(X[:, 1]) for k in Y.T]).T
                mask_k_sigma = astats.sigma_clip(Y_detrend, sigma=4, axis=0).mask.sum(axis=1) > 0
                X = X[~mask_k_sigma]
                Y = Y[~mask_k_sigma]

                if method == 'gpr':
                    model = GPy.models.GPRegression(X, Y, kern, noise_var=var_noise)
                    Y_pre = model.predict(X_pre)[0].reshape(-1, 2)
                    Y_pre_amp, Y_pre_phase = ctoap(Y_pre[:, 0], Y_pre[:, 1])
                elif method == 'spline':
                    Y_pre_r = SmoothBivariateSpline(X[:, 0], X[:, 1], Y[:, 0], kx=1, ky=2)(
                        X_pre[:, 0], X_pre[:, 1], grid=False)
                    Y_pre_i = SmoothBivariateSpline(X[:, 0], X[:, 1], Y[:, 1], kx=1, ky=2)(
                        X_pre[:, 0], X_pre[:, 1], grid=False)
                    Y_pre_amp, Y_pre_phase = ctoap(Y_pre_r, Y_pre_i)

                pre_amp[:, i, pol_id] = Y_pre_amp
                pre_phase[:, i, pol_id] = Y_pre_phase

        return Gains(times_pre, freqs_pre, pre_amp, pre_phase, self.ant, self.pol, self.direction)

    def prepare_h5(self):
        time = np.unique(self.times)
        freq = np.unique(self.freqs)
        assert self.amp.shape[0] == len(time) * len(freq)

        amps = self.amp.reshape((len(freq), len(time), self.amp.shape[1], 1, self.amp.shape[2]))
        phases = self.phase.reshape((len(freq), len(time), self.amp.shape[1], 1, self.amp.shape[2]))

        amps = amps.transpose(1, 0, 2, 3, 4)
        phases = phases.transpose(1, 0, 2, 3, 4)

        return time, freq, amps, phases

    def save_to_h5(self, h5_file):
        time, freq, amps, phases = self.prepare_h5()
        weights = np.ones_like(amps)

        axis_vals = [time, freq, self.ant, ['[%s]' % self.direction], self.pol]
        axes_name = ['time', 'freq', 'ant', 'dir', 'pol']

        if os.path.exists(h5_file):
            os.remove(h5_file)

        los_h5 = losoto.h5parm.h5parm(h5_file, readonly=False)
        los_h5.makeSolset('sol000')
        sol_set = los_h5.getSolset('sol000')
        sol_set.makeSoltab('amplitude', 'amplitude000', axesNames=axes_name, axesVals=axis_vals,
                           vals=amps, weights=weights)
        sol_set.makeSoltab('phase', 'phase000', axesNames=axes_name, axesVals=axis_vals, vals=phases, weights=weights)
        los_h5.close()


class MultiGain(object):

    def __init__(self):
        self.dirs = dict()

    def add(self, direction, gains):
        self.dirs[direction] = gains

    @staticmethod
    def get_all_directions(h5_files):
        directions = set()
        for file_h5 in h5_files:
            sol_file = losoto.h5parm.h5parm(file_h5)
            solset = sol_file.getSolsets()[0]
            directions = directions.union(set(solset.getSoltabs()[0].getAxisValues('dir')))
            sol_file.close()
        return Gains.norm_dirs(directions)

    @staticmethod
    def from_h5_files(h5_files, directions=None):
        all_dirs = MultiGain.get_all_directions(h5_files)
        multi_gains = MultiGain()

        for direction in all_dirs:
            if directions is not None and direction not in directions:
                continue
            gains = Gains.from_h5_files(h5_files, direction=direction)
            multi_gains.add(direction, gains)

        return multi_gains

    def build_gain_model(self, times_pre, freqs_pre, time_coh_scale_hour, freq_coh_scale_mhz,
                         var_snr=0.01, method='gpr', directions=None):
        multi_model_gains = MultiGain()

        for direction, gains in self.dirs.items():
            if directions is not None and direction not in directions:
                continue
            model_gains = gains.build_gain_model(times_pre, freqs_pre, time_coh_scale_hour[direction],
                                                 freq_coh_scale_mhz[direction], method=method, var_snr=var_snr)
            multi_model_gains.add(direction, model_gains)

        return multi_model_gains

    def save_to_h5(self, h5_file):
        all_amps = []
        all_phases = []

        assert len(self.dirs) > 0

        for direction, gains in self.dirs.items():
            time, freq, amps, phases = gains.prepare_h5()
            all_amps.append(amps)
            all_phases.append(phases)

        amps = np.concatenate(all_amps, axis=3)
        phases = np.concatenate(all_phases, axis=3)
        weights = np.ones_like(amps)

        axis_vals = [time, freq, gains.ant, ['[%s]' % k for k in self.dirs.keys()], gains.pol]
        axes_name = ['time', 'freq', 'ant', 'dir', 'pol']

        if os.path.exists(h5_file):
            os.remove(h5_file)

        los_h5 = losoto.h5parm.h5parm(h5_file, readonly=False)
        los_h5.makeSolset('sol000')
        sol_set = los_h5.getSolset('sol000')
        sol_set.makeSoltab('amplitude', 'amplitude000', axesNames=axes_name, axesVals=axis_vals,
                           vals=amps, weights=weights)
        sol_set.makeSoltab('phase', 'phase000', axesNames=axes_name, axesVals=axis_vals, vals=phases, weights=weights)
        los_h5.close()


def copy_weights(in_h5, out_h5, direction=None):
    sol_file = losoto.h5parm.h5parm(in_h5)
    solset = sol_file.getSolsets()[0]
    soltab = solset.getSoltabs()[0]
    weight = soltab.getValues(weight=True, retAxesVals=False)
    time_sol = soltab.getAxisValues('time')
    freq_sol = soltab.getAxisValues('freq')
    if direction is not None:
        idx_main = np.where(soltab.getAxisValues('dir') == '[%s]' % direction)[0][0]
        weight = weight[:, :, :, idx_main, :][:, :, :, None, :]
    sol_file.close()

    out_sol_file = losoto.h5parm.h5parm(out_h5, readonly=False)
    solset = out_sol_file.getSolsets()[0]
    soltab_amp, soltab_phase = solset.getSoltabs()
    out_time_sol = soltab_amp.getAxisValues('time')
    out_freq_sol = soltab_amp.getAxisValues('freq')

    weight_out = weight.copy()
    if weight.shape[0] > 1:
        weight_out = interp1d(time_sol, weight_out, kind='nearest', axis=0)(out_time_sol)
    else:
        weight_out = np.repeat(weight_out, len(out_time_sol), axis=0)

    if weight.shape[1] > 1:
        weight_out = interp1d(freq_sol, weight_out, kind='nearest', axis=1)(out_freq_sol)
    else:
        weight_out = np.repeat(weight_out, len(out_freq_sol), axis=1)

    soltab_amp.setValues(weight_out, weight=True)
    soltab_phase.setValues(weight_out, weight=True)

    out_sol_file.close()


def get_directions(h5_file):
    sol_file = losoto.h5parm.h5parm(h5_file)
    solset = sol_file.getSolsets()[0]
    soltab = solset.getSoltabs()[0]
    directions = soltab.getAxisValues('dir')
    sol_file.close()

    return Gains.norm_dirs(directions)


def plot_smooth_gains(name, gains, plot_dir='.', time_coh_scale_hour=20,
                      freq_coh_scale_mhz=10, method='gpr'):
    times_pre = np.linspace(np.nanmin(gains.times) - 1e3, np.nanmax(gains.times) + 1e3, num=20)
    freqs_pre = np.linspace(np.nanmin(gains.freqs) - 1e6, np.nanmax(gains.freqs) + 1e6, num=20)
    times_pre, freqs_pre = np.meshgrid(times_pre, freqs_pre)

    gain_smooth = gains.build_gain_model(times_pre, freqs_pre, time_coh_scale_hour,
                                         freq_coh_scale_mhz, method)

    if not os.path.isdir(plot_dir):
        os.makedirs(plot_dir)

    for type in ['amp', 'phase']:
        extent = [gain_smooth.times_norm.min(), gain_smooth.times_norm.max(),
                  gain_smooth.freqs_norm.min(), gain_smooth.freqs_norm.max()]

        for pol_id, pol in enumerate(gains.pol):
            if type == 'amp':
                vmin = np.min(gain_smooth.amp[:, :, pol_id])
                vmax = np.max(gain_smooth.amp[:, :, pol_id])
                d_m = gain_smooth.amp
                d = gains.amp
            else:
                vmin = - np.pi
                vmax = np.pi
                d_m = gain_smooth.phase
                d = gains.phase

            fig, axs = plt.subplots(ncols=7, nrows=8, sharex=True, sharey=True,
                                    constrained_layout=False, figsize=(12, 14))
            axs = axs.flatten()

            for i in range(56):
                im = axs[i].imshow(d_m[:, i, pol_id].reshape(len(times_pre), len(freqs_pre)),
                                   aspect='auto', extent=extent, vmin=vmin, vmax=vmax)
                axs[i].scatter(gains.times_norm, gains.freqs_norm, c=d[:, i, pol_id].flatten(),
                               vmin=vmin, vmax=vmax, edgecolors='gray')
            #     axs[i].set_xlim(0, times_pre.max())
                axs[i].text(0.05, 0.97, str(i), transform=axs[i].transAxes, va='top', ha='left')

            fig.tight_layout(pad=2, h_pad=0, w_pad=0)
            axs[21].set_ylabel('Frequency [MHz]')
            axs[52].set_xlabel('Time [h]')
            fig.colorbar(im, ax=axs.tolist(), use_gridspec=True, fraction=0.02, pad=0.005, aspect=35)

            fig.savefig(f'{plot_dir}/smooth_gain_{name}_{type}_{pol}.png')


def get_time_freq(ms_file):
    with pt.table(ms_file) as t:
        time = np.unique(t.getcol('TIME'))
    with pt.table(ms_file + '/SPECTRAL_WINDOW') as t:
        freq = t.getcol('CHAN_FREQ').squeeze()

    return time, freq


def smooth_solutions(ms_files, parmdb_in, parmdb_out, time_scale=30, freq_scale=15,
                     time_scale_ateam=0.5, freq_scale_ateam=4, plot_dir='.', method='gpr'):
    h5_files = [os.path.join(f, parmdb_in) for f in ms_files]

    time, freq = get_time_freq(ms_files[0])
    observing_time = atime.Time(time.mean() / 3600. / 24., scale='utc', format='mjd')
    name = f'{observing_time.strftime("%Y%m%d")}_{int(freq.mean() * 1e-6)}MHz'

    print('Loading h5 files ...')
    gains = MultiGain.from_h5_files(h5_files)

    time_scale_dir = {}
    freq_scale_dir = {}
    for direction in gains.dirs.keys():
        if direction == 'Main':
            time_scale_dir[direction] = time_scale
            freq_scale_dir[direction] = freq_scale
        else:
            time_scale_dir[direction] = time_scale_ateam
            freq_scale_dir[direction] = freq_scale_ateam

    print('Plotting smooth gains ...')
    for direction, dir_gains in gains.dirs.items():
        plot_smooth_gains(name + f'_{direction}', dir_gains, plot_dir=plot_dir,
                          time_coh_scale_hour=time_scale_dir[direction],
                          freq_coh_scale_mhz=freq_scale_dir[direction], method=method)

    print('Building smooth gains version ...')
    for in_h5, ms_file in zip(h5_files, ms_files):
        directions = get_directions(in_h5)
        out_h5 = os.path.join(ms_file, parmdb_out)

        time, freq = get_time_freq(ms_file)
        time, freq = np.meshgrid(time, freq)

        gain_smooth = gains.build_gain_model(time, freq, time_coh_scale_hour=time_scale_dir,
                                             freq_coh_scale_mhz=freq_scale_dir,
                                             method=method, directions=directions)

        print(f'-> Saving to {out_h5} ...')
        gain_smooth.save_to_h5(out_h5)

        print(f'-> Copy weights ...')
        copy_weights(in_h5, out_h5)

    print('All done !')

