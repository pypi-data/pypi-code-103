from building_plus.basic.window_solar_transmittance import window_solar_transmittance
from building_plus.basic.solar_calc import solar_calc
from building_plus.basic.area_weighted_temperature import area_weighted_temperature
from building_plus.process.load_sched import load_sched
from building_plus.process.zone_loads import zone_loads

import numpy as np


def load_actual_building_data(buildings,observer,weather,forecast,date,res):
    n_b = len(buildings)
    if n_b>0:
        actual_data = {}
        for t in range(len(date)):
            weather_now = {}
            for i in weather:
                weather_now[i] = weather[i][t]
            internal_gain_scalar = building_variability(buildings)
            
            actual_data['loads'] = [{} for i in range(n_b)]
            actual_data['gains'] = [{} for i in range(n_b)]
            actual_data['S'] = [[] for i in range(n_b)]
            actual_data['water_heat'] = [[] for i in range(n_b)]
            actual_data['Tz_nominal'] = [[] for i in range(n_b)]
            actual_data['T_avg'] = [[] for i in range(n_b)]
            actual_data['E0'] = [forecast['E0'][0]]
            actual_data['H0'] = [forecast['H0'][0]]
            actual_data['C0'] = [forecast['C0'][0]]
            for i, bldg in enumerate(buildings):
                humidity = observer['building_humidity'][i]
                T_zone = observer['building_zone_temp'][i]
                frost = observer['building_frost'][i]
                schedules = load_sched(bldg['schedule'], bldg['holidays'], date, None, False)#can replace with modified schedules
                loads, gains, _, _, _, _, _, _, water_heat = zone_loads(bldg, date[0], schedules, weather_now, T_zone, humidity, res, frost)
                actual_gains = [internal_gain_scalar[i][j]*g for j,g in enumerate(loads['internal_gain'])]
                new_loads, new_gains,S = update_real_gains(bldg, weather_now, loads, gains, date[0], actual_gains)
                actual_data['loads'][i] = {}
                for k in new_loads:
                    if isinstance(new_loads[k],dict):
                        actual_data['loads'][i][k] = {}
                        for kk in new_loads[k]:
                            if isinstance(new_loads[k][kk],list):
                                actual_data['loads'][i][k][kk] = [j for j in new_loads[k][kk]]
                            else:
                                actual_data['loads'][i][k][kk] = new_loads[k][kk]+0
                    elif isinstance(new_loads[k],list):
                        actual_data['loads'][i][k] = [j for j in new_loads[k]]
                    else:
                        actual_data['loads'][i][k] = new_loads[k]+0
                actual_data['gains'][i] = {}
                for k in new_gains:
                    if isinstance(new_gains[k],list):
                        actual_data['gains'][i][k] = [j for j in new_gains[k]]
                    else:
                        actual_data['gains'][i][k] = new_gains[k]+0
                actual_data['S'][i] = [[j for j in w] for w in S]
                actual_data['water_heat'][i] = water_heat
                actual_data['Tz_nominal'][i] = [j for j in forecast['Tz_nominal'][i]]
                actual_data['T_avg'][i] = [area_weighted_temperature(bldg,actual_data['Tz_nominal'][i])]
    else:
        actual_data = None
    return actual_data


def building_variability(buildings):
    ##TODO replace with values or function to add variability to schedule
    scale = [[] for i in range(len(buildings))]
    for i, bldg in enumerate(buildings):
        scale[i] = [1 for z in range(len(bldg['zones']['name']))] 
    return scale


def update_real_gains(building,weather,loads,gains,date,new_internal_gain):
    '''
    pulls in actual weather and 'actual' internal gains to scale the original
    lighting, plug load and occupancy gains of each zone. The gains are then
    split to convected and latent for use in the building simulation
    '''
    new_loads = {}
    new_gains = {}
    ## Solar
    _,_, azimuth, zenith = solar_calc(building['location']['longitude'][0],building['location']['latitude'][0],building['location']['timezone'][0],[date])
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
    

    ## scale loads to actual internal gains
    nz = len(new_internal_gain)
    scale = []
    for i in range(nz):
        if loads['internal_gain'][i]>0:
            scale.append(new_internal_gain[i]/loads['internal_gain'][i])
        else:
            scale.append(0)
    
    new_loads['latent'] = [loads['latent'][i]*scale[i] for i in range(nz)]
    new_loads['convected'] = [loads['convected'][i]*scale[i] for i in range(nz)]
    new_loads['visible'] = [loads['visible'][i]*scale[i] for i in range(nz)]
    new_loads['radiant'] = [loads['radiant'][i]*scale[i] for i in range(nz)]
    new_loads['lighting_internal'] = [loads['lighting_internal'][i]*scale[i] for i in range(nz)]
    new_loads['plug_load'] = [loads['plug_load'][i]*scale[i] for i in range(nz)]
    new_loads['exterior'] = {}
    new_loads['exterior']['lighting'] = loads['exterior']['lighting']+0
    new_loads['exterior']['equipment'] =  loads['exterior']['equipment']+0
    new_loads['case'] = {}
    new_loads['case']['electric'] = [j for j in loads['case']['electric']]
    new_loads['rack'] = {}
    new_loads['rack']['electric'] = [j for j in loads['rack']['electric']]
    new_loads['multiplier'] = [j for j in loads['multiplier']]

    ## Windows
    visible = [loads['visible'][building['windows']['zone_index'][i]]/building['zones']['interior_area'][building['windows']['zone_index'][i]] for i in range(len(building['windows']['area']))]
    long_wave = [loads['radiant'][building['windows']['zone_index'][i]]/building['zones']['interior_area'][building['windows']['zone_index'][i]] for i in range(len(building['windows']['area']))]
    window_gain,S = window_solar_transmittance(building['windows'],building['surfaces'],vect_2_sun,weather['dir_norm_irr'],weather['dif_horz_irr'],visible,long_wave)

    new_gains['zone_sensible'] = [gains['zone_sensible'][i] - loads['convected'][i] + new_loads['convected'][i]  for i in range(nz)]
    new_gains['zone_latent'] = [gains['zone_latent'][i] - loads['latent'][i] + new_loads['latent'][i] for i in range(nz)]
    new_gains['interior_surface'] = [(new_loads['radiant'][building['surfaces']['zone_index'][i]] + new_loads['visible'][building['surfaces']['zone_index'][i]])*building['surfaces']['area'][i]/building['zones']['interior_area'][building['surfaces']['zone_index'][i]] for i in range(len(building['surfaces']['area']))]
    new_gains['exterior_surface'] = [j for j in ext_gain]
    new_gains['hvac_sensible'] = [j for j in gains['hvac_sensible']]
    new_gains['hvac_latent'] = [j for j in gains['hvac_latent']]
    new_gains['window'] = [j for j in window_gain]
    new_gains['ref_rack_water_sensible'] = [j for j in gains['ref_rack_water_sensible']]
    new_gains['ref_rack_water_latent'] = [j for j in gains['ref_rack_water_latent']]
    return new_loads,new_gains,S