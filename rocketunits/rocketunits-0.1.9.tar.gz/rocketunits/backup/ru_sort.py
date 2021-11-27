
from rocketunits import rocket_units as ru

unit_show_orderD = {} # index=category, value = unit list in show order (small to large)

catL = ru.categoryL

for cat in catL:
    unitL = []
    for u,c in ru.unit_catD.items():
        if c == cat:
            unitL.append( (ru.conv_factD[u], u.lower(),  u) ) # tuples of (factor, uname_lower, uname)
            
    unitL.sort() # sorted by factor and lower case name
    lmax = max( [len(uname) for (_,_,uname) in unitL] )
    
    fmin = min( [factor for (factor,_,_) in unitL] )
    for i,(factor, uname_lower, uname) in enumerate(unitL):
        unitL[i] = (factor/fmin, uname_lower, uname)
    
    fmt = '%' + '%is'%lmax
    
    print( cat )
    unit_show_orderD[cat] = []
    for (factor, uname_lower, uname) in unitL:
        print('    ', fmt%uname, '%12g'%factor, ru.get_category(uname) )
        unit_show_orderD[cat].append( uname )
        
    print( '    ',unit_show_orderD[cat] )
    print('='*22)

print('='*55)
print( """unit_show_orderD = {} # index=category, value = unit list in show order (small to large)""" )
for cat in ru.categoryL:
    print( "unit_show_orderD['%s'] = "%cat, unit_show_orderD[cat] )


