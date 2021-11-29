from building_plus.basic.natural_convection import natural_convection
from building_plus.basic.exterior_convection import exterior_convection

from scipy.sparse import linalg
from scipy.sparse import spdiags

def solve_surface_temp(building,Ts_j0,B,T_surface,T_zone,T,wind_speed,leward,gains):
    
    sig = 5.67e-8 # W/m^2*K^4 Stephan-Boltzman const
    vf = building['zones']['view_factors']
    z_index = building['surfaces']['zone_index']
    is_absorb = building['ctf']['interior_absorb']
    n_sur = len(building['ctf']['sur_state1'])
    n_z = len(T_zone)
    n_ext = len(building['ctf']['sur_state2'])
    n_ss = len(B)

    T_win = T['windows_int']
    T_interior = [T_surface[building['ctf']['sur_state1'][i]] for i in range(n_sur)]
    dT = [T_interior[i] - T_zone[z_index[i]] for i in range(n_sur)]#interior surface convection = h*A*(Tsur - Tzone) 
    h_interior = natural_convection(building['surfaces']['normal'],dT,None,building['convection']['interior'])
    h_exterior,h_sky = exterior_convection(building,[T_surface[building['ctf']['sur_state2'][i]] for i in range(n_ext)],T['air_surface'],wind_speed,leward,T['sky'],building['convection']['exterior'])

    A_diag = [i for i in building['ctf']['A_diag']]
    A_diag[1] = [A_diag[1][i]+B[i] for i in range(n_ss)]
    
    b = [B[i]*Ts_j0[i] for i in range(n_ss)]    

    ## convective heat transfer with zone
    for i in range(n_sur):
        ss_i = building['ctf']['sur_state1'][i]
        z = building['surfaces']['zone_index'][i]
        A_diag[1][ss_i] += h_interior[i]
        b[ss_i] += h_interior[i]*T_zone[z]
    ## convective heat transfer with exterior, sky, and ground
    for i in range(n_ext):
        ss_i = building['ctf']['sur_state2'][i]
        A_diag[1][ss_i] += h_exterior[i] + h_sky[i]
        b[ss_i] += h_exterior[i]*T['exterior'][i] + h_sky[i]*T['sky']

    ## radiative heat transfer
    for z in range(n_z):
        z_s = len(building['zones']['surfaces'][z])
        z_w = len(building['zones']['windows'][z])
        for s in range(z_s):
            i = building['zones']['surfaces'][z][s]
            ss_i = building['ctf']['sur_state1'][i]
            for k in range(z_s):
                j = building['zones']['surfaces'][z][k]
                if k>s:
                    if T_interior[i] != T_interior[j]:
                        q_rad_i = sig*vf[i][j]*is_absorb[i]*((T_interior[i]+273)**4 - (T_interior[j]+273)**4)
                        h_rad_i = q_rad_i/(T_interior[i] - T_interior[j])
                        q_rad_j = sig*vf[j][i]*is_absorb[j]*((T_interior[j]+273)**4 - (T_interior[i]+273)**4)
                        h_rad_j = q_rad_j/(T_interior[j] - T_interior[i])
                    else:
                        h_rad_i = sig*vf[i][j]*is_absorb[i]*4*(T_interior[i]+273)**3 #avoid nan by using derivative
                        h_rad_j = sig*vf[j][i]*is_absorb[j]*4*(T_interior[j]+273)**3 #avoid nan by using derivative
                    A_diag[1][ss_i] += h_rad_i
                    b[ss_i] += h_rad_i*T_interior[j]

                    ss_j = building['ctf']['sur_state1'][j]
                    A_diag[1][ss_j] += h_rad_j
                    b[ss_j] += h_rad_j*T_interior[i]
            for w in range(z_w):
                j = building['zones']['windows'][z][w]
                if T_interior[i] != T_win[j]:
                    q_rad_win = sig*vf[i][j+n_sur]*is_absorb[i]*((T_interior[i]+273)**4 - (T_win[j]+273)**4)
                    h_rad_win = q_rad_win/(T_interior[i] - T_win[j])
                else:
                    h_rad_win = sig*vf[i][j+n_sur]*is_absorb[i]*4*(T_interior[i]+273)**3
                A_diag[1][ss_i] += h_rad_win
                b[ss_i] += h_rad_win*T_win[j]

    for i in range(n_sur):
        b[building['ctf']['interior_surface'][i]] += (gains['interior_surface'][i] + gains['window'][i])/building['surfaces']['area'][i]
    for i in range(n_ext):
        b[building['ctf']['exterior_surface'][i]] +=  gains['exterior_surface'][i]

    A = spdiags(A_diag,[-1,0,1],n_ss,n_ss)
    new_Ts = linalg.spsolve(A,b)
    new_Ts = [float(j) for j in new_Ts]
    max_e_s = max([abs(T_surface[j]-new_Ts[j]) for j in range(n_ss)])
    T_surface = [0.2*T_surface[j]+0.8*new_Ts[j] for j in range(n_ss)]
    dT = [T_interior[i] - T_zone[z_index[i]] for i in range(n_sur)]#interior surface convection = h*A*(Tsur - Tzone) 
    h_interior = natural_convection(building['surfaces']['normal'],dT,None,building['convection']['interior'])
    return new_Ts,h_interior,max_e_s