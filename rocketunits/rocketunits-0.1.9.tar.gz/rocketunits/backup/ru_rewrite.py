
from rocketunits import rocket_units as ru

top_lines = open('ru_top.py', 'r').read()

with open("rocket_units_clean.py", "w") as fOut:
    fOut.write( top_lines )
    
    def writeln( s ):
        fOut.write( s + '\n' )

    catL = ru.categoryL
    all_unit_keyL = sorted( list(ru.unit_catD.keys()), key=lambda x:x.lower() )

    for cat in catL:
        def_units = ru.cat_defaultD[cat]
        writeln('')
        writeln(f'# Creating Unit Category for "{cat}"')
        writeln( '# Read As: 1 default unit = conv_factor u_name units' )
        writeln( f'create_category(       c_name="{cat}", def_units="{def_units}" )' )
        
        max_ulen = 1
        for u in all_unit_keyL:
            if ru.unit_catD[u] == cat:
                max_ulen = max( max_ulen, len(u) )
        max_ulen += 2
        
        for u in all_unit_keyL:
            if ru.unit_catD[u] == cat:
                conv_factor = ru.conv_factD[u]
                offset = ru.offsetD[u]
                u_name = '"%s"'%u
                u_name = u_name.ljust( max_ulen )
                
                writeln( f'add_units_to_category( c_name="{cat}", u_name={u_name}, conv_factor={conv_factor}, offset={offset} )' )
        
        
    # place bottom lines
    bottom_lines = open('ru_bottom.py', 'r').read()
    fOut.write( bottom_lines )