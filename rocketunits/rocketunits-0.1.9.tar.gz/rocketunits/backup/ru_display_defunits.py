
dD = {'Density':'lbm/in**3', 'HeatCapacity':'BTU/lbm/F', 
      'HxCoeff':'BTU/inch**2/s/F', 'ThermalCond':'BTU/hr/ft/F',
      "Temperature": "degF"}

from rocketunits import rocket_units as ru

print( 'display_def_unitsD = {} # index=category, value=default units' )

for cat in ru.categoryL:
    if cat in dD:
        def_units = dD[ cat ]
    else:
        def_units = ru.cat_defaultD[ cat ]
    
    
    if def_units not in ru.display_unitsD[cat]:
        print( '               ',def_units, 'missing for', cat )
    else:
        print( f'display_def_unitsD["{cat}"] = "{def_units}"' )
