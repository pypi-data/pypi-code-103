'''
Loads equipment sizes as determined by EnergyPlus
'''

from building_plus.config.building import EIO_FIELDS


def import_sizes(filename,building):
    component = parse_eio(filename)
    for t in range(len(component['type'])):
        i_loc = EIO_FIELDS[component['type'][t]]['location']
        if len(i_loc)==2:
            if i_loc[1] in building[i_loc[0]]:
                i = building[i_loc[0]][i_loc[1]].index(component['name'][t])
            else:
                i = component['name'][t]
        elif len(i_loc)==3:
            i = building[i_loc[0]][i_loc[1]][i_loc[2]].index(component['name'][t])        
        
        try:
            par = EIO_FIELDS[component['type'][t]][component['field'][t]][0]
            if len(i_loc)==1:
                building[i_loc[0]][component['name'][t]][par] = component['value'][t]
            elif len(i_loc)==2:
                if i_loc[1]=='name' and 'name' not in building[i_loc[0]]:
                    building[i_loc[0]][i][par] = component['value'][t]
                else:
                    building[i_loc[0]][par][i] = component['value'][t]
            elif len(i_loc)==3:
                building[i_loc[0]][i_loc[1]][par][i] = component['value'][t]
        except KeyError:
            if component['field'][t]=='Design Size Reheat Coil Sizing Air Volume Flow Rate [m3/s]':
                par = 'rated_air_flow'
            elif component['field'][t]=='Design Size Reheat Coil Sizing Inlet Air Temperature [C]':
                par = 'air_inlet_temperature'
            elif component['field'][t]=='Design Size Reheat Coil Sizing Inlet Air Humidity Ratio [kgWater/kgDryAir]':
                par = 'air_inlet_humidity_ratio'
            building['coils_heating'][building['hvac']['terminals']['reheat_coil_name'][i]][par]= component['value'][t]
        
    cp_air = 1025 # J/kg*K
    air_density = 1.204 #kg/m^3 %standard air density (1.204 kg/m3) adjusted for the i_local barometric pressure (standard barometric pressure corrected for altitude, ASHRAE 1997 HOF pg. 6.1).
    for c in building['coils_heating']:
        if building['coils_heating'][c]['type'] == 'Heating:Water' and building['coils_heating'][c]['rated_air_flow'] == 0:
            building['coils_heating'][c]['rated_air_flow'] = building['coils_heating'][c]['design_capacity']/(cp_air*air_density*(building['coils_heating'][c]['air_outlet_temperature']-building['coils_heating'][c]['air_inlet_temperature']))

    for c in building['coils_cooling']:
        if building['coils_cooling'][c]['type'] == 'Cooling:Water' and building['coils_cooling'][c]['rated_air_flow'] == 0:
            building['coils_cooling'][c]['rated_air_flow'] = building['coils_cooling'][c]['design_capacity']/(cp_air*air_density*(building['coils_cooling'][c]['air_inlet_temperature']-building['coils_cooling'][c]['air_outlet_temperature']))

    building['coils_cooling'] = water_setpoint(building['coils_cooling'],'c', building['plant_demand_equip'], building['plant_supply_equip'],building['plant_loop'])
    building['coils_heating'] = water_setpoint(building['coils_heating'],'h', building['plant_demand_equip'], building['plant_supply_equip'],building['plant_loop'])
    return building


def parse_eio(filename):
    heading,z_info = read_eio(filename)
    component = {}
    c_objects = z_info['Component Sizing Information']
    var = ['type','name','field','value']
    for i in var:
        component[i] = []
    for j in range(len(c_objects)):
        component['type'].append(read_num(c_objects[j][0]))
        component['name'].append(read_num(c_objects[j][1].lower()))
        component['field'].append(read_num(c_objects[j][2]))
        component['value'].append(read_num(c_objects[j][3]))
        
    if 'Water Heating Coil Capacity Information' in z_info:
        hc_objects = z_info['Water Heating Coil Capacity Information']
        for j in range(len(hc_objects)):
            component['type'].append(hc_objects[j][0])
            component['name'].append(hc_objects[j][1].lower())
            component['field'].append(heading['Water Heating Coil Capacity Information'][1])
            component['value'].append(read_num(hc_objects[j][2]))
    if 'Water Cooling Coil Capacity Information' in z_info:
        cc_objects = z_info['Water Cooling Coil Capacity Information']
        coil_cool = heading['Water Cooling Coil Capacity Information']
        f = len(coil_cool)-1
        for p in range(len(cc_objects)):
            component['type'].extend([cc_objects[p][0] for x in range(f)])
            component['name'].extend([cc_objects[p][1].lower() for x in range(f)])
            component['field'].extend([i for i in coil_cool[1:]])
            component['value'].extend([read_num(cc_objects[p][x+2]) for x in range(f)])
    return component


def read_eio(filename):
    """Parses the given text file into a dictionary with the relevant
    data.
    """
    # Read lines of file.
    heading = {}
    z_info = {}
    with open(filename, 'r') as f:
        line = next(f)
        while True: #START with second line
            try:
                line = next(f).lstrip()
            except StopIteration:
                break
            com = [pos for pos, char in enumerate(line) if char == ',']
            if line[0]=='!':
                cat = line[3:com[0]-1]
                cat = cat.replace('<','')
                cat = cat.replace('#','')
                if len(com)==1:
                    headings = [line[com[0]+2:-1].lstrip()]
                else:
                    headings = [line[com[0]+1:com[1]].lstrip()]
                    for j in range(2,len(com)-1):
                        headings.append(line[com[j]+1:com[j+1]].lstrip())
                    headings.append(line[com[-1]+1:-1].lstrip())
                heading[cat] = headings
                z_info[cat]= []
            elif len(com)>0:
                cat = line[:com[0]]
                cat = cat.replace('<','')
                cat = cat.replace('#','')
                if len(com)==1:
                    info=[line[com[0]+1:-1].lstrip()]
                else:
                    info=[line[com[0]+1:com[1]].lstrip()]
                    for j in range(1,len(com)-1):
                        info.append(line[com[j]+1:com[j+1]].lstrip())
                    info.append(line[com[-1]+1:-1].lstrip())
                try:
                    z_info[cat].append(info)
                except KeyError:
                        pass#hopefully none of these are ones I need
    return heading,z_info


def water_setpoint(coil,c_or_h,de,se,bpl):
    for x in coil:
        if coil[x]['type'] == 'Cooling:Water:DetailedGeometry' or coil[x]['type']== 'Cooling:Water':
            try:
                pl = de['loop'][de['name'].index(x)]
            except ValueError:
                pl = se['loop'][se['name'].index(x)]
            if 'water_inlet_temperature' in coil[x]: 
                Tw_in = coil[x]['water_inlet_temperature']
            else:
                Tw_in = bpl['exit_temperature'][pl]
                coil[x]['water_inlet_temperature'] = Tw_in
            if c_or_h == 'c':
                Tw_out = Tw_in + bpl['temperature_difference'][pl]
            elif c_or_h == 'h':
                Tw_out = Tw_in - bpl['temperature_difference'][pl]
            coil[x]['water_outlet_temperature'] = Tw_out
    return coil

def read_num(n):
    """Convert to an integer or float if possible."""
    try:
        n = int(n)
    except ValueError:
        try:
            n = float(n)
        except ValueError:
            if isinstance(n, str):
                if n:
                    return n
                else:
                    return None
    return n