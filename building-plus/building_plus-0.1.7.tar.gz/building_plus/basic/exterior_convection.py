from building_plus.basic.natural_convection import natural_convection

def exterior_convection(building,T_exterior_sur,Tair,wind_speed,leward,T_sky,method):
    sig = 5.67e-8 # W/m^2*K^4 Stephan-Boltzman const
    exterior = building['surfaces']['exterior']
    n_ext = len(exterior['name'])
    F_grnd = [0.5*(1-exterior['cos_phi'][i]) for i in range(n_ext)]
    F_sky = [0.5*(1+exterior['cos_phi'][i]) for i in range(n_ext)]
    h_wind = [0 for i in range(n_ext)]
    beta = [F_sky[i]**.5 for i in range(n_ext)]
    h_n = natural_convection(exterior['normal'],[T_exterior_sur[i] - Tair[i] for i in range(n_ext)],None,method)
    
    h_ground = []
    h_air = []
    h_sky = []
    
    for i in range(n_ext):
        if exterior['boundary'][i] == 'ground':
            F_sky[i] = 0
            F_grnd[i] = 0
            h_wind[i] = 0
        else:
            if method=='DOE-2':
                if leward[i]:
                    h_wind[i] = h_n[i] + exterior['roughness_factor'][i]*((h_n[i]**2 + (3.55*wind_speed[i]**.617)**2)**.5-h_n[i])
                else:
                    h_wind[i] = h_n[i] + exterior['roughness_factor'][i]*((h_n[i]**2 + (3.26*wind_speed[i]**.89)**2)**.5-h_n[i])
            elif method=='Detailed' or method=='BLAST' or method=='TARP':
                if leward[i]:
                    h_wind[i] = h_n[i] + 2.537*.5*exterior['roughness_factor'][i]*(exterior['perimeter'][i]*wind_speed[i]/exterior['area'][i])**.5
                else:
                    h_wind[i] = h_n[i] + 2.537*exterior['roughness_factor'][i]*(exterior['perimeter'][i]*wind_speed[i]/exterior['area'][i])**.5    
        if exterior['boundary'][i] == 'ground':
            h_ground.append(building['ctf']['ground_cond'][i])
            h_air.append(0)
        elif T_exterior_sur[i]==Tair[i]:
            h_ground.extend(exterior['thermal_absorptance'][i]*sig*F_grnd[i]*4*(Tair[i])**3) #avoid nan by using derivative
            h_air.extend(exterior['thermal_absorptance'][i]*sig*F_sky[i]*(1-beta[i])*4*(Tair[i])**3) #avoid nan by using derivative
        else:    
            h_ground.append(exterior['thermal_absorptance'][i]*sig*F_grnd[i]*((T_exterior_sur[i]+273)**4 - (Tair[i]+273)**4)/(T_exterior_sur[i] - Tair[i]))
            h_air.append(exterior['thermal_absorptance'][i]*sig*F_sky[i]*(1-beta[i])*((T_exterior_sur[i]+273)**4 - (Tair[i]+273)**4)/(T_exterior_sur[i] - Tair[i]))
        if T_exterior_sur[i]==T_sky:
            h_sky.append(exterior['thermal_absorptance'][i]*sig*F_sky[i]*beta[i]*4*(T_sky)**3) #avoid nan by using derivative
        else:
            h_sky.append(exterior['thermal_absorptance'][i]*sig*F_sky[i]*beta[i]*((T_exterior_sur[i]+273)**4 - (T_sky+273)**4)/(T_exterior_sur[i] - T_sky))
    h_s = [h_wind[i] + h_air[i] + h_ground[i] for i in range(n_ext)]
    return h_s,h_sky