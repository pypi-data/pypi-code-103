
from building_plus.basic.psychometric import psychometric
from building_plus.basic.eval_curve import eval_curve
from building_plus.components.water_equipment import water_equipment
from building_plus.basic.window_solar_transmittance import window_solar_transmittance
from building_plus.basic.solar_calc import solar_calc

import numpy as np
import datetime 

def zone_loads(building,date,profile,weather,T_zone,m_v_zone,dt,frost):
    m_v_air = psychometric({'P':weather['pres_pa'],'Tdp':weather['t_dewp']},'w')
    n_z = len(building['zones']['name'])
    T_air = [weather['t_dryb']*building['ctf']['z_height'][i] -0.0065*building['ctf']['z_height'][i] for i in range(n_z)] #outdoor air temp next to each zone
    T_mains = water_mains(building['water_main_temperature'],date)
    
    ## Occupancy and latent heat from occupants
    loads = {}
    cat = ['convected','radiant','latent','visible','lost']
    for x in cat:
        loads[x] = [0 for i in range(n_z)]

    occupancy = [0 for i in range(n_z)]
    loads['occupancy'] = [0 for i in range(n_z)]
    loads['internal_gain'] = [0 for i in range(n_z)]
    for i in range(len(building['occupancy']['zone'])):
        z_i = building['occupancy']['zone'][i]
        sched_i = building['occupancy']['schedule'][i]
        new_occ = profile[sched_i]*building['occupancy']['nominal'][i]*building['zones']['floor_area'][z_i]
        occupancy[z_i] += new_occ
        try:
            metabolic_rate = profile[building['occupancy']['activity'][i]] # W/person
        except KeyError:
            metabolic_rate = 120  #120W/person
        sensible_heat = (6.461927 + 0.946892*metabolic_rate + .0000255737*metabolic_rate**2 + 7.139322*T_zone[z_i] -
            0.0627909*T_zone[z_i]*metabolic_rate + 0.0000589172*T_zone[z_i]*metabolic_rate**2 - 0.198550*T_zone[z_i]**2 + 
            0.000940018*T_zone[z_i]**2*metabolic_rate - 0.00000149532*T_zone[z_i]**2*metabolic_rate**2)

        loads['radiant'][z_i] += building['occupancy']['radiant'][i]*new_occ*sensible_heat  #radiant is a portion of the sensible heat
        loads['convected'][z_i] += building['occupancy']['convected'][i]*new_occ*sensible_heat
        loads['latent'][z_i] += new_occ*(metabolic_rate - sensible_heat)
        loads['occupancy'][z_i] += new_occ*metabolic_rate
    loads['internal_gain'] = [loads['internal_gain'][i] + loads['occupancy'][i] for i in range(n_z)]

    loads['multiplier'] = building['zones']['multiplier']
    loads['area'] = building['zones']['floor_area']

    ## Infiltration and Mixing
    infiltration = [0 for i in range(n_z)] #volumetric flows (m3/s)
    for j in range(len(building['infiltration']['nominal'])):
        infiltration[building['infiltration']['zone'][j]] = building['infiltration']['nominal'][j]*profile[building['infiltration']['schedule'][j]] #volumetric flows (m3/s)
    mixing = [[0 for i in range(n_z)] for j in range(n_z)] #volumetric flows (m3/s)
    for j in range(len(building['mixing']['nominal'])):
        if building['mixing']['type'][j]=='flow/person':
            mixing[building['mixing']['receiving_zone'][j]][building['mixing']['source_zone'][j]] = building['mixing']['nominal'][j]*occupancy[building['mixing']['source_zone'][j]]*profile[building['mixing']['schedule'][j]] #volumetric flows (m3/s)
        else:
            mixing[building['mixing']['receiving_zone'][j]][building['mixing']['source_zone'][j]] = building['mixing']['nominal'][j]*profile[building['mixing']['schedule'][j]]#volumetric flows (m3/s)
    
    ## Equipment and Lighting
    prop = ['lighting_internal','plug_load','gas_load']
    for j in prop:
        loads[j] = [0 for i in range(n_z)]
        for i in range(len(building[j]['name'])):
            z_i = building[j]['zone'][i]
            sched_i = building[j]['schedule'][i]
            loads[j][z_i] += profile[sched_i]*building[j]['nominal'][i]*building['zones']['floor_area'][z_i] 
            loads['internal_gain'][z_i] += loads[j][z_i]
            for c in cat:
                if c in building[j]:
                    loads[c][z_i] += loads[j][z_i]*building[j][c][i]
    ## Solar
    sunrise, sunset, azimuth, zenith = solar_calc(building['location']['longitude'][0],building['location']['latitude'][0],building['location']['timezone'][0],[date])
    vect_2_sun = [float(np.sin(np.radians(zenith[0]))*np.sin(np.radians(azimuth[0]))),
                  float(np.sin(np.radians(zenith[0]))*np.cos(np.radians(azimuth[0]))),
                  float(np.cos(np.radians(zenith[0])))]## normal vector pointed at sun from azimuth (compass heading of sun) and zenith (angle beween sun and normal to surface of earth)
    #solar gain per unit area of exterior        
    if (weather['dir_norm_irr']+weather['dif_horz_irr'])>0:
        ext_gain = []
        for i in range(len(building['surfaces']['exterior']['cos_phi'])):
            if building['surfaces']['exterior']['boundary'][i]=='ground':
                ext_gain.append(0)
            else:    
                F_s = 0.5*(1+building['surfaces']['exterior']['cos_phi'][i])
                F_g = 0.5*(1-building['surfaces']['exterior']['cos_phi'][i])
                ext_gain.append(weather['dif_horz_irr']*(building['surfaces']['exterior']['solar_absorptance'][i]*F_s) + building['site']['ground_reflect']*weather['dif_horz_irr']*(building['surfaces']['exterior']['solar_absorptance'][i]*F_g))
                cos_theta = vect_2_sun[0]*building['surfaces']['exterior']['normal'][i][0] + vect_2_sun[1]*building['surfaces']['exterior']['normal'][i][1] + vect_2_sun[2]*building['surfaces']['exterior']['normal'][i][2] #dot product of two vectors
                SF = 1 #shading factor, needs development, pg 211
                if cos_theta>0:
                    ext_gain[i] += weather['dir_norm_irr']*building['surfaces']['exterior']['solar_absorptance'][i]*SF*cos_theta #Absorbed direct normal radiation
    else:
        ext_gain = [0 for i in range(len(building['surfaces']['exterior']['cos_phi']))]  
    
    ## Windows
    visible = [loads['visible'][building['windows']['zone_index'][i]]/building['zones']['interior_area'][building['windows']['zone_index'][i]] for i in range(len(building['windows']['area']))]
    long_wave = [loads['radiant'][building['windows']['zone_index'][i]]/building['zones']['interior_area'][building['windows']['zone_index'][i]] for i in range(len(building['windows']['area']))]
    window_gain,S = window_solar_transmittance(building['windows'],building['surfaces'],vect_2_sun,weather['dir_norm_irr'],weather['dif_horz_irr'],visible,long_wave)
    ## Refrigeration
    loads['case'],ref_gain,frost = refrigerated_cases(building,profile,T_zone,m_v_zone,frost,dt)
    loads['rack'],rack_gain = compressor_racks(building,loads['case'],T_air[0],T_zone,m_v_air)

    ## Water Equipment
    water_gain, water_heat = water_equipment_gains(building,profile,T_zone,m_v_zone,T_mains,dt)

    ## Exterior loads
    frac_dark = astronomical_clock_controlled_exterior_lights(date,dt,sunrise,sunset)
    loads['exterior'] = {}
    loads['exterior']['lighting'] = 0
    loads['exterior']['equipment'] = 0
    for j in building['exterior']:
        prof = profile[building['exterior'][j]['schedule']]
        if building['exterior'][j]['type']=='lights':
            loads['exterior']['lighting'] += prof*building['exterior'][j]['nominal']*frac_dark
        else:
            loads['exterior']['equipment'] += prof*building['exterior'][j]['nominal']

    # group terms
    loads['latent'] = [loads['latent'][i] + water_gain['latent'][i] for i in range(n_z)]
    gains = {}
    gains['zone_sensible'] = [loads['convected'][i] + rack_gain['zone'][i] + ref_gain['zone_sensible'][i] + water_gain['sensible'][i] for i in range(n_z)]
    gains['zone_latent'] = [loads['latent'][i] + ref_gain['zone_latent'][i] for i in range(n_z)]
    gains['interior_surface'] = [(loads['radiant'][building['surfaces']['zone_index'][i]] + loads['visible'][building['surfaces']['zone_index'][i]])*building['surfaces']['area'][i]/building['zones']['interior_area'][building['surfaces']['zone_index'][i]] for i in range(len(building['surfaces']['area']))]
    gains['exterior_surface'] = ext_gain
    gains['hvac_sensible'] = [rack_gain['hvac'][i] + ref_gain['hvac_sensible'][i] for i in range(n_z)]
    gains['hvac_latent'] = ref_gain['hvac_latent']
    gains['window'] = window_gain
    gains['ref_rack_water_sensible'] = [rack_gain['zone'][i] + ref_gain['zone_sensible'][i] + water_gain['sensible'][i] for i in range(n_z)]
    gains['ref_rack_water_latent'] = [water_gain['latent'][i] + ref_gain['zone_latent'][i] for i in range(n_z)]

    return loads,gains,occupancy,mixing,infiltration,S,frost,T_mains,water_heat

def refrigerated_cases(building,profile,T_zone,m_v_zone,frost,dt):
    ##See page 1343 of the reference manual
    n_c = len(building['cases'])
    n_z = len(building['zones']['name'])
    loads = {}
    loads['electric'] = [0 for i in range(n_c)]
    loads['evap'] = [0 for i in range(n_c)]
    loads['case'] = []
    ref_gain = {}
    ref_gain['zone_sensible'] = [0 for i in range(n_z)] #cumulative sensible heat to all refrigerated cases from the building zone
    ref_gain['zone_latent'] = [0 for i in range(n_z)]
    ref_gain['hvac_sensible'] = [0 for i in range(n_z)] #cumulative sensible heat credits applied to HVAC
    ref_gain['hvac_latent'] = [0 for i in range(n_z)]
    j=-1
    for i in building['cases']:
        j+=1
        bc = building['cases'][i]
        loads['case'].append(i)
        z = building['zones']['name'].index(bc['zone'])
        RAF = bc['return_air_frac']
        sched_i = bc['schedule']
        if bc['defrost_type']=='none':
                P_fan = bc['fan_power_per_length']*bc['length']
        elif bc['defrost_type']=='electric':
                sched_def = profile[bc['defrost_schedule']] #fraction of time defrosting
                sched_drip = profile[bc['defrost_drip_down_schedule']]
                P_def = bc['defrost_power_per_length']*bc['length']*sched_def
                latent_ratio = 1
                new_frost = bc['capacity_per_length']*bc['length']*bc['runtime_fraction']*bc['latent_heat_ratio']*latent_ratio*dt*(1-sched_drip)/(335000 + 2498000)
                max_melt_frost = P_def*dt/335000
                frost[j],Q_def = frost_calc(frost[j],new_frost,P_def,max_melt_frost,dt)
                P_fan = bc['fan_power_per_length']*bc['length']*(1-sched_def)
        elif bc['defrost_type']=='offcycle':
            #       sched_drip = profile[bc['defrost_drip_down_schedule']]
                P_fan = bc['fan_power_per_length']*bc['length']
        elif bc['defrost_type']=='hotgas':
            pass
        elif bc['defrost_type']=='hotbrine':
            pass
        RH = psychometric({'Tdb':T_zone[z],'w':m_v_zone[z]},'RH')
        Tdp = psychometric({'Tdb':bc['temperature'],'w':m_v_zone[z]},'Tdp')

        P_lights = bc['standard_lighting_per_unit_length']*bc['length']*profile[bc['light_schedule']]
        if bc['anti_sweat_control']=='none':
            P_as = 0
        elif bc['anti_sweat_control']=='constant':
            P_as = bc['anti_sweat_heater_per_length']*bc['length']
        elif bc['anti_sweat_control']=='RelativeHumid' or bc['anti_sweat_control']=='linear':
            P_as = bc['anti_sweat_heater_per_length']*bc['length']*(1 - (bc['rated_ambient_RH'] - RH)/(bc['rated_ambient_RH'] - bc['humidity_at_zero_percent']))
        elif bc['anti_sweat_control']=='dewpoint':
            pass
        elif bc['anti_sweat_control']=='heatbalance' or bc['anti_sweat_control']=='HeatBalanceMethod':
            ### first find R_case at nominal conditions
            Tdp_rated = psychometric({'Tdb':bc['rated_ambient_T'],'RH':bc['rated_ambient_RH']},'Tdp')
            R_case = (Tdp_rated - bc['temperature'])/(bc['anti_sweat_heater_per_length']/bc['height'] - (Tdp_rated - bc['rated_ambient_T'])/0.3169)
            P_as = ((Tdp - T_zone[z])*bc['height']/0.3169 + (Tdp - bc['temperature'])/R_case)*bc['length']
        P_as = max(P_as,bc['minimum_anti_sweat_per_length']*bc['length'])
        Q_restock = profile[bc['restock_schedule']]*bc['length']
        try: 
            credit_frac = profile[bc['case_credit_fraction_schedule']]
        except:
            credit_frac = 1
        Q_sensible_credit_rated = (bc['capacity_per_length']*bc['length']*bc['runtime_fraction']*(1-bc['latent_heat_ratio']) - P_lights*bc['light_to_case'] - P_as*bc['anti_sweat_heat_to_case'] - P_fan)
        Q_sensible_credit = Q_sensible_credit_rated*((T_zone[z] - bc['temperature'])/(bc['rated_ambient_T'] - bc['temperature']))*credit_frac
        ref_gain_sensible = (P_lights*(1-bc['light_to_case']) + P_as*(1-bc['anti_sweat_heat_to_case']) - Q_sensible_credit)*profile[sched_i]
        loads['evap'][j] = (Q_sensible_credit + P_fan + P_lights*bc['light_to_case'] + P_as*bc['anti_sweat_heat_to_case'] + Q_restock + Q_def)*profile[sched_i]
        ## Latent loads
        if bc['latent_credit_curve_type']=='casetemperaturemethod':
            latent_ratio = 1 - (bc['rated_ambient_RH'] - RH)*eval_curve(building['curves'],bc['latent_credit_curve_name'],[bc['temperature']])
        elif bc['latent_credit_curve_type']=='relativehumiditymethod':
            latent_ratio = eval_curve(building['curves'],bc['latent_credit_curve_name'],[RH])
        elif bc['latent_credit_curve_type']=='dewpointmethod':
            latent_ratio = eval_curve(building['curves'],bc['latent_credit_curve_name'],[Tdp])
        else:
            print('check names of case latent credit curve')
        if latent_ratio>1:
            latent_ratio = 1
        elif latent_ratio<0:
            latent_ratio = 0
        ref_gain_latent = bc['capacity_per_length']*bc['length']*bc['latent_heat_ratio']*bc['runtime_fraction']*credit_frac*latent_ratio

        ##split into zone & hvac due to return_air fraction
        ref_gain['hvac_sensible'][z] += ref_gain_sensible*RAF
        ref_gain['zone_sensible'][z] += ref_gain_sensible*(1-RAF)
        ref_gain['hvac_latent'][z] += ref_gain_latent*RAF
        ref_gain['zone_latent'][z] += ref_gain_latent*(1-RAF)

        loads['electric'][j] = (P_fan + P_lights + P_as)*profile[sched_i]
        if bc['defrost_type']=='electric':
            loads['electric'][j] += P_def*profile[sched_i]
    return loads,ref_gain,frost

def compressor_racks(building,case_loads,T_air,T_zone,m_v_air):
    n_r = len(building['racks'])
    loads = {}
    loads['electric'] = [0 for i in range(n_r)]
    loads['water'] = [0 for i in range(n_r)]
    loads['evap'] = [0 for i in range(n_r)]
    Q_reclaim = [0 for i in range(n_r)]
    rack_gain = {}
    n_z=len(building['zones']['name'])
    rack_gain['zone'] = [0 for i in range(n_z)] 
    rack_gain['hvac'] = [0 for i in range(n_z)]
    j = -1
    for i in building['racks']:
        j +=1
        br = building['racks'][i]
        k = [case_loads['case'].index(br['cases'][x]) for x in range(len(br['cases']))]
        loads['evap'][j] = sum([case_loads['evap'][c] for c in k])
        if br['heat_reject_location']=='outdoors':
            z = -1
            if br['condensor_type']=='aircooled':
                T_eval = T_air
            else: # br['condensor_type']=='evapcooled':
                print ('error: non air cooled rack condensor' )
                # Twb = psychometric({'Tdb':T_air,'w':m_v_air},'Twb')
                # T_effective = Twb + (1-evap_condenser_effectiveness)*(T_air - Twb)
                # T_eval = T_effective
                T_eval = T_air
        else:
            z = building['zones']['name'].index(br['heat_reject_location'])
            T_eval = T_zone[z]

        COP = br['design_COP']*eval_curve(building['curves'],br['COP_curve'],[T_eval])
        if br['condensor_type']=='watercooled':
            fan_power = 0
            loads['water'][j] = loads['evap'][j]/COP
        else:
            try:
                fan_power = br['fan_power']*eval_curve(building['curves'],br['fan_power_temperature_curve'],[T_eval])
            except:
                fan_power = br['fan_power']

        if br['heat_reject_location']!='outdoors' or br['condensor_type']=='aircooled' or br['condensor_type']=='evapcooled':
            loads['electric'][j] = loads['evap'][j]/COP + fan_power

        if z>=0:
            rack_gain['zone'][z] = sum(case_loads['evap'][k]*(1-building['cases']['return_air_frac'][br['cases']]))/sum(case_loads['evap'][k])*(loads['evap'][j]/COP + fan_power)
            rack_gain['hvac'][z] = (loads['evap'][j]/COP + fan_power) - rack_gain['zone'][z]
        else:
            Q_reclaim[j] = 0.3*loads['evap'][j]*(1 + 1/COP) #possible to reclaim up to 30% waste heat
    return loads,rack_gain

def astronomical_clock_controlled_exterior_lights(date,dt,sunrise,sunset):
    shift = .04 #.125 % fraction of day exterior lights remain on after sunrise
    if date.hour<(sunrise*24+shift):
        frac_dark = 1
    elif date.hour-dt<=(sunrise*24+shift):
        frac_dark = 1-((sunrise*24+shift) - (date.hour-dt))/dt
    elif date.hour<(sunset*24-shift):
        frac_dark = 0
    elif (date.hour-dt)<(sunset*24-shift):
        frac_dark =((sunset*24-shift) - (date.hour-dt))/dt
    else:
        frac_dark = 1
    return frac_dark

def frost_calc(frost,new_frost,P_def,max_melt_frost,dt):
    frost = frost + new_frost
    Q_def = 0
    if P_def>0:
        if frost>max_melt_frost:
            frost = frost-max_melt_frost
        else:
            frost = 0
            Q_def = P_def - frost*335000/dt
    return frost,Q_def

def water_mains(main,date):
    julian_day = round((date - datetime.datetime(date.year,1,1)).seconds/(3600*24) +.5)
    T_out_avg = main['outdoor_average'][0]*9/5+32 #convert to F 
    T_max_diff = main['max_temp_difference'][0]*9/5 #convert to delta F
    ratio = 0.4 + 0.01*(T_out_avg-44)
    lag = 35 - 1.0*(T_out_avg-44)
    T_mains = float((T_out_avg+6) + ratio*(T_max_diff/2)*np.sin((0.986*(julian_day - 15 - lag) -90)*np.pi/180))
    T_mains = (T_mains-32)*5/9 #convert back to C
    return T_mains

def water_equipment_gains(building,profile,T_zone,m_v_zone,T_mains,dt):
    Cp_water = 4186 #J/kg*K
    den_water = 995 #kg/m^3
    n_z = len(building['zones']['name'])
    water_gain = {}
    water_gain['sensible'] = [0 for i in range(n_z)]
    water_gain['latent'] = [0 for i in range(n_z)]
    water_heat = 0
    for j in building['water_use']:
        z = building['zones']['name'].index(building['water_use'][j]['zone'])
        _,_,T_target,T_hot,T_cold = water_equipment(building['water_use'][j],profile,T_mains,None)
        ##find gain into zones
        
        m_mix = building['water_use'][j]['peak_flow']*profile[building['water_use'][j]['flow_schedule']]*den_water 
        m_hot = m_mix*(T_target- T_cold)/(T_hot - T_cold)
        Q_total = m_mix*Cp_water*(T_target - T_zone[z]) #Watts of energy relative to zone     
        e_num = building['plant_demand_equip']['name'].index(j)
        loop_connect = building['plant_demand_equip']['loop'][e_num]
        if building['plant_loop']['type'][loop_connect]!='Heating':
            water_heat += (m_hot*Cp_water*(T_hot - T_cold))*building['zones']['multiplier'][z] #only if not on a plant loop
        water_gain['latent'][z] = profile[building['water_use'][j]['latent_frac_schedule']]*Q_total
        water_gain['sensible'][z] = Q_total*profile[building['water_use'][j]['sensible_frac_schedule']] #energy added to zone (without zone multiplier)
    return water_gain, water_heat