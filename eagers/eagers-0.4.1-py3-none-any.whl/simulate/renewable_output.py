from numpy import cos, deg2rad

from eagers.basic.solar_calc import solar_calc
from eagers.setup.update_qpform_all import assign_type


def renewable_output(gen, date, irradiance, location):
    '''date is the vector of time points at which you request data.'''
    gen = ensure_dict_form(gen)
    power = []
    if gen['type'] == 'Solar':
        get_solar_power(power, gen, date, irradiance, location)
    elif gen['type'] == 'Wind':
        raise NotImplementedError('Need to update renewable_output.py for Wind.')
    else:
        raise ValueError('Unrecognized renewable generator type.')
    return power


def ensure_dict_form(gen):
    '''Return the given generator in dict form, if it's not already.'''
    if not isinstance(gen, dict):
        assigned_type = assign_type(gen)
        gen = gen.__dict__
        gen['type'] = assigned_type
    return gen


def get_solar_power(power, gen, date, irradiance, location):
    '''Calculate solar power generated at the given times. Returned
    values are in kW.

    Positional arguments:
    power - (list) List to be updated in place with power values.
    gen - (dict) QP form of solar generator.
    date - (list of datetime.datetime) Timestamps to obtain solar power
        for.
    irradiance - (array of floats) Direct normal irradiance (DNI) values
        in kW/m^2.
    location - (dict) Location information: longitude, latitude, time
        zone.
    '''
    _, _, azimuth, zenith = solar_calc(location['longitude'],location['latitude'],location['time_zone'],date)
    tracking = gen['tracking']
    if gen['tracking'] == 'fixed':
        for t in range(len(irradiance)):
            power.append(gen['size_m2'] * irradiance[t] / 1000 * gen['eff'] * cos(deg2rad(zenith[t] - gen['tilt'])) * max(0, cos(deg2rad(azimuth[t] - gen['azimuth']))))
    elif gen['tracking'] == 'one_axis':
        for t in range(len(irradiance)):
            power.append(gen['size_m2'] * irradiance[t] / 1000 * gen['eff'] * cos(deg2rad(zenith[t] - gen['tilt'])))
    elif gen['tracking'] == 'dual_axis':
        for t in range(len(irradiance)):
            power.append(gen['size_m2']* irradiance[t] / 1000* gen['eff'])
    else:
        tracking = gen['tracking']
        raise ValueError(f'Tracking type {tracking!r} is invalid.')
    return power
