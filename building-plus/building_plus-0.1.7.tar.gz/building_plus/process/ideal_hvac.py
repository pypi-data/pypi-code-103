'''
Iterate to find central air and direct zone air temperature and flow that achieves temperature constraints
'''

from building_plus.basic.psychometric import psychometric
from building_plus.process.window_temperature import window_temperature
from building_plus.basic.natural_convection import natural_convection
from building_plus.components.water_coil import water_coil
from building_plus.components.fan_calc import fan_calc
from building_plus.components.manager_override import manager_override
from building_plus.process.update_model_states_implicit import update_model_states_implicit
from building_plus.components.availability_managers import availability_managers
from building_plus.basic.leward_calc import leward_calc
from building_plus.basic.wind_speed_calc import wind_speed_calc

def ideal_hvac(building,profile,leward,wind_speed,S,air_nodes,dry_bulb,mixing,infiltration,gains,T,w,T_set,w_set,occupancy,dt,des_day):
    air_density = 1.204 #kg/m^3  #standard air density (1.204 kg/m3) adjusted for the local barometric pressure (standard barometric pressure corrected for altitude, ASHRAE 1997 HOF pg. 6.1).
    n_z = len(T['zone'])
    n_sur = len(building['surfaces']['name'])
    n_win = len(building['windows']['name'])
    fresh_air = {}
    fresh_air['Tdb'] = dry_bulb
    fresh_air['w'] = w['air']+0
    fresh_air['h'] = psychometric(fresh_air,'h')
    cp_zone = [(1006 + 1860*w['zone'][i])*air_density for i in range(n_z)] #Specific heat in J/m^3
    T['zone_est'] = [j for j in T['zone']]
    T['surf_est'] = [j for j in T['surf']]
    w['zone_est'] = [j for j in w['zone']] #estimated values at the end of the time step
    T['central'] = []
    fresh_air_zone_req = design_zone_outdoor_air(building,occupancy) #requested fresh air of the zone
    net_H2O_gain = [gains['zone_latent'][i]/2264705 + air_density*(sum([mixing[i][j]*w['zone'][j] for j in range(len(mixing[i]))]) + infiltration[i]*w['air']) for i in range(len(infiltration))] #flows in m^3/s converted to kg/s, everything into kg/s of water 
    fan_avail = {}
    for i in building['fans']:
        fan_avail[i] = profile[building['fans'][i]['schedule']]
    
    Q_transient = [[],[]]
    Q_transient[0] = [(T['zone'][k] - T_set['cool'][k])*cp_zone[k]*building['zones']['volume'][k]/dt for k in range(n_z)]
    if T_set['dual_sp']:
        Q_transient[1] = [(T['zone'][k] - T_set['heat'][k])*cp_zone[k]*building['zones']['volume'][k]/dt for k in range(n_z)] #zone heat capacitance*deltaT/dt = power (W)

    Q_Tset = [[],[]]
    T_loop = [13 for i in range(len(building['hvac']['loop']['name']))]
    w['loop'] = [.01 for i in range(len(building['hvac']['loop']['name']))]
    window_wind_speed = [wind_speed[building['windows']['ext_surf'][i]] for i in range(n_win)]
    window_leward = [leward[building['windows']['ext_surf'][i]] for i in range(n_win)]
    window_air_temp = [dry_bulb - 0.0065*building['windows']['height'][i]+273 for i in range(n_win)]

    tol = building['site']['temp_tol']
    max_e = 10*tol
    count = 0
    while count<8 and max_e>0.1*tol:
        ## Windows
        T_interior = [T['surf_est'][i] for i in building['ctf']['sur_state1']]
        T_int_K = [T_interior[i]+273 for i in range(len(T_interior))]
        window_zone_temp = [T['zone_est'][building['windows']['zone_index'][i]]+273 for i in range(n_win)]        
        cp_window = [cp_zone[building['windows']['zone_index'][i]] for i in range(n_win)]
        T['windows'],T['windows_int'],Q_windows,_ = window_temperature(building,window_wind_speed,window_leward,S,T['windows'],T['windows_int'],
                                        T['sky']+273,window_zone_temp,window_air_temp,T_int_K,cp_window)
        
        ## Predicts the zone energy exchange that achieves the temperature setpoints 
        ## Assume convection and mixing at expected zone/surface temperatures
        dT = [T_interior[i] - T['zone_est'][building['surfaces']['zone_index'][i]] for i in range(n_sur)] #interior surface convection = h*A*(Tsur - Tzone) 
        h_interior = natural_convection(building['surfaces']['normal'],dT,T_set['no_hvac'],building['convection']['interior'])
        Q_mixing = [cp_zone[i]*(sum([mixing[i][j]*T['zone_est'][j] for j in range(n_z)]) - sum(mixing[i])*T['zone_est'][i])for i in range(n_z)]  #heat into zone via mixing from another zone
        Q_infiltration = [cp_zone[i]*infiltration[i]*(T['air_zone'][i] - T['zone_est'][i]) for i in range(n_z)] #heat into zone from air infiltration 
        Q_Tset = qset(T_set,building,gains['zone_sensible'],Q_windows,Q_transient,Q_infiltration,Q_mixing,T_interior,h_interior)#Energy required by the zone in W 
        
        ## determine the supply flow rate and temperature to each zone/loop that will result in the desired zone temperature (passive control within deadband)
        T_min,T_max = zone_limits(building,T['zone_est'])
        exhaust_flow = exhaust_fan_flow(building,profile,mixing)
        flow_imbalance = [infiltration[i] - exhaust_flow[i] for i in range(n_z)] #volumetric flow (m^3/s)

        if not des_day:
            central_flow = terminal_flow(building,Q_Tset,T_set,cp_zone,T_min,T_max,T['central'],flow_imbalance,fan_avail,T_loop,w['loop'],T['air_zone'][0])
            loop_flow = supply_flow_limit(building,profile,central_flow,fan_avail) #enforces minimum and maximum flow rates     
            loop_2_zone,central_flow = divide_loop_flow(building,loop_flow,central_flow)
            direct_flow = zone_hvac_flow(building,profile,Q_Tset)
            fresh_air_loop = loop_outdoor_air(building,profile,fresh_air_zone_req,central_flow,loop_flow,flow_imbalance)
            direct_fresh_air = direct_zone_outdoor_air(building,profile,Q_Tset,flow_imbalance,central_flow)
        else:
            central_flow,direct_flow,loop_flow,direct_fresh_air,fresh_air_loop = des_day_zone_flow(building,fresh_air_zone_req,cp_zone,Q_Tset,T_set,T_min,T_max,flow_imbalance)
        
        flow_exiting_zone,return_flow,plenum = plenum_return_flow(building,profile,central_flow,direct_flow,mixing,infiltration)
        direct_return_air,loop_return_air = return_air_calc(building,gains,T['zone_est'],w['zone_est'],return_flow,direct_flow,direct_fresh_air)
        T_loop,w['loop'],mixed_air_loop,air_nodes = loop_supply_setpoint(building,profile,air_nodes,fresh_air,fresh_air_loop,loop_return_air,loop_flow,central_flow,loop_2_zone,cp_zone,flow_exiting_zone,net_H2O_gain,T_set,w_set,Q_Tset,T_min,T_max,fan_avail,des_day)
        supply_flow,T,w = zones_supply_setpoint(building,T,w,central_flow,cp_zone,T_loop,direct_return_air,T_set,Q_Tset,T_min,T_max,fresh_air,direct_fresh_air,direct_flow,fan_avail)

        ## Estimate of zone conditions if HVAC logic is applied
        T_z_new,T['surf_est'],w['zone_est'],e_dict = update_model_states_implicit(building,T,S,wind_speed,leward,gains,dt,w,mixing,plenum,infiltration,supply_flow)

        ## add night manager here, if it turns things on or off, don't update T.zone_est, and don't count up
        fan_avail,override = availability_managers(building,T_z_new,T_set,dt,fan_avail)
        if override:
            max_e = 10*tol
        else:
            max_e = max([abs(T_z_new[i] - T['zone_est'][i]) for i in range(n_z)])
            cp_zone = [(1006 + 1860*w['zone_est'][i])*air_density for i in range(n_z)] #Specific heat in J/m^3
            T['zone_est'] = [j for j in T_z_new]
            count +=1    

    # print('ideal_hvac loops:  ' + str(count))
    # if any([T['zone_est'][j]<T_set['heat'][j]- building['hvac']['managers']['thermostat_tolerance'][building['zones']['air_loop'][j]] and not T_set['no_hvac'][j] for j in range(len(T['zone_est']))]):
    #     ## estimate shortfall of HVAC treatment
    #     zone_cool = [supply_flow['flow'][z]*cp_zone[z]*(supply_flow['Tdb'][z]- T_set['cool'][z]) for z in range(n_z)]
    #     zone_heat = [supply_flow['flow'][z]*cp_zone[z]*(supply_flow['Tdb'][z]- T_set['heat'][z]) for z in range(n_z)]
    #     cooling_shortfall_perc = [0 if zone_cool[z] == 0 else 100*max(0,-Q_Tset[0][z] - zone_cool[z])/(-Q_Tset[0][z]) for z in range(n_z)]
    #     heating_shortfall_perc = [0 if zone_heat[z] == 0 else 100*max(0,Q_Tset[1][z] - zone_heat[z])/Q_Tset[1][z] for z in range(n_z)]
    #     print('investigate why building not reaching setpoint')
    return air_nodes,central_flow,direct_flow,mixed_air_loop,direct_return_air,plenum,T,w,fan_avail

def qset(T_set,building,sensible_gain,Q_windows,Q_trans,Q_infiltration,Q_mixing,T_interior,h_interior):
    # Detrimes the energy requirment to be within acceptable temperature window
    # + is heating, - is cooling
    # if no heating is required to reach heating setpoint and no cooling required to reach cooling setpoint then temperature can drift naturally
    # Q_set[0][i] represents the heating required to reach the cooling setpoint in zone 1. A negative value requires cooling
    # Q_set[1][i] represents the heating required to reach the heating setpoint in zone 1. A positive value requires heating
    Q_set = [[],[]]
    n_z = len(T_set['cool'])
    n_sur = len(building['surfaces']['name'])
    Q_surfaces = [sum([-h_interior[j]*(T_set['cool'][k]- T_interior[j])*building['surfaces']['area'][j] for j in range(n_sur) if building['surfaces']['zone_index'][j] ==k]) for k in range(n_z)] #estimated heat transfer to zone from walls/floor/ceiling 
    Q_set[0] = [-(sensible_gain[j] + Q_windows[j] + Q_mixing[j] + Q_infiltration[j] + Q_trans[0][j] + Q_surfaces[j]) if not T_set['no_hvac'][j] else 0 for j in range(n_z)]#Energy provided to the zone in W to achieve T_set.cool, + is heating
    if T_set['dual_sp']:
        Q_surfaces = [sum([-h_interior[j]*(T_set['heat'][k]- T_interior[j])*building['surfaces']['area'][j] for j in range(n_sur) if building['surfaces']['zone_index'][j] ==k]) for k in range(n_z)] #estimated heat transfer to zone from walls/floor/ceiling 
        Q_set[1] = [-(sensible_gain[j] + Q_windows[j] + Q_mixing[j] + Q_infiltration[j] + Q_trans[1][j] + Q_surfaces[j]) if not T_set['no_hvac'][j] else 0 for j in range(n_z)]#Energy provided to the zone in W to achieve T_set.heat, + is heating
    else:
        Q_set[1] = Q_set[0]
    return Q_set

def design_zone_outdoor_air(building,occupancy):
    '''
    ##Determine max fresh air requirements
    '''
    n_z = len(building['zones']['name'])
    fresh_air_zone = [0 for i in range(n_z)]
    for i in range(n_z):
        try:
            z = building['setpoints']['zone'][i]
            if building['setpoints']['outdoor_flow_method'][i]=='flow/person':
                    fresh_air_zone[z] = building['setpoints']['outdoor_flow_value'][i]*occupancy[z]
            elif building['setpoints']['outdoor_flow_method'][i]=='flow/area':
                    fresh_air_zone[z] = building['setpoints']['outdoor_flow_value'][i]*building['zones']['floor_area'][z]
            elif building['setpoints']['outdoor_flow_method'][i]=='flow/zone':
                    fresh_air_zone[z] = building['setpoints']['outdoor_flow_value'][i]    
        except IndexError:
            pass
    return fresh_air_zone

def zone_limits(building,T_zone):
    T_min = [0 for i in range(len(T_zone))]
    T_max = [0 for i in range(len(T_zone))]
    for i in range(len(building['setpoints']['name'])):
        z = building['setpoints']['zone'][i]
        if building['setpoints']['cooling_T_method'][i]=='supplyairtemperature':
            T_min[z] = building['setpoints']['cooling_T_des'][i]
        else:
            T_min[z] -= building['setpoints']['cooling_dT_des'][i]
        if building['setpoints']['heating_T_method'][i]== 'supplyairtemperature':
            T_max[z] = building['setpoints']['heating_T_des'][i]
        else:
            T_max[z] += building['setpoints']['heating_dT_des'][i]
    for i in range(len(building['manager']['name'])):
        if building['manager']['type'][i]=='SingleZone:Reheat':
            z = building['zones']['name'].index(building['manager']['zone'][i])
            T_min[z] = building['manager']['min_temp'][i]
            T_max[z] = building['manager']['max_temp'][i]
    return T_min,T_max

def  exhaust_fan_flow(building,profile,mixing):
    ##exhaust fans
    n_z = len(building['zones']['name'])
    exhaust_flow = [-sum([mixing[j][i] for j in range(n_z)]) for i in range(n_z)]#balanced exhaust flow (m^3/s)
    for i in building['fans']:
        if building['fans'][i]['exhaust']:
            exhaust_flow[building['fans'][i]['exhaust_zone']] += building['fans'][i]['flow_rate']*profile[building['fans'][i]['schedule']] #volumetric flow (m^3/s)   #See page 1601 of the reference manual
    return exhaust_flow

def terminal_flow(building,Q_Tset,T_set,cp_zone,T_min,T_max,T_central,flow_imbalance,fan_avail,T_loop,w_loop,T_air):
    ##do VAV terminal air calculations  
    #Determine flow rate to zones, based on fan flow limits, fresh air requirements and if HVAC is on
    air_density = 1.204 #kg/m^3  #standard air density (1.204 kg/m3) adjusted for the local barometric pressure (standard barometric pressure corrected for altitude, ASHRAE 1997 HOF pg. 6.1).
    hv = building['hvac']
    n_z = len(T_min)
    zone_flow_req = [0 for i in range(n_z)]
    for i in range(n_z):
        if T_set['no_hvac'][i]:
            pass
        elif Q_Tset[1][i]>0: #heating
            zone_flow_req[i] = Q_Tset[1][i]/(cp_zone[i]*(T_max[i] - T_set['heat'][i]))
        elif Q_Tset[0][i]<0:#cooling
            zone_flow_req[i] =  Q_Tset[0][i]/(cp_zone[i]*(T_min[i] - T_set['cool'][i]))

    n = len(hv['terminals']['name'])
    term_flow = [0 for i in range(n)]
    min_term_flow = [0 for i in range(n)]
    if 'min_flow' in hv['terminals']:
        for i in range(n):
            if hv['terminals']['min_flow'][i] == None:
                min_term_flow[i] = 0
            else:
                min_term_flow[i] = hv['terminals']['min_flow'][i]/building['zones']['multiplier'][hv['terminals']['zone'][i]]        
    max_term_flow = [hv['terminals']['max_flow'][i]/building['zones']['multiplier'][hv['terminals']['zone'][i]] for i in range(n)]

    for i in range(len(hv['loop']['name'])):# find the fan on the air loop and adjust min/max flow by fan availability
        term_i = []
        z_i = []
        m = []
        no_flow = False
        for x in range(len(building['air_supply_equip']['loop'])):
            if building['air_supply_equip']['loop'][x] ==i and (building['air_supply_equip']['type'][x][:4]=='fan:'):
                f = building['air_supply_equip']['name'][x]
        for j , k in enumerate( hv['terminals']['loop']):
            if k==i:
                min_term_flow[j] = min_term_flow[j]*fan_avail[f]
                max_term_flow[j] = max_term_flow[j]*fan_avail[f]
                if fan_avail[f]==0:
                    no_flow = True
        
                #Cooling mode:supply temperature is based on limiting zone, other zones operate with reduced flow. If a terminal minimum flow is hit, re-heat prevents from overcooling
                #Heating mode: minimum flow. re_heat does all necessary heating
                term_i.append(j)
                z_i.append(hv['terminals']['zone'][j])
                m.append(building['zones']['multiplier'][hv['terminals']['zone'][j]])
        if not no_flow:
            if hv['terminals']['type'][term_i[0]]=='SingleDuct:Uncontrolled': #what if terminals on same loop are of different variety? Not an issue with default buildings
                for j in range(len(z_i)):
                    term_flow[term_i[j]] =  zone_flow_req[z_i[j]] #volumetric flow m^3/s
            elif hv['terminals']['type'][term_i[0]]=='SingleDuct:ConstantVolume:Reheat':
                    print('has constantvolume:reheat, dont know what to do')
            elif hv['terminals']['type'][term_i[0]]=='SingleDuct:VAV:Reheat':
                if len(z_i) == 1:#loop serves a single zone, heating = min flow, vary temp ... cooling = supply temp, vary flow
                    if Q_Tset[0][z_i[0]]<0 and T_set['no_hvac'][z_i[0]]==False: #cooling
                        term_flow[term_i[0]] = zone_flow_req[z_i[0]]
                    else: #if not cooling, set to minimuim (bottom of page 694)
                        term_flow[term_i[0]] = min_term_flow[term_i[0]]
                else: #loop serves multiple zones, must supply at temperature that provides sufficient cooling to all zones at max flow
                    #find the limiting zone, i.e. max flow at this supply temperature = perfect cooling. Other zones have re-heat
                    if any([Q_Tset[0][x]<0 and T_set['no_hvac'][x]==False for x in z_i]): #loop in cooling mode for at least 1 zone
                        cool_T = [max(T_min[z_i[j]],T_set['cool'][z_i[j]] + Q_Tset[0][z_i[j]]/(cp_zone[z_i[j]]*max_term_flow[term_i[j]])) for j in range(len(z_i))]
                        min_cooling_T = min(cool_T)
                        if len(T_central)>0:
                            min_cooling_T = min(min_cooling_T,min([T_central[z_k] for z_k in z_i]))
                        ## If it can reach below min_cooling without chillers, then preferable to be at lower temperature and reduced flow. 
                        if T_air<min_cooling_T:
                            min_cooling_T = max(max([T_min[zk] for zk in z_i]),T_air)

                        for j in range(len(z_i)):
                            no_treat_cooling = min_term_flow[term_i[j]]*cp_zone[z_i[j]]*(T_set['heat'][z_i[j]] - min_cooling_T) #m*cp*deltaT at minimum flow and temperature
                            if Q_Tset[0][z_i[j]]<0 and T_set['no_hvac'][z_i[j]]==False:
                                term_flow[term_i[j]] = Q_Tset[0][z_i[j]]/(cp_zone[z_i[j]]*(min_cooling_T - T_set['cool'][z_i[j]])) #volumetric flow m^3/s
                            elif (Q_Tset[1][z_i[j]] + no_treat_cooling)>0 and T_set['no_hvac'][z_i[j]] == False:
                                term_flow[term_i[j]] = (Q_Tset[1][z_i[j]] + no_treat_cooling)/(cp_zone[z_i[j]]*(T_max[z_i[j]] - T_set['heat'][z_i[j]])) #volumetric flow m^3/s
                            else: 
                                term_flow[term_i[j]] = 0
                    else: #passive or heating
                        for j in range(len(z_i)):
                            if Q_Tset[1][z_i[j]]>0:
                                if hv['terminals']['reheat_coil_type'][term_i[j]]=='coil:heating:water':
                                    name = hv['terminals']['reheat_coil_name'][term_i[j]]
                                    max_flow = air_density*building['hvac']['terminals']['max_flow'][term_i[j]]
                                    air,_,_,_ = water_coil(building,name,T_set['heat'][z_i[j]],Q_Tset[1][z_i[j]]*m[j],[T_loop[i],w_loop[i],max_flow])
                                    term_flow[term_i[j]] = air['m_dot']/air_density/m[j]
                                else:
                                    term_flow[term_i[j]] = Q_Tset[1][z_i[j]]/(cp_zone[z_i[j]]*(T_max[z_i[j]]-T_set['heat'][z_i[j]]))
            else:
                print('need additional air terminal types')
    central_flow = [0 for i in range(n_z)]
    for i in range(len(hv['terminals']['name'])):
        if T_set['no_hvac'][hv['terminals']['zone'][i]]==False:
            term_flow[i] =  max(term_flow[i], -flow_imbalance[hv['terminals']['zone'][i]]) #volumetric flow m^3/s
        term_flow[i] =  min(max(term_flow[i],min_term_flow[i]),max_term_flow[i])
        central_flow[hv['terminals']['zone'][i]] = term_flow[i]
    return central_flow

def supply_flow_limit(building,profile,central_flow,fan_avail):
    #reduce flow if any equipment in air_loop limits flow
    n_z = len(building['zones']['name'])
    n_l = len(building['hvac']['loop']['name'])
    limit_flow = [x for x in building['hvac']['loop']['max_flow']] #volumetric flow (m3/s)
    minimum_flow = [0 for x in building['hvac']['loop']['max_flow']] #volumetric flow (m3/s)
    ##go through equipment and reduce if schedule is reduced
    for i in range(len(building['air_supply_equip']['name'])):
        loop = building['air_supply_equip']['loop'][i]
        if building['air_supply_equip']['type'][i]=='CoilSystem:Cooling:DX' or building['air_supply_equip']['type'][i]=='Coil:Cooling:Water':
                k = building['coils_cooling']['name'].index(building['air_supply_equip']['name'][i])
                sched = building['coils_cooling']['schedule'][k]
                limit_flow[loop] = min(limit_flow[loop],building['coils_cooling']['rated_air_flow'][k]*profile[sched]) # #mass flow (kg/s)
        elif building['air_supply_equip']['type'][i][:4]=='fan:':
                fan_name = building['air_supply_equip']['name'][i]
                minimum_flow[loop],limit_flow[loop] = fan_flow_limit(building,fan_avail[fan_name],minimum_flow[loop],limit_flow[loop],fan_name)
        elif building['air_supply_equip']['type'][i]=='airloophvac:unitaryheatcool':
                u = building['unitary_heat_cool']['name'].index(building['air_supply_equip']['name'][i])
                fan_name = building['unitary_heat_cool']['fan_name'][u]
                minimum_flow[loop],limit_flow[loop] = fan_flow_limit(building,fan_avail[fan_name],minimum_flow[loop],limit_flow[loop],fan_name)         
    loop_flow = [0 for i in range(n_l)]
    for i in range(n_z):
        if building['zones']['air_loop'][i]!=None:
            loop_flow[building['zones']['air_loop'][i]] += central_flow[i]*building['zones']['multiplier'][i] #volumetric flow (m3/s)
    for i in range(n_l):
        if loop_flow[i]>limit_flow[i]:
            loop_flow[i]=limit_flow[i]
        elif loop_flow[i]<minimum_flow[i]:
            loop_flow[i]=minimum_flow[i]
    return loop_flow

def fan_flow_limit(building,fan_avail,minimum,limit,f):
    if building['fans'][f]['type']=='ConstantVolume' or building['fans'][f]['type']=='OnOff':
        limit_flow = building['fans'][f]['flow_rate']*fan_avail #volumetric flow (m3/s)
        min_flow = building['fans'][f]['flow_rate']*fan_avail #volumetric flow (m3/s)
    elif building['fans'][f]['type']=='VariableVolume':
        limit_flow = min(limit,building['fans'][f]['flow_rate']*fan_avail) #volumetric flow (m3/s)
        min_flow = max(minimum,building['fans'][f]['min_flow_rate']*fan_avail) #volumetric flow (m3/s)   
    elif building['fans'][f]['type']=='Fan:SystemModel':
            print('need to program Fan:SystemModel')
    return min_flow,limit_flow

def divide_loop_flow(building,loop_flow,central_flow):
    n_z = len(building['zones']['name'])
    n_l = len(building['hvac']['loop']['name'])
    loop_2_zone = [[0 for j in range(n_l)] for i in range(n_z)]
    zone_request= [[0 for j in range(n_l)] for i in range(n_z)]
    loop_request = [0 for i in range(n_l)]
    adj_central_flow = []
    for i in range(n_z):
        l=building['zones']['air_loop'][i]
        if l!=None:
            zone_request[i][l]= central_flow[i]*building['zones']['multiplier'][i]
            loop_request[l] += zone_request[i][l]
            
    for l in range(n_l):
        if loop_flow[l]>0 and loop_request[l]==0: #split flow based on heating/cooling request flow #avoid NaN, split to zones based on max zone flow
            n_t = len(building['hvac']['terminals']['name'])
            for j in range(n_t):
                if building['zones']['air_loop'][building['hvac']['terminals']['zone'][j]]==l:
                    zone_request[building['hvac']['terminals']['zone'][j]][l] += building['hvac']['terminals']['max_flow'][j]
            loop_request[l] = sum([zone_request[i][l] for i in range(n_z)])
        for i in range(n_z):
            if loop_request[l]>0:
                loop_2_zone[i][l] = zone_request[i][l]/loop_request[l]
    for i in range(n_z):
        adj_central_flow.append(sum([loop_flow[l]*loop_2_zone[i][l] for l in range(n_l)])/building['zones']['multiplier'][i]) #loop flow adjusted in air loop flow constraints were active
    return loop_2_zone,adj_central_flow

def zone_hvac_flow(building,profile,Q_Tset):
    #flow for zones not on a HVAC loop (unit heaters)
    n_z = len(building['zones']['name'])
    direct_flow = [0 for i in range(n_z)]
    for i in building['unitary_sys']:
        f = building['unitary_sys'][i]['fan_name']
        z = building['unitary_sys'][i]['zone']
        if building['unitary_sys'][i]['type']=='UnitHeater':
            direct_flow[z] = building['fans'][f]['flow_rate']*profile[building['fans'][f]['schedule']]/building['zones']['multiplier'][z]
        elif building['unitary_sys'][i]['type']=='FourPipeFanCoil':
            direct_flow[z] = building['fans'][f]['flow_rate']*profile[building['fans'][f]['schedule']]/building['zones']['multiplier'][z]
        elif building['unitary_sys'][i]['type']== 'PackagedTerminalAirConditioner':
                ## need to find part-load-ratio (PLR) see page 1541
                ## later infer PLR from this flow
                if Q_Tset[1][z]>0: #heating
                    direct_flow[z] = building['unitary_sys'][i]['heating_air_flow']/building['zones']['multiplier'][z]
                elif Q_Tset[0][z]<0: #cooling
                    direct_flow[z] = building['unitary_sys'][i]['cooling_air_flow']/building['zones']['multiplier'][z]
                else:
                    direct_flow[z] = building['unitary_sys'][i]['no_load_air_flow']/building['zones']['multiplier'][z]
    return direct_flow

def loop_outdoor_air(building,profile,fresh_air_zone_req,central_flow,loop_flow,flow_imbalance):
    #fresh air specified by a AirLoop HVAC
    nl = len(building['hvac']['loop']['name'])
    n_z = len(building['zones']['name'])
    fresh_air_loop = [0 for i in range(nl)]
    for i in range(len(building['hvac']['outdoor_air']['name'])): #loop through outside_air controllers to get minimum
        fresh_air_loop[building['hvac']['outdoor_air']['loop'][i]] = building['hvac']['outdoor_air']['min_flow'][i]*profile[building['hvac']['outdoor_air']['min_air_schedule'][i]] 
    for l in range(nl):
        flow_imbal = sum([-flow_imbalance[i]*building['zones']['multiplier'][i] for i in range(n_z) if building['zones']['air_loop'][i]==l])
        fresh_air_loop[l] = max(fresh_air_loop[l],flow_imbal) #mass flow that must be made up by fresh air(kg/s)
    return fresh_air_loop

def direct_zone_outdoor_air(building,profile,Q_Tset,flow_imbalance,central_flow):
    #fresh air specified by ZoneHVAC units
    n_z = len(building['zones']['name'])
    direct_fresh_air = [0 for i in range(n_z)]
    for i in building['unitary_sys']:
        z = building['unitary_sys'][i]['zone']
        if building['unitary_sys'][i]['type']=='FourPipeFanCoil':
            if ('outdoor_air_schedule' in building['unitary_sys'][i] and building['unitary_sys'][i]['outdoor_air_schedule'] != None):
                direct_fresh_air[z] = building['unitary_sys'][i]['outdoor_air_flow']*profile[building['unitary_sys'][i]['outdoor_air_schedule']]/building['zones']['multiplier'][z]
            else:
                direct_fresh_air[z] = building['unitary_sys'][i]['outdoor_air_flow']/building['zones']['multiplier'][z]
        elif building['unitary_sys'][i]['type']=='PackagedTerminalAirConditioner':
                if Q_Tset[1][z]>0: #heating
                    direct_fresh_air[z] = building['unitary_sys'][i]['heating_outdoor_air_flow']*profile[building['unitary_sys'][i]['fan_schedule']]/building['zones']['multiplier'][z]
                elif Q_Tset[0][z]<0: #cooling
                    direct_fresh_air[z] = building['unitary_sys'][i]['cooling_outdoor_air_flow']*profile[building['unitary_sys'][i]['fan_schedule']]/building['zones']['multiplier'][z]
                else:
                    direct_fresh_air[z] = building['unitary_sys'][i]['no_load_outdoor_air_flow']*profile[building['unitary_sys'][i]['fan_schedule']]/building['zones']['multiplier'][z]
    d2 = [-(flow_imbalance[i] + central_flow[i]) for i in range(n_z)]
    direct_fresh_air = [max(direct_fresh_air[i],d2[i]) for i in range(n_z)]
    return direct_fresh_air


def plenum_return_flow(building,profile,central_flow,direct_flow,mixing,infiltration):
    ##exhaust fans
    n_z = len(building['zones']['name'])
    n_p = len(building['hvac']['plenum']['name'])
    exhaust_flow = [-sum([mixing[j][i] for j in range(n_z)]) for i in range(n_z)]#balanced exhaust flow (m^3/s)
    for i in building['fans']:
        if building['fans'][i]['exhaust']:
            exhaust_flow[building['fans'][i]['exhaust_zone']] += building['fans'][i]['flow_rate']*profile[building['fans'][i]['schedule']] #volumetric flow (m^3/s)   #See page 1601 of the reference manual
    hvac_supply = [central_flow[i] + direct_flow[i] for i in range(n_z)]
    for i in building['unitary_sys']:
        if 'terminal' in building['unitary_sys'][i]:
            z = building['unitary_sys'][i]['zone']
            hvac_supply[z] = direct_flow[z]

    return_flow = [hvac_supply[i] + sum(mixing[i]) - sum([mixing[j][i] for j in range(n_z)]) + infiltration[i] - exhaust_flow[i] for i in range(n_z)] #volumetric flows (m3/s)
    plenum_flow = [[0 for j in range(n_z)] for i in range(n_z)] #keep track of what zone plenum flow is from
    inflow = [0 for i in range(n_p)]
    for i in range(n_p):
        z=building['hvac']['plenum']['zone_index'][i]
        for j in building['hvac']['plenum']['in_zones'][i]:
            inflow[i] += return_flow[j]
            plenum_flow[z][j] =return_flow[j]
            return_flow[j] = 0
        return_flow[z] +=inflow[i]
    flow_exiting_zone = [hvac_supply[i] + sum(mixing[i]) + infiltration[i] + sum(plenum_flow[i])  for i in range(n_z)]#flow leaves through exhaust, mixing to another zone or plenum, or return air
    return flow_exiting_zone,return_flow,plenum_flow

def return_air_calc(building,gains,T,w,return_flow,direct_flow,direct_flow_fresh):
    #determine air returning to HVAC from zone, and agregate into loops
    air_density = 1.204 #kg/m^3  #standard air density (1.204 kg/m3) adjusted for the local barometric pressure (standard barometric pressure corrected for altitude, ASHRAE 1997 HOF pg. 6.1).
    n_z = len(T)
    #add sensible and latent heat from refrigeration equipment
    latent_H2O = [gains['hvac_latent'][i]/2264705  for i in range(n_z)]#convert J/s to kg/s of water
    air_H2O = [w[i]*return_flow[i]*air_density for i in range(n_z)]
    cp_zone = [1006 + 1860*w[i] for i in range(n_z)] #J/kg*K
    return_air = {}
    return_air['m_dot'] = [return_flow[i]*air_density + latent_H2O[i] for i in range(n_z)] #mass flow (kg/s)
    return_air['Tdb'] = [0 for i in range(n_z)]
    return_air['w'] = [0 for i in range(n_z)]
    for i in range(n_z):
        if return_air['m_dot'][i]>0:
            return_air['Tdb'][i] = T[i] + gains['hvac_sensible'][i]/(cp_zone[i]*return_air['m_dot'][i])
            return_air['w'][i] = (air_H2O[i] + latent_H2O[i])/return_air['m_dot'][i]
        else:
            return_air['Tdb'][i] = T[i] 
            return_air['w'][i] = w[i] 
    return_air['h'] =  psychometric(return_air,'h')

    central_return_air = {}
    central_return_air['Tdb'] = [j for j in return_air['Tdb']]
    central_return_air['w'] = [j for j in return_air['w']]
    central_return_air['h'] = [j for j in return_air['h']]
    central_return_air['m_dot'] = [max(0,return_air['m_dot'][i] - (direct_flow[i] - direct_flow_fresh[i])*air_density) for i in range(n_z)]

    direct_return_air = {}
    direct_return_air['Tdb'] = [j for j in return_air['Tdb']]
    direct_return_air['w'] = [j for j in return_air['w']]
    direct_return_air['h'] = [j for j in return_air['h']]
    direct_return_air['m_dot'] = [max(0,(direct_flow[i] - direct_flow_fresh[i])*air_density) for i in range(n_z)]

    #flow agregated into air loops for supply side
    loop_return_air = {}
    n_l = len(building['hvac']['loop']['name'])
    loop_return_air['m_dot'] = [0 for i in range(n_l)]
    loop_return_air['h'] = [0 for i in range(n_l)]
    loop_return_air['w'] = [0 for i in range(n_l)]
    for i in range(n_z):
        if building['zones']['air_loop'][i]!=None:
            loop_return_air['m_dot'][building['zones']['air_loop'][i]] += central_return_air['m_dot'][i]*building['zones']['multiplier'][i]    
            loop_return_air['h'][building['zones']['air_loop'][i]] += central_return_air['m_dot'][i]*central_return_air['h'][i]*building['zones']['multiplier'][i]
            loop_return_air['w'][building['zones']['air_loop'][i]] += central_return_air['m_dot'][i]*central_return_air['w'][i]*building['zones']['multiplier'][i]
    for i in range(n_l):
        if loop_return_air['m_dot'][i]>0:
            loop_return_air['h'][i] = loop_return_air['h'][i]/loop_return_air['m_dot'][i]
            loop_return_air['w'][i] = loop_return_air['w'][i]/loop_return_air['m_dot'][i]
        else: #avoid issues with zero or nearly zero flow
            onl = len([j for j in range(n_z) if building['zones']['air_loop'][j]==i])
            if onl>0:
                loop_return_air['h'][i] = sum([central_return_air['h'][j] for j in range(n_z) if building['zones']['air_loop'][j]==i])/onl
                loop_return_air['w'][i] = sum([central_return_air['w'][j] for j in range(n_z) if building['zones']['air_loop'][j]==i])/onl
    loop_return_air['Tdb'] =  psychometric(loop_return_air,'Tdb')
    return direct_return_air,loop_return_air

def mix_air(s1,s2):
    mixed_air = {}
    mixed_air['m_dot'] = s1['m_dot'] + s2['m_dot'] #mass flow (kg/s)
    if mixed_air['m_dot']==0:
        for k in s1:
            mixed_air[k] = s1[k]+0
    else:
        mixed_air['h'] = (s1['m_dot']*s1['h'] + s2['m_dot']*s2['h'])/mixed_air['m_dot']
        w_sat = psychometric({'h':mixed_air['h']},'w')
        mix_w = (s1['m_dot']*s1['w'] + s2['m_dot']*s2['w'])/mixed_air['m_dot']
        mixed_air['m_dot'] = mixed_air['m_dot']*(1 - max(0,mix_w-w_sat))
        mixed_air['w'] = min(w_sat,mix_w)
        mixed_air['Tdb'] = psychometric(mixed_air,'Tdb')
    return mixed_air

def loop_supply_setpoint(building,profile,air_nodes,fresh_air,fresh_air_loop,loop_return_air,loop_flow,cf,loop_2_zone,cp_zone,flow_exiting_zone,net_H2O_gain,T_set,w_set,Q_Tset,T_min,T_max,fan_avail,des_day):
    air_density = 1.204 #kg/m^3  #standard air density (1.204 kg/m3) adjusted for the local barometric pressure (standard barometric pressure corrected for altitude, ASHRAE 1997 HOF pg. 6.1).
    n_z = len(cf)
    loop_T_supply = [j for j in loop_return_air['Tdb']]
    loop_w_supply = [j for j in loop_return_air['w']]
    mixed_air_loop = {}
    for k in loop_return_air:
        mixed_air_loop[k] = [j for j in loop_return_air[k]]
    for i in range(len(fresh_air_loop)):
        term_i = [j for j ,x in enumerate(building['hvac']['terminals']['loop']) if x==i]
        z_i = [building['hvac']['terminals']['zone'][j]  for j in term_i]
        # cf = [central_flow[j]  for j in z_i]
        on_loop = [j for j ,x in enumerate(building['air_supply_equip']['loop']) if x == i]
        if sum([cf[j]  for j in z_i]) > 0:
            air={}
            air['Tdb'] = loop_return_air['Tdb'][i]+0
            air['w'] = loop_return_air['w'][i]+0
            air['h'] = loop_return_air['h'][i]+0
            air['m_dot'] = loop_return_air['m_dot'][i]+0
            for j in on_loop:
                if building['air_supply_equip']['type'][j][:4]=='fan:':
                    fan_name = building['air_supply_equip']['name'][j]
                elif building['air_supply_equip']['type'][j]=='airloophvac:unitaryheatcool':
                    fan_name = building['unitary_heat_cool'][building['air_supply_equip']['name'][j]]['fan_name']
            sched = False
            try:
                k = building['manager']['node'].index(building['air_supply_nodes']['name'][building['air_supply_equip']['outlet'][on_loop[-1]]])
                if building['manager']['type'][k]=='Scheduled':
                    sched = True
                    for j in on_loop:
                        out = building['air_supply_equip']['outlet'][j]
                        node = building['air_supply_nodes']['name'][out]
                        if building['air_supply_equip']['type'][j]=='airloophvac:outdoorairsystem':
                            mixed_air,fresh_air_loop[i] = economized_outdoor_air(building,fresh_air_loop[i],air,fresh_air,loop_flow[i],i,fan_avail,fan_name,des_day)
                            mixed_air_loop['Tdb'][i] = air['Tdb']+0
                            mixed_air_loop['w'][i] = air['w']+0
                            mixed_air_loop['h'][i] = air['h']+0
                            mixed_air_loop['m_dot'][i] = air['m_dot']+0
                            air_nodes['supply_T_set'][out] = mixed_air['Tdb']+0
                        else:
                            air_nodes['supply_T_set'][out] = manager_override(building,profile,node,profile[building['manager']['schedule'][k]],air,fresh_air,fan_avail)
            except ValueError:
                pass
            if not sched:
                _,_,Q_to_air = fan_calc(building['fans'][fan_name],air,fan_avail[fan_name])
                Q_f2zone = [0 for x in range(n_z)]
                for x in z_i:
                    Q_f2zone[x] = Q_to_air*loop_2_zone[x][i]/building['zones']['multiplier'][x] #fan heat to zone air supply
                air_nodes['supply_T_set'][building['air_supply_equip']['inlet'][on_loop[0]]] = air['Tdb']
                for j  in range(len(on_loop)):
                    ## making sure simulation of these components is in the order they are on the supply branch
                    for k in on_loop:
                        if building['air_supply_equip']['branch_order'][k] == j:
                            out = building['air_supply_equip']['outlet'][k]
                            inl = building['air_supply_equip']['inlet'][k]
                            ty = building['air_supply_equip']['type'][k]
                            break
                    
                    air_nodes['supply_T_set'][out] = air_nodes['supply_T_set'][inl]
                    node = building['air_supply_nodes']['name'][out]
                    if ty=='airloophvac:outdoorairsystem':
                        air,fresh_air_loop[i] = economized_outdoor_air(building,fresh_air_loop[i],air,fresh_air,loop_flow[i],i,fan_avail,fan_name,des_day)
                        air_nodes['supply_T_set'][out] = air['Tdb']+0
                        mixed_air_loop['Tdb'][i] = air['Tdb']+0
                        mixed_air_loop['w'][i] = air['w']+0
                        mixed_air_loop['h'][i] = air['h']+0
                        mixed_air_loop['m_dot'][i] = air['m_dot']+0
                    elif ty[:6]=='coil:h':
                        if any([(cf[x]*cp_zone[x]*(air['Tdb']-T_set['heat'][x])<(Q_Tset[1][x]-Q_f2zone[x]) and cf[x]>0) for x in z_i]): #HVAC in heating mode
                            air['Tdb'] = -1e4 #set arbitraily small so that it gets set to maximum of z_sup_T (may be smaller than initial air['Tdb'])
                            for x in z_i:
                                if cf[x]>0:
                                    z_sup_T = Q_Tset[1][x]/(cp_zone[x]*cf[x]) + T_set['heat'][x]
                                    air['Tdb'] = max(air['Tdb'],min(max(z_sup_T,T_min[x]),T_max[x]))
                            air['Tdb'] = min(air['Tdb'],building['hvac']['design']['Tsupply_h'][i]) #constrain supply temperature
                            air_nodes['supply_T_set'][out] = manager_override(building,profile,node,air['Tdb'],air,fresh_air,fan_avail)
                    elif ty[:4]=='coil' or ty[:3]=='dx:':
                        if any([(cf[x]*cp_zone[x]*(air['Tdb']-T_set['cool'][x])>(Q_Tset[0][x]-Q_f2zone[x]) and cf[x]>0) for x in z_i]): #HVAC in cooling mode
                            air['Tdb'] = 1e4 #set arbitraily large so that it gets set to minimum of z_sup_T (may be larger than initial air['Tdb'])
                            for x in z_i:
                                if cf[x]>0:
                                    z_sup_T = Q_Tset[0][x]/(cp_zone[x]*cf[x]) + T_set['cool'][x]
                                    air['Tdb'] = max(min(air['Tdb'],z_sup_T),building['hvac']['design']['Tsupply_c'][i]) #constrain supply temperature
                            air_nodes['supply_T_set'][out] = manager_override(building,profile,node,air['Tdb'],air,fresh_air,fan_avail)
                        if any([w_set['dehumidify'][x]<1 for x in z_i]):
                            w_target = psychometric({'Tdb':[T_set['cool'][x] for x in z_i],'RH':[w_set['dehumidify'][x]*100 for x in z_i]},'w')
                            w_supply = max(.001,sum([flow_exiting_zone[x]*w_target - net_H2O_gain[x] for x in z_i])/sum([cf[x]  for x in z_i])) # find supply humidity
                            air['w'] = w_supply+0
                            if mixed_air_loop['w'][i] > air['w']:
                                air['Tdb'] =  min(psychometric({'Tdb':[T_set['cool'][x] for x in z_i],'w':[w_supply]},'Tdp'))
                                air_nodes['supply_T_set'][out] = manager_override(building,profile,node,air['Tdb'],air,fresh_air,fan_avail)
                    elif ty[:4]=='fan:':
                        _,_,Q_to_air = fan_calc(building['fans'][fan_name],air,fan_avail[fan_name])
                        air['Tdb'] = air_nodes['supply_T_set'][inl] + Q_to_air/(air['m_dot']*sum([cp_zone[x] for x in z_i])/len(z_i)/air_density)
                        air_nodes['supply_T_set'][out] = air['Tdb']+0 #manager_override(building,profile,node,air['Tdb'],air,fresh_air,fan_avail)
                        Q_f2zone = [0 for i in range(n_z)] #zero out for any components downstream of fan
                    elif ty=='airloophvac:unitaryheatcool':
                        if any([(cf[x]*cp_zone[x]*(air['Tdb']-T_set['cool'][x])>(Q_Tset[0][x]-Q_f2zone[x]) and cf[x]>0) for x in z_i]): #HVAC in cooling mode
                            air['Tdb'] = 1e4 #set arbitraily large so that it gets set to minimum of z_sup_T (may be larger than initial air['Tdb'])
                            for x in z_i:
                                if cf[x]>0:
                                    z_sup_T = Q_Tset[0][x]/(cp_zone[x]*cf[x]) + T_set['cool'][x]
                                    air['Tdb'] = min(air['Tdb'],z_sup_T)
                        elif any([(cf[x]*cp_zone[x]*(air['Tdb']-T_set['heat'][x])<(Q_Tset[1][x]-Q_f2zone[x]) and cf[x]>0) for x in z_i]): #HVAC in heating mode
                            air['Tdb'] = -1e4 #set arbitraily small so that it gets set to maximum of z_sup_T (may be smaller than initial air['Tdb'])
                            for x in z_i:
                                if cf[x]>0:
                                    z_sup_T = Q_Tset[1][x]/(cp_zone[x]*cf[x]) + T_set['heat'][x]
                                    air['Tdb'] = max(air['Tdb'],min(max(z_sup_T,T_min[x]),T_max[x]))
                            air['Tdb'] = min(building['hvac'].design.Tsupply_h[i],air['Tdb'])
                        else:
                            air = fan_calc(building['fans'][fan_name],air,fan_avail[fan_name])
                        air_nodes['supply_T_set'][out] = manager_override(building,profile,building['air_supply_nodes'].name[inl],air['Tdb'],air,fresh_air,fan_avail)
                    elif ty=='humidifier:steam:electric':
                        if any([w_set['humidify'][x]>0 for x in z_i]):
                            ##need to figure out temperature when humidifying?
                            w_target = psychometric({'Tdb':[T_set['heat'][x] for x in z_i],'RH':[w_set['humidify'][x]*100 for x in z_i]},'w') #heating = maybe humidifying
                            w_supply = max(.001,sum([flow_exiting_zone[z_i[x]]*w_target[x] - net_H2O_gain[z_i[x]] for x in range(len(z_i))])/sum([cf[x]  for x in z_i])) # find supply humidity
                            if mixed_air_loop['w'][i]<w_supply:
                                air['w'] = max(w_supply)
                        air_nodes['supply_T_set'][out] = air['Tdb']+0
                    else:
                        print('something else on air loop?')
            loop_T_supply[i] = air_nodes['supply_T_set'][out]+0
            loop_w_supply[i] = air['w']+0
        else:
            for j in on_loop:
                out = building['air_supply_equip']['outlet'][j]
                air_nodes['supply_T_set'][out] = loop_return_air['Tdb'][i]+0
    return loop_T_supply,loop_w_supply,mixed_air_loop,air_nodes

def economized_outdoor_air(building,min_flow,air,fresh_air,loop_flow,l,fan_avail,fan_name,des_day):
    air_density = 1.204 #kg/m^3 %standard air density (1.204 kg/m3) adjusted for the local barometric pressure (standard barometric pressure corrected for altitude, ASHRAE 1997 HOF pg. 6.1).
    r_air = {}
    r_air['Tdb'] = air['Tdb']+0
    r_air['w'] = air['w']+0
    r_air['h'] = air['h']+0
    f_air = {}
    f_air['Tdb'] = fresh_air['Tdb']+0
    f_air['w'] = fresh_air['w']+0
    f_air['h'] = fresh_air['h']+0
    fresh_air_loop = min_flow+0
    T_supply_max = building['hvac']['design']['Tsupply_h'][l]
    Ta = f_air['Tdb']+0
    Tb = r_air['Tdb']+0
    ## run checks to see if economizer is active
    econ_on = False
    if econ_on and not des_day and T_supply_max>Ta and r_air['Tdb']>T_supply_max:
        error = 1
        max_flow = building['hvac']['outdoor_air']['max_flow'](l)
        while error>1e-3:
            f_air['m_dot'] = fresh_air_loop*air_density
            r_air['m_dot'] = (loop_flow - fresh_air_loop)*air_density
            mixed_air = mix_air(r_air,f_air)
            cp = (1006 + 1860*mixed_air['w']) #Specific heat in kJ/kg
            _,_,Q_to_air = fan_calc(building['fans'][fan_name],mixed_air,fan_avail[fan_name])
            T_no_treat = mixed_air['Tdb'] + Q_to_air/(mixed_air['m_dot']*cp)
            error = T_no_treat - T_supply_max
            if (error>0 and fresh_air_loop>=max_flow) or (error<0 and fresh_air_loop<=min_flow):
                error = 0
            d_flow = 0
            if (Ta-Tb)!=0:
                d_flow = loop_flow*(1-(Tb+20)/(error+20))/(Ta-Tb)*error
            fresh_air_loop = max(min_flow,min(max_flow,fresh_air_loop + d_flow))
    else:
        f_air['m_dot'] = fresh_air_loop*air_density
        r_air['m_dot'] = (loop_flow - fresh_air_loop)*air_density
        mixed_air = mix_air(r_air,f_air)
    return mixed_air,fresh_air_loop

def zones_supply_setpoint(building,T,w,central_flow,cp_zone,loop_T_supply,direct_return_air,T_set,Q_Tset,T_min,T_max,fresh_air,direct_fresh_air,direct_flow,fan_avail):
    air_density = 1.204 #kg/m^3 #standard air density (1.204 kg/m3) adjusted for the local barometric pressure (standard barometric pressure corrected for altitude, ASHRAE 1997 HOF pg. 6.1).
    n_z = len(building['zones']['name'])
    supply_flow = {}
    supply_flow['Tdb'] = [T['zone'][i] for i in range(n_z)]
    for z in range(n_z):
        if central_flow[z]>0:
            try:
                term_z = building['hvac']['terminals']['zone'].index(z)
                supply_flow['Tdb'][z] = loop_T_supply[building['hvac']['terminals']['loop'][term_z]]
                if building['hvac']['terminals']['type'][term_z] == 'SingleDuct:Uncontrolled':
                    pass
                    ##do nothing
                elif building['hvac']['terminals']['type'][term_z] == 'SingleDuct:ConstantVolume:Reheat':
                    ##need example
                    pass
                elif building['hvac']['terminals']['type'][term_z] == 'SingleDuct:VAV:Reheat':
                    if central_flow[z]*cp_zone[z]*(supply_flow['Tdb'][z]- T_set['heat'][z])<Q_Tset[1][z]: #needs heat
                        m = building['zones']['multiplier'][z]
                        Q_reheat_max = m*central_flow[z]*cp_zone[z]*(T_max[z] - supply_flow['Tdb'][z])
                        # Q_reheat_max = min(Q_reheat_max,building['coils_heating'][building['hvac']['terminals']['reheat_coil_name'][term_z]]['capacity']) #remove, sometimes coil exceeds rated maximum
                        Q_reheat_for_target = m*(Q_Tset[1][z] - central_flow[z]*cp_zone[z]*(supply_flow['Tdb'][z]- T_set['heat'][z]))
                        Q_terminal = max(0,min(Q_reheat_for_target,Q_reheat_max))
                        supply_flow['Tdb'][z] += Q_terminal/(central_flow[z]*m*cp_zone[z])
                else:
                    print('air terminal of type: '+ building['hvac']['terminals']['type'][term_z])
            except ValueError:
                #not on an air loop (no terminal) check unitary systems
                supply_flow['Tdb'][z]= direct_return_air['Tdb'][z]
    supply_flow['w'] = [j for j in w['zone']]
    for i in range(n_z):
        if building['zones']['air_loop'][i]!=None:
            supply_flow['w'][i] =w['loop'][building['zones']['air_loop'][i]]
    
    supply_flow['flow'] = [j for j in central_flow]
    supply_flow['m_dot'] = [central_flow[x]*air_density for x in range(len(central_flow))]
    supply_flow['h'] = psychometric(supply_flow,'h')
    T['central'] = [j for j in supply_flow['Tdb']]
    T['direct'] = [j for j in T['central']]
    w['central'] = [j for j in supply_flow['w']]
    w['direct'] = [j for j in w['central']]
    
    for i in building['unitary_sys']:
        z = building['unitary_sys'][i]['zone']
        fan_name = building['unitary_sys'][i]['fan_name']
        if direct_flow[z]>0:
            c_air = {}
            for x in supply_flow:
                c_air[x] = supply_flow[x][z]
            r_air = {}
            for x in direct_return_air:
                r_air[x] = direct_return_air[x][z]
            if 'terminal' in building['unitary_sys'][i]:
                r_air['m_dot'] = direct_flow[z]*air_density - c_air['m_dot']
                _,_,Q_to_air = fan_calc(building['fans'][fan_name],mixed_air,fan_avail[fan_name]) #unitary system fan is for all zones (divide by multiplier)
                mixed_air = mix_air(r_air,c_air)
                Q_direct = [Q_Tset[0][z],Q_Tset[1][z]]
            else:
                r_air['m_dot'] = (direct_flow[z] - direct_fresh_air[z])*air_density 
                Q_loop_air = supply_flow['flow'][z]*cp_zone[z]*(supply_flow['Tdb'][z] - T['zone_est'][z])
                f_air = {}
                for k in fresh_air:
                    f_air[k] = fresh_air[k]+0
                f_air['m_dot'] = direct_fresh_air[z]*air_density
                mixed_air = mix_air(r_air,f_air) #fresh air directly to zone, not outdoor air mixing on loop
                Q_direct = [Q_Tset[0][z]+Q_loop_air,Q_Tset[1][z]+Q_loop_air]
                _,_,Q_to_air = fan_calc(building['fans'][fan_name],mixed_air,fan_avail[fan_name]) #unitary system fan is for all zones (divide by multiplier)


            supply_flow['Tdb'][z] = mixed_air['Tdb'] + Q_to_air/(mixed_air['m_dot']*cp_zone[z]*building['zones']['multiplier'][z])
            supply_flow['w'][z] = mixed_air['w']
            supply_flow['m_dot'][z] = mixed_air['m_dot']
            supply_flow['h'][z] = mixed_air['h']
            flow = mixed_air['m_dot']/air_density

            if building['unitary_sys'][i]['type']=='PackagedTerminalAirConditioner' or building['unitary_sys'][i]['type']=='FourPipeFanCoil':
                if flow*cp_zone[z]*(supply_flow['Tdb'][z] - T_set['cool'][z])>Q_direct[0]: #unitary system in cooling mode
                    T_unit_cooler = min(max(Q_direct[0]/(cp_zone[z]*flow) + T_set['cool'][z],T_min[z]),T_max[z])
                    supply_flow['Tdb'][z] = min(supply_flow['Tdb'][z],T_unit_cooler)
                elif flow*cp_zone[z]*(supply_flow['Tdb'][z] - T_set['heat'][z])<Q_direct[1]: #unitary system  in heating mode
                    T_unit_heater = min(Q_direct[1]/(cp_zone[z]*flow) + T_set['heat'][z],T_max[z])
                    supply_flow['Tdb'][z] = max(supply_flow['Tdb'][z],T_unit_heater)
            elif building['unitary_sys'][i]['type']=='UnitHeater':
                if flow*cp_zone[z]*(supply_flow['Tdb'][z] - T_set['heat'][z])<Q_direct[1]: #unitary system  in heating mode
                    T_unit_heater = min(Q_direct[1]*(cp_zone[z]*flow) + T_set['heat'][z],T_max[z])
                    supply_flow['Tdb'][z] = max(supply_flow['Tdb'][z],T_unit_heater)
            elif building['unitary_sys'][i]['type']=='WindowAirConditioner':
                print('need WindowAirConditioner')
            else:
                print('need other types of unitary system')
            T['direct'][z] = supply_flow['Tdb'][z]
            w['direct'][z] = supply_flow['w'][z]
            if 'terminal' not in building['unitary_sys'][i]: #Mixing central air for net supply to zone
                d_air = {}
                d_air['Tdb'] = supply_flow['Tdb'][z]
                d_air['w'] = supply_flow['w'][z]
                d_air['m_dot'] = supply_flow['m_dot'][z]
                d_air['h'] = supply_flow['h'][z]
                mixed_air = mix_air(d_air,c_air)
                supply_flow['Tdb'][z] = mixed_air['Tdb'] 
                supply_flow['w'][z] = mixed_air['w']
                supply_flow['m_dot'][z] = mixed_air['m_dot']
                supply_flow['h'][z] = mixed_air['h']
            supply_flow['flow'] = [supply_flow['m_dot'][i]/air_density for i in range(n_z)]
    return supply_flow, T, w

def des_day_zone_flow(building,fresh_air_zone,cp_supply,Q_Tset,T_set,T_min,T_max,flow_imbalance):
    n_z = len(building['zones']['name'])
    zone_flow_req = [0 for i in range(len(n_z))]
    for i in range(n_z):
        if T_set['no_hvac'][i]:
            pass
        elif Q_Tset[1][i]>0:
            zone_flow_req[i] = max(Q_Tset[1][i]/(cp_supply[i]*(T_max[i] - T_set['heat'][i])),-flow_imbalance[i])
        elif Q_Tset[0][i]<0:
            zone_flow_req[i] =  max(Q_Tset[0][i]/(cp_supply[i]*(T_min[i] - T_set['cool'][i])),-flow_imbalance[i])
    zone_flow = [max(fresh_air_zone[i],zone_flow_req[i]) for i in range(n_z)]#volumetric flow m^3/s
    direct_flow = [0 for i in range(n_z)] #flow for zones not on a HVAC loop (unit heaters)
    for i in range(len(building['unitary_sys'])):
        try:
            l = building['hvac']['loop']['supply_outlet'].index(building['unitary_sys'][i]['outlet'])
            z = building['unitary_sys'][i]['zone']
            direct_flow[z] = zone_flow[z]
        except ValueError:
            pass
    central_flow = [zone_flow[i] - direct_flow[i] for i in range(n_z)]
    n_l = len(building['hvac']['loop']['name'])
    supply_flow = [0 for i in range(n_l)]
    fresh_air_loop= [0 for i in range(n_l)]
    for i in range(n_z):
        supply_flow[building['zones']['air_loop'][i]] += central_flow[i]*building['zones']['multiplier'][i] #mass flow for the loop (kg/s)
        fresh_air_loop[building['zones']['air_loop'][i]] += fresh_air_zone[i]
    loop_2_zone = []
    zone_request= [[0 for j in range(n_l)] for i in range(n_z)]
    loop_request = [0 for i in range(n_l)]
    for i in range(n_z):
        l=building['zones']['air_loop'][i]
        if l!=None:
            zone_request[i][l]= central_flow[i]*building['zones']['multiplier'][i]
            loop_request[l] += zone_request[i][l]
    for i in range(n_z):
        if loop_request[l]>0:
            loop_2_zone.append([zone_request[i][l]/loop_request[l] for l in range(n_l)])
        else:
            loop_2_zone.append([0  for l in range(n_l)])
    direct_fresh_air = [fresh_air_zone[i] - sum([fresh_air_loop[l]*loop_2_zone[i][l] for l in range(n_l)]) for i in range(n_z)]
    return central_flow,direct_flow,supply_flow,direct_fresh_air,fresh_air_loop