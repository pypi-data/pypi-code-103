#!/usr/bin/env python

import click

import numpy as np

import astropy.units as u
from astropy.time import Time
from astropy.coordinates import SkyCoord

from casacore import tables

from nenucal import __version__
from nenucal import skymodel


t_file = click.Path(exists=True, dir_okay=False)
t_dir = click.Path(exists=True, file_okay=False)


@click.group()
@click.version_option(__version__)
def main():
    ''' NenuFAR sky model utilities: Build sky model from catalog; transform intrinsic to apparent sky model '''


@main.command('build')
@click.argument('ms_file', type=t_dir)
@click.option('--catalog', '-c', help='The catalog to fetch data from',
              type=click.Choice(['specfind', 'lcs165']), default='lcs165')
@click.option('--min_flux', '-m', help='Min Flux of the catalog at 74 MHz in Jy', default=0.5,
              type=float, show_default=True)
@click.option('--radius', '-r', help='Radius around the phase center', default=20, type=float, show_default=True)
@click.option('--out_file', '-o', help='Output filename', default='catalog.skymodel', type=str, show_default=True)
def build(ms_file, catalog, min_flux, radius, out_file):
    ''' Build an intrinsic sky model from catalog
    '''
    skymodel.build_sky_model_ms(ms_file, min_flux, radius, out_file, catalog=catalog)


@main.command('attenuate')
@click.argument('ms_file', type=t_dir)
@click.argument('input_models', type=t_file, nargs=-1, required=True)
@click.option('--min_flux', '-m', help='Minimum flux of the apparent sky model', type=float,
              default=0.5, show_default=True)
@click.option('--min_flux_patch', '-p', help='Minimum patch flux', type=float, default=20, show_default=True)
@click.option('--min_elevation', '-e', help='Minimum elevation in degree', type=float, default=10, show_default=True)
@click.option('--keep', '-k', multiple=True, help='Always keep specified patch')
@click.option('--remove', '-r', multiple=True, help='Always remove specified patch')
@click.option('--out_file', '-o', help='Output filename', default='apparent.skymodel', type=str, show_default=True)
def attenuate(ms_file, input_models, min_flux, min_flux_patch, min_elevation, keep, remove, out_file):
    ''' Make apparent sky model from intrinsic beam model
    '''
    ms = tables.table(ms_file)
    time = ms.getcol('TIME')
    mtime = np.array([np.quantile(time, 0.25), np.quantile(time, 0.5), np.quantile(time, 0.75)])
    mfmhz = tables.table(ms.getkeyword('SPECTRAL_WINDOW')).getcol('CHAN_FREQ').mean() * 1e-6
    phase_dir = tables.table(ms.getkeyword('FIELD')).getcol('PHASE_DIR').squeeze()

    coord_phase_dir = SkyCoord(ra=phase_dir[0] * u.rad, dec=phase_dir[1] * u.rad)
    observing_time = Time(mtime / 3600. / 24., scale='utc', format='mjd')

    sky_model = skymodel.concatenate(input_models)

    sky_model = skymodel.apply_nenufar_beam(sky_model, observing_time, coord_phase_dir, mfmhz)

    sky_model = skymodel.edit_model(sky_model, observing_time, min_flux=min_flux, min_flux_patch=min_flux_patch, 
                                    min_elevation_patch=min_elevation, always_keep=keep, always_remove=remove)

    print(f'Saving apparent sky model to {out_file} ...')
    sky_model.write(out_file, clobber=True)
    print('All done !')


@main.command('concatenate')
@click.argument('ms_file', type=t_dir)
@click.argument('input_models', type=t_file, nargs=-1, required=True)
@click.option('--min_flux', '-m', help='Minimum flux of the apparent sky model', type=float,
              default=0.5, show_default=True)
@click.option('--min_flux_patch', '-p', help='Minimum patch flux', type=float, default=20, show_default=True)
@click.option('--min_elevation', '-e', help='Minimum elevation in degree', type=float, default=10, show_default=True)
@click.option('--keep', '-k', multiple=True, help='Always keep specified patch')
@click.option('--remove', '-r', multiple=True, help='Always remove specified patch')
@click.option('--out_file', '-o', help='Output filename', default='apparent.skymodel', type=str, show_default=True)
def concatenate(ms_file, input_models, min_flux, min_flux_patch, min_elevation, keep, remove, out_file):
    ''' Concatenate multiple sky models file into one
    '''
    ms = tables.table(ms_file)
    time = ms.getcol('TIME')
    mtime = np.array([np.quantile(time, 0.25), np.quantile(time, 0.5), np.quantile(time, 0.75)])
    observing_time = Time(mtime / 3600. / 24., scale='utc', format='mjd')

    sky_model = skymodel.concatenate(input_models)

    sky_model = skymodel.edit_model(sky_model, observing_time, min_flux=min_flux, min_flux_patch=min_flux_patch, 
                                    min_elevation_patch=min_elevation, always_keep=keep, always_remove=remove)

    print(f'Saving concatenated sky model to {out_file} ...')
    sky_model.write(out_file, clobber=True)
    print('All done !')


@main.command('set_patch_name')
@click.argument('input_model', type=t_file)
@click.argument('patch_name', type=str)
@click.option('--out_file', '-o', help='Output filename', default=None, type=str, show_default=True)
def set_patch_name(input_model, patch_name, out_file):
    ''' Set a single patch name in the sky model
    '''

    if not out_file:
        out_file = input_model

    sky_model = skymodel.lsmtool.load(input_model)
    sky_model.set_patch_name(sky_model, patch_name)
    sky_model.write(out_file, clobber=True)

if __name__ == '__main__':
    main()
