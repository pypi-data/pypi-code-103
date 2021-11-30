import os
from urllib.request import urlopen

import numpy as np

import astropy.units as u
import astropy.table as atable
from astropy.time import Time
from astropy.coordinates import SkyCoord, Angle, AltAz, EarthLocation

from casacore import tables

import lsmtool
from lsmtool import tableio
lsmtool.logger.setLevel('warning')

from .settings import TEMPLATE_DIR


# Lazy loaded:
# - astroquery.vizier in build_sky_model_from_specfind()
# - nenupy.beam in compute_beam()


all_mas = [0, 1, 3, 7, 11, 13]

nenufar_location = EarthLocation(lat=47.376511 * u.deg, lon=2.1924002 * u.deg)

sky_model_catalogs = ['specfind', 'lcs165']


def get_optfreq(fmhz):
    if fmhz <= 50:
        return 40
    if fmhz <= 68:
        return 60
    return 80

def get_lowres_ateam_skymodel_path():
    return os.path.join(TEMPLATE_DIR, 'Ateam_lowres.skymodel')


def compute_beam(altaz, altaz_phase_center, fmhz=70, ma=0, pol='NW'):
    from nenupy.beam import ABeam

    anabeam = ABeam(fmhz * u.MHz, pol, altaz_phase_center.az.deg, altaz_phase_center.alt.deg, ma=ma)
    anabeam.squint_freq = get_optfreq(fmhz)

    return anabeam.beam_values(altaz.transform_to('icrs'), Time(altaz.obstime.datetime))


def compute_beam_freqs(altaz, altaz_phase_center, fmhz, ma=0, pol='NW'):
    return np.array([compute_beam(altaz, altaz_phase_center, ma=ma, fmhz=k, pol='NW') for k in fmhz])


def compute_beam_freqs_mas(altaz, altaz_phase_center, fmhz, mas, pol='NW'):
    return np.array([compute_beam_freqs(altaz, altaz_phase_center, fmhz, ma=k, pol='NW') for k in mas])


def build_sky_model_from_specfind(coord, min_flux, radius, out_file, waste_spidx=-0.8):
    from astroquery.vizier import Vizier
    Vizier.ROW_LIMIT = 100000

    print(f'Querying SPECFIND v2 spec catalog for phase center {coord}...')

    catalog = Vizier(catalog='VIII/85A/spectra', row_limit=100000,
                     column_filters={'nu': '30..200', 'S(nu)': f'> {0.2 * 0.5 * 1e3}',
                                     'Name': '~|4C*|6C*|7C*|8C*|VLSS*'})

    table = catalog.query_region(coord, radius=Angle(radius, "deg"))[0]
    # Get unique physical source
    tg = table.group_by('Seq')
    table_uniq = tg[tg.groups.indices[:-1]]

    # Compute flux at 74 Mhz from the spectra index
    table_uniq['S_nu_74'] = (10 ** (table_uniq['a'] * np.log10(74) + table_uniq['b']))
    table_uniq = table_uniq[table_uniq['S_nu_74'] > min_flux * 1e3]

    coords = SkyCoord(ra=table_uniq['RAJ2000'], dec=table_uniq['DEJ2000'])

    print(f'-> Found {len(table_uniq)} sources with flux > {min_flux} Jy with radius > {radius} deg')

    print('Querying SPECFIND v2 waste catalog ...')
    catalog = Vizier(catalog='VIII/85A/waste', row_limit=100000,
                     column_filters={'nu': '30..200', 'S(nu)': f'> {0.2 * 0.5 * 1e3}',
                                     'Name': '~|4C*|6C*|7C*|8C*|VLSS*'})

    table_waste = catalog.query_region(coord, radius=Angle(radius, "deg"))[0]
    table_waste = table_waste[table_waste['Seq'] < 0]
    # Get unique physical source
    tg = table_waste.group_by('Seq')
    table_waste = tg[tg.groups.indices[:-1]]
    # Look for duplicate name entries
    tg = table_waste.group_by('Name')
    table_waste = tg[tg.groups.indices[:-1]]
    table_waste['S_nu_74'] = table_waste['S_nu_']

    coords_waste = SkyCoord(ra=table_waste['RAJ2000'], dec=table_waste['DEJ2000'])

    # Extract the extra sources which are not in the main table
    _, idx2, _, _ = coords_waste.search_around_sky(coords, 0.2 * u.deg)
    table_extra = table_waste[np.setdiff1d(np.arange(len(coords_waste)), idx2)]

    print(f'-> Found {len(table_extra)} extra sources in waste table (default spectra index: {waste_spidx})')

    table_merge = atable.vstack([table_uniq, table_extra], metadata_conflicts='silent')
    table_merge['a'].fill_value = waste_spidx
    table_merge.sort('S_nu_74', reverse=True)

    coords_merge = SkyCoord(ra=table_merge['RAJ2000'], dec=table_merge['DEJ2000'])

    print(f'Building sky model with {len(table_merge)} sources ...')

    sky_model = atable.Table(names=['Name', 'Type', 'Patch', 'Ra', 'Dec', 'I', 'ReferenceFrequency', 'SpectralIndex'],
                             dtype=[str] * 8, data=np.zeros((8, len(table_merge))).T)
    sky_model['Ra'] = coords_merge.ra.deg
    sky_model['Ra'].unit = u.deg

    sky_model['Dec'] = coords_merge.dec.deg
    sky_model['Dec'].unit = u.deg

    sky_model['Name'] = table_merge['Name']
    sky_model['Patch'] = 'Main'
    sky_model['Type'] = 'Point'
    sky_model['ReferenceFrequency'] = [74e6] * len(table_merge)
    sky_model['ReferenceFrequency'].unit = u.Hz

    sky_model['I'] = table_merge['S_nu_74'] * 1e-3
    sky_model['I'].unit = u.Jansky

    sky_model['SpectralIndex'] = [np.array([a], dtype=object) for a in table_merge['a'].filled()]

    print(f'Saving Intrinsic sky model to {out_file} ...')

    tableio.skyModelWriter(sky_model, out_file)

    return lsmtool.load(out_file)


def build_sky_model_from_lcs165(coord, min_flux, radius, out_file):
    assert radius <= 20, 'Radius is limited to 20 degrees for lcs165 sky models'
    url = 'https://lcs165.lofar.eu/cgi-bin/gsmv1.cgi'
    cmd = f'{url}?coord={coord.ra.deg},{coord.dec.deg}&radius={radius}&cutoff={min_flux}&unit=deg&deconv=y'
    print('Sending request:', cmd)
    with urlopen(cmd) as response:
        response = response.read()

    print(f'Saving Intrinsic sky model to {out_file} ...')

    with open(out_file, mode='w') as fp:
        fp.write(response.decode('utf-8'))

    sky_model = lsmtool.load(out_file)
    set_patch_name(sky_model, 'Main')
    sky_model.write(out_file, clobber=True)

    print(f'Sky model saved with {len(sky_model)} components')

    return sky_model


def build_sky_model(coord, min_flux, radius, out_file, catalog='specfind'):
    if catalog == 'specfind':
        sky_model = build_sky_model_from_specfind(coord, min_flux, radius, out_file)
    else:
        sky_model = build_sky_model_from_lcs165(coord, min_flux, radius, out_file)

    return sky_model


def build_sky_model_ms(ms_file, min_flux, radius, out_file, catalog='specfind'):
    phase_dir = tables.table(ms_file + '/FIELD').getcol('PHASE_DIR').squeeze()
    coord_phase_dir = SkyCoord(ra=phase_dir[0] * u.rad, dec=phase_dir[1] * u.rad)

    return build_sky_model(coord_phase_dir, min_flux, radius, out_file, catalog=catalog)


def print_info(model):
    patch_count = dict(zip(*np.unique(model.getColValues('Patch'), return_counts=True)))
    if model.getPatchNames() is not None:
        for patch, tot_flux in zip(model.getPatchNames(), model.getColValues('I', aggregate='sum')):
            print(f'- {patch}: {patch_count[patch]} cmpts totaling {tot_flux:.1f} Jy')


def apply_nenufar_beam(sky_model, observing_time, coord, mfmhz):
    print('Sky model info:')
    print_info(sky_model)

    print(f'Computing beam:')
    if isinstance(observing_time.iso, np.ndarray):
        print(f'--Dates: {" ".join(observing_time.iso)}')
    else:
        print(f'--Date: {observing_time.iso}')
    print(f'--Pointing: {coord.to_string("hmsdms")}')
    print(f'--Frequency: {mfmhz} MHz')

    beams = []

    for obs_time in observing_time:
        altaz = AltAz(location=nenufar_location, obstime=obs_time)

        altaz_phase_dir = coord.transform_to(altaz)

        coord_skymodel = SkyCoord(ra=sky_model.getColValues('Ra') * u.deg, dec=sky_model.getColValues('Dec') * u.deg)
        altaz_skymodel = coord_skymodel.transform_to(altaz)

        beam_nw = compute_beam_freqs_mas(altaz_skymodel, altaz_phase_dir, [mfmhz], all_mas, pol='NW')
        beam_ne = compute_beam_freqs_mas(altaz_skymodel, altaz_phase_dir, [mfmhz], all_mas, pol='NE')
        beam = 0.5 * (beam_nw + beam_ne)
        beam_pointing = compute_beam(SkyCoord([altaz_phase_dir]), altaz_phase_dir, fmhz=mfmhz)
        beam = beam.squeeze()
        # print(beam.max(axis=1), beam_pointing.max(axis=1))
        beam = beam / beam_pointing.squeeze()
        beam[np.isnan(beam)] = 0
        beams.append(beam)

    beams = np.array(beams)

    # Take the mean of the beam of all MA rotations
    app_sky_model = sky_model.copy()
    flux = app_sky_model.getColValues('I') * beams.mean(axis=1).max(axis=0).squeeze()
    app_sky_model.setColValues('I', flux)

    print('Sky model info after applying beam:')
    print_info(app_sky_model)

    return app_sky_model


def edit_model(sky_model, observing_time, min_flux=0.5, min_flux_patch=20, min_elevation_patch=10, 
               always_keep=['Main'], always_remove=[]):
    print(f'Removing components with flux < {min_flux} Jy ...')
    sky_model.remove(f'I < {min_flux}')

    print(f'Removing patch with total flux < {min_flux_patch} Jy ...')

    for patch, sum_I in zip(sky_model.getPatchNames(), sky_model.getColValues('I', aggregate='sum')):
        if sum_I < min_flux_patch and ((patch not in always_keep) or sum_I < 1):
            print(f'-- Removing patch {patch}')
            sky_model.remove(f'Patch == {patch}')

    print(f'Removing patch with elevation < {min_elevation_patch} deg ...')
    altaz = AltAz(location=nenufar_location, obstime=observing_time)

    for patch, (ra, dec) in sky_model.getPatchPositions(method='wmean').items():
        elevation = SkyCoord(ra=ra.deg * u.deg, dec=dec.deg * u.deg).transform_to(altaz).alt.max()
        print(f'-- Max elevation of {patch}: {elevation:.2f}')
        if (np.isnan(elevation.deg) or elevation.deg < min_elevation_patch) \
                and ((patch not in always_keep) or elevation < 0):
            print(f'-- Removing Patch {patch} (elevation {elevation.deg} deg)')
            sky_model.remove(f'Patch == {patch}')

    if always_remove is not None:
        print(f'Removing user specified patch ...')
        for patch in sky_model.getPatchNames():
            if patch in always_remove:
                print(f'-- Removing Patch {patch}')
                sky_model.remove(f'Patch == {patch}')

    print('Sky model info after model editing:')
    print_info(sky_model)

    return sky_model


def add_mssing_logarithmic_si_col(skymodel):
    if 'LogarithmicSI' not in skymodel.getColNames():
        skymodel.setColValues('LogarithmicSI', ['true'] * len(skymodel))


def concatenate(sky_model_filenames):
    sky_model = lsmtool.load(sky_model_filenames[0])
    add_mssing_logarithmic_si_col(sky_model)
    for f in sky_model_filenames[1:]:
        other_sky_model = lsmtool.load(f)
        add_mssing_logarithmic_si_col(other_sky_model)
        lsmtool.operations.concatenate.concatenate(sky_model, other_sky_model)

    return sky_model


def set_patch_name(sky_model, patch_name):
    sky_model.setColValues('PATCH', [patch_name] * len(sky_model), index=2)
    sky_model.setPatchPositions(method='wmean')
