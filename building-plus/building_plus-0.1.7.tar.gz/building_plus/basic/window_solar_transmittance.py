def window_solar_transmittance(windows,surfaces,vect_2_sun,norm_irrad,horz_irrad,visible,long_wave):
    # outputs:
    # S is energy hitting surface of windows, 
    n_win = len(windows['name'])
    window_gain = [0 for i in range(len(surfaces['name']))]
    S = [[0 for i in range(n_win)] for j in range(4)]

    cos_phi_sun = [max(0,sum([vect_2_sun[j]*windows['normal'][i][j] for j in range(3)])) for i in range(n_win)]    
    ## transmit/reflect for glazing and simple glazing 
    transmit_angle_mod = [windows['transmittance'][i][0]*cos_phi_sun[i]**4 + windows['transmittance'][i][1]*cos_phi_sun[i]**3 + windows['transmittance'][i][2]*cos_phi_sun[i]**2 + windows['transmittance'][i][3]*cos_phi_sun[i] + windows['transmittance'][i][4] for i in range(n_win)]    
    reflect_angle_mod = [windows['reflectance'][i][0]*cos_phi_sun[i]**4 + windows['reflectance'][i][1]*cos_phi_sun[i]**3 + windows['reflectance'][i][2]*cos_phi_sun[i]**2 + windows['reflectance'][i][3]*cos_phi_sun[i] + windows['reflectance'][i][4] for i in range(n_win)]    
    reflect = []
    transmit = []
    visible_absorptance = []
    for i in range(n_win):
        transmit.append([windows['normal_transmittance'][i][0]*transmit_angle_mod[i],
                         windows['normal_transmittance'][i][0]*transmit_angle_mod[i],
                         windows['normal_transmittance'][i][1]*transmit_angle_mod[i],
                         windows['normal_transmittance'][i][1]*transmit_angle_mod[i]])
        reflect.append([windows['normal_reflectance'][i][j]*reflect_angle_mod[i] for j in range(4)])
        visible_absorptance.append([max(0,1 - transmit[i][j] - reflect[i][j]) for j in range(4)])##solve equation on page 290 for absorptance, for single layer it is what is not transmitted or reflected
    diffuse_absorptance = [[visible_absorptance[i][j] for j in range(4)] for i in range(n_win)] #cant find any mention describing how to get this paramater for simple window model

    for i in range(n_win):
        if windows['type'][i]=='SimpleGlazingSystem':
                S[0][i] = .5*(norm_irrad*cos_phi_sun[i]*visible_absorptance[i][0] + horz_irrad*diffuse_absorptance[i][0] + visible[i]*(1 - windows['normal_transmittance'][i][0] - windows['normal_reflectance'][i][0]))
                S[1][i] = S[0][i] + windows['emittance'][i][1]*long_wave[i] #add interior radiation to inside of 1st pane for simpleglazing
        else:
                S[0][i] = .5*(norm_irrad*cos_phi_sun[i]*visible_absorptance[i][0] + horz_irrad*diffuse_absorptance[i][0] + visible[i]*windows['normal_transmittance'][i][1]*(1 - windows['normal_transmittance'][i][0] - windows['normal_reflectance'][i][0]))
                S[1][i] = S[0][i]
                S[2][i] = .5*(norm_irrad*cos_phi_sun[i]*transmit[i][0]*visible_absorptance[i][2] + horz_irrad*windows['normal_transmittance'][i][0]*diffuse_absorptance[i][2] + visible[i]*(1 - windows['normal_transmittance'][i][1] + windows['normal_reflectance'][i][3]))
                S[3][i] = S[2][i] + windows['emittance'][i][1]*long_wave[i] #add interior radiation to inside of 1st pane for simpleglazing
        
        #solar distribution (page 212 of reference) 
    if norm_irrad>0 or horz_irrad>0:
        T_incident = []
        for i in range(n_win):
            if windows['type'][i]=='Glazing':
                T_incident.append(transmit[i][0]*transmit[i][2]/(1-reflect[i][2]*reflect[i][1]))
            else:
                T_incident.append(transmit[i][0]) #net transmittance factor for direct sunlight    

        for i in range(n_win):
            z = windows['zone_index'][i]
            surf = [x for x in range(len(surfaces['name'])) if surfaces['zone_index'][x]==z and surfaces['type'][x]!='InternalMass'] #no solar gain onto interior furnishings
            z_surf_area = sum([surfaces['area'][j] for j in surf])
            f = [x for x in surf if  surfaces['surf_type'][x] == 'floor']
            tot_area = sum([surfaces['area'][x] for x in f]) 
            f_absorb = [surfaces['absorptance_visible'][x][0]*surfaces['area'][x]/tot_area for x in f] #for things like corridors with multiple 'floor' surfaces
            normal2zone = norm_irrad*cos_phi_sun[i]*T_incident[i]*windows['area'][i]
            horizontal_irrad = horz_irrad*windows['normal_transmittance'][i][0]*windows['area'][i] + normal2zone*(1-sum(f_absorb))
            for j in range(len(f)):
                window_gain[f[j]] += normal2zone*f_absorb[j]
            for j in surf:
                window_gain[j] += horizontal_irrad*surfaces['area'][j]/z_surf_area #distribute diffuse sunlight to surfaces in zone

    return window_gain,S    