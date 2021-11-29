'''
Calculates the surface temperature of each window pane 
all temperatures in Kelvin for this function
T is a matrix where each row holds the temperature states for a single window. 
The first column is the inside surface of the innermost pane, second column is outside of first pane, third is inside of 2nd pane...
'''
from building_plus.basic.natural_convection import natural_convection
from building_plus.basic.window_convection import window_convection

import numpy as np

def window_temperature(building,wind_speed,leward,S,T,T_int,T_sky,T_i,T_o,T_s,cp):
    sig = 5.67e-8 # W/m^2*K^4 Stephan-Boltzman const
    windows = building['windows']
    n_sur = len(building['surfaces']['name'])
    n_win = len(windows['type'])
    T_new = [[0,0,0,0] for i in range(n_win)]
    k_air = [26.3e-3*windows['gap_thickness'][i] for i in range(n_win)]

    Z = [sig*windows['emittance'][i][1]*windows['emittance'][i][2]/(1-(1-windows['emittance'][i][1])*(1-windows['emittance'][i][2])) for i in range(n_win)]
    F_sky = [0.5*(1+windows['cos_phi'][i]) for i in range(n_win)]
    Eo = [sig*((0.5*(1-windows['cos_phi'][i]))*T_o[i]**4 + F_sky[i]**1.5*T_sky**4 + F_sky[i]*(1-F_sky[i]**.5)*T_o[i]**4) for i in range(n_win)]
    Ei_s = [sig*sum([building['zones']['view_factors'][i][j+n_sur]*building['surfaces']['area_rad'][i]*(T_s[i])**4 for i in range(n_sur)])/building['windows']['area'][j] for j in range(n_win)] #internal radiation from other surfaces to window
    vf_w = [[building['zones']['view_factors'][i+n_sur][j+n_sur] for j in range(n_win)] for i in range(n_win)] #window 2 window view factors
    error = 1
    count = 0
    r = .4
    while error>0.1*building['site']['temp_tol'] and count<10:
        h_n_ext = natural_convection(windows['normal'], [T[i][0] - T_o[i] for i in range(n_win)],None,building['convection']['exterior'])
        h_o = [0 for i in range(n_win)]
        if building['convection']['exterior'] =='DOE-2':
            for i in range(n_win):
                if leward[i]:
                    h_o[i] = (h_n_ext[i]**2 + (3.55*wind_speed[i]**.617)**2)**.5
                else:
                    h_o[i] = (h_n_ext[i]**2 + ((3.26*wind_speed[i])**(.89))**2)**.5 
        elif building['convection']['exterior'] == 'Detailed' or building['convection']['exterior'] == 'BLAST' or building['convection']['exterior'] == 'TARP':
           for i in range(n_win):
                if leward[i]:
                    h_o[i] = h_n_ext[i] + 2.537*.5*(windows['perimeter'][i]*wind_speed[i]/windows['area'][i])**.5
                else:
                    h_o[i] = h_n_ext[i] + 2.537*(windows['perimeter'][i]*wind_speed[i]/windows['area'][i])**.5
        h_i = window_convection(windows,T_int,T_i,cp)
        error = 0
        for i in range(n_win):
            Ei = Ei_s[i]+ sig*(sum([vf_w[i][j]*T_int[j]**4 for j in range(n_win)]))
            if windows['type'][i]=='SimpleGlazingSystem':
                k = windows['thermal_conductivity'][i]/windows['thickness'][i]
                h_r = [windows['emittance'][i][j]*sig*T[i][j]**3 for j in range(2)]
                e = windows['emittance'][i][0:2]
                A = np.array([[-h_r[0]-k-h_o[i],       k           ],
                              [      k         ,   -h_r[1]-k-h_i[i]]])
                B = np.array([-e[0]*Eo[i] - h_o[i]*T_o[i] - S[0][i],
                    -e[1]*Ei - h_i[i]*T_i[i] - S[1][i]])
                ans = np.linalg.solve(A,B)
            elif windows['type'][i]=='Glazing':
                k = [windows['thermal_conductivity'][i][j]/windows['thickness'][i][j] for j in range(len(windows['thermal_conductivity'][i]))]
                h_r = [windows['emittance'][i][j]*sig*T[i][j]**3 for j in range(4)]
                e = [windows['emittance'][i][0],windows['emittance'][i][3]]
                h_r[1] = Z[i]*T[i][1]**3
                h_r[2] = Z[i]*T[i][2]**3
                h1 = k_air[i]
                A = np.array([[-h_r[0]-k[0]-h_o[i],       k[0]       ,        0       ,      0             ],
                                [   k[0]            ,   -h_r[1]-k[0]-h1,      h1+h_r[2] ,      0             ],
                                [       0           ,       h1+h_r[1]  , -h1-k[1]-h_r[2],     k[1]           ],
                                [        0          ,         0        ,       k[1]     , -h_r[3]-k[1]-h_i[i]]]) 
                B = np.array([-e[0]*Eo[i] - h_o[i]*T_o[i] - S[0][i],
                                -S[1][i],
                                -S[2][i],
                    -e[1]*Ei - h_i[i]*T_i[i] - S[3][i]])
                ans = np.linalg.solve(A,B)
            T_new[i] = [float(ans[j]) for j in range(len(ans))]
            error = float(max(error,np.amax([abs(T_new[i][j] - T[i][j]) for j in range(len(T_new[i]))])))
       
        for i in range(n_win):
            T[i] = [(1-r)*T_new[i][j] + r*T[i][j] for j in range(len(T_new[i]))]
            if windows['type'][i] =='SimpleGlazingSystem':
                T_int[i] = T[i][1]
            else:
                T_int[i] = T[i][3]
        count +=1
    Q_windows = [0 for i in range(len(building['zones']['name']))]
    for i in range(n_win):
        Q_windows[windows['zone_index'][i]] += h_i[i]*windows['area'][i]*(T_int[i] - T_i[i])
    T_windows_int = [T_int[i] - 273 for i in range(n_win)] #convert back to Celcius
    return T,T_windows_int,Q_windows,h_i