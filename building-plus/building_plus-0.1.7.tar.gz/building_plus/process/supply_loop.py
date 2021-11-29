from building_plus.components.manager_override import manager_override
from building_plus.basic.eval_curve import eval_curve
from building_plus.components.water_heater import water_heater
from building_plus.components.cooling_tower import cooling_tower
from building_plus.process.flow_resolver_supply import boiler_PLR
from building_plus.process.flow_resolver_supply import chiller_PLR

def supply_loop(building,profile,plant_nodes,wh_tank,T_air,w_air,l,dt):
    Cp_water = 4186  #J/kg*K
    fresh_air = {}
    fresh_air['Tdb'] = T_air 
    fresh_air['w'] = w_air 
    cool_elec = 0
    heat_gas = 0
    water_gas = 0
    water_elec = 0
    tower_elec = 0
    s_equip = building['plant_supply_equip'] 
    d_equip = building['plant_demand_equip'] 
    on_loop = [i for i,x in enumerate(s_equip['loop']) if x == l]
    for j in on_loop:
        T_target = building['plant_loop']['exit_temperature'][l] 
        node = building['plant_loop']['setpoint_node'][l] 
        T_target = manager_override(building,profile,node,T_target,None,fresh_air,None) 
        in_n = s_equip['inlet'][j] 
        out_n = s_equip['outlet'][j] 
        if s_equip['type'][j]=='pipe:adiabatic':
            plant_nodes['supply_temperature'][out_n] = plant_nodes['supply_temperature'][in_n] 
        elif s_equip['type'][j]=='mixer':
            if type(in_n) !=list:
                in_n = [in_n]
            if plant_nodes['supply_flow'][out_n]>0:
                plant_nodes['supply_temperature'][out_n] = sum([plant_nodes['supply_temperature'][k]*plant_nodes['supply_flow'][k]/plant_nodes['supply_flow'][out_n] for k in in_n])
            else: #avoid divide by zero
                plant_nodes['supply_temperature'][out_n] = sum([plant_nodes['supply_temperature'][k] for k in in_n]) 
        elif s_equip['type'][j]=='splitter':
            if type(out_n) !=list:
                out_n = [out_n]
            for k in out_n:
                plant_nodes['supply_temperature'][k] = plant_nodes['supply_temperature'][in_n] 
        elif s_equip['type'][j]=='chiller:electric:reformulatedeir' or s_equip['type'][j]=='chiller:electric:eir':
            PLR,Q_evap,plant_nodes['supply_temperature'][out_n],Q_avail,c = chiller_PLR(building,s_equip['name'][j],plant_nodes['supply_flow'][in_n],plant_nodes['supply_temperature'][in_n],plant_nodes['supply_temperature'][out_n])
            if PLR > 0:
                cycling_ratio = min(PLR/building['chiller'][c]['min_part_load'],1) 
                PLR = max(PLR,building['chiller'][c]['min_unload_ratio']) 
                Q_false_load = Q_avail*PLR*cycling_ratio - Q_evap 
                if 'electric_in_out_curve_type' in building['chiller'][c]:
                    if building['chiller'][c]['electric_in_out_curve_type']=='leavingcondenserwatertemperature':
                        C_EIR_PLR = eval_curve(building['curves'],building['chiller'][c]['electric_in_out_part_load_curve'],[building['chiller'][c]['condenser_water_temperature_ref'],PLR]) 
                    else:
                        dT_ref = building['chiller'][c]['condenser_water_temperature_ref'] - building['chiller'][c]['chilled_water_temperature_ref']
                        dT = (building['chiller'][c]['condenser_water_temperature_ref'] - plant_nodes['supply_temperature'][out_n])/dT_ref 
                        T_dev = (plant_nodes['supply_temperature'][out_n] - building['chiller'][c]['chilled_water_temperature_ref'])/dT_ref 
                        C_EIR_PLR = eval_curve(building['curves'],building['chiller'][c]['electric_in_out_part_load_curve'],[dT,PLR,T_dev]) 
                else:
                    C_EIR_PLR = eval_curve(building['curves'],building['chiller'][c]['electric_in_out_part_load_curve'],[PLR]) 
                CEIR_T = eval_curve(building['curves'],building['chiller'][c]['electric_in_out_temperature_curve'],[plant_nodes['supply_temperature'][out_n],building['chiller'][c]['condenser_water_temperature_ref']]) 
                P_chiller = PLR*Q_avail*(1/building['chiller'][c]['COP_ref'])*CEIR_T*C_EIR_PLR*cycling_ratio 
                if building['chiller'][c]['frac_power_2_condenser']== None:
                    Q_cond = Q_evap+Q_false_load
                else:
                    Q_cond = (P_chiller*building['chiller'][c]['frac_power_2_condenser'])+Q_evap+Q_false_load 
                if 'condenser_type' in building['chiller'][c] and building['chiller'][c]['condenser_type']=='aircooled':
                    pass
                    ## Do something for air_cooled chiller?
                else:#water cooled
                    d_e_num = d_equip['name'].index(s_equip['name'][j])
                    plant_nodes['load'][d_equip['outlet'][d_e_num]] = Q_cond 
                    plant_nodes['demand_flow'][d_equip['outlet'][d_e_num]] = Q_cond/(Cp_water*building['plant_loop']['temperature_difference'][l]) 
                cool_elec += P_chiller #Watts
        elif s_equip['type'][j]=='boiler:hotwater':
            PLR,load,plant_nodes['supply_temperature'][out_n],b = boiler_PLR(building,s_equip['name'][j],plant_nodes['supply_flow'][in_n],plant_nodes['supply_temperature'][in_n],plant_nodes['supply_temperature'][out_n])
            if load>0:
                if building['boiler'][b]['normalized_eff_curve']==None:
                    eff = building['boiler'][b]['efficiency']
                else:
                    try:
                        eff = eval_curve(building['curves'],building['boiler'][b]['normalized_eff_curve'],[PLR,plant_nodes['supply_temperature'][out_n]]) 
                    except ValueError:
                        print('error in manage_plant_equip, supply_loop')
                heat_gas += load/eff #Watts
        elif s_equip['type'][j]=='pump:variablespeed' or s_equip['type'][j]=='pump:constantspeed':
            ## pump heat goes into tank at start of half-loop
            plant_nodes['supply_temperature'][out_n] = plant_nodes['supply_temperature'][in_n] 
        elif s_equip['type'][j]=='waterheater:mixed':
            T_exit = profile[building['water_heater'][s_equip['name'][j]]['temperature_schedule']]
            wh_tank[s_equip['name'][j]]['T'],wh_tank[s_equip['name'][j]]['on'],wh_gas,wh_elec = water_heater(building,wh_tank[s_equip['name'][j]]['T'],wh_tank[s_equip['name'][j]]['on'],T_exit,T_air,plant_nodes['supply_temperature'][in_n],plant_nodes['supply_flow'][in_n],dt,s_equip['name'][j]) 
            water_gas += wh_gas
            water_elec += wh_elec
            plant_nodes['supply_temperature'][out_n] = wh_tank[s_equip['name'][j]]['T'] 
        elif (s_equip['type'][j]=='coolingtower:singlespeed' or
              s_equip['type'][j]=='coolingtower:twospeed' or
              s_equip['type'][j]=='coolingtower:variablespeed:merkel'):
            P_fan,plant_nodes['supply_temperature'][out_n],bypass = cooling_tower(building,s_equip['name'][j],plant_nodes['supply_flow'][in_n],plant_nodes['supply_temperature'][in_n],T_target,T_air,w_air) 
            tower_elec += P_fan #Watts
        else:
            print('need additional plant supply loop component__' + s_equip['type'][j])
    return plant_nodes,wh_tank,cool_elec,heat_gas,water_gas,water_elec,tower_elec