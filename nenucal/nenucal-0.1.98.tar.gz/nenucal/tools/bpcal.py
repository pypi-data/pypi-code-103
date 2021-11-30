import os

import numpy as np
import astropy.stats as astats

import click

import matplotlib as mpl
mpl.use('Agg')

import matplotlib.pyplot as plt
from matplotlib.backends import backend_pdf

from nenucal import datahandler
from nenucal.delayflag import make_ps
from ps_eor import psutil

mpl.rcParams['image.cmap'] = 'Spectral_r'
mpl.rcParams['image.origin'] = 'lower'
mpl.rcParams['image.interpolation'] = 'nearest'
mpl.rcParams['axes.grid'] = True


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
        

def open_sol(file_h5):
    import losoto.h5parm
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

    sol_file.close()

    return GainSol(time, freqs, ant, directions, pol, amp, phase)


# def get_mean_gain(gain_sols):
#     ants = sorted(set([a for gain_sol in gain_sols for a in gain_sol.ant]))
#     gain_sols_m = np.zeros((1, len(gain_sols[0].freqs), len(ants), 1, 2), dtype=np.complex)
#     for i, ant in enumerate(ants):
#         d = np.concatenate([gain_sol.d[:, :, gain_sol.ant == ant, 0, :] for gain_sol in gain_sols if ant in gain_sol.ant])
#         gain_sols_m[0, :, i] = np.mean(astats.sigma_clip(d, axis=0), axis=0)

#     return gain_sols_m


def get_mean_gain(gain_sols):
    ants = sorted(set([a for gain_sol in gain_sols for a in gain_sol.ant]))
    gain_sols_m = np.zeros((1, len(gain_sols[0].freqs), len(ants), 1, 2), dtype=complex)
    for i, ant in enumerate(ants):
        ant_gain_sols = []
        for gain_sol in gain_sols:
            if ant in gain_sol.ant:
                d = gain_sol.d[:, :, gain_sol.ant == ant, 0]
                d = astats.sigma_clip(d.real, maxiters=10, sigma=5) + 1j * astats.sigma_clip(d.imag, maxiters=10, sigma=5)
                time_mask = astats.sigma_clip(d.std(axis=(1, 2, 3)), sigma=2).mask
                time_mask2 = astats.sigma_clip(d.mask.sum(axis=(1, 2, 3)), sigma=2).mask
                ant_gain_sols.append(d[~(time_mask | time_mask2), :, 0])

        gain_sols_m[0, :, i, 0] = np.mean(np.concatenate(ant_gain_sols), axis=0)

    return gain_sols_m


def save_h5(h5_file, time, freq, amps, phases, ant, direction='Main', pol=[]):
    import losoto.h5parm
    weights = np.ones_like(amps)
    
    print(ant)

    axis_vals = [time, freq, ant, ['[%s]' % direction], np.array(['XX', 'YY'])]
    axes_name = ['time', 'freq', 'ant', 'dir', 'pol']

    if os.path.exists(h5_file):
        os.remove(h5_file)
        
    print(time.shape, freq.shape, ant.shape, amps.shape, phases.shape)

    los_h5 = losoto.h5parm.h5parm(h5_file, readonly=False)
    try:
        los_h5.makeSolset('sol000')
        sol_set = los_h5.getSolset('sol000')
        sol_set.makeSoltab('amplitude', 'amplitude000', axesNames=axes_name, axesVals=axis_vals,
                           vals=amps, weights=weights)
        sol_set.makeSoltab('phase', 'phase000', axesNames=axes_name, axesVals=axis_vals, vals=phases, 
                           weights=weights)
    finally:
        los_h5.close()


def plot(freqs, gain_sols_m, ants, output_pdf, nrows=5):
    pdf = backend_pdf.PdfPages(output_pdf)

    for i in np.arange(np.ceil(gain_sols_m.shape[2] / nrows)):
        fig, axs = plt.subplots(figsize=(10, 15), nrows=nrows, sharex=True)
        for j, ax in enumerate(axs):
            k = int(i * nrows + j)
            if k >= gain_sols_m.shape[2]:
                continue
            ax.plot(freqs * 1e-6, np.abs(gain_sols_m[0, :, k, 0, :]))
            ax.text(0.05, 0.95, ants[k], transform=ax.transAxes, va='top', ha='left')
        axs[-1].set_xlabel('Frequency [MHz]')
        fig.tight_layout(pad=0)
        pdf.savefig(fig)
    pdf.close()


def plot_delay(freqs, gain_sols_m, ants, output_pdf, fmax=71e6, ncols=5, delay_max=7):
    nrows = int(np.ceil(gain_sols_m.shape[2] / 5))
    fig, axs = plt.subplots(figsize=(10, nrows * 2.25), ncols=ncols, nrows=nrows, sharex=True, sharey=True)
    axs = axs.flatten()
    idx = (freqs < fmax)
    gain_sols_m[np.isnan(gain_sols_m)] = 0
    for i, (ant, ax) in enumerate(zip(ants, axs)):
        delay = psutil.get_delay(freqs[idx]) * 1e6
        ps = make_ps(gain_sols_m[0, idx, i, 0, :], freqs[idx])
        ps = ps / ps.max()
        ax.plot(delay, ps)
        ax.set_xlim(0, delay_max)
        ax.set_yscale('log')
        ax.text(0.05, 0.95, ant, transform=ax.transAxes, va='top', ha='left')
    fig.tight_layout(pad=0)
    fig.savefig(output_pdf)


@click.command()
@click.argument('obs_ids', type=str)
@click.argument('output_h5', type=str)
@click.option('--config', '-c', help='Data handler configuration file', type=str,
              default='data_handler.toml', show_default=True)
@click.option('--input_h5_name', '-i', help='Name of the input h5 file', type=str,
              default='instrument_di_bp.h5', show_default=True)
@click.option('--data_level', '-l', help='Level of the data', type=str, default='L2_12C40S', show_default=True)
def main(obs_ids, output_h5, config, input_h5_name, data_level):
    dh = datahandler.DataHandler.from_file(config)

    all_gain_sols_m = []
    all_freqs = []
    obs_ids = dh.get_obs_ids(obs_ids)

    for sw in dh.get_spectral_windows():
        h5_files = [f'{k}/{input_h5_name}' for k in dh.get_all_ms_path(obs_ids, [data_level], [sw])]
        gain_sols = [open_sol(h5_file) for h5_file in h5_files]
        sw_gain_sols_m = get_mean_gain(gain_sols)
        all_gain_sols_m.append(sw_gain_sols_m)
        all_freqs.append(gain_sols[0].freqs)

    gain_sols_m = np.concatenate(all_gain_sols_m, axis=1)
    freqs = np.concatenate(all_freqs)
    ants = sorted(set([a for gain_sol in gain_sols for a in gain_sol.ant]))

    plot(freqs, gain_sols_m, ants, output_h5.replace('.h5', '') + '.pdf')
    plot_delay(freqs, gain_sols_m, ants, output_h5.replace('.h5', '') + '_delay.pdf')

    save_h5(output_h5, gain_sols[0].time[:1], freqs, np.abs(gain_sols_m), 
            np.angle(gain_sols_m), np.array(ants))


if __name__ == '__main__':
    main()
