'''
mode 1 (empty plant_nodes, only heating coils): Given inlet temperatures and zone load request, for given air_flow find water flow that meets load. If water flow saturates, increase air flow until load is met or air flow saturates
mode 2: Given water and air inlet flows and temperature, find air outlet
Detailed water coil applies only to cooling, only mode 2
'''
from building_plus.basic.psychometric import psychometric
from building_plus.basic.two_way_interp import two_way_interp
from building_plus.components.detailed_water_coil import detailed_water_coil

import numpy as np
import copy

def water_coil(building,name,var1,var2,var3):
    if name in building['coils_heating']:
        coil  = building['coils_heating'][name]
        mode = 'heating'
    else:
        coil = building['coils_cooling'][name]
        mode = 'cooling'

    n = building['plant_demand_equip']['name'].index(name)   
    out = building['plant_demand_equip']['outlet'][n] 
    if type(var3) is dict:
        solve4 = 'water'
        air_in = {}
        for f in list(var1.keys()):
            air_in[f] = copy.copy(var1[f])
        T_supply = copy.copy(var2)
        in_n = building['plant_demand_equip']['inlet'][n]
        Tw_in = var3['demand_temperature'][in_n]
        Cp_air = 1006 + 1860*air_in['w'] #J/kg*K
        if mode=='heating':
            sensible_load  = air_in['m_dot']*Cp_air*(T_supply - air_in['Tdb'])
        elif mode=='cooling':
            sensible_load  = air_in['m_dot']*Cp_air*(air_in['Tdb'] - T_supply)
    else:
        solve4 = 'air'
        air_in = {}
        air_in['Tdb']  = var3[0]
        air_in['w']  = var3[1]
        m_a_max = var3[2]
        Cp_air = 1006 + 1860*air_in['w'] #J/kg*K
        air_in['m_dot'] = var2/(Cp_air*(coil['air_outlet_temperature']-var1))
        sensible_load = air_in['m_dot']*Cp_air*(coil['air_outlet_temperature'] - air_in['Tdb'])
        air_in['m_dot'] = min(air_in['m_dot'],m_a_max)
        air_in['h'] = psychometric(air_in,'h')
        Tw_in = coil['water_inlet_temperature']
        T_supply = var3[0]
    if coil['type']=='Cooling:Water:DetailedGeometry' or coil['type']=='Heating:Water:DetailedGeometry':
        air_out,m_w,actual_load = detailed_water_coil(coil,air_in,sensible_load,Tw_in,T_supply)
    elif coil['type']=='Heating:Water':
            air_out,m_w,actual_load = heating_water_coil(coil,air_in,sensible_load,Tw_in,T_supply,solve4)
    elif coil['type']=='Cooling:Water':
            air_out,m_w,actual_load = cooling_water_coil(coil,air_in,sensible_load,Tw_in,T_supply)
    return air_out,m_w,actual_load,out

def heating_water_coil(coil,air_in,sensible_load,Tw_in,T_supply,solve4):
    #sensible energy transfer only
    air_out = {}
    for f in list(air_in.keys()):
        air_out[f] = copy.copy(air_in[f])
    air_density = 1.204 #kg/m^3
    if air_in['m_dot']>1e-3*coil['rated_air_flow']*air_density and sensible_load/air_in['m_dot']>1 and coil['rated_water_flow']>0:
        den_water = 995 #kg/m^3
        Cp_air = 1006 + 1860*air_in['w'] #J/kg*K
        Cp_water = 4186 #J/kg*K
        Ta_in = air_in['Tdb']
        Tw_in0 = coil['water_inlet_temperature']
        Ta_in0 = coil['air_inlet_temperature']
        Tw_out = min(coil['water_outlet_temperature'],Tw_in - 1)
        m_a_rated = coil['rated_air_flow']*air_density
        m_a = air_in['m_dot']
        m_w_rated = coil['rated_water_flow']*den_water #convert m^3/s to kg/s
        hA_w0,hA_a0,n_f = w_coil_param(coil)
        x_a = 1 + 4.769e-3*(Ta_in - Ta_in0)
        x_w = 1 + (.014/(1 + .014*Tw_in0))*(Tw_in - Tw_in0)
        if solve4=='air':
            ##line search to solve for water flow that gives correct sensible load (page 789 & 960 of the manual)
            ##water flow rate and water outlet temperature change
            n = 10
            h_out = [0 for i in range(n)]
            m_w_min = max(1e-8*m_w_rated,min(m_w_rated,.02*sensible_load/(Cp_water*(Tw_in - Tw_out))))
            flow = np.logspace(np.log10(m_w_min),np.log10(m_w_rated),n)
            flow = [float(x) for x in flow]
            for i in range(n):
                T_out = dry_coil(x_w,flow[i],m_w_rated,hA_w0,x_a,m_a,m_a_rated,hA_a0,n_f,Cp_air,Ta_in,Tw_in)
                h_out[i] = psychometric({'Tdb':T_out,'w':air_out['w']},'h')
            actual_load = [air_out['m_dot']*(h_out[i] - air_in['h']) for i in range(n)] #heat added in W
            if actual_load[-1]<sensible_load:
                m_w = m_w_rated
            else:
                m_w = two_way_interp(sensible_load,actual_load,flow)
            ## If increasing water flow was insufficient, solve for air flow to meet load
            flow = np.linspace(air_out['m_dot'],m_a_rated,n)
            flow = [float(x) for x in flow]
            for i in range(n):
                T_out = dry_coil(x_w,m_w,m_w_rated,hA_w0,x_a,flow[i],m_a_rated,hA_a0,n_f,Cp_air,Ta_in,Tw_in)
                h_out[i] = psychometric({'Tdb':T_out,'w':air_out['w']},'h')
            actual_load = [flow[i]*(h_out[i] - air_in['h']) for i in range(n)] #heat added in W
            if actual_load[-1]<sensible_load:
                air_out['m_dot'] = m_a_rated
            else:
                air_out['m_dot'] = two_way_interp(sensible_load,actual_load,flow)
        elif solve4=='water': #if m_w == 0 %first guess solving for m_w
            ##line search to solve for water flow that gives correct sensible load (page 789 & 960 of the manual)
            ##water flow rate and water outlet temperature change
            n = 10
            T_out = [0 for i in range(n)]
            m_w_min = max(1e-8*m_w_rated,min(m_w_rated,.002*sensible_load/(Cp_water*(Tw_in - Tw_out))))
            flow = np.logspace(np.log10(m_w_min),np.log10(m_w_rated),n)
            flow = [float(x) for x in flow]
            for i in range(n):
                T_out[i] = dry_coil(x_w,flow[i],m_w_rated,hA_w0,x_a,m_a,m_a_rated,hA_a0,n_f,Cp_air,Ta_in,Tw_in)
            if T_out[-1]<T_supply:
                m_w = m_w_rated
            else:
                m_w = two_way_interp(T_supply,T_out,flow)
            air_out['Tdb'] = dry_coil(x_w,m_w,m_w_rated,hA_w0,x_a,m_a,m_a_rated,hA_a0,n_f,Cp_air,Ta_in,Tw_in)
            air_out['h'] = psychometric(air_out,'h')
        actual_load = -air_out['m_dot']*(air_out['h'] - air_in['h']) #heat added in W
    else:
        air_out['Tdb'] = T_supply
        air_out['h'] = psychometric(air_out,'h')
        actual_load = 0
        m_w = 0
    return air_out,m_w,actual_load

def w_coil_param(coil):
    #part of UA calculations depending only on inputs
    if 'air_water_convection_ratio' in coil and coil['air_water_convection_ratio']!=None:
        r = coil['air_water_convection_ratio']
        hA_w0 = coil['UA']*((r+1)/r)
        hA_a0 = coil['capacity']/abs(coil['air_outlet_temperature'] - coil['air_inlet_temperature'])
        n_f = r*hA_w0/hA_a0
    else: # need to find root where r and n_f satisfy set of equations
        den_water = 995 #kg/m^3
        Cp_water = 4186 #J/kg*K
        hA_a0 = coil['capacity']/abs(coil['air_outlet_temperature'] - coil['air_inlet_temperature'])
        hA_w0 = coil['rated_water_flow']*den_water*Cp_water #coil['capacity']/abs(coil['water_inlet_temperature'] - coil['water_outlet_temperature'])
        n_f = 1/(hA_a0/coil['UA']- hA_a0/hA_w0) #fin efficiency  
        r = n_f*hA_a0/hA_w0 #air water convection ratio
    return hA_w0,hA_a0,n_f

def dry_coil(x_w,m_w,m_w_rated,hA_w0,x_a,m_a,m_a_rated,hA_a0,n_f,Cp_air,Ta_in,Tw_in):
    #find new UA factor
    Cp_water = 4186 #J/kg*K
    hA_a = x_a*((m_a/m_a_rated)**.8)*hA_a0
    hA_w = x_w*((m_w/m_w_rated)**.85)*hA_w0
    UA = 1/(1/hA_w + 1/(n_f*hA_a))

    #capacitance
    C_air = Cp_air*m_a
    C_w = Cp_water*m_w
    C_min = min(C_air,C_w)
    Z = C_min/max(C_air,C_w)

    #Find outlet temperatures
    NTU = UA/C_min
    effect = 1 - float(np.exp((np.exp(-Z*NTU**.78)-1)/(Z*NTU**(-.22)))) #cross flow effectiveness
    # effect = (1 - exp(-NTU.*(1-Z)))./(Z*exp(-NTU.*(1-Z))) #counter flow effectiveness
    Ta_out = Ta_in - effect*C_min*(Ta_in - Tw_in)/C_air
    # Tw_out = Tw_in + effect*C_min*(Ta_in - Tw_in)/C_w
    return Ta_out

def cooling_water_coil(coil,air_in,sensible_load,Tw_in,T_supply):
    #sensible energy transfer only
    air_out = {}
    for f in list(air_in.keys()):
        air_out[f] = copy.copy(air_in[f])
    m_w = 0
    if air_in['m_dot']>0 and coil['rated_water_flow']>0 and sensible_load/air_in['m_dot']>1 and Tw_in<air_in['Tdb']:
        air_density = 1.204 #kg/m^3
        den_water = 995 #kg/m^3
        Cp_water = 4186 #J/kg*K
        Cp_air = 1006 + 1860*air_in['w'] #J/kg*K
        Ta_in = air_in['Tdb']
        Tw_in0 = coil['water_inlet_temperature']
        Ta_in0 = coil['air_inlet_temperature']
        Tw_out = Tw_in + (coil['water_outlet_temperature'] - coil['water_inlet_temperature'])
        m_a_rated = coil['rated_air_flow']*air_density
        m_a = air_in['m_dot']
        m_w_rated = coil['rated_water_flow']*den_water #convert m^3/s to kg/s
        hA_w0,hA_a0,n_f = w_coil_param(coil)
        MaxQ = m_w_rated*Cp_water*(Ta_in-Tw_in)
        if Tw_in > air_in['Tdb']:
            print('cooling coil water hotter than air inlet') #should never be here except maybe during warm-up?
        else:
            if Tw_in>T_supply:
                T_supply = Tw_in+0.1 #should never be here except maybe during warm-up?
        
            ##loop to solve for wet/dry portion of coil (page 789 & 960 of the manual)
            ##water flow rate and water outlet temperature change
            Tdp = psychometric(air_in,'Tdp')

            dry = False
            if Tdp < Tw_in:
                dry = True #dry because water is not cold enough to condense moisture
            elif Tdp < T_supply:
                dry = True #dry because it does need to get to the dew point
            elif MaxQ<(air_in['m_dot']*(air_in['h'] - psychometric({'Tdp':Tdp,'w':air_in['w']},'h'))):
                dry = True #dry because there is not enough water cooling capcity to reach dew point
            if dry:
                #simulate dry coil
                x_a = 1 + 4.769e-3*(Ta_in - Ta_in0)
                x_w = 1 + (.014/(1 + .014*Tw_in0))*(Tw_in - Tw_in0)
                ##line search to solve for water flow that gives correct sensible load (page 789 & 960 of the manual)
                ##water flow rate and water outlet temperature change
                n = 10
                T_out = [0 for i in range(n)]
                T_out[-1] = dry_coil(x_w,m_w_rated,m_w_rated,hA_w0,x_a,m_a,m_a_rated,hA_a0,n_f,Cp_air,Ta_in,Tw_in)
                if T_out[-1]>T_supply:
                    m_w = m_w_rated
                    air_out['Tdb'] = T_out[-1]
                else: 
                    m_w_min = max(1e-8*m_w_rated,min(m_w_rated,.002*sensible_load/(Cp_water*(Tw_out - Tw_in))))
                    flow = np.logspace(np.log10(m_w_min),np.log10(m_w_rated),n)
                    flow = [float(x) for x in flow]
                    for i in range(n-1):
                        T_out[i] = dry_coil(x_w,flow[i],m_w_rated,hA_w0,x_a,m_a,m_a_rated,hA_a0,n_f,Cp_air,Ta_in,Tw_in)
                    m_w = two_way_interp(T_supply,T_out,flow)
                    flow = np.logspace(np.log10(.85*m_w),np.log10(min(m_w_rated,1.25*m_w)),n)
                    T_out = [dry_coil(x_w,flow[i],m_w_rated,hA_w0,x_a,m_a,m_a_rated,hA_a0,n_f,Cp_air,Ta_in,Tw_in) for i in range(n)]
                    if T_out[-1]>T_supply:
                        flow = np.logspace(np.log10(1.25*m_w),np.log10(min(m_w_rated,2*m_w)),n)
                        T_out = [dry_coil(x_w,flow[i],m_w_rated,hA_w0,x_a,m_a,m_a_rated,hA_a0,n_f,Cp_air,Ta_in,Tw_in) for i in range(n)]
                    elif T_out[0]<T_supply:
                        flow = np.logspace(np.log10(.5*m_w),np.log10(min(m_w_rated,.85*m_w)),n)
                        T_out = [dry_coil(x_w,flow[i],m_w_rated,hA_w0,x_a,m_a,m_a_rated,hA_a0,n_f,Cp_air,Ta_in,Tw_in) for i in range(n)]
                    m_w = two_way_interp(T_supply,T_out,flow)
                    air_out['T'] = T_supply+0
                #air_out['Tdb'] = dry_coil(x_w,m_w,m_w_rated,hA_w0,x_a,m_a,m_a_rated,hA_a0,n_f,Cp_air,Ta_in,Tw_in)
                air_out['h'] = psychometric(air_out,'h')
            else:
                #wet or partially wet coil
                #must at leach reach dew point
                #search to find water mass flow and dry length
                air_mid  = {}
                for f in list(air_in.keys()):
                    air_mid [f] = copy.copy(air_in[f])
                air_mid['Tdb'] = Tdp
                air_mid['h'] = psychometric(air_mid,'h')
                q_dry = air_in['m_dot']*(air_in['h'] - air_mid['h'])
                
                air_out['Tdb'] = T_supply #initial guess
                air_out['w'] = psychometric({'Twb':air_out['Tdb']},'w')
                if air_in['w']<=air_out['w']:
                    air_out['w'] = air_in['w']+0
                condensate_H2O = air_in['m_dot']*(air_in['w'] - air_out['w'])
                latent_power = condensate_H2O*2264.705 # kg/s *kJ/kg
                air_out['m_dot'] = air_in['m_dot'] - condensate_H2O
                air_out['h'] = psychometric(air_out,'h')
                
                q_wet = max(0,air_mid['m_dot']*air_mid['h'] - air_out['m_dot']*air_out['h'] + latent_power)

                m_w_min = max(1.01*q_wet/(Cp_water*(Tdp - Tw_in)),(q_dry+q_wet)/(Cp_water*(air_in['Tdb'] - Tw_in)))
                m_w_min = max(1e-8*m_w_rated,m_w_min)
                if m_w_rated<=m_w_min:
                    m_w = m_w_rated #need all the cooling we can get
                elif q_wet == 0:
                    m_w = m_w_min
                else:
                    mw_r = [m_w_min,m_w_rated]
                    #for a given water flow Tw_mid is known, and the length of dry coil
                    #to get to Tdb can be found. Iterate m_w to get total heat transfer correct
                    min_e = 1
                    n = 10
                    while min_e>1e-3 and (mw_r[1]-mw_r[0])>0.01*(m_w_rated - m_w_min):
                        flow = np.logspace(np.log10(mw_r[0]),np.log10(mw_r[1]),n)
                        flow = [float(x) for x in flow]
                        Tw_mid =[min(Tdp-1e-8,Tw_in + q_wet/(Cp_water*flow[i])) for i in range(n)]
                        Tlmtd = [((Tdp-Tw_mid[i]) - (T_supply-Tw_in))/float(np.log(Tdp-Tw_mid[i]) - np.log(T_supply-Tw_in)) for i in range(n)]
                        UA_wet_needed = [q_wet/Tlmtd[i] for i in range(n)]
                        UA_wet,_ = wet_coil(flow,m_w_rated,hA_w0,m_a,m_a_rated,hA_a0,n_f,Cp_air,Ta_in,Tw_in,Tw_mid,Tdp,Ta_in0,Tw_in0)
                        min_needed = float(np.amin(UA_wet_needed))
                        error = [(UA_wet[i]-UA_wet_needed[i])/min_needed for i in range(n)]
                        min_e = abs(error[0])
                        mw_r = [flow[0],flow[1]]
                        ind = 0
                        for i in range(n-2):
                            if abs(error[i+1]) <min_e:
                                if error[i+1]<0:
                                    mw_r = [flow[i+1],flow[i+2]]
                                else:
                                    mw_r = [flow[i],flow[i+1]]
                                ind = i+1
                    if UA_wet[-1]<UA_wet_needed[ind]:
                        m_w = flow[-1]
                    elif UA_wet[0]>UA_wet_needed[ind]:
                        m_w = flow[0]
                    else:
                        flow = [flow[i] for i in range(n) if UA_wet[i]>0]
                        UA_wet = [UA_wet[i] for i in range(n) if UA_wet[i]>0]
                        if UA_wet_needed[ind]<UA_wet[0]:
                            m_w = flow[0]
                        else:
                            m_w = two_way_interp(UA_wet_needed[ind],UA_wet,flow)
    actual_load = -air_out['m_dot']*(air_out['h'] - air_in['h'])#heat added in W
    return air_out,m_w,actual_load

def wet_coil(flow,m_w_rated,hA_w0,m_a,m_a_rated,hA_a0,n_f,Cp_air,Ta_in,Tw_in,Tw_mid,Tdp,Ta_in0,Tw_in0):
    #find fraction of coil thats dry, then the UA of the wet portion
    Cp_water = 4186 #J/kg*K
    C_air = Cp_air*m_a
    n = 20 #len(flow)
    frac = [0 for i in range(len(flow))]
    UA_wet = [0 for i in range(len(flow))]
    x_a = 1 + 4.769e-3*(Ta_in - Ta_in0)
    hA_a = x_a*((m_a/m_a_rated)**.8)*hA_a0
    for i in range(len(flow)):
        m_w = flow[i]
        f = np.logspace(-2,0,n)
        f = [float(x) for x in f]
        C_w = Cp_water*m_w
        C_min = min(C_air,C_w)
        Z = C_min/max(C_air,C_w)
        x_w = 1 + (.014/(1 + .014*Tw_in0))*(Tw_mid[i] - Tw_in0)
        hA_w = x_w*((m_w/m_w_rated)**.85)*hA_w0
        UA = [f[j]/(1/(hA_w) + 1/(n_f*hA_a)) for j in range(n)]
        NTU = [UA[j]/C_min for j in range(n)]
        effect = [1 - float(np.exp((np.exp(-Z*NTU[j]**.78)-1)/(Z*NTU[j]**(-.22)))) for j in range(n)] #cross flow effectiveness
        Ta_mid = [Ta_in - effect[j]*C_min*(Ta_in - Tw_mid[i])/C_air for j in range(n)]
        if Tdp<Ta_mid[-1]:
            frac[i] = 1
            UA_wet[i] = -1e8
        else:
            x_a = 1 + 4.769e-3*(Tdp - Ta_in0)
            x_w = 1 + (.014/(1 + .014*Tw_in0))*(Tw_in - Tw_in0)
            hA_a = x_a*((m_a/m_a_rated)**.8)*hA_a0
            hA_w = x_w*((m_w/m_w_rated)**.85)*hA_w0
            if Ta_in<Tdp:
                frac[i] = 0
            else:
                f1 = [0]
                f1.extend(f)
                Ta = [Ta_in]
                Ta.extend(Ta_mid)
                frac[i] = two_way_interp(Tdp,Ta,f1)
            UA_wet[i] = (1-frac[i])/(1/hA_w + 1/(n_f*hA_a))
    return UA_wet,frac