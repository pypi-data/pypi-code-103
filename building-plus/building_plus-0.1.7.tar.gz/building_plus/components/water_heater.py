
import numpy as np

def water_heater(building,T,tank_on,T_exit,T_air,T_source,flow_source,dt,name):
    Cp_water = 4186 #J/kg*K
    den_water = 997 #kg/m^3
    wh = building['water_heater'][name]
    wh_gas=0
    wh_elec=0
    e_source = wh['source_side_effectiveness']
    m_cp = wh['tank_volume']*den_water*Cp_water
    T_dif = wh['deadband_temperature_dif']
    if T_dif==None:
        T_dif = 0
    if e_source==None:
        e_source = 1
    if wh['on_cycle_fuel_use']==None:
        q_on_cycle = 0
    else:
        q_on_cycle = wh['on_cycle_fuel_use']*wh['on_cycle_frac2tank']
    if wh['off_cycle_fuel_use']==None:
        q_off_cycle = 0
    else:
        q_off_cycle = wh['off_cycle_fuel_use']*wh['off_cycle_frac2tank']
    UA_on_cycle = wh['on_cycle_loss2ambient']
    UA_off_cycle = wh['off_cycle_loss2ambient']
    q_heater = wh['heater_maximum_capacity']*wh['heater_efficiency']
    a_on = (q_heater + q_on_cycle + UA_on_cycle*T_air + e_source*flow_source*Cp_water*T_source)/m_cp
    b_on = -(UA_on_cycle + e_source*flow_source*Cp_water)/m_cp
    a_off = (q_off_cycle + UA_off_cycle*T_air + e_source*flow_source*Cp_water*T_source)/m_cp
    b_off = -(UA_off_cycle + e_source*flow_source*Cp_water)/m_cp

    sec_on = 0
    t = 0
    while t < dt:
        step = min(60,dt-t) #minutes
        if T<T_exit-T_dif:
            tank_on = True
        if tank_on:
            if b_on == 0:
                T_new = a_on*step + T
            else:
                T_new = (a_on/b_on + T)*float(np.exp(b_on*step)) - a_on/b_on
            if T_new>=T_exit:#turns off partway through step
                tank_on = False
                if b_on == 0:
                    t_on = (T_exit - T)/a_on
                else:
                    t_on = 1/b_on*float(np.log((a_on/b_on + T_exit)/(a_on/b_on + T)))
                sec_on = sec_on + t_on #on for fraction of minute
                #off for remainder of minute
                T = T_exit
                if b_off == 0:
                    T = a_off*(step-sec_on) + T
                else:
                    T = (a_off/b_off + T)*float(np.exp(b_off*(step-sec_on))) - a_off/b_off
            else:
                sec_on = sec_on + step
        else:
            if b_off == 0:
                T = a_off*step + T
            else:
                T = (a_off/b_off + T)*float(np.exp(b_off*step)) - a_off/b_off
        t += step

    if wh['heater_fuel']=='naturalgas':
        wh_gas += sec_on/dt*wh['heater_maximum_capacity'] #Watts
    else:
        wh_elec += sec_on/dt*wh['heater_maximum_capacity'] #Watts
    if q_on_cycle>0:
        if wh['on_cycle_fuel_type']=='naturalgas':
            wh_gas += sec_on/dt*wh['on_cycle_fuel_use'] #Watts
        else:
            wh_elec +=sec_on/dt*wh['on_cycle_fuel_use'] #Watts
    if q_off_cycle>0:
        if wh['off_cycle_fuel_type']=='naturalgas':
            wh_gas += (dt-sec_on)/dt*wh['off_cycle_fuel_use'] #Watts
        else:
            wh_elec += (dt-sec_on)/dt*wh['off_cycle_fuel_use'] #Watts
    return T,tank_on,wh_gas,wh_elec