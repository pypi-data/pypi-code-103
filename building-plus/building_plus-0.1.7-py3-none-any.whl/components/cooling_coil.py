from building_plus.basic.psychometric import psychometric
from building_plus.basic.two_way_interp import two_way_interp
from building_plus.basic.eval_curve import eval_curve

import numpy as np

def cooling_coil(building,name,air_in,T_outside,T_treat):
    ## Compute the cooling and electric load for DX cooling coils (local AC units not on a central water loop)
    coil = building['coils_cooling'][name]
    curve = building['curves']
    air_density = 1.204  #kg/m^3  #standard air density (1.204 kg/m3) adjusted for the local barometric pressure (standard barometric pressure corrected for altitude, ASHRAE 1997 HOF pg. 6.1).
    air_out = {}
    for k in air_in:
        air_out[k] = air_in[k]+0
    spec_heat_supply = 1006 + 1860*air_in['w']  #J/kg*K
    sensible_load = air_in['m_dot']*spec_heat_supply*(air_in['Tdb'] - T_treat)
    if sensible_load>10:
        if coil['type']=='Cooling:DX:SingleSpeed' or coil['type']=='Cooling:DX:TwoSpeed': #page 805
            try: 
                c_n = building['hvac']['components']['name'].index(name)
                al = building['hvac']['components']['loop'][c_n] #air loop
                bf_rated = bypass_factor_rated(building['hvac']['design']['Tsupply_c'][al],building['hvac']['design']['w_supply_c'][al],building['hvac']['design']['all_outdoor_flow_cooling'][al])
            except ValueError:
                al =[]
                for uhc in building['unitary_heat_cool']:
                    if ('cool_coil' in building['unitary_heat_cool'][uhc] and building['unitary_heat_cool'][uhc]['cool_coil']==name):
                        al = building['unitary_heat_cool'][uhc]['loop']
                        bf_rated = bypass_factor_rated(building['hvac']['design']['Tsupply_c'][al],building['hvac']['design']['w_supply_c'][al],building['hvac']['design']['all_outdoor_flow_cooling'][al])
                        break
                if len(al)==0:
                    for us in building['unitary_sys']:
                        if ('cool_coil' in building['unitary_sys'][us] and building['unitary_sys'][us]['cool_coil']==name):
                            z = building['unitary_sys'][us]['zone']
                            sp = building['setpoints']['zone'].index(z)
                            bf_rated = bypass_factor_rated(building['setpoints']['cooling_T_des'][sp],building['setpoints']['cooling_w_des'][sp],False)
                            break
                    
            coil['rated_A0'] = float(-np.log(bf_rated))*coil['rated_air_flow']*air_density
            
            bypass_factor = float(np.exp(-coil['rated_A0']/air_in['m_dot']))
            input = [psychometric(air_in,'Twb'),T_outside]  #needs to be outdoor wetbulb temperature if it is an evaporative cooled condenser
            
            TotCapTempMod= eval_curve(curve,coil['capacity_v_temperature_curve'],input)
            EIRTempMod = eval_curve(curve,coil['energy_input_v_temperature_curve'],input)

            input2 = air_in['m_dot']/(coil['rated_air_flow']*air_density)  #normalized flow
            TotCapFlowMod = eval_curve(curve,coil['capacity_v_flow_curve'],[input2]) 
            EIRFlowMod= eval_curve(curve,coil['energy_input_v_flow_curve'],[input2])
            EIR = (1/coil['rated_COP'])*EIRTempMod*EIRFlowMod #energy input ratio
            Q_total = coil['rated_capacity']*TotCapTempMod*TotCapFlowMod
            PLR = min(1,sensible_load/Q_total)
            Q_max = Q_total
            Speed_ratio = 1
            if coil['type']=='Cooling:DX:TwoSpeed':
                TotCapTempMod_2 = eval_curve(curve,coil['capacity_v_temperature_curve2'],input)
                EIRTempMod_2 = eval_curve(curve,coil['energy_input_v_temperature_curve2'],input)

                Q_total2 = coil['rated_capacity2']*TotCapTempMod_2*TotCapFlowMod
                EIR_2 = (1/coil['rated_COP2'])*EIRTempMod_2*EIRFlowMod #energy input ratio

                Speed_ratio = max(0,(sensible_load - Q_total2)/(Q_total - Q_total2))
                if Speed_ratio<0:
                    PLR = min(1,sensible_load/Q_total2)
                    Q_max = Q_total2
            error = 100
            old_error = 100
            while abs(error)>1e-4:
                air_out = coil_air_out(air_in,Q_max,bypass_factor,PLR)
                air_out2 = coil_air_out(air_in,Q_max,bypass_factor,PLR+1e-3)
                dT_dPLR = (air_out['Tdb'] - air_out2['Tdb'])/1e-3
                if dT_dPLR<0:
                    dT_dPLR = .05
                error = (air_out['Tdb'] - T_treat)
                if (PLR == 1 and error>0) or (error<0 and PLR == 0):
                    error = 0
                if error>old_error:
                    PLR = max(0,min(1,PLR + error/(4*dT_dPLR)))
                else:
                    PLR = max(0,min(1,PLR + error/dT_dPLR))
                old_error = error
            if coil['type']=='Cooling:DX:TwoSpeed' and Speed_ratio>0:
                revised_sensible_load = PLR*Q_total
                Speed_ratio = max(0,(revised_sensible_load - Q_total2)/(Q_total - Q_total2))
                Power = Speed_ratio*Q_total*EIR + (1-Speed_ratio)*Q_total2*EIR_2
                heat_rejected = Speed_ratio*Q_total*(1+EIR) + (1-Speed_ratio)*Q_total2*(1+EIR_2)
            else:
                PartLoadFrac = max(.7,eval_curve(curve,coil['part_load_curve'],[PLR]))
                RTF = PLR/PartLoadFrac #runtime fraction
                if coil['type']=='Cooling:DX:TwoSpeed':
                    Power = Q_total2*EIR_2*RTF
                    heat_rejected = Q_total2*(1+EIR_2)
                else:
                    Power = Q_total*EIR*RTF
                    heat_rejected = Q_total*(1+EIR)
    else:
        Power = 0
    return air_out,Power

def coil_air_out(air_in,Q_total,bypass_factor,PLR):
    ## Determine exit air conditions based on operating status of the coil

    #find apparatus dewpoint
    h_ADP = air_in['h'] - (Q_total/air_in['m_dot'])/(1-bypass_factor) # J/kg
    T_search = [2*i+2 for i in range(19)]
    w_ADP = two_way_interp(h_ADP,psychometric({'Twb':T_search},'h'),psychometric({'Twb':T_search},'w'))
    air_out = {}
    air_out['m_dot'] = air_in['m_dot']
    air_out['h'] = air_in['h'] - Q_total*PLR/air_out['m_dot'] #J/kg
    if air_in['w']<w_ADP:  #dry coil
        sensible_heat_ratio = 1
        air_out['w'] = air_in['w']
    else:
        sensible_heat_ratio = min(1,(psychometric({'Tdb':air_in['Tdb'],'w':w_ADP},'h')-h_ADP)/(air_in['h'] - h_ADP))
        h_Tin_w_out = air_in['h'] - (1-sensible_heat_ratio)*(air_in['h'] - air_out['h'])
        air_out['w'] = psychometric({'Tdb':air_in['Tdb'],'h':h_Tin_w_out},'w') 
    spec_heat = 1006 + 1860*(air_in['w']+air_out['w'])/2  #J/kg*K
    air_out['Tdb'] = air_in['Tdb'] - sensible_heat_ratio*Q_total*PLR/(air_out['m_dot']*spec_heat)
    return air_out

def bypass_factor_rated(T_supply,w_supply,all_outdoor):
    ## determine bypass factor based on rated dew point
    if all_outdoor:
        T_mix = 26.7
        w_mix = 0.01115  #T_wb = 19.5, RH = 50.7 #
    else:
        T_mix = 35
        w_mix = 0.014  #T_wb = 23.9, RH = 40 #
    h_mix = psychometric({'Tdb':T_mix,'w':w_mix},'h')
    h_sup = psychometric({'Tdb':T_supply,'w':w_supply},'h')

    rated_slope = (w_mix - w_supply)/(T_mix - T_supply)
     # #find apparatus dewpoint
    T_search = [5+i for i in range(round(T_supply+.5))]
    W_s = psychometric({'Twb':T_search},'w')
    W_coil_linear_extrap = [rated_slope*(T_search[i]-T_supply) + w_supply for i in range(len(T_search))]
    for i in range(len(W_s)):
        if W_s[i]>=W_coil_linear_extrap[i]:
            break
    apparatus_dewpoint = T_search[i]

    h_ADP = psychometric({'Tdb':apparatus_dewpoint,'w':W_s[i]},'h')
    bf = (h_sup - h_ADP)/(h_mix-h_ADP)
    return bf