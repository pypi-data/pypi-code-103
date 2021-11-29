'''

'''
from building_plus.basic.psychometric import psychometric
from building_plus.basic.two_way_interp import two_way_interp

from scipy.special import j0 as besseli0
from scipy.special import j1 as besseli1
from scipy.special import kn as besselk

import numpy as np

def detailed_water_coil(coil,air_in,sensible_load,Tw_in,T_supply):
    air_out = {}
    for k in air_in:
        air_out[k] = air_in[k]+0
    if air_in['m_dot']>0 and sensible_load>0:
        den_water = 995 #kg/m^3
        pi = 3.14159
        Cp_air = 1006 + 1860*air_in['w'] #J/kg*K
        m_w_rated = coil['rated_water_flow']*den_water #convert m^3/s to kg/s
        h1 = psychometric({'Twb':Tw_in},'h')
        h2 = psychometric({'Twb':Tw_in+1},'h')
        bb = h2-h1
        aa = h1 - bb*Tw_in
        Pr = 0.733
        viscosity = 1.846e-5
        tube_thickness = (coil['tube_od']-coil['tube_id'])/2
        pipe_area = coil['tubes_per_row']*pi*(coil['tube_id']**2)/4
        surface_area = coil['tube_area_outside'] + coil['fin_area'] #total_coil_outside_area
        fin_height = (coil['fin_diameter']-coil['tube_od'])/2
        fin_effective_diam = (4*coil['fin_diameter']*coil['coil_depth']/(pi*coil['tube_rows']*coil['tubes_per_row']))**.5
        FA2SA = coil['fin_area']/surface_area #% Ratio of secondary (fin) to total (secondary plus primary) surface areas
        ma_scaled = (1+air_in['w'])*air_in['m_dot']/coil['min_airflow_area']
        coil_id_effective = 4*coil['min_airflow_area']*coil['coil_depth']/surface_area
        Re_a = coil_id_effective*ma_scaled/viscosity #Re_a should be between 400 and 1500
        tube_to_fin = coil['tube_od']/fin_effective_diam
        fin_diam_var = 0.5*(fin_effective_diam - coil['tube_od'])
        C1 = 0.159*(coil['fin_thickness']/coil_id_effective)**(-0.065)*(coil['fin_thickness']/fin_diam_var)**0.141
        C2 = -0.323*(coil['fin_spacing']/fin_diam_var)**0.049*(fin_effective_diam/coil['tube_spacing'])**0.549*(coil['fin_thickness']/coil['fin_spacing'])**(-0.028)

        f_o = C1*Re_a**C2*ma_scaled*Cp_air*Pr**(-2/3)
        f_o_w = f_o*(1.425 - 5.1e-4*Re_a + 2.63e-7*Re_a**2)
        
        n_o = surface_efficiency(f_o,tube_to_fin,coil['tube_od'],FA2SA,fin_effective_diam,coil['fin_conductivity'],coil['fin_thickness'])
        n_o_w = surface_efficiency(f_o_w,tube_to_fin,coil['tube_od'],FA2SA,fin_effective_diam,coil['fin_conductivity'],coil['fin_thickness'])
        
        R_o = 1/(f_o*n_o*surface_area)
        R_o_w = Cp_air/bb/(f_o_w*n_o_w*surface_area)
        R_mf = tube_thickness/(coil['tube_conductivity']*coil['tube_area_inside']) # + 5e-2/coil.tube_area_inside(k) #fouling factor from page 800 is 5e-2 m^2*K/W
        ## line search mass flow of water to get to desired outlet temperature
        n = 10
        Cp_water = 4186 #J/kg*K
        Tout = [0 for i in range(n)]
        Tw_out = max(coil['water_outlet_temperature'],Tw_in + 1)
        m_w_nom = max(1e-8*m_w_rated,sensible_load/(Cp_water*(Tw_out - Tw_in)))
        m_w_test = np.logspace(np.log10(.12*m_w_nom),np.log10(m_w_rated),n)
        mw_test = [float(x) for x in m_w_test]
        for i in range(n):
            Tout[i],_ = detailed_coil_heat_transfer(m_w_test[i],air_in,Tw_in,pipe_area,coil['tube_area_inside'],coil['tube_id'],aa,bb,R_mf,R_o,R_o_w)
        if Tout[-1]>T_supply:
            m_w = m_w_rated
        elif Tout[0]<T_supply:
            m_w = m_w_test[0]
        else:
            m_w = two_way_interp(T_supply,Tout,m_w_test)
        air_out['Tdb'],air_out['w'] = detailed_coil_heat_transfer(m_w,air_in,Tw_in,pipe_area,coil['tube_area_inside'],coil['tube_id'],aa,bb,R_mf,R_o,R_o_w)
        air_out['h'] = psychometric(air_out,'h')
        T_water_out = Tw_in + (-air_out['m_dot']*(air_out['h'] - air_in['h']))/(Cp_water*m_w)
    actual_load = -air_out['m_dot']*(air_out['h'] - air_in['h']) #heat added in W
    return air_out,m_w,actual_load


def surface_efficiency(f_o,rho,tube_od,FA2SA,fin_diameter,fin_conductivity,fin_thickness):
    fai = (fin_diameter - tube_od)/2*(2*f_o/(fin_conductivity*fin_thickness))**.5
    u_e = fai/(1-rho)
    u_b = u_e*rho
    n_fin = -2*rho/(fai*(1+rho))*(besseli1(u_b)*besselk(1,u_e) - besselk(1,u_b)*besseli1(u_e))/(besseli0(u_b)*besselk(1,u_e) - besselk(0,u_b)*besseli1(u_e))
    n_o = 1 - (1 - n_fin)*FA2SA
    return n_o

def detailed_coil_heat_transfer(m_w,air_in,Tw_in,pipe_area,area_inside,tube_id,aa,bb,R_mf,R_o,R_o_w):
    den_water = 995 #kg/m^3
    Cp_water = 4186 #J/kg*K
    Cp_air = 1006 + 1860*air_in['w'] #J/kg*K

    V_w = m_w/den_water/pipe_area #velocity in m/s
    water_tube_thermresist =(tube_id)**0.2/(area_inside*1.429*(V_w**0.8)) # 
    f_i = (1+0.0146*(Tw_in+273))/water_tube_thermresist
    R_i = 1/(f_i*area_inside)
    UA_dry = (1/(R_i + R_mf + R_o))
    ## compute exit temperature with all dry
    X = 1/(air_in['m_dot']*Cp_air)
    Y = -1/(m_w*Cp_water)
    Z_d = float(np.exp(UA_dry*(X + Y)))
    K1 = (Z_d-1)/(Z_d +Y/X)
    # K1 = X*(Z-1)/(X*Z+Y)
    # K2 = (X+Y)*Z/(X*Z+Y)
    Tw_2 = Tw_in
    Ta_2 = air_in['Tdb'] - K1*(air_in['Tdb'] - Tw_2)
    ## Check if exit dewpoint temperature is less than surface temperature
    Tdp = psychometric(air_in,'Tdp')
    T_s_2 = Tw_2 + ((1/UA_dry)-R_o)/(1/UA_dry)*(Ta_2 - Tw_2)
    if Tdp<T_s_2:
        ## completely dry coil
        Ta_out = Ta_2
        w_out = air_in['w']
    else:
        ## not completely dry, line search to find portion wet
        X2 = 1/air_in['m_dot']
        Y2 = -bb/(m_w*Cp_water)
        x_test = np.logspace(-2,0,25)
        x_test = [float(x) for x in x_test]
        T_s_2 = [0 for i in range(len(x_test)+1)]
        T_s_2[0],_,_ = wet_coil_calc(1e-4,aa,bb,R_i,R_mf,R_o,R_o_w,UA_dry,X,Y,X2,Y2,air_in,Tw_in)
        for i in range(len(x_test)):
            T_s_2[i+1],_,_ = wet_coil_calc(x_test[i],aa,bb,R_i,R_mf,R_o,R_o_w,UA_dry,X,Y,X2,Y2,air_in,Tw_in)
        x = two_way_interp(Tdp,T_s_2,[1e-4]+x_test)
        _,Ta_2,Tw_2 = wet_coil_calc(x,aa,bb,R_i,R_mf,R_o,R_o_w,UA_dry,X,Y,X2,Y2,air_in,Tw_in)

        Q_w = m_w*Cp_water*(Tw_2 - Tw_in)
        Ha_2 = psychometric({'Tdb':Ta_2,'w':air_in['w']},'h') #condition at end of dry section (equal to dew point)
        Ha3 = Ha_2 - Q_w/air_in['m_dot']
        Ta_out = psychometric({'h':Ha3},'Tdb')
        w_out = psychometric({'h':Ha3,'Tdb':Ta_out},'w')
    return Ta_out,w_out

def wet_coil_calc(x,aa,bb,R_i,R_mf,R_o,R_o_w,UA_dry,X,Y,X2,Y2,air_in,Tw_in):
    Cp_air = 1006 + 1860*air_in['w'] #J/kg*K
    if x == 0: #fully wet 
        UA_wet = (1/bb/(R_i + R_mf + R_o_w))
        Z_w = float(np.exp(UA_wet*(X2 + Y2)))
        #  K3 = (X2+Y2)/(X2*Z_w + Y2)
        K5 = Z_w*(Y2 + X2)/(X2*Z_w + Y2)
        K6 = Y2*(1 - Z_w)/(bb*(X2*Z_w + Y2))
        Tw_2 = K5*Tw_in + K6*(air_in['h'] - aa)
        Ta_2 = air_in['Tdb']
        R_x = (R_mf + R_i)/R_o_w
        T_s_2 = 1/(R_x+1)*(Tw_2 + R_x/bb*(air_in['h'] - aa))
    else:#partially wet
        UA_wet = (1-x)*(1/bb/(R_i + R_mf + R_o_w))
        UA_dry_x = x*UA_dry
        Z_d = float(np.exp(UA_dry_x*(X + Y)))
        Z_w = float(np.exp(UA_wet*(X2 + Y2)))
        K1 = (Z_d-1)/(Z_d +Y/X)
        K5 = Z_w*(Y2 + X2)/(X2*Z_w + Y2)
        K6 = Y2*(1 - Z_w)/(bb*(X2*Z_w + Y2))
        Tw_2 = 1/(1 - K1*K6*Cp_air)*(K5*Tw_in + K6*(air_in['h'] - Cp_air*air_in['Tdb']*K1 -aa))
        Ta_2 = air_in['Tdb'] - K1*(air_in['Tdb'] - Tw_2)
        T_s_2 = Tw_2 + ((1/UA_dry_x)-R_o)/(1/UA_dry_x)*(Ta_2 - Tw_2)
    return T_s_2,Ta_2,Tw_2