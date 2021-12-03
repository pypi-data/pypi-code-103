#!/usr/bin/env python3
# -*- coding:utf-8 -*-
from __future__ import with_statement, print_function
import math
import numpy as np
import os
import filecmp

# constant variables
avogad = 6.0220434469282E+23  # avogadro number (molecules/mole), from MCNP6
E_175 = (1.00001E-007, 4.13994E-007, 5.31579E-007, 6.82560E-007, 8.76425E-007,
         1.12535E-006, 1.44498E-006, 1.85539E-006, 2.38237E-006, 3.05902E-006,
         3.92786E-006, 5.04348E-006, 6.47595E-006, 8.31529E-006, 1.06770E-005,
         1.37096E-005, 1.76035E-005, 2.26033E-005, 2.90232E-005, 3.72665E-005,
         4.78512E-005, 6.14421E-005, 7.88932E-005, 1.01301E-004, 1.30073E-004,
         1.67017E-004, 2.14454E-004, 2.75364E-004, 3.53575E-004, 4.53999E-004,
         5.82947E-004, 7.48518E-004, 9.61117E-004, 1.23410E-003, 1.58461E-003,
         2.03468E-003, 2.24867E-003, 2.48517E-003, 2.61259E-003, 2.74654E-003,
         3.03539E-003, 3.35463E-003, 3.70744E-003, 4.30742E-003, 5.53084E-003,
         7.10174E-003, 9.11882E-003, 1.05946E-002, 1.17088E-002, 1.50344E-002,
         1.93045E-002, 2.18749E-002, 2.35786E-002, 2.41755E-002, 2.47875E-002,
         2.60584E-002, 2.70001E-002, 2.85011E-002, 3.18278E-002, 3.43067E-002,
         4.08677E-002, 4.63092E-002, 5.24752E-002, 5.65622E-002, 6.73795E-002,
         7.20245E-002, 7.94987E-002, 8.25034E-002, 8.65170E-002, 9.80365E-002,
         1.11090E-001, 1.16786E-001, 1.22773E-001, 1.29068E-001, 1.35686E-001,
         1.42642E-001, 1.49956E-001, 1.57644E-001, 1.65727E-001, 1.74224E-001,
         1.83156E-001, 1.92547E-001, 2.02419E-001, 2.12797E-001, 2.23708E-001,
         2.35177E-001, 2.47235E-001, 2.73237E-001, 2.87246E-001, 2.94518E-001,
         2.97211E-001, 2.98491E-001, 3.01974E-001, 3.33733E-001, 3.68832E-001,
         3.87742E-001, 4.07622E-001, 4.50492E-001, 4.97871E-001, 5.23397E-001,
         5.50232E-001, 5.78443E-001, 6.08101E-001, 6.39279E-001, 6.72055E-001,
         7.06512E-001, 7.42736E-001, 7.80817E-001, 8.20850E-001, 8.62936E-001,
         9.07180E-001, 9.61672E-001, 1.00259E+000, 1.10803E+000, 1.16484E+000,
         1.22456E+000, 1.28735E+000, 1.35335E+000, 1.42274E+000, 1.49569E+000,
         1.57237E+000, 1.65299E+000, 1.73774E+000, 1.82684E+000, 1.92050E+000,
         2.01897E+000, 2.12248E+000, 2.23130E+000, 2.30693E+000, 2.34570E+000,
         2.36533E+000, 2.38513E+000, 2.46597E+000, 2.59240E+000, 2.72532E+000,
         2.86505E+000, 3.01194E+000, 3.16637E+000, 3.32871E+000, 3.67879E+000,
         4.06570E+000, 4.49329E+000, 4.72367E+000, 4.96585E+000, 5.22046E+000,
         5.48812E+000, 5.76950E+000, 6.06531E+000, 6.37628E+000, 6.59241E+000,
         6.70320E+000, 7.04688E+000, 7.40818E+000, 7.78801E+000, 8.18731E+000,
         8.60708E+000, 9.04837E+000, 9.51229E+000, 1.00000E+001, 1.05127E+001,
         1.10517E+001, 1.16183E+001, 1.22140E+001, 1.25232E+001, 1.28403E+001,
         1.34986E+001, 1.38403E+001, 1.41907E+001, 1.45499E+001, 1.49182E+001,
         1.56831E+001, 1.64872E+001, 1.69046E+001, 1.73325E+001, 1.96403E+001)
E_709 = (1.05E-11, 1.10E-11, 1.15E-11, 1.20E-11, 1.26E-11, 1.32E-11, 1.38E-11,
         1.45E-11, 1.51E-11, 1.58E-11, 1.66E-11, 1.74E-11, 1.82E-11, 1.91E-11,
         2.00E-11, 2.09E-11, 2.19E-11, 2.29E-11, 2.40E-11, 2.51E-11, 2.63E-11,
         2.75E-11, 2.88E-11, 3.02E-11, 3.16E-11, 3.31E-11, 3.47E-11, 3.63E-11,
         3.80E-11, 3.98E-11, 4.17E-11, 4.37E-11, 4.57E-11, 4.79E-11, 5.01E-11,
         5.25E-11, 5.50E-11, 5.75E-11, 6.03E-11, 6.31E-11, 6.61E-11, 6.92E-11,
         7.24E-11, 7.59E-11, 7.94E-11, 8.32E-11, 8.71E-11, 9.12E-11, 9.55E-11,
         1.00E-10, 1.05E-10, 1.10E-10, 1.15E-10, 1.20E-10, 1.26E-10, 1.32E-10,
         1.38E-10, 1.45E-10, 1.51E-10, 1.58E-10, 1.66E-10, 1.74E-10, 1.82E-10,
         1.91E-10, 2.00E-10, 2.09E-10, 2.19E-10, 2.29E-10, 2.40E-10, 2.51E-10,
         2.63E-10, 2.75E-10, 2.88E-10, 3.02E-10, 3.16E-10, 3.31E-10, 3.47E-10,
         3.63E-10, 3.80E-10, 3.98E-10, 4.17E-10, 4.37E-10, 4.57E-10, 4.79E-10,
         5.01E-10, 5.25E-10, 5.50E-10, 5.75E-10, 6.03E-10, 6.31E-10, 6.61E-10,
         6.92E-10, 7.24E-10, 7.59E-10, 7.94E-10, 8.32E-10, 8.71E-10, 9.12E-10,
         9.55E-10, 1.00E-09, 1.05E-09, 1.10E-09, 1.15E-09, 1.20E-09, 1.26E-09,
         1.32E-09, 1.38E-09, 1.45E-09, 1.51E-09, 1.58E-09, 1.66E-09, 1.74E-09,
         1.82E-09, 1.91E-09, 2.00E-09, 2.09E-09, 2.19E-09, 2.29E-09, 2.40E-09,
         2.51E-09, 2.63E-09, 2.75E-09, 2.88E-09, 3.02E-09, 3.16E-09, 3.31E-09,
         3.47E-09, 3.63E-09, 3.80E-09, 3.98E-09, 4.17E-09, 4.37E-09, 4.57E-09,
         4.79E-09, 5.01E-09, 5.25E-09, 5.50E-09, 5.75E-09, 6.03E-09, 6.31E-09,
         6.61E-09, 6.92E-09, 7.24E-09, 7.59E-09, 7.94E-09, 8.32E-09, 8.71E-09,
         9.12E-09, 9.55E-09, 1.00E-08, 1.05E-08, 1.10E-08, 1.15E-08, 1.20E-08,
         1.26E-08, 1.32E-08, 1.38E-08, 1.45E-08, 1.51E-08, 1.58E-08, 1.66E-08,
         1.74E-08, 1.82E-08, 1.91E-08, 2.00E-08, 2.09E-08, 2.19E-08, 2.29E-08,
         2.40E-08, 2.51E-08, 2.63E-08, 2.75E-08, 2.88E-08, 3.02E-08, 3.16E-08,
         3.31E-08, 3.47E-08, 3.63E-08, 3.80E-08, 3.98E-08, 4.17E-08, 4.37E-08,
         4.57E-08, 4.79E-08, 5.01E-08, 5.25E-08, 5.50E-08, 5.75E-08, 6.03E-08,
         6.31E-08, 6.61E-08, 6.92E-08, 7.24E-08, 7.59E-08, 7.94E-08, 8.32E-08,
         8.71E-08, 9.12E-08, 9.55E-08, 1.00E-07, 1.05E-07, 1.10E-07, 1.15E-07,
         1.20E-07, 1.26E-07, 1.32E-07, 1.38E-07, 1.45E-07, 1.51E-07, 1.58E-07,
         1.66E-07, 1.74E-07, 1.82E-07, 1.91E-07, 2.00E-07, 2.09E-07, 2.19E-07,
         2.29E-07, 2.40E-07, 2.51E-07, 2.63E-07, 2.75E-07, 2.88E-07, 3.02E-07,
         3.16E-07, 3.31E-07, 3.47E-07, 3.63E-07, 3.80E-07, 3.98E-07, 4.17E-07,
         4.37E-07, 4.57E-07, 4.79E-07, 5.01E-07, 5.25E-07, 5.50E-07, 5.75E-07,
         6.03E-07, 6.31E-07, 6.61E-07, 6.92E-07, 7.24E-07, 7.59E-07, 7.94E-07,
         8.32E-07, 8.71E-07, 9.12E-07, 9.55E-07, 1.00E-06, 1.05E-06, 1.10E-06,
         1.15E-06, 1.20E-06, 1.26E-06, 1.32E-06, 1.38E-06, 1.45E-06, 1.51E-06,
         1.58E-06, 1.66E-06, 1.74E-06, 1.82E-06, 1.91E-06, 2.00E-06, 2.09E-06,
         2.19E-06, 2.29E-06, 2.40E-06, 2.51E-06, 2.63E-06, 2.75E-06, 2.88E-06,
         3.02E-06, 3.16E-06, 3.31E-06, 3.47E-06, 3.63E-06, 3.80E-06, 3.98E-06,
         4.17E-06, 4.37E-06, 4.57E-06, 4.79E-06, 5.01E-06, 5.25E-06, 5.50E-06,
         5.75E-06, 6.03E-06, 6.31E-06, 6.61E-06, 6.92E-06, 7.24E-06, 7.59E-06,
         7.94E-06, 8.32E-06, 8.71E-06, 9.12E-06, 9.55E-06, 1.00E-05, 1.05E-05,
         1.10E-05, 1.15E-05, 1.20E-05, 1.26E-05, 1.32E-05, 1.38E-05, 1.45E-05,
         1.51E-05, 1.58E-05, 1.66E-05, 1.74E-05, 1.82E-05, 1.91E-05, 2.00E-05,
         2.09E-05, 2.19E-05, 2.29E-05, 2.40E-05, 2.51E-05, 2.63E-05, 2.75E-05,
         2.88E-05, 3.02E-05, 3.16E-05, 3.31E-05, 3.47E-05, 3.63E-05, 3.80E-05,
         3.98E-05, 4.17E-05, 4.37E-05, 4.57E-05, 4.79E-05, 5.01E-05, 5.25E-05,
         5.50E-05, 5.75E-05, 6.03E-05, 6.31E-05, 6.61E-05, 6.92E-05, 7.24E-05,
         7.59E-05, 7.94E-05, 8.32E-05, 8.71E-05, 9.12E-05, 9.55E-05, 1.00E-04,
         1.05E-04, 1.10E-04, 1.15E-04, 1.20E-04, 1.26E-04, 1.32E-04, 1.38E-04,
         1.45E-04, 1.51E-04, 1.58E-04, 1.66E-04, 1.74E-04, 1.82E-04, 1.91E-04,
         2.00E-04, 2.09E-04, 2.19E-04, 2.29E-04, 2.40E-04, 2.51E-04, 2.63E-04,
         2.75E-04, 2.88E-04, 3.02E-04, 3.16E-04, 3.31E-04, 3.47E-04, 3.63E-04,
         3.80E-04, 3.98E-04, 4.17E-04, 4.37E-04, 4.57E-04, 4.79E-04, 5.01E-04,
         5.25E-04, 5.50E-04, 5.75E-04, 6.03E-04, 6.31E-04, 6.61E-04, 6.92E-04,
         7.24E-04, 7.59E-04, 7.94E-04, 8.32E-04, 8.71E-04, 9.12E-04, 9.55E-04,
         1.00E-03, 1.05E-03, 1.10E-03, 1.15E-03, 1.20E-03, 1.26E-03, 1.32E-03,
         1.38E-03, 1.45E-03, 1.51E-03, 1.58E-03, 1.66E-03, 1.74E-03, 1.82E-03,
         1.91E-03, 2.00E-03, 2.09E-03, 2.19E-03, 2.29E-03, 2.40E-03, 2.51E-03,
         2.63E-03, 2.75E-03, 2.88E-03, 3.02E-03, 3.16E-03, 3.31E-03, 3.47E-03,
         3.63E-03, 3.80E-03, 3.98E-03, 4.17E-03, 4.37E-03, 4.57E-03, 4.79E-03,
         5.01E-03, 5.25E-03, 5.50E-03, 5.75E-03, 6.03E-03, 6.31E-03, 6.61E-03,
         6.92E-03, 7.24E-03, 7.59E-03, 7.94E-03, 8.32E-03, 8.71E-03, 9.12E-03,
         9.55E-03, 1.00E-02, 1.05E-02, 1.10E-02, 1.15E-02, 1.20E-02, 1.26E-02,
         1.32E-02, 1.38E-02, 1.45E-02, 1.51E-02, 1.58E-02, 1.66E-02, 1.74E-02,
         1.82E-02, 1.91E-02, 2.00E-02, 2.09E-02, 2.19E-02, 2.29E-02, 2.40E-02,
         2.51E-02, 2.63E-02, 2.75E-02, 2.88E-02, 3.02E-02, 3.16E-02, 3.31E-02,
         3.47E-02, 3.63E-02, 3.80E-02, 3.98E-02, 4.17E-02, 4.37E-02, 4.57E-02,
         4.79E-02, 5.01E-02, 5.25E-02, 5.50E-02, 5.75E-02, 6.03E-02, 6.31E-02,
         6.61E-02, 6.92E-02, 7.24E-02, 7.59E-02, 7.94E-02, 8.32E-02, 8.71E-02,
         9.12E-02, 9.55E-02, 1.00E-01, 1.05E-01, 1.10E-01, 1.15E-01, 1.20E-01,
         1.26E-01, 1.32E-01, 1.38E-01, 1.45E-01, 1.51E-01, 1.58E-01, 1.66E-01,
         1.74E-01, 1.82E-01, 1.91E-01, 2.00E-01, 2.09E-01, 2.19E-01, 2.29E-01,
         2.40E-01, 2.51E-01, 2.63E-01, 2.75E-01, 2.88E-01, 3.02E-01, 3.16E-01,
         3.31E-01, 3.47E-01, 3.63E-01, 3.80E-01, 3.98E-01, 4.17E-01, 4.37E-01,
         4.57E-01, 4.79E-01, 5.01E-01, 5.25E-01, 5.50E-01, 5.75E-01, 6.03E-01,
         6.31E-01, 6.61E-01, 6.92E-01, 7.24E-01, 7.59E-01, 7.94E-01, 8.32E-01,
         8.71E-01, 9.12E-01, 9.55E-01, 1.00E+00, 1.05E+00, 1.10E+00, 1.15E+00,
         1.20E+00, 1.26E+00, 1.32E+00, 1.38E+00, 1.45E+00, 1.51E+00, 1.58E+00,
         1.66E+00, 1.74E+00, 1.82E+00, 1.91E+00, 2.00E+00, 2.09E+00, 2.19E+00,
         2.29E+00, 2.40E+00, 2.51E+00, 2.63E+00, 2.75E+00, 2.88E+00, 3.02E+00,
         3.16E+00, 3.31E+00, 3.47E+00, 3.63E+00, 3.80E+00, 3.98E+00, 4.17E+00,
         4.37E+00, 4.57E+00, 4.79E+00, 5.01E+00, 5.25E+00, 5.50E+00, 5.75E+00,
         6.03E+00, 6.31E+00, 6.61E+00, 6.92E+00, 7.24E+00, 7.59E+00, 7.94E+00,
         8.32E+00, 8.71E+00, 9.12E+00, 9.55E+00, 1.00E+01, 1.02E+01, 1.04E+01,
         1.06E+01, 1.08E+01, 1.10E+01, 1.12E+01, 1.14E+01, 1.16E+01, 1.18E+01,
         1.20E+01, 1.22E+01, 1.24E+01, 1.26E+01, 1.28E+01, 1.30E+01, 1.32E+01,
         1.34E+01, 1.36E+01, 1.38E+01, 1.40E+01, 1.42E+01, 1.44E+01, 1.46E+01,
         1.48E+01, 1.50E+01, 1.52E+01, 1.54E+01, 1.56E+01, 1.58E+01, 1.60E+01,
         1.62E+01, 1.64E+01, 1.66E+01, 1.68E+01, 1.70E+01, 1.72E+01, 1.74E+01,
         1.76E+01, 1.78E+01, 1.80E+01, 1.82E+01, 1.84E+01, 1.86E+01, 1.88E+01,
         1.90E+01, 1.92E+01, 1.94E+01, 1.96E+01, 1.98E+01, 2.00E+01, 2.10E+01,
         2.20E+01, 2.30E+01, 2.40E+01, 2.50E+01, 2.60E+01, 2.70E+01, 2.80E+01,
         2.90E+01, 3.00E+01, 3.20E+01, 3.40E+01, 3.60E+01, 3.80E+01, 4.00E+01,
         4.20E+01, 4.40E+01, 4.60E+01, 4.80E+01, 5.00E+01, 5.20E+01, 5.40E+01,
         5.60E+01, 5.80E+01, 6.00E+01, 6.50E+01, 7.00E+01, 7.50E+01, 8.00E+01,
         9.00E+01, 1.00E+02, 1.10E+02, 1.20E+02, 1.30E+02, 1.40E+02, 1.50E+02,
         1.60E+02, 1.80E+02, 2.00E+02, 2.40E+02, 2.80E+02, 3.20E+02, 3.60E+02,
         4.00E+02, 4.40E+02, 4.80E+02, 5.20E+02, 5.60E+02, 6.00E+02, 6.40E+02,
         6.80E+02, 7.20E+02, 7.60E+02, 8.00E+02, 8.40E+02, 8.80E+02, 9.20E+02,
         9.60E+02, 1.00E+03)

ELE_TABLE = ('H', 'He', 'Li', 'Be', 'B',
             'C', 'N', 'O', 'F', 'Ne',
             'Na', 'Mg', 'Al', 'Si', 'P',
             'S', 'Cl', 'Ar', 'K', 'Ca',
             'Sc', 'Ti', 'V', 'Cr', 'Mn',
             'Fe', 'Co', 'Ni', 'Cu', 'Zn',
             'Ga', 'Ge', 'As', 'Se', 'Br',
             'Kr', 'Rb', 'Sr', 'Y', 'Zr',
             'Nb', 'Mo', 'Tc', 'Ru', 'Rh',
             'Pd', 'Ag', 'Cd', 'In', 'Sn',
             'Sb', 'Te', 'I', 'Xe', 'Cs',
             'Ba', 'La', 'Ce', 'Pr', 'Nd',
             'Pm', 'Sm', 'Eu', 'Gd', 'Tb',
             'Dy', 'Ho', 'Er', 'Tm', 'Yb',
             'Lu', 'Hf', 'Ta', 'W', 'Re',
             'Os', 'Ir', 'Pt', 'Au', 'Hg',
             'Tl', 'Pb', 'Bi', 'Po', 'At',
             'Rn', 'Fr', 'Ra', 'Ac', 'Th',
             'Pa', 'U', 'Np', 'Pu', 'Am',
             'Cm', 'Bk', 'Cf', 'Es', 'Fm')


def get_ele_table():
    return ELE_TABLE


def log(func):
    def wrapper(*args, **kw):
        print('running {0}:'.format(func.__name__))
        return func(*args, **kw)
    return wrapper


def time_to_sec(value, unit):
    """time_to_sec convert the time of cooling time to the unit of sec.
    input parameters:value, a float number of time,
                     unit, a string of time unit, like SECS, MINS, HOURS, DAYS, YEARS
    return value: value, a float number of time in unit of sec"""
    # convert value to float incase of it's a string
    value = float(value)
    # unit check
    if unit.lower() not in ('s', 'sec', 'secs', 'second', 'seconds',
                            'm', 'min', 'mins', 'minute', 'minutes',
                            'h', 'hr', 'hour', 'hours',
                            'd', 'day', 'days',
                            'y', 'a', 'year', 'years'):
        raise ValueError('unit of time must in given value, not aribitary one')
    if unit.lower() in ('s', 'sec', 'secs', 'second', 'seconds'):
        return value * 1.0
    if unit.lower() in ('m', 'min', 'mins', 'minute', 'minutes'):
        return value * 60.0
    if unit.lower() in ('h', 'hr', 'hour', 'hours'):
        return value * 3600.0
    if unit.lower() in ('d', 'day', 'days'):
        return value * 3600 * 24.0
    if unit.lower() in ('y', 'a', 'year', 'years'):
        return value * 3600 * 24 * 365.25


def time_sec_to_unit(value, unit):
    """
    Convert time from unit (s) to another unit.
    """
    value = float(value)
    # unit check
    if unit.lower() not in ('s', 'sec', 'secs', 'second', 'seconds',
                            'm', 'min', 'mins', 'minute', 'minutes',
                            'h', 'hr', 'hour', 'hours',
                            'd', 'day', 'days',
                            'y', 'a', 'year', 'years'):
        raise ValueError('unit of time must in given value, not aribitary one')
    if unit.lower() in ('s', 'sec', 'secs', 'second', 'seconds'):
        return value / 1.0
    if unit.lower() in ('m', 'min', 'mins', 'minute', 'minutes'):
        return value / 60.0
    if unit.lower() in ('h', 'hr', 'hour', 'hours'):
        return value / 3600.0
    if unit.lower() in ('d', 'day', 'days'):
        return value / (3600 * 24.0)
    if unit.lower() in ('y', 'a', 'year', 'years'):
        return value / (3600 * 24 * 365.25)


def sgn(value):
    """sgn return 1 for number greater than 0.0, return -1 for number smaller than 0"""
    if not isinstance(value, (int, float)):
        raise ValueError('value for sgn must a number of int or float')
    if value == 0:
        sgn = 0
    if value < 0.0:
        sgn = -1
    if value > 0.0:
        sgn = 1
    return sgn


def ci2bq(value):
    """Convert unit from Ci to Bq."""
    # input check
    if not isinstance(value, float):
        raise ValueError("Input value for Ci must be float")
    if value < 0:
        raise ValueError("Negtive input for Ci")
    return value * 3.7e+10


def scale_list(value):
    """scale_list: scale a list of float, normalized to 1"""
    # check the input
    if not isinstance(value, list):
        raise ValueError('scale_list can only apply to a list')
    for item in value:
        if not isinstance(item, float):
            raise ValueError('scale_list can only apply to a list of float')
    # scale the list
    t = sum(value)
    for i in range(len(value)):
        value[i] /= t
    return value


def get_ct_index(ct, cts):
    """
    Get the index of a cooling time in cooling_times. As there is roundoff
    error in data.

    Parameters:
    -----------
    ct: float
        The cooling time to find.
    cts: list of float
        The cooling times.
    """
    for i in range(len(cts)):
        if math.isclose(ct, cts[i], rel_tol=1e-2):
            return i
    raise ValueError("ct {0} not found".format(ct))


def is_short_live(half_life, threshold=30):
    """
    Check whether the nuclide is short life (half life <= 30 years) nuclide.
    """
    # input check
    try:
        half_life = float(half_life)
    except:
        raise ValueError("half_life must be a float")
    if half_life < 0:
        raise ValueError("half_life < 0, invalide")
    # 30 year
    threshold_s = 60.0 * 60 * 24 * 365.25 * threshold
    if half_life <= threshold_s:
        return True
    else:
        return False


def data_to_line_1d(key, value, delimiter=',', postfix='\n', decimals=5):
    """
    Create a print line for given key and value.
    """
    data_content = ''
    if isinstance(value, list) or isinstance(value, np.ndarray):
        for i, item in enumerate(value):
            if i == 0:
                data_content = format_single_output(item, decimals=decimals)
            else:
                data_content = delimiter.join(
                    [data_content, format_single_output(item, decimals=decimals)])
    else:
        data_content = format_single_output(value, decimals=decimals)

    if key is not None:
        line = delimiter.join([format_single_output(
            key, decimals=decimals), data_content])
    else:
        line = data_content
    return line+postfix


def format_single_output(value, decimals=5):
    """
    Format a single item for output.
    """
    if isinstance(value, float):
        if decimals is None:
            return str(value)
        else:
            style = "{0:."+str(decimals)+"E}"
            return style.format(value)
    else:
        return str(value)


def str2float(s):
    """
    Convert string to float. Including some strange value.
    """
    try:
        value = float(s)
        return value
    except:
        if '-' in s:
            base = s.split('-')[0]
            index = s.split('-')[1]
            s_fix = ''.join([base, 'E-', index])
            return float(s_fix)
        else:
            raise ValueError("{0} can't convert to float".format(s))


def calc_ctr_flag_chn2018(rwc, rwcs):
    """
    Calculate the flat '>' or '<' for a specific radwaste class.
    Eg: rwc='Clearance', rwcs=['HLW', 'ILW'], flag is '>'.
    Eg: rwc='ILW', rwcs=['LLW', 'VLLW'], flag is '<'.
    """
    class_dict = {'Clearance': 0, 'VLLW': 1, 'LLW': 2, 'ILW': 3, 'HLW': 4}
    min_level = len(class_dict) - 1
    max_level = 0
    for i, item in enumerate(rwcs):
        if min_level > class_dict[item]:
            min_level = class_dict[item]
        if max_level < class_dict[item]:
            max_level = class_dict[item]

    if class_dict[rwc] < min_level:
        return '>'
    else:
        return '<'


def calc_ctr_flag_usnrc(rwc, rwcs):
    """
    Calculate the flat '>' or '<' for a specific radwaste class.
    Supprted standard: 'USNRC' and 'USNRC_FETTER'.
    Eg: rwc='LLWA', rwcs=['LLWC', 'LLWB'], flag is '>'.
    Eg: rwc='ILW', rwcs=['LLWC', 'LLWB'], flag is '<'.
    """
    class_dict = {'LLWA': 0, 'LLWB': 1, 'LLWC': 2, 'ILW': 3}
    min_level = len(class_dict) - 1
    max_level = 0
    for i, item in enumerate(rwcs):
        if min_level > class_dict[item]:
            min_level = class_dict[item]
        if max_level < class_dict[item]:
            max_level = class_dict[item]

    if class_dict[rwc] < min_level:
        return '>'
    else:
        return '<'


def calc_ctr_flag_uk(rwc, rwcs):
    """
    Calculate the flat '>' or '<' for a specific radwaste class.
    Eg: rwc='LLW', rwcs=['HLW', 'ILW'], flag is '>'.
    Eg: rwc='HLW', rwcs=['ILW', 'LLW'], flag is '<'.
    """
    class_dict = {'LLW': 0, 'ILW': 1, 'HLW': 2}
    min_level = len(class_dict) - 1
    max_level = 0
    for i, item in enumerate(rwcs):
        if min_level > class_dict[item]:
            min_level = class_dict[item]
        if max_level < class_dict[item]:
            max_level = class_dict[item]

    if class_dict[rwc] < min_level:
        return '>'
    else:
        return '<'


def calc_ctr_flag_russian(rwc, rwcs):
    """
    Calculate the flat '>' or '<' for a specific radwaste class.
    Eg: rwc='Clearance', rwcs=['HLW', 'ILW'], flag is '>'.
    Eg: rwc='ILW', rwcs=['LLW', 'VLLW'], flag is '<'.
    """
    class_dict = {'LLW': 0, 'ILW': 1, 'HLW': 2}
    min_level = len(class_dict) - 1
    max_level = 0
    for i, item in enumerate(rwcs):
        if min_level > class_dict[item]:
            min_level = class_dict[item]
        if max_level < class_dict[item]:
            max_level = class_dict[item]

    if class_dict[rwc] < min_level:
        return '>'
    else:
        return '<'


def calc_ctr(cooling_times, rwcs, classes, standard='CHN2018', out_unit='a', decimals=2):
    """
    Calculate cooling time requirement for specific rwc.

    Parameters:
        cooling_times: list or pandas DataFrame series
            Cooling times, unit: s.
        rwcs: list
            Radwaste classes for each cooling time.
        classes: list
            Radwaste types.
            Eg: for CHN2018: ['HLW', 'ILW', 'LLW', 'VLLW', 'Clearance']
        standard: string
            Radwaste standard used. Supported standards: 'CHN2018', 'USNRC', 'UK'.
        out_unit: string
            Unit of output unit of cooling time. Supported value: 's', 'a'.

    Returns:
        ctr: list of strings
            Required cooling times (in string).
    """
    cooling_times = list(cooling_times)
    if out_unit == 'a':
        # unit conversion
        for i, ct in enumerate(cooling_times):
            cooling_times[i] = time_sec_to_unit(ct, 'a')

    exist_rwcs = list(set(rwcs))
    # find rwc in rwcs
    ctr = []
    for i, item in enumerate(classes):
        if standard in ['USNRC', 'USNRC_FETTER'] and item == 'LLW':
            item = 'LLWC'
        if item in rwcs:
            index = rwcs.index(item)
            ctr.append(format_single_output(
                cooling_times[index], decimals=decimals))
        else:
            if standard == 'CHN2018':
                flag = calc_ctr_flag_chn2018(item, exist_rwcs)
            elif standard in ['USNRC', 'USNRC_FETTER']:
                flag = calc_ctr_flag_usnrc(item, exist_rwcs)
            elif standard == 'UK':
                flag = calc_ctr_flag_uk(item, exist_rwcs)
            elif standard == 'RUSSIAN':
                flag = calc_ctr_flag_russian(item, exist_rwcs)
            else:
                raise ValueError(f"standard: {standard} not supported")

            if flag == '>':
                ctr.append(''.join([flag, format_single_output(
                    cooling_times[-1], decimals=decimals)]))
            else:
                ctr.append(''.join([flag, format_single_output(
                    cooling_times[0], decimals=decimals)]))
    return ctr


def calc_recycle_ctr(cooling_times, cds, rh='CRH', out_unit='a', decimals=2):
    """
    Calculate cooling time requirement for recycling.

    Parameters:
        cooling_times: list or pandas DataFrame series
            Cooling times, unit: s.
        cds: list
            Contact dose rate for each cooling time.
        classes: list
            Recycling methods.
            Could be CRH and ARH. [CRH, ARH]
        out_unit: string
            Unit of output unit of cooling time. Supported value: 's', 'a'.

    Returns:
        ctr: float
           In unit of out_unit.
    """
    cooling_times = list(cooling_times)
    if out_unit == 'a':
        # unit conversion
        for i, ct in enumerate(cooling_times):
            cooling_times[i] = time_sec_to_unit(ct, 'a')
    # determin limit
    if rh.upper() == 'CRH':
        limit = 1e-2
    elif rh.upper() == 'ARH':
        limit = 1e4
    else:
        raise ValueError(f"rh {rh} not supported, use 'CRH' or 'ARH'")
    # calc ctr
    for i, ct in enumerate(cooling_times):
        if i == 0 and cds[0] < limit:
            ctr = ''.join(['<', format_single_output(
                cooling_times[0], decimals=decimals)])
            return ctr
        if cds[i-1] > limit and cds[i] <= limit:
            ctr = ''.join([format_single_output(
                cooling_times[i], decimals=decimals)])
            return ctr
    # cds do not meet limit
    ctr = ''.join(['>', format_single_output(
        cooling_times[-1], decimals=decimals)])
    return ctr


def mcnp_style_str_append(s, value, indent_length=6):
    """append lines as mcnp style, line length <= 80"""
    indent_str = ' '*indent_length
    s_tmp = ''.join([s, ' ', format_single_output(value, decimals=None)])
    if len(s_tmp.split('\n')[-1]) >= 80:
        s_tmp = ''.join([s, '\n', indent_str, ' ',
                        format_single_output(value, decimals=None)])
    s = s_tmp
    return s


def is_blank_line(line):
    """check blank line"""
    line_ele = line.split()
    if len(line_ele) == 0:
        return True
    else:
        return False


def scale_list(value):
    """scale_list: scale a list of float, normalized to 1"""
    # check the input
    if not isinstance(value, list):
        raise ValueError('scale_list can only apply to a list')
    for i, item in enumerate(value):
        try:
            value[i] = float(item)
        except:
            raise ValueError('scale_list can only apply to a list of float')
    # scale the list
    t = sum(value)
    for i in range(len(value)):
        value[i] /= t
    return value


def diff_check_file(f1, f2):
    command = ''.join(["diff ", "--strip-trailing-cr ", f1, " ", f2])
    flag = os.system(command)
    return flag


def compare_lists(l1, l2):
    """
    Compare two lists.
    """
    if len(l1) != len(l2):
        return False
    for i in range(len(l1)):
        if l1[i] != l2[i]:
            return False
    return True


def get_energy_group(n_group_size=175):
    """
    Define neutron energy group
    """
    if n_group_size == 175:
        return E_175
    elif n_group_size == 709:
        return E_709
    else:
        raise ValueError(f"Unspported energy group {n_group_size}")


def str_to_unicode(s):
    """
    This function convert a str from binary or unicode to str (unicode).
    If it is a list of string, convert every element of the list.

    Parameters:
    -----------
    s : str or list of str

    Returns:
    --------
    s : text str or list of unicode str
    """
    if isinstance(s, str) or isinstance(s, bytes):
        # it is a str, convert to text str
        try:
            s = s.decode('utf-8')
        except:
            pass
        return s
    else:
        for i, item in enumerate(s):
            try:
                s[i] = item.decode('utf-8')
            except:
                pass
        return s


def is_float(s):
    """
    This function checks whether a string can be converted as a float number.
    """
    try:
        float(s)
        return True
    except ValueError:
        return False


def str_almost_same(s1, s2, rel_tol=1e-9):
    """
    This function is used to compare two string to check whether they are
    almost the same.
    Return True if two strings are exactly the same.
    Return True if two strings are almost the same with only slight difference
    of float decimals.
    Return False if two strings are different.
    """
    # if string can be converted to float number
    if is_float(s1) and is_float(s2):
        return math.isclose(float(s1), float(s2), rel_tol=rel_tol)
    else:
        # not a number
        return s1 == s2


def line_almost_same(l1, l2, rel_tol=1e-9):
    """
    This function is used to compare two lines (read from files). If they are
    the same, or almost the same (with only slight difference on float
    numbers), return True. Ohterwise, return False.

    Parameters:
    -----------
    l1 : str
        Line 1
    l2 : str
        Line 2
    rel_tol : float
        Relative tolerance for float comparison

    Returns:
    --------
    True, if two lines are the same. False, if they are different.
    """
    if l1 == l2:
        # exactly the same
        return True
    else:
        # There are differences
        tokens1 = l1.strip().split()
        tokens2 = l2.strip().split()
        if len(tokens1) != len(tokens2):
            return False
        else:
            # compare string elements of the line
            for i in range(len(tokens1)):
                if str_almost_same(tokens1[i], tokens2[i], rel_tol=rel_tol):
                    pass
                else:
                    return False
        return True


def file_almost_same(f1, f2, rel_tol=1e-9):
    """
    For some reasones, it's useful to compare two files that are almost the
    same. Two files, f1 and f2, the text contents are exactly the same, but
    there is a small difference in numbers. Such as the difference between
    'some text 9.5' and 'some text 9.500000000001'.
    For example, in PyNE test files, there are some expected file generated
    by python2, however, the the file generated by python3 may have difference
    in decimals.

    Parameters:
    -----------
    f1 : str 
        Filename of file 1 or lines
    f2 : str
        Filename of file 2 or lines
    rel_tol : float
        Relative tolerance for float numbers

    Returns:
    True : bool
        If two file are exactly the same, or almost the same with only decimal
        differences.
    False : bool
        If the strings of the two files are different and/or their numbers differences are greater than the tolerance
    """
    if os.path.isfile(f1) and os.path.isfile(f2):
        if filecmp.cmp(f1, f2):
            # precheck
            return True
    else:
        # read lines of f1 and f2, convert to unicode
        if os.path.isfile(f1):
            with open(f1, 'r') as f:
                lines1 = f.readlines()
        else:
            lines1 = f1
        lines1 = str_to_unicode(f1)
        lines1 = lines1.strip().split(u'\n')

        if os.path.isfile(f2):
            with open(f2, 'r') as f:
                lines2 = f.readlines()
        else:
            lines2 = f2
        lines2 = str_to_unicode(f2)
        lines2 = lines2.strip().split(u'\n')

        # compare two files
        # check length of lines
        if len(lines1) != len(lines2):
            return False
        # check content line by line
        for i in range(len(lines1)):
            if line_almost_same(lines1[i], lines2[i], rel_tol=rel_tol):
                pass
            else:
                return False

    # no difference found
    return True


def neutron_intensity_to_power(value):
    """
    Convert the neutron intensity to fusion power [MW].
    1 MW fusion power is equivalent to 3.545e+17 n/s
    """
    return value / 3.545e17


# codes for test functions
if __name__ == '__main__':
    pass
