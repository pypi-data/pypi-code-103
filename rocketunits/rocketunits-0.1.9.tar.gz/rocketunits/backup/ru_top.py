#!/usr/bin/env python
# -*- coding: ascii -*-

r"""
RocketUnits provides a graphic user interface (GUI) for engineering units conversion.

RocketUnits provides units conversion for a number of engineering categories.
Included units categories include: Acceleration, Angle, AngVelocity, 
Area, DeltaT, Density, ElementDensity, Energy, EnergySpec, Force, Frequency, 
HeatCapacity, HxCoeff, Isp, Length, Mass, MassFlow, MolecularWt, Power, 
Pressure, SurfaceTension, Temperature, ThermalCond, Time, Velocity, 
Viscosity_Dynamic, Viscosity_Kinematic, Volume, and VolumeFlow.
Unit conversion can be performed either with the included GUI, or directly
from python by importing the units conversion data file.


RocketUnits
Copyright (C) 2020  Applied Python

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

-----------------------

"""
import os
here = os.path.abspath(os.path.dirname(__file__))


# for multi-file projects see LICENSE file for authorship info
# for single file projects, insert following information
__author__ = 'Charlie Taylor'
__copyright__ = 'Copyright (c) 2020 Charlie Taylor'
__license__ = 'GPL-3'

# run metadata_reset.py to update version number
__version__ = '0.1.4'  # METADATA_RESET:__version__ = '<<version>>'
__email__ = "cet@appliedpython.com"
__status__ = "4 - Beta" # "3 - Alpha", "4 - Beta", "5 - Production/Stable"

#
# import statements here. (built-in first, then 3rd party, then yours)
#

categoryD = {}    # index=category name, value=list of members (e.g. 'Area':['inch**2', 'ft**2', 'cm**2', 'm**2'])
cat_defaultD = {} # index=category name, value=default units (e.g. 'Area':'inch**2')
unit_catD = {}    # index=units name, value=category (e.g. 'inch':'Length')
conv_factD = {}   # index=units name, value=float conversion value to default units (e.g. 'cm':1.0/2.54)
offsetD = {}      # index=units name, value=float offset value (e.g. 'cm':0.0)

# N = 1 kg-m/sec**2,  g = 9.80665 m/sec**2
# (NOTE: time=='s',  Isp=='sec')

def create_category( c_name='', def_units='' ):
    """Create a Units Category and define the default units"""
    cat_defaultD[c_name]  = def_units
    unit_catD[def_units]  = c_name
    conv_factD[def_units] = float(1.0)
    offsetD[def_units]    = float(0.0)
    
# Read As: 1 default unit = conv_factor u_name units
def add_units_to_category( c_name="", u_name="", conv_factor=1.0, offset=0.0 ):
    """
    Add conversion factor and offset for Units(u_name) to Category(c_name)
    Read As: 1 default unit = conv_factor u_name units
    """
    unit_catD[u_name]  = c_name
    conv_factD[u_name] = float(conv_factor)
    offsetD[u_name]    = float(offset)
    
    if c_name in categoryD:
        categoryD[ c_name ].append( u_name )
    else:
        categoryD[ c_name ] = [u_name]


