
def convert_value( inp_val=20.0, inp_units='degC', out_units='degK'):
    """Convert inp_val from inp_units to out_units and return.
        :param inp_val   : input value to be converted
        :param inp_units : units of inp_val
        :param out_units : desired output units
        :type inp_val   : float
        :type inp_units : str
        :type out_units : str
        :return: value converted from inp_units to out_units
        :retype: float
    """
    # convert inp_val to default units
    def_unit_val = (inp_val - offsetD[inp_units]) / conv_factD[inp_units]
    # convert from default units to requested output units
    return def_unit_val * conv_factD[out_units] + offsetD[out_units]
    
# Read As: 1 default unit = conv_factD target units
def get_value_str( inp_val=20.0, inp_units='degC', out_units='degK', fmt='%g'):
    val = convert_value(inp_val=inp_val, inp_units=inp_units, out_units=out_units)
    return fmt%val + ' %s'%out_units

def get_category( units ):
    """return the category that units belongs to."""
    if units in unit_catD:
        return unit_catD[ units ]
    return ''
        

# ============== some common conversions ===================
def get_degK( val, inp_units ):
    """ val uses input units... e.g. 25, 'degC' """
    return convert_value( inp_val=float( val ), inp_units=inp_units, out_units='degK')
    
def get_degR( val, inp_units ):
    """ val uses input units... e.g. 25, 'degC' """
    return convert_value(  inp_val=float( val ), inp_units=inp_units, out_units='degR')

categoryL = list( categoryD.keys() )
categoryL.sort(key=str.lower)

MAX_UNIT_CHARS = 0
for unit in conv_factD.keys():
    MAX_UNIT_CHARS = max( MAX_UNIT_CHARS, len(unit) )
UNIT_FMT_STR = '%%%is'%MAX_UNIT_CHARS

# === to simplify output in GUI, use display_unitsD to pick units to display
# === Note that redundant units are hand-deleted

display_unitsD = {} # index=category, value = unit list in show order (small to large)
display_unitsD['Acceleration'] =  ['gee', 'm/s**2', 'mile/hr/s', 'ft/s**2', 'cm/s**2']
display_unitsD['Angle'] =  ['circle', 'revolution', 'rad', 'deg', 'grad', 'arcmin', 'arcsec']
display_unitsD['AngVelocity'] =  ['rad/s', 'rpm', 'deg/s', 'rad/min', 'deg/min']
display_unitsD['Area'] =  ['mile**2', 'acre', 'm**2', 'ft**2', 'in**2', 'inch**2', 'cm**2']
display_unitsD['DeltaT'] =  ['delC', 'delK', 'delF', 'delR']
display_unitsD['Density'] =  ['lbm/in**3', 'g/ml', 'SG', 'specific_gravity', 'slug/ft**3', 'lbm/galUS', 'lbm/ft**3', 'ounce/galUS', 'kg/m**3']
display_unitsD['ElementDensity'] =  ['elem/cm**2', 'elem/in**2']
display_unitsD['Energy'] =  ['kW*hr', 'kcal', 'W*hr', 'BTU', 'kJ', 'cal', 'ft*lbf', 'J', 'erg']
display_unitsD['EnergySpec'] =  ['kcal/g', 'kW*hr/kg', 'cal/g', 'kcal/kg', 'BTU/lbm', 'J/g', 'kJ/kg', 'J/kg']
display_unitsD['Force'] =  ['kN', 'lbf', 'N', 'dyn']
display_unitsD['Frequency'] =  ['GHz', 'MHz', 'kHz', 'Hz']
display_unitsD['HeatCapacity'] =  ['kcal/g/C', 'BTU/lbm/F', 'cal/g/C',  'kJ/kg/K', 'J/kg/K']
display_unitsD['HxCoeff'] =  [ 'BTU/inch**2/s/F', 'cal/cm**2/s/C', 'BTU/ft**2/hr/F', 'kcal/m**2/hr/C',  'W/m**2/C']
display_unitsD['Isp'] =  ['km/sec', 'lbf-sec/lbm', 'sec', 'm/sec', 'N-sec/kg']
display_unitsD['Length'] =  ['light_year', 'astronomical_unit', 'nautical_mile', 'mile', 'km', 'm', 'yd', 'ft', 'in', 'cm', 'mm', 'mil', 'micron', 'angstrom']
display_unitsD['Mass'] =  ['long_ton', 'metric_ton', 'short_ton', 'slug', 'gal_H2O', 'kg', 'lbm', 'g']
display_unitsD['MassFlow'] =  ['kg/s', 'lbm/s', 'kg/min', 'lbm/min', 'g/s', 'kg/hr', 'lbm/hr', 'g/min', 'g/hr']
display_unitsD['MolecularWt'] =  ['g/gmole', 'lbm/lbmole']
display_unitsD['Power'] =  ['MW', 'Btu/s', 'kW', 'hp', 'cal/s', 'ft*lbf/s', 'W', 'Btu/hr']
display_unitsD['Pressure'] =  ['MPa', 'atm', 'bar', 'N/cm**2', 'lbf/inch**2', 'psia', 'psid', 'inHg', 'kPa', 'mmHg', 'torr', 'lbf/ft**2', 'psf', 'N/m**2', 'Pa']
display_unitsD['SurfaceTension'] =  ['lbf/in', 'lbf/ft', 'N/m', 'mN/m', 'dyne/cm']
display_unitsD['Temperature'] =  ['degC', 'degK', 'degF', 'degR']
display_unitsD['ThermalCond'] =  [ 'BTU/s/inch/F', 'BTU/s/ft/F', 'cal/s/cm/C', 'W/cm/C', 'cal/s/m/C',  'BTU/hr/ft/F', 'W/m/K']
display_unitsD['Time'] =  ['year', 'day', 'hr', 'min', 's', 'millisec', 'ms', 'microsec', 'nanosec']
display_unitsD['Velocity'] =  ['m/s', 'mile/hr', 'ft/s', 'km/hr', 'inch/s', 'cm/s']
display_unitsD['Viscosity_Dynamic'] =  ['kg/s/cm', 'lbm/s/inch', 'lbm/s/ft', 'kg/s/m', 'Pa*s', 'poise', 'kg/hr/cm', 'lbm/hr/inch', 'cp', 'cpoise', 'lbm/hr/ft', 'kg/hr/m']
display_unitsD['Viscosity_Kinematic'] =  ['m**2/s', 'ft**2/s', 'stokes', 'ft**2/hr', 'centistokes']
display_unitsD['Volume'] =  ['m**3', 'yd**3', 'barOil', 'ft**3', 'galUK', 'galUS', 'liter', 'quart', 'pint', 'cup', 'in**3', 'inch**3', 'cm**3']
display_unitsD['VolumeFlow'] =  ['m**3/s', 'ft**3/s', 'galUS/s', 'l/s', 'ft**3/min', 'm**3/hr', 'galUS/min', 'gpm', 'inch**3/s', 'ft**3/hr', 'galUS/hr', 'ml/s', 'inch**3/min', 'galUS/day', 'ml/min', 'inch**3/hr', 'ml/hr']


if __name__ == "__main__":

    print( categoryL )
    print()
    
    for outunits in ['lbf-sec/lbm', 'm/sec', 'km/sec', 'N-sec/kg']:
        print( '452.3 sec Isp =',  get_value_str(452.3, 'sec', outunits, fmt='%g') )
    
    
    
    for i,cat in enumerate(categoryL):
        print( '%s(%i %s)'%(cat, len(categoryD[cat]), cat_defaultD[cat]), end=' ' )
        if i>0 and i%5==0:
            print()
    print()
    


    print( 'MAX_UNIT_CHARS =',MAX_UNIT_CHARS )
    
    for units in ['degC','degF','degK','degR']:
        print( '20C =', '%g'%convert_value( 20.0, 'degC', units), units )
        
    for units in ['degC','degF','degK','degR']:
        print( '20 %s ='%units, '%g'%get_degK( 20.0, units ), 
               'degK  = ', '%g'%get_degR( 20.0, units ), 'degR' )
    
    
    print( 'Check SurfaceTension:', convert_value(1.0, 'lbf/in', 'N/m'), convert_value(1.0, 'lbf/in', 'dyne/cm') )
    
    print( 'Check Frequency:', convert_value(5555.0, 'Hz', 'kHz'), convert_value(6.666, 'kHz', 'MHz') )
    

