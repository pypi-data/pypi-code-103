'''
Analytic equation soln (eqn 2.11 in engineering reference) for zone temperature
Finite diference Implicit solution for surface temperatures
'''
from building_plus.basic.window_convection import window_convection
from building_plus.basic.solve_surface_temp import solve_surface_temp

def update_model_states_implicit(building,T,S,wind_speed,leward,gains,dt,w,mix,plenum,infiltration,supply_flow):
    e = 2.718281828459 #natural log to avoid importing numpy
    air_density = 1.204 #kg/m^3 #standard air density (1.204 kg/m3) adjusted for the local barometric pressure (standard barometric pressure corrected for altitude, ASHRAE 1997 HOF pg. 6.1).
    n_z = len(T['zone'])# number of zone states
    n_ss = len(T['surf'])# number of subsurfaces with temperature state
    n_sur = len(building['surfaces']['name'])# number of surfaces
    n_win = len(building['windows']['name'])# number of windows
    tol = building['site']['temp_tol']
    z_index = building['surfaces']['zone_index']
    s_area = building['surfaces']['area']

    cp_zone = [air_density*(1006 + 1860*w['zone'][i]) for i in range(n_z)] #J/m^3*K
    cp_window = [cp_zone[building['windows']['zone_index'][i]] for i in range(n_win)]
    c_t = building['zones']['volume']#sensible heat multiplier
    
    ##m*Cp & h*A*T terms for grouping all temperature and humidity states as (T.zonem_v_zone] for analytic solution  
    mass_balance = [sum(mix[i]) + sum(plenum[i]) + infiltration[i] + supply_flow['flow'][i]  for i in range(n_z)]
    den_w =[air_density*mass_balance[i] if mass_balance[i]>0 else air_density*v/dt for i, v in enumerate(building['zones']['volume'])]#adjustment for zones with zero air flow of any kind into them
    cap_z = [cp_zone[i]*c_t[i] for i in range(n_z)]
    cap_w = [air_density*building['zones']['volume'][i] for i in range(n_z)] #capacitance [zone_thermal,zone_moisture]
    m_cp_no_mix = [cp_zone[i]*(infiltration[i]*T['air_zone'][i] +  supply_flow['flow'][i]*supply_flow['Tdb'][i]) for i in range(n_z)]#flows in m^3/s converted to kg/s*J/(kg*K)*K = W 
    h2o_no_mix = [gains['zone_latent'][i]/2264705 + air_density*(infiltration[i]*w['air'] +  supply_flow['flow'][i]*supply_flow['w'][i]) for i in range(n_z)] #flows in m^3/s converted to kg/s, everything into kg/s of water 
    window_int_temp = [T['windows_int'][i]+273 for i in range(len(T['windows_int']))]

    #determine how small of time steps to take and scale implicit matrix by time constant
    sub_steps = 1
    tc = dt/sub_steps
    B = [building['ctf']['capacitance'][i]/building['ctf']['surf_area'][i]/tc for i in range(n_ss)]

    #Previous states
    Tz_j0 = [j for j in T['zone']]
    Ts_j0 = [j for j in T['surf']]
    mv_j0 = [j for j in w['zone']]
    #Loop through sub-steps 
    for ss in range(sub_steps): 
        if sub_steps>1:
            #initial guess for next step: interpolate from T.zone and T.zone_est from previous call to update_model_states, and add error in sub_steps
            g = (ss+1)/sub_steps
            if ss>0:
                errorTz = [Tz_j[i]-Tz_i[i] for i in range(n_z)]
                errorTs = [Ts_j[i]-Ts_i[i] for i in range(n_ss)]
                errorW = [mv_j[i]-mv_i[i] for i in range(n_z)]
            Tz_i = [(1-g)*T['zone'][j] + g*T['zone_est'][j] for j in range(n_z)]#zone temperature at next time step
            Ts_i = [(1-g)*T['surf'][j] + g*T['surf_est'][j] for j in range(n_ss)]
            mv_i = [(1-g)*w['zone'][j] + g*w['zone_est'][j] for j in range(n_z)]
            if ss>0:
                Tz_j = [Tz_i[j] + .5*errorTz[j] for j in range(n_z)]
                Ts_j = [Ts_i[j] + .5*errorTs[j] for j in range(n_ss)]
                mv_j = [mv_i[j] + .5*errorW[j]  for j in range(n_z)]
            else:
                Tz_j = [j for j in Tz_i]
                Ts_j = [j for j in Ts_i]
                mv_j = [j for j in mv_i]
        else:
            Tz_j = [j for j in T['zone_est']]
            Ts_j = [j for j in T['surf_est']]
            mv_j = [j for j in w['zone_est']]
        ## converge to a solution for the sub-step
        count = 0
        old_Tz = [j for j in Tz_j] #second value in outer iteration to track change in sign of error
        max_e = 10*tol
        while max_e>0.2*tol:
            ### Surface temperature portion
            Ts_j,h_interior,max_e_s = solve_surface_temp(building,Ts_j0,B,Ts_j,Tz_j,T,wind_speed,leward,gains)
            ###zone temperature portion
            window_zone_temp = [Tz_j[building['windows']['zone_index'][i]]+273 for i in range(n_win)] 
            h_windows = window_convection(building['windows'],window_int_temp,window_zone_temp,cp_window)
            h_A = [0 for i in range(n_z)]
            h_A_T = [0 for i in range(n_z)]
            for j in range(n_sur):
                h_A[z_index[j]] += h_interior[j]*s_area[j]
                h_A_T[z_index[j]] += h_interior[j]*s_area[j]*Ts_j[building['ctf']['sur_state1'][j]]
            for j in range(n_win):
                h_A[building['windows']['zone_index'][j]] += h_windows[j]*building['windows']['area'][j]
                h_A_T[building['windows']['zone_index'][j]] += h_windows[j]*building['windows']['area'][j]*T['windows_int'][j]

            den_z = [h_A[j] + cp_zone[j]*mass_balance[j] for j in range(n_z)] # convection + inter-zone mixing + infiltration + HVAC
            m_cp_T = [cp_zone[j]*sum([(mix[j][k]+plenum[j][k])*Tz_j[k] for k in range(n_z)]) + m_cp_no_mix[j] for j in range(n_z)]
            #Analytic equation soln (eqn 2.11 in engineering reference)
            term1_z = [gains['zone_sensible'][j] + h_A_T[j] + m_cp_T[j] for j in range(n_z)]# internal gains + convection*T.surface + inter-zone mixing*T.source + infiltration*T.air + HVAC*T.supply_zone   
            new_Tz = [(Tz_j0[j] - term1_z[j]/den_z[j])*e**(-den_z[j]/cap_z[j]*tc) + term1_z[j]/den_z[j] for j in range(n_z)]
            #determine error with last iteration
            max_e_z = max([abs(new_Tz[i] - Tz_j[i]) for i in range(n_z)])
            Tz_j  = [Tz_j[i] + .65*(new_Tz[i] - Tz_j[i]) if ((new_Tz[i] - Tz_j[i])<0 and old_Tz[i]<Tz_j[i]) or ((new_Tz[i] - Tz_j[i])>0 and old_Tz[i]>Tz_j[i]) else Tz_j[i] + 0.2*(new_Tz[i] - Tz_j[i]) for i in range(n_z)]
            old_Tz = [j for j in new_Tz]

            #worst error in zone or surface temperature
            max_e = max(max_e_s,max_e_z)
            count += 1

        #zone  humidity portion
        max_e_h = tol
        while max_e_h>1e-4:
            t1 = [air_density*sum([(mix[j][k]+plenum[j][k])*mv_j[k] for k in range(n_z)]) + h2o_no_mix[j] for j in range(n_z)]#flows in m^3/s converted to kg/s, everything into kg/s of water 
            mv_new = [(mv_j0[j] - t1[j]/den_w[j])*e**(-den_w[j]/cap_w[j]*tc) + t1[j]/den_w[j] for j in range(n_z)]
            max_e_h = max([abs(mv_j[j] - mv_new[j]) for j in range(n_z)])
            mv_j = mv_new#zone humidity at end of sub-step 
            
        if ss+1<sub_steps:
            #Previous states
            Tz_j0 = [j for j in Tz_j]
            Ts_j0 = [j for j in Ts_j]
            mv_j0 = [j for j in mv_j]

    # ## Test energy balance
    # T_interior = [Ts_j[i] for i in building['ctf']['sur_state1']]
    # window_zone_temp = [Tz_j[building['windows']['zone_index'][i]]+273 for i in range(n_win)] 
    # h_windows = window_convection(building['windows'],window_int_temp,window_zone_temp,cp_window)
    # Q_windows = [0 for i in range(len(building['zones']['name']))]
    # for i in range(n_win):
    #     Q_windows[building['windows']['zone_index'][i]] += h_windows[i]*building['windows']['area'][i]*(T['windows_int'][i] - Tz_j[building['windows']['zone_index'][i]]) #heat to zone 
    # Q_surfaces = [sum([h_interior[j]*(T_interior[j] - Tz_j[k])*building['surfaces']['area'][j] for j in range(n_sur) if building['surfaces']['zone_index'][j] ==k]) for k in range(n_z)] #estimated heat transfer to zone from walls/floor/ceiling 
    # Q_mixing = [cp_zone[i]*(sum([mix[i][j]*Tz_j[j] for j in range(n_z)]) - sum(mix[i])*Tz_j[i])for i in range(n_z)]  #heat into zone via mixing from another zone
    # Q_infiltration = [cp_zone[i]*infiltration[i]*(T['air_zone'][i] - Tz_j[i]) for i in range(n_z)] #heat into zone from air infiltration 
    # Q_supply = [cp_zone[i]*supply_flow['flow'][i]*(supply_flow['Tdb'][i] - Tz_j[i]) for i in range(n_z)] #heat into zone from treated air supply
    # Q_net = [(gains['zone_sensible'][j] + Q_windows[j] + Q_mixing[j] + Q_infiltration[j] + Q_supply[j] + Q_surfaces[j]) for j in range(n_z)]#Energy provided to the zone in W to achieve T_set.cool, + is heating
    # T_est = [T['zone'][j] + Q_net[j]*dt/(cp_zone[j]*building['zones']['volume'][j]) for j in range(n_z)]
    # error = [T_est[j] - Tz_j[j] for j in range(n_z)]
    # e_dict = dict(error = error,T_est = T_est, Q_net = Q_net, Q_supply = Q_supply, Q_infiltration = Q_infiltration, Q_mixing = Q_mixing, Q_surfaces = Q_surfaces, Q_windows = Q_windows)
    e_dict = dict()
    
    ##need fix so that when raining outside exterior surface temperature = T wet bulb (page 91 of manual)
    T_z = [j for j in Tz_j]
    T_s = [j for j in Ts_j]
    m_v = [j for j in mv_j]

    return T_z,T_s,m_v,e_dict