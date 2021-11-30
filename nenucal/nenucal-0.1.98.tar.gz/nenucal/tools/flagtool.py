#!/usr/bin/env python

import os
import sys

import toml
import click

import numpy as np

import matplotlib as mpl
mpl.use('Agg')

import matplotlib.pyplot as plt

from nenucal import __version__

# Lazy loaded:
# - nenucal.msutils in most commands
# - nenucal.settings, nenucal.flagutils in ssins() and plot_ssins_result()
# - nenucal.delayflag in delay_flag()


mpl.rcParams['image.cmap'] = 'Spectral_r'
mpl.rcParams['image.origin'] = 'lower'
mpl.rcParams['image.interpolation'] = 'nearest'
mpl.rcParams['axes.grid'] = True

t_file = click.Path(exists=True, dir_okay=False)
t_dir = click.Path(exists=True, file_okay=False)


@click.group()
@click.version_option(__version__)
def main():
    ''' Flagging utilities: backup/restore/copy flags; flag with SSINS ...'''


@main.command('backup')
@click.argument('ms_in', type=t_dir)
@click.argument('backup_file')
def backup(ms_in, backup_file):
    ''' Backup FLAG from MS_IN to BACKUP_FILE'''
    from nenucal.msutils import FlagManager

    flag = FlagManager.load_from_ms(ms_in)
    flag.save(backup_file)


@main.command('restore')
@click.argument('ms_in', type=t_dir)
@click.argument('backup_file', type=t_file)
def restore(ms_in, backup_file):
    ''' Restore FLAG from BACKUP_FILE to MS_IN '''
    from nenucal.msutils import FlagManager

    flag = FlagManager.load(backup_file)
    flag.save_to_ms(ms_in)


@main.command('reset')
@click.argument('ms_ins', nargs=-1, type=t_dir)
def reset(ms_ins):
    ''' Reset all FLAG of MS_INS '''
    from nenucal.msutils import FlagManager

    for ms_in in ms_ins:
        FlagManager.reset(ms_in)


@main.command('copy')
@click.argument('ms_in', type=t_dir)
@click.argument('ms_out', type=t_dir)
def copy(ms_in, ms_out):
    ''' Copy FLAG from MS_IN to MS_OUT '''
    from nenucal.msutils import FlagManager

    flag = FlagManager.load_from_ms(ms_in)
    flag.save_to_ms(ms_out)


def plot_ssins_result(ms_filename, ms_data, mask, output_file):
    from nenucal import flagutils

    ss_spc_before = flagutils.get_ss_spc(ms_data.data, zero_mean=False)
    ss_spc_after = flagutils.get_ss_spc(np.ma.array(ms_data.data, mask=mask), zero_mean=False)

    vmin = np.quantile(ss_spc_after, 0.001)
    vmax = np.quantile(ss_spc_after, 0.999)

    fig, (ax1, ax2) = plt.subplots(ncols=2, sharey=True, figsize=(8, 3))
    ax1.imshow(ss_spc_before, aspect='auto', vmin=vmin, vmax=vmax)
    ax2.imshow(ss_spc_after, aspect='auto', vmin=vmin, vmax=vmax)
    ax1.set_ylabel('Freq index')
    ax1.set_xlabel('Time index')
    ax2.set_xlabel('Time index')
    ax1.set_title('Before')
    ax2.set_title('After')
    fig.suptitle(f'SSINS flagging result for {os.path.basename(ms_filename.strip("/"))}', y=1)

    fig.tight_layout()
    fig.savefig(output_file)


def plot_baseline_result(ms_filename, ms_data, mask, output_file):
    from libpipe import msutils

    def get_baseline_mask_map(ant1, ant2, mask):
        idx_freq_full_flag = (mask[:, :, :, 0].sum(axis=(1, 2)) == mask.shape[1] * mask.shape[2])
        ant_max = max([ant2.max(), ant1.max()])
        su = mask[~idx_freq_full_flag].sum(axis=(0, 1, 3))
        si = (mask[~idx_freq_full_flag].shape[0] * mask.shape[1] * mask.shape[3])
        return msutils.make_ant_matrix(ant1, ant2, 100. * su / si, a_max=ant_max)

    fig, (ax1, ax2) = plt.subplots(ncols=2, sharey=True, figsize=(7.5, 3.5))
    ax1.imshow(get_baseline_mask_map(ms_data.ant1, ms_data.ant2, ms_data.data.mask), vmin=0, vmax=100)
    im = ax2.imshow(get_baseline_mask_map(ms_data.ant1, ms_data.ant2, mask), vmin=0, vmax=100)
    plt.colorbar(im, ax=ax2)
    fig.tight_layout()
    ax1.set_ylabel('Ant 1')
    ax1.set_xlabel('Ant 2')
    ax2.set_xlabel('Ant 2')
    ax1.set_title('Before')
    ax2.set_title('After')
    fig.suptitle(f'SSINS flagging result for {os.path.basename(ms_filename.strip("/"))}', y=1)

    fig.tight_layout()
    fig.savefig(output_file)


def backup_restore(ms_in, backup_flag, restore_flag, backup_file):
    from libpipe import msutils

    h5_flag_backup = os.path.join(ms_in, backup_file)

    if backup_flag and restore_flag:
        print('Either backup or restore are allowed (not both).')
        sys.exit(1)

    if backup_flag:
        if os.path.exists(h5_flag_backup):
            print('Original flags have already been backed up')
        else:
            print('Backing up original flags ...')
            msutils.FlagManager.load_from_ms(ms_in).save(h5_flag_backup)

    if restore_flag:
        if not os.path.exists(h5_flag_backup):
            print('Can not restore: backup does not exist.')
            sys.exit(1)
        print('Restoring flags ...')
        msutils.FlagManager.load(h5_flag_backup).save_to_ms(ms_in)
        print(f'Done')
        sys.exit(0)


@main.command('ssins')
@click.argument('ms_in', type=t_dir)
@click.option('--umin', help='Min baseline (in meter)', type=float, default=20, show_default=True)
@click.option('--umax', help='Max baseline (in meter)', type=float, default=4000, show_default=True)
@click.option('--config', help='SSINS configuration file', type=t_file, default=None)
@click.option('--data_col', help='DATA column to run SSINS on', type=str, default='DATA')
@click.option('--dry_run', help='Do not apply flags', is_flag=True)
@click.option('backup_flag', '--backup', help='Backup flags before SSINS', is_flag=True)
@click.option('restore_flag', '--restore', help='Restore previously backup-ed flags', is_flag=True)
@click.option('--plot_dir', help='Plot directory', type=t_dir, default=None)
@click.option('--backup_file', help='Backup filename', type=str, default='flags_before_ssins.h5')
def ssins(ms_in, umin, umax, data_col, config, dry_run, backup_flag, restore_flag, plot_dir, backup_file):
    ''' Run the SSINS flagger algorithm on MS_IN '''
    from libpipe import msutils
    from nenucal import flagutils, settings

    if config is None:
        config = os.path.join(settings.TEMPLATE_DIR, 'ssins_config.toml')

    config = toml.load(config)

    backup_restore(ms_in, backup_flag, restore_flag, backup_file)

    print(f'Opening MS file {ms_in} ...')
    ms = msutils.MsDataCube.load(ms_in, umin, umax, data_col)

    if ms.weights is not None:
        ms.data = ms.data * (ms.weights) ** .5

    print(f'Flag before SSINS: {100. * ms.data.mask.sum() / ms.data.mask.size:.2f} %')

    print(f'Starting SSINS flagging ...')
    mask_ssins = np.sum([flagutils.ssins_flagger(ms.data, k, config) for k in config["n_time_avg"]], axis=0)
    mask = (mask_ssins + ms.data.mask).astype(bool)

    mask_time_freq = flagutils.time_freq_threshold_flagger(mask, config["time_freq_threshold"])
    mask_baseline = flagutils.baseline_threshold_flagger(mask, config["baseline_threshold"])
    mask_snaphot = flagutils.snapshot_threshold_flagger((mask + mask_time_freq + mask_baseline).astype(bool),
                                                        config["snapshot_threshold"])

    mask = (mask_ssins + ms.data.mask + mask_time_freq + mask_baseline + mask_snaphot).astype(bool)

    if plot_dir is not None:
        print(f'Plotting results ...')

        if not os.path.isdir(plot_dir):
            os.makedirs(plot_dir)

        file = os.path.basename(ms_in.strip('/')).split('.MS')[0]
        plot_ssins_result(ms_in, ms.data, mask, os.path.join(plot_dir, f'ssins_flag_{file}.png'))
        plot_baseline_result(ms_in, ms, mask, os.path.join(plot_dir, f'baseline_flag_{file}.png'))

    print(f'Flag after SSINS: {100. * mask.sum() / mask.size:.2f} %')

    if not dry_run:
        print(f'Saving to MS file {ms_in} ...')

        ms.save_flag(ms_in, mask)

    print(f'All done')


@main.command('delay_flagger')
@click.argument('ms_in', type=t_dir)
@click.option('--data_col', help='DATA column to run delay flagger on', type=str, default='DATA')
@click.option('--umin', help='Min baseline (in meter)', type=float, default=50, show_default=True)
@click.option('--umax', help='Max baseline (in meter)', type=float, default=400, show_default=True)
@click.option('--n_time_avg', help='Number of time slot to averages', type=int, default=50)
@click.option('--n_times', help='Number of time bins', type=int, default=20)
@click.option('--n_sigma_i', help='Stokes I n sigma threshold', type=int, default=6)
@click.option('--n_sigma_v', help='Stokes V n sigma threshold', type=int, default=6)
@click.option('backup_flag', '--backup', help='Backup flags before delay flagger', is_flag=True)
@click.option('restore_flag', '--restore', help='Restore previously backup-ed flags', is_flag=True)
@click.option('--plot_dir', help='Plot directory', type=t_dir, default=None)
@click.option('--plot_ps_all_baselines', is_flag=True)
@click.option('--backup_file', help='Backup filename', type=str, default='flags_before_delay_flag.h5')
@click.option('--dry_run', help='Do not apply flags', is_flag=True)
def delay_flagger(ms_in, data_col, umin, umax, n_time_avg, n_times, n_sigma_i, n_sigma_v,
                  backup_flag, restore_flag, plot_dir, plot_ps_all_baselines, backup_file, dry_run):
    ''' Run the delay flagger algorithm on MS_IN '''
    from nenucal import delayflag

    backup_restore(ms_in, backup_flag, restore_flag, backup_file)

    f = delayflag.DelayFlagger(ms_in, n_time_avg, data_col, umin, umax)
    res = f.do_flag(n_times, n_sigma_i, n_sigma_v)

    if plot_dir is not None:
        print(f'Plotting results ...')
        if plot_ps_all_baselines:
            f.plot_delay_ps_iv(plot_dir)
        f.plot_delay_flag(res, plot_dir)

    if not dry_run:
        f.save_flag(res)


if __name__ == '__main__':
    main()
