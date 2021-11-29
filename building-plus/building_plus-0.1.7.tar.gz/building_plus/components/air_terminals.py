from building_plus.components.water_coil import water_coil

def air_terminals(building,air_nodes,zone_air,e_use,plant_nodes,terminal_T_supply):
    ## re-heat or zone box cooling 
    air_density = 1.204 #kg/m^3 #standard air density (1.204 kg/m3) adjusted for the local barometric pressure (standard barometric pressure corrected for altitude, ASHRAE 1997 HOF pg. 6.1).
    for j in range(len(building['hvac']['terminals']['name'])):
        if building['hvac']['terminals']['type'][j]=='SingleDuct:Uncontrolled':
            pass###
        elif building['hvac']['terminals']['type'][j]=='SingleDuct:ConstantVolume:Reheat':
            pass###
        elif building['hvac']['terminals']['type'][j]=='SingleDuct:VAV:Reheat':
            z = building['hvac']['terminals']['zone'][j]
            if terminal_T_supply[z]>zone_air['Tdb'][z]:
                air = {}
                for x in zone_air:
                    air[x] = zone_air[x][z]
                air['m_dot'] = air['m_dot']*building['zones']['multiplier'][z]
                #update intermediate air as it passes between equipment
                name = building['hvac']['terminals']['reheat_coil_name'][j]
                c = building['coils_heating'][name]
                if c['type'] == 'Heating:Fuel' or c['type']=='Heating:Electric':
                        cp_air = (1006 + 1860*air['w'])*air_density #Specific heat in J/m^3
                        Q_terminal = air['m_dot']*cp_air*(terminal_T_supply[z] - air['Tdb'])
                        air['Tdb'] = terminal_T_supply[z]
                        if c['type'] == 'Heating:Fuel':
                            e_use['heat_gas'] += Q_terminal/c['efficiency'] #heat added in W
                        elif c['type']=='Heating:Electric':
                            e_use['heat_elec'] += Q_terminal/c['efficiency'] #heat added in W
                elif c['type'] == 'Heating:Water' or c['type'] == 'Cooling:Water':
                        air,m_w,actual_load,out = water_coil(building,name,air,terminal_T_supply[z],plant_nodes)
                        plant_nodes['demand_flow'][out] = m_w #kg/s
                        plant_nodes['load'][out] = actual_load #load in Watts (negative because air leaves hotter)
                air['m_dot'] = air['m_dot']/building['zones']['multiplier'][z]
                for x in zone_air:
                    zone_air[x][z] = air[x]
    return zone_air,e_use,plant_nodes