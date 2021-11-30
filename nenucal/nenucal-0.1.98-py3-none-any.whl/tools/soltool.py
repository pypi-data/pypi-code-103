#!/usr/bin/env python

import os
from multiprocessing import Pool

import click

import numpy as np

import losoto.h5parm

import matplotlib as mpl
mpl.use('Agg')

import matplotlib.pyplot as plt

from nenucal import __version__

# Lazy loaded:
# - astropy.stats and  astropy.convolution in astro_convolve


mpl.rcParams['image.cmap'] = 'Spectral_r'
mpl.rcParams['image.origin'] = 'lower'
mpl.rcParams['image.interpolation'] = 'nearest'
mpl.rcParams['axes.grid'] = True

t_file = click.Path(exists=True, dir_okay=False)


class GainSol(object):

    def __init__(self, time, freqs, ant, directions, pol, amp, phase):
        self.time = time
        self.freqs = freqs
        self.ant = ant
        self.dir = directions
        self.pol = pol
        self.amp = amp
        self.phase = phase
        self.d = self.amp * np.exp(1j * self.phase)


@click.group()
@click.version_option(__version__)
def main():
    ''' DPPP gains solution utilities ...'''


def ctoap(r, i):
    c = r + 1j * i
    return abs(c), np.angle(c)


def aptoc(amp, phase):
    c = amp * np.exp(1j * phase)
    return c.real, c.imag


def get_next_odd(f):
    f = int(np.ceil(f))
    return f + 1 if f % 2 == 0 else f


def clip_and_smooth(amp, phase, x_stddev, y_stddev, sigma_clip=5):
    import astropy.stats as astats
    from astropy.convolution import Gaussian2DKernel
    from astropy.convolution import convolve

    xs = get_next_odd(np.clip(10 * x_stddev, 25, 100))
    ys = get_next_odd(np.clip(10 * y_stddev, 25, 100))

    kernel = Gaussian2DKernel(x_stddev=x_stddev, y_stddev=y_stddev, x_size=xs, y_size=ys)
    real, imag = aptoc(amp, phase)

    real = astats.sigma_clip(real, sigma=sigma_clip, maxiters=10)
    imag = astats.sigma_clip(imag, sigma=sigma_clip, maxiters=10)

    real = convolve(real, kernel, boundary='extend')
    imag = convolve(imag, kernel, boundary='extend')

    return ctoap(real, imag)


def smooth_sol(sol, fwhm_time, main_fwhm_time, fwhm_freq, main_fwhm_freq, main_name='main', sigma_clip=5):
    dx_min = (sol.time[1] - sol.time[0]) / 60.
    dx_mhz = (sol.freqs[1] - sol.freqs[0]) * 1e-6

    s_amp = np.zeros_like(sol.amp)
    s_phase = np.zeros_like(sol.phase)

    for i_c in range(len(sol.dir)):
        if sol.dir[i_c].strip('[] ').lower() == main_name:
            c_fwhm_time = main_fwhm_time
            c_fwhm_freq = main_fwhm_freq
        else:
            c_fwhm_time = fwhm_time
            c_fwhm_freq = fwhm_freq
        stddev_time = c_fwhm_time / dx_min / 2.3
        stddev_freqs = c_fwhm_freq / dx_mhz / 2.3
        print(f'Smoothing {sol.dir[i_c]} with a Gaussian kernel of FWHM {c_fwhm_time} min and {c_fwhm_freq} MHz')

        for i_s in range(len(sol.ant)):
            for i_p in range(len(sol.pol)):
                a, p = clip_and_smooth(sol.amp[:, :, i_s, i_c, i_p], sol.phase[:, :, i_s, i_c, i_p], 
                                      stddev_freqs, stddev_time, sigma_clip=sigma_clip)
                s_amp[:, :, i_s, i_c, i_p] = a
                s_phase[:, :, i_s, i_c, i_p] = p

    return GainSol(sol.time, sol.freqs, sol.ant, sol.dir, sol.amp, s_amp, s_phase)


def open_sol(file_h5):
    sol_file = None
    try:
        sol_file = losoto.h5parm.h5parm(file_h5)
        solset = sol_file.getSolsets()[0]
        soltab, soltab_phase = solset.getSoltabs(useCache=True)

        ant = soltab.getAxisValues('ant')
        directions = soltab.getAxisValues('dir')
        time = soltab.getAxisValues('time')
        pol = soltab.getAxisValues('pol')

        freqs = soltab.getAxisValues('freq')

        weight = soltab.getValues(weight=True)[0].astype(bool)
        amp = np.ma.array(soltab.getValues(weight=False)[0], mask=~weight)
        phase = np.ma.array(soltab_phase.getValues(weight=False)[0], mask=~weight)

        amp = amp[:, :, :]
        phase = phase[:, :, :]
    finally:
        if sol_file is not None:
            sol_file.close()

    return GainSol(time, freqs, ant, directions, pol, amp, phase)


def save_sol(file_h5, sol):
    sol_file = None
    try:
        print('Saving solutions ...')
        sol_file = losoto.h5parm.h5parm(file_h5, readonly=False)
        solset = sol_file.getSolsets()[0]
        soltab, soltab_phase = solset.getSoltabs()
        
        soltab.setValues(sol.amp)
        soltab_phase.setValues(sol.phase)
    finally:
        if sol_file is not None:
            sol_file.close()
        print('Done')


def plot_sol(sol, dir, pol, data_type, filename):
    if data_type == 'Amplitude':
        v = sol.amp[:, :, :, dir, pol]
    elif data_type == 'Phase':
        v = sol.phase[:, :, :, dir, pol]
    else:
        print(f'Error: data type {data_type} unknown')
        return

    vmax = np.nanquantile(v[~v.mask & ~np.isnan(v) & (v != 0)], 0.999)
    vmin = np.nanquantile(v[~v.mask & ~np.isnan(v) & (v != 0)], 0.001)
    extent = [0, len(sol.time), sol.freqs.min() * 1e-6, sol.freqs.max() * 1e-6]

    n = v.shape[2]
    ncols, nrows = int(np.ceil(np.sqrt(n))), int(np.ceil(n / np.ceil(np.sqrt(n))))

    fig, axs = plt.subplots(ncols=ncols, nrows=nrows, sharey=True, figsize=(1 + 2 * ncols, 1 + 1.5 * nrows),
                            sharex=True)

    im = None

    for i, ax in zip(range(v.shape[2]), axs.flatten()):
        if v.shape[0] > 1 and v.shape[1] > 1:
            im = ax.imshow(v[:, :, i].T, aspect='auto', vmax=vmax, vmin=vmin, extent=extent)
        elif v.shape[0] == 1:
            ax.plot(sol.freqs * 1e-6, v[0, :, i].T)
        elif v.shape[1] == 1:
            ax.plot(v[:, 0, i].T)
        ax.text(0.025, 0.975, sol.ant[i], transform=ax.transAxes, fontsize=11, va='top')

    ylabel = ''
    xlabel = ''

    if v.shape[0] > 1 and v.shape[1] > 1 and im is not None:
        cax = fig.add_axes([0.6, 1.04, 0.39, 0.02])
        cax.set_xlabel(data_type)
        fig.colorbar(im, cax=cax, orientation='horizontal')
        xlabel = 'Time index'
        ylabel = 'Frequency [Mhz]'
    elif v.shape[0] == 1:
        xlabel = 'Frequency [MHz]'
        ylabel = data_type
    elif v.shape[1] == 1:
        xlabel = 'Time index'
        ylabel = data_type

    for ax in axs[:, 0]:
        ax.set_ylabel(ylabel)
    for ax in axs[-1, :]:
        ax.set_xlabel(xlabel)

    fig.tight_layout(pad=0)
    fig.savefig(filename, dpi=120, bbox_inches="tight")


@main.command('smooth')
@click.argument('sols', nargs=-1, type=t_file)
@click.option('--fwhm_time', help='Time coherence scale (min)', type=float, default=16)
@click.option('--fwhm_freq', help='Freq coherence scale (MHz)', type=float, default=2)
@click.option('--main_fwhm_time', help='Time coherence scale (min) for Main direction', type=float, default=20)
@click.option('--main_fwhm_freq', help='Freq coherence scale (MHz) for Main direction', type=float, default=4)
@click.option('--clip_nsigma', help='Clip solution above NSIGMA', type=float, default=4)
@click.option('--main_name', help='Name of the main direction', type=str, default='main')
def smooth(sols, fwhm_time, fwhm_freq, main_fwhm_time, main_fwhm_freq, clip_nsigma, main_name):
    ''' Smooth solutions with a Gaussian kernel'''
    for sol_file in sols:
        sol = open_sol(sol_file)
        s_sol = smooth_sol(sol, fwhm_time, main_fwhm_time, fwhm_freq, main_fwhm_freq, main_name=main_name, sigma_clip=clip_nsigma)
        save_sol(sol_file, s_sol)


@main.command('plot')
@click.argument('sols', nargs=-1, type=t_file)
@click.option('--plot_dir', help='Plot directory', type=str, default='sol_plots')
@click.option('--n_cpu', help='Number of CPU to use', type=str, default=4)
def plot(sols, plot_dir, n_cpu):
    ''' Plot solutions of the h5 files SOLS '''
    for sol_file in sols:
        sol = open_sol(sol_file)

        with Pool(n_cpu) as pool:
            for data_type in ['Amplitude', 'Phase']:
                for dir in range(len(sol.dir)):
                    for pol in range(len(sol.pol)):
                        filename = f'{data_type}_dir{sol.dir[dir]}_pol{sol.pol[pol]}.png'
                        path = os.path.join(os.path.dirname(sol_file), plot_dir, filename)

                        if not os.path.exists(os.path.dirname(path)):
                            os.makedirs(os.path.dirname(path))

                        # plot_sol(sol, dir, pol, data_type, path)
                        pool.apply_async(plot_sol, [sol, dir, pol, data_type, path])
            pool.close()
            pool.join()


if __name__ == '__main__':
    main()
