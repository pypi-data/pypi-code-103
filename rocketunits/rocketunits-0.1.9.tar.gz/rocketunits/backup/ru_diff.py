
from rocketunits import rocket_units as ru

for cat, catL in ru.categoryD.items():

    # cL will include missing items in catL
    cL = []
    actual_catD = {}
    for unit,c in ru.unit_catD.items():
        if c in actual_catD:
            actual_catD[c].append( unit )
        else:
            actual_catD[c] = [unit]
            
        if cat == c:
            cL.append( c )
    
    if len(cL) != len(catL):
        diff = len(cL) - len(catL)
        print(cat, 'missing', diff )
        print( '    ', set(actual_catD[cat]) - set(catL) )
        